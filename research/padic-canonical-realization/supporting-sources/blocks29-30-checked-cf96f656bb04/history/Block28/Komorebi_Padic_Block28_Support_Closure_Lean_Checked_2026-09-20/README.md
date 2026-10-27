# Komorebi p-adic program — Block 28

Authoritative focused release: least support-aware coefficient coordinates inside
the least degree profile. The canonical all-coefficient theorem is preserved.

Read REPORT.md, PROOF_BOUNDARY.md, RESULTS.json and CONTINUE_HERE.md. Source is in
lean/KomorebiPadic. Exact finite audit and examples are in verification. Fresh
command logs, return codes, input hashes and axiom closures are in results. The
compiled directory contains project proof artifacts only, not a compiler runtime.

Read-only verification: python3 verify_release.py
Build reproduction: REPRODUCE.md
The complete release preserves all earlier blocks and adds this one under
blocks/Block28. This focused release already contains every production Lean module
needed by the current project; the pinned external mathlib cache remains separate.
