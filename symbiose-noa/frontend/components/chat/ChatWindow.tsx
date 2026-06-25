"use client"
import { useState } from "react"
import { useSession } from "next-auth/react"
import MessageList from "./MessageList"
import InputBar from "./InputBar"
import { apiRequest } from "@/lib/api"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
}

export default function ChatWindow() {
  const { data: session } = useSession()
  const [messages, setMessages] = useState<Message[]>([])
  const [threadId, setThreadId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const sendMessage = async (text: string) => {
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: text }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await apiRequest<{ response: string; thread_id: string }>(
        "/api/chat/",
        {
          method: "POST",
          token: session?.backendToken,
          body: JSON.stringify({ query: text, thread_id: threadId }),
        }
      )
      if (!threadId) setThreadId(res.thread_id)
      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: "assistant", content: res.response },
      ])
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: "assistant", content: `Erreur : ${err.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <MessageList messages={messages} />
      <InputBar onSend={sendMessage} disabled={loading} />
    </div>
  )
}
