import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        token: { type: "text" },
        email: { type: "email" },
      },
      async authorize({ token, email }) {
        try {
          const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/auth/magic-link/verify`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ token, email }),
            }
          )
          if (!res.ok) return null
          const data = await res.json()
          return {
            id: email as string,
            email: email as string,
            backendToken: data.access_token,
            role: data.role,
          }
        } catch {
          return null
        }
      },
    }),
  ],
  pages: {
    signIn: "/login",
  },
  trustHost: true,
  callbacks: {
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
