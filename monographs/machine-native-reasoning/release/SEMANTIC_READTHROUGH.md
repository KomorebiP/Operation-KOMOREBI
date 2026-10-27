# Core 3.2 independent proof and correspondence audit

**Normalized claim.** Let Ω be a finite world set, let c : Ω → I be a surjective cell map, and let t : Ω → Y be arbitrary. Admit exactly the events c⁻¹(J), for all J ⊆ I, and allow every candidate V ⊆ Ω, including ∅. Put D = image(ω ↦ (c(ω),t(ω))), r = |D|, O(V) = image(V → D), and Σ(V)(E) = t(V ∩ E). Then Σ(V) = Σ(W) iff O(V) = O(W); the attained signatures are equivalent to the full powerset of D and hence number 2^r; an r-bit deterministic representation with exact readout and evidence updates exists; every exact fixed-width b-bit representation under the inherited readout/update contract has r ≤ b.

**Primary verdict: proved as written.** This is an independent mathematical/proof-correspondence verdict for the exact revisions below, not a kernel-replay, release-gate, or source-book attribution certificate. No semantic gap was found. No production file was edited by this reviewer.

## Claim card and authoritative scope

- Source: `source/core_v0.2.tex`, label `r:occupancy`, lines 335–340, setup 303–305 and 328–333, inherited memory argument 314–325, global finite/nonempty convention at line 96. The prose source assumes finite nonempty Ω and nonempty codomains. The implementation additionally permits empty Ω; this is a valid extension, not a restriction of the source theorem.
- Restart contract: `release/NEXT_CORE32_SPEC.md`. Its recorded status is a specification/proof plan, not previously accepted Lean evidence. The proof modules' introductory word “Reviewed” was not treated as evidence.
- Quantifiers: every candidate subset, every admitted event, every pair of candidate subsets, every occupancy subset, every finite evidence list, and every natural bit width b. There is no reachability filter or nonempty-candidate restriction.
- Evidence is the full range of cell preimages, not an arbitrary subalgebra and not all world subsets. Singleton-cell events are present. Events splitting a cell are absent.
- Target Y is an arbitrary type. There is no `Fintype Y`, target surjectivity, `DecidableEq Y`, or identification of Y with the attained range in the stated API. D, rather than I × Y, is counted.
- Finite Ω suffices to make D and the set of attained signatures finite. The classification/equivalence arguments themselves do not require finiteness. Nonempty cells correspond exactly to surjectivity of c.
- Fixed-bit exactness is the inherited formal contract: encoding ρ : Set Ω → (Fin b → Bool), readout q, deterministic step δ, q(ρ(V)) = t(V), and δ(E,ρ(V)) = ρ(V ∩ E), for all V and E. No variable-length, average-length, acquisition-cost, or runtime statement is included. The count also gives the usual injective encoding bound for signatures themselves.
- Coefficients, grading, signs, completion, equivariance, and geometric objects do not apply.

## Dependency graph and leaf classification

1. `Behavior.Attained` and `record` define the actual image subtype; `attainedFintype` derives finite image types from finite domains. These are internal definitions/proofs.
2. `Correction.EvidenceAlgebra`, `signature`, `Memory`, and `filter` provide the inherited correction contract. `any_exact_memory_separates` directly proves that equal encoded states yield equal signatures using q and δ. These are internal proofs, read in raw source.
3. The new `algebra`, `Pair`, `pair`, and `occupancy` instantiate exactly the source objects. Singleton-cell interrogation plus transport of an occupied pair between candidates proves the classification iff.
4. Surjectivity of Ω → D proves `occupancy_realize`. Classification and realization prove `fromOccupancy_bijective`, hence the actual `memoryEquiv`.
5. Finite powerset cardinality and that equivalence yield 2^r. These use elementary mathlib finite-cardinality lemmas; the mathematical counting argument is independently checked here.
6. `bitsEquiv` is the characteristic-function equivalence after a finite indexing D ≃ Fin r. Occupancy projection and cell masking yield exact read/update and finite continuation.
7. Equal b-bit encodings of the realizing candidates imply equal signatures by inherited separation, then equal occupancy subsets. Thus P(D) injects into b-bit vectors; 2^r ≤ 2^b implies r ≤ b.

