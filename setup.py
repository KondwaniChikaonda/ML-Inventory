#!/usr/bin/env python3
"""
Automated setup script for Hospital Supply Chain ML System
Run this once to set up the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n{'='*70}")
    print(f"{description}...")
    print(f"{'='*70}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during {description}: {e}")
        return False

def main():
    """Run setup process"""
    print("\n" + "="*70)
    print("HOSPITAL SUPPLY CHAIN ML SYSTEM - AUTOMATED SETUP")
    print("="*70)
    
    # Check Python version
    print(f"\nPython Version: {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        sys.exit(1)
    
    # Step 1: Create virtual environment
    if not run_command("python3 -m venv .venv", "Creating virtual environment"):
        print("\n✗ Setup failed: Could not create virtual environment")
        sys.exit(1)
    
    # Determine pip command based on OS
    if sys.platform == "win32":
        pip_cmd = r".venv\Scripts\pip"
        python_cmd = r".venv\Scripts\python"
    else:
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    # Step 2: Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        print("\nWarning: Could not upgrade pip, continuing with current version...")
    
    # Step 3: Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        print("\n✗ Setup failed: Could not install dependencies")
        print("Try manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 4: Verify installation
    print(f"\n{'='*70}")
    print("Verifying installation...")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            f"{python_cmd} -c \"import pandas; import numpy; print('✓ Core packages verified')\"",
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except:
        print("⚠ Could not verify packages (this may be normal)")
    
    # Step 5: Create data directory if needed
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir()
        print(f"✓ Created {data_dir} directory for your data")
    
    models_dir = Path("models")
    if not models_dir.exists():
        models_dir.mkdir()
        print(f"✓ Created {models_dir} directory for models")
    
    # Final instructions
    print(f"\n{'='*70}")
    print("SETUP COMPLETE!")
    print(f"{'='*70}")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if sys.platform == "win32":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("\n2. Run the system:")
    print("   python main.py")
    print("\n3. Or run with your own data:")
    print("   - Place CSV files in data/ folder")
    print("   - Modify main.py line ~89 to set sample=False")
    print("   - Run: python main.py")
    print(f"\n{'='*70}")
    print("For detailed info, see DEPLOYMENT.md")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
