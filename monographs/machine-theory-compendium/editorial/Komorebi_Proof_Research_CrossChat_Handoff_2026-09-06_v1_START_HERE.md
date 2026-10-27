# Komorebi proof research: cross-chat handoff

**Author: Komorebi P.**  
**Snapshot: September 6, 2026 (America/Chicago)**  
**Archive: `Komorebi_Proof_Research_CrossChat_Handoff_2026-09-06_v1.zip`**

## Resume from here

This is a consolidated handoff of the mathematics, code, experiments, learned artifacts, negative results, and release history developed in this conversation. It is not a verbatim chat transcript and does not claim to contain every Komorebi project.

**Latest active work: Typed Proof Learner v0.3.0.** It constructs propositional proof terms and proposes useful intermediate claims before completing a target. A proposed claim must be proved and checked before use. Start in `active/Komorebi_Typed_Proof_Learner_v0.3.0/`.

**Parallel retained branch: Resolution Completion v0.12.0.** It contains the longer development from certified representations to world-model learning and live tactic proof feedback. Start in `active/Komorebi_Resolution_Completion_v0.12.0/`.

These are separate branches. The typed constructor has **not** been integrated into the world-action dispatcher. Do not infer a completed integration from having both in one archive.

## Contents

| Location | Purpose |
|---|---|
| `active/` | Complete, unchanged expanded copies of both latest releases |
| `releases/` | All 17 original project ZIP releases, byte-for-byte preserved |
| `findings/` | 16 standalone results and verification reports |
| `individual_outputs/` | Individually delivered source files, proof files, guides, JSON reports and demonstrations |
| `references/` | Consulted Komorebi source excerpts, AI machinery inventory, and external-source retrieval map |
| `toolchain/` | Portable Lean starter, assembly instructions and part hashes, not the large runtime |
| `SOURCE_ARCHIVES.json` | Original release filenames, source IDs, hashes and archive inventory |
| `RESUME_STATE.json` | Machine-readable state of both branches |
| `MANIFEST.json` | SHA-256 inventory of all payload files, excluding the manifest itself |
| `verify_handoff.py` | Standard-library integrity check for an extracted handoff |

## Before continuing

Read `CURRENT_STATE.md`, `NEXT_STEPS.md`, and the latest project's README and verification record. Preserve the distinction between proof, checked refutation, finite tests, and unresolved search. Existing logs are historical evidence, not a fresh run on changed source.

This packaging operation checked file integrity, original ZIP CRCs, and exact expanded copies. It did **not** rerun Lean, retrain the learner, or create new mathematical results. Use `RUN_AND_VERIFY.md` to run those checks in a later environment.

## Use in another chat

Ask:

> Open `Komorebi_Proof_Research_CrossChat_Handoff_2026-09-06_v1.zip` from my Library. Read START_HERE.md and CURRENT_STATE.md, then continue the Typed Proof Learner v0.3.0 from NEXT_STEPS.md. Preserve the recorded failures and distinguish inherited verification from new checks.

An archive saved to Library can be retrieved in a later chat where Library access is available. It does not automatically load into every new conversation. The companion START_HERE file provides a searchable index outside the ZIP. Use the archive's stable name, not an old sandbox path.

## Quick integrity check

After extracting this top-level folder:

```text
python verify_handoff.py
```

A successful integrity check means the packaged bytes match the handoff manifest. It is not a Lean proof check.
