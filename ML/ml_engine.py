"""
ML Engine - Main orchestration layer for market prediction ML system
Integrates with existing Bloomberg and India engines
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import threading
import time

from feature_engineering import FeatureEngineer
from ml_models import EnsembleModel, LSTMModel
from ml_trainer import MLTrainer
from ml_predictor import MLPredictor


class MLEngine:
    """
    Main ML Engine for Finance-X platform.
    Provides market predictions, model management, and performance tracking.
    """
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.predictors = {}  # Cache of loaded predictors
        self.prediction_cache = {}  # Cache predictions
        self.cache_ttl = 3600  # 1 hour cache
        
        # Supported symbols for prediction
        self.supported_symbols = [
            'SPY',   # S&P 500
            'QQQ',   # Nasdaq 100
            'DIA',   # Dow Jones
            '^NSEI', # NIFTY 50
            '^NSEBANK', # Bank NIFTY
        ]
        
        self.auto_retrain_enabled = False
        self.retrain_thread = None
    
    def get_predictor(self, symbol: str, version: str = "v1") -> MLPredictor:
        """
        Get or create predictor for a symbol.
        
        Args:
            symbol: Stock/index symbol
            version: Model version
            
        Returns:
            MLPredictor instance
        """
        cache_key = f"{symbol}_{version}"
        
        if cache_key not in self.predictors:
            try:
                self.predictors[cache_key] = MLPredictor(symbol, version)
            except FileNotFoundError:
                raise ValueError(f"No trained model found for {symbol}. Please train first.")
        
        return self.predictors[cache_key]
    
    def predict(self, symbol: str, use_cache: bool = True) -> Dict:
        """
        Get market prediction for a symbol.
        
        Args:
            symbol: Stock/index symbol
            use_cache: Whether to use cached prediction
            
        Returns:
            Prediction dictionary
        """
        # Check cache
        if use_cache and symbol in self.prediction_cache:
            cached = self.prediction_cache[symbol]
            cache_time = datetime.fromisoformat(cached['timestamp'])
            
            if (datetime.now() - cache_time).seconds < self.cache_ttl:
                cached['from_cache'] = True
                return cached
        
        # Generate new prediction
        try:
            predictor = self.get_predictor(symbol)
            prediction = predictor.predict_with_explanation()
            
            # Cache it
            self.prediction_cache[symbol] = prediction
            
            # Store in database
            if self.db_manager:
                self._store_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            return {
                'error': str(e),
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
    
    def batch_predict(self, symbols: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Get predictions for multiple symbols.
        
        Args:
            symbols: List of symbols (defaults to all supported)
            
        Returns:
            Dictionary mapping symbols to predictions
        """
        if symbols is None:
            symbols = self.supported_symbols
        
        results = {}
        for symbol in symbols:
            results[symbol] = self.predict(symbol)
        
        return results
    
    def train_model(self, symbol: str, lookback_days: int = 730, 
                    test_size: float = 0.2, train_lstm: bool = False) -> Dict:
        """
        Train ML model for a symbol.
        
        Args:
            symbol: Stock/index symbol
            lookback_days: Days of historical data
            test_size: Test set fraction
            train_lstm: Whether to train LSTM
            
        Returns:
            Training metrics
        """
        print(f"\n{'='*60}")
        print(f"Training model for {symbol}")
        print(f"{'='*60}\n")
        
        trainer = MLTrainer(symbol, lookback_days)
        metrics = trainer.full_training_pipeline(
            test_size=test_size,
            train_lstm=train_lstm,
            cross_validate=False,
            save_models=True
        )
        
        # Store model metadata in database
        if self.db_manager:
            self._store_model_metadata(symbol, metrics)
        
        # Clear predictor cache for this symbol
        cache_key = f"{symbol}_v1"
        if cache_key in self.predictors:
            del self.predictors[cache_key]
        
        return metrics
    
    def get_model_performance(self, symbol: str, days: int = 30) -> Dict:
        """
        Get model performance metrics over time.
        
        Args:
            symbol: Stock/index symbol
            days: Number of days to analyze
            
        Returns:
            Performance statistics
        """
        if not self.db_manager:
            return {'error': 'Database not available'}
        
        # Query predictions from database
        query = """
            SELECT prediction_date, predicted_direction, actual_direction, confidence_score
            FROM ml_predictions
            WHERE symbol = ? AND prediction_date >= ?
            ORDER BY prediction_date DESC
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            predictions = self.db_manager.execute_query(
                query, 
                (symbol, start_date.isoformat())
            )
            
            if not predictions:
                return {'error': 'No historical predictions found'}
            
            # Calculate metrics
            total = len(predictions)
            correct = sum(1 for p in predictions if p[1] == p[2] and p[2] is not None)
            accuracy = correct / total if total > 0 else 0
            
            avg_confidence = np.mean([p[3] for p in predictions if p[3] is not None])
            
            return {
                'symbol': symbol,
                'period_days': days,
                'total_predictions': total,
                'correct_predictions': correct,
                'accuracy': accuracy,
                'average_confidence': float(avg_confidence),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def update_actual_outcomes(self):
        """
        Update actual outcomes for past predictions.
        Compares predicted vs actual market direction.
        """
        if not self.db_manager:
            return
        
        # Get predictions without actual outcomes
        query = """
            SELECT id, symbol, prediction_date, predicted_direction
            FROM ml_predictions
            WHERE actual_direction IS NULL
            AND prediction_date < ?
        """
        
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        try:
            predictions = self.db_manager.execute_query(query, (yesterday,))
            
            for pred_id, symbol, pred_date, predicted_dir in predictions:
                # Fetch actual data
                import yfinance as yf
                
                pred_datetime = datetime.fromisoformat(pred_date)
                next_day = pred_datetime + timedelta(days=1)
                
                data = yf.download(symbol, start=pred_datetime, end=next_day + timedelta(days=2), progress=False)
                
                if len(data) >= 2:
                    actual_direction = 'UP' if data['Close'].iloc[1] > data['Close'].iloc[0] else 'DOWN'
                    
                    # Update database
                    update_query = """
                        UPDATE ml_predictions
                        SET actual_direction = ?
                        WHERE id = ?
                    """
                    self.db_manager.execute_query(update_query, (actual_direction, pred_id))
            
            print(f"Updated {len(predictions)} prediction outcomes")
            
        except Exception as e:
            print(f"Error updating outcomes: {e}")
    
    def _store_prediction(self, prediction: Dict):
        """Store prediction in database"""
        if 'error' in prediction:
            return
        
        try:
            query = """
                INSERT INTO ml_predictions 
                (symbol, prediction_date, predicted_direction, confidence_score, model_version, features_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            import json
            features_json = json.dumps(prediction.get('feature_importance', {}))
            
            self.db_manager.execute_query(
                query,
                (
                    prediction['symbol'],
                    prediction['timestamp'],
                    prediction['final_prediction'],
                    prediction['final_confidence'],
                    'v1',
                    features_json
                )
            )
        except Exception as e:
            print(f"Error storing prediction: {e}")
    
    def _store_model_metadata(self, symbol: str, metrics: Dict):
        """Store model training metadata"""
        try:
            ensemble_metrics = metrics.get('ensemble', {})
            
            query = """
                INSERT INTO ml_models
                (model_name, model_type, version, trained_date, accuracy, precision_score, recall_score, f1_score, model_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db_manager.execute_query(
                query,
                (
                    symbol,
                    'ensemble',
                    'v1',
                    datetime.now().isoformat(),
                    ensemble_metrics.get('accuracy', 0),
                    ensemble_metrics.get('precision', 0),
                    ensemble_metrics.get('recall', 0),
                    ensemble_metrics.get('f1', 0),
                    f"ml_models/{symbol}_v1"
                )
            )
        except Exception as e:
            print(f"Error storing model metadata: {e}")
    
    def start_auto_retrain(self, symbols: List[str], interval_days: int = 7):
        """
        Start automatic model retraining.
        
        Args:
            symbols: Symbols to retrain
            interval_days: Days between retraining
        """
        self.auto_retrain_enabled = True
        
        def retrain_loop():
            while self.auto_retrain_enabled:
                for symbol in symbols:
                    print(f"\nAuto-retraining model for {symbol}...")
                    try:
                        self.train_model(symbol)
                    except Exception as e:
                        print(f"Auto-retrain failed for {symbol}: {e}")
                
                # Sleep for interval
                time.sleep(interval_days * 24 * 3600)
        
        self.retrain_thread = threading.Thread(target=retrain_loop, daemon=True)
        self.retrain_thread.start()
        
        print(f"Auto-retrain started for {symbols} (every {interval_days} days)")
    
    def stop_auto_retrain(self):
        """Stop automatic retraining"""
        self.auto_retrain_enabled = False
        print("Auto-retrain stopped")
    
    def get_market_regime(self, symbol: str) -> str:
        """
        Detect current market regime (bull/bear/sideways).
        
        Args:
            symbol: Stock/index symbol
            
        Returns:
            Market regime string
        """
        import yfinance as yf
        
        # Get 6 months of data
        data = yf.download(symbol, period='6mo', progress=False)
        
        if data.empty:
            return 'UNKNOWN'
        
        # Calculate trend
        sma_50 = data['Close'].rolling(window=50).mean()
        sma_200 = data['Close'].rolling(window=200).mean()
        
        current_price = data['Close'].iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        current_sma_200 = sma_200.iloc[-1] if len(sma_200) > 0 else current_sma_50
        
        # Determine regime
        if current_price > current_sma_50 > current_sma_200:
            return 'BULL'
        elif current_price < current_sma_50 < current_sma_200:
            return 'BEAR'
        else:
            return 'SIDEWAYS'
    
    def get_dashboard_data(self) -> Dict:
        """
        Get comprehensive dashboard data for UI.
        
        Returns:
            Dashboard data dictionary
        """
        dashboard = {
            'predictions': {},
            'performance': {},
            'market_regimes': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Get predictions for all supported symbols
        for symbol in self.supported_symbols:
            try:
                dashboard['predictions'][symbol] = self.predict(symbol)
                dashboard['performance'][symbol] = self.get_model_performance(symbol, days=30)
                dashboard['market_regimes'][symbol] = self.get_market_regime(symbol)
            except:
                pass
        
        return dashboard


if __name__ == "__main__":
    print("ML Engine initialized")
    print(f"Supported symbols: {MLEngine().supported_symbols}")
    
    # Example usage
    engine = MLEngine()
    
    # Get prediction
    prediction = engine.predict('SPY')
    print(f"\nPrediction for SPY: {prediction}")
