# Paper VII computational replay audit

Fresh run: `fresh_20261006/manifest.json`, schema version 2, UTC
`2026-10-06T02:46:59.857625+00:00`. The manifest passed
`tools/validate_manifest.py ... --root PROJECT`. It records 791 execution inputs:
784 preserved raw source files, two archives, three replay/witness scripts and
two unmodified computation-audit provenance tools. No Git revision exists for
this recovered archive project; `commit: unavailable` and `dirty: true` are
explicit. Source and archive hashes identify the inputs instead.

## Contract and result

The contract is to replay available finite assertions in the shipped code,
authenticate the source archives, and check the internal consistency of the
stored final Lean report. A passing gate supports that code path and its stated
finite input range. A numerical failure would require distinguishing numerical
tolerance, implementation error and violated hypotheses before calling it a
mathematical counterexample. Missing dependencies leave their gate unavailable.
No gate supplies a universal theorem, a continuum limit, or a physical solution
of quantum gravity.

| Gate | Fresh result | Interpretation |
|---|---|---|
| Archive CRC and complete byte comparison | 725 complete + 59 strengthened files, all match | All 784 recovered raw file bytes match the delivered ZIP members |
| Source pre/post SHA-256 inventories | Identical, 784 files | Replay did not modify raw sources |
| Original `Run-PaperVII.py verify` | PASS, 723 manifest payload entries and 724 checksum entries | Original standard-library file-integrity gate; not a formal theorem verifier |
| Original `scripts/test_verifier.py` | 16 unittest cases pass | Software parsing, dependency and cache-invalidation regression tests |
| Original companion test functions | All 22 pass, 5 source files | Direct invocation of unchanged zero-argument functions; pytest collection/plugins were not run |
| Original `run_experiments` | All 1,048 leaf records exactly match, including 1,045 numeric fields | Deterministic finite experiment replay; comparison tolerance was unnecessary in this run |
| Strengthened `verification/verify_paper_vii.py` | 18,049 checks in 15 groups pass | Unchanged finite numerical and source checks, run in an isolated copy |
| Stored strengthened result comparison | Exactly equal | Structural result/counts and NumPy version match the stored report |
| Active formal source/inherited report consistency | 25 modules, 323 theorem audits consistent | Fresh static inventory and source/log hash checks of inherited 2026-09-06 evidence |
| Six constructed objects, separate binding audit | 12 fresh static checks pass | Source/inventory/runner/log/cumulative-report bindings agree; adds zero theorem declarations |
| Independent exact rational witnesses | 269 named assertions pass | Separate finite algebra examples using standard-library `Fraction` |
| Fresh Lean compilation and deliberate rejection controls | Unavailable | Lean, Lake and the pinned portable kit are absent; stored evidence is inherited |
| Original pytest runner | Unavailable | No fake pytest replacement was created |
| Original SymPy visual exact examples | Unavailable | SymPy and mpmath are absent; the rational witness script is an independent gate |

The original companion is copied to a temporary directory before loading its
test modules and library. Each original test function has zero arguments and
requires no pytest fixture. `test_experiment_certificates` calls the original
experiment suite as shipped; the replay then calls the same unchanged
`run_experiments` function with explicit JSON/CSV destinations to compare every
stored field. The documented all-in-one original runner also includes figure
generation, pytest and TeX rebuilding. This audit does not claim to have run that
full chain.

The strengthened package is also copied to a temporary directory. The unchanged
script writes its result, summary and PDF text there. It uses the actual shipped
TeX, bibliography, PDF, legacy results and 16 figure PDFs; its successful PDF
checks do not constitute a fresh TeX build. Six of its last-group checks consume
legacy numerical values rather than recomputing them; the separate original
experiment replay does recompute those values.

## Arithmetic, conventions and bounds

NumPy and SciPy computations use IEEE binary64 real/complex arrays. The original
library uses the computational tensor basis with qubit zero at the first
Kronecker factor. Projectors are assumed orthogonal and complete where required;
Hamiltonians are assumed Hermitian. Feshbach inverses are only meaningful where
the hidden block and full operator are invertible. The strengthened Feshbach
tests use `z = 0.4 + 0.7i` and Hermitian finite matrices, which provide those
invertibility conditions. The strengthened channel code uses column
vectorization, Choi output-tensor-input order, and output partial trace.

