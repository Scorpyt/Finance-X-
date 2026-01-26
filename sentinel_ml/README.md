# Sentinel X - Autonomous Financial Intelligence Engine

## 🏛️ What is Sentinel X?

Sentinel X is an **institution-grade autonomous financial intelligence engine** designed for:
- Market instability detection
- Regime classification  
- Contextual risk awareness
- Explainable AI decision-making

### ⛔ What Sentinel X is NOT:
- **NOT** a trading system
- **NOT** a forecasting engine
- **NOT** a price prediction tool

### ✅ What Sentinel X IS:
- A **continuous market cognition system**
- A **belief-driven autonomous intelligence**
- An **explainable institutional-grade platform**
- A **living analytical brain** that thinks continuously

---

## 🧠 Three-Layer Cognitive Architecture

Sentinel X operates as a living system with three interconnected layers:

```
PERCEPTION → BELIEF → REASONING
```

### Layer 1: Perception Engine
- **Purpose**: Continuously observe raw market reality
- **Inputs**: Price returns, volatility, correlation, volume, macro indicators
- **Outputs**: Normalized feature tensors
- **Key**: Pure sensing, no interpretation

### Layer 2: Belief Engine (The Core Brain)
- **Purpose**: Maintain internal belief state
- **Belief Vector**: [Stable, Transitional, Stressed, Crisis]
- **Updates**: Bayesian updating, HMM inference, ensemble consensus
- **Internal States**: Uncertainty entropy, regime persistence, belief velocity

### Layer 3: Reasoning Engine
- **Purpose**: Explain WHY beliefs are changing
- **Functions**: Feature importance, crisis similarity, narrative generation
- **Outputs**: Human-readable explanations with full traceability

---

## 🔄 Autonomous Inference Loop

The system runs continuously without user prompts:

```python
while system_active:
    ingest_market_data()
    update_feature_tensors()
    apply_memory_decay()
    update_belief_state()
    compute_uncertainty_entropy()
    detect_regime_shift_probability()
    retrieve_similar_historical_states()
    generate_explanatory_context()
    store_snapshot()
    sleep(interval)
```

This is the system's **heartbeat** - it never stops thinking.

---

## 🚀 Quick Start

### Installation

```bash
cd sentinel_ml
pip install -r requirements.txt
```

### Run Sentinel X

```bash
# Start with default settings
python sentinel_main.py

# Test mode (30s interval, limited symbols)
python sentinel_main.py --test

# Custom interval and symbols
python sentinel_main.py --interval 60 --symbols SPY QQQ DIA VIX

# Single inference cycle (no continuous loop)
python sentinel_main.py --no-loop
```

### Expected Output

```
╔═══════════════════════════════════════════════════════════════╗
║                      SENTINEL X                               ║
║         Autonomous Financial Intelligence Engine             ║
╚═══════════════════════════════════════════════════════════════╝

✅ All safety constraints validated
🚀 Autonomous Inference Loop STARTED
System is now ALIVE and thinking continuously...

[Cycle #0001] Regime: Stable (70% confidence) | Entropy: 1.234
[Cycle #0002] Regime: Stable (68% confidence) | Entropy: 1.289
...
```

---

## 📊 Feature Groups

Sentinel X extracts **50+ features** across 6 groups:

1. **Price Behavior** (5 features)
   - log_return, rolling_return_5d/20d, drawdown_pct, price_distance_from_high

2. **Volatility Structure** (5 features)
   - vol_30, vol_90, vol_180, vol_ratio_30_180, vol_acceleration

3. **Correlation & Contagion** (3 features)
   - avg_correlation, correlation_change, correlation_dispersion

4. **Energy & Macro Context** (4 features)
   - energy_shock_index, oil_volatility, inflation_delta, rate_change_velocity

5. **Event Pressure** (3 features)
   - event_count, weighted_event_score, decay_adjusted_event_score

6. **Regime Memory** (3 features)
   - regime_persistence, days_in_current_regime, transition_frequency

---

## 🎯 Core Principles

### 1. No Prediction Certainty
- Never output directional price targets
- Always quantify uncertainty
- Express probabilities, not outcomes

### 2. Belief-Based Intelligence
- Maintain internal belief vectors
- Update beliefs continuously
- Never reset state unless explicitly commanded

