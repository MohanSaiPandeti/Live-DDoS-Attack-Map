import httpx
from datetime import datetime, timezone, timedelta
from config import get_settings
from models.schemas import TrafficTrend, TrendSummary
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

CF_RADAR_BASE = "https://api.cloudflare.com/client/v4/radar"


async def fetch_traffic_trends(period: str = "1h") -> TrendSummary:
    if not settings.CLOUDFLARE_API_TOKEN:
        logger.warning("No Cloudflare token — returning mock trends")
        return _mock_trends(period)

    headers = {
        "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    now = datetime.now(timezone.utc)
    period_map = {"1h": 1, "24h": 24, "7d": 168}
    hours_back = period_map.get(period, 1)
    date_start = (now - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_end = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(
                f"{CF_RADAR_BASE}/http/timeseries_groups/threat_category",
                headers=headers,
                params={
                    "dateStart": date_start,
                    "dateEnd": date_end,
                    "aggInterval": "1h" if hours_back <= 24 else "1d",
                    "format": "json",
                },
            )
            resp.raise_for_status()
            return _parse_cf_response(resp.json(), period)
        except Exception as e:
            logger.error(f"Cloudflare fetch failed: {e}")
            return _mock_trends(period)


async def fetch_attack_layer3_summary() -> dict:
    if not settings.CLOUDFLARE_API_TOKEN:
        return _mock_l3_summary()

    headers = {"Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(
                f"{CF_RADAR_BASE}/attacks/layer3/summary",
                headers=headers,
                params={"dateRange": "1d"},
            )
            resp.raise_for_status()
            return resp.json().get("result", {}).get("summary_0", {})
        except Exception as e:
            logger.error(f"L3 summary failed: {e}")
            return _mock_l3_summary()


def _parse_cf_response(data: dict, period: str) -> TrendSummary:
    try:
        series = data.get("result", {}).get("serie_0", {})
        timestamps = series.get("timestamps", [])
        ddos_values = series.get("DDoS", [])
        trends = []
        for i, ts in enumerate(timestamps):
            threat_pct = float(ddos_values[i]) if i < len(ddos_values) else 0.0
            trends.append(TrafficTrend(
                timestamp=datetime.fromisoformat(ts.replace("Z", "+00:00")),
                requests_total=0,
                threats_total=0,
                attack_percentage=threat_pct,
            ))
        avg_pct = sum(t.attack_percentage for t in trends) / len(trends) if trends else 0
        peak = max(trends, key=lambda t: t.attack_percentage, default=None)
        return TrendSummary(
            period=period,
            trends=trends,
            peak_attack_time=peak.timestamp if peak else None,
            total_threats=sum(int(t.attack_percentage) for t in trends),
            avg_attack_percentage=round(avg_pct, 2),
        )
    except Exception as e:
        logger.error(f"Failed to parse Cloudflare response: {e}")
        return _mock_trends(period)


def _mock_trends(period: str) -> TrendSummary:
    import random
    now = datetime.now(timezone.utc)
    trends = []
    for i in range(12):
        ts = now - timedelta(minutes=5 * (12 - i))
        trends.append(TrafficTrend(
            timestamp=ts,
            requests_total=random.randint(50000, 500000),
            threats_total=random.randint(100, 5000),
            attack_percentage=round(random.uniform(2.0, 18.0), 2),
        ))
    avg = sum(t.attack_percentage for t in trends) / len(trends)
    peak = max(trends, key=lambda t: t.attack_percentage)
    return TrendSummary(
        period=period,
        trends=trends,
        peak_attack_time=peak.timestamp,
        total_threats=sum(t.threats_total for t in trends),
        avg_attack_percentage=round(avg, 2),
        
    )


def _mock_l3_summary() -> dict:
    return {"UDP": "58%", "TCP": "26%", "ICMP": "10%", "GRE": "6%"}