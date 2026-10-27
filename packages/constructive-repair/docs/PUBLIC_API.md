# Proposed 1.0 public interface

## Supported surface

The public import is `komorebi_repair`. Exported names are `ExactMatrix`, `InvalidData`, `Outcome`, `free_problem`, `menu_problem`, `load`, `solve`, `verify`, and `__version__`.

The engine modules `repair_certificates`, `rational_menu`, and `branch_menu` remain shipped for compatibility with the source workflows, but their internal helper names are not part of the stable public API.

`ExactMatrix` stores immutable tuples of exact `fractions.Fraction` entries. `ExactMatrix.of` accepts integers and Fractions, not floats or booleans. An explicit column count must agree with nonempty data. For an empty matrix, supply the column count explicitly when it is nonzero. Duplicate column selections are permitted as linear-algebra data; boolean or noninteger indices are not.

`free_problem(D, R)` creates a validated original free-repair problem. `menu_problem(D, E, R, costs, admissible_masks=None)` creates the current branch problem. `None` admits all subsets. `[]` admits none. An explicit list must be sorted, duplicate-free and in range. It can be nonhereditary.

`load(path)` checks file bytes and parses a problem, raising `InvalidData` for malformed mathematical input. Filesystem errors remain ordinary filesystem exceptions.

`solve(problem, max_nodes=8191, max_linear_trials=8191, max_menu_trials=256)` copies the original problem, dispatches by its explicit schema, constructs witnesses and rechecks them. The node and linear limits apply to branch problems. The menu trial limit applies to legacy exhaustive menus. Free repair uses exact matrix elimination subject to the matrix/wire limits. These are work limits, not a wall-clock guarantee.

`verify(problem, certificate)` copies the inputs and checks all required equalities, constraints and source binding. It does not trust a producer's status label. Mutating the caller's certificate later cannot change the stored snapshot in the returned outcome. The certificate data within an Outcome are still ordinary Python data, not a cryptographically immutable object.

## Outcomes

An `Outcome` has `status`, `mode`, `problem_sha256`, `certificate`, `checks`, `statistics`, `trace`, `error_code`, and `error`. `to_dict()` produces a JSON-compatible snapshot. Its `kernel_checked` property is always false.

- `PYTHON_CERTIFICATE_VALID`: an exact Python check passed. Inspect `certificate.kind` for the mathematical outcome.
- `UNRESOLVED`: invalid input/certificate or exhausted resources. This does not rule out a repair.

Common `certificate.kind` values are `optimal_free_repair`, `optimal_menu`, and `no_admissible_repair`. The last concerns only the original admissible menu.

The separate source-archive Lean commands can return kernel-checked statuses only after successful compilation, axiom audit, replay and original-input echo. The wheel API intentionally provides no convenience flag that asserts Lean has run.

## Wire compatibility

The existing protocols are preserved unchanged:

- `komorebi.repair.rational.v0.3.0`
- `komorebi.repair.rational-menu.v0.4.0`
- `komorebi.repair.branch-menu.v0.5.0`

A software release number is not a reason to rewrite stored certificate schemas or their original-problem hashes. All 72 previously exported problems and certificates remain accepted by the public interface. Schema changes require a new explicit version and migration description, not silent reinterpretation.

## CLI contract

`komorebi-repair solve INPUT --output NEW_DIRECTORY` and `check INPUT CERTIFICATE --output NEW_DIRECTORY` emit one final JSON record on stdout. Exit zero means Python validation succeeded, including a valid scoped no-repair certificate. Exit two means unresolved or command-line failure. Existing output paths are not overwritten.

`doctor` reports the installed Python capability and explicitly does not claim a Lean execution. `python -m komorebi_repair` is an equivalent entry point.

## Installation scope

The wheel is pure Python and requires no third-party runtime package. It is tested here on Linux x86_64 with CPython 3.13.5. The source syntax targets Python 3.10+, but other interpreter/platform combinations are not promoted to tested status by the wheel's portability tag. The declared release-tested configuration remains Linux x86_64 / CPython 3.13.5. `PLATFORM_SUPPORT.md` records every untested combination and the offline runner. This support scope is fixed for rc2; a portable wheel tag does not expand it.

## Text I/O in rc2

Source exporters, evidence readers/writers, and text subprocess captures explicitly use UTF-8. This fixes the demonstrated failure under the POSIX C locale. Mathematical functions, public signatures, wire schemas, and Lean declarations are unchanged. Exact exported Lean source remains subject to the separate kernel workflow.
