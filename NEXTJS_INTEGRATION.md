# Next.js Integration Guide

## Overview

Your Next.js project will serve as the **data provider** and the ML-Inventory system will be the **data consumer**.

```
Next.js Project (Data Source)
    ↓ (API Endpoints)
    ↓
ML-Inventory System (Analysis)
    ↓ (Results)
    ↓
Back to Next.js (Display Results)
```

---

## Setup Steps

### 1. Create Next.js API Endpoints

In your Next.js project, create two API endpoints to serve the hospital data:

**File: `pages/api/inventory/usage-history.js`**
```javascript
export default async function handler(req, res) {
  // TODO: Fetch from your database
  const usageData = [
    {
      date: "2026-01-01",
      facility_id: "FAC_01",
      medicine_id: "MED_001",
      units_used: 25,
      medicine_name: "Aspirin"
    },
    {
      date: "2026-01-01",
      facility_id: "FAC_01",
      medicine_id: "MED_002",
      units_used: 18,
      medicine_name: "Ibuprofen"
    },
    // ... more data
  ];

  res.status(200).json(usageData);
}
```

**File: `pages/api/inventory/current-inventory.js`**
```javascript
export default async function handler(req, res) {
  // TODO: Fetch from your database
  const inventoryData = [
    {
      facility_id: "FAC_01",
      medicine_id: "MED_001",
      medicine_name: "Aspirin",
      current_stock: 150,
      expiry_date: "2026-06-30",
      batch_id: "BATCH_001"
    },
    {
      facility_id: "FAC_01",
      medicine_id: "MED_002",
      medicine_name: "Ibuprofen",
      current_stock: 220,
      expiry_date: "2026-05-15",
      batch_id: "BATCH_002"
    },
    // ... more data
  ];

  res.status(200).json(inventoryData);
}
```

**File: `pages/api/inventory/analysis.js`** (Optional - receive results)
```javascript
export default async function handler(req, res) {
  if (req.method === 'POST') {
    // TODO: Save analysis results to database
    const analysisResults = req.body;
    
    console.log("Analysis Results Received:", analysisResults);
    
    return res.status(200).json({
      message: "Analysis received successfully",
      timestamp: new Date().toISOString()
    });
  }
  
  res.status(405).json({ error: "Method not allowed" });
}
```

---

## Integration Options

### Option A: Direct API Integration (Recommended for Development)

Modify `utils/data_loader.py` to fetch from Next.js API:

**File: `utils/data_loader_nextjs.py`**
```python
"""
Data loader for Next.js API integration
"""

import requests
import pandas as pd
from typing import Tuple, Dict
import os

class NextJSDataLoader:
    """Load data from Next.js API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize NextJS data loader
        
        Args:
            base_url: Base URL of Next.js application
        """
        self.base_url = base_url
    
    def fetch_usage_history(self) -> pd.DataFrame:
        """
        Fetch usage history from Next.js API
        
        Returns:
            DataFrame with columns: date, facility_id, medicine_id, units_used, medicine_name
        """
        try:
            url = f"{self.base_url}/api/inventory/usage-history"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            return df
        
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Next.js API at {self.base_url}. "
                "Make sure Next.js is running."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch usage history: {e}")
    
    def fetch_current_inventory(self) -> pd.DataFrame:
        """
        Fetch current inventory from Next.js API
        
        Returns:
            DataFrame with inventory data
        """
        try:
            url = f"{self.base_url}/api/inventory/current-inventory"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            # Convert expiry_date to datetime
            df['expiry_date'] = pd.to_datetime(df['expiry_date'])
            
            return df
        
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Next.js API at {self.base_url}. "
                "Make sure Next.js is running."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch inventory: {e}")
    
    def send_analysis_results(self, results: Dict) -> bool:
        """
        Send analysis results back to Next.js
        
        Args:
            results: Analysis results dictionary
        
        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/api/inventory/analysis"
            response = requests.post(url, json=results, timeout=10)
            response.raise_for_status()
            
            return True
        
        except Exception as e:
            print(f"Failed to send analysis results: {e}")
            return False
```

