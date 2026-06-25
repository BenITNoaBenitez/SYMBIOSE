"use client"
import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { apiRequest } from "@/lib/api"

interface Stats {
  threads: number
  today: {
    request_count: number
    tokens_total: number
    cost_eur: number
  }
  quota_mensuel: number | null
}

export default function StatsCards() {
  const { data: session } = useSession()
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    if (!session?.backendToken) return
    apiRequest<Stats>("/api/dashboard/stats", { token: session.backendToken })
      .then(setStats)
      .catch(() => {})
  }, [session])

  const cards = [
    { label: "Conversations", value: stats?.threads ?? "—" },
    { label: "Requêtes aujourd'hui", value: stats?.today.request_count ?? "—" },
    { label: "Coût du jour", value: stats ? `€${Number(stats.today.cost_eur).toFixed(4)}` : "—" },
    { label: "Quota mensuel", value: stats?.quota_mensuel ?? "Illimité" },
  ]

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
      gap: 16,
      marginBottom: 32,
    }}>
      {cards.map((card) => (
        <div
          key={card.label}
          style={{
            background: "white",
            borderRadius: 12,
            padding: "20px 24px",
            boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
          }}
        >
          <p style={{ color: "#888", fontSize: 12, margin: "0 0 8px" }}>{card.label}</p>
          <p style={{ fontSize: 24, fontWeight: 600, margin: 0 }}>{card.value}</p>
        </div>
      ))}
    </div>
  )
}
