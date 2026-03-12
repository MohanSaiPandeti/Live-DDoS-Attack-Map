import { useEffect, useRef } from "react";

function confidenceColor(score) {
  if (score >= 90) return "#FF3B3B";
  if (score >= 80) return "#FF8C00";
  return "#FFD700";
}

function timeAgo(isoString) {
  const diff = (Date.now() - new Date(isoString)) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export default function AttackFeed({ arcs }) {
  const feedRef = useRef(null);
  const sorted = [...arcs].reverse().slice(0, 30);

  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = 0;
  }, [arcs.length]);

  return (
    <div className="panel">
      <div className="panel-header">
        <span>🔴 Live Attack Feed</span>
        <span className="badge">{arcs.length}</span>
      </div>
      <div className="feed-list" ref={feedRef}>
        {sorted.length === 0 && (
          <div className="feed-empty">Waiting for attack data...</div>
        )}
        {sorted.map((arc) => (
          <div key={arc.id} className="feed-item">
            <div className="feed-ip" style={{ color: confidenceColor(arc.confidence) }}>
              {arc.ip}
            </div>
            <div className="feed-meta">
              <span>📍 {arc.src_city}, {arc.src_country}</span>
              <span className="feed-time">{timeAgo(arc.timestamp)}</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div
                className="confidence-bar"
                style={{
                  width: `${arc.confidence}%`,
                  background: confidenceColor(arc.confidence),
                }}
              />
              <span style={{ fontSize: 11, fontFamily: "monospace", color: confidenceColor(arc.confidence) }}>
                {arc.confidence}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}