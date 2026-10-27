# Exploratory evidence, not authoritative replay

`scan_original.py.txt` preserves the original exploratory script as inert text. It used a work-directory-specific import of the predecessor's `general_carrier.py`, a degree-18 column enumeration, and a floating-point LP. It is not advertised as a portable runner. The preceding ZIP contains that discovery implementation.

`scan.json` preserves raw exploratory results, including the rejected modulus-45 input (1,10,19,28,36,37), which is not balanced. That input and its capacity are excluded from all theorem statements and the final input JSON. Do not use this file as a Hodge census.

`check_cycle_formula.py` is a portable exploratory symbolic check, superseded by the broader authoritative `checks/verify_all.py`.

To reproduce the claimed exact results, use `python checks/verify_all.py` from the bundle root. Repeating the floating-point discovery process is unnecessary: frozen candidates are validated by exact, globally sufficient certificates.
