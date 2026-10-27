# Paper IX chart recovery record

Author: Komorebi P. — 8 September 2026.

Workspace maintenance removed the active chart working tree and its unfinished integrated verification run. The cumulative chart ZIP had not yet been assembled or saved. The previously saved perturbation release was recovered intact: 883 files, ZIP SHA-256 61322b5b58a43def882cb77eff8dd00d8af44f803c99f97cce27c2e7f909f4e9. The pinned Lean runtime survived.

The lost working tree had eight new modules. Individual development compilations had passed. Two integrated verification attempts failed due to inherited Python parsers truncating primed Lean declaration names. The first failed before compiling project sources because the inventory was missing. The second compiled the sources and contracts but rejected the axiom report for reorderPoint_inverse'. A third run was reported to have recompiled all 25 mathematical modules before maintenance removed its working directory. No completed PASS report or archive from that run was recovered.

Those descriptions are retained conversation observations. They are not substitutes for raw logs, which were lost. The earlier claim that those failed logs were preserved described their state before maintenance.

The new sources are reconstructed from recorded theorem statements and proof structure. They are checked in a new run, with new source hashes and newly retained logs. Byte identity with the lost sources is not assumed. The release verdict relies on this fresh evidence. The surviving previous release and its historical verification remain unchanged.

The reconstruction retains the actual full-Jacobian hypothesis, automatic coordinate selection, original root locus, arbitrary p-adic parameters, exact inverse projection, and every congruence depth. Weighted nonunit-Jacobian lifting and first-order root motion remain separate unfinished blocks.

The first post-recovery integrated run, replay_recovered_01, stopped with OSError [Errno 28] No space left on device after fourteen mathematical modules had passed. The same storage failure left its intended report empty. An attempted status read and the attempted independent reconciliation therefore could not parse that report. This was an environment failure, not a mathematical counterexample or completed verification.

Available logs and a separate disk-exhaustion record are retained. Reproducible compiled outputs from that interrupted run were removed to recover space. A new run uses replay_recovered_02; its own completed report and reconciliation determine the final status.

The second post-recovery run also stopped with Errno 28, after all 25 mathematical modules, both positive controls, and the first two contract files had passed. Its report could not be written. The available logs and disk-failure record remain preserved.

A third attempt placed gate outputs on the separate tmpfs filesystem but failed at compiler startup: the portable wrapper still tried to copy its executable-path adapter under the full /tmp filesystem. The fourth attempt preloaded the exact already-shipped adapter directly from the pinned kit, and placed the runner's temporary directory on tmpfs. This uses the existing wrapper/runner behavior without modifying Lean, Mathlib, or proof sources. Its safe execution environment and adapter hash are recorded beside the final gate.

The final archive is assembled and checked on tmpfs, then written into space already reserved for its local output. This prevents unrelated disk consumption from invalidating the completed release write. New failed run records are retained; none is reported as a successful proof check.
