from __future__ import annotations

import json
from pathlib import Path

from generative_deformation.experiments import run_all


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    print(json.dumps(run_all(base), indent=2))
