import time
from datetime import datetime, timedelta
import random
from models import MarketEvent
from engine import IntelligenceEngine
from analyst import Analyst

def run_simulation():
    print("Initializing Financial Intelligence System...")
    engine = IntelligenceEngine(decay_rate=0.2)
    analyst = Analyst()
    
    # Simulating a day from 9:00 AM
    current_time = datetime(2024, 1, 1, 9, 0, 0)
    
    # Scripted events to demonstrate state transitions
    scenario_events = [
        (datetime(2024, 1, 1, 9, 30), "Market Open - Normal trading", 2.0),
        (datetime(2024, 1, 1, 10, 15), "Breaking: Inflation data higher than expected", 7.5),
        (datetime(2024, 1, 1, 10, 45), "Rumor: Central Bank emergency meeting", 6.0),
        (datetime(2024, 1, 1, 11, 0), "Tech Sector sell-off begins", 5.0),
        (datetime(2024, 1, 1, 11, 30), "Major Exchange halts trading due to glitch", 8.0),
        (datetime(2024, 1, 1, 14, 0), "Central Bank reassures markets - nothing wrong", 3.0),
    ]
    
    event_idx = 0
    
    # Simulation Loop (1 hour per step for speed)
    for _ in range(10):
        print(f"\n================ TIME: {current_time.strftime('%H:%M')} ================")
        
        # 1. Ingest Events
        while event_idx < len(scenario_events) and scenario_events[event_idx][0] <= current_time:
            t, desc, impact = scenario_events[event_idx]
            evt = MarketEvent(
                timestamp=t,
                event_type="NEWS",
                description=desc,
                base_impact=impact,
                asset_class="GENERAL"
            )
            engine.ingest(evt)
            event_idx += 1
            
        # 2. Update Engine (Decay & State)
        engine.apply_decay(current_time)
        snapshot = engine.detect_state(current_time)
        
        # 3. Analyst Insight
        # Only ask analyst if something interesting is happening (weight > 0)
        report = analyst.explain_situation(snapshot)
        print(report)
        
        # Advance time
        current_time += timedelta(minutes=30)
        time.sleep(1) # Pause for readability

if __name__ == "__main__":
    run_simulation()
