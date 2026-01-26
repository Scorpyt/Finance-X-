"""
Sentinel X - Main Entry Point
Institution-grade autonomous financial intelligence engine

This is NOT a trading system.
This is NOT a forecasting engine.
This IS a continuous market cognition system.
"""

import argparse
import sys
from pathlib import Path

# Add sentinel_ml to path
sys.path.append(str(Path(__file__).parent))

from utils.config import SentinelConfig
from utils.logging import SentinelLogger
from inference.autonomous_loop import AutonomousInferenceLoop

logger = SentinelLogger.get_logger("sentinel_main")


def main():
    """Main entry point for Sentinel X"""
    
    parser = argparse.ArgumentParser(
        description="Sentinel X - Autonomous Financial Intelligence Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with default settings
  python sentinel_main.py

  # Start with custom inference interval (seconds)
  python sentinel_main.py --interval 60

  # Monitor specific symbols
  python sentinel_main.py --symbols SPY QQQ DIA VIX

  # Run in test mode (shorter interval, fewer symbols)
  python sentinel_main.py --test

Safety Constraints:
  - No trade recommendations
  - No price targets
  - No certainty claims
  - Always quantifies uncertainty
  - Explainability required
        """
    )
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=None,
        help='Inference interval in seconds (default: from config)'
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        default=None,
        help='Symbols to monitor (default: from config)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (30s interval, limited symbols)'
    )
    
    parser.add_argument(
        '--no-loop',
        action='store_true',
        help='Run single inference cycle without continuous loop'
    )
    
    args = parser.parse_args()
    
    # Display banner
    print_banner()
    
    # Validate safety constraints
    SentinelConfig.validate_safety()
    
    # Configure based on arguments
    if args.test:
        symbols = ["SPY", "QQQ", "VIX"]
        interval = 30
        logger.info("Running in TEST mode")
    else:
        symbols = args.symbols
        interval = args.interval
    
    # Initialize autonomous loop
    logger.info("Initializing Sentinel X...")
    loop = AutonomousInferenceLoop(
        symbols=symbols,
        inference_interval=interval
    )
    
    if args.no_loop:
        # Run single cycle
        logger.info("Running single inference cycle...")
        loop._execute_inference_cycle()
        logger.info("Single cycle complete")
        
        # Display latest state
        latest_state = loop.get_latest_state()
        if latest_state:
            print("\n" + "="*60)
            print("FINAL STATE")
            print("="*60)
            print(latest_state["explanation_context"]["narrative_summary"])
            print("="*60)
    else:
        # Start continuous loop
        loop.start()
        
        print("\n" + "="*60)
        print("SENTINEL X IS NOW ALIVE")
        print("="*60)
        print("The system is thinking continuously...")
        print("Monitoring market reality without interpretation...")
        print("Updating beliefs through Bayesian inference...")
        print("Explaining every decision path...")
        print("\nPress Ctrl+C to stop")
        print("="*60 + "\n")
        
        try:
            import time
            while True:
                time.sleep(10)
                status = loop.get_status()
                
                # Display status update
                print(f"[Cycle #{status['cycle_count']:04d}] "
                      f"Regime: {status['current_regime']} "
                      f"({status['regime_confidence']:.0%} confidence) | "
                      f"Entropy: {status['uncertainty_entropy']:.3f}")
                
        except KeyboardInterrupt:
            print("\n\nShutting down Sentinel X...")
            loop.stop()
            print("✅ System stopped gracefully")
            print("Belief state preserved for next session")


def print_banner():
    """Print Sentinel X banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                      SENTINEL X                               ║
║         Autonomous Financial Intelligence Engine             ║
║                                                               ║
║  This is NOT a trading system                                ║
║  This is NOT a forecasting engine                            ║
║  This IS a continuous market cognition system                ║
║                                                               ║
║  • Observes real-time data                                   ║
║  • Maintains internal beliefs                                ║
║  • Updates confidence dynamically                            ║
║  • Detects instability and regime transitions                ║
║  • Explains every inference path                             ║
║                                                               ║
║  Institution-Grade | Explainable | Autonomous                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


if __name__ == "__main__":
    main()
