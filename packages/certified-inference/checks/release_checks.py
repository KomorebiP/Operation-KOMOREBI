#!/usr/bin/env python3
import sys,subprocess
from pathlib import Path
out=Path(sys.argv[1])
subprocess.run([sys.executable,'checks/test_cached.py',str(out/'diagnostics.json')],check=True)
subprocess.run([sys.executable,'checks/benchmark_cached.py',str(out/'benchmark'),'5'],check=True)
