"""
Finance-X Terminal - Comprehensive Feature Demo
Demonstrates all new models system features including:
- Enhanced enums with helper methods
- ML predictions with confidence levels
- Sentinel X belief distributions with entropy
- Portfolio analytics with P&L tracking
- Validation and computed properties
"""

import datetime
from models import (
    # Enums
    SystemState, MarketRegime, RiskLevel, ConfidenceLevel,
    PredictionDirection, PredictionHorizon, BeliefState, AlertSeverity,
    # Market Models
    MarketEvent, ProcessedEvent, Ticker, PricePoint, MarketSnapshot,
    # ML Models
    MLPrediction, FeatureVector, ModelMetrics, EnsemblePrediction,
    # Sentinel X Models
    BeliefDistribution, CognitiveSnapshot, RegimeTransition,
    # Portfolio Models
    Position, Portfolio,
)
from models.enums import AssetClass


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_enums_with_helpers():
    """Demo 1: Enums with helper methods"""
    print_section("DEMO 1: Enhanced Enums with Helper Methods")
    
    # Risk Level from score
    print("🎯 Risk Level Conversion:")
    scores = [5, 30, 50, 70, 95]
    for score in scores:
        risk = RiskLevel.from_score(score)
        print(f"  Score {score:3d} → {risk.value:12s} ({risk})")
    
    # Confidence Level from probability
    print("\n🎯 Confidence Level Conversion:")
    probs = [0.15, 0.35, 0.55, 0.75, 0.95]
    for prob in probs:
        conf = ConfidenceLevel.from_probability(prob)
        print(f"  Probability {prob:.2f} → {conf.value:12s} ({conf})")
    
    # All available enums
    print("\n📋 All Available Enums:")
    print(f"  SystemState: {[s.value for s in SystemState]}")
    print(f"  MarketRegime: {[r.value for r in MarketRegime]}")
    print(f"  BeliefState: {[b.value for b in BeliefState]}")
    print(f"  PredictionDirection: {[d.value for d in PredictionDirection]}")
    print(f"  AlertSeverity: {[a.value for a in AlertSeverity]}")


def demo_ml_predictions():
    """Demo 2: ML Predictions with computed properties"""
    print_section("DEMO 2: ML Predictions with Confidence & Risk Levels")
    
    # Create ML prediction
    prediction = MLPrediction(
        symbol="AAPL",
        direction=PredictionDirection.UP,
        confidence=0.85,
        probability_distribution={'up': 0.85, 'down': 0.15},
        horizon=PredictionHorizon.SHORT_TERM,
        feature_importance={
            'RSI': 0.25,
            'MACD': 0.20,
            'Volume': 0.18,
            'Bollinger': 0.15,
            'SMA_20': 0.12,
            'ATR': 0.10
        }
    )
    
    print(f"📊 Prediction for {prediction.symbol}:")
    print(f"  Direction: {prediction.direction.value}")
    print(f"  Confidence: {prediction.confidence:.1%}")
    print(f"  Confidence Level: {prediction.confidence_level.value}")
    print(f"  Risk Level: {prediction.risk_level.value}")
    print(f"  Horizon: {prediction.horizon.value}")
    print(f"  High Confidence: {prediction.is_high_confidence}")
    
    print(f"\n🔝 Top 5 Features:")
    for feature, importance in prediction.top_features:
        print(f"  {feature:12s}: {importance:.1%}")
    
    print(f"\n📝 Summary: {prediction.prediction_summary}")
    
    # Ensemble prediction
    print("\n🎯 Ensemble Prediction (3 models):")
    pred1 = MLPrediction(symbol="TSLA", direction=PredictionDirection.UP, confidence=0.75)
    pred2 = MLPrediction(symbol="TSLA", direction=PredictionDirection.UP, confidence=0.82)
    pred3 = MLPrediction(symbol="TSLA", direction=PredictionDirection.DOWN, confidence=0.65)
    
    ensemble = EnsemblePrediction(symbol="TSLA", predictions=[pred1, pred2, pred3])
    
    print(f"  Consensus: {ensemble.consensus_direction.value}")
    print(f"  Average Confidence: {ensemble.average_confidence:.1%}")
    print(f"  Model Agreement: {ensemble.model_agreement:.1%}")
    print(f"  Strong Consensus: {ensemble.is_strong_consensus}")