---

## Update main.py for Next.js Integration

Modify `main.py` to use Next.js data:

**Replace in `main.py` (around line 89):**
```python
def load_data(self, source: str = "sample"):
    """
    Load data from different sources
    
    Args:
        source: "sample" (demo), "nextjs" (API), or "csv" (files)
    """
    print("Loading data...")
    
    if source == "nextjs":
        # Load from Next.js API
        from utils.data_loader_nextjs import NextJSDataLoader
        
        print("  - Connecting to Next.js API...")
        loader = NextJSDataLoader("http://localhost:3000")
        
        try:
            self.usage_data = loader.fetch_usage_history()
            self.inventory_data = loader.fetch_current_inventory()
            
            print(f"✓ Loaded {len(self.usage_data)} usage records from Next.js")
            print(f"✓ Loaded {len(self.inventory_data)} inventory items from Next.js")
            
            # Optionally send results back
            self.nextjs_loader = loader
        
        except Exception as e:
            print(f"✗ Error loading from Next.js: {e}")
            print("Falling back to sample data...")
            self.load_data(source="sample")
    
    elif source == "csv":
        # Load from CSV files
        print("  - Loading from CSV files...")
        self.usage_data = self.data_loader.load_csv_data('usage_history.csv')
        self.inventory_data = self.data_loader.load_csv_data('current_inventory.csv')
    
    else:  # source == "sample"
        # Load sample data
        print("  - Generating sample data...")
        self.usage_data = self.data_loader.generate_sample_usage_data(
            days=90, facilities=5, medicines_per_facility=10
        )
        self.inventory_data = self.data_loader.generate_sample_inventory_data(
            facilities=5, medicines_per_facility=10
        )
    
    # Preprocess data
    print("  - Preprocessing data...")
    self.usage_data = self.data_loader.preprocess_usage_data(self.usage_data)
```

Then update the `run_full_analysis()` method:
```python
def run_full_analysis(self, data_source: str = "sample"):
    """
    Execute complete analysis pipeline
    
    Args:
        data_source: "sample", "nextjs", or "csv"
    """
    print("=" * 70)
    print("HOSPITAL SUPPLY CHAIN ML SYSTEM")
    print("=" * 70)
    print(f"Data Source: {data_source.upper()}")
    print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Load data from specified source
        self.load_data(source=data_source)
        
        # ... rest of analysis ...
        
        # Optional: Send results back to Next.js
        if data_source == "nextjs" and hasattr(self, 'nextjs_loader'):
            print("\nSending results back to Next.js...")
            self.nextjs_loader.send_analysis_results({
                'alerts': len(self.all_alerts),
                'critical_alerts': sum(1 for a in self.all_alerts 
                                      if getattr(a, 'severity', getattr(a, 'alert_level', 'info')) == 'critical'),
                'redistribution_plans': len(self.redistribution_plans),
                'timestamp': datetime.now().isoformat()
            })
```

---

## Run ML Analysis from Next.js

### Option 1: Call Python Script from Next.js

Create a Next.js API route that calls the Python script:

**File: `pages/api/ml/run-analysis.js`**
```javascript
import { spawn } from 'child_process';
import path from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const dataSource = req.body.dataSource || 'nextjs';  // Use Next.js API as source
  
  return new Promise((resolve, reject) => {
    // Path to Python script
    const pythonScriptPath = path.join(
      process.cwd(),
      '..',
      'ML-Inventory',
      'run_analysis.py'  // We'll create this
    );
    
    // Spawn Python process
    const python = spawn('python3', [pythonScriptPath, dataSource]);
    
    let output = '';
    let errorOutput = '';
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        res.status(200).json({
          success: true,
          output: output,
          message: 'Analysis completed successfully'
        });
        resolve();
      } else {
        res.status(500).json({
          success: false,
          error: errorOutput,
          message: 'Analysis failed'
        });
        reject();
      }
    });
  });
}
```

