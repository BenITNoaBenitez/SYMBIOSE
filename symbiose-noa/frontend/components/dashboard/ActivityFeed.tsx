"use client"
import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { apiRequest } from "@/lib/api"

interface AuditEntry {
  id: string
  action: string
  agent_id: string | null
  success: boolean
  created_at: string
}

export default function ActivityFeed() {
  const { data: session } = useSession()
  const [entries, setEntries] = useState<AuditEntry[]>([])

  useEffect(() => {
    if (!session?.backendToken) return
    apiRequest<AuditEntry[]>("/api/dashboard/activity", { token: session.backendToken })
      .then(setEntries)
      .catch(() => {})
  }, [session])

  return (
    <div style={{
      background: "white",
      borderRadius: 12,
      padding: 24,
      boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
    }}>
      <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 16px" }}>Activité récente</h2>
      {entries.length === 0 ? (
        <p style={{ color: "#aaa", fontSize: 14, margin: 0 }}>Aucune activité à afficher</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {entries.map((entry) => (
            <div
              key={entry.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontSize: 14,
              }}
            >
              <span style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <span style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: entry.success ? "#1D9E75" : "#e53e3e",
                  flexShrink: 0,
                }} />
                {entry.action}
                {entry.agent_id && (
                  <span style={{ color: "#888", fontSize: 12 }}>({entry.agent_id})</span>
                )}
              </span>
              <span style={{ color: "#aaa", fontSize: 12, flexShrink: 0, marginLeft: 16 }}>
                {new Date(entry.created_at).toLocaleString("fr-FR")}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
