# Fixed-spin chemistry recovery: focused replay export

Komorebi P. 13 November 2026. Python3.12, NumPy2.5.4, SymPy1.14.0.

This export contains the exact stage-fourteen proof/code files, their required
earlier helper modules, the frozen probes, saved certificates and a minimal
H10 input view. It is not the full historical handoff archive. Unused state
vectors, earlier research stages and machine-specific runtime logs/manifests
are omitted. The written self-review retains original evidence identifiers;
it is a historical report, not a claim that omitted runtime manifests are here.

FIXTURE_VIEW.json binds the derived NPZ to the original container. Its h1,
eri and ground_energy arrays have identical shapes, dtypes and element bytes.
Only these arrays are read by the molecular replay. Thus the Hamiltonian,
action-error cap and response are identical, while the NPZ container hash
reported in a fresh run differs. The saved original qualification remains
unchanged and records the original full-container hash. This distinction is
intentional; the small NPZ is not presented as the original container.

Run from this export root with fresh output folders:

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
python chemistry_stage14/recover_sector_cache.py --input chemistry_stage14/example_cache.json --output replay/certificate.json
python chemistry_stage14/audit_sector.py --output replay/exact
python chemistry_stage14/qualify_frozen_core.py --output replay/molecular
```

Expected:82 exact audit checks pass. The molecular projection identity and
exact positivity pass; response radius is below9.314e-11 at eta0.01 Hartree.
For new bounded provenance, use the installed mathbox computation-audit
run_experiment.py with record_runs.py --kind exact/molecular --run replay01.
It creates new manifests for the supplied input view; it does not reproduce
the original machine's runtime metadata or source-container hash.

PUBLIC_SHA256SUMS verifies all other export files. No claim is made about
neutral-state/source accuracy, frozen-core approximation error, original
full-H10 runtime superiority, actual Coulomb realizability of arbitrary PSD
representatives, or world priority. Read NORMAL_FORM.md, RECOVERY_THEOREM.md,
ROBUST_SPIN_COMPARISON.md and FROZEN_CORE_CONTRACT.md in chemistry_stage14.
