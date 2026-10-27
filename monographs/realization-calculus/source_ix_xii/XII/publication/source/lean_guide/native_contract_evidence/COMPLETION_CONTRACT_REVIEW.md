# Paper XII: direct review of Claims 3.1 and 3.3

## Scope of this review

The v0.17.0 archive contains the complete construction for both claims. This continuation
replays those existing sources rather than attributing them to a new proof discovery.
The intervening 47/49 response was not backed by a failed proof: it was a conflicting
status report based on an older checkpoint. Current status is determined by the fresh
compiler and axiom records, not by either conversational assertion.

The production sources are unchanged. `checks/ManuscriptContractReplay.lean` adds three
separate audit declarations. They are excluded from the 49 manuscript claims and from
the production theorem census. This is a self-review plus kernel replay, not an external
referee report or an independently implemented Lean kernel.

## Claim 3.1 — completed tensor quotient

**Objects.** `FiniteTensor.Raw` is Mathlib's finite `PiTensorProduct`, not a formal symbol.
`CompletedTensor` is its actual separated uniform completion for the ideal-adic topology.
The ideal of definition includes the extended base ideal and all factor ideals. This
retains the base-adic topology when the family is empty.

**Conditions.** `closedConditions_eq` identifies the quotient ideal with the closure of
the sum of the actual images of the supplied factor condition ideals.

**Equivalence.** `completed_tensor_quotient` constructs a coefficient-algebra equivalence
from the completed tensor of the factor quotients to the quotient of the completed tensor.
`completed_tensor_quotient_continuous` checks both directions of continuity, and
`completed_tensor_quotient_factor` checks every canonical factor map.

**Topology.** `quotient_isAdic` proves that the quotient topology is the image-ideal adic
topology. `CompletionQuotient.equiv` constructs both inverse maps. Completeness of the
closed quotient follows from the countably based complete additive-group theorem in
Mathlib. It is not assumed as an input.

**Local manuscript setting.** The Noetherian assumptions imply finite generation of the
ideal of definition. `AdicCompletionComparison` relates the uniform completion to the
actual inverse-limit adic completion; `FiniteTensorLocality` identifies the common residue
field, locality, and the maximal-ideal topology. Proper/nonzero quotients are local. The
unit-ideal case is the zero ring, not a purported nonzero local ring.

**Direct contract test.** `claim31_contract` explicitly demands an algebra equivalence,
continuity in both directions, and all canonical-factor identities. The existing construction
satisfies all clauses. No completed-tensor equivalence is supplied as a hypothesis.

## Claim 3.3 — simultaneous local conditions after global base change

**Objects.** `CompletedLocalConditions.Conditions` is the completed tensor of the local
quotients. Its identification with the quotient of `LocalTensor` is constructed using
Claim 3.1. `GlobalRing` is the actual completion of the global ring tensor this condition
ring. It is not defined by declaring its desired point functor.

**Topology and identification.** `quotientIdentification_ideal` identifies the transported
ideal with the natural defining ideal. For a complete global ring B, the completed global
base change is bicontinuously isomorphic to B modulo the closure of the extended condition
ideal. Its map from B is surjective.

**Point statement.** A continuous local coefficient-algebra point into a complete Hausdorff
target has a unique continuous local coefficient-algebra factor exactly when every original
local restriction kills its condition ideal. A closed-kernel criterion gives the vanishing
condition; surjectivity gives locality. `algebra_factor_natural` gives naturality.

**No extra arithmetic premise.** In `claim33_contract`, finite-generation inputs and the
structural ideal bound are discharged from Noetherian factor rings, the common residue-field
data, and the local global structural map. They are not added assumptions replacing the
missing conclusion. Complete/Hausdorff point targets are retained as in the manuscript
category. Original arithmetic representability remains an explicit external input.

## Exact kernel check

`exact_closed_kernel` directly checks that the kernel of the canonical completed quotient
map is the closed extended ideal. This excludes a mere one-sided kernel containment from
being mistaken for the quotient comparison. It is a corollary of the checked equivalence,
not a new manuscript claim.

## Unchanged boundaries

The revised ledger and the original-wording ledger remain distinct. The eight inherited
amendments remain 6.12, 9.4, 9.5, 9.6, 10.5, 12.2, 12.4 and 12.6. The conditional arithmetic
inputs, including representability, residual automorphic occupancy, applicable patching
and classicality, attached Galois representations, Frobenius density, semisimplification
and the general Brauer–Nesbitt input, are not promoted.

## Reference alignment

The completed tensor convention agrees with completion of the tensor product with the
linear topology induced by its factors; see Stacks Project Definition 87.4.7, tag 0AMU.
For the finite adic family the ideal-of-definition description is the convention used
in the manuscript. The countably based quotient-completeness fact is provided by
`QuotientAddGroup.completeSpace_right` in the pinned Mathlib source.

These references explain the standard constructions. They do not substitute for the
compiler replay and do not establish a novelty claim for this project.
