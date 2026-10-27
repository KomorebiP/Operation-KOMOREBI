# Block 09: internal cone filters and the arithmetic boundary

## Contract

Continue v0.8.0 without modifying the encoded ZFC axioms, the regular uncountable guard, the original Theta or predecessor mathematical sources. Construct the missing internal cone filter and locate every support-size obligation. Only compiler-checked theorems count as formal completion.

The attempted full arbitrary-model forward implication is not yet closed. The delivered result is an exact all-model reduction plus complete concrete ZFSet discharge.

## Definitions

All variables below denote internal sets in an arbitrary membership structure M. Small(K,S) uses an internally existing injection graph from S into a member of K.

U(K), or SmallUnionClosed(K), asserts that the union of a small internal family of small internal sets is small.

P(K), or SmallProductClosed(K), asserts that the internally represented product of two small internal sets is small.

For P_K(I), the internal set of small subsets of I, define

    Cone(B) = {J in P_K(I) : B is a subset of J}.

The cone filter consists of internal subsets of P_K(I) containing Cone(B) for some B in P_K(I). Membership in that filter is given by an explicit first-order condition, so Separation on the internal powerset constructs the filter as a set.

## Cone-filter completeness

Each cone contains its own generating support, proving properness. Singletons prove fineness. To intersect a small internal family A of filter members, choose a support B_s for each s in A using the internal selection machinery. A Replacement image creates the family of selected supports. An internal surjection from A proves that this image is small. U(K) makes their union B small. Cone(B) is contained in every member of A, so their carrier-relative intersection belongs to the cone filter.

This constructs the input for Extension(K), which returns the required fine complete ultrafilter. No external family is passed to internal completeness.

## Why the support hypothesis is not merely convenient

Assume the fine principle. For a small family B of small sets, take a fine complete ultrafilter on the small subsets of its union R. Each small member b has a large cone: intersect its small internal family of point cones. Intersect the small internal family of those large cones for all b in B. Properness supplies a small J containing every b and therefore R. Since subsets of small internal sets are small, R is small.

Thus Fine(K) implies U(K). Combined with the construction, Extension(K) and an inductive member give Fine(K) iff U(K).

## Reduction from unions to products

Under the original Guard(K), take a small family B whose members are small. Internally select an ordinal bound a_s in K and an injection s -> a_s for each member. The image of B under the bound selector is a small subset of K. SmallBounded supplies one bound a in K for the entire family.

Using only internally constructed selectors and relation graphs, embed the union into B times a: each element selects a containing member s, then is mapped to (s, its value under the selected injection for s). The graph is internally existing and injectivity is proved. P(K) therefore makes the union small.

Conversely, express X times Y as the union of the slices {x} times Y. The family of slices is a small image of X, and every slice embeds into Y. U(K) therefore gives P(K).

The checked equivalences are

    Guard(K) -> [U(K) iff P(K)]
    Guard(K) and Extension(K) -> [Fine(K) iff P(K)].

## Closed sentences and concrete discharge

The predicates U and P are compiled to membership-only formulas, with exact interpretation lemmas in every structure. Their equivalence and the guarded extension-dependent cone reduction are actual closed sentences proved in every model of zfcTheory.

The remaining arithmetic sentence is

    forall K, Guard(K) -> P(K).

For concrete ZFSet it is proved. Internal product codes are identified exactly with Kuratowski products, their cardinality is bounded by the product of the small carriers, and Cardinal.mul_lt_of_lt supplies the strict bound at an infinite cardinal. This discharges the forward implication for concrete ZFSet.

For arbitrary models, the internal version of this cardinal-arithmetic proof is still missing. It is not a new large-cardinal requirement. The definitions of ZFC, KZFC, Guard and Theta have not been strengthened to bypass the gap.

## Formalization inventory

Seven new modules add 61 named theorem declarations. Together with 378 preserved declarations, there are 439. Names and locations are listed in THEOREM_INDEX.md. These counts include technical and interpretation lemmas.

The exact verification outcome is stored in verification/RESULTS.json. The reproduction process performs a clean project rebuild, separate warnings-as-errors checks, a full axiom audit, unchanged-source and predecessor checks, and negative controls. Runtime and dependency caches are not distributed or rebuilt as part of the source verification.
