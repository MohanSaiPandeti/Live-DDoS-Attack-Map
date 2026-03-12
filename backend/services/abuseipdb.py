import httpx
import asyncio
from datetime import datetime
from typing import Optional
from config import get_settings
from models.schemas import AttackEvent, GeoLocation
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

ABUSEIPDB_BASE = "https://api.abuseipdb.com/api/v2"


async def fetch_blacklisted_ips() -> list[dict]:
    if not settings.ABUSEIPDB_API_KEY:
        logger.warning("No AbuseIPDB API key — returning mock data")
        return _mock_ip_data()

    headers = {
        "Key": settings.ABUSEIPDB_API_KEY,
        "Accept": "application/json",
    }
    params = {
        "confidenceMinimum": settings.ABUSEIPDB_CONFIDENCE_THRESHOLD,
        "limit": settings.ABUSEIPDB_LIMIT,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(
                f"{ABUSEIPDB_BASE}/blacklist",
                headers=headers,
                params=params,
            )
            resp.raise_for_status()
            return resp.json().get("data", [])
        except Exception as e:
            logger.error(f"AbuseIPDB fetch failed: {e}")
            return _mock_ip_data()


async def geolocate_ip(ip: str) -> Optional[GeoLocation]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                f"{settings.GEO_API_BASE}/{ip}",
                params={"fields": "status,lat,lon,city,country,countryCode,isp"},
            )
            data = resp.json()
            if data.get("status") != "success":
                return None
            return GeoLocation(
                lat=data["lat"],
                lon=data["lon"],
                city=data.get("city", "Unknown"),
                country=data.get("country", "Unknown"),
                country_code=data.get("countryCode", "??"),
                isp=data.get("isp"),
            )
        except Exception as e:
            logger.warning(f"Geo lookup failed for {ip}: {e}")
            return None


async def geolocate_batch(ips: list[str], batch_size: int = 10) -> dict[str, Optional[GeoLocation]]:
    results = {}
    for i in range(0, len(ips), batch_size):
        batch = ips[i:i + batch_size]
        tasks = [geolocate_ip(ip) for ip in batch]
        geos = await asyncio.gather(*tasks)
        for ip, geo in zip(batch, geos):
            results[ip] = geo
        if i + batch_size < len(ips):
            await asyncio.sleep(1.5)
    return results


async def build_attack_events(raw_ips: list[dict]) -> list[AttackEvent]:
    filtered = [
        ip for ip in raw_ips
        if ip.get("abuseConfidenceScore", 0) >= settings.ABUSEIPDB_CONFIDENCE_THRESHOLD
    ]
    ip_list = [entry["ipAddress"] for entry in filtered]
    geo_map = await geolocate_batch(ip_list)

    events = []
    for entry in filtered:
        ip = entry["ipAddress"]
        geo = geo_map.get(ip)
        if not geo:
            continue
        event = AttackEvent(
            ip=ip,
            confidence_score=entry.get("abuseConfidenceScore", 0),
            total_reports=entry.get("totalReports", 0),
            last_reported=datetime.fromisoformat(
                entry.get("lastReportedAt", datetime.utcnow().isoformat()).replace("Z", "+00:00")
            ),
            geo=geo,
            categories=entry.get("categories", []),
            is_ddos=True,
        )
        events.append(event)
    return events


def _mock_ip_data() -> list[dict]:
    from datetime import timezone
    now = datetime.now(timezone.utc).isoformat()
    return [
        {"ipAddress": "1.2.3.4", "abuseConfidenceScore": 95, "totalReports": 234, "lastReportedAt": now, "categories": [4, 7]},
        {"ipAddress": "5.6.7.8", "abuseConfidenceScore": 88, "totalReports": 89, "lastReportedAt": now, "categories": [5, 10]},
        {"ipAddress": "9.10.11.12", "abuseConfidenceScore": 92, "totalReports": 156, "lastReportedAt": now, "categories": [7]},
        {"ipAddress": "185.220.101.1", "abuseConfidenceScore": 99, "totalReports": 512, "lastReportedAt": now, "categories": [4, 5, 7]},
        {"ipAddress": "45.142.212.1", "abuseConfidenceScore": 85, "totalReports": 67, "lastReportedAt": now, "categories": [10]},
    ]