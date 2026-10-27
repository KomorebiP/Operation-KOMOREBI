#!/usr/bin/env python3
"""Execute the archived benchmark while preventing caches beside raw sources."""
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode=True
runpy.run_path(str(Path(__file__).with_name('benchmark_finite_primitives.py')),run_name='__main__')
