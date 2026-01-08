"""
Enhanced Tanker Models with Rich Metadata
Extends core models.py without modifying it
"""

from dataclasses import dataclass
from typing import Optional

# Import base models
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import GeoPoint


@dataclass
class EnhancedTanker:
    """
    Extended tanker model with detailed shipping information.
    Used by enhanced server for rich visualization.
    """
    id: str
    name: str
    location: GeoPoint
    destination: str
    status: str  # "MOVING", "ANCHORED", "LOADING"
    cargo_level: float  # 0-100%
    heading: float = 0.0
    
    # NEW FIELDS - Rich metadata
    cargo_type: str = "CRUDE_OIL"  # CRUDE_OIL, REFINED, LNG
    cargo_grade: str = "WTI"  # WTI, BRENT, DUBAI, etc.
    origin_country: str = "USA"
    origin_port: str = "HOUSTON"
    destination_country: str = "NETHERLANDS"
    vessel_type: str = "VLCC"  # VLCC, Suezmax, Aframax
    dwt: int = 300000  # Deadweight tonnage
    flag: str = "🇺🇸"  # Country flag emoji
    speed_knots: float = 12.0
    eta_hours: int = 72  # Estimated time to arrival
    
    def to_dict(self):
        """Convert to JSON-serializable dict"""
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.location.lat,
            "lon": self.location.lon,
            "destination": self.destination,
            "status": self.status,
            "cargo_level": self.cargo_level,
            "heading": self.heading,
            "cargo_type": self.cargo_type,
            "cargo_grade": self.cargo_grade,
            "origin_country": self.origin_country,
            "origin_port": self.origin_port,
            "destination_country": self.destination_country,
            "vessel_type": self.vessel_type,
            "dwt": self.dwt,
            "flag": self.flag,
            "speed_knots": self.speed_knots,
            "eta_hours": self.eta_hours
        }
