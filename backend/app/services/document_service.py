import uuid
import io
from typing import Dict, Any
from app.config import settings
from app.celery_app.tasks import run_ingestion_pipeline
from app.db.session import async_session


class DocumentService:
    async def upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        file_size = len(file_content)
        if file_size > settings.max_upload_size_mb * 1024 * 1024:
            raise ValueError(f"File exceeds {settings.max_upload_size_mb}MB limit")

        document_id = str(uuid.uuid4())

        minio_path = await self._store_file(file_content, filename, document_id)
        await self._create_document_record(document_id, filename, minio_path, file_size)

        run_ingestion_pipeline(document_id, file_content, filename)

        return {
            "document_id": document_id,
            "filename": filename,
            "status": "uploaded",
            "file_size_bytes": file_size,
        }

    async def _store_file(self, content: bytes, filename: str, document_id: str) -> str:
        from minio import Minio

        client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

        bucket = settings.minio_bucket
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

        object_path = f"{document_id}/{filename}"
        client.put_object(
            bucket,
            object_path,
            io.BytesIO(content),
            len(content),
            content_type="application/octet-stream",
        )

        return f"minio://{bucket}/{object_path}"

    async def _create_document_record(
        self, document_id: str, filename: str, minio_path: str, file_size: int
    ):
        from sqlalchemy import text
        async with async_session() as session:
            stmt = text("""
                INSERT INTO documents (id, filename, file_type, file_size_bytes, minio_path, status)
                VALUES (:id, :filename, :file_type, :file_size, :minio_path, 'uploaded')
            """)
            await session.execute(stmt, {
                "id": document_id,
                "filename": filename,
                "file_type": filename.rsplit(".", 1)[-1].lower(),
                "file_size": file_size,
                "minio_path": minio_path,
            })
            await session.commit()

    async def get_status(self, document_id: str) -> Dict[str, Any]:
        doc = await self._get_document(document_id)
        if not doc:
            raise ValueError(f"Document not found: {document_id}")
        return doc

    async def _get_document(self, document_id: str) -> Dict[str, Any]:
        from sqlalchemy import text
        async with async_session() as session:
            stmt = text("""
                SELECT id::text, filename, file_type, status, page_count,
                       file_size_bytes, error_message, created_at, updated_at
                FROM documents
                WHERE id = :id AND deleted_at IS NULL
            """)
            result = await session.execute(stmt, {"id": document_id})
            row = result.fetchone()
            if not row:
                return None
            return dict(row._mapping)
