"""
Configuration settings for Hospital Supply Chain ML System
"""

# Data paths
DATA_DIR = "data"
MODELS_DIR = "models"

# Forecasting parameters
FORECAST_HORIZON = 7  # days
LOOKBACK_PERIOD = 90  # days of historical data
MIN_STOCK_ALERT_THRESHOLD = 10  # units
REORDER_POINT = 20  # units

# Expiry tracking
EXPIRY_WARNING_DAYS = 14  # alert if expiry within 14 days
CRITICAL_EXPIRY_DAYS = 3   # critical alert if expiry within 3 days

# Model parameters
TRAIN_TEST_SPLIT = 0.8
RANDOM_STATE = 42

# Alert thresholds
SHORTAGE_PROBABILITY_THRESHOLD = 0.7  # trigger alert if shortage probability > 70%
LOW_STOCK_THRESHOLD = 0.3  # as percentage of average usage

# Redistribution
REDISTRIBUTION_TRIGGER_THRESHOLD = 0.5  # trigger redistribution if > 50% facilities face shortage
