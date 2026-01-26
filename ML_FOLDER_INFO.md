# Finance-X ML Module

The ML module has been organized into a separate folder: `ML/`

## 📁 Folder Structure

```
Finance-X/
└── ML/
    ├── __init__.py                    # Package initialization
    ├── feature_engineering.py         # 50+ technical indicators
    ├── ml_models.py                   # Ensemble + LSTM models
    ├── ml_trainer.py                  # Training pipeline
    ├── ml_predictor.py                # Real-time predictions
    ├── ml_engine.py                   # Main orchestration
    ├── test_ml_infrastructure.py      # Test suite
    ├── requirements_ml.txt            # ML dependencies
    ├── README.md                      # Quick start guide
    └── USAGE.md                       # Usage examples
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r ML/requirements_ml.txt
```

### 2. Import and Use
```python
# Import from ML package
from ML import MLEngine

# Get prediction
engine = MLEngine()
prediction = engine.predict('SPY')
print(f"{prediction['final_prediction']} with {prediction['final_confidence']:.2%} confidence")
```

### 3. Train a Model
```bash
python -m ML.ml_trainer SPY
```

### 4. Get Prediction
```bash
python -m ML.ml_predictor SPY
```

### 5. Run Tests
```bash
python -m ML.test_ml_infrastructure
```

## 📚 Documentation

- **README.md** - Quick start and features
- **USAGE.md** - Detailed usage examples
- **walkthrough.md** (in artifacts) - Complete documentation

## 🔗 Integration

The ML module integrates with existing Finance-X components:
- Uses `database.py` for storing predictions
- Compatible with `bloomberg_engine.py` and `india_engine.py`
- Ready for `server.py` API endpoints

## ✅ What's Included

- ✅ Feature engineering (50+ indicators)
- ✅ Ensemble models (RF, XGB, LGBM)
- ✅ LSTM for time-series
- ✅ Training pipeline
- ✅ Real-time predictions
- ✅ Confidence scoring
- ✅ Market regime detection
- ✅ Comprehensive tests

All ML code is now cleanly organized in the `ML/` folder!