### Option 2: Direct Python Integration (Advanced)

Use Python-to-Node.js bridge like `node-gyp` or `child_process` to run Python directly.

---

## Create Python Script for CLI

**File: `run_analysis.py`** (in ML-Inventory root)
```python
"""
Command-line interface for running analysis
Accepts data source as argument
"""

import sys
sys.path.insert(0, str(Path(__file__).parent))

from main import HospitalSupplyChainSystem

def main():
    data_source = sys.argv[1] if len(sys.argv) > 1 else "sample"
    
    if data_source not in ["sample", "nextjs", "csv"]:
        print(f"Invalid data source: {data_source}")
        print("Use: python run_analysis.py [sample|nextjs|csv]")
        sys.exit(1)
    
    system = HospitalSupplyChainSystem()
    result = system.run_full_analysis(data_source=data_source)
    
    if result['status'] == 'success':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Complete Next.js Integration Example

**File: `pages/inventory-analysis.js`** (React component)
```javascript
import { useState, useEffect } from 'react';

export default function InventoryAnalysis() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/ml/run-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataSource: 'nextjs' })
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Inventory Analysis</h1>
      
      <button onClick={runAnalysis} disabled={loading}>
        {loading ? 'Running Analysis...' : 'Run Analysis'}
      </button>

      {error && <div style={{ color: 'red' }}>{error}</div>}
      
      {results && (
        <div style={{ marginTop: '20px' }}>
          <h2>Results</h2>
          <pre>{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

---

## Network Setup (Development)

### If Next.js and ML System on Same Machine:

```
Next.js: http://localhost:3000
ML System: Calls http://localhost:3000/api/inventory/*
```

### If on Different Machines:

Update `data_loader_nextjs.py`:
```python
loader = NextJSDataLoader("http://192.168.x.x:3000")  # Another machine IP
```

---

## Database Option

If you want a more robust setup, use a shared database:

**File: `utils/data_loader_db.py`**
```python
import psycopg2  # or mysql, sqlite, etc.
import pandas as pd

class DatabaseDataLoader:
    """Load data from shared database"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def fetch_usage_history(self) -> pd.DataFrame:
        query = """
            SELECT date, facility_id, medicine_id, units_used, medicine_name
            FROM usage_history
            ORDER BY date DESC
        """
        return pd.read_sql(query, self.connection_string)
    
    def fetch_current_inventory(self) -> pd.DataFrame:
        query = """
            SELECT facility_id, medicine_id, medicine_name, 
                   current_stock, expiry_date, batch_id
            FROM inventory
        """
        return pd.read_sql(query, self.connection_string)
```

---

## Summary: Quick Setup

1. **Create Next.js API endpoints** (usage history, current inventory)
2. **Create `data_loader_nextjs.py`** (download from this guide)
3. **Update `main.py`** to support `data_source="nextjs"`
4. **Test locally:** Both Next.js and ML system running
5. **Call from Next.js:** Use `/api/ml/run-analysis` endpoint

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to Next.js API" | Make sure Next.js is running on localhost:3000 |
| "Module not found: requests" | `pip install requests` |
| "Data type mismatch" | Ensure API returns proper JSON format |
| "Timeout error" | Increase timeout in `data_loader_nextjs.py` |

---

## Next Steps

1. ✅ Set up Next.js API endpoints
2. ✅ Copy `data_loader_nextjs.py` to utils/
3. ✅ Update main.py with data_source parameter
4. ✅ Test: `python main.py` (with sample first)
5. ✅ Run from Next.js: POST to `/api/ml/run-analysis`
6. ✅ Display results in React component

**You're ready to integrate!** 🚀
