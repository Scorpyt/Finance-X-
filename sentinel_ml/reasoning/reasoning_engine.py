"""
Sentinel X - Reasoning Engine (Layer 3)
Explains WHY beliefs are changing. Provides human-readable context.

This layer interprets the belief state and provides explanations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import SentinelConfig
from utils.logging import SentinelLogger

logger = SentinelLogger.get_logger("reasoning_engine")


class ReasoningEngine:
    """
    Layer 3: Reasoning Engine
    
    Purpose: Explain why beliefs are changing
    
    Functions:
    - Identify dominant contributing features
    - Compare current state to historical crises
    - Compute similarity vectors
    - Summarize narrative pressure
    - Explain uncertainty sources
    
    Outputs must be human-readable but fully traceable.
    """
    
    def __init__(self):
        """Initialize Reasoning Engine"""
        self.logger = logger
        
        # Historical crisis library (will be expanded)
        self.crisis_library = {
            "2008_financial_crisis": {
                "period": "2008-09-01 to 2008-12-31",
                "characteristics": {
                    "vol_acceleration": 2.5,
                    "correlation_compression": 0.85,
                    "drawdown_pct": -0.45,
                    "avg_correlation": 0.75
                }
            },
            "2020_covid_crash": {
                "period": "2020-02-01 to 2020-03-31",
                "characteristics": {
                    "vol_acceleration": 3.0,
                    "correlation_compression": 0.90,
                    "drawdown_pct": -0.35,
                    "avg_correlation": 0.80
                }
            },
            "2022_rate_hike_volatility": {
                "period": "2022-01-01 to 2022-06-30",
                "characteristics": {
                    "vol_acceleration": 1.5,
                    "correlation_compression": 0.65,
                    "drawdown_pct": -0.25,
                    "avg_correlation": 0.60
                }
            }
        }
        
        self.logger.info("Reasoning Engine initialized with crisis library")
    
    def identify_dominant_features(self, features: Dict[str, float], 
                                   top_n: int = 5) -> List[Tuple[str, float, str]]:
        """
        Identify features contributing most to current state.
        
        Args:
            features: Current feature values
            top_n: Number of top features to return
            
        Returns:
            List of (feature_name, value, direction) tuples
        """
        # Score features by deviation from normal
        feature_scores = []
        
        for feature_name, value in features.items():
            # Determine if feature is elevated or depressed
            if "vol" in feature_name or "correlation" in feature_name:
                # Higher is more concerning
                direction = "↑" if value > 0.5 else "↓"
                score = abs(value)
            elif "drawdown" in feature_name or "distance" in feature_name:
                # More negative is more concerning
                direction = "↓" if value < 0 else "↑"
                score = abs(value)
            else:
                direction = "↑" if value > 0 else "↓"
                score = abs(value)
            
            feature_scores.append((feature_name, value, direction, score))
        
        # Sort by score
        feature_scores.sort(key=lambda x: x[3], reverse=True)
        
        # Return top N
        return [(name, value, direction) for name, value, direction, _ in feature_scores[:top_n]]
    
    def compute_crisis_similarity(self, current_features: Dict[str, float]) -> Dict[str, float]:
        """
        Compute similarity to historical crises.
        
        Args:
            current_features: Current feature values
            
        Returns:
            Dictionary mapping crisis names to similarity scores (0-1)
        """
        similarities = {}
        
        for crisis_name, crisis_data in self.crisis_library.items():
            crisis_features = crisis_data["characteristics"]
            
            # Compute cosine similarity
            common_features = set(current_features.keys()) & set(crisis_features.keys())
            
            if not common_features:
                similarities[crisis_name] = 0.0
                continue
            
            # Build vectors
            current_vector = np.array([current_features[f] for f in common_features])
            crisis_vector = np.array([crisis_features[f] for f in common_features])
            
            # Cosine similarity
            dot_product = np.dot(current_vector, crisis_vector)
            norm_current = np.linalg.norm(current_vector)
            norm_crisis = np.linalg.norm(crisis_vector)
            
            if norm_current > 0 and norm_crisis > 0:
                similarity = dot_product / (norm_current * norm_crisis)
                # Convert to 0-1 range
                similarity = (similarity + 1) / 2
            else:
                similarity = 0.0
            
            similarities[crisis_name] = float(similarity)
        
        return similarities
    
    def explain_belief_change(self, old_belief: Dict[str, float], 
                             new_belief: Dict[str, float],
                             features: Dict[str, float]) -> str:
        """
        Generate human-readable explanation of belief change.
        
        Args:
            old_belief: Previous belief distribution
            new_belief: Current belief distribution
            features: Current feature values
            
        Returns:
            Explanation string
        """
        # Calculate changes
        changes = {
            state: new_belief[state] - old_belief[state]
            for state in old_belief.keys()
        }
        
        # Find biggest change
        max_change_state = max(changes, key=lambda s: abs(changes[s]))
        max_change_value = changes[max_change_state]
        
        # Get dominant features
        top_features = self.identify_dominant_features(features, top_n=3)
        
        # Build explanation
        if abs(max_change_value) < 0.02:
            explanation = "Belief state remains stable with minimal change."
        elif max_change_value > 0:
            explanation = f"Belief in '{max_change_state}' regime increased by {max_change_value:.1%}. "
        else:
            explanation = f"Belief in '{max_change_state}' regime decreased by {abs(max_change_value):.1%}. "
        
        # Add feature context
        if top_features:
            feature_desc = ", ".join([f"{name} {direction}" for name, _, direction in top_features[:2]])
            explanation += f"Primary drivers: {feature_desc}."
        
        return explanation
    
    def explain_uncertainty(self, entropy: float, belief_velocity: Dict[str, float]) -> str:
        """
        Explain sources of uncertainty.
        
        Args:
            entropy: Current entropy value
            belief_velocity: Rate of belief change
            
        Returns:
            Uncertainty explanation
        """
        max_velocity = max(abs(v) for v in belief_velocity.values())
        
        if entropy > 1.5 and max_velocity > 0.1:
            return "High uncertainty: Beliefs are rapidly changing with no clear dominant regime."
        elif entropy > 1.5:
            return "High uncertainty: Multiple regimes have similar probabilities."
        elif max_velocity > 0.1:
            return "Moderate uncertainty: Beliefs are transitioning between regimes."
        else:
            return "Low uncertainty: Belief state is stable and confident."
    
    def generate_narrative_summary(self, belief_state: Dict, 
                                   features: Dict[str, float],
                                   model_agreement: float) -> str:
        """
        Generate complete narrative summary of current state.
        
        Args:
            belief_state: Current belief state from Belief Engine
            features: Current feature values
            model_agreement: Model consensus percentage
            
        Returns:
            Human-readable narrative
        """
        dominant_regime = belief_state["dominant_regime"]
        confidence = belief_state["regime_confidence"]
        entropy = belief_state["uncertainty_entropy"]
        
        # Build narrative
        narrative = []
        
        # Current state
        narrative.append(f"Current State: {dominant_regime}")
        narrative.append(f"Confidence: {confidence:.0%}")
        narrative.append(f"Model Agreement: {model_agreement:.0%}")
        
        # Primary drivers
        top_features = self.identify_dominant_features(features, top_n=3)
        narrative.append("\nPrimary Drivers:")
        for feature_name, value, direction in top_features:
            narrative.append(f"  - {feature_name}: {value:.4f} {direction}")
        
        # Historical similarity
        similarities = self.compute_crisis_similarity(features)
        if similarities:
            top_crisis = max(similarities, key=similarities.get)
            top_similarity = similarities[top_crisis]
            
            if top_similarity > 0.3:
                crisis_name = top_crisis.replace("_", " ").title()
                narrative.append(f"\nHistorical Similarity:")
                narrative.append(f"  - {top_similarity:.0%} similarity to {crisis_name}")
        
        # Uncertainty note
        uncertainty_note = self.explain_uncertainty(entropy, belief_state["belief_velocity"])
        narrative.append(f"\nUncertainty Note:")
        narrative.append(f"  {uncertainty_note}")
        
        return "\n".join(narrative)
    
    def generate_explanation_context(self, belief_state: Dict,
                                    features: Dict[str, float],
                                    model_outputs: Optional[Dict] = None) -> Dict:
        """
        Generate complete explanation context for dashboard.
        
        Args:
            belief_state: Current belief state
            features: Current feature values
            model_outputs: Optional model outputs for agreement calculation
            
        Returns:
            Dictionary with all explanation components
        """
        # Calculate model agreement
        if model_outputs:
            model_agreement = self._calculate_model_agreement(model_outputs)
        else:
            model_agreement = 0.0
        
        # Get dominant features
        dominant_features = self.identify_dominant_features(features, top_n=5)
        
        # Get crisis similarities
        crisis_similarities = self.compute_crisis_similarity(features)
        
        # Generate narrative
        narrative = self.generate_narrative_summary(belief_state, features, model_agreement)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "narrative_summary": narrative,
            "dominant_features": [
                {"name": name, "value": value, "direction": direction}
                for name, value, direction in dominant_features
            ],
            "crisis_similarities": crisis_similarities,
            "model_agreement": model_agreement,
            "uncertainty_level": "high" if belief_state["uncertainty_entropy"] > 1.5 else "medium" if belief_state["uncertainty_entropy"] > 1.0 else "low"
        }
    
    def _calculate_model_agreement(self, model_outputs: Dict) -> float:
        """Calculate percentage of models in agreement"""
        if not model_outputs:
            return 0.0
        
        # Get dominant regime from each model
        model_regimes = []
        for model_name, output in model_outputs.items():
            if isinstance(output, dict) and "regime" in output:
                model_regimes.append(output["regime"])
        
        if not model_regimes:
            return 0.0
        
        # Find most common regime
        from collections import Counter
        regime_counts = Counter(model_regimes)
        most_common_count = regime_counts.most_common(1)[0][1]
        
        agreement = most_common_count / len(model_regimes)
        return agreement


if __name__ == "__main__":
    # Test Reasoning Engine
    print("Testing Reasoning Engine...")
    print("=" * 60)
    
    reasoning = ReasoningEngine()
    
    # Sample features
    features = {
        "vol_acceleration": 1.8,
        "correlation_compression": 0.70,
        "drawdown_pct": -0.15,
        "avg_correlation": 0.65,
        "vol_30": 0.25
    }
    
    # Identify dominant features
    print("\n✅ Dominant Features:")
    top_features = reasoning.identify_dominant_features(features, top_n=3)
    for name, value, direction in top_features:
        print(f"  {name}: {value:.4f} {direction}")
    
    # Compute crisis similarity
    print("\n✅ Crisis Similarities:")
    similarities = reasoning.compute_crisis_similarity(features)
    for crisis, similarity in sorted(similarities.items(), key=lambda x: x[1], reverse=True):
        print(f"  {crisis}: {similarity:.2%}")
    
    # Generate narrative
    belief_state = {
        "dominant_regime": "Transitional",
        "regime_confidence": 0.45,
        "uncertainty_entropy": 1.3,
        "belief_velocity": {"Stable": -0.05, "Transitional": 0.08, "Stressed": -0.02, "Crisis": -0.01}
    }
    
    print("\n✅ Narrative Summary:")
    print(reasoning.generate_narrative_summary(belief_state, features, model_agreement=0.78))
    
    print("\n" + "=" * 60)
    print("Reasoning Engine test complete!")
