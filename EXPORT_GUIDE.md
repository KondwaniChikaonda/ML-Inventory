# Export & Transfer Guide

## How to Export This Project

### Option 1: Create a ZIP Archive (Recommended)

**On macOS/Linux:**
```bash
cd /Users/michaelchikaonda/Desktop
zip -r ML-Inventory.zip ML-Inventory/ -x "ML-Inventory/.venv/*" "ML-Inventory/__pycache__/*" "ML-Inventory/data/*.csv"
```

**On Windows:**
```cmd
# Using built-in: Right-click ML-Inventory folder → Send to → Compressed (zipped) folder
# Or use 7-Zip/WinRAR to create ML-Inventory.zip (exclude .venv and __pycache__)
```

### Option 2: Using Git (If Available)

```bash
cd ML-Inventory
git init
git add .
git commit -m "Initial commit: Hospital Supply Chain ML System"
# Push to GitHub/GitLab or share the .git folder
```

### Option 3: Manual Copy

Just copy the entire `ML-Inventory` folder (excluding `.venv/` and `__pycache__/`)

---

## What's Included in Export

✓ **Core System:**
- `main.py` - Main orchestration script
- `requirements.txt` - All Python dependencies
- `config/` - Configuration modules
- `utils/` - 6 core utility modules
- `setup.py` - Automated setup script
- `run.sh` / `run.bat` - Quick run scripts

✓ **Documentation:**
- `README.md` - Comprehensive documentation
- `DEPLOYMENT.md` - Detailed deployment guide
- `QUICKSTART.md` - Quick reference
- `EXPORT_GUID.md` - This file

✓ **Configuration:**
- `.gitignore` - Git exclusions
- Directory structure for `data/`, `models/`, `notebooks/`

❌ **NOT Included (by design):**
- `.venv/` - Virtual environment (regenerated on target machine)
- `__pycache__/` - Python cache files
- `data/*.csv` - Your data files (add your own)
- `*.log` - Log files

---

## Transfer to Another Machine

### Step 1: Copy Project
```bash
# Option A: Extract ZIP on target machine
unzip ML-Inventory.zip
cd ML-Inventory

# Option B: Copy folder
cp -r ML-Inventory /destination/path
cd /destination/path/ML-Inventory

# Option C: Git clone (if using Git)
git clone <repo-url>
cd ML-Inventory
```

### Step 2: Run Setup
See `QUICKSTART.md` or `DEPLOYMENT.md` for OS-specific instructions

**Quick setup (all OS):**
```bash
python3 setup.py
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python main.py
```

---

## File Size Estimate

```
Core Project:           ~500 KB (without .venv)
With Dependencies:      ~300-500 MB (when installed)
Your Data:              Varies (you add this)
```

**ZIP File Size:** ~2-5 MB (without .venv and data)

---

## System Requirements on Target Machine

✓ **Minimum:**
- Python 3.8+
- 2GB RAM
- 500MB disk space for dependencies

✓ **Recommended:**
- Python 3.11+
- 4GB+ RAM
- 2GB+ disk space
- macOS 10.13+, Linux, or Windows 10/11

---

## Transferring Custom Data

1. **Prepare your CSV files:**
   - `usage_history.csv` - Daily medication usage
   - `current_inventory.csv` - Current inventory levels
   - See `DEPLOYMENT.md` for format specifications

2. **Add to exported project:**
   ```
   ML-Inventory/
   └── data/
       ├── usage_history.csv
       └── current_inventory.csv
   ```

3. **Update main.py (line ~89):**
   ```python
   def load_data(self, sample: bool = False):  # Change True to False
       """Load data (sample for demo or from CSV)"""
   ```

4. **Run:**
   ```bash
   python main.py
   ```

---

## Troubleshooting Transfer

### Issue: "ModuleNotFoundError: No module named 'pandas'"
**Solution:** 
```bash
pip install -r requirements.txt
```

### Issue: "Python version too old"
**Solution:** Install Python 3.8+ from python.org

### Issue: Permission denied (macOS/Linux)
**Solution:**
```bash
chmod +x setup.py run.sh
python3 setup.py
```

### Issue: Virtual environment corrupted
**Solution:**
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Next Steps After Transfer

1. ✓ Extract/copy project on target machine
2. ✓ Run `setup.py` or manual setup
3. ✓ Test with sample data: `python main.py`
4. ✓ Add your own CSV data to `data/` folder
5. ✓ Update `main.py` to use your data
6. ✓ Run analysis on your data

---

## Support During Transfer

If you encounter issues:
1. Check `DEPLOYMENT.md` troubleshooting section
2. Verify Python version: `python3 --version`
3. Verify pip: `pip --version`
4. Test imports: `python3 -c "import pandas; print('OK')"`
5. Review README.md for architecture details

---

**Exported:** March 26, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✓
