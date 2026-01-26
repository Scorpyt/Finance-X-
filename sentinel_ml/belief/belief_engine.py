"""
Sentinel X - Belief Engine (Layer 2)
The Core Brain: Maintains internal belief state and updates continuously.

This is the system's MIND. It holds beliefs, not facts.
Beliefs evolve smoothly through Bayesian updating.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from scipy.stats import entropy
import json

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import SentinelConfig
from utils.logging import SentinelLogger

logger = SentinelLogger.get_logger("belief_engine")


class BeliefEngine:
    """
    Layer 2: Belief Engine - The Core Brain
    
    Maintains internal belief state:
    - Belief Vector: [Stable, Transitional, Stressed, Crisis]
    - Each belief sums to 1.0
    - Evolves smoothly via Bayesian updating
    
    Additional Internal States:
    - Uncertainty entropy
    - Regime persistence
    - Belief velocity (rate of change)
    - Confidence decay
    """
    
    def __init__(self, initial_belief: Optional[Dict[str, float]] = None):
        """
        Initialize Belief Engine with initial belief state.
        
        Args:
            initial_belief: Initial belief distribution (defaults to config)
        """
        self.logger = logger
        
        # Initialize belief state
        self.belief_states = SentinelConfig.BELIEF_STATES
        self.current_belief = initial_belief or SentinelConfig.INITIAL_BELIEF.copy()
        
        # Validate belief distribution
        self._validate_belief()
        
        # Internal state tracking
        self.belief_history = [self.current_belief.copy()]
        self.belief_timestamps = [datetime.now()]
        
        # Uncertainty tracking
        self.uncertainty_entropy = self._calculate_entropy(self.current_belief)
        self.entropy_history = [self.uncertainty_entropy]
        
        # Regime persistence
        self.current_regime = self._get_dominant_regime()
        self.regime_start_time = datetime.now()
        self.days_in_current_regime = 0
        
        # Belief velocity (rate of change)
        self.belief_velocity = {state: 0.0 for state in self.belief_states}
        
        # Confidence decay factor
        self.confidence_decay_rate = 0.95  # Decay per update
        
        self.logger.info(f"Belief Engine initialized: {self.current_belief}")
        self.logger.info(f"Initial regime: {self.current_regime}")
    
    def _validate_belief(self):
        """Ensure belief distribution is valid (sums to 1.0)"""
        total = sum(self.current_belief.values())
        if not np.isclose(total, 1.0, atol=1e-6):
            raise ValueError(f"Belief distribution must sum to 1.0, got {total}")
        
        for state, prob in self.current_belief.items():
            if prob < 0 or prob > 1:
                raise ValueError(f"Belief probability must be in [0, 1], got {prob} for {state}")
    
    def _calculate_entropy(self, belief: Dict[str, float]) -> float:
        """
        Calculate Shannon entropy of belief distribution.
        Higher entropy = more uncertainty
        """
        probs = list(belief.values())
        return float(entropy(probs, base=2))
    
    def _get_dominant_regime(self) -> str:
        """Get the regime with highest belief"""
        return max(self.current_belief, key=self.current_belief.get)
    
    def update_belief_bayesian(self, evidence: Dict[str, float], 
                               evidence_strength: float = 0.1):
        """
        Update beliefs using Bayesian updating.
        
        Args:
            evidence: Evidence for each state (unnormalized)
            evidence_strength: How much to weight new evidence (0-1)
        """
        old_belief = self.current_belief.copy()
        
        # Bayesian update: P(state|evidence) ∝ P(evidence|state) * P(state)
        new_belief = {}
        for state in self.belief_states:
            # Likelihood * Prior
            likelihood = evidence.get(state, 0.5)  # Default to neutral
            prior = old_belief[state]
            
            # Weighted combination
            new_belief[state] = (1 - evidence_strength) * prior + evidence_strength * likelihood
        
        # Normalize to sum to 1.0
        total = sum(new_belief.values())
        if total > 0:
            new_belief = {state: prob / total for state, prob in new_belief.items()}
        else:
            new_belief = old_belief.copy()
        
        # Update belief state
        self.current_belief = new_belief
        self._validate_belief()
        
        # Update internal states
        self._update_internal_states(old_belief)
        
        # Log belief update
        SentinelLogger.log_belief_update(
            self.logger, old_belief, new_belief,
            [f"{state}: {evidence.get(state, 0.5):.3f}" for state in self.belief_states]
        )
    
    def update_belief_hmm(self, observation: np.ndarray, transition_matrix: np.ndarray):
        """
        Update beliefs using Hidden Markov Model inference.
        
        Args:
            observation: Current observation vector
            transition_matrix: State transition probabilities
        """
        # Convert current belief to state vector
        state_vector = np.array([self.current_belief[state] for state in self.belief_states])
        
        # HMM update: P(state_t|obs) ∝ P(obs|state_t) * Σ P(state_t|state_{t-1}) * P(state_{t-1})
        # Simplified: state_vector @ transition_matrix
        new_state_vector = state_vector @ transition_matrix
        
        # Incorporate observation
        new_state_vector = new_state_vector * observation
        
        # Normalize
        new_state_vector = new_state_vector / new_state_vector.sum()
        
        # Update belief
        old_belief = self.current_belief.copy()
        self.current_belief = {
            state: float(prob) 
            for state, prob in zip(self.belief_states, new_state_vector)
        }
        
        self._update_internal_states(old_belief)
    
    def update_belief_ensemble(self, model_outputs: Dict[str, Dict[str, float]], 
                              model_weights: Optional[Dict[str, float]] = None):
        """
        Update beliefs using ensemble of model outputs.
        
        Args:
            model_outputs: Dictionary mapping model names to belief distributions
            model_weights: Optional weights for each model
        """
        if not model_outputs:
            return
        
        # Default to equal weights
        if model_weights is None:
            model_weights = {model: 1.0 / len(model_outputs) for model in model_outputs.keys()}
        
        # Weighted average of model beliefs
        ensemble_belief = {state: 0.0 for state in self.belief_states}
        
        for model_name, model_belief in model_outputs.items():
            weight = model_weights.get(model_name, 0.0)
            for state in self.belief_states:
                ensemble_belief[state] += weight * model_belief.get(state, 0.0)
        
        # Normalize
        total = sum(ensemble_belief.values())
        if total > 0:
            ensemble_belief = {state: prob / total for state, prob in ensemble_belief.items()}
        
        # Update belief
        old_belief = self.current_belief.copy()
        self.current_belief = ensemble_belief
        
        self._update_internal_states(old_belief)
        
        self.logger.info(f"Ensemble belief update from {len(model_outputs)} models")
    
    def _update_internal_states(self, old_belief: Dict[str, float]):
        """Update all internal state variables"""
        # Update entropy
        self.uncertainty_entropy = self._calculate_entropy(self.current_belief)
        self.entropy_history.append(self.uncertainty_entropy)
        
        # Update belief velocity (rate of change)
        for state in self.belief_states:
            self.belief_velocity[state] = self.current_belief[state] - old_belief[state]
        
        # Update regime tracking
        new_regime = self._get_dominant_regime()
        if new_regime != self.current_regime:
            # Regime transition detected
            SentinelLogger.log_regime_transition(
                self.logger, self.current_regime, new_regime,
                self.current_belief[new_regime],
                [f"{state}: {self.belief_velocity[state]:+.3f}" for state in self.belief_states]
            )
            
            self.current_regime = new_regime
            self.regime_start_time = datetime.now()
            self.days_in_current_regime = 0
        else:
            # Update persistence
            time_in_regime = (datetime.now() - self.regime_start_time).total_seconds() / 86400
            self.days_in_current_regime = time_in_regime
        
        # Store history
        self.belief_history.append(self.current_belief.copy())
        self.belief_timestamps.append(datetime.now())
        
        # Trim history (keep last 1000 updates)
        if len(self.belief_history) > 1000:
            self.belief_history = self.belief_history[-1000:]
            self.belief_timestamps = self.belief_timestamps[-1000:]
            self.entropy_history = self.entropy_history[-1000:]
    
    def apply_confidence_decay(self):
        """
        Apply exponential decay to confidence.
        Beliefs drift toward uncertainty over time without new evidence.
        """
        # Move beliefs slightly toward uniform distribution
        uniform_belief = {state: 1.0 / len(self.belief_states) for state in self.belief_states}
        
        decay_factor = self.confidence_decay_rate
        
        decayed_belief = {}
        for state in self.belief_states:
            decayed_belief[state] = (
                decay_factor * self.current_belief[state] + 
                (1 - decay_factor) * uniform_belief[state]
            )
        
        self.current_belief = decayed_belief
        self._validate_belief()
    
    def get_belief_state(self) -> Dict:
        """
        Get complete belief state snapshot.
        
        Returns:
            Dictionary containing all belief information
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "current_belief": self.current_belief.copy(),
            "dominant_regime": self.current_regime,
            "regime_confidence": self.current_belief[self.current_regime],
            "uncertainty_entropy": self.uncertainty_entropy,
            "days_in_regime": self.days_in_current_regime,
            "belief_velocity": self.belief_velocity.copy(),
            "is_transitioning": max(abs(v) for v in self.belief_velocity.values()) > 0.05
        }
    
    def get_regime_persistence(self) -> float:
        """
        Calculate regime persistence score (0-1).
        Higher = more stable regime
        """
        if len(self.belief_history) < 10:
            return 1.0
        
        # Check how consistent the dominant regime has been
        recent_regimes = [
            max(belief, key=belief.get) 
            for belief in self.belief_history[-10:]
        ]
        
        persistence = sum(1 for r in recent_regimes if r == self.current_regime) / len(recent_regimes)
        return persistence
    
    def get_transition_probability(self) -> float:
        """
        Estimate probability of regime transition in next update.
        Based on belief velocity and entropy.
        """
        # High velocity + high entropy = high transition probability
        max_velocity = max(abs(v) for v in self.belief_velocity.values())
        normalized_entropy = self.uncertainty_entropy / 2.0  # Max entropy is 2.0 for 4 states
        
        transition_prob = (max_velocity + normalized_entropy) / 2.0
        return min(transition_prob, 1.0)
    
    def save_state(self, filepath: str):
        """Save belief engine state to file"""
        state = {
            "current_belief": self.current_belief,
            "current_regime": self.current_regime,
            "regime_start_time": self.regime_start_time.isoformat(),
            "days_in_current_regime": self.days_in_current_regime,
            "uncertainty_entropy": self.uncertainty_entropy,
            "belief_velocity": self.belief_velocity,
            "belief_history": self.belief_history[-100:],  # Last 100 updates
            "timestamps": [ts.isoformat() for ts in self.belief_timestamps[-100:]]
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        self.logger.info(f"Belief state saved to {filepath}")
    
    def load_state(self, filepath: str):
        """Load belief engine state from file"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.current_belief = state["current_belief"]
        self.current_regime = state["current_regime"]
        self.regime_start_time = datetime.fromisoformat(state["regime_start_time"])
        self.days_in_current_regime = state["days_in_current_regime"]
        self.uncertainty_entropy = state["uncertainty_entropy"]
        self.belief_velocity = state["belief_velocity"]
        self.belief_history = state["belief_history"]
        self.belief_timestamps = [datetime.fromisoformat(ts) for ts in state["timestamps"]]
        
        self.logger.info(f"Belief state loaded from {filepath}")


if __name__ == "__main__":
    # Test Belief Engine
    print("Testing Belief Engine...")
    print("=" * 60)
    
    # Initialize
    belief_engine = BeliefEngine()
    print(f"\n✅ Initial belief: {belief_engine.current_belief}")
    print(f"✅ Initial regime: {belief_engine.current_regime}")
    print(f"✅ Uncertainty entropy: {belief_engine.uncertainty_entropy:.4f}")
    
    # Simulate evidence updates
    print("\n--- Simulating market stress evidence ---")
    stress_evidence = {
        "Stable": 0.3,
        "Transitional": 0.4,
        "Stressed": 0.5,
        "Crisis": 0.2
    }
    
    belief_engine.update_belief_bayesian(stress_evidence, evidence_strength=0.2)
    print(f"Updated belief: {belief_engine.current_belief}")
    print(f"New regime: {belief_engine.current_regime}")
    print(f"Belief velocity: {belief_engine.belief_velocity}")
    
    # Get state
    state = belief_engine.get_belief_state()
    print(f"\n✅ Belief state:")
    print(f"  Dominant regime: {state['dominant_regime']}")
    print(f"  Confidence: {state['regime_confidence']:.2%}")
    print(f"  Transitioning: {state['is_transitioning']}")
    print(f"  Transition probability: {belief_engine.get_transition_probability():.2%}")
    
    print("\n" + "=" * 60)
    print("Belief Engine test complete!")
