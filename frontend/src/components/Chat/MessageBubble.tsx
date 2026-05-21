import type { Message } from '../../types'
import { cn } from '../../lib/utils'

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'

  return (
    <div
      className={cn(
        'flex gap-4 animate-slide-up',
        isUser ? 'justify-end' : 'justify-start',
      )}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center mt-0.5">
          <span className="font-mono text-[10px] text-accent font-medium">
            AI
          </span>
        </div>
      )}

      <div className={cn('max-w-[75%]', isUser ? 'order-1' : 'order-2')}>
        <div className="flex items-center gap-2 mb-1">
          <span className="font-mono text-[10px] text-muted uppercase tracking-wider">
            {isUser ? 'You' : 'Assistant'}
          </span>
        </div>

        <div
          className={cn(
            'rounded-lg px-5 py-3 text-sm leading-relaxed',
            isUser
              ? 'bg-accent/10 border border-accent/20 text-text'
              : 'bg-surface border border-border blockquote-border text-text',
          )}
        >
          <div className="whitespace-pre-wrap font-serif">
            {message.content}
            {message.isStreaming && (
              <span className="inline-block w-1.5 h-4 bg-accent ml-1 animate-pulse-cursor align-middle" />
            )}
          </div>

          {message.citations && message.citations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-border">
              <p className="font-mono text-[10px] text-muted uppercase tracking-wider mb-2">
                Sources
              </p>
              {message.citations.map((c, i) => (
                <div
                  key={i}
                  className="font-mono text-xs text-muted flex items-center gap-2 py-0.5"
                >
                  <span className="text-accent">&sect;</span>
                  <span>{c.document_name}</span>
                  {c.page && <span>p.{c.page}</span>}
                  <span className="text-[10px] opacity-50">
                    {(c.score * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-surface border border-border flex items-center justify-center mt-0.5 order-2">
          <span className="font-mono text-[10px] text-muted font-medium">
            U
          </span>
        </div>
      )}
    </div>
  )
}
