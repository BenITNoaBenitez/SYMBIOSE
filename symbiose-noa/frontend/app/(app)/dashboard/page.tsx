import StatsCards from "@/components/dashboard/StatsCards"
import ActivityFeed from "@/components/dashboard/ActivityFeed"

export default function DashboardPage() {
  return (
    <div style={{ padding: 32 }}>
      <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 24 }}>Dashboard</h1>
      <StatsCards />
      <ActivityFeed />
    </div>
  )
}
