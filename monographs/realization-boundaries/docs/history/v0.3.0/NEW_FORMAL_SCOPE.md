# New formal scope — v0.3.0

## Actual tail-divisibility signature

`HasPrimeRoot x p` means that the original additive group contains a root y with p*y=x. `hasPrimeRoot_map` and `hasPrimeRoot_equiv` prove preservation and, for equivalences, reflection. `preimage_prime_root_iff` connects this intrinsic question to the single prime coordinate of an actual preimage element.

`tailExceptions r d` is the union of numerator primes, denominator primes and support(d). `tailExceptions_finite` requires r != 0. `normalForm_coordinate_ne_zero_iff` proves the exact support assertion outside this set. `selector_tail_signature` takes a genuinely nontorsion original-group element and produces a finite exceptional set. The positive suite checks zero-rational failure, numerator and denominator exceptions, and finite-support perturbations.

## Unmarked classification and finite-change transport

`pairedGroup_isomorphic_iff` states that a nonempty type of actual additive equivalences exists exactly when the set of differing selector indices is finite. `pairedGroup_eq_of_finite_disagreement` proves the stronger literal equality of subgroups inside the fixed product. `pairedEquivOfFiniteDisagreement` leaves the underlying product vector unchanged.

The transport between the genuinely twisted normal-form groups is

    (r,d) |-> (r,d+s_A(r)-s_B(r)).

The section difference is proved finite, the rational coordinate is retained, the realized ambient element is fixed, and `normalFormTransportEquiv` is an actual additive equivalence with this exact formula. It is not the identity between two ordinary split-product group structures.

## Marked classification

`pairedGroup_marked_isomorphic_iff` retains the required equality of marked elements as an explicit condition and concludes literal equality of the selector functions. `toggleBit` supplies a universal one-bit control: the subgroups remain equal but their distinguished points admit no marking-preserving isomorphism.

## Arbitrary homomorphisms and torsion

`finite_disagreement_of_nontorsion_image` is the key strengthening. If any element has nontorsion image under any additive homomorphism, then the selector bits agree outside a finite set. No continuity, coordinate formula, induced rational scalar, or diagonality assumption is used.

Contraposition proves that infinitely different selectors force the image into the actual finite-support subgroup D. `torsionFactor` constructs the unique D-valued factor. No embedding or surjection exists in this case. Conversely a finite change gives an isomorphism, so embeddings, surjections, and isomorphisms have the same existence criterion within this family.

Torsion image does not mean zero image or a finite image. The positive suite constructs a nonzero one-coordinate map between the constant-false and constant-true groups. A corresponding negative control rejects the zero-image overstatement.

## Canonical completion consequences

The constant selectors differ everywhere and their actual groups are not isomorphic. Their canonical completions remain continuously additively equivalent through the previously checked comparison with the ambient product. `no_completion_invariant_reconstruction` rules out any group-valued assignment that respects those completion isomorphisms while recovering every original group. It has no computability assumption.

`no_lift_of_commonCompletionEquiv` proves that the canonical coordinate comparison between completions cannot be extended from a homomorphism of original groups when the selectors differ infinitely. Its hypothesis is equality on the actual canonical eta images. This is an explicit nonfullness witness.

These results do not claim that a supplied homomorphism between paired groups can induce an isomorphism without itself being an isomorphism. The monograph's opposite, restricted reflection statement is a separate pending theorem.

## Remaining boundary

The full formula for all homomorphisms, the endomorphism ring and its units, seed ranks, root-fiber cardinalities, CRT cyclic identifications, oracle-presentation semantics, and grammar diagonalization remain separate tasks. The no-decoder result is currently packaged for canonical completion isomorphisms, not a new formal Pro-category decoder interface. No Python extraction equivalence, external peer review, or historical-priority certification is claimed.
