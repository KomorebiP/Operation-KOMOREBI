# Work and correction record

## Starting point

The unchanged v1.13.0 publication had written proofs of the three Chapter 30 results and recorded their Lean translations as unfinished. `BASELINE.json` fixes the parent archive and source identities. `TARGET_CONTRACT.md` fixed the actual infinite model, exact constants, complete tail statements, full real-budget limit, and literal ceiling schedule before implementation.

The work proceeded through dependent mathematical tasks: exact series estimates, actual Hilbert-vector construction and optimizer identification, deterministic noise transfer, and sharp asymptotics. Intermediate compilable statements were not treated as completion of a printed result until their model hypotheses were discharged. In particular, a conditional bias lemma did not close Corollary 30.3, and the sampled-budget limit did not close Theorem 30.2.

## Environment attempts

An initial remote setup was too slow to provide useful feedback. No remote proof output entered the accepted evidence. Its setup process was later observed to have exited; see `REMOTE_SETUP_RECONCILIATION.json`.

The local official compiler initially failed before proof elaboration because of this host's numbered process-path mismatch. `LEAN_SYSROOT` alone did not resolve it. A tracing diagnostic was denied and was not escalated. The narrow `readlink` compatibility shim then allowed the unchanged pinned compiler to run. The independent environment audit checked both release-file identities and the shim's restricted behavior. The final environment is recorded separately from the historical attempt record.

An initial root dependency build overlapped an agent's checkout and failed on a transient batteries HEAD lookup. The next dependency build passed. Other command-level mistakes included a relative helper path, a dependency path resolved from the wrong working directory, and an initial generic-budget draft write addressed to a nonexistent doubled project path. These caused failed commands or missing files, not accepted proof evidence. The final completion-record generation also initially used a relative parent path and failed before writing; it succeeded after resolving the project root absolutely.

## Mathematical proof development

The series proof establishes summability and exact infinite-tail identities before bounding them. Its cutoff estimates use telescoping comparisons for reciprocal powers. The Hilbert construction uses positive-coordinate indexing explicitly and proves equality with the existing universal regularized correction. Minor linter failures in an intermediate Hilbert compile were corrected and retained in the logs.

The noise proof first checked the scalar ceiling inequalities, then proved the actual diagonal bias estimate and applied the existing Hilbert stability theorem. The final corollary has no undischarged bias hypothesis.

The sharp asymptotic proof uses two monotone kernels, `f(x) = (1+x²)⁻²` and `h(x) = (1+x²)⁻¹`, with `g = h - f`. Their exact half-line integrals and a uniform right-sum comparison give the scalar limits. A separate generic mesh theorem uses the first crossing index and a two-sided squeeze to pass to all real budgets. It requires only the stated positivity, monotonicity, divergence, ratio, and sampled-product hypotheses. The actual mesh is shifted to `sqrt(A(n+1))`, avoiding the zero initial parameter. Finally, the actual hard-prefix vector's norm and residual tail yield the comparator limit one.

The asymptotic source went through fourteen recorded compiler attempts. Failed elaborations and their corresponding source snapshots remain under `logs/`; the final exact source and all 47 explicit declarations passed. A missing existing dependency object during the first full-budget application was resolved by building that existing module without editing it. The generic mesh proof's deprecated-lemma lint failure is also retained.

## Audit correction

The first targeted control run correctly elaborated the deliberate project axiom, but the harness failed to classify it because Lean printed its name without the namespace prefix expected by a substring test. The original script, report, and output are preserved with `_attempt_001` filenames. The corrected parser reads the entire reported axiom set and rejects every member outside the three permitted standard axioms.

The final control run has eight expected outcomes: two successes, five elaboration rejections, and one axiom-policy rejection. The wrong-asymptotic-constant control fails specifically because the theorem concludes π/4, not 1. The production audit uses Lean's recursive axiom collector and module provenance directly, rather than parsing printed theorem-name prefixes.

## Acceptance and scope

Independent reviewers matched every target conclusion against the actual source and the printed statements. A separate reviewer checked environment identity, reproduction instructions, unchanged parent sources, and the final package records. The root then replayed all seven new production modules and their import entrypoint with warnings rejected, checked every new exported declaration, and reran all eight targeted controls.

All original production theorem sources and original import entrypoints remain byte-identical to the parent. The new work adds seven modules and one entrypoint; only configuration and usage documentation changed among the parent's files. The completed publication PDF and archive are unchanged. All three target formalization obligations are closed; integration of the new status into a future publication edition remains a separate editorial release task.
