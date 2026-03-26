"""
Model Performance Evaluation
Tests demand forecasting accuracy on holdout test set
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import TRAIN_TEST_SPLIT, RANDOM_STATE
from utils.data_loader import SupplyDataLoader
from utils.demand_forecaster import DemandForecaster

def calculate_metrics(y_true, y_pred):
    """Calculate model performance metrics"""
    
    # Handle arrays
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Mean Absolute Percentage Error
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    # Root Mean Square Error
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    # Mean Absolute Error
    mae = np.mean(np.abs(y_true - y_pred))
    
    # Mean Absolute Scaled Error (baseline: naive forecast)
    naive_errors = np.abs(np.diff(y_true))
    if len(naive_errors) > 0:
        mase = mae / np.mean(naive_errors)
    else:
        mase = mae
    
    # R-squared
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return {
        'MAPE': mape,
        'RMSE': rmse,
        'MAE': mae,
        'MASE': mase,
        'R²': r2
    }

def evaluate_model():
    """Evaluate demand forecasting model"""
    
    print("=" * 80)
    print("DEMAND FORECASTING MODEL - PERFORMANCE EVALUATION")
    print("=" * 80)
    
    # Load data
    print("\n1. LOADING DATA...")
    loader = SupplyDataLoader()
    usage_data = loader.generate_sample_usage_data(days=90, facilities=5, medicines_per_facility=10)
    usage_data = loader.preprocess_usage_data(usage_data)
    
    print(f"   ✓ Loaded {len(usage_data)} total records")
    print(f"   ✓ Date range: {usage_data['date'].min()} to {usage_data['date'].max()}")
    
    # Group by medicine for separate model evaluation
    medicines = usage_data['medicine_id'].unique()
    print(f"   ✓ Medicines to evaluate: {len(medicines)}")
    
    # Evaluate each medicine
    all_metrics = []
    detailed_results = []
    
    print("\n2. TRAINING & TESTING MODELS...")
    print("-" * 80)
    
    for medicine_id in medicines[:5]:  # Test first 5 medicines for speed
        medicine_data = usage_data[usage_data['medicine_id'] == medicine_id].copy()
        medicine_data = medicine_data.sort_values('date').reset_index(drop=True)
        
        if len(medicine_data) < 14:  # Need at least 2 weeks of data
            continue
        
        # Train/test split
        split_idx = int(len(medicine_data) * TRAIN_TEST_SPLIT)
        train_data = medicine_data.iloc[:split_idx]
        test_data = medicine_data.iloc[split_idx:]
        
        if len(test_data) < 2:
            continue
        
        # Train model
        forecaster = DemandForecaster(forecast_horizon=1)
        try:
            forecaster.train(train_data, window=7)
        except Exception as e:
            print(f"   ✗ {medicine_id}: Training failed ({str(e)[:30]})")
            continue
        
        # Make predictions on test set
        predictions = []
        for i in range(len(test_data)):
            test_slice = pd.concat([train_data.iloc[-(14-i):], test_data.iloc[:i]])
            if len(test_slice) >= 7:
                try:
                    pred = forecaster.forecast(test_slice, days=1)[0]
                    predictions.append(pred)
                except:
                    predictions.append(test_data.iloc[i]['units_used'])
        
        if len(predictions) < 2:
            continue
        
        # Calculate metrics
        y_true = test_data.iloc[:len(predictions)]['units_used'].values
        y_pred = np.array(predictions)
        
        metrics = calculate_metrics(y_true, y_pred)
        metrics['medicine_id'] = medicine_id
        metrics['train_size'] = len(train_data)
        metrics['test_size'] = len(predictions)
        all_metrics.append(metrics)
        
        # Store detailed results for visualization
        detailed_results.append({
            'medicine_id': medicine_id,
            'actual': y_true,
            'predicted': y_pred,
            'dates': test_data.iloc[:len(predictions)]['date'].values
        })
        
        print(f"   ✓ {medicine_id}")
        print(f"     - Train: {len(train_data)} days | Test: {len(predictions)} days")
        print(f"     - MAPE: {metrics['MAPE']:.2f}% | RMSE: {metrics['RMSE']:.2f} | R²: {metrics['R²']:.3f}")
    
    # Summary statistics
    print("\n3. OVERALL PERFORMANCE SUMMARY...")
    print("-" * 80)
    
    if all_metrics:
        metrics_df = pd.DataFrame(all_metrics)
        
        # Remove non-numeric columns for stats
        numeric_metrics = metrics_df[['MAPE', 'RMSE', 'MAE', 'MASE', 'R²']]
        
        print(f"\nMetrics across {len(all_metrics)} medicines:\n")
        
        for metric in ['MAPE', 'RMSE', 'MAE', 'MASE', 'R²']:
            mean_val = numeric_metrics[metric].mean()
            std_val = numeric_metrics[metric].std()
            min_val = numeric_metrics[metric].min()
            max_val = numeric_metrics[metric].max()
            
            if metric == 'MAPE':
                print(f"{metric:6} | Mean: {mean_val:7.2f}% | Std: {std_val:7.2f}% | Range: {min_val:7.2f}% - {max_val:7.2f}%")
            elif metric == 'R²':
                print(f"{metric:6} | Mean: {mean_val:7.3f}  | Std: {std_val:7.3f}  | Range: {min_val:7.3f} - {max_val:7.3f}")
            else:
                print(f"{metric:6} | Mean: {mean_val:7.2f}  | Std: {std_val:7.2f}  | Range: {min_val:7.2f} - {max_val:7.2f}")
        
        print("\n4. PER-MEDICINE DETAILS...")
        print("-" * 80)
        print(f"{'Medicine':<10} {'MAPE':<10} {'RMSE':<10} {'MAE':<10} {'R²':<10}")
        print("-" * 80)
        
        for _, row in metrics_df.iterrows():
            print(f"{row['medicine_id']:<10} {row['MAPE']:>7.2f}%  {row['RMSE']:>7.2f}  {row['MAE']:>7.2f}  {row['R²']:>7.3f}")
        
        # Interpretation
        print("\n5. MODEL INTERPRETATION...")
        print("-" * 80)
        
        mean_mape = numeric_metrics['MAPE'].mean()
        mean_r2 = numeric_metrics['R²'].mean()
        
        if mean_mape < 20:
            accuracy_rating = "EXCELLENT ⭐⭐⭐⭐⭐"
        elif mean_mape < 30:
            accuracy_rating = "GOOD ⭐⭐⭐⭐"
        elif mean_mape < 40:
            accuracy_rating = "FAIR ⭐⭐⭐"
        elif mean_mape < 50:
            accuracy_rating = "ACCEPTABLE ⭐⭐"
        else:
            accuracy_rating = "NEEDS IMPROVEMENT ⭐"
        
        print(f"\nAccuracy Rating: {accuracy_rating}")
        print(f"Average MAPE: {mean_mape:.2f}%")
        print(f"Average R²: {mean_r2:.3f}")
        
        print("\nInterpretation:")
        print(f"  • MAPE {mean_mape:.1f}% means predictions are off by ~{mean_mape:.1f}% on average")
        print(f"  • R² {mean_r2:.3f} explains {mean_r2*100:.1f}% of the variance in demand")
        print(f"  • RMSE {numeric_metrics['RMSE'].mean():.2f} units average prediction error")
        
        # Recommendations
        print("\n6. RECOMMENDATIONS...")
        print("-" * 80)
        
        if mean_mape < 25:
            print("✓ Model performance is strong - suitable for production use")
            print("✓ Use for shortage prediction and procurement planning")
        elif mean_mape < 35:
            print("✓ Model performance is acceptable - use with caution")
            print("⚠ Consider collecting more historical data (20+ days)")
            print("⚠ Combine with domain expert judgement for critical decisions")
        else:
            print("⚠ Model needs improvement")
            print("  → Collect more historical data (90+ days recommended)")
            print("  → Review data quality for anomalies")
            print("  → Consider external factors (seasonality, events, etc.)")
        
        # Feature importance if available
        print("\n7. FEATURE IMPORTANCE...")
        print("-" * 80)
        
        forecaster = DemandForecaster()
        forecaster.train(usage_data[usage_data['medicine_id'] == medicines[0]], window=7)
        importance = forecaster.get_feature_importance()
        
        if importance:
            print("\nFeature weights (higher = more important):\n")
            for feature, weight in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                bar = "█" * int(weight * 50)
                print(f"  {feature:<20} {bar} {weight:.4f}")
        
        return {
            'status': 'success',
            'metrics': metrics_df,
            'mean_mape': mean_mape,
            'mean_r2': mean_r2
        }
    
    else:
        print("✗ No valid models to evaluate")
        return {'status': 'error'}

if __name__ == "__main__":
    result = evaluate_model()
    
    print("\n" + "=" * 80)
    if result['status'] == 'success':
        print("✓ EVALUATION COMPLETE")
        print(f"  Average MAPE: {result['mean_mape']:.2f}%")
        print(f"  Average R²: {result['mean_r2']:.3f}")
    else:
        print("✗ EVALUATION FAILED")
    print("=" * 80)
