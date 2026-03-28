"""
Simple runner script that sets up Python path correctly.
"""
import sys
sys.path.insert(0, '.')

from src.main import main

if __name__ == "__main__":
    exit(main())
