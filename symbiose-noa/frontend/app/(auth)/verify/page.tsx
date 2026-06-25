"use client"
import { useEffect, useState } from "react"
import { signIn } from "next-auth/react"
import { useSearchParams } from "next/navigation"

export default function VerifyPage() {
  const params = useSearchParams()
  const [status, setStatus] = useState<"loading" | "error">("loading")

  useEffect(() => {
    const token = params.get("token")
    const email = params.get("email")

    if (!token || !email) {
      setStatus("error")
      return
    }

    signIn("credentials", { token, email, callbackUrl: "/chat" }).then((res) => {
      if (res?.error) setStatus("error")
    })
  }, [params])

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "#f8f7f2",
    }}>
      <div style={{
        background: "white",
        borderRadius: 16,
        padding: "40px 48px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        textAlign: "center",
        maxWidth: 380,
      }}>
        <div style={{ fontSize: 32, marginBottom: 16 }}>🌿</div>
        {status === "loading" ? (
          <>
            <p style={{ fontWeight: 500, margin: "0 0 8px" }}>Connexion en cours...</p>
            <p style={{ color: "#888", fontSize: 13, margin: 0 }}>Vous allez être redirigé automatiquement.</p>
          </>
        ) : (
          <>
            <p style={{ fontWeight: 500, margin: "0 0 8px", color: "#e53e3e" }}>Lien invalide ou expiré</p>
            <p style={{ color: "#888", fontSize: 13, margin: "0 0 20px" }}>
              Le lien a peut-être déjà été utilisé ou a expiré (15 min).
            </p>
            <a href="/login" style={{
              display: "inline-block",
              background: "#1D9E75",
              color: "white",
              padding: "10px 20px",
              borderRadius: 8,
              textDecoration: "none",
              fontSize: 14,
              fontWeight: 500,
            }}>
              Demander un nouveau lien
            </a>
          </>
        )}
      </div>
    </div>
  )
}
