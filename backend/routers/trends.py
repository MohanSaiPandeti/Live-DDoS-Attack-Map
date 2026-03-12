from fastapi import APIRouter, Query
from services.cloudflare import fetch_traffic_trends, fetch_attack_layer3_summary
from models.schemas import TrendSummary

router = APIRouter()


@router.get("/http", response_model=TrendSummary)
async def get_http_trends(period: str = Query(default="1h", pattern="^(1h|24h|7d)$")):
    return await fetch_traffic_trends(period)


@router.get("/layer3")
async def get_layer3_summary():
    return await fetch_attack_layer3_summary()