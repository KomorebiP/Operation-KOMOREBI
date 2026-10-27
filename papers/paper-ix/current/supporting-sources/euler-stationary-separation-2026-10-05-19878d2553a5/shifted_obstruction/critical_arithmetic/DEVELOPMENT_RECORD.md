# Development record

The first bounded-run invocation supplied the computation-contract path relative
to the execution root, while the runner reads that argument relative to the
calling directory. It failed before launching the computation with a missing
contract-file error. Supplying the correct path fixed this setup error. No
mathematical failure or partially completed computation was counted as a pass.

The local arithmetic proof did not establish the requested all-index
nonvanishing theorem. The rational approximation route reaches a valid finite
certificate, but its available height bound does not separate the approximation
from zero. The rationality-transfer shortcut is explicitly refuted by the cubic
in Section5 of LOCAL_ARITHMETIC_CERTIFICATE.md.

The final run additionally checks the exact integer polynomial identity behind
the cubic's critical-value expression. The prior certified_run is retained as
development evidence; certified_run_final pins the final script and proof.
