# Continuation entry point

Read START_HERE.md and formal_release/LATEST_STATUS.md first. The current proof
release is v0.17.1; its production sources and recorded audits supersede older
conversation status statements. Its revised 49-claim contract and separate
original-wording ledger must not be conflated.

Read visual_appendix/README.md before changing the reader appendix. This is an
editorial source tree with exact-example checks, not an extension of the Lean
proof census. Main manuscript and appendix are composed at PDF level by the
included Python builder, with both LaTeX trees available for editing.

Run `python Run-PaperXII.py verify` before modifying files. Use build copies when
rerunning checks so the packaged evidence remains available. Do not treat the
packaging audit or an exact-example test as a new Lean compilation certificate.
Use BUILD_AND_DEPENDENCIES.md for the pinned toolchain requirements and replay
commands. Original arithmetic existence/realization inputs remain external.
