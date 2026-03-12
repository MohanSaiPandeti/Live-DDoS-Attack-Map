import GlobeView from "./components/GlobeView";
import AttackFeed from "./components/AttackFeed";
import TrendChart from "./components/TrendChart";
import StatsBar from "./components/StatsBar";
import { useWebSocket } from "./hooks/useWebSocket";
import { useTrends } from "./hooks/useTrends";
import "./index.css";

export default function App() {
  const { arcs, stats, connected } = useWebSocket("ws://localhost:8000/ws");
  const { trends, layer3 } = useTrends();

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <span className="logo">⚡ DDoS Live Map</span>
          <span className={`status-dot ${connected ? "online" : "offline"}`} />
          <span className="status-label">{connected ? "LIVE" : "CONNECTING..."}</span>
        </div>
        <div className="header-right">
          {stats && (
            <>
              <span className="stat-pill">{stats.total_ips} IPs tracked</span>
              <span className="stat-pill red">{stats.high_confidence} critical</span>
              <span className="stat-pill">{stats.countries_affected} countries</span>
            </>
          )}
        </div>
      </header>

      <main className="main-layout">
        <div className="globe-container">
          <GlobeView arcs={arcs} />
        </div>
        <aside className="sidebar">
          <StatsBar stats={stats} layer3={layer3} />
          <TrendChart trends={trends} />
          <AttackFeed arcs={arcs} />
        </aside>
      </main>
    </div>
  );
}