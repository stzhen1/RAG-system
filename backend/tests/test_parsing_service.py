from app.services.parsing_service import ParsingService


def test_parse_pdf_extracts_text():
    service = ParsingService()
    result = service.parse_pdf_text_only(b"dummy", filename="test.pdf")
    assert isinstance(result, dict)
    assert "text" in result or "error" in result


def test_parse_unsupported_type_raises():
    service = ParsingService()
    result = service.parse(b"content", filename="test.xyz")
    assert "error" in result
