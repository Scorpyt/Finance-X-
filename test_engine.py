import unittest
from datetime import datetime
from engine import IntelligenceEngine
from models import MarketEvent, SystemState

class TestIntelligenceEngine(unittest.TestCase):
    def setUp(self):
        # High decay rate for easier testing
        self.engine = IntelligenceEngine(decay_rate=0.7) 
        self.start_time = datetime(2024, 1, 1, 10, 0, 0)

    def test_relevance_scoring(self):
        evt = MarketEvent(self.start_time, "NEWS", "Test Event", 5.0, "STOCKS")
        self.engine.ingest(evt)
        self.assertEqual(len(self.engine.events), 1)
        self.assertEqual(self.engine.events[0].current_weight, 5.0)

    def test_memory_decay(self):
        evt = MarketEvent(self.start_time, "NEWS", "Test Event", 10.0, "STOCKS")
        self.engine.ingest(evt)
        
        # Advance 1 hour
        later_time = datetime(2024, 1, 1, 11, 0, 0)
        self.engine.apply_decay(later_time)
        
        # Expected: 10 * e^(-0.7 * 1) = 10 * 0.496 = ~4.96
        current_weight = self.engine.events[0].current_weight
        self.assertAlmostEqual(current_weight, 4.96, delta=0.1)

    def test_state_detection_crash(self):
        # Inject massive events
        for i in range(3):
            evt = MarketEvent(self.start_time, "CRISIS", f"Crash {i}", 9.0, "ALL")
            self.engine.ingest(evt)
            
        snapshot = self.engine.detect_state(self.start_time)
        
        # Total Risk = 9+9+9 = 27 (> 25 threshold)
        self.assertEqual(snapshot.state, SystemState.CRASH)

if __name__ == '__main__':
    unittest.main()
