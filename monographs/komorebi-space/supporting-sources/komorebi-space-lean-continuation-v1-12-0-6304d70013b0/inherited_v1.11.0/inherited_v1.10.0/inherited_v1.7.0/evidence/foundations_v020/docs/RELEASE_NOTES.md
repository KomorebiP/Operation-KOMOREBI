# v0.19.0

# Komorebi Space Theory: derived holonomy projection and stability
## v0.19.0 · Komorebi P.

This block discharges the anchor-correction estimate left as a hypothesis in v0.18, for finite-dimensional real inner-product fibers. It constructs the orthogonal anchor projection, derives a finite optimal gain for the existing maximum residual norm, and applies the result to actual graph transports and ambient sections. An exact Cayley-rotation family proves that a common gain over all connections is impossible, even on a fixed triangle with real fiber dimension two.



See HOLONOMY_PROJECTION_STABILITY.md and the current verification records.

---

# Current update — v0.7.0

v0.7 adds six modules, 79 named theorems and 45 indexed constructions. The 44 previous proof modules are unchanged. See `LOSSLESS_RESIDUAL_EXTENSION.md`.

---

# Release v0.6.0 — controlled residual reindexing

Six new modules and 84 named theorem declarations; cumulative 44 modules, 480 named theorems and 203 indexed constructions. All 38 prior proof modules remain byte-identical.

New results: typed block telescope; bounded common-schedule candidate/residual maps; `d_phi S_phi = C_phi d`; gain bounded by the maximum skipped-block length; exact repair-mismatch factorization; triangular presentation-change coordinates; cofinal cancellation counterexample; sharp stride gain; bounded-gap preservation of local residual decay.

Read `RESIDUAL_REINDEXING_EXTENSION.md` for hypotheses. Read `VERIFICATION.md` for current evidence and failures. Numerical residual invariance and automatic repair naturality are explicitly not asserted.

---

# Historical release notes

# Release v0.3.0

Added five modules and 84 named theorem declarations. Total: 25 modules and 240 named theorems. All original v0.2.0 proof modules are byte-identical.

The primary addition is an explicit bounded correction operator for split Banach towers with a strict propagation gap, followed by a continuous linear equivalence between the candidate space and protected semantic coordinates times residuals. Exactness becomes the zero-residual coordinate slice.

The construction preserves the entire seed/innovation profile, not merely an initial scalar flag. Exact separation and uniqueness for that observable are proved rather than assumed.

A real dimension-growing model satisfies all hypotheses. Its repaired identity has the all-level formula diag(2^(-n), …, 1). An identity-bonding counterexample proves that a bounded residual need not have a bounded primitive when the strict gap is absent.

Independent exact-rational checks cover 360 deterministic cases and 2,564 positive assertions, plus two mutation controls. These are implementation checks, not the source of the universal Lean conclusions.

The offline pinned runtime was restored from its saved split archive. A clean baseline replay succeeded. The first release-level build found that the new root imports had been appended after a `set_option` command. All individual modules compiled, but the root failed; imports were moved to the import header and the full audit rerun. The failed build is retained in `audit/root_import_order_failure/`. Development elaboration and linter failures are retained in `audit/development_v0.3.0/`.

Historical release notes follow.

---

# v0.2.0 release notes

**Komorebi P. — September 27, 2026**

The highest-priority algebraic/analytic bridge in v0.1.0 is now instantiated for uniformly bounded sequential Banach towers on a common schedule.

The release adds six Lean modules with 60 named theorem declarations to the unchanged 14-module baseline. It constructs the actual complete operator-family space and bounded naturality differential, builds an explicit protected correction iteration, proves its limiting bounded projection and exact/residual splitting, and realizes repaired maps on coherent inverse-limit points. A constant-tower model establishes genuine canonicity, a split model verifies a nonvacuous correction scheme, and a finite-coordinate example refutes unconditional uniqueness.

All 20 modules and the root import passed a fresh build with warnings as errors. All 156 explicit named theorems passed the dependency audit. All three negative controls passed. The separate delivery receipt records the extracted-ZIP replay.

The correction-operator hypothesis is not erased. No full pro-category localization, universal representation stack, higher obstruction complex, general descent, or arithmetic correspondence is added by assumption.

See `BANACH_TOWER_EXTENSION.md` for the mathematical statements and `VERIFICATION.md` for the actual checks and trust boundary.
