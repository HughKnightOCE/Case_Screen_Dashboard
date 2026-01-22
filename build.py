#!/usr/bin/env python3
"""
Build script for Case Screen Dashboard using PyInstaller.
"""

import subprocess
import sys
import shutil
from pathlib import Path

def build():
    try:
        # Clean previous build
        dist_dir = Path("dist")
        if dist_dir.exists():
            try:
                shutil.rmtree(dist_dir)
            except PermissionError:
                print("Error: Cannot remove dist directory. Please close any running instances of CaseDashboard.exe and try again.")
                sys.exit(1)
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "CaseDashboard",
            "main.py"
        ]
        subprocess.run(cmd, check=True)
        print("Build successful. Executable in dist/ directory.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()