import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.app import run_app

if __name__ == "__main__":
    raise SystemExit(run_app())
