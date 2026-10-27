# Current continuation: sum-preserving packet corrections

Start with `RESEARCH_NOTE.md`. The universal assertions use the classical results pinned in `SOURCES.md` and the explicit proofs in the note. Finite computations are recorded separately.

To verify the retained results from the parent `lehmer_residual_audit` directory:

    python continuation_symmetry/verify_all.py

Dependencies: Python 3, SymPy, NumPy and SciPy. The verifier imports the symbolic operator from the search module but does not invoke the optimizer. NumPy/SciPy are required by that module's imports. Only the separate proposal scripts use floating-point linear programming; retained certificates are rational and all decisive sign/dual checks are exact.

Main data:
- `KERNELS_EXTENDED.json`: fourteen universally null correction polynomials.
- `POSITIVITY_RESULTS.json`, `EXTENDED_RESULTS.json`: proposed coefficients and exact certificate margins.
- `DUAL_31.json`: exact impossibility witness for the seven-correction span through degree 16 at index 31.
- `VERIFICATION.json`, `VERIFY_LOG.txt`: latest exact verification.
- `AUDIT_RECORD.json`: command, versions, bounds, and input/output hashes.
- `FACTORIZATIONS.json`: bounded auxiliary-polynomial exploration, not a universal theorem.

The degree in kernel/certificate data is the degree of Q, not the degree of DQ or the theta weight. These are d, d+10, d+12 respectively.

The bundle also retains earlier research blocks. Their logs are historical, not a statement that all previous checks were rerun in this block. Nothing in this continuation proves Lehmer for all primes.
