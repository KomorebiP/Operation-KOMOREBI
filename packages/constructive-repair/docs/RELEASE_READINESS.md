# 1.0 release gates

Candidate: **1.0.0rc3**. Scope: standalone exact rational constructive repair.

The mathematical source and wire schemas remain frozen. The new candidate
replaces recursively embedded release ZIPs with exact proof snapshots and adds
an artifact-level gate binding the current source, current wheel, fresh test
receipts, and compiled monograph.

## Technical gate

From a freshly extracted, unmodified distribution:

```bash
python scripts/release_gate.py
```

A passing result contains `technical_status: PASS` and, while licensing is
unselected, `publication_status: AWAITING_AUTHOR_LICENSE_SELECTION`. These two
fields deliberately answer different questions. The command performs read-only
checks and suppresses local bytecode cache creation. Execute further work in a
separate copy or output directory, since added files violate a strict manifest.

The gate does not rerun Lean. The full replay command remains:

```bash
python scripts/verify_release.py --kit /path/to/PINNED_KIT --output /tmp/new-lean-evidence
```

An offline Python acceptance rerun is available separately:

```bash
python scripts/accept_release.py --output /tmp/new-python-evidence
```

Both output locations must be new. Receipts are evidence of the configurations
actually tested, not general platform guarantees. The gate is not a signature,
an independent theorem prover, or a proof of the external JSON parser.

## Remaining author decision

Public code and document license choices remain unselected. Permissions are
unchanged. `PUBLICATION_DECISION.json` records no authorization to publish.
Adding selected license texts or changing metadata requires a new artifact build
and appropriate checks. No foundational expansion is needed for that step.

No source or package has been uploaded to GitHub, PyPI, or another service.
Main-library integration, authoritative Paper III imports, other operating
systems, a fully formal external parser, and native arithmetic applications
remain separate scoped work rather than requirements hidden inside this tag.
