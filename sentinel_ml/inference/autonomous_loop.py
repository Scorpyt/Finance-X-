"""
Sentinel X - Autonomous Inference Loop
The system's heartbeat. Runs continuously without user prompts.

This is what makes Sentinel X ALIVE.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict
import json
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import SentinelConfig
from utils.logging import SentinelLogger
from perception.perception_engine import PerceptionEngine
from belief.belief_engine import BeliefEngine
from reasoning.reasoning_engine import ReasoningEngine

logger = SentinelLogger.get_logger("autonomous_loop")


class AutonomousInferenceLoop:
    """
    The Autonomous Inference Loop - Sentinel X's Heartbeat
    
    This loop runs continuously:
    1. Ingest market data
    2. Update feature tensors
    3. Apply memory decay
    4. Update belief state
    5. Compute uncertainty
    6. Detect regime shifts
    7. Generate explanations
    8. Store snapshot
    9. Sleep(interval)
    
    The system NEVER requires user prompts to operate.
    """
    
    def __init__(self, 
                 symbols: Optional[list] = None,
                 inference_interval: int = None):
        """
        Initialize the autonomous inference loop.
        
        Args:
            symbols: List of symbols to monitor
            inference_interval: Seconds between inference cycles
        """
        self.logger = logger
        
        # Initialize cognitive layers
        self.perception = PerceptionEngine(symbols=symbols)
        self.belief = BeliefEngine()
        self.reasoning = ReasoningEngine()
        
        # Loop control
        self.inference_interval = inference_interval or SentinelConfig.INFERENCE_INTERVAL_SECONDS
        self.is_running = False
        self.cycle_count = 0
        
        # Threading
        self.loop_thread = None
        
        # State storage
        self.snapshot_dir = SentinelConfig.MEMORY_DIR
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Autonomous Inference Loop initialized")
        self.logger.info(f"Inference interval: {self.inference_interval}s")
        self.logger.info(f"Monitoring {len(self.perception.symbols)} symbols")
    
    def start(self):
        """Start the autonomous inference loop in a background thread"""
        if self.is_running:
            self.logger.warning("Inference loop already running")
            return
        
        self.is_running = True
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()
        
        self.logger.info("🚀 Autonomous Inference Loop STARTED")
        self.logger.info("System is now ALIVE and thinking continuously...")
    
    def stop(self):
        """Stop the autonomous inference loop"""
        if not self.is_running:
            self.logger.warning("Inference loop not running")
            return
        
        self.is_running = False
        if self.loop_thread:
            self.loop_thread.join(timeout=10)
        
        self.logger.info("⏸️  Autonomous Inference Loop STOPPED")
    
    def _run_loop(self):
        """Main inference loop (runs in background thread)"""
        self.logger.info("Entering autonomous inference loop...")
        
        while self.is_running:
            try:
                cycle_start = time.time()
                
                # Execute one inference cycle
                self._execute_inference_cycle()
                
                cycle_duration = (time.time() - cycle_start) * 1000  # ms
                
                # Log cycle completion
                SentinelLogger.log_inference_cycle(
                    self.logger, self.cycle_count, cycle_duration, 
                    models_executed=9  # Will be dynamic later
                )
                
                # Sleep until next cycle
                time.sleep(self.inference_interval)
                
            except Exception as e:
                self.logger.error(f"Error in inference cycle: {e}", exc_info=True)
                time.sleep(self.inference_interval)  # Continue despite errors
    
    def _execute_inference_cycle(self):
        """
        Execute one complete inference cycle.
        
        This is the core cognitive process:
        PERCEPTION → BELIEF → REASONING
        """
        self.cycle_count += 1
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"INFERENCE CYCLE #{self.cycle_count}")
        self.logger.info(f"{'='*60}")
        
        # Step 1: PERCEPTION - Observe market
        self.logger.info("Step 1: Observing market reality...")
        market_data = self.perception.observe_market(lookback_days=90)
        
        if not market_data:
            self.logger.warning("No market data available, skipping cycle")
            return
        
        # Step 2: PERCEPTION - Compute features
        self.logger.info("Step 2: Computing feature tensors...")
        features = self.perception.compute_feature_tensor(market_data)
        
        # Step 3: BELIEF - Apply memory decay
        self.logger.info("Step 3: Applying confidence decay...")
        self.belief.apply_confidence_decay()
        
        # Step 4: BELIEF - Update belief state
        self.logger.info("Step 4: Updating belief state...")
        
        # Convert features to evidence for belief update
        # (Simplified - will be enhanced with actual models later)
        evidence = self._features_to_evidence(features)
        
        old_belief = self.belief.current_belief.copy()
        self.belief.update_belief_bayesian(evidence, evidence_strength=0.15)
        
        # Step 5: BELIEF - Compute uncertainty
        self.logger.info("Step 5: Computing uncertainty entropy...")
        uncertainty = self.belief.uncertainty_entropy
        transition_prob = self.belief.get_transition_probability()
        
        self.logger.info(f"  Uncertainty entropy: {uncertainty:.4f}")
        self.logger.info(f"  Transition probability: {transition_prob:.2%}")
        
        # Step 6: BELIEF - Check for regime shift
        if self.belief.current_regime != self._get_regime_from_belief(old_belief):
            self.logger.warning(f"  🚨 REGIME SHIFT DETECTED: {self._get_regime_from_belief(old_belief)} → {self.belief.current_regime}")
        
        # Step 7: REASONING - Generate explanations
        self.logger.info("Step 7: Generating explanations...")
        
        belief_state = self.belief.get_belief_state()
        
        # Get aggregated features (average across symbols)
        aggregated_features = self._aggregate_features(features)
        
        explanation_context = self.reasoning.generate_explanation_context(
            belief_state, aggregated_features
        )
        
        # Step 8: Store snapshot
        self.logger.info("Step 8: Storing state snapshot...")
        self._store_snapshot(belief_state, explanation_context, aggregated_features)
        
        # Display current state
        self._display_current_state(belief_state, explanation_context)
        
        self.logger.info(f"{'='*60}\n")
    
    def _features_to_evidence(self, features: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Convert feature tensor to evidence for belief update.
        
        This is a simplified heuristic. Will be replaced with actual models.
        """
        # Aggregate features across symbols
        aggregated = self._aggregate_features(features)
        
        # Heuristic evidence calculation
        vol_acceleration = aggregated.get('vol_acceleration', 0.0)
        avg_correlation = aggregated.get('avg_correlation', 0.0)
        drawdown = abs(aggregated.get('drawdown_pct', 0.0))
        
        # Simple rules (will be replaced with ML models)
        if vol_acceleration > 2.0 or drawdown > 0.3:
            # Crisis evidence
            evidence = {"Stable": 0.1, "Transitional": 0.2, "Stressed": 0.3, "Crisis": 0.4}
        elif vol_acceleration > 1.0 or drawdown > 0.15:
            # Stressed evidence
            evidence = {"Stable": 0.2, "Transitional": 0.3, "Stressed": 0.4, "Crisis": 0.1}
        elif avg_correlation > 0.7:
            # Transitional evidence
            evidence = {"Stable": 0.3, "Transitional": 0.5, "Stressed": 0.15, "Crisis": 0.05}
        else:
            # Stable evidence
            evidence = {"Stable": 0.6, "Transitional": 0.25, "Stressed": 0.1, "Crisis": 0.05}
        
        return evidence
    
    def _aggregate_features(self, features: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Aggregate features across all symbols (mean)"""
        if not features:
            return {}
        
        aggregated = {}
        feature_names = list(next(iter(features.values())).keys())
        
        for feature_name in feature_names:
            values = [symbol_features.get(feature_name, 0.0) 
                     for symbol_features in features.values()]
            aggregated[feature_name] = sum(values) / len(values) if values else 0.0
        
        return aggregated
    
    def _get_regime_from_belief(self, belief: Dict[str, float]) -> str:
        """Get dominant regime from belief distribution"""
        return max(belief, key=belief.get)
    
    def _store_snapshot(self, belief_state: Dict, explanation_context: Dict, 
                       features: Dict[str, float]):
        """Store complete state snapshot to disk"""
        snapshot = {
            "cycle_number": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "belief_state": belief_state,
            "explanation_context": explanation_context,
            "aggregated_features": features
        }
        
        # Save to file
        snapshot_file = self.snapshot_dir / f"snapshot_{self.cycle_count:06d}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        # Also save latest snapshot
        latest_file = self.snapshot_dir / "latest_snapshot.json"
        with open(latest_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
    
    def _display_current_state(self, belief_state: Dict, explanation_context: Dict):
        """Display current state in console"""
        print("\n" + "="*60)
        print("CURRENT MARKET STATE")
        print("="*60)
        print(explanation_context["narrative_summary"])
        print("="*60 + "\n")
    
    def get_latest_state(self) -> Optional[Dict]:
        """Get the most recent state snapshot"""
        latest_file = self.snapshot_dir / "latest_snapshot.json"
        
        if not latest_file.exists():
            return None
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def get_status(self) -> Dict:
        """Get current loop status"""
        return {
            "is_running": self.is_running,
            "cycle_count": self.cycle_count,
            "inference_interval": self.inference_interval,
            "symbols_monitored": len(self.perception.symbols),
            "current_regime": self.belief.current_regime,
            "regime_confidence": self.belief.current_belief[self.belief.current_regime],
            "uncertainty_entropy": self.belief.uncertainty_entropy
        }


if __name__ == "__main__":
    print("Sentinel X - Autonomous Inference Loop")
    print("="*60)
    
    # Initialize with small universe for testing
    test_symbols = ["SPY", "QQQ", "VIX"]
    
    loop = AutonomousInferenceLoop(
        symbols=test_symbols,
        inference_interval=30  # 30 seconds for testing
    )
    
    # Start the loop
    loop.start()
    
    print("\n✅ Autonomous loop started!")
    print("The system is now ALIVE and thinking continuously...")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Monitor status
        while True:
            time.sleep(10)
            status = loop.get_status()
            print(f"Status: Cycle #{status['cycle_count']}, "
                  f"Regime: {status['current_regime']} "
                  f"({status['regime_confidence']:.0%} confidence)")
    except KeyboardInterrupt:
        print("\n\nStopping loop...")
        loop.stop()
        print("✅ Loop stopped")