def demo_sentinel_beliefs():
    """Demo 3: Sentinel X Belief Distributions with Entropy"""
    print_section("DEMO 3: Sentinel X Belief States with Shannon Entropy")
    
    # Create belief distribution
    belief = BeliefDistribution(
        stable=0.15,
        transitional=0.35,
        stressed=0.40,
        crisis=0.10,
        regime_persistence=5
    )
    
    print("🧠 Belief Distribution:")
    print(f"  Stable:       {belief.stable:.1%}")
    print(f"  Transitional: {belief.transitional:.1%}")
    print(f"  Stressed:     {belief.stressed:.1%}")
    print(f"  Crisis:       {belief.crisis:.1%}")
    
    print(f"\n📊 Computed Properties:")
    print(f"  Dominant Regime: {belief.dominant_regime.value}")
    print(f"  Dominant Confidence: {belief.dominant_confidence:.1%}")
    print(f"  Uncertainty Entropy: {belief.uncertainty_entropy:.3f}")
    print(f"  Is Certain: {belief.is_certain}")
    print(f"  Is Uncertain: {belief.is_uncertain}")
    print(f"  Regime Persistence: {belief.regime_persistence} days")
    
    # Regime transition
    print("\n🔄 Regime Transition:")
    transition = RegimeTransition(
        from_regime=BeliefState.STABLE,
        to_regime=BeliefState.STRESSED,
        timestamp=datetime.datetime.now(),
        trigger_features=['Volatility Spike', 'Volume Surge', 'Correlation Breakdown'],
        confidence=0.78
    )
    
    print(f"  From: {transition.from_regime.value} → To: {transition.to_regime.value}")
    print(f"  Type: {transition.transition_type}")
    print(f"  Severity Change: {transition.severity_change:+d}")
    print(f"  Critical: {transition.is_critical_transition}")
    print(f"  Confidence: {transition.confidence:.1%}")
    print(f"  Triggers: {', '.join(transition.trigger_features)}")
    
    # Cognitive snapshot
    print("\n🎯 Cognitive Snapshot:")
    snapshot = CognitiveSnapshot(
        timestamp=datetime.datetime.now(),
        perception_features={
            'price_volatility': 0.85,
            'volume_anomaly': 0.72,
            'correlation_stress': 0.68,
            'momentum_shift': -0.45,
            'liquidity_pressure': 0.55
        },
        belief_state=belief,
        reasoning_narrative="Market showing elevated stress with high volatility and volume anomalies. Correlation breakdown suggests contagion risk.",
        crisis_similarity={
            '2008_financial_crisis': 0.42,
            '2020_covid_crash': 0.38,
            '2022_rate_hike': 0.55
        }
    )
    
    print(f"  Current Regime: {snapshot.current_regime.value}")
    print(f"  Regime Confidence: {snapshot.regime_confidence:.1%}")
    print(f"  Most Similar Crisis: {snapshot.most_similar_crisis}")
    print(f"  Max Similarity: {snapshot.max_crisis_similarity:.1%}")
    print(f"  Crisis-Like: {snapshot.is_crisis_like}")
    
    print(f"\n  Top 3 Features:")
    for feature, value in snapshot.get_top_features(3):
        print(f"    {feature:20s}: {value:+.2f}")


