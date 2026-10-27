# Block 14 proof guide: target-relative joint reconstruction

**Machine-Native Reasoning · Reviewed Core 0.2 · Companion 0.14.0 · Komorebi P.**

This block formalizes Core **8.1**, `r:reconstruction`, at `source/core_v0.2.tex:873–878`. Together with the retained preceding blocks it covers **22 of 27 selected source results** when the current release gates pass. The source book and all 58 preceding substantive Lean modules are preserved byte for byte. Supporting lemmas and examples are not additional discoveries.

## Exact claim

Let V be a finite-dimensional vector space over a field K. A linear map A sends a state to its joint accessible record, and a linear map Q sends it to the protected target. A linear decoder D, defined on the **whole record space**, satisfies Q = D ∘ A exactly when ker A is contained in ker Q.

The condition says that any state difference invisible to the records is also irrelevant to the protected target. It does not require the records to determine the entire state. Full-state recovery, with Q the identity, is possible exactly when A is injective. For stacked records A(v) = (Aᵢ(v))ᵢ, the kernel of A is the intersection of the component kernels.

## Proof and implementation

The necessity direction applies D to A(v) = 0 and uses linearity to obtain Q(v) = 0. For sufficiency, first factor Q through the quotient V / ker A. The kernel inclusion is precisely what permits this quotient map. The canonical linear equivalence V / ker A ≃ range A then gives a linear decoder on attainable records. Mathlib's linear extension theorem extends that decoder from range A to the whole record space. Composing with A recovers Q.

The proof therefore includes the extension step in the manuscript. A decoder restricted to the range alone would not satisfy the stated interface. Conversely, surjectivity of A is not assumed: unattainable records may receive noncanonical values. Any two valid decoders agree on range A, but they need not agree everywhere.

The generic linear argument works for arbitrary vector spaces over a field using the classical extension theorem. The source-facing theorem explicitly retains finite-dimensional V and a finite participant family. This stronger generic infrastructure does not silently alter the source admission. The formalized maps are algebraic linear maps; no topology, continuity, conditioning, approximation or numerical stability claim is made.

For the full-state specialization, the identity map has zero kernel. A map with zero kernel is injective. For stacked records, a vector is in the joint kernel exactly when every component sends it to zero. The family may have dependent record-space types; the source specialization uses finitely many participants.

## Exact examples and source caveat

Over F₂, write the state as (b,s). Participant A observes b+s and participant B observes s. The joint target decoder adds the two records, since s+s = 0. A full-state decoder returns their sum and the second record, so the joint map is invertible. Either participant alone has a collision with different b values and cannot decode b, even with an arbitrary nonlinear function.

The source paragraph immediately after the proposition says that a nuisance bit may remain unknown. This is valid as a general target-relative possibility, but not for s in the specific two-dimensional invertible example: the second joint record already equals s. The manuscript remains unchanged. A separate three-dimensional example (b,s,n), with the same records (b+s,s) and target b, makes the intended distinction exact: changing n leaves all records unchanged, yet b is still reconstructible. Full-state recovery fails for this enlarged state.

The examples also exercise a nonsurjective record map with a total decoder. They check why kernel inclusion has the stated direction, why joint sufficiency does not give individual sufficiency, and why target reconstruction does not imply injectivity. Deliberately false variants are covered by explicit negative-control contracts. The concrete examples illustrate the generic proof; they do not substitute finite enumeration for it.

## Reading the formal files

| File | Role |
|---|---|
| `MachineTheory/JointReconstruction.lean` | Quotient/range construction, full-space extension, kernel criterion, full-state specialization and stacked kernels. |
| `MachineTheory/JointReconstructionExamples.lean` | Actual F₂ linear maps and exact boundary examples. |
| `checks/CheckJointReconstructionAPI.lean` | Direct source-facing types and public API checks. |
| `checks/NEGATIVE_CONTROLS.json` | Required diagnostics for deliberately invalid variants. |
| `docs/ASSUMPTION_REVIEW_BLOCK14.md` | Assumption and scope review. |
| `evidence/CORE81_SOURCE_AND_CODE_AUDIT.md` | Separate source/code review of the critical implications. |
| `evidence/RELEASE_RESULTS_BLOCK14.md` | Actual completed gate outcomes and counts. |

## Verification and limits

Admission requires two complete cumulative cold builds from identical frozen source, with the second using a separately extracted source snapshot. The verifier checks the exact source map, predecessor hashes, public interfaces, elaborated declarations, transitive axioms, same-kernel module replay and expected negative-control outcomes. Every production proof object must be byte-identical across the two runs. The allowed foundational axioms remain `Classical.choice`, `Quot.sound` and `propext`.

Both runs reuse the same pinned Lean and Mathlib runtime. Replaying proofs through the same kernel and comparing objects does not amount to an independent proof implementation. Source review remains distinct from machine verification. The release receipts record actual execution; historical receipts cannot certify subsequent edits.

An algebraic decoder establishes what the accessible records determine. It does not send records, authenticate their meaning, authorize disclosure, or install a bounded executable decoder in a recipient. Those remain separate application obligations, as the source states. No noisy reconstruction theorem, communication protocol, empirical evaluator, performance benchmark or physical-model validation is claimed.

Five selected results remain: Core 2.4, 2.5, 3.2, 8.2 and 8.3. The next connected result is Core 8.2, preserving legal operations under a quotient.
