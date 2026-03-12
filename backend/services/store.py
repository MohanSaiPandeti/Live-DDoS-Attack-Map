import uuid
from datetime import datetime, timezone
from collections import deque
from models.schemas import AttackEvent, AttackArc, AttackStats

TARGET = {"lat": 17.3850, "lon": 78.4867, "city": "Hyderabad", "country": "India"}

_attack_events: list[AttackEvent] = []
_attack_arcs: deque[AttackArc] = deque(maxlen=200)
_seen_ips: set[str] = set()


def get_all_arcs() -> list[AttackArc]:
    return list(_attack_arcs)


def get_recent_arcs(limit: int = 50) -> list[AttackArc]:
    arcs = list(_attack_arcs)
    return arcs[-limit:]


def get_attack_stats() -> AttackStats:
    events = _attack_events
    if not events:
        return AttackStats(
            total_ips=0,
            high_confidence=0,
            countries_affected=0,
            top_countries=[],
            last_updated=datetime.now(timezone.utc),
        )

    high_conf = [e for e in events if e.confidence_score >= 90]
    country_counts: dict[str, int] = {}
    for e in events:
        cc = e.geo.country
        country_counts[cc] = country_counts.get(cc, 0) + 1

    top_countries = sorted(
        [{"country": k, "count": v} for k, v in country_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:5]

    return AttackStats(
        total_ips=len(events),
        high_confidence=len(high_conf),
        countries_affected=len(country_counts),
        top_countries=top_countries,
        last_updated=datetime.now(timezone.utc),
    )


def ingest_attack_events(events: list[AttackEvent]) -> list[AttackArc]:
    new_arcs = []
    for event in events:
        if event.ip in _seen_ips:
            continue
        _seen_ips.add(event.ip)
        _attack_events.append(event)
        arc = AttackArc(
            id=str(uuid.uuid4()),
            src_lat=event.geo.lat,
            src_lon=event.geo.lon,
            src_city=event.geo.city,
            src_country=event.geo.country,
            dst_lat=TARGET["lat"],
            dst_lon=TARGET["lon"],
            dst_city=TARGET["city"],
            confidence=event.confidence_score,
            ip=event.ip,
            timestamp=event.last_reported,
        )
        _attack_arcs.append(arc)
        new_arcs.append(arc)
    return new_arcs


def clear_store():
    global _attack_events
    _attack_events = []
    _attack_arcs.clear()
    _seen_ips.clear()