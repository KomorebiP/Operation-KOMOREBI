# Membership-language interpretation of residual compactness

## 1. The proposition already classified

For a cardinal kappa, `CompleteFilterExtension kappa` asserts that every proper kappa-complete filter on every type in the selected universe extends to a kappa-complete ultrafilter. Mathlib orders filters by reverse inclusion of their families of large sets. The extension inequality is therefore U <= F.

The unchanged predecessor proves, for regular kappa, equivalence with fixed-domain constraint compactness, Boolean constraint compactness, the fine complete-ultrafilter principle, and the residual schema for the specified constraint class. Value domains and constraint scopes have cardinality strictly less than kappa. The local support bound is also strictly less than kappa.

This release does not reclassify arbitrary residual hierarchies. It interprets this already specified and independently classified principle in actual set-theoretic syntax.

## 2. Exact coding, not restricted observation

For X : ZFSet, use the small carrier `Carrier X := Shrink X`. Its elements map injectively onto exactly the members of X. A subset of this carrier is encoded as the ZFSet range of its member map. The inverse operation decodes a set code by membership.

The checked identities are:

    decode X (encode X s) = s
    encode X (decode X S) = S                 [S subset X]

The same construction applies to families of subsets, with their bound in the powerset of X. Round trips hold in both directions. No subsets are discarded by this conversion. The equivalence between a family and the small carrier of its code proves equality of cardinalities, not merely a cardinal estimate.

Every Type u has a representative of the form Carrier X for some ZFSet.{u}: choose the set code of the initial ordinal of its cardinal. This gives the missing reverse implication from a proposition quantified over ZFSet carriers to the predecessor proposition quantified over all Type u. Filter maps along the carrier equivalence preserve the needed completeness and extension relation.

## 3. Intersections must be relative

For a family S of subsets of X define

    relInter(X,S) = {x in X | for every s in S, x in s}.

In particular, relInter(X,empty) = X. Encoding preserves this operation, including the empty case.

Mathlib's unbounded ZFSet.sInter(empty) is empty. Its convention is legitimate for that operation, but it is not the empty-family intersection in the powerset Boolean algebra of a fixed X. The theorem `absolute_intersection_complete_impossible` proves that imposing the unbounded operation in all small-family completeness clauses contradicts properness as soon as 0 < kappa. The empty family is already a counterexample.

## 4. Independently stated set filters

`IsSetFilter X F` asserts:

* F is a subset of the powerset of X;
* X belongs to F;
* F is upward closed among subsets of X;
* F is closed under binary intersections.

`IsProperSetFilter` additionally excludes the empty set. `IsSetUltrafilter` imposes the complement decision law: for each S subset X, S belongs to F exactly when X \ S does not. This is an independently stated set predicate, with checked conversions to and from Mathlib filters and ultrafilters.

For an external cardinal parameter kappa define completeness by

    for every family S subset F with card(S) < kappa,
      relInter(X,S) belongs to F.

The `codeFilter_complete_iff` theorem identifies this with `CardinalInterFilter`. The set inclusion between filter codes identifies exactly with the reversed Mathlib filter order.

These constructions give the two-way all-carrier theorem

    SetCompleteFilterExtension(kappa) <-> CompleteFilterExtension(kappa).

No existence of an ultrafilter with stronger completeness is assumed or derived without the corresponding hypothesis.

## 5. Replace external cardinal bounds by set-quantified smallness

The formula must not contain Lean's Cardinal type or a semantic smallness oracle. A function is instead represented by its set of Kuratowski ordered pairs. The implementation proves that the constructed graph satisfies Mathlib's `ZFSet.IsFunc` and that an injective set-coded graph is equivalent to a genuine carrier embedding.

Define

    SetEmbeds(S,a) := there exists an injective function graph from S to a;
    SetSmall(K,S) := there exists a in K such that SetEmbeds(S,a).

The cardinal parameter is represented by

    K = kappa.ord.toZFSet.

Lean proves, for every cardinal kappa and set S,

    SetSmall(kappa.ord.toZFSet,S) <-> S.card < kappa.

Thus the strict bound is encoded through smaller ordinals and actual injections. No cardinal predicate remains in the final formula's language.

