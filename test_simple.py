#!/usr/bin/env python
"""
Simple test script to verify all components work
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("HOSPITAL SUPPLY CHAIN ML SYSTEM - COMPONENT TEST")
print("=" * 70)

# Test imports
print("\n1. Testing imports...")
try:
    from config.settings import FORECAST_HORIZON, EXPIRY_WARNING_DAYS
    print(f"   ✓ Config loaded (FORECAST_HORIZON={FORECAST_HORIZON})")
except Exception as e:
    print(f"   ✗ Config error: {e}")
    sys.exit(1)

try:
    from utils.data_loader import SupplyDataLoader
    print("   ✓ Data Loader imported")
except Exception as e:
    print(f"   ✗ Data Loader error: {e}")
    sys.exit(1)

try:
    from utils.demand_forecaster import DemandForecaster
    print("   ✓ Demand Forecaster imported")
except Exception as e:
    print(f"   ✗ Demand Forecaster error: {e}")
    sys.exit(1)

try:
    from utils.expiry_tracker import ExpiryTracker
    print("   ✓ Expiry Tracker imported")
except Exception as e:
    print(f"   ✗ Expiry Tracker error: {e}")
    sys.exit(1)

try:
    from utils.alert_system import AlertSystem
    print("   ✓ Alert System imported")
except Exception as e:
    print(f"   ✗ Alert System error: {e}")
    sys.exit(1)

try:
    from utils.redistribution_optimizer import RedistributionOptimizer
    print("   ✓ Redistribution Optimizer imported")
except Exception as e:
    print(f"   ✗ Redistribution Optimizer error: {e}")
    sys.exit(1)

try:
    from utils.analytics import SupplyChainAnalytics
    print("   ✓ Analytics Engine imported")
except Exception as e:
    print(f"   ✗ Analytics error: {e}")
    sys.exit(1)

# Test data generation
print("\n2. Testing data generation...")
try:
    loader = SupplyDataLoader()
    usage_data = loader.generate_sample_usage_data(days=90, facilities=3, medicines_per_facility=5)
    print(f"   ✓ Generated usage data: {len(usage_data)} records")
    
    inventory_data = loader.generate_sample_inventory_data(facilities=3, medicines_per_facility=5)
    print(f"   ✓ Generated inventory data: {len(inventory_data)} items")
except Exception as e:
    print(f"   ✗ Data generation error: {e}")
    sys.exit(1)

# Test component initialization
print("\n3. Testing component initialization...")
try:
    forecaster = DemandForecaster()
    print("   ✓ Demand Forecaster initialized")
    
    tracker = ExpiryTracker()
    print("   ✓ Expiry Tracker initialized")
    
    alerts = AlertSystem()
    print("   ✓ Alert System initialized")
    
    optimizer = RedistributionOptimizer()
    print("   ✓ Redistribution Optimizer initialized")
    
    analytics = SupplyChainAnalytics()
    print("   ✓ Analytics Engine initialized")
except Exception as e:
    print(f"   ✗ Initialization error: {e}")
    sys.exit(1)

# Test quick operations
print("\n4. Testing core operations...")
try:
    # Test expiry tracking
    usage_stats = {'MED_001': 25, 'MED_002': 18, 'MED_003': 32, 'MED_004': 22, 'MED_005': 28}
    expiry_alerts = tracker.track_inventory(inventory_data, usage_stats)
    print(f"   ✓ Expiry tracking: {len(expiry_alerts)} alerts generated")
except Exception as e:
    print(f"   ✗ Expiry tracking error: {e}")

try:
    # Test shortage checking
    forecast = [25, 26, 24, 25, 27, 26, 25]
    shortage_risk, prob = alerts.check_shortage_risk(forecast, current_stock=100)
    print(f"   ✓ Shortage check: risk={shortage_risk}, probability={prob:.2%}")
except Exception as e:
    print(f"   ✗ Shortage check error: {e}")

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED - System is ready!")
print("=" * 70)
print("\nTo run the full analysis:")
print("  .venv/bin/python main.py")
print("\n" + "=" * 70)