No dependency points from an inherited lemma back into the new claim. The count is derived after, and from, the equivalence; it is not used to assert the equivalence. Neither the finite fixtures nor any author/reviewer verdict is a load-bearing leaf. No external substantive theorem is imported as a substitute for the displayed elementary arguments. The source's [GA] attribution is outside this focused audit and is not needed for validity of the supplied proof.

## Obligation and code correspondence matrix

Line numbers below refer to the pinned snapshot.

| Obligation | Status | Exact code/evidence |
|---|---|---|
| Exact event family with univ and intersections | passed | `PartitionOccupancy.lean:18–30`, `algebra`, `event`, `event_membership_iff`; witnesses univ and J ∩ K |
| Source nonempty partition cells | passed | `nonempty_cells_iff_surjective`, lines 212–220; source endpoint in `OccupancyBinary.lean:118–131` includes surjective c |
| D consists of attained pairs, not the ambient product | passed | `Pair` and `pair`, lines 33–42; inherited `Behavior.lean:18–22` |
| Occupancy records existence, not world multiplicity | passed | `occupancy`, `mem_occupancy_iff`, lines 45–57 |
| Signature ⇒ occupancy | passed | `mem_occupancy_iff_single_cell`, lines 60–69; forward branch `signature_eq_iff_occupancy_eq`, lines 72–79 |
| Occupancy ⇒ signature for every admitted event | passed | backward branch, lines 80–107, extracts J from the actual event's range witness |
| Every occupancy subset is realized | passed | `realize`, `occupancy_realize`, `occupancy_surjective`, lines 110–119 |
| Actual two-sided equivalence, not two counts | passed | `fromOccupancy_bijective`, `memoryEquiv`, lines 121–157; compatibility on remembered candidates is proved |
| Precisely 2^r attained signatures | passed | `card_memory`, lines 159–162; finite image and powerset cardinality |
| Actual r-bit state, encoder, readout, update | passed | `OccupancyBinary.lean:18–68`; `bitsEquiv`, `binaryMemoryEquiv`, `encode`, `readBits`, `updateBits`, exactness and encoder surjectivity |
| Every finite evidence sequence | passed | `bits_finite_continuation`, `bits_readout_continuation`, lines 70–84; induction includes empty list |
| Every exact fixed-width b-bit representation needs r ≤ b | passed | `exact_bits_occupancy_injective`, `fixed_bits_necessary`, lines 86–114; inherited `Correction.lean:75–83` |
| Raw source endpoint | passed | `partition_correction_memory`, `OccupancyBinary.lean:118–131`; no target finiteness or surjectivity added |
| Eight worlds, four attained pairs, sixteen signatures | passed | `OccupancyExamples.lean:14–54`; actual source variables (b,s,n), cell (b,s), target b |
| Empty, mixed-target, shared-target, and unused-target boundaries | passed | `OccupancyExamples.lean:93–146,195–225`; independent finite checks below |
| Contradictory filter and exact binary contradiction readout | passed | `OccupancyExamples.lean:96–107`, `contradictory_filter`, `contradictory_binary_readout`; direct definition expansion and inherited exactness equations |
| Added splitting event / missing singleton-cell events | passed | `OccupancyExamples.lean:148–193`; direct counterexamples below |
| Lean elaboration, kernel replay, transitive axioms, release status | out of scope | Separate gate owner; this verdict must not be substituted for those checks |
| External source attribution to [GA] | out of scope | No attribution claim made by this audit |

## Decisive independent reconstruction

Fix an attained pair d = (i,y). Directly from the definitions,

    d ∈ O(V)  iff  ∃ω∈V, c(ω)=i and t(ω)=y
               iff  y ∈ t(V ∩ c⁻¹({i})).

The right side is an admitted signature coordinate because the evidence family contains every cell preimage. Therefore equal signatures force the same truth value for every attained pair. Conversely, for any admitted E choose J with E = c⁻¹(J). Then

    y ∈ Σ(V)(E)  iff  ∃d∈O(V), d.cell∈J and d.target=y.