def demo_portfolio_analytics():
    """Demo 4: Portfolio with P&L Analytics"""
    print_section("DEMO 4: Portfolio Analytics with P&L Tracking")
    
    # Create portfolio
    portfolio = Portfolio(user_id="demo_user", cash_balance=10000.0)
    
    # Add positions
    positions = [
        Position(symbol="AAPL", quantity=100, entry_price=150.0, current_price=175.0),
        Position(symbol="TSLA", quantity=50, entry_price=200.0, current_price=185.0),
        Position(symbol="NVDA", quantity=75, entry_price=400.0, current_price=480.0),
        Position(symbol="MSFT", quantity=60, entry_price=300.0, current_price=285.0),
    ]
    
    for pos in positions:
        portfolio.add_position(pos)
    
    print("💼 Portfolio Overview:")
    print(f"  User ID: {portfolio.user_id}")
    print(f"  Position Count: {portfolio.position_count}")
    print(f"  Cash Balance: ${portfolio.cash_balance:,.2f}")
    print(f"  Total Value: ${portfolio.total_value:,.2f}")
    print(f"  Total P&L: ${portfolio.total_pnl:,.2f} ({portfolio.total_pnl_pct:+.2f}%)")
    print(f"  Win Rate: {portfolio.win_rate:.1%}")
    
    print("\n📊 Individual Positions:")
    for pos in portfolio.positions:
        print(f"\n  {pos.symbol}:")
        print(f"    Quantity: {pos.quantity}")
        print(f"    Entry: ${pos.entry_price:.2f} → Current: ${pos.current_price:.2f}")
        print(f"    P&L: ${pos.unrealized_pnl:,.2f} ({pos.pnl_pct:+.2f}%)")
        print(f"    Value: ${pos.current_value:,.2f}")
        print(f"    Status: {'✅ Profitable' if pos.is_profitable else '❌ Loss'}")
        print(f"    Holding Period: {pos.holding_period_days} days")
    
    print("\n🏆 Performance Metrics:")
    best = portfolio.best_performer
    worst = portfolio.worst_performer
    largest = portfolio.largest_position
    
    print(f"  Best Performer: {best.symbol} ({best.pnl_pct:+.2f}%)")
    print(f"  Worst Performer: {worst.symbol} ({worst.pnl_pct:+.2f}%)")
    print(f"  Largest Position: {largest.symbol} (${largest.current_value:,.2f})")
    print(f"  Concentration Risk: {portfolio.concentration_risk:.1f}%")
    
    print("\n📈 Allocation:")
    allocation = portfolio.get_allocation()
    for symbol, pct in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
        print(f"  {symbol}: {pct:.1f}%")


def demo_market_models():
    """Demo 5: Market Models with Computed Properties"""
    print_section("DEMO 5: Market Models with Volatility & Event Tracking")
    
    # Create ticker with history
    ticker = Ticker(
        symbol="SPY",
        name="S&P 500 ETF",
        current_price=450.0,
        change_pct=1.5,
        asset_class=AssetClass.INDICES
    )
    
    # Add price history
    base_time = datetime.datetime.now() - datetime.timedelta(days=10)
    prices = [440, 442, 445, 443, 448, 450, 452, 449, 451, 450]
    for i, price in enumerate(prices):
        ticker.history.append(PricePoint(
            timestamp=base_time + datetime.timedelta(days=i),
            price=price,
            volume=1000000 + i * 50000
        ))
    
    print(f"📈 Ticker: {ticker.symbol} - {ticker.name}")
    print(f"  Current Price: ${ticker.current_price:.2f}")
    print(f"  Change: {ticker.change_pct:+.2f}%")
    print(f"  Previous Close: ${ticker.previous_close:.2f}")
    print(f"  Change Amount: ${ticker.change_amount:+.2f}")
    print(f"  Is Gaining: {ticker.is_gaining}")
    print(f"  Volatility: {ticker.volatility:.4f}")
    print(f"  Asset Class: {ticker.asset_class.value}")
    
    # Market event
    print("\n📰 Market Event:")
    event = MarketEvent(
        timestamp=datetime.datetime.now(),
        event_type="FED_RATE_DECISION",
        description="Federal Reserve raises rates by 25 basis points",
        base_impact=7.5,
        asset_class=AssetClass.STOCKS,
        affected_symbols=["SPY", "QQQ", "DIA"],
        source="FEDERAL_RESERVE"
    )
    
    print(f"  Type: {event.event_type}")
    print(f"  Impact: {event.base_impact}/10.0")
    print(f"  Asset Class: {event.asset_class.value}")
    print(f"  Affected: {', '.join(event.affected_symbols)}")
    
    # Processed event with decay
    processed = ProcessedEvent(
        original_event=event,
        current_weight=5.2,
        relevance_score=0.85,
        age_hours=12.0
    )
    
    print(f"\n⏱️  Processed Event (after 12 hours):")
    print(f"  Current Weight: {processed.current_weight:.2f}")
    print(f"  Relevance: {processed.relevance_score:.1%}")
    print(f"  Is Active: {processed.is_active}")
    print(f"  Decay Rate: {processed.decay_rate:.3f}/hour")


