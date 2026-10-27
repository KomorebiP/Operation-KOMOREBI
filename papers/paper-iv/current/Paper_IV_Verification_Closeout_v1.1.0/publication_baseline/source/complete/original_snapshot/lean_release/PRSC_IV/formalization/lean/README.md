# Paper IV v1.0.0

**Komorebi P. — September 5, 2026**

All 68 theorem-like manuscript results now have their full scoped statements covered in Lean: 68 full, 0 partial, 0 unmapped. The last 15 partial records are closed by nine new modules. The original statements and hypotheses are preserved.

The 151-row map covers 1164 declarations (953 theorems and 211 constructions). The namespace audit covers 2234 declarations, including 1999 theorem declarations. The warning-fatal integration build passes 3521 jobs. The existing 43 semantic checks are retained. Permitted transitive axioms: `propext`, `Classical.choice`, `Quot.sound`.

The package contains the PDF and LaTeX, complete Lean sources and pinned lockfile, reviewed theorem map and declaration-kind contract, kernel audit, checksum manifest and reproduction scripts. Build caches are excluded.

The general coefficient-order criterion, imported standard fact 11.1, remains explicitly imported; it is outside the 68 results and is not needed by the checked order proofs. Open problems and historical priority are outside this contract. Complex powers retain their stated branch domains; conditional asymptotic theorems retain their original hypotheses.

Run from a short extraction path:

```sh
../../VERIFY.sh --release --archive /path/to/PRSC_IV_v1.0.0.zip
```

See `../../provenance/COMPLETION_STATUS.md` for result-level coverage and `formalization/lean/LEAN_THEOREM_MAP_v1.0.0.md` for exact declarations.
