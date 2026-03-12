from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GeoLocation(BaseModel):
    lat: float
    lon: float
    city: str
    country: str
    country_code: str
    isp: Optional[str] = None


class AttackEvent(BaseModel):
    ip: str
    confidence_score: int
    total_reports: int
    last_reported: datetime
    geo: GeoLocation
    categories: list[int] = []
    is_ddos: bool = True


class AttackArc(BaseModel):
    id: str
    src_lat: float
    src_lon: float
    src_city: str
    src_country: str
    dst_lat: float
    dst_lon: float
    dst_city: str
    confidence: int
    ip: str
    timestamp: datetime


class TrafficTrend(BaseModel):
    timestamp: datetime
    requests_total: int
    threats_total: int
    attack_percentage: float


class TrendSummary(BaseModel):
    period: str
    trends: list[TrafficTrend]
    peak_attack_time: Optional[datetime] = None
    total_threats: int
    avg_attack_percentage: float


class AttackStats(BaseModel):
    total_ips: int
    high_confidence: int
    countries_affected: int
    top_countries: list[dict]
    last_updated: datetime