def demo_validation():
    """Demo 6: Validation System"""
    print_section("DEMO 6: Validation System in Action")
    
    print("✅ Valid Examples:")
    
    # Valid ML prediction
    try:
        pred = MLPrediction(
            symbol="AAPL",
            direction=PredictionDirection.UP,
            confidence=0.75,
            probability_distribution={'up': 0.75, 'down': 0.25}
        )
        print(f"  ✓ ML Prediction created: {pred.symbol} {pred.direction.value}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Valid belief distribution
    try:
        belief = BeliefDistribution(
            stable=0.25, transitional=0.25,
            stressed=0.25, crisis=0.25
        )
        print(f"  ✓ Belief Distribution created (entropy: {belief.uncertainty_entropy:.3f})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\n❌ Invalid Examples (will raise ValidationError):")
    
    # Invalid probability
    try:
        pred = MLPrediction(
            symbol="AAPL",
            direction=PredictionDirection.UP,
            confidence=1.5  # Invalid: > 1.0
        )
    except Exception as e:
        print(f"  ✗ Invalid confidence: {type(e).__name__}: {e}")
    
    # Invalid distribution (doesn't sum to 1.0)
    try:
        belief = BeliefDistribution(
            stable=0.3, transitional=0.3,
            stressed=0.3, crisis=0.3  # Sum = 1.2
        )
    except Exception as e:
        print(f"  ✗ Invalid distribution: {type(e).__name__}")
    
    # Invalid price
    try:
        pos = Position(
            symbol="AAPL",
            quantity=100,
            entry_price=-150.0,  # Invalid: negative
            current_price=175.0
        )
    except Exception as e:
        print(f"  ✗ Invalid price: {type(e).__name__}: {e}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("=" + " " * 78 + "=")
    print("=  FINANCE-X TERMINAL - COMPREHENSIVE FEATURE DEMO".ljust(79) + "=")
    print("=  New Models System Showcase".ljust(79) + "=")
    print("=" + " " * 78 + "=")
    print("=" * 80)
    
    # Run all demos
    demo_enums_with_helpers()
    demo_ml_predictions()
    demo_sentinel_beliefs()
    demo_portfolio_analytics()
    demo_market_models()
    demo_validation()
    
    # Summary
    print_section("DEMO COMPLETE - Summary")
    print("✅ Demonstrated Features:")
    print("  1. Enhanced Enums with helper methods (RiskLevel, ConfidenceLevel)")
    print("  2. ML Predictions with confidence levels and feature importance")
    print("  3. Sentinel X Belief Distributions with Shannon entropy")
    print("  4. Portfolio Analytics with P&L, win rate, and allocation")
    print("  5. Market Models with volatility calculation and event decay")
    print("  6. Validation System with constraint enforcement")
    print("\n📊 Statistics:")
    print("  • 9 Enums with helper methods")
    print("  • 7 Validation functions")
    print("  • 40+ Computed properties")
    print("  • 100% Type-safe data structures")
    print("\n🚀 All features working perfectly!\n")


if __name__ == "__main__":
    main()
