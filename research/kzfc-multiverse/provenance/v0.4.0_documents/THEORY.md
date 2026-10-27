# Classification of the semantic residual compactness principle

## 1. The class is fixed before the principle is asserted

Fix an infinite cardinal kappa. A constraint system consists of a set I of constraints, a set V of variables, a value domain A, a scope sigma(i) contained in V for each i, and a predicate C_i on total assignments a: V -> A.

Assume |A| < kappa and |sigma(i)| < kappa. Locality means that assignments agreeing on sigma(i) either both satisfy C_i or both fail it. The formal interface needs only the implication from the first assignment to the second, universally quantified over the pair, so the reverse implication follows by exchanging them.

For J contained in I, let Sat(J) mean that some total assignment V -> A satisfies every constraint indexed by J. FixedDomainCompactness(kappa) asserts, for all such systems:

    [for every J subset I with |J| < kappa, Sat(J)] -> Sat(I).

The domain stays exactly A. The theorem does not pass to a larger elementary extension. There is no bound on the total number of constraints or variables apart from membership in the declared universe.

The residual encoding is independently specified:

    Exact = Sat(I)
    Piece = {J subset I : |J| < kappa}
    size(J) = |J|
    Obstruct(q,J) = [q=0 and not Sat(J)].

Restriction of a global assignment proves soundness without compactness. Contraposition proves FixedDomainKRR0(kappa) <-> FixedDomainCompactness(kappa). Since this particular encoding has no positive-degree obstructions, FixedDomainKRR(kappa) <-> FixedDomainKRR0(kappa).

This result does not silently replace the predecessor's derived tower by a logical theory. It classifies one declared semantic constraint class. The algebraic tower remains a separate test object.

## 2. An independently formulated existence property

CompleteFilterExtension(kappa) says that for every set X and every proper filter F on X closed under intersections of fewer than kappa sets, there exists a kappa-complete ultrafilter U extending F.

The implementation uses Mathlib.Filter, Mathlib.Ultrafilter, and CardinalInterFilter. Mathlib orders filters oppositely to inclusion of their collections of large sets. Accordingly `(U : Filter X) <= F` means that U extends F.

FineUltrafilterPrinciple(kappa) says that for every set I there is a kappa-complete ultrafilter on P_kappa(I), the set of subsets of I having cardinality below kappa, such that each cone `{J : i in J}` belongs to the ultrafilter.

These are definitions of propositions, not assumptions made globally. All uses of them in proof terms are explicit hypotheses or consequences of another explicitly given principle.

## 3. The substantive converse: a Boolean assignment constructs an ultrafilter

Suppose Boolean constraint compactness holds at kappa. Start with any proper kappa-complete filter F on X. Introduce one Boolean variable p_s for each subset s of X. Impose the following constraints:

    p_X = true
    p_(X \ s) <-> not p_s
    p_(s intersect t) <-> (p_s and p_t)
    p_(intersection S) <-> (for every s in S, p_s), whenever |S| < kappa
    p_s = true, whenever s belongs to F.

Each scope has cardinality below kappa. In particular, the intersection constraint uses the members of S and one additional variable for their intersection. Finite scope estimates require only that kappa is infinite.

Every small collection J of these constraints is satisfiable. Collect the fewer than kappa F-sets demanded by its last type of constraint. Their intersection belongs to F by kappa-completeness and is nonempty because F is proper. Choose x in it and set p_s true exactly when x belongs to s. Point evaluation satisfies all Boolean and intersection laws literally and all chosen F-membership requirements.

Compactness gives a global assignment p. Define

    U = {s subset X : p_s is true}.

The top and intersection laws make U a filter. The complement law makes it an ultrafilter. The small-intersection laws make it kappa-complete. The final requirements show that it extends F. All of these assertions concern actual constructed Mathlib objects and are checked in FilterExtension.lean.

The Boolean fragment follows from FixedDomainCompactness by taking the two-valued domain. The Lean proof uses ULift Prop to align universes, with its cardinality proved to be two in the standard ambient classical foundations. This use does not turn the truth values into a new set-theoretic assumption.

## 4. Recovering the fine ultrafilter from filter extension

Assume kappa is regular. For s in P_kappa(I), put

    Cone(s) = {J in P_kappa(I) : s subset J}.

A set D of small pieces is large in the cone filter exactly when some Cone(s) is contained in D. Each cone contains its own generating support s, so the filter is proper.

For fewer than kappa generating supports, regularity ensures that their union still has cardinality below kappa. The cone above that union lies inside the intersection of the corresponding large sets. Therefore the cone filter is kappa-complete.

Each single-coordinate cone belongs to this filter. Extending it to a kappa-complete ultrafilter gives a fine ultrafilter. This proves CompleteFilterExtension(kappa) -> FineUltrafilterPrinciple(kappa), with the role of regularity explicit.

## 5. The forward construction preserves the actual value domain

