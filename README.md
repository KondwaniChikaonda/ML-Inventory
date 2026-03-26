# Hospital Supply Chain ML System

An intelligent machine learning system for hospital inventory management that forecasts demand, predicts shortages, and optimizes medicine redistribution while minimizing expiry and waste.

## Features

### 1. **Demand Forecasting**
- Predicts future medicine demand based on historical usage patterns
- Uses Random Forest regression with sliding-window features
- Incorporates seasonality and day-of-week patterns
- Provides forecast confidence metrics

### 2. **Shortage Prediction & Prevention**
- Forecasts potential medicine shortages 7+ days in advance
- Calculates shortage probability for each medicine at each facility
- Triggers alerts before critical stock levels are reached
- Enables proactive procurement and redistribution

### 3. **Expiry & Wastage Reduction**
- Tracks medicine expiry dates in real-time
- Estimates waste probability based on usage rates and expiry timeline
- Prioritizes distribution of medicines nearing expiration
- Categorizes alerts by urgency (Critical/Warning/Info)
- Automated alerts ensure pharmacists act before expiry

### 4. **Intelligent Redistribution**
- Identifies optimal transfer routes between facilities
- Solves shortage problems through internal redistribution
- Prevents waste by moving expiring stock to high-demand areas
- Estimates impact of redistribution plans

### 5. **Comprehensive Analytics**
- Facility performance analysis
- Medicine demand patterns
- Key performance indicators (KPIs)
- Actionable recommendations

## System Architecture

```
Hospital Supply Chain ML System
├── Data Loading & Preprocessing
│   └── SupplyDataLoader
├── Demand Forecasting
│   └── DemandForecaster (Random Forest)
├── Inventory Tracking
│   ├── ExpiryTracker
│   ├── AlertSystem
│   └── SupplyChainAnalytics
├── Optimization
│   └── RedistributionOptimizer
└── Orchestration
    └── HospitalSupplyChainSystem
```

## Installation

### Requirements
- Python 3.8+
- pip or conda

### Setup

1. **Clone or navigate to the project:**
```bash
cd /Users/michaelchikaonda/Desktop/ML-Inventory
```

2. **Create and activate a Python virtual environment (recommended):**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the complete analysis pipeline:

```bash
python main.py
```

This will:
1. Load/generate sample hospital supply data
2. Train demand forecasting models
3. Generate shortage and expiry alerts
4. Optimize medicine redistribution
5. Provide actionable recommendations

### Sample Output

```
======================================================================
HOSPITAL SUPPLY CHAIN ML SYSTEM
======================================================================

Loading data...
  - Generating sample usage data...
  - Generating sample inventory data...
  - Preprocessing data...
✓ Loaded 4500 usage records
✓ Loaded 50 inventory items

Training demand forecasting models...
✓ Trained 10 demand forecasting models

Generating alerts...
  - Tracking expiry dates...
  - Checking shortage risks...
✓ Generated 12 alerts

Optimizing redistribution...
✓ Created 8 redistribution plans

SYSTEM HEALTH SUMMARY
======================================================================
Total Medicines:        10
Total Facilities:       5
Current Stock:          9250 units
Days of Supply:         14.2 days

ALERT SUMMARY
======================================================================
Total Alerts:           12
  ├─ Critical:          2
  ├─ Warning:           5
  ├─ Shortage Risks:    4
  └─ Expiry Risks:      5
```

## Configuration

Edit `config/settings.py` to customize system parameters:

```python
# Forecasting
FORECAST_HORIZON = 7           # days to forecast
LOOKBACK_PERIOD = 90           # historical data window

# Expiry tracking
EXPIRY_WARNING_DAYS = 14       # alert before expiry
CRITICAL_EXPIRY_DAYS = 3       # critical threshold

# Alerts
SHORTAGE_PROBABILITY_THRESHOLD = 0.7    # trigger alert if > 70%
MIN_STOCK_ALERT_THRESHOLD = 10          # minimum units
LOW_STOCK_THRESHOLD = 0.3               # as percentage of usage
```

## Data Format

### Usage History (usage_history.csv)
```
date,facility_id,medicine_id,units_used,medicine_name
2026-01-01,FAC_01,MED_001,25,Medicine_1
2026-01-01,FAC_01,MED_002,18,Medicine_2
...
```

### Current Inventory (current_inventory.csv)
```
facility_id,medicine_id,medicine_name,current_stock,expiry_date,batch_id
FAC_01,MED_001,Medicine_1,150,2026-06-30,BATCH_001
FAC_01,MED_002,Medicine_2,220,2026-05-15,BATCH_002
...
```

## Key Classes & Methods

### DemandForecaster
```python
forecaster = DemandForecaster(forecast_horizon=7)
forecaster.train(df)                    # Train model
forecast = forecaster.forecast(df)      # Predict next N days
importance = forecaster.get_feature_importance()
```

### ExpiryTracker
```python
tracker = ExpiryTracker(warning_days=14, critical_days=3)
alerts = tracker.track_inventory(inventory_df, usage_stats)
prioritized = tracker.prioritize_distribution(alerts)
```

### AlertSystem
```python
system = AlertSystem()
shortage_risk, prob = system.check_shortage_risk(forecast, stock)
is_low, severity = system.check_low_stock(stock, daily_usage)
alert = system.generate_shortage_alert(...)
```

### RedistributionOptimizer
```python
optimizer = RedistributionOptimizer()
plans = optimizer.create_redistribution_plan(inventory_df, usage_stats)
impact = optimizer.estimate_impact(plans)
```

## Performance Metrics

The system tracks:
- **Forecast Accuracy**: MAPE and RMSE of demand predictions
- **Alert Precision**: Timeliness and severity classification
- **Waste Reduction**: Units saved through redistribution
- **Shortage Prevention**: Proactive interventions
- **Cost Optimization**: Efficient resource allocation

## Use Cases

1. **COVID-19 or Emergency Response**: Quickly redistribute critical medicines
2. **Seasonal Demand**: Anticipated fluctuations in demand
3. **Supply Chain Disruption**: Immediate rebalancing between facilities
4. **Medication Recalls**: Identify affected batches quickly
5. **Budget Optimization**: Reduce waste & unnecessary procurement

## Future Enhancements

- [ ] Deep Learning models (LSTM, Transformer) for complex patterns
- [ ] Real-time data streaming integration
- [ ] Web dashboard for live monitoring
- [ ] Mobile alerts for pharmacists
- [ ] Multi-facility optimization (global optimization)
- [ ] Integration with ERP/Hospital Management Systems
- [ ] Automatic procurement triggering

## Troubleshooting

### Model Training Issues
- Ensure data has at least 7 days of historical records
- Check for negative values in usage data

### Empty Alert Lists
- Verify inventory data includes expiry dates
- Check that forecasted demand exceeds thresholds in settings

### Low Forecast Accuracy
- Increase lookback period for more training data
- Check for data anomalies or outliers

## Contributing

Contributions welcome! Areas for improvement:
- Advanced forecasting models
- Real-time data integration
- UI/Dashboard development
- Documentation improvements

## License

MIT License - See LICENSE file for details

## Contact & Support

For questions or issues, please contact the development team.

---

**Last Updated**: March 2026
**Version**: 1.0.0
# ML-Inventory
