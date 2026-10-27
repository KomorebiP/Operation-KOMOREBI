# Core 8.2 source and code audit

Primary verdict: **proved as written**, with deterministic successors interpreted on their enabled-action domain as the source explicitly stipulates. The reviewed code preserves that domain, constructs the quotient from the three stated fibre conditions, proves uniqueness of the actual partial data, and preserves every finite legal execution and its complete label sequence. No mathematical gap was found in the frozen sources below.

This is a separate source and raw-code review by an agent in the same model family. The source argument was reconstructed before inspecting the implementation. Focused Lean checks use the same pinned runtime as the authoring task. This is not independent peer review, a different proof kernel, an upstream source rebuild, or the cumulative release gate. This reviewer wrote only this report.

## Exact source, predecessor, and reviewed inputs

The authoritative theorem is Reviewed Core 0.2, label `r:governance`, canonical LaTeX lines 888–898. Line 886 supplies finite states, a finite action alphabet, protected labels, enabled-action sets, and a deterministic successor defined for enabled actions.

The complete base archive is retained at `evidence/history/block14/Komorebi_Machine_Theory_Lean_Block14_v0.14.0_complete.zip`. Its independently recomputed SHA256 is `5c709adbf7c3d45216804f4d6c27e27fd778115d79618ea23b7705d52d6867d4`, matching `PREDECESSOR.json`. In addition to hashing the archive, the reviewer read and compared all 60 predecessor substantive Lean files and all five source-book files against both the actual archive members and their recorded predecessor hashes. All 65 comparisons matched. This is a targeted preservation check, not a new replay of Block 14's historical proof evidence or a repeat of the full 8,258-file package check.

The following SHA256 values identify the reviewed Block 15 inputs. Paths are relative to `Komorebi_Machine_Theory_Lean_Block15_v0.15.0`.

| Input | SHA256 |
|---|---|
| `source/core_v0.2.tex` | `a15f192322357893c2bb9b2427aac2a02b0753e558b42c0460a6288006ddbe6b` |
| `MachineTheory/LegalQuotient.lean` | `072d47a330191db1a5952c7503d5f13fb9b2cf275f91a0876c24f6a88e36ccf8` |
| `MachineTheory/LegalTrace.lean` | `a9160dd3d5303aa10c24a57d8790630fb2b60ec02d3b1f4ffbfac9afeef3a7b6` |
| `MachineTheory/LegalQuotientExamples.lean` | `1e456bb98aaa2ccdcaf51f8a9ab50dc543e98671ddb4c1b3045069b05316c1d0` |
| `checks/CheckLegalQuotientAPI.lean` | `9e5e4a1fd18449a89c274fb8116f29682bede159f66e0ce90dbdd2b8199b3b02` |
| `docs/BLOCK15_PROOF_GUIDE.md` | `ffb2793ee67a27001f547d3eddc966f8972c78e2cbe476b494a7909904bac69b` |
| `docs/ASSUMPTION_REVIEW_BLOCK15.md` | `42ce6738d84f1a4b674785ca5f6f649af812177bd4cbea527b474797f29c6557` |

Continuity instructions were read in `CONTINUE_HERE.md`, `PROGRESS_LEDGER.md`, and `docs/NEXT_BLOCK.md`. The original reviewed source and preceding substantive Lean files were not edited by this reviewer.

## Normalized claim and reconstructed proof

Let X be a finite state space, A a finite action alphabet, L a label type, and π:X→Z surjective. Let ℓ:X→L be the protected label, D(x) the enabled-action set, and F(x,a,h) the deterministic successor when h proves a∈D(x). Quotient labels, enabled sets and legal successors exist exactly when π(x)=π(y) implies:

1. ℓ(x)=ℓ(y).
2. D(x)=D(y).
3. For any enabled action and corresponding legality proofs, π(F(x,a,hₓ))=π(F(y,a,hᵧ)).

