# Source inventory reconciliation

**27 October 2026 · Komorebi P.**

The [review publication check](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/40580137408) stopped with `Availability/component ID mismatch`. The import configuration had grown from 153 to 166 components, while the availability and assessment indexes still contained 153. All 13 additional import receipts were already present at [commit 080487d6401a](https://github.com/KomorebiP/Operation-KOMOREBI/commit/080487d6401a7e9d90c415fd9ffbbf8d825e3842).

The indexes now include **166 imported components: 91 primary and 75 supporting**, owning **139,002 distinct source files**. The strict receipt validator checks configuration bindings, aggregate SHA-256 record digests, and every committed path, Git blob SHA-1 value, and mode. It found no missing or mismatched owned files. This comparison does not constitute a fresh SHA-256 read of every source blob.

The correction updates the availability index, contribution ledger, status catalog, and generated navigation together. Existing scientific assessments are retained. The **seven new primary works and six supporting collections remain scientifically unassessed**, including Lean coverage; [F16 in the finalization queue](FINALIZATION_QUEUE.md) records their next review gate. No imported source, proof, experiment output, or historical review is rewritten by this reconciliation.

| New component | Classification |
|---|---|
| [ARC-AGI-2 experiment](../experiments/arc-agi2/) | Primary; needs assessment |
| [Offline handoff](../experiments/arc-agi2/supporting-sources/offline-handoff/) | Supporting; scientifically unassessed |
| [Original solver](../experiments/arc-agi2/supporting-sources/original-solver/) | Supporting; scientifically unassessed |
| [Public evaluation](../experiments/arc-agi2/supporting-sources/public-evaluation/) | Supporting; scientifically unassessed |
| [Training evidence](../experiments/arc-agi2/supporting-sources/training-evidence/) | Supporting; scientifically unassessed |
| [Recovery v14](../packages/certified-inference/supporting-sources/recovery-v14/) | Supporting; scientifically unassessed |
| [Large Signal Model software](../packages/large-signal-model/) | Primary; needs assessment |
| [Supporting sources](../packages/large-signal-model/supporting-sources/) | Supporting; scientifically unassessed |
| [Machine Theory Compendium](../monographs/machine-theory-compendium/) | Primary; needs assessment |
| [Physics: curvature states](../research/physics-curvature-states/) | Primary; needs assessment |
| [Physics: energy and backreaction](../research/physics-energy-backreaction/) | Primary; needs assessment |
| [Physics: origin locking](../research/physics-origin-locking/) | Primary; needs assessment |
| [Realization Calculus: twin edition](../monographs/realization-calculus-twin-edition/) | Primary; needs assessment |

The [reconciliation record](../manifests/source-inventory-reconciliation-2026-10-27.json) pins the checked revision and records the exact added identifiers and totals. Mathematical proof coverage remains [26 of 62 Machine Societies pairs](MACHINE_SOCIETIES_PROOF_REVIEW_BATCH2_2026-10-27.md), including one qualified statement; source availability does not change those verdicts.
