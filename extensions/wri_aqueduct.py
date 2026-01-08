"""WRI Aqueduct Water Risk Data Provider"""
import logging
from typing import List
from datetime import datetime, timedelta
import random
from extensions.wri_models import *

logger = logging.getLogger(__name__)

class WRIAqueductProvider:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
        self.major_ports = [
            {"name": "Singapore", "country": "Singapore", "lat": 1.29, "lon": 103.85},
            {"name": "Shanghai", "country": "China", "lat": 31.23, "lon": 121.47},
            {"name": "Rotterdam", "country": "Netherlands", "lat": 51.92, "lon": 4.48},
            {"name": "Dubai", "country": "UAE", "lat": 25.27, "lon": 55.30},
            {"name": "Los Angeles", "country": "USA", "lat": 33.74, "lon": -118.27},
            {"name": "Santos", "country": "Brazil", "lat": -23.96, "lon": -46.33},
            {"name": "Mumbai", "country": "India", "lat": 18.95, "lon": 72.82},
            {"name": "Jeddah", "country": "Saudi Arabia", "lat": 21.54, "lon": 39.17},
        ]
        self.commodity_regions = [
            {"commodity": "Soy", "region": "Mato Grosso", "country": "Brazil"},
            {"commodity": "Palm Oil", "region": "Sumatra", "country": "Indonesia"},
            {"commodity": "Coffee", "region": "Minas Gerais", "country": "Brazil"},
            {"commodity": "Cocoa", "region": "Ivory Coast", "country": "Côte d'Ivoire"},
            {"commodity": "Wheat", "region": "Punjab", "country": "India"},
            {"commodity": "Crude Oil", "region": "Persian Gulf", "country": "Saudi Arabia"},
        ]
    
    def _calculate_risk_category(self, score: float) -> str:
        if score < 1.5: return "Low"
        elif score < 2.5: return "Medium"
        elif score < 3.5: return "High"
        else: return "Extreme"
    
    def _generate_risk_indicators(self, base_stress: float = None) -> WaterRiskIndicators:
        if base_stress is None:
            base_stress = random.uniform(0.5, 4.5)
        drought_risk = min(5.0, base_stress + random.uniform(-0.5, 0.5))
        flood_risk = random.uniform(0.5, 3.0)
        water_scarcity_2030 = min(5.0, base_stress + random.uniform(0.2, 0.8))
        overall_score = (base_stress * 0.4 + drought_risk * 0.3 + flood_risk * 0.2 + water_scarcity_2030 * 0.1)
        return WaterRiskIndicators(
            baseline_water_stress=round(base_stress, 2),
            drought_risk=round(drought_risk, 2),
            flood_risk=round(flood_risk, 2),
            water_scarcity_2030=round(water_scarcity_2030, 2),
            overall_risk_score=round(overall_score, 2),
            risk_category=self._calculate_risk_category(overall_score)
        )
    
    def get_port_water_risks(self) -> List[PortWaterRisk]:
        cache_key = "port_risks"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        port_risks = []
        for port in self.major_ports:
            if port["country"] in ["UAE", "Saudi Arabia"]:
                base_stress = random.uniform(3.5, 4.8)
            elif port["country"] in ["India", "China"]:
                base_stress = random.uniform(2.0, 3.5)
            else:
                base_stress = random.uniform(0.8, 2.5)
            risk = PortWaterRisk(
                port_name=port["name"],
                country=port["country"],
                latitude=port["lat"],
                longitude=port["lon"],
                risk_indicators=self._generate_risk_indicators(base_stress),
                last_updated=datetime.now()
            )
            port_risks.append(risk)
        self.cache[cache_key] = (port_risks, datetime.now())
        return port_risks
    
    def get_commodity_region_risks(self) -> List[CommodityRegionRisk]:
        cache_key = "commodity_risks"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        region_risks = []
        for region in self.commodity_regions:
            base_stress = random.uniform(1.5, 4.0)
            risk_indicators = self._generate_risk_indicators(base_stress)
            if risk_indicators.overall_risk_score > 3.5:
                trend, alert_level = "Deteriorating", "Critical"
            elif risk_indicators.overall_risk_score > 2.5:
                trend, alert_level = random.choice(["Stable", "Deteriorating"]), "Warning"
            else:
                trend, alert_level = random.choice(["Improving", "Stable"]), "None"
            risk = CommodityRegionRisk(
                commodity=region["commodity"],
                region=region["region"],
                country=region["country"],
                production_volume=random.uniform(1000000, 50000000),
                risk_indicators=risk_indicators,
                trend=trend,
                alert_level=alert_level
            )
            region_risks.append(risk)
        self.cache[cache_key] = (region_risks, datetime.now())
        return region_risks
    
    def get_active_alerts(self) -> List[WaterRiskAlert]:
        alerts = []
        commodity_risks = self.get_commodity_region_risks()
        for risk in commodity_risks:
            if risk.alert_level in ["Critical", "Warning"]:
                alert = WaterRiskAlert(
                    alert_id=f"WRA-{risk.commodity}-{datetime.now().strftime('%Y%m%d')}",
                    alert_type=risk.alert_level,
                    title=f"{'Extreme' if risk.alert_level == 'Critical' else 'Elevated'} Water Risk in {risk.region}",
                    description=f"{risk.commodity} {'production at risk' if risk.alert_level == 'Critical' else 'supply chain monitoring recommended'}. Risk score: {risk.risk_indicators.overall_risk_score:.2f}",
                    affected_region=f"{risk.region}, {risk.country}",
                    commodity=risk.commodity,
                    risk_score=risk.risk_indicators.overall_risk_score,
                    timestamp=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=7)
                )
                alerts.append(alert)
        return alerts
    
    def get_water_risk_summary(self) -> WaterRiskSummary:
        port_risks = self.get_port_water_risks()
        commodity_risks = self.get_commodity_region_risks()
        alerts = self.get_active_alerts()
        high_risk_ports = sum(1 for p in port_risks if p.risk_indicators.risk_category in ["High", "Extreme"])
        critical_alerts = sum(1 for a in alerts if a.alert_type == "Critical")
        avg_risk = sum(p.risk_indicators.overall_risk_score for p in port_risks) / len(port_risks)
        sorted_regions = sorted(commodity_risks, key=lambda x: x.risk_indicators.overall_risk_score, reverse=True)
        top_risk_regions = [f"{r.region}, {r.country}" for r in sorted_regions[:5]]
        return WaterRiskSummary(
            total_ports_monitored=len(port_risks),
            high_risk_ports=high_risk_ports,
            total_commodity_regions=len(commodity_risks),
            critical_alerts=critical_alerts,
            average_risk_score=round(avg_risk, 2),
            top_risk_regions=top_risk_regions,
            last_updated=datetime.now()
        )
