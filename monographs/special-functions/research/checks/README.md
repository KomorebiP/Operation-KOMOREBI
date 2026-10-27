# Finite verification suite

The exact proofs are in `routes/`; these programs verify their implementations and finite examples. A successful run proves none of the universal analytic or priority claims by itself.

| Script | Arithmetic and finite scope | Reported exact assertions |
|---|---|---:|
| `nonlinear_dilation.py` | Rational recurrence and independent Picard integration through degree 61; five rational scales; symbolic coefficient polynomials through index 12 | 1,218 |
| `asymmetric_dilation.py` | Rational recurrence and Picard integration through degree 61; seven scale pairs and two two-channel banks; bivariate coefficient polynomials through index 8 | 1,811 |
| `complex_depth.py` | Exact rational depth shifts, radical invariance and Gram determinants on finite arithmetic supports | 301 |
| `orbit_zeta.py` | Exact rational power sums for integers N=2..8 and k=1..8; triangular, formal-log and reciprocal constructions; N=2/4 Bernoulli closed forms | 138 |
| `arithmetic_polynomials.py` | Numerical arithmetic moments, orthogonality, matrix pencils, transport, Uvarov, endpoint recovery and differentiation at 160 decimal digits | 0 |

The suite has **3,468 exact assertions**. The complex-depth script additionally makes three numerical direct/Newton comparisons at 80 digits. The arithmetic polynomial script makes **2,273 numerical assert statements** at 160 digits, for a combined numerical total of **2,276**. Counts use executed assert statements: an `all(...)` group, compound positivity condition or maximum coefficient residual counts once. They do not count every underlying scalar comparison separately. Arithmetic counts are reconstructed from its inspected loops and successful report metadata, with a complete breakdown in the aggregate summary.

Numerical assertions include 60 arithmetic parameter cases and 1,260 orthogonality residuals, 12 matrix pencils with 30 determinant residuals, three sieve-margin bounds, 60 depth transports, 48 tau identities with separate positivity assertions, 24 Uvarov formulas, seven endpoint bounds and one derivative residual. These calculations are not interval or ball certificates.

## Reproduce individual checks

Use Python 3.12 or later, without `-O`. All exact-only scripts use the standard library. `complex_depth.py` and `arithmetic_polynomials.py` also require mpmath; the recorded run used version 1.3.0.

From the project root:

```bash
python checks/nonlinear_dilation.py
python checks/asymmetric_dilation.py
python checks/orbit_zeta.py
python checks/complex_depth.py
PYTHONPATH=/path/to/mpmath-parent python checks/arithmetic_polynomials.py
```

The standalone arithmetic script writes `evidence/arithmetic_polynomial_checks.json`. The aggregate preserves an exact byte-for-byte snapshot below its fresh run directory so that this location-dependent output goes into that directory. Original source hashes and snapshot equality are recorded; the mathematical implementation is unchanged.

## Reproduce a bounded aggregate run

Set `SF_DISCOVERY_PROJECT` to this project's absolute directory and `SF_AUDIT_SKILL_DIR` to the installed mathbox computation-audit skill directory. If mpmath is already importable, omit the aggregate's `--dependencies` argument. Otherwise it must name the directory containing the mpmath package. Choose a fresh `--output` directory and change every result path together when repeating a run.

```bash
python "$SF_AUDIT_SKILL_DIR/scripts/run_experiment.py" \
  --root "$SF_DISCOVERY_PROJECT" \
  --contract "$SF_DISCOVERY_PROJECT/evidence/final_run_contract.json" \
  --input checks/run_all.py \
  --input checks/nonlinear_dilation.py \
  --input checks/asymmetric_dilation.py \
  --input checks/complex_depth.py \
  --input checks/arithmetic_polynomials.py \
  --input checks/orbit_zeta.py \
  --input checks/README.md \
  --input routes/nonlinear_dilation.md \
  --input routes/asymmetric_dilation.md \
  --input routes/complex_depth.md \
  --input routes/arithmetic_polynomials.md \
  --input routes/orbit_zeta.md \
  --input evidence/independent_math_review.md \
  --input evidence/final_run_contract.json \
  --output evidence/final-run-001 \
  --result evidence/final-run-001/summary.json \
  --result evidence/final-run-001/nonlinear_dilation.json \
  --result evidence/final-run-001/asymmetric_dilation.json \
  --result evidence/final-run-001/complex_depth.json \
  --result evidence/final-run-001/orbit_zeta.json \
  --result evidence/final-run-001/arithmetic-snapshot/checks/arithmetic_polynomials.py \
  --result evidence/final-run-001/arithmetic-snapshot/evidence/arithmetic_polynomial_checks.json \
  --timeout 600 --max-output-bytes 8388608 \
  --max-memory-bytes 2147483648 --max-cpu-seconds 300 \
  --max-cores 1 --max-threads 1 -- \
  python checks/run_all.py --output-dir evidence/final-run-001 \
    --dependencies /path/to/mpmath-parent

python "$SF_AUDIT_SKILL_DIR/scripts/validate_manifest.py" \
  "$SF_DISCOVERY_PROJECT/evidence/final-run-001/manifest.json" \
  --root "$SF_DISCOVERY_PROJECT"
```

The runner records supplied inputs before and after execution, command, software, limits, logs and declared-result hashes in a schema-v2 manifest. `run_all.py` also hashes the external mpmath Python source tree before and after execution and records its version. The external dependency is outside the project-relative runner input set; its source provenance appears in `summary.json`. Conventional thread environment caps are cooperative. CPU-time and address-space limits are inherited per process, rather than an aggregate process-tree CPU/memory budget.

No random sampling, network access or dependency installation is part of the verification command. A changed input or result invalidates the recorded provenance and requires a new run, or a separate documented correction.
