import { useEffect, useRef } from 'react'
import { useChat } from '../../hooks/useChat'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'

export default function ChatWindow() {
  const { messages, isLoading, sendMessage, clearChat } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col h-full">
      <header className="border-b border-border px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="font-mono text-sm font-medium text-text">Chat</h2>
          <p className="font-mono text-[10px] text-muted uppercase mt-0.5">
            RAG-Powered Q&A
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="font-mono text-xs text-muted hover:text-accent transition-colors uppercase tracking-wider"
          >
            Clear
          </button>
        )}
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
            <div className="w-12 h-12 rounded-full bg-surface border border-border flex items-center justify-center">
              <span className="font-mono text-accent text-lg">&para;</span>
            </div>
            <div>
              <p className="font-mono text-sm text-muted uppercase tracking-wider">
                Ready for Questions
              </p>
              <p className="text-sm text-muted mt-2 max-w-sm leading-relaxed">
                Upload documents and ask questions about their contents. The
                system will search across your knowledge base and provide
                cited answers.
              </p>
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-border p-4">
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  )
}
