from deterministic_bootstrap import ensure as _ensure_deterministic
_ensure_deterministic()

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")
from stage_preaudit import main as preaudit
from stage_final import main as final
from external_preflight import main as external_preflight

if __name__ == "__main__":
    preaudit()
    final()
    # The package-local call intentionally has no third-party paths. It records
    # the current environment without pretending that the checkpoint ran.
    import sys
    sys.argv = ["external_preflight.py"]
    external_preflight()
