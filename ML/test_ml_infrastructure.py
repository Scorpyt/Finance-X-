"""
Quick test script for ML infrastructure
Tests feature extraction and model training on SPY
"""

import sys
import warnings
warnings.filterwarnings('ignore')

def test_feature_engineering():
    """Test feature extraction"""
    print("\n" + "="*60)
    print("TEST 1: Feature Engineering")
    print("="*60)
    
    from feature_engineering import FeatureEngineer
    
    engineer = FeatureEngineer()
    print("✓ FeatureEngineer initialized")
    
    try:
        X, y = engineer.prepare_training_data('SPY', lookback_days=365)
        print(f"✓ Features extracted: {X.shape[0]} samples, {X.shape[1]} features")
        print(f"✓ Target distribution: UP={sum(y)}, DOWN={len(y)-sum(y)}")
        print(f"✓ Feature names: {len(engineer.feature_names)} features")
        return True
    except Exception as e:
        print(f"✗ Feature extraction failed: {e}")
        return False


def test_model_training():
    """Test model training (quick version)"""
    print("\n" + "="*60)
    print("TEST 2: Model Training (Quick)")
    print("="*60)
    
    from ml_trainer import MLTrainer
    
    try:
        trainer = MLTrainer('SPY', lookback_days=365)
        print("✓ MLTrainer initialized")
        
        X, y = trainer.prepare_data()
        print(f"✓ Data prepared: {X.shape}")
        
        # Quick train (no LSTM, no CV)
        X_train, X_test, y_train, y_test = trainer.train_ensemble(X, y, test_size=0.2)
        print("✓ Ensemble model trained")
        
        if 'ensemble' in trainer.metrics:
            metrics = trainer.metrics['ensemble']
            print(f"✓ Accuracy: {metrics['accuracy']:.4f}")
            print(f"✓ Precision: {metrics['precision']:.4f}")
            print(f"✓ F1 Score: {metrics['f1']:.4f}")
        
        # Save model
        trainer.save_models(version='test')
        print("✓ Model saved")
        
        return True
    except Exception as e:
        print(f"✗ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prediction():
    """Test real-time prediction"""
    print("\n" + "="*60)
    print("TEST 3: Real-time Prediction")
    print("="*60)
    
    from ml_predictor import MLPredictor, print_prediction
    
    try:
        predictor = MLPredictor('SPY', model_version='test')
        print("✓ MLPredictor initialized")
        
        prediction = predictor.predict_with_explanation()
        print("✓ Prediction generated")
        
        print_prediction(prediction)
        
        return True
    except FileNotFoundError:
        print("✗ No trained model found. Run test_model_training first.")
        return False
    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ml_engine():
    """Test ML Engine integration"""
    print("\n" + "="*60)
    print("TEST 4: ML Engine")
    print("="*60)
    
    from ml_engine import MLEngine
    
    try:
        engine = MLEngine()
        print("✓ MLEngine initialized")
        
        # Test prediction
        prediction = engine.predict('SPY')
        print(f"✓ Prediction: {prediction.get('final_prediction', 'N/A')}")
        print(f"✓ Confidence: {prediction.get('final_confidence', 0):.2%}")
        
        # Test market regime
        regime = engine.get_market_regime('SPY')
        print(f"✓ Market Regime: {regime}")
        
        return True
    except Exception as e:
        print(f"✗ ML Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" ML INFRASTRUCTURE TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Test 1: Feature Engineering
    results['feature_engineering'] = test_feature_engineering()
    
    # Test 2: Model Training (only if features work)
    if results['feature_engineering']:
        results['model_training'] = test_model_training()
    else:
        results['model_training'] = False
        print("\n⚠ Skipping model training test (feature extraction failed)")
    
    # Test 3: Prediction (only if training works)
    if results['model_training']:
        results['prediction'] = test_prediction()
    else:
        results['prediction'] = False
        print("\n⚠ Skipping prediction test (model training failed)")
    
    # Test 4: ML Engine (only if prediction works)
    if results['prediction']:
        results['ml_engine'] = test_ml_engine()
    else:
        results['ml_engine'] = False
        print("\n⚠ Skipping ML engine test (prediction failed)")
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name.replace('_', ' ').title():30} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! ML infrastructure is ready.")
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")
    
    return results


if __name__ == "__main__":
    # Check if specific test requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        if test_name == "features":
            test_feature_engineering()
        elif test_name == "train":
            test_model_training()
        elif test_name == "predict":
            test_prediction()
        elif test_name == "engine":
            test_ml_engine()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: features, train, predict, engine")
    else:
        # Run all tests
        run_all_tests()