The original experiment RNG uses `default_rng(20260727)`. The original tests
use fixed seeds 4 and 2 in their two random tests. The strengthened script uses
`default_rng(20260814)` once with fixed ordering. No RNG is used in the independent
exact witness script. The original numerical tests retain their thresholds,
typically `1e-12` to `1e-10`, with moving-frame experiment tolerance `1e-6`.
The stored-field comparator records relative `1e-8` and absolute `1e-10`, but all
fields were exactly equal. The strengthened script starts with `TOL = 2e-9` and
uses explicit per-assertion tolerances up to `2e-7`.

| Strengthened group | Checks | Actual finite range |
|---|---:|---|
| Seed orbit and rank | 290 | `d = 1..5`, `m = 1..6`, `r = 0..min(d,m)`; explicit seed construction `m = 1..9` |
| Cyclic projectors and tensor refinement | 744 | Cyclic order `N = 2..9`, sampled multiplicities 1..3; tensor orders 2..5 |
| Circuit paths and interference | 80 | Dimensions 3..7, three sampled unitary gates, three sectors, 81 path terms |
| Fixed and moving leakage | 1,044 | Dimensions 2..8, 15 Hermitian samples each, eight times 0..1.5; three rotation speeds and eleven times 0..2 |
| Direct rotation and curvature | 184 | Forty angles 0.001..0.5; 10,20,40,80 steps; 9 by 11 interior Bloch points |
| Operator packets and channels | 165 | Dimensions 2..6; 21 damping parameters 0..1; 3D random linear supermaps |
| Lindblad coherence | 48 | Two-dimensional generator; eleven semigroup times 0..2 |
| Error correction | 164 | Three-qubit bit-flip code, four errors; 30 sampled densities, one perturbed error and 100 vector-pair tests |
| Feshbach and stability | 500 | Splits `(1,1),(2,1),(2,2),(3,2)`, 25 samples each; perturbations of scale `1e-4` |
| Memory kernel and local closure | 180 | Splits `(1,2),(2,2),(2,3)`, 15 samples each; six sampled times, one spectral/Laplace evaluation each |
| Euclidean transfer and reflection positivity | 336 | Dimensions 2..8, 12 samples each; six-vector reflection Grams, powers 0..6 |
| Spectral geometry | 14,206 | Dimensions 1..3, sizes 4..32; full 1D and 2D mode lists for 2D sizes≤18, otherwise 100 sampled modes; heat times .01,.03,.1,.4, sizes 16,32,64,128 and reference cutoff 80 |
| Constraints | 14 | Pauli span closure, one nonclosing pair, one common-kernel compression, one 2-to-3D isometric transport |
| Bounded towers and closures | 60 | Twelve 4D Hamiltonians; four sizes 5,10,20,40 for kernel/constraint/heat illustrations |
| Legacy certificates and source integrity | 34 | Six stored numerical values; current TeX/Bib/PDF and 16 vector figures, 193 abstract words, 149 labels, 29 references |

Original experiments use three-qubit reachability at maximum word depth 5; a
two-qubit Bell/parity system; 101 leakage times 0..5; one random Hermitian
6-by-6 Hamiltonian at `z = 7.5 + 0.4i`; a 2D moving frame with time-difference
step `1e-6`; 31 Bloch angles with derivative step `1e-5`; one damping parameter
.23; a three-qubit bit-flip recovery; circle sizes 32,48,64,96,128,192; one
256-cycle and one 48-by-48 torus at 180 heat times; and a 42-state confining
nearest-neighbor volume toy at transfer time .35. These are finite diagnostics.

The independent exact witness bounds and certificates are in
`EXACT_WITNESS_AUDIT.md` and `fresh_20261006/exact_rational_witnesses.json`.
They are not replacements for the unreplayed SymPy examples or Lean modules.

## Implementation review and residual limits

Object reconstruction, tensor order, channel completeness, Choi partial trace,
projector idempotence/orthogonality, and the relevant norm and trace invariants
were inspected in the original library and strengthened verifier. The seed
orbit matrix `C.T` tensor identity is consistent with column vectorization.
The Choi and vectorization conventions are internally consistent. The exact
small witnesses provide an independent algebraic benchmark for projector,
seed, rational channel and Schur/Feshbach identities.

The following limits matter when interpreting the result:

