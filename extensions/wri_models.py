"""WRI Aqueduct Water Risk Data Models"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WaterRiskIndicators(BaseModel):
    baseline_water_stress: float
    drought_risk: float
    flood_risk: float
    water_scarcity_2030: Optional[float] = None
    overall_risk_score: float
    risk_category: str

class PortWaterRisk(BaseModel):
    port_name: str
    country: str
    latitude: float
    longitude: float
    risk_indicators: WaterRiskIndicators
    seasonal_patterns: Optional[dict] = None
    last_updated: datetime

class CommodityRegionRisk(BaseModel):
    commodity: str
    region: str
    country: str
    production_volume: Optional[float] = None
    risk_indicators: WaterRiskIndicators
    trend: str
    alert_level: str

class WaterRiskAlert(BaseModel):
    alert_id: str
    alert_type: str
    title: str
    description: str
    affected_region: str
    commodity: Optional[str] = None
    risk_score: float
    timestamp: datetime
    expires_at: Optional[datetime] = None

class WaterRiskSummary(BaseModel):
    total_ports_monitored: int
    high_risk_ports: int
    total_commodity_regions: int
    critical_alerts: int
    average_risk_score: float
    top_risk_regions: List[str]
    last_updated: datetime
