"""Recompute every low Newton valuation printed in the final metric tables."""
from delta_boundary_checks import packet, mixed, vp
from pathlib import Path
import json
import sys


TABLES = {
    (2, 0): (1, 3), (2, 1): (2, 5, 9, 11),
    (4, 0): (1, 3), (4, 1): (1, 3),
    (4, 2): (4, 6, 9, 13, 16, 22), (4, 3): (2, 8, 8, 15),
    (8, 0): (1, 3), (8, 1): (1, 3), (8, 2): (1, 3), (8, 3): (1, 3),
    (8, 4): (4, 6, 9, 13, 16, 20), (8, 5): (3, 6, 10, 13, 17),
    (8, 6): (2, 6, 8, 13), (8, 7): (2, 11, 8, 15),
}
BOUNDARIES = ((16, 9, 5, 7), (32, 18, 6, 6), (32, 19, 5, 7))

records = []
for (width, address), valuations in TABLES.items():
    values = packet(width, address, len(valuations))
    for order, expected in enumerate(valuations, 1):
        coefficient = mixed(values, 0, [1] * order)
        assert vp(coefficient) == expected
        records.append(dict(N=width, j=address, k=order,
                            value=str(coefficient), valuation=expected))
controls = []
for width, address, first, second in BOUNDARIES:
    values = packet(width, address, 2)
    for step, expected in ((1, first), (2, second)):
        difference = values[step] - 1
        assert vp(difference) == expected
        controls.append(dict(N=width, j=address, H=step,
                             value=str(difference), valuation=expected))
result = dict(status="passed", coefficient_assertions=len(records),
              boundary_assertions=len(controls), coefficients=records,
              boundaries=controls,
              non_claim="Finite arithmetic proves these coefficient certificates and counterexamples; the universal metric requires the separate proved tail criterion.")
Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ("status", "coefficient_assertions", "boundary_assertions")}))
