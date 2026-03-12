from fastapi import APIRouter, Query
from services.store import get_recent_arcs, get_attack_stats
from services.abuseipdb import fetch_blacklisted_ips, build_attack_events
from services.store import ingest_attack_events
from models.schemas import AttackArc, AttackStats

router = APIRouter()


@router.get("/arcs", response_model=list[AttackArc])
async def get_arcs(limit: int = Query(default=50, le=200)):
    return get_recent_arcs(limit)


@router.get("/stats", response_model=AttackStats)
async def get_stats():
    return get_attack_stats()


@router.post("/refresh")
async def refresh_attacks():
    raw_ips = await fetch_blacklisted_ips()
    events = await build_attack_events(raw_ips)
    new_arcs = ingest_attack_events(events)
    return {
        "fetched": len(raw_ips),
        "geolocated": len(events),
        "new_arcs": len(new_arcs),
    }