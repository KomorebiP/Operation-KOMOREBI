# Continue here — Machine-Native Reasoning, Lean Block04

**Author: Komorebi P. · Source book: Reviewed Core0.2 · Formal companion0.4.0**

1. Verify `SHA256SUMS.json` with `python scripts/verify_release.py` before generating new evidence.
2. Read `README.md`, `REVIEW_NOTES.md`, and `docs/BLOCK04_PROOF_GUIDE.md`.
3. Check the completed `evidence/final04/report.json`, `evidence/fresh04/report.json`, and `evidence/FRESH_REBUILD_BLOCK04.json` on their pinned inputs. They describe actual current-source verification, not every historical attempt.
4. The current formal frontier is **11/27** source results. `THEOREM_MAP.json` is the exact result register. `docs/NEXT_BLOCK.md` identifies Core4.1 as the recommended next step.
5. Use the existing finite `Instrument` and `Variation` interfaces. Do not replace exact probability laws with empirical frequencies or silently transfer a fixed-loss theorem to a changed loss.

No process needs to remain running for continuity. Source, proof objects, logs and the next obligations are in this package. The pinned external portable runtime is not included and must be supplied separately for a new build.