For the forward implication, use the pair of the witnessing world. For the reverse implication, use a world witnessing d ∈ O(V). This formula proves equality of the entire Y-valued image for equal occupancies, including y outside the attained target range, where both sides are false. It does not assume t onto and does not collapse different cells sharing y. The candidate proof performs precisely this witness transport.

Let p : Ω → D be the pair map. It is onto by the definition of D. For S ⊆ D, use V_S = p⁻¹(S). Then p(V_S)=S. This is the full-fibre preimage witness, an explicit alternative to the prose's one-representative-per-pair witness. It neither adds a pair outside S nor omits a pair in S. `fromOccupancy` maps S to the signature of V_S; classification proves its injectivity, and any attained signature represented by V equals that of V_(O(V)), proving surjectivity. `memoryEquiv` is formed from this proved bijection and has both inverse laws through `Equiv`; its value on every remembered candidate is O(V).

Readout is projection of S onto its target coordinates. Filtering by c⁻¹(J) replaces S with S ∩ {(i,y): i∈J}. `eventCells` chooses a cell-subset representative of an actual admitted event; its preimage equality is proved. Even without surjectivity of c, different representatives agree at every attained pair's cell because each such cell has a world witness. Consequently this choice introduces no dependence on empty named cells. For the source endpoint c is onto anyway.

For the lower bound, suppose ρ(V_S)=ρ(V_T). Applying deterministic step for a single-cell event and then q gives equal filtered target sets by the exactness equations. The singleton-cell formula gives S=T. Thus S ↦ ρ(V_S) is injective on the whole powerset. A b-bit vector has 2^b states, so 2^r ≤ 2^b and r ≤ b. This is the actual direction in the code, with inherited signature separation as its intermediate lemma. No pigeonhole claim is used to prove its own hypothesis.

## Edge cases and finite checks

The source excludes empty Ω, but the implementation's extension is consistent: D=∅, the only candidate is ∅, the attained signature type has one element, and zero bits suffice. The empty candidate inside a nonempty source world set is also retained: its occupancy, every signature coordinate, and its readout are empty, and every update keeps it empty. Empty evidence can send any candidate to this contradiction state.

For one nonempty cell and a constant target, r=1, with exactly the empty/nonempty occupancy states. Two distinct singleton candidates have the same old occupancy. Admitting one singleton as new evidence distinguishes them, so the old occupancy is insufficient after evidence splits a cell. With two singleton cells and one constant target, r=2; removing the singleton-cell events and keeping only ∅ and Ω merges the two singleton candidates, reducing the signatures from four to two. This confirms both uses of “exactly” in the evidence premise.

For Ω={0,1}², c the first coordinate and t the second, each cell contains both target values and each target occurs in both cells: D has four pairs and all sixteen occupancy records occur. An unoccupied value 2 of a Nat target contributes no pair; universal Y remains unrestricted in the Lean theorem. For the source sensor Ω={0,1}³, c=(b,s), t=b, there are four pairs and sixteen signatures. The source candidates V={(0,0,0),(1,1,0)} and W={(0,1,0),(1,0,0)} both currently yield {0,1}; filtering by s=0 yields {0} and {1}. Three bits have only eight states and cannot encode all sixteen occupancies.

The independent supplemental script `independent_edge_checks.py` builds worlds, cell maps, events, signatures, occupancies, and full-fibre realizations directly as Python finite sets. It imports no project code and uses no Lean output. All candidate pairs, all admitted events, and all occupancy subsets are checked within each of seven explicitly listed fixtures. The largest is exactly the eight-world sensor: 256 candidates, 16 events, and 65,536 candidate-pair signature comparisons. Other world sizes are 0,1,2,3,2,4. The split-event, removed-event, source sensor collision, unused-target, and 16-versus-8 bit-cardinality checks also pass. These are finite sanity evidence only; no exhaustive claim is made across all partitions, target maps, arbitrary codomains, or encoders. They do not establish the universal theorem.

Command executed successfully (exit 0):

    python /workspace/scratch/6a8ff46cf015/mnr_coordination/audit/independent_edge_checks.py

Results: `independent_edge_checks.json`. Script SHA-256: `83687586a6cffeea8f96efea6a615f0c2cea97cdf8d06eedb0101b54ff103717`.