Given the fine complete ultrafilter, choose a satisfying assignment for each small set of constraints. For a fixed variable v, the possible values partition P_kappa(I) into fewer than kappa fibers. Kappa-completeness forces one of those fibers to be ultrafilter-large. Choose that value as a(v).

For constraint i, intersect the agreement sets for all variables in sigma(i), together with the fine set of pieces containing i. This is a nonempty ultrafilter-large intersection. A local solution on a piece in it agrees with a throughout sigma(i), so locality transfers satisfaction to a.

Thus the global assignment takes values in the same A. This is the predecessor's forward theorem, now supplied with an independently constructed fine ultrafilter.

## 6. Classification theorem

For each regular infinite kappa the Lean development proves:

    FixedDomainKRR(kappa)
      <-> FixedDomainKRR0(kappa)
      <-> FixedDomainCompactness(kappa)
      <-> BooleanCompactness(kappa)
      <-> CompleteFilterExtension(kappa)
      <-> FineUltrafilterPrinciple(kappa).

The independent filter and ultrafilter definitions are essential. This is not merely the contrapositive of a proposition relabeled twice. The central converse constructs an ultrafilter from a Boolean constraint model, and the forward implication constructs a global assignment from a fine ultrafilter.

For regular uncountable kappa, the all-sets reading of the last two principles is a standard strong-compactness characterization. The literature record authenticates that terminology. The formal theorems use explicit definitions rather than an assumed external theorem named StrongCompact.

## 7. What becomes of the proposed ZFC expansion

Define the candidate residual existence assertion as:

    There is a regular uncountable kappa satisfying FixedDomainKRR(kappa).

Independently define the corresponding existence assertion using CompleteFilterExtension. Lean proves these two existence propositions equivalent. Neither existence proposition is proved to hold or introduced as an axiom.

Under the set-theoretic all-sets reading, the proposed extension is therefore a residual presentation of the existence of a strongly compact cardinal. This block gives no evidence for a new consistency strength beyond that known principle. Its formal contribution is the checked semantic classification and its compatibility with the earlier residual interface.

The Lean equivalence is not yet a formal theorem of the first-order object theory ZFC. Translating the definitions, quantifiers, cardinal bounds and semantic constraints into that object language remains a separate task. Consequently no formal relative-consistency or independence theorem is claimed here.

## 8. Baseline and explicit successor-cardinal obstruction

At kappa = aleph0, every proper filter has an ultrafilter extension by the ordinary ambient choice-based theorem. Finite-intersection closure is automatic. The classification therefore proves finite-domain, finite-scope compactness and its residual formulation without a new existence principle.

For any infinite mu, the principle fails at kappa = mu-plus. Take a variable set V of size mu-plus and a value set A of size mu. For each pair of distinct variables, require different values. Each constraint has only two variables in its scope.

Any set of fewer than mu-plus constraints involves at most mu variables. Assign them distinct values in A, and extend the assignment arbitrarily outside that support. Thus every required small subsystem is satisfiable. A global solution would inject a set of size mu-plus into one of size mu, which is impossible. SuccessorObstruction.lean proves this uniformly for all infinite mu, then transfers it to FixedDomainKRR and CompleteFilterExtension.

For example, at aleph1 every countable subsystem of the distinct-value problem on aleph1 variables can be assigned values in N, but the whole problem cannot. This does not contradict the aleph0 baseline, whose allowed value domains must be finite.

## 9. Preserved counterexamples and interpretation corrections

The predecessor's integer-tower example remains byte-for-byte unchanged. Every finite subsystem of a(n) - 3 a(n+1) = 1 is soluble over Z, but the full tower is not. The explicit nonzero product-cokernel class restricts to zero in every finite-prefix cokernel. Its standard derived-limit interpretation was recorded earlier, but its identification with Mathlib right-derived limits remains unformalized.

Finite proof length and finite support of a restricted object are distinct. Allowing positive residual depth does not by itself repair finite-support detection. For a fixed system, allowing more depths or more supports weakens the witness assertion. A broad translation can also hide depth in the index of a piece.

The foundational strength found here already occurs at depth zero. It comes from the class of allowed systems, their scope and value-domain cardinalities, and the global assertion that every locally satisfiable system has a realization. It does not come from the number of degree labels.

A separate subtlety is that class-level compactness need not be monotone when kappa changes. Increasing kappa both enlarges permitted local pieces and changes the allowed domains and arities. The fixed-system support-monotonicity theorem must not be applied to this changing class without an additional argument.

## 10. Exact scope

All independent sets in each theorem are represented in one arbitrary universe Type u. The assertions hold uniformly in u but do not themselves give an object-language theory ranging over a literal set of all Lean universes. Completeness means intersections indexed by sets of cardinality strictly below kappa. Regularity is an explicit premise of the equivalence cycle. Full infinitary syntax L_(kappa,kappa), local lambda-indexed compactness levels, structural reflection and generic absoluteness are not formalized in this checkpoint.
