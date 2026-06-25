import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await auth()
  if (!session) redirect("/login")

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside style={{
        width: 240,
        background: "#1a1a1a",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        gap: 8,
        flexShrink: 0,
      }}>
        <div style={{ color: "white", fontSize: 18, fontWeight: 600, marginBottom: 24 }}>
          🌿 NOA
        </div>
        <a href="/chat" style={{
          color: "#ccc", textDecoration: "none", padding: "8px 12px",
          borderRadius: 6, fontSize: 14,
        }}>
          Chat
        </a>
        <a href="/dashboard" style={{
          color: "#ccc", textDecoration: "none", padding: "8px 12px",
          borderRadius: 6, fontSize: 14,
        }}>
          Dashboard
        </a>
        <div style={{ marginTop: "auto", color: "#666", fontSize: 12, padding: "8px 12px" }}>
          {session.user?.email}
        </div>
      </aside>
      <main style={{ flex: 1, background: "#f8f7f2", overflow: "auto" }}>
        {children}
      </main>
    </div>
  )
}