## Remaining gap, safe statement, and next check

No remaining mathematical or source-correspondence gap was found for Core 3.2 under the exact claim card. The strongest safe statement from this audit is the normalized theorem and its source correspondence for these raw proof revisions. It is not yet a claim that all separate release acceptance conditions have passed. The cheapest next checks are completion of the designated Lean/kernel/axiom/release gates and a final hash comparison against the pins below. If any audited source/proof/dependency changes, the affected raw argument must be reread; passing a later build does not refresh this semantic review automatically.

## Review provenance and exact revisions

Independent isolated reviewer `/root/mnr_audit`, applying `mathbox:proof-audit` and its general-logic/typing and computation-coverage obligations. The reviewer received the target and raw artifacts, not an author verdict or suspected gap, and reconstructed the critical iff before reporting findings. The author's “Reviewed” comment and later coordination message were not treated as proof evidence. Review date: 2026-10-25. This is model-based independent review, not independent human peer review.

The initially read `OccupancyBinary.lean` hash was `98b6fb74c8003bb70785a3b30e2444c7f4fe914700c9664612c1dd3de9de9eaf`. During review it changed to the pin below (an additional mathlib import, simp proof adjustments, and omission of the unused Fintype hypothesis on the injection lemma). `OccupancyExamples.lean` first changed from `e504fbb7e4b78dffe6ac435d798610db4a539c1cf00a11bdf4dc5a98e52502ea` to `020a5bfd53a867dabf749ac81923c9f00ac7b46934912e57ebb2c4b845115209` through elaboration-oriented `change`, `simp`, `decide`, and local-instance adjustments. Both entire revised files were reread. The final examples revision below then added exactly `contradictory_filter` and `contradictory_binary_readout`; a targeted diff review confirms no other changes. These revisions are covered by this verdict. Initial and final source contracts are semantically the same. Copies of every final pinned artifact are preserved under `audit/snapshot/`, with the preceding example snapshot also retained as `OccupancyExamples.020a5bfd.lean`.

The final contradiction endpoints were independently rederived: `event c ∅` has world set c⁻¹(∅)=∅, so its filter sends every V to ∅. `encode_update` followed by `encode_read` identifies the updated binary readout with t(V∩∅)=t(∅)=∅. All quantifiers remain unrestricted except the finite-world hypothesis already needed by the binary representation. No target nonemptiness, target-surjectivity, or choice of an arbitrary replacement target is introduced. The primary verdict is unchanged. Main-module hashes were rechecked unchanged during this targeted rereview; this supplements semantic review and does not replace the separate final gates.

| Artifact, relative to project root | SHA-256 audited |
|---|---|
| Base source ZIP, supplied provenance identifier | `206a735d18d4d96f8dfd32f80622f905f214233678f941dc0968c8205435ad45` |
| `source/core_v0.2.tex` | `a15f192322357893c2bb9b2427aac2a02b0753e558b42c0460a6288006ddbe6b` |
| `release/NEXT_CORE32_SPEC.md` | `3c71ccb23cfbadfcbe87025421e6bd45156c6af09b7a12e770a2e272b00c21fc` |
| `MachineTheory/Behavior.lean` | `7feeb686710bccb3b81a330dcb0abe9e55cbbcf2626ac647c457372b75b24cd8` |
| `MachineTheory/Correction.lean` | `7085f9f708cd33d2dcc025e6eaed93be4f451656bb445faeb02c49160cb47a2e` |
| `MachineTheory/PartitionOccupancy.lean` | `ed6e2a088abf68b0fb53da4ea7e6f400e026b32e10408123a32295295accb88b` |
| `MachineTheory/OccupancyBinary.lean` | `8af6469782ebe0344428f6fa88e34043502e57516933811ddf256054b4f69105` |
| `MachineTheory/OccupancyExamples.lean` | `18f2a6e59fc08ae2421d3bc330ac670e2cd9f2b5b0cd3c9c39092e387f5729ab` |

The base ZIP identifier was supplied by the parent; this reviewer did not independently reauthenticate that ZIP or inherited release pins. The individual files above were independently hashed and inspected. No Lean build, replay, or gate log was used to infer semantic correspondence.
