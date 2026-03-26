# Quick Start Guide

## For macOS/Linux:

```bash
# Method 1: Using setup script (recommended)
python3 setup.py
source .venv/bin/activate
python main.py

# Method 2: Manual setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py

# Method 3: Using run script
chmod +x run.sh
./run.sh
```

## For Windows:

```cmd
REM Method 1: Using setup script (recommended)
python setup.py
.venv\Scripts\activate
python main.py

REM Method 2: Manual setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py

REM Method 3: Using run script
run.bat
```

## What You Get:

✓ Demand forecasting with ML models  
✓ Automated shortage prediction  
✓ Expiry & waste tracking  
✓ Redistribution optimization  
✓ Real-time alerts  
✓ Comprehensive analytics  

## Next: Add Your Data

1. Place `usage_history.csv` and `current_inventory.csv` in the `data/` folder
2. Edit `main.py` line ~89: change `sample=True` to `sample=False`
3. Run `python main.py`

See `DEPLOYMENT.md` for detailed CSV format requirements.

---

**Questions?** Check README.md for comprehensive documentation.
