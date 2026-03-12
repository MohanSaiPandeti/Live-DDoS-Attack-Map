import { useState, useEffect } from "react";

const API_BASE = "http://localhost:8000/api";

export function useTrends(period = "1h", refreshInterval = 300000) {
  const [trends, setTrends] = useState(null);
  const [layer3, setLayer3] = useState(null);

  const fetchTrends = async () => {
    try {
      const [trendRes, l3Res] = await Promise.all([
        fetch(`${API_BASE}/trends/http?period=${period}`),
        fetch(`${API_BASE}/trends/layer3`),
      ]);
      setTrends(await trendRes.json());
      setLayer3(await l3Res.json());
    } catch (err) {
      console.error("Failed to fetch trends:", err);
    }
  };

  useEffect(() => {
    fetchTrends();
    const interval = setInterval(fetchTrends, refreshInterval);
    return () => clearInterval(interval);
  }, [period]);

  return { trends, layer3 };
}