Factoring quotient data immediately imply these conditions. Conversely, choose a preimage of each quotient state, use its label and availability, and project its legal successors. The three conditions make the construction independent of the representative. Surjectivity forces the data at every quotient state, establishing uniqueness on the legal domain. Induction on an arbitrary finite action list preserves availability, the projected state sequence, and every protected label.

The empty word must retain its initial state and label. An unavailable action must terminate execution as illegal, rather than invoke a fabricated successor. The implementation has both properties.

## Representation and dependency audit

`System` contains an actual label function and `step : X → Action → Option X`. The enabled set is precisely the domain on which `step` returns `some`. `none` means disabled. Thus a `System` encodes a deterministic partial function and does not contain arbitrary disabled-action successors.

This representation is connected to the source's independent inputs. `ofEnabled` accepts the given ℓ, D and dependent F. `enabled_ofEnabled` proves literal equality of the encoded and supplied enabled sets; `ofEnabled_step_of_mem` preserves every supplied legal successor; the complementary theorem returns `none` on disabled actions. `legalSuccessor` and `ofEnabled_reconstruct` establish the reverse representation. The proof does not silently replace the source's permission set with a smaller successor domain.

`Factors` has separate label, enabled-set and legal-successor equations. `FibreCompatible` has the corresponding three actual input conditions on equal fibres. It contains neither quotient existence nor a field assuming the desired theorem. `Factors.step_map` combines the legal equations into equality of canonical partial steps, handling the disabled case using the availability equation.

The sufficiency chain is explicit: surjectivity → actual representative → `representativeQuotient` → compatibility proves factorization. Necessity is proved separately. `quotient_unique` compares both structural fields at a preimage of every quotient state. `ofEnabled_fibre_iff` then translates compatibility to the raw ℓ,D,F conditions, and `finite_source_legal_quotient` states the source-facing existence-and-uniqueness equivalence directly for those inputs.

For executions, `execute` returns the initial state and every successor, or `none` when a requested action is disabled. `Factors.execute_map` proves equality of the quotient path with pointwise projection of the actual path. `Factors.legal_iff` reflects and preserves legality. `Factors.labels_eq` preserves the whole label list. `Factors.endpoint_map` separately exposes endpoint projection, and `Factors.lift_execution` lifts a quotient execution from any chosen representative of its starting state. These are general finite-list induction theorems, not bounded trace enumeration.

## Obligation matrix and boundaries

| Obligation | Finding |
|---|---|
| Exact labels and enabled sets | Passed, including the raw-input source translation. |
| Deterministic legal successor | Passed; one `some` value on each enabled pair. |
| Three independent fibre conditions | Passed; all are explicit and necessary. |
| Projected successor equality | Passed; literal equality of fine successors is not required. |
| Surjectivity | Explicit in existence and uniqueness endpoints. |
| Noncircular construction | Passed; the quotient is built from representatives. |
| Legal-domain uniqueness | Passed for canonical partial data. No uniqueness of arbitrary disabled defaults is asserted. |
| Source finiteness | Retained in source-facing declarations. |
| Empty carriers | Admitted; no `Nonempty` or `Inhabited` state assumption is added. |
| Arbitrary finite words | Passed; no fixed horizon substitutes for `List Action`. |
| Initial and intermediate labels | Retained, including the empty-word initial label. |
| Legality reflection | Passed, as well as forward preservation. |
| External authority | Outside the theorem and explicitly excluded. |

The generic representative argument and finite-word induction do not use finiteness. The source-facing finite assumptions nevertheless remain in the actual elaborated types. A finite X with surjective π also has finite quotient carrier; no additional nonempty quotient or label assumption is required. If X is empty, surjectivity forces Z empty and the construction remains well-typed. With no actions, only empty words are available and their initial labels are preserved.

The source's uniqueness statement is sound because its successors are defined only for enabled actions. If instead one arbitrarily totalizes disabled successors, those extra values can differ without altering legal behaviour. The code avoids that pitfall by using canonical absence and proving the exact source translation.