Define the entirely set-quantified predicate

    Comp(K,X,F) := for every S subset F,
      SetSmall(K,S) implies relInter(X,S) in F.

Then define

    InternalExtension(K) := for every X,F,
      ProperFilter(X,F) and Comp(K,X,F) imply
      there exists U with Ultra(X,U), F subset U, and Comp(K,X,U).

The main predicate-level interpretation proves

    InternalExtension(kappa.ord.toZFSet) <-> CompleteFilterExtension(kappa).

## 6. The actual first-order formula

The language has no function symbols and exactly one binary relation symbol, membership. Equality is logical equality. The construction uses Mathlib's `FirstOrder.Language.Formula` syntax and a membership structure on ZFSet. A free variable of type Unit is the single parameter K.

The macros are all finite syntax constructors. They encode subsets, empty sets, relative difference, binary and relative family intersections, singleton and unordered pairs, Kuratowski ordered pairs, products, function graphs, injectivity, smallness, filter laws, complement decisions, and completeness. None of these is added as a new relation symbol.

The final formula is schematically

    Phi(K) := forall X forall F,
      [ProperFilter(X,F) and Comp(K,X,F)] ->
      exists U [Ultra(X,U) and F subset U and Comp(K,X,U)].

Every displayed abbreviation has an actual expansion to membership, equality, connectives and first-order quantifiers. Binder correctness uses Option-indexed free-variable extensions and proved semantic equivalences. This avoids variable capture rather than ignoring binder indices.

For every macro, its realization in the concrete ZFSet structure is proved equivalent to the intended set predicate. Composing these lemmas yields the main theorem:

    extensionFormula_iff_filterExtension:
      Realize_ZFSet(Phi, initialOrdinal(kappa))
        <-> CompleteFilterExtension(kappa).

For regular kappa:

    extensionFormula_iff_residual:
      Realize_ZFSet(Phi, initialOrdinal(kappa))
        <-> FixedDomainKRR(kappa).

The formula itself is fixed and independent of the cardinal. The cardinal enters only as its parameter assignment. K is constrained to an initial-ordinal code by the interpretation theorem, not by an unproved claim about all arbitrary parameter sets.

## 7. Sanity checks inherited all the way to syntax

The aleph0 theorem and the infinite-successor counterexample transfer through the semantic equivalence:

    ZFSet realizes Phi(initialOrdinal(aleph0));
    not ZFSet realizes Phi(initialOrdinal(mu-plus))     [aleph0 <= mu].

These are Lean proofs for all indicated cardinals, not finite tests. The successor result concerns the changing admissible constraint class as kappa changes. It is not contradicted by the fixed-system monotonicity lemmas of earlier releases.

## 8. What is still missing for an internal ZFC result

An actual formula plus semantic adequacy in one concrete model is not a syntactic derivation from a first-order theory. The current theorem uses Lean's ambient type theory and the concrete ZFSet API. This release does not prove that every model of ZFC has the required internally interpreted equivalence. Internal cardinality, internal functions, internal completeness and quantifier domains must not be replaced silently by their external versions when working in arbitrary models.

The precise remaining tasks are:

1. Encode and interpret the regular-uncountable initial-cardinal guard, so the parameter formula can be assembled into the intended closed existence sentence. Merely existentially closing Phi would include the already true aleph0 case and would be the wrong axiom.
2. State the residual/constraint side in the same object language, and establish its semantics without adding new predicates by assumption.
3. Build an internal proof or a suitable arbitrary-model interpretation of the equivalence using explicit ZFC axioms and satisfaction infrastructure.
4. Only after that, prove any desired model transformation or relative-consistency consequence with its metatheory explicitly identified.

No step above is claimed complete in this release. In particular, the existing ambient equivalence of two uncountable existence assertions is not a proof that either assertion holds.

## 9. Novelty and scope

The predecessor identifies a known global strong-compactness formulation, with exact restrictions stated in LITERATURE.md. This release provides a checked representation and interpretation of that formulation. No new set-theoretic consistency strength, mathematical priority, or first-formalization claim is made. Higher derived residuals and the explicit integer cokernel are preserved but are not resolved by the new membership formula.
