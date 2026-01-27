"""
ML Trainer - Training pipeline for market prediction models
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os

try:
    from .feature_engineering import FeatureEngineer
    from .ml_models import EnsembleModel, LSTMModel
except ImportError:
    from feature_engineering import FeatureEngineer
    from ml_models import EnsembleModel, LSTMModel


class MLTrainer:
    """
    Complete training pipeline for market prediction models.
    """
    
    def __init__(self, symbol: str, lookback_days: int = 730):
        self.symbol = symbol
        self.lookback_days = lookback_days
        self.engineer = FeatureEngineer()
        self.ensemble_model = EnsembleModel()
        self.lstm_model = LSTMModel()
        
        self.metrics = {}
        
    def prepare_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare training data"""
        print(f"Preparing data for {self.symbol}...")
        X, y = self.engineer.prepare_training_data(self.symbol, self.lookback_days)
        print(f"Data shape: {X.shape}")
        print(f"Target distribution: UP={sum(y)}, DOWN={len(y)-sum(y)}")
        return X, y
    
    def time_series_split(self, X: pd.DataFrame, y: pd.Series, n_splits: int = 5):
        """
        Perform time-series cross-validation.
        
        Returns:
            List of (train_idx, test_idx) tuples
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        return list(tscv.split(X))
    
    def train_ensemble(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Train ensemble model with train/test split"""
        # Time-based split (last test_size% for testing)
        split_idx = int(len(X) * (1 - test_size))
        
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"\nTraining ensemble on {len(X_train)} samples...")
        print(f"Testing on {len(X_test)} samples...")
        
        # Train
        self.ensemble_model.train(X_train, y_train, X_test, y_test)
        
        # Evaluate
        y_pred = self.ensemble_model.predict(X_test, use_stacking=True)
        y_proba = self.ensemble_model.predict_proba(X_test, use_stacking=True)[:, 1]
        
        self.metrics['ensemble'] = self._calculate_metrics(y_test, y_pred, y_proba)
        
        print("\n=== Ensemble Model Performance ===")
        self._print_metrics(self.metrics['ensemble'])
        
        return X_train, X_test, y_train, y_test
    
    def train_lstm(self, X_train: pd.DataFrame, y_train: pd.Series, 
                   X_test: pd.DataFrame, y_test: pd.Series, epochs: int = 50):
        """Train LSTM model"""
        try:
            print(f"\nTraining LSTM on {len(X_train)} samples...")
            
            # Split train into train/val
            val_split = int(len(X_train) * 0.8)
            X_train_lstm, X_val_lstm = X_train[:val_split], X_train[val_split:]
            y_train_lstm, y_val_lstm = y_train[:val_split], y_train[val_split:]
            
            self.lstm_model.train(X_train_lstm, y_train_lstm, X_val_lstm, y_val_lstm, epochs=epochs)
            
            # Evaluate (need enough samples for sequence)
            if len(X_test) >= self.lstm_model.sequence_length:
                y_pred = self.lstm_model.predict(X_test)
                y_proba = self.lstm_model.predict_proba(X_test)[:, 1]
                
                # Only evaluate on the last prediction
                self.metrics['lstm'] = self._calculate_metrics(
                    y_test.iloc[-1:], 
                    y_pred[-1:], 
                    y_proba[-1:]
                )
                
                print("\n=== LSTM Model Performance ===")
                self._print_metrics(self.metrics['lstm'])
            else:
                print(f"Not enough test samples for LSTM evaluation (need {self.lstm_model.sequence_length})")
                
        except Exception as e:
            print(f"LSTM training failed: {e}")
            print("Continuing without LSTM model...")
    
    def _calculate_metrics(self, y_true, y_pred, y_proba) -> Dict:
        """Calculate evaluation metrics"""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }
        
        try:
            metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
        except:
            metrics['roc_auc'] = 0.0
        
        return metrics
    
    def _print_metrics(self, metrics: Dict):
        """Print metrics in a formatted way"""
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall:    {metrics['recall']:.4f}")
        print(f"  F1 Score:  {metrics['f1']:.4f}")
        print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"  Confusion Matrix:")
        cm = np.array(metrics['confusion_matrix'])
        print(f"    [[TN={cm[0,0]}, FP={cm[0,1]}],")
        print(f"     [FN={cm[1,0]}, TP={cm[1,1]}]]")
    
    def cross_validate(self, X: pd.DataFrame, y: pd.Series, n_splits: int = 5):
        """Perform time-series cross-validation"""
        print(f"\nPerforming {n_splits}-fold time-series cross-validation...")
        
        splits = self.time_series_split(X, y, n_splits)
        cv_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(splits, 1):
            print(f"\nFold {fold}/{n_splits}")
            
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Train temporary model
            temp_model = EnsembleModel()
            temp_model.train(X_train, y_train)
            
            # Evaluate
            y_pred = temp_model.predict(X_test, use_stacking=True)
            accuracy = accuracy_score(y_test, y_pred)
            cv_scores.append(accuracy)
            
            print(f"  Fold {fold} Accuracy: {accuracy:.4f}")
        
        print(f"\n=== Cross-Validation Results ===")
        print(f"  Mean Accuracy: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores):.4f})")
        print(f"  Min Accuracy:  {np.min(cv_scores):.4f}")
        print(f"  Max Accuracy:  {np.max(cv_scores):.4f}")
        
        return cv_scores
    
    def plot_confusion_matrix(self, save_path: str = "confusion_matrix.png"):
        """Plot confusion matrix"""
        if 'ensemble' not in self.metrics:
            print("No metrics available to plot")
            return
        
        cm = np.array(self.metrics['ensemble']['confusion_matrix'])
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['DOWN', 'UP'], 
                    yticklabels=['DOWN', 'UP'])
        plt.title(f'Confusion Matrix - {self.symbol}')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(save_path)
        print(f"Confusion matrix saved to {save_path}")
        plt.close()
    
    def get_feature_importance(self, top_n: int = 15):
        """Get and display top features"""
        top_features = self.ensemble_model.get_top_features(top_n)
        
        print(f"\n=== Top {top_n} Most Important Features ===")
        for model_name, features in top_features.items():
            print(f"\n{model_name.upper()}:")
            for i, (feature, importance) in enumerate(features, 1):
                print(f"  {i}. {feature}: {importance:.4f}")
        
        return top_features
    
    def save_models(self, version: str = "v1"):
        """Save trained models"""
        print(f"\nSaving models for {self.symbol} (version: {version})...")
        self.ensemble_model.save(self.symbol, version)
        
        if self.lstm_model.is_trained:
            self.lstm_model.save(self.symbol, version)
        
        print("Models saved successfully!")
    
    def full_training_pipeline(self, test_size: float = 0.2, train_lstm: bool = True, 
                               cross_validate: bool = False, save_models: bool = True):
        """
        Run complete training pipeline.
        
        Args:
            test_size: Fraction of data to use for testing
            train_lstm: Whether to train LSTM model
            cross_validate: Whether to perform cross-validation
            save_models: Whether to save trained models
        """
        print(f"\n{'='*60}")
        print(f"TRAINING PIPELINE FOR {self.symbol}")
        print(f"{'='*60}")
        
        # Prepare data
        X, y = self.prepare_data()
        
        # Cross-validation (optional)
        if cross_validate:
            self.cross_validate(X, y)
        
        # Train ensemble
        X_train, X_test, y_train, y_test = self.train_ensemble(X, y, test_size)
        
        # Train LSTM (optional)
        if train_lstm:
            self.train_lstm(X_train, y_train, X_test, y_test)
        
        # Feature importance
        self.get_feature_importance()
        
        # Plot confusion matrix
        self.plot_confusion_matrix(f"{self.symbol}_confusion_matrix.png")
        
        # Save models
        if save_models:
            self.save_models()
        
        print(f"\n{'='*60}")
        print(f"TRAINING COMPLETE!")
        print(f"{'='*60}")
        
        return self.metrics


if __name__ == "__main__":
    import sys
    
    # Example usage
    symbol = sys.argv[1] if len(sys.argv) > 1 else "SPY"
    
    print(f"Starting training for {symbol}...")
    
    trainer = MLTrainer(symbol, lookback_days=730)
    metrics = trainer.full_training_pipeline(
        test_size=0.2,
        train_lstm=False,  # Set to True if TensorFlow is installed
        cross_validate=False,  # Set to True for CV (takes longer)
        save_models=True
    )
    
    print("\nFinal Metrics:")
    print(metrics)