- Floating rank decisions use thresholds, and the code does not provide
  conditioning/error certificates for every sampled matrix. Successful residuals
  are numerical evidence rather than exact proofs. The strengthened seed cyclic
  criterion uses both an explicit rank tolerance and NumPy's default tolerance.
- In the strengthened dispersion loop, `-N//2` means `(-N)//2`. For odd `N`,
  `arange(-N//2, N-N//2)` has `N+1` entries and repeats a residue class. The
  inequalities remain tested at those actual indices. This loop must not be
  described as enumerating exactly `N` distinct residue representatives. The
  separate heat-trace checks use even sizes and do not have this issue.
  A separately labeled corrected edition closes this bookkeeping issue with
  exactly two lower-endpoint edits. It passes 87 representative assertions for
  sizes 4..32 and 17,699 suite checks in 15 groups. The preserved raw 18,049-check
  replay remains unchanged. See `corrected_strengthened/CORRECTION_AUDIT.md`
  and `corrected_fresh_20261006_r2/manifest.json` for separate evidence.
- The short-rotation example follows one fixed planar generator. Its direct
  rotation products are structurally exact up to roundoff and do not establish
  a convergence rate for arbitrary moving projectors. The strengthened Bloch
  test uses analytic derivatives despite its comment mentioning finite
  differences; the original experiment uses finite differences.
- The bounded tower sets `hlim = hs[-1]`: it checks a finite terminal tail
  inequality, not convergence of an infinite sequence. Its scalar identity
  perturbation leaves commutators unchanged, so it is not a general anomaly
  closure experiment.
- The original public library relies on documented mathematical assumptions.
  For example, its bit-flip channel checks four probabilities and their sum but
  does not reject negative probabilities, and its Euclidean transfer helper
  casts the Hamiltonian to real arrays. The passing intended cases do not
  certify unrestricted inputs to these helpers.
- Stored theorem source and log hash equality authenticates consistency with
  the inherited report. It does not independently recheck the kernel, imported
  Mathlib proofs, omitted compiled interfaces, or the original environment.

Structural evidence here is the exact finite algebra and specified invariants.
Observed ranks, residual sizes, spectral plateaus and finite convergence plots
remain tied to their cases. A uniform conclusion requires the corresponding
paper proof with its hypotheses, reviewed separately.

## Provenance and rerun

Actual environment: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib
3.10.8, PyMuPDF 1.26.6, Linux x86-64. `pdftotext`, `pdfimages`, TeX tools and Git
were found. Lean, Lake, SymPy, mpmath and pytest were not found.

The run completed in 2.480446 seconds under a 600-second wall limit, 10-MiB
combined log cap, 2-GiB per-process address-space limit, 480-second per-process
CPU limit and one-core affinity. Numerical thread variables request one thread;
libraries may ignore those cooperative limits. The manifest records this risk.

From the recovered project root, choose a new output directory:

```bash
python verification/scripts/reproduce.py --source source --downloads downloads --out verification/my_fresh_run
python verification/tools/validate_manifest.py verification/my_fresh_run/manifest.json --root .
```

`--source` and `--downloads` are relative to `--root`, which defaults to the
current directory. Results are saved outside the protected input trees. The
portable helpers in `tools/` were copied unchanged from the installed
`mathbox:computation-audit` bounded runner and validator. The wrapper pins all
source/archive/script bytes, uses actual software versions, and never installs
dependencies. Original commands are derived from `Run-PaperVII.py`, the snapshot
README, companion `Run_All.ps1`, and the strengthened script's `main` entry.

The manifest directly hashes the declared scientific `results.json`; that file
in turn records hashes of all 15 replay result/log artifacts. Full stdout and
stderr are separately hashed by the runner. A completed process is execution
success; the finite interpretation in this audit is separate.

`constructed_bindings_20261006/manifest.json` separately records the six-object
binding audit. It validates the saved audit source, inventory, runner, log and
cumulative-summary hashes, the source `#print axioms` set, parsed stored log
audits, allowed axioms, inherited completion flags and all 25 cumulative source
hashes. Its reusable standard-library command is:

```bash
python verification/scripts/check_constructed_bindings.py --source source --out verification/my_constructed_bindings/results.json
```

This checks inherited evidence only. The actual constructed-object Lean audit
still requires the original pinned kit and regenerated interfaces.
