from __future__ import annotations

import sys

import arc_agi
import arcengine
import komorebi_arc3_offline

print(f"Python: {sys.executable}")
print(f"arc-agi: {getattr(arc_agi, '__version__', 'installed')}")
print(f"arcengine: {getattr(arcengine, '__version__', 'installed')}")
print(f"runner: {komorebi_arc3_offline.__version__}")
