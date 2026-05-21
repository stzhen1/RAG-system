import { useState } from 'react'
import Sidebar from './components/Layout/Sidebar'
import ChatWindow from './components/Chat/ChatWindow'
import UploadDialog from './components/DocumentUpload/UploadDialog'

export default function App() {
  const [activeView, setActiveView] = useState<'chat' | 'documents'>('chat')
  const [uploadOpen, setUploadOpen] = useState(false)

  return (
    <div className="flex h-screen bg-background text-text">
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        onUpload={() => setUploadOpen(true)}
      />
      <main className="flex-1 flex flex-col overflow-hidden">
        {activeView === 'chat' && <ChatWindow />}
        {activeView === 'documents' && (
          <div className="flex-1 flex items-center justify-center">
            <p className="font-mono text-sm text-muted uppercase tracking-wider">
              Document management &mdash; Phase 2
            </p>
          </div>
        )}
      </main>
      <UploadDialog open={uploadOpen} onClose={() => setUploadOpen(false)} />
    </div>
  )
}
