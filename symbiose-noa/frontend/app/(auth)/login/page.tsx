"use client"
import { signIn } from "next-auth/react"

export default function LoginPage() {
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
        width: "100%",
      }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>🌿</div>
        <h1 style={{ fontSize: 22, fontWeight: 500, marginBottom: 4, margin: "0 0 4px" }}>NOA</h1>
        <p style={{ color: "#888", fontSize: 14, margin: "0 0 32px" }}>
          Symbiose Paysage
        </p>
        <button
          onClick={() => signIn("google", { callbackUrl: "/chat" })}
          style={{
            width: "100%",
            padding: "12px 24px",
            background: "#1D9E75",
            color: "white",
            border: "none",
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 500,
            cursor: "pointer",
          }}
        >
          Se connecter avec Google
        </button>
        <p style={{ color: "#aaa", fontSize: 11, margin: "24px 0 0" }}>
          Accès réservé aux collaborateurs Symbiose Paysage
        </p>
      </div>
    </div>
  )
}
