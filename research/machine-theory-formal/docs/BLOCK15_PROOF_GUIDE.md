# Block 15 proof guide: a quotient preserving legal operations

**Machine-Native Reasoning · Reviewed Core 0.2 · Companion 0.15.0 · Komorebi P.**

This block addresses Core **8.2**, `r:governance`, at `source/core_v0.2.tex:888–898`. The surrounding line 886 supplies finite states, a finite action alphabet, protected labels, enabled-action sets and deterministic successors defined for enabled actions. Admission brings the selected-source tally to **23/27** only when the completed current-source gates pass. All 60 preceding substantive Lean modules and the source book are preserved.

## Exact claim

Let π : X → Z be surjective. Quotient labels, enabled sets and legal successors exist exactly when any states x and y with π(x) = π(y) satisfy all three conditions:

1. Their protected labels agree.
2. Their enabled-action sets agree.
3. For every enabled action, the projected successor states agree.

The quotient data are unique on their actual legal domain. They preserve and reflect legality of arbitrary finite action words, project the successive states correctly, and preserve the whole protected-label sequence, including the initial label.

## Representing partial legal operations

The formal system has a protected label and an `Option`-valued deterministic successor. `some y` means that the action is enabled and its successor is y; `none` means that the action is disabled. The enabled set is therefore exactly the set of actions with a defined successor. This is a canonical representation of a partial function, not a choice of an arbitrary successor at disabled actions.

An explicit translation takes the source's separately supplied enabled set D(x) and successor F(x,a,h), where h proves that a is enabled. It returns `some (F x a h)` on the enabled domain and `none` elsewhere. The translation proves that the resulting enabled set equals D. Proof irrelevance prevents the successor from depending on which proof of membership was supplied.

The source-facing finite-state, finite-action endpoint retains the manuscript's scope. The representative construction itself works more generally, without a finiteness restriction. Surjectivity supplies a representative for each quotient state without requiring a global nonempty-state assumption. Empty state and quotient types remain admitted.

## Constructing and proving the quotient

Choose one representative x of each z. Define the quotient label and availability from x, and project each defined successor through π. The three fibre conditions make these definitions independent of the representative. In particular, a different representative cannot turn a disabled action into an enabled one. When an action is enabled, both projected successors agree.

Conversely, any factoring quotient makes equal fibres agree on labels and availability. Its legal-successor equation also forces equal projected successors. This proves necessity separately from the representative construction. Quotient existence is a conclusion, not an assumption hidden inside the compatibility premise.

For uniqueness, take any quotient state z and a preimage x. Every factoring quotient must give z the label and availability forced by x. Its enabled successor is likewise forced by the projected successor of x. The canonical `none` value fixes disabled cases without claiming that an arbitrary totalized disabled successor has mathematical significance.

## Finite executions and complete label sequences

Execution follows an action list from left to right. A successful execution records the initial state and every successive state. If an action is disabled at any step, execution returns `none`.

Induction on the entire action list proves that quotient execution equals projection of the original execution. The base case retains the initial state. At each step, availability agrees, so both executions either reject the action or proceed to related states. The induction hypothesis then applies to the remaining word. This is a theorem for arbitrary finite words, not a check up to a chosen length.

Mapping protected labels over the full state sequence gives the same label sequence on both sides. Successful execution exists on one side exactly when it exists on the other. The theorem therefore protects legal action availability and all intermediate labels, beyond merely agreeing on one sensor response or the final output.

## Exact boundary examples

Small finite systems isolate the three obligations. States can have the same protected output while differing in permission to perform a repair. Merging those states fails the availability condition even when an output-only summary looks adequate. Other examples isolate differing labels and incompatible projected successors. A valid quotient forgets irrelevant history while retaining the protected operational distinctions.

Surjectivity is also substantive: values at an unattained quotient state cannot generally be forced by factorization. Likewise, arbitrary total extensions can disagree at disabled actions while representing the same legal partial transition. These are limits of the uniqueness claim, not failures of the source theorem. Deliberately false variants are tested by explicit rejection contracts with required mathematical diagnostics.

## Files and verification

| File | Role |
|---|---|
| `MachineTheory/LegalQuotient.lean` | Partial-system representation, source translation, fibre criterion, construction and uniqueness. |
| `MachineTheory/LegalTrace.lean` | Arbitrary finite execution, legality and complete label-sequence preservation. |
| `MachineTheory/LegalQuotientExamples.lean` | Exact finite examples and counterexamples. |
| `checks/CheckLegalQuotientAPI.lean` | Source-facing interfaces and concrete endpoint checks. |
| `docs/ASSUMPTION_REVIEW_BLOCK15.md` | Mathematical scope and assumptions. |
| `evidence/CORE82_SOURCE_AND_CODE_AUDIT.md` | Separate source and raw-code review. |
| `evidence/RELEASE_RESULTS_BLOCK15.md` | Completed gate outcomes, counts and limitations. |

Two complete cumulative gates must compile the frozen local sources into empty object directories, check APIs and actual declarations, audit transitive axioms, replay substantive modules through the same Lean kernel, and satisfy every negative-control contract. The second run starts from a separately extracted source snapshot. Every production proof object must match byte for byte. The foundational allowlist remains `Classical.choice`, `Quot.sound` and `propext`.

The gates reuse pinned upstream objects. They do not rebuild Lean or Mathlib from source, supply a different proof kernel, or establish independent peer review. The source/code audit is a separate reasoning pass in the same model family. Development failures and recovery problems are retained in the review notes and evidence.

## Scope and continuation

The enabled set is part of the declared mathematical system. Preserving it does not establish moral authority, real-world legality, authentication or authorization outside that model. No institutional database, access-control deployment, empirical agent or communication protocol is implemented here.

The complete original Block 14 archive is retained under `evidence/history/block14`. Its 8,258 payload hashes were checked before extracting the current sources. This preserves the full historical evidence without duplicating every historical proof object in the current directory tree. The current sources and Block 15 evidence remain directly accessible.

Four selected results remain: Core 2.4, 2.5, 3.2 and 8.3. The next connected target is Core 8.3, safe continuation that retains an ending strategy. Selected-result counts do not measure relative proof difficulty or count discoveries.
