import { useState, useCallback } from 'react'
import { chatStream } from '../api/client'
import type { Message } from '../types'

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = useCallback(
    async (query: string) => {
      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: query,
      }

      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        isStreaming: true,
      }

      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsLoading(true)

      const history = messages
        .filter((m) => !m.isStreaming)
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }))

      try {
        let content = ''
        for await (const chunk of chatStream({ query, history })) {
          content += chunk
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsg.id ? { ...m, content } : m,
            ),
          )
        }
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsg.id ? { ...m, isStreaming: false } : m,
          ),
        )
      } catch (error) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsg.id
              ? {
                  ...m,
                  content: `Error: ${(error as Error).message}`,
                  isStreaming: false,
                }
              : m,
          ),
        )
      } finally {
        setIsLoading(false)
      }
    },
    [messages],
  )

  const clearChat = useCallback(() => {
    setMessages([])
  }, [])

  return { messages, isLoading, sendMessage, clearChat }
}
