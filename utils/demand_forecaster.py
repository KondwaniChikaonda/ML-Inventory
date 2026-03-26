"""
Demand forecasting models for hospital supply chain
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
import warnings

warnings.filterwarnings('ignore')

class DemandForecaster:
    """Forecast future demand using historical usage patterns"""
    
    def __init__(self, forecast_horizon: int = 7):
        """
        Initialize forecaster
        
        Args:
            forecast_horizon: Number of days to forecast ahead
        """
        self.forecast_horizon = forecast_horizon
        self.model_weights = None
        self.feature_columns = None
        self.mean = None
        self.std = None
    
    def create_features(self, df: pd.DataFrame, window: int = 7) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create time-series features for ML model
        
        Args:
            df: Time series data with 'units_used' column
            window: Rolling window size for features
        
        Returns:
            Tuple of (X, y) for model training
        """
        df = df.sort_values('date').reset_index(drop=True)
        
        features = []
        targets = []
        
        for i in range(window, len(df) - 1):
            # Historical usage windows
            historical = df['units_used'].iloc[i-window:i].values
            
            # Create feature vector
            feature_vec = [
                np.mean(historical),           # mean usage
                np.std(historical),            # volatility
                np.min(historical),            # min usage
                np.max(historical),            # max usage
                historical[-1],                # last day usage
                np.sum(historical),            # total usage in window
                np.max(historical) - np.min(historical),  # range
            ]
            
            # Day of week encoding (cyclical)
            day_of_week = df['date'].iloc[i].dayofweek if hasattr(df['date'].iloc[i], 'dayofweek') else i % 7
            feature_vec.append(np.sin(2 * np.pi * day_of_week / 7))
            feature_vec.append(np.cos(2 * np.pi * day_of_week / 7))
            
            features.append(feature_vec)
            targets.append(df['units_used'].iloc[i + 1])
        
        self.feature_columns = [
            'mean_usage', 'std_usage', 'min_usage', 'max_usage',
            'last_usage', 'sum_usage', 'range_usage',
            'day_sin', 'day_cos'
        ]
        
        return np.array(features), np.array(targets)
    
    def train(self, df: pd.DataFrame, window: int = 7) -> None:
        """
        Train demand forecasting model using simple weighted average
        
        Args:
            df: Historical usage data
            window: Rolling window size
        """
        # Create features
        X, y = self.create_features(df, window)
        
        # Simple approach: calculate weights based on correlation with target
        if len(X) > 0 and len(y) > 0:
            # Normalize features
            self.mean = np.nanmean(X, axis=0)
            self.std = np.nanstd(X, axis=0)
            self.std[self.std == 0] = 1  # Avoid division by zero
            
            X_normalized = (X - self.mean) / self.std
            
            # Calculate correlation-based weights for each feature
            weights = []
            for col in range(X_normalized.shape[1]):
                if np.std(X_normalized[:, col]) > 0:
                    corr = np.corrcoef(X_normalized[:, col], y)[0, 1]
                    weights.append(max(0, corr))  # Only positive correlations
                else:
                    weights.append(0)
            
            # Normalize weights
            weight_sum = sum(weights)
            self.model_weights = np.array(weights) / max(weight_sum, 0.01)
    
    def forecast(self, df: pd.DataFrame, days: int = None) -> List[float]:
        """
        Forecast demand for future days
        
        Args:
            df: Historical usage data (sorted by date)
            days: Number of days to forecast (uses forecast_horizon if not specified)
        
        Returns:
            List of forecasted demand values
        """
        days = days or self.forecast_horizon
        df = df.sort_values('date').reset_index(drop=True)
        
        # Use last 7 days as initial window
        window = 7
        current_data = df['units_used'].iloc[-window:].values.copy()
        forecasts = []
        
        for _ in range(days):
            # Create feature vector
            feature_vec = np.array([
                np.mean(current_data),
                np.std(current_data),
                np.min(current_data),
                np.max(current_data),
                current_data[-1],
                np.sum(current_data),
                np.max(current_data) - np.min(current_data),
                0, 0  # day encoding (placeholder)
            ])
            
            # Predict using weighted average if model trained
            if self.model_weights is not None and self.mean is not None:
                X_normalized = (feature_vec - self.mean) / self.std
                pred = float(np.dot(X_normalized, self.model_weights) * np.mean(current_data) + np.mean(current_data))
            else:
                # Simple exponential smoothing fallback
                pred = float(np.mean(current_data) * 0.7 + current_data[-1] * 0.3)
            
            pred = max(0, pred)  # Ensure non-negative
            forecasts.append(pred)
            
            # Update window with new prediction
            current_data = np.append(current_data[1:], pred)
        
        return forecasts
    
    @staticmethod
    def calculate_forecast_confidence(residuals: np.ndarray) -> Dict:
        """
        Calculate confidence metrics for forecast
        
        Args:
            residuals: Model prediction residuals
        
        Returns:
            Dictionary with confidence metrics
        """
        mape = np.mean(np.abs(residuals)) if len(residuals) > 0 else 0
        rmse = np.sqrt(np.mean(residuals ** 2)) if len(residuals) > 0 else 0
        
        return {
            'mape': mape,
            'rmse': rmse,
            'confidence': max(0, min(1, 1 - (mape / max(100, 1))))
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if self.model_weights is None:
            return {}
        
        importance = {}
        for col, imp in zip(self.feature_columns, self.model_weights):
            importance[col] = float(imp)
        
        return importance
