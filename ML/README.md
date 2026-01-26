# ML Market Prediction - Quick Start

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_ml.txt
```

### 2. Train Your First Model
```bash
python ml_trainer.py SPY
```

### 3. Make a Prediction
```bash
python ml_predictor.py SPY
```

### 4. Run Tests
```bash
python test_ml_infrastructure.py
```

## 📁 Core Files

- `feature_engineering.py` - Extract 50+ technical indicators
- `ml_models.py` - Ensemble (RF, XGB, LGBM) + LSTM models
- `ml_trainer.py` - Training pipeline with cross-validation
- `ml_predictor.py` - Real-time predictions with confidence
- `ml_engine.py` - Main orchestration & integration layer
- `test_ml_infrastructure.py` - Comprehensive test suite

## 🎯 Supported Symbols

- SPY, QQQ, DIA (US markets)
- ^NSEI, ^NSEBANK (Indian markets)
- Any symbol supported by yfinance

## 📊 Expected Performance

- Accuracy: 55-65% (better than random 50%)
- Confidence scores: 0-1 (higher = more reliable)
- Risk levels: LOW/MEDIUM/HIGH

## 🔧 Usage Examples

### Python API
```python
from ml_engine import MLEngine

engine = MLEngine()

# Single prediction
pred = engine.predict('SPY')
print(f"Direction: {pred['final_prediction']}")
print(f"Confidence: {pred['final_confidence']:.2%}")

# Batch predictions
preds = engine.batch_predict(['SPY', 'QQQ'])

# Market regime
regime = engine.get_market_regime('SPY')  # BULL/BEAR/SIDEWAYS
```

### Command Line
```bash
# Train model
python ml_trainer.py AAPL

# Get prediction
python ml_predictor.py AAPL

# Test specific component
python test_ml_infrastructure.py features
```

## 📈 Features

✅ 50+ technical indicators (RSI, MACD, Bollinger Bands, etc.)
✅ Ensemble learning (Random Forest + XGBoost + LightGBM)
✅ Optional LSTM for time-series patterns
✅ Confidence scoring & risk assessment
✅ Feature importance analysis
✅ Market regime detection
✅ Database integration for tracking
✅ Comprehensive test suite

## 🔄 Integration

Works with existing Finance-X components:
- `bloomberg_engine.py` - FX rates, sector data
- `india_engine.py` - NSE stocks
- `database.py` - Prediction storage
- `server.py` - Ready for API endpoints

## 📚 Documentation

See `walkthrough.md` for complete documentation.
