# Revision log

## v0.3.0 — 2026-09-03

This release advances the v0.2.1 learned-checkpoint audit from a single
history/future endpoint to a two-index completion surface.

Scientific additions:

- exhaustive ordinary-history surfaces for every `0 <= L,H <= 8`;
- separate cumulative and exact history/future views;
- collision-free recursive hard continuation signatures;
- separate probability and centered-logit collapse assays;
- diagonal maps `Q_(L,H+1) -> Q_(L+1,H)` with exact D4 action checks;
- repeated `r4`, `f2`, `frfr`, and `rfrf` identity paths at registered token budgets through 64;
- matched final-bit-toggle nonidentity controls;
- first-revealing-suffix witnesses for delayed observability;
- fail-closed normalization and explicit numerical-validity accounting.

Integrity additions:

- all scientific sources, checkpoints, and the v0.2.1 lineage result were
  frozen before any v0.3.0 learned endpoint was inspected;
- the inherited v0.2.1 exact-`L6`/cumulative-`H3` behavior was replayed before
  the registered run;
- a maximal transparent-model dry run and 19 structural tests passed before
  source freeze;
- the registered result was independently audited with 1,247,629 consistency
  checks and zero errors;
- reporting scripts and release documents were added post hoc without
  changing the twelve frozen scientific files.

Result change:

- the post-transition ordinary hard code is exact throughout the registered
  window, but one seed-0 root anchor invalidates the cumulative hard rectangle;
- exact soft collapse is rejected;
- repeated identity paths expose delayed hard failures at greater depth;
- matched nonidentity failures prevent attributing the broad long-path defect
  solely to identity-loop holonomy.

The v0.2.1 registration, report, and run receipt are retained under `lineage/`.
