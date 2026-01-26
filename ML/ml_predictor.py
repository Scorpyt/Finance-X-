"""
ML Predictor - Real-time market prediction engine
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from feature_engineering import FeatureEngineer
from ml_models import EnsembleModel, LSTMModel


class MLPredictor:
    """
    Real-time prediction engine for market direction.
    """
    
    def __init__(self, symbol: str, model_version: str = "v1"):
        self.symbol = symbol
        self.model_version = model_version
        
        self.engineer = FeatureEngineer()
        self.ensemble_model = EnsembleModel()
        self.lstm_model = LSTMModel()
        
        self._load_models()
    
    def _load_models(self):
        """Load trained models"""
        try:
            print(f"Loading models for {self.symbol} (version: {self.model_version})...")
            self.ensemble_model.load(self.symbol, self.model_version)
            print("✓ Ensemble model loaded")
        except FileNotFoundError:
            print(f"⚠ No trained ensemble model found for {self.symbol}")
            print("  Please train the model first using ml_trainer.py")
            raise
        
        try:
            self.lstm_model.load(self.symbol, self.model_version)
            print("✓ LSTM model loaded")
        except:
            print("⚠ LSTM model not available (optional)")
    
    def predict(self, use_ensemble: bool = True, use_lstm: bool = False) -> Dict:
        """
        Make prediction for the next trading session.
        
        Args:
            use_ensemble: Use ensemble model
            use_lstm: Use LSTM model (requires TensorFlow)
            
        Returns:
            Dictionary with prediction results
        """
        print(f"\nGenerating prediction for {self.symbol}...")
        
        # Get latest features
        try:
            X, y = self.engineer.prepare_training_data(self.symbol, lookback_days=365)
            X_latest = X.iloc[[-1]]  # Last row as DataFrame
        except Exception as e:
            return {
                'error': f"Failed to fetch data: {str(e)}",
                'symbol': self.symbol,
                'timestamp': datetime.now().isoformat()
            }
        
        result = {
            'symbol': self.symbol,
            'timestamp': datetime.now().isoformat(),
            'predictions': {},
            'confidence': {},
            'final_prediction': None,
            'final_confidence': 0.0
        }
        
        # Ensemble prediction
        if use_ensemble and self.ensemble_model.is_trained:
            ensemble_pred = self.ensemble_model.predict(X_latest, use_stacking=True)[0]
            ensemble_proba = self.ensemble_model.predict_proba(X_latest, use_stacking=True)[0]
            ensemble_confidence = self.ensemble_model.get_confidence_score(X_latest)
            
            result['predictions']['ensemble'] = 'UP' if ensemble_pred == 1 else 'DOWN'
            result['confidence']['ensemble'] = float(ensemble_confidence)
            result['probability'] = {
                'down': float(ensemble_proba[0]),
                'up': float(ensemble_proba[1])
            }
        
        # LSTM prediction
        if use_lstm and self.lstm_model.is_trained:
            try:
                lstm_pred = self.lstm_model.predict(X)[0]
                lstm_proba = self.lstm_model.predict_proba(X)[0]
                
                result['predictions']['lstm'] = 'UP' if lstm_pred == 1 else 'DOWN'
                result['confidence']['lstm'] = float(max(lstm_proba))
            except Exception as e:
                print(f"LSTM prediction failed: {e}")
        
        # Determine final prediction
        if result['predictions']:
            # If both models agree, high confidence
            if len(result['predictions']) > 1:
                predictions_list = list(result['predictions'].values())
                if predictions_list[0] == predictions_list[1]:
                    result['final_prediction'] = predictions_list[0]
                    result['final_confidence'] = 0.9  # High confidence
                else:
                    # Use ensemble as primary
                    result['final_prediction'] = result['predictions']['ensemble']
                    result['final_confidence'] = 0.6  # Medium confidence
            else:
                # Only ensemble available
                result['final_prediction'] = result['predictions']['ensemble']
                result['final_confidence'] = result['confidence']['ensemble']
        
        # Risk assessment
        result['risk_level'] = self._assess_risk(result['final_confidence'])
        
        return result
    
    def _assess_risk(self, confidence: float) -> str:
        """Assess risk level based on confidence score"""
        if confidence >= 0.8:
            return "LOW"
        elif confidence >= 0.6:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def get_feature_importance(self, top_n: int = 10) -> Dict:
        """Get top influential features for current prediction"""
        top_features = self.ensemble_model.get_top_features(top_n)
        
        # Get current feature values
        X, _ = self.engineer.prepare_training_data(self.symbol, lookback_days=365)
        latest_values = X.iloc[-1].to_dict()
        
        # Combine importance with current values
        result = {}
        for model_name, features in top_features.items():
            result[model_name] = [
                {
                    'feature': feature,
                    'importance': float(importance),
                    'current_value': float(latest_values.get(feature, 0))
                }
                for feature, importance in features
            ]
        
        return result
    
    def predict_with_explanation(self) -> Dict:
        """
        Make prediction with detailed explanation.
        
        Returns:
            Dictionary with prediction and feature importance
        """
        prediction = self.predict(use_ensemble=True, use_lstm=False)
        
        if 'error' in prediction:
            return prediction
        
        # Add feature importance
        prediction['feature_importance'] = self.get_feature_importance(top_n=5)
        
        # Add interpretation
        prediction['interpretation'] = self._generate_interpretation(prediction)
        
        return prediction
    
    def _generate_interpretation(self, prediction: Dict) -> str:
        """Generate human-readable interpretation"""
        direction = prediction['final_prediction']
        confidence = prediction['final_confidence']
        risk = prediction['risk_level']
        
        interpretation = f"The model predicts the market will go {direction} "
        interpretation += f"with {confidence*100:.1f}% confidence ({risk} risk). "
        
        if 'probability' in prediction:
            prob = prediction['probability']
            interpretation += f"Probability: {prob['up']*100:.1f}% UP, {prob['down']*100:.1f}% DOWN."
        
        return interpretation
    
    def batch_predict(self, symbols: list) -> Dict[str, Dict]:
        """
        Make predictions for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to predictions
        """
        results = {}
        
        for symbol in symbols:
            print(f"\nPredicting for {symbol}...")
            try:
                predictor = MLPredictor(symbol, self.model_version)
                results[symbol] = predictor.predict()
            except Exception as e:
                results[symbol] = {
                    'error': str(e),
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat()
                }
        
        return results


def print_prediction(prediction: Dict):
    """Pretty print prediction results"""
    print("\n" + "="*60)
    print(f"MARKET PREDICTION: {prediction['symbol']}")
    print("="*60)
    
    if 'error' in prediction:
        print(f"❌ Error: {prediction['error']}")
        return
    
    print(f"\n📊 Final Prediction: {prediction['final_prediction']}")
    print(f"🎯 Confidence: {prediction['final_confidence']*100:.1f}%")
    print(f"⚠️  Risk Level: {prediction['risk_level']}")
    
    if 'probability' in prediction:
        prob = prediction['probability']
        print(f"\n📈 Probabilities:")
        print(f"   UP:   {prob['up']*100:.1f}%")
        print(f"   DOWN: {prob['down']*100:.1f}%")
    
    if 'interpretation' in prediction:
        print(f"\n💡 Interpretation:")
        print(f"   {prediction['interpretation']}")
    
    if 'feature_importance' in prediction:
        print(f"\n🔍 Top Influential Features:")
        for model_name, features in prediction['feature_importance'].items():
            print(f"\n   {model_name.upper()}:")
            for i, feat in enumerate(features[:5], 1):
                print(f"      {i}. {feat['feature']}: {feat['current_value']:.4f} (importance: {feat['importance']:.4f})")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import sys
    
    # Example usage
    symbol = sys.argv[1] if len(sys.argv) > 1 else "SPY"
    
    try:
        predictor = MLPredictor(symbol)
        prediction = predictor.predict_with_explanation()
        print_prediction(prediction)
        
    except FileNotFoundError:
        print(f"\n❌ No trained model found for {symbol}")
        print(f"Please train the model first:")
        print(f"  python ml_trainer.py {symbol}")
    except Exception as e:
        print(f"\n❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
