# Recovered finite formal core

The unchanged stored original is Komorebi_Projector_Calculus_Lean_Browser_Core_v1.2.2.lean. BrowserCoreLocal.lean replaces its broad Mathlib import with five targeted imports and changes one unnecessary `simpa` to `simp`. The complete patch is retained. The theorem statements and mathematical scope are unchanged.

BrowserCoreAxiomAudit.lean repeats the checked core and adds #print axioms for its 39 named theorems. This duplicate is an audit harness, not an additional theorem count. The local build passed with warnings as errors. Only propext, Classical.choice and Quot.sound appear, and no sorryAx appears.

This checks operator grammar, finite projector/transfer algebra, coefficient sections, finite differences, and finite diagonal coordinates. It does not formalize the entire-function growth, analytic continuation, arithmetic asymptotics or other analytic claims of the monograph.

Run `python tools/check_local_lean.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /tmp/sf_lean.json` from the package root. No downloads are used. Initial failures (broad import timeout, one linter correction, and an audit-name parser error) remain in verification/local_lean/.
