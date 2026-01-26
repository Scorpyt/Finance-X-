# ML Module - Usage Examples

## Import from ML package

```python
# Option 1: Import from package
from ML import MLEngine, MLPredictor, MLTrainer

# Option 2: Import specific modules
from ML.ml_engine import MLEngine
from ML.ml_predictor import MLPredictor
from ML.feature_engineering import FeatureEngineer
```

## Quick Examples

### 1. Get Market Prediction
```python
from ML import MLEngine

engine = MLEngine()
prediction = engine.predict('SPY')

print(f"Direction: {prediction['final_prediction']}")
print(f"Confidence: {prediction['final_confidence']:.2%}")
print(f"Risk: {prediction['risk_level']}")
```

### 2. Train a New Model
```python
from ML import MLTrainer

trainer = MLTrainer('AAPL', lookback_days=730)
metrics = trainer.full_training_pipeline()
```

### 3. Batch Predictions
```python
from ML import MLEngine

engine = MLEngine()
predictions = engine.batch_predict(['SPY', 'QQQ', 'DIA'])

for symbol, pred in predictions.items():
    print(f"{symbol}: {pred['final_prediction']} ({pred['final_confidence']:.2%})")
```

### 4. Feature Engineering
```python
from ML import FeatureEngineer

engineer = FeatureEngineer()
X, y = engineer.prepare_training_data('SPY', lookback_days=365)

print(f"Features: {X.shape[1]}")
print(f"Samples: {X.shape[0]}")
```

## Running from Command Line

```bash
# Navigate to Finance-X root directory
cd "d:\shreyansh jharghanti\Finance-X-"

# Train model
python -m ML.ml_trainer SPY

# Get prediction
python -m ML.ml_predictor SPY

# Run tests
python -m ML.test_ml_infrastructure
```

## Installation

```bash
# Install ML dependencies
pip install -r ML/requirements_ml.txt
```

## File Structure

```
ML/
├── __init__.py                    # Package initialization
├── feature_engineering.py         # Feature extraction
├── ml_models.py                   # Model definitions
├── ml_trainer.py                  # Training pipeline
├── ml_predictor.py                # Prediction engine
├── ml_engine.py                   # Main orchestration
├── test_ml_infrastructure.py      # Test suite
├── requirements_ml.txt            # Dependencies
└── README.md                      # Documentation
```
