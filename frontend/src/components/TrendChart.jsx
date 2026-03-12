import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#0f172a", border: "1px solid #334155",
      padding: "8px 12px", borderRadius: 6, fontSize: 12, color: "#e2e8f0"
    }}>
      <p style={{ margin: 0, color: "#94a3b8" }}>{label}</p>
      <p style={{ margin: 0, color: "#FF3B3B" }}>
        Attack %: <b>{payload[0]?.value?.toFixed(2)}%</b>
      </p>
    </div>
  );
}

export default function TrendChart({ trends }) {
  if (!trends?.trends?.length) {
    return (
      <div className="panel">
        <div className="panel-header">📈 Traffic Trends</div>
        <div className="feed-empty">Loading trend data...</div>
      </div>
    );
  }

  const data = trends.trends.map((t) => ({
    time: new Date(t.timestamp).toLocaleTimeString("en", { hour: "2-digit", minute: "2-digit" }),
    attack_pct: t.attack_percentage,
  }));

  return (
    <div className="panel">
      <div className="panel-header">
        <span>📈 DDoS Traffic Trends</span>
        <span className="badge" style={{ background: "#FF3B3B22", color: "#FF3B3B" }}>
          avg {trends.avg_attack_percentage}%
        </span>
      </div>
      <ResponsiveContainer width="100%" height={120}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
          <defs>
            <linearGradient id="attackGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#FF3B3B" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#FF3B3B" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="time" tick={{ fill: "#64748b", fontSize: 10 }} />
          <YAxis tick={{ fill: "#64748b", fontSize: 10 }} unit="%" />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="attack_pct"
            stroke="#FF3B3B"
            strokeWidth={2}
            fill="url(#attackGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}