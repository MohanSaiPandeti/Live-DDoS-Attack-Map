export default function StatsBar({ stats, layer3 }) {
  const l3Colors = { UDP: "#FF3B3B", TCP: "#4ECDC4", ICMP: "#FFD700", GRE: "#A855F7" };

  return (
    <div className="panel">
      <div className="panel-header">📊 Attack Overview</div>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value red">{stats?.total_ips ?? "—"}</div>
          <div className="stat-label">Total IPs</div>
        </div>
        <div className="stat-card">
          <div className="stat-value orange">{stats?.high_confidence ?? "—"}</div>
          <div className="stat-label">Critical ≥90%</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats?.countries_affected ?? "—"}</div>
          <div className="stat-label">Countries</div>
        </div>
      </div>

      {stats?.top_countries?.length > 0 && (
        <>
          <div className="section-label">Top Sources</div>
          {stats.top_countries.map((c) => (
            <div key={c.country} className="country-row">
              <span>{c.country}</span>
              <div className="country-bar-wrap">
                <div
                  className="country-bar"
                  style={{
                    width: `${Math.min(100, (c.count / stats.total_ips) * 100)}%`,
                  }}
                />
              </div>
              <span className="country-count">{c.count}</span>
            </div>
          ))}
        </>
      )}

      {layer3 && (
        <>
          <div className="section-label" style={{ marginTop: 10 }}>Protocol Breakdown (L3)</div>
          {Object.entries(layer3).map(([proto, pct]) => (
            <div key={proto} className="country-row">
              <span>{proto}</span>
              <div className="country-bar-wrap">
                <div
                  className="country-bar"
                  style={{
                    width: pct,
                    background: l3Colors[proto] || "#94a3b8",
                  }}
                />
              </div>
              <span className="country-count">{pct}</span>
            </div>
          ))}
        </>
      )}
    </div>
  );
}