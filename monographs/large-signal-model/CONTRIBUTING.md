# Contributing

Technical questions, concrete counterexamples, proof corrections and reproduction reports are welcome through GitHub issues and pull requests. Refer to an exact proposition, declaration or command so the discussion can be checked.

The `Lean/` directory is the exact checked formal companion. Its manifest and source-bound receipts belong to those delivered bytes. Changes to the outer guides, workflows and publication material can be reviewed separately from mathematical source changes.

For a proposed mathematical revision, work on a branch and retain all relevant hypotheses. Update the source index, proposition correspondence and source checkpoint, and run a fresh clean Lean verification for the changed source before preparing its new frozen baseline. Preserve earlier release evidence rather than relabeling an old PASS. The current frozen-payload CI check deliberately flags changes to `Lean/` until a new reviewed and verified release baseline is supplied.

Run the read-only source and packaging checks from the repository root:

```bash
python3 ci/quick_checks.py --project Lean
```

The opt-in **Full clean Lean verification** workflow provisions the pinned toolchain and dependencies and invokes `Lean/scripts/verify.py` unchanged. Its new receipts are uploaded as workflow artifacts. It leaves the original evidence under `Lean/verification/` intact. See [CI and verification](docs/CI.md) for the exact scope and the distinction between the delivered verification and future CI executions.

For proof changes, report actual compilation, axiom-audit, kernel-replay and negative-control results. A timeout, missing dependency, unrelated elaboration failure or incomplete report is not a successful mathematical check. Explain any unresolved obligation directly.

Use the issue templates for the affected statement or the smallest reproducible build problem. Keep pull requests focused enough that another reader can identify the source change, its mathematical effect and its verification evidence. The repository's license and third-party notices apply to contributions and bundled material as specified in `LICENSE` and `THIRD_PARTY_NOTICES.md`.
