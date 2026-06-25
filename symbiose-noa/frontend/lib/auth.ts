import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async signIn({ user }) {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/auth/google`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: user.email,
              name: user.name,
              google_id: user.id,
            }),
          }
        )
        if (!res.ok) return false
        const data = await res.json()
        ;(user as any).backendToken = data.access_token
        ;(user as any).role = data.role
        return true
      } catch {
        return false
      }
    },
    async jwt({ token, user }) {
      if (user) {
        token.backendToken = (user as any).backendToken
        token.role = (user as any).role
      }
      return token
    },
    async session({ session, token }) {
      session.backendToken = token.backendToken as string
      session.user.role = token.role as string
      return session
    },
  },
})
