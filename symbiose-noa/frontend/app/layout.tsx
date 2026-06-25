import type { Metadata } from "next"
import { SessionProvider } from "next-auth/react"

export const metadata: Metadata = {
  title: "NOA — Symbiose Paysage",
  description: "Assistant IA interne Symbiose Paysage",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body style={{ margin: 0, fontFamily: "system-ui, -apple-system, sans-serif" }}>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  )
}
