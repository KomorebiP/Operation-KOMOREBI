# Five-core packet continuation

Start with `RESEARCH_NOTE.md`. `SOURCES.md` records the classical dependencies.

Run the complete bounded audit from the parent directory:

```
python3 continuation_5core/check_five_core.py
```

Only Python's standard library is required. The script imports the retained parent `explore.py` for an independent Jacobi recurrence and small eta-product check.

- `explore_shell.py`: exact shell enumeration and packet polynomial construction.
- `check_five_core.py`: hook, shell, polynomial, valuation, and local-root checks.
- `RESULTS.json`: exact selected coefficient arrays, tau values, root residues and counts.
- `RUN_LOG.txt`: retained execution summary.
- `MANIFEST.json`: bounds, arithmetic conventions, input/output hashes and execution provenance. Its external schema validator was not run.

Status: all stated finite checks passed. Two explicit root-resolution certificates are proved from the exact polynomial residues. A general termwise index-prime-unit lemma is proved in the note. Lehmer's conjecture remains unproved by this continuation.
