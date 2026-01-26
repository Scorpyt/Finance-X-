"""
ML Models Module - Ensemble and Deep Learning Models for Market Prediction
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import joblib
import os


class EnsembleModel:
    """
    Ensemble of multiple ML models for robust predictions.
    Combines Random Forest, XGBoost, and LightGBM.
    """
    
    def __init__(self, model_dir: str = "ml_models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models with optimized hyperparameters
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=4,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1
            ),
            'xgboost': XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                eval_metric='logloss'
            ),
            'lightgbm': LGBMClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
        }
        
        # Meta-learner for stacking
        self.meta_learner = LogisticRegression(random_state=42, max_iter=1000)
        
        self.is_trained = False
        self.feature_importance = {}
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, 
              X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None):
        """
        Train all ensemble models.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
        """
        print("Training ensemble models...")
        
        # Train individual models
        for name, model in self.models.items():
            print(f"  Training {name}...")
            model.fit(X_train, y_train)
            
            # Store feature importance
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = dict(zip(
                    X_train.columns, 
                    model.feature_importances_
                ))
            
            # Validation score
            if X_val is not None and y_val is not None:
                val_score = model.score(X_val, y_val)
                print(f"    {name} validation accuracy: {val_score:.4f}")
        
        # Train meta-learner (stacking)
        print("  Training meta-learner (stacking)...")
        meta_features_train = self._get_meta_features(X_train)
        self.meta_learner.fit(meta_features_train, y_train)
        
        if X_val is not None and y_val is not None:
            meta_features_val = self._get_meta_features(X_val)
            meta_score = self.meta_learner.score(meta_features_val, y_val)
            print(f"    Meta-learner validation accuracy: {meta_score:.4f}")
        
        self.is_trained = True
        print("Ensemble training complete!")
    
    def _get_meta_features(self, X: pd.DataFrame) -> np.ndarray:
        """Get predictions from base models as meta-features"""
        meta_features = []
        for model in self.models.values():
            # Get probability predictions
            probs = model.predict_proba(X)[:, 1]
            meta_features.append(probs)
        return np.column_stack(meta_features)
    
    def predict(self, X: pd.DataFrame, use_stacking: bool = True) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features
            use_stacking: If True, use meta-learner; otherwise use voting
            
        Returns:
            Binary predictions (0 or 1)
        """
        if not self.is_trained:
            raise ValueError("Models not trained yet!")
        
        if use_stacking:
            meta_features = self._get_meta_features(X)
            return self.meta_learner.predict(meta_features)
        else:
            # Simple voting
            predictions = []
            for model in self.models.values():
                predictions.append(model.predict(X))
            return np.round(np.mean(predictions, axis=0)).astype(int)
    
    def predict_proba(self, X: pd.DataFrame, use_stacking: bool = True) -> np.ndarray:
        """
        Get probability predictions.
        
        Args:
            X: Features
            use_stacking: If True, use meta-learner; otherwise average probabilities
            
        Returns:
            Probability predictions for each class
        """
        if not self.is_trained:
            raise ValueError("Models not trained yet!")
        
        if use_stacking:
            meta_features = self._get_meta_features(X)
            return self.meta_learner.predict_proba(meta_features)
        else:
            # Average probabilities
            all_probs = []
            for model in self.models.values():
                all_probs.append(model.predict_proba(X))
            return np.mean(all_probs, axis=0)
    
    def get_confidence_score(self, X: pd.DataFrame) -> float:
        """
        Get confidence score based on model agreement.
        
        Returns:
            Confidence score between 0 and 1
        """
        predictions = []
        for model in self.models.values():
            predictions.append(model.predict(X))
        
        # Calculate agreement percentage
        predictions = np.array(predictions)
        agreement = np.mean(predictions == predictions[0])
        
        return float(agreement)
    
    def save(self, symbol: str, version: str = "v1"):
        """Save all models to disk"""
        model_path = os.path.join(self.model_dir, f"{symbol}_{version}")
        os.makedirs(model_path, exist_ok=True)
        
        for name, model in self.models.items():
            joblib.dump(model, os.path.join(model_path, f"{name}.pkl"))
        
        joblib.dump(self.meta_learner, os.path.join(model_path, "meta_learner.pkl"))
        joblib.dump(self.feature_importance, os.path.join(model_path, "feature_importance.pkl"))
        
        print(f"Models saved to {model_path}")
    
    def load(self, symbol: str, version: str = "v1"):
        """Load models from disk"""
        model_path = os.path.join(self.model_dir, f"{symbol}_{version}")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path {model_path} not found")
        
        for name in self.models.keys():
            self.models[name] = joblib.load(os.path.join(model_path, f"{name}.pkl"))
        
        self.meta_learner = joblib.load(os.path.join(model_path, "meta_learner.pkl"))
        self.feature_importance = joblib.load(os.path.join(model_path, "feature_importance.pkl"))
        
        self.is_trained = True
        print(f"Models loaded from {model_path}")
    
    def get_top_features(self, top_n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get top N most important features for each model.
        
        Returns:
            Dictionary mapping model name to list of (feature, importance) tuples
        """
        top_features = {}
        
        for model_name, importance_dict in self.feature_importance.items():
            sorted_features = sorted(
                importance_dict.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:top_n]
            top_features[model_name] = sorted_features
        
        return top_features


class LSTMModel:
    """
    LSTM model for time-series market prediction.
    Uses TensorFlow/Keras.
    """
    
    def __init__(self, sequence_length: int = 20, model_dir: str = "ml_models"):
        self.sequence_length = sequence_length
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.is_trained = False
    
    def _build_model(self, input_shape: Tuple[int, int]):
        """Build LSTM architecture"""
        try:
            from tensorflow import keras
            from tensorflow.keras import layers
        except ImportError:
            print("TensorFlow not installed. LSTM model unavailable.")
            return None
        
        model = keras.Sequential([
            layers.LSTM(128, return_sequences=True, input_shape=input_shape),
            layers.Dropout(0.3),
            layers.LSTM(64, return_sequences=False),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM input"""
        X_seq, y_seq = [], []
        
        for i in range(len(X) - self.sequence_length):
            X_seq.append(X[i:i + self.sequence_length])
            y_seq.append(y[i + self.sequence_length])
        
        return np.array(X_seq), np.array(y_seq)
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, 
              X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None,
              epochs: int = 50, batch_size: int = 32):
        """Train LSTM model"""
        try:
            from sklearn.preprocessing import StandardScaler
            from tensorflow import keras
        except ImportError:
            print("Required libraries not installed. Skipping LSTM training.")
            return
        
        print("Training LSTM model...")
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Create sequences
        X_train_seq, y_train_seq = self._create_sequences(X_train_scaled, y_train.values)
        
        # Build model
        self.model = self._build_model((self.sequence_length, X_train.shape[1]))
        
        if self.model is None:
            return
        
        # Prepare validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            X_val_seq, y_val_seq = self._create_sequences(X_val_scaled, y_val.values)
            validation_data = (X_val_seq, y_val_seq)
        
        # Train
        history = self.model.fit(
            X_train_seq, y_train_seq,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            verbose=1,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)
            ]
        )
        
        self.is_trained = True
        print("LSTM training complete!")
        
        return history
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained or self.model is None:
            raise ValueError("LSTM model not trained yet!")
        
        X_scaled = self.scaler.transform(X)
        
        # For prediction, we need at least sequence_length samples
        if len(X_scaled) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} samples for prediction")
        
        # Use the last sequence_length samples
        X_seq = X_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
        
        prediction = self.model.predict(X_seq, verbose=0)
        return (prediction > 0.5).astype(int).flatten()
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get probability predictions"""
        if not self.is_trained or self.model is None:
            raise ValueError("LSTM model not trained yet!")
        
        X_scaled = self.scaler.transform(X)
        X_seq = X_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
        
        prob = self.model.predict(X_seq, verbose=0)[0][0]
        return np.array([[1 - prob, prob]])
    
    def save(self, symbol: str, version: str = "v1"):
        """Save LSTM model"""
        if self.model is None:
            return
        
        model_path = os.path.join(self.model_dir, f"{symbol}_{version}_lstm")
        os.makedirs(model_path, exist_ok=True)
        
        self.model.save(os.path.join(model_path, "lstm_model.h5"))
        joblib.dump(self.scaler, os.path.join(model_path, "scaler.pkl"))
        
        print(f"LSTM model saved to {model_path}")
    
    def load(self, symbol: str, version: str = "v1"):
        """Load LSTM model"""
        try:
            from tensorflow import keras
        except ImportError:
            print("TensorFlow not installed. Cannot load LSTM model.")
            return
        
        model_path = os.path.join(self.model_dir, f"{symbol}_{version}_lstm")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"LSTM model path {model_path} not found")
        
        self.model = keras.models.load_model(os.path.join(model_path, "lstm_model.h5"))
        self.scaler = joblib.load(os.path.join(model_path, "scaler.pkl"))
        
        self.is_trained = True
        print(f"LSTM model loaded from {model_path}")


if __name__ == "__main__":
    print("ML Models module loaded successfully!")
    print("Available models: EnsembleModel, LSTMModel")