## Exact examples

The positive finite system stores an outstanding-repair bit and a historical bit. Observation is always enabled; repair is enabled only while outstanding. Forgetting the historical coordinate preserves labels, availability, and projected successors even though literal fine successors can differ. The example proves the complete repair-then-observation trace and rejects repeated repair after the first repair clears the outstanding condition. Its empty trace retains the initial label.

Separate counterexamples isolate loss of a protected label, unequal availability despite equal sensor labels, and unequal projected successors despite equal labels and availability. An unattained quotient state supplies two distinct factoring quotients when surjectivity is removed. A disabled partial step with different `getD` defaults exhibits why arbitrary totalized values are not unique quotient data.

These are exact finite definitions and proofs. They do not model an actual institution's authority or verify an access-control deployment. Their role is to expose hypotheses and boundaries of the general theorem.

## Focused checks executed

The runtime facade and environment were read from `evidence/runtime15/runtime_view.json`, using `/workspace/scratch/8e3bc2f54f55/runtime15/toolchain/bin/lean` and its recorded `LD_PRELOAD`. Existing Block 15 development objects were prepended to the recorded `LEAN_PATH`. Pinned upstream objects were reused.

The reviewer executed, from the Block 15 root:

```text
lean -j1 -M4096 -DwarningAsError=true MachineTheory/LegalQuotient.lean
lean -j1 -M4096 -DwarningAsError=true MachineTheory/LegalTrace.lean
lean -j1 -M4096 -DwarningAsError=true MachineTheory/LegalQuotientExamples.lean
lean -j1 -M4096 -DwarningAsError=true checks/CheckLegalQuotientAPI.lean
```

All four returned exit code zero and empty diagnostic output. No output-object path was requested. These are focused source/API compilations rather than cold cumulative builds.

A separate `lean -j1 -M4096 --stdin` invocation imported `MachineTheory.LegalTrace` and checked:

```lean
#check @Komorebi.MachineTheory.LegalQuotient.finite_source_legal_quotient
#check @Komorebi.MachineTheory.LegalQuotient.finite_legal_quotient_sequences
#print Komorebi.MachineTheory.LegalQuotient.representativeQuotient
#print axioms Komorebi.MachineTheory.LegalQuotient.finite_source_legal_quotient
#print axioms Komorebi.MachineTheory.LegalQuotient.Factors.execute_map
```

It returned exit code zero. The source endpoint retains `Fintype X`, `Fintype Action`, the supplied label, D, dependent F, surjective π, and all three raw fibre equations. The sequence endpoint retains finite states/actions and quantifies over every action list. The printed quotient definition uses actual representative labels and projected partial steps. The source endpoint's inspected axiom list is `propext`, `Classical.choice`, and `Quot.sound`; the inspected execution-map theorem lists only `propext`.

The API was read in full, including its direct raw-input theorem restatement and its finite-trace endpoint. Source review used `rg`, `sed`, `cat`, and `sha256sum`. Python's `hashlib` and `zipfile` performed the predecessor archive and 65-file preservation checks described above.

This reviewer did not run the complete negative-control manifest, cumulative transitive axiom audit, same-kernel replay, cold-build comparison, or final Block 15 archive check. Those require their own completed current-source receipts. No such release outcome is claimed here.

## Proofreading and final conclusion

The two new proof and assumption guides were reviewed in context. Their partial-operation, finite-word, uniqueness, empty-type and authority qualifications match the source and code. No unresolved objective mathematical, notation, or prose issue was found within that scope. The original manuscript and all production code were left unchanged by this reviewer.

The strongest safe conclusion is exactly the source theorem: a surjective quotient preserves labels, enabled actions and deterministic legal transitions precisely under the three fibre conditions, uniquely as partial operational data, and it preserves every finite legal action and label sequence. Final cumulative release verification remains a separate obligation at the time of this report.
