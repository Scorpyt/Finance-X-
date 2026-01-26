"""
Sentinel X - Logging Infrastructure
Institutional-grade logging with audit trail
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

class SentinelLogger:
    """
    Centralized logging system for Sentinel X.
    Provides audit trail for all system decisions.
    """
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, log_dir: Optional[Path] = None) -> logging.Logger:
        """
        Get or create a logger with the given name.
        
        Args:
            name: Logger name (typically module name)
            log_dir: Directory for log files (optional)
            
        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (if log_dir provided)
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def log_belief_update(cls, logger: logging.Logger, old_belief: dict, new_belief: dict, 
                         contributing_factors: list):
        """
        Log belief state updates with full audit trail.
        
        Args:
            logger: Logger instance
            old_belief: Previous belief distribution
            new_belief: Updated belief distribution
            contributing_factors: List of factors that influenced the update
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "BELIEF_UPDATE",
            "old_belief": old_belief,
            "new_belief": new_belief,
            "contributing_factors": contributing_factors,
            "belief_change": {
                state: new_belief[state] - old_belief[state]
                for state in old_belief.keys()
            }
        }
        
        logger.info(f"Belief Update: {json.dumps(audit_entry, indent=2)}")
    
    @classmethod
    def log_regime_transition(cls, logger: logging.Logger, from_regime: str, 
                             to_regime: str, confidence: float, triggers: list):
        """
        Log regime transitions with full context.
        
        Args:
            logger: Logger instance
            from_regime: Previous regime
            to_regime: New regime
            confidence: Confidence in transition
            triggers: Triggering factors
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "REGIME_TRANSITION",
            "from_regime": from_regime,
            "to_regime": to_regime,
            "confidence": confidence,
            "triggers": triggers
        }
        
        logger.warning(f"Regime Transition: {json.dumps(audit_entry, indent=2)}")
    
    @classmethod
    def log_model_decision(cls, logger: logging.Logger, model_name: str, 
                          decision: str, confidence: float, features_used: list):
        """
        Log individual model decisions for explainability.
        
        Args:
            logger: Logger instance
            model_name: Name of the model
            decision: Model's decision/output
            confidence: Confidence score
            features_used: Features that influenced decision
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "MODEL_DECISION",
            "model_name": model_name,
            "decision": decision,
            "confidence": confidence,
            "features_used": features_used
        }
        
        logger.debug(f"Model Decision: {json.dumps(audit_entry, indent=2)}")
    
    @classmethod
    def log_inference_cycle(cls, logger: logging.Logger, cycle_number: int, 
                           duration_ms: float, models_executed: int):
        """
        Log inference loop cycles for performance monitoring.
        
        Args:
            logger: Logger instance
            cycle_number: Inference cycle number
            duration_ms: Cycle duration in milliseconds
            models_executed: Number of models executed
        """
        logger.info(
            f"Inference Cycle #{cycle_number}: "
            f"{duration_ms:.2f}ms, {models_executed} models executed"
        )


if __name__ == "__main__":
    # Test logging
    from pathlib import Path
    
    log_dir = Path(__file__).parent.parent / "logs"
    logger = SentinelLogger.get_logger("sentinel_test", log_dir)
    
    logger.info("Sentinel X logging system initialized")
    logger.debug("Debug message test")
    logger.warning("Warning message test")
    
    # Test belief update logging
    old_belief = {"Stable": 0.7, "Transitional": 0.2, "Stressed": 0.08, "Crisis": 0.02}
    new_belief = {"Stable": 0.6, "Transitional": 0.25, "Stressed": 0.12, "Crisis": 0.03}
    
    SentinelLogger.log_belief_update(
        logger, old_belief, new_belief,
        ["volatility_spike", "correlation_compression"]
    )
    
    print("✅ Logging system test complete")