### 3. Explainability-First
- Every output traces back to features, models, memory
- Full confidence contribution analysis
- Audit trail for all decisions

### 4. Autonomy Through Inference Loops
- Runs without user prompts
- Updates state on timed intervals
- Accumulates pressure and decays memory naturally

### 5. Local Cognition
- Training may occur offline
- Inference runs on user CPU/GPU
- GPU acceleration for vector math

---

## 📁 Project Structure

```
sentinel_ml/
├── perception/
│   └── perception_engine.py      # Layer 1: Market observation
├── belief/
│   └── belief_engine.py           # Layer 2: Internal mind
├── reasoning/
│   └── reasoning_engine.py        # Layer 3: Explainability
├── inference/
│   └── autonomous_loop.py         # Continuous inference heartbeat
├── utils/
│   ├── config.py                  # Configuration & safety
│   └── logging.py                 # Audit trail logging
├── models/                        # Statistical, unsupervised, regime, similarity
├── memory/                        # State snapshots
├── data/                          # Raw, cleaned, features, labels
├── sentinel_main.py               # Main entry point
└── requirements.txt               # Dependencies
```

---

## 🔒 Safety Constraints

Sentinel X enforces **mandatory safety rules**:

```python
SAFETY_RULES = {
    "no_trade_recommendations": True,
    "no_price_targets": True,
    "no_certainty_claims": True,
    "always_quantify_uncertainty": True,
    "explainability_required": True
}
```

These constraints are **validated on startup** and cannot be disabled.

---

## 📈 Output Format

Example system output:

```
Current State: Transitional
Confidence: 81%
Model Agreement: 7 / 9 models

Primary Drivers:
  - Correlation compression (↑)
  - Volatility acceleration (↑)
  - Narrative divergence (↑)

Historical Similarity:
  - 32% similarity to Feb 2020 early-stage
  - 18% similarity to Aug 2011

Uncertainty Note:
  Confidence entropy rising. System stability decreasing.
```

**No deterministic claims. Only probabilistic awareness.**

---

## 🧪 Testing

```bash
# Run test mode
python sentinel_main.py --test

# Single inference cycle
python sentinel_main.py --no-loop

# Monitor specific symbols
python sentinel_main.py --symbols SPY QQQ VIX --interval 30
```

---

## 🛠️ Development Status

### ✅ Completed
- Three-layer cognitive architecture
- Autonomous inference loop
- Belief state management
- Feature extraction (price, volatility, correlation)
- Explainability engine
- Safety constraints
- Logging & audit trail

### 🚧 In Progress
- Statistical models (Z-score, EWMA, changepoint)
- Unsupervised models (Isolation Forest, HDBSCAN)
- Regime models (HMM, regime classifier)
- Similarity models (DTW, cosine similarity)
- Memory system (short/mid/long-term)
- News intelligence integration
- Dashboard & API

### 📋 Planned
- Global stock universe (40,000+ stocks)
- Multi-threading optimization
- GPU acceleration
- Distributed training
- Crisis backtesting
- Walk-forward validation

---

## 🎓 Philosophy

Sentinel X is designed to be:
- **Conservative**: Emphasizes uncertainty over confidence
- **Institutional**: Production-grade code quality
- **Explainable**: Every decision is traceable
- **Autonomous**: Thinks continuously without prompts
- **Living**: Adaptive, self-evolving, not static

> "This system must feel alive, adaptive, and self-evolving — not reactive, not scripted, not static."

---

## 📞 Support

For questions or issues:
1. Check the implementation plan: `implementation_plan.md`
2. Review the task breakdown: `task.md`
3. Examine the code documentation (inline comments)

---

## ⚖️ License & Compliance

Sentinel X is designed for:
- Risk awareness (not action)
- Market intelligence (not trading signals)
- Institutional compliance (auditable, explainable)

**This system communicates risk awareness, not action.**

---

## 🌟 Vision

Sentinel X represents:
- A continuously thinking market intelligence brain
- A belief-driven autonomous system
- An explainable institutional-grade platform
- A personal supercomputer for market awareness
- Elite technology made accessible

**The system is ALIVE. It observes. It believes. It explains. It never stops thinking.**
