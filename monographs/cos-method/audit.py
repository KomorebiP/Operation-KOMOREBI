#!/usr/bin/env python3
"""Run the final publication audit. Numerical replay is a separate command."""
from pathlib import Path
import runpy
if __name__=='__main__':
    runpy.run_path(str(Path(__file__).resolve().parent/'verification/closing/audit_release.py'),run_name='__main__')
