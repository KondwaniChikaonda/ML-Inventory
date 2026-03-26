# Hospital Supply Chain ML System - Deployment Guide

## Quick Start (5 minutes)

### On Target Machine:

1. **Download and navigate to project:**
```bash
cd /path/to/ML-Inventory
```

2. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the system:**
```bash
python main.py
```

---

## Installation by OS

### macOS & Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Windows (Command Prompt):
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Windows (PowerShell):
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

---

## Troubleshooting

### Issue: `python` command not found
**Solution:** Use `python3` instead
```bash
python3 -m venv .venv
python3 main.py
```

### Issue: Package installation fails
**Solution:** Upgrade pip first
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Import errors after installation
**Solution:** Ensure virtual environment is activated
```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

---

## Using Your Own Data

Replace sample data with your real hospital data:

### 1. Prepare CSV files:

**usage_history.csv:**
```csv
date,facility_id,medicine_id,units_used,medicine_name
2026-01-01,FAC_01,MED_001,25,Aspirin
2026-01-01,FAC_01,MED_002,18,Ibuprofen
...
```

**current_inventory.csv:**
```csv
facility_id,medicine_id,medicine_name,current_stock,expiry_date,batch_id
FAC_01,MED_001,Aspirin,150,2026-06-30,BATCH_001
FAC_01,MED_002,Ibuprofen,220,2026-05-15,BATCH_002
...
```

### 2. Place in data/ folder:
```
ML-Inventory/
├── data/
│   ├── usage_history.csv
│   └── current_inventory.csv
...
```

### 3. Modify main.py to load your data:
Edit line ~89 in `main.py`:
```python
def load_data(self, sample: bool = True):  # Change to False
    """Load data (sample for demo or from CSV)"""
    print("Loading data...")
    
    if sample:  # Change to: if sample is False:
        # ... existing code ...
    else:
        try:
            self.usage_data = self.data_loader.load_csv_data('usage_history.csv')
            self.inventory_data = self.data_loader.load_csv_data('current_inventory.csv')
        # ...
```

Or call with `sample=False`:
```python
system = HospitalSupplyChainSystem()
result = system.run_full_analysis()  # Uses self.load_data(sample=True) by default
```

---

## Project Structure

```
ML-Inventory/
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── DEPLOYMENT.md              # This file
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration parameters
├── utils/
│   ├── __init__.py
│   ├── data_loader.py        # Data loading
│   ├── demand_forecaster.py  # Forecasting models
│   ├── expiry_tracker.py     # Expiry monitoring
│   ├── alert_system.py       # Alert generation
│   ├── redistribution_optimizer.py  # Optimization
│   └── analytics.py          # Analytics & reporting
├── data/                      # Your data files here
├── models/                    # Saved models
└── notebooks/                 # Optional notebooks
```

---

## Customization

### Adjust forecasting parameters:
Edit `config/settings.py`:
```python
FORECAST_HORIZON = 7           # days to forecast
EXPIRY_WARNING_DAYS = 14       # alert threshold
SHORTAGE_PROBABILITY_THRESHOLD = 0.7  # alert probability
```

### Control system behavior:
Edit `main.py` `run_full_analysis()` method to customize analysis steps

---

## Performance Tips

- **Larger datasets:** May take longer to train. Consider reducing LOOKBACK_PERIOD
- **Multiple runs:** Cache forecasts to reuse trained models
- **Memory constraints:** Process data in batches if you have 100K+ records

---

## Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review error messages and try the Troubleshooting section
3. Verify Python version (3.8+) and pip installation

---

**Version:** 1.0.0  
**Last Updated:** March 2026
