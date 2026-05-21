import { MessageSquare, FileText, Upload, Hash } from 'lucide-react'
import { cn } from '../../lib/utils'

interface SidebarProps {
  activeView: 'chat' | 'documents'
  onViewChange: (view: 'chat' | 'documents') => void
  onUpload: () => void
}

export default function Sidebar({
  activeView,
  onViewChange,
  onUpload,
}: SidebarProps) {
  return (
    <aside className="w-64 border-r border-border bg-surface flex flex-col select-none">
      <div className="p-5 border-b border-border">
        <div className="flex items-center gap-2 mb-1">
          <Hash className="h-4 w-4 text-accent" />
          <span className="font-mono text-xs text-muted uppercase tracking-wider">
            Enterprise
          </span>
        </div>
        <h1 className="font-mono text-lg font-medium text-text tracking-tight">
          RAG
        </h1>
      </div>

      <nav className="flex flex-col gap-1 p-3 flex-1">
        <button
          onClick={() => onViewChange('chat')}
          className={cn(
            'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
            activeView === 'chat'
              ? 'bg-accent/10 text-accent font-medium'
              : 'text-muted hover:text-text hover:bg-white/5',
          )}
        >
          <MessageSquare className="h-4 w-4" />
          Chat
        </button>

        <button
          onClick={() => onViewChange('documents')}
          className={cn(
            'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
            activeView === 'documents'
              ? 'bg-accent/10 text-accent font-medium'
              : 'text-muted hover:text-text hover:bg-white/5',
          )}
        >
          <FileText className="h-4 w-4" />
          Documents
        </button>
      </nav>

      <div className="p-3 border-t border-border">
        <button
          onClick={onUpload}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-md bg-accent text-background font-medium text-sm hover:bg-accent/90 transition-colors"
        >
          <Upload className="h-4 w-4" />
          Upload Document
        </button>
      </div>

      <div className="p-3 border-t border-border">
        <p className="font-mono text-[10px] text-muted uppercase tracking-wider leading-relaxed">
          Local Deployment
          <br />
          v0.1.0 &mdash; Phase 1
        </p>
      </div>
    </aside>
  )
}
