# Residual depth, support, and a conditional compactness bridge

## 1. The corrected logical ordering

For fixed data S, KRR0 asks every global failure to have an admissible degree-zero witness. KRR asks for a witness at any natural-number degree. Consequently:

    KRR0(S) -> KRRUpTo(S, 1) -> KRRUpTo(S, 2) -> KRR(S).

Increasing the permitted degree makes this assertion weaker. It does not by itself increase consistency strength. The same qualification applies to cardinal support: increasing the permitted support size makes it easier to find a witness for a fixed system.

The predecessor's Flattenable property requires each higher-degree witness to yield a degree-zero witness in the same system. It is not a theorem excluding translations into other structures, other languages, or other sets of local pieces.

In fact, degreePacked(S) uses pairs (q, J) as pieces, keeps the underlying exactness assertion, and declares its degree-zero obstruction to be the old degree-q obstruction. Lean proves:

    KRR0(degreePacked(S)) <-> KRR(S).

This is only syntactic reindexing. It removes no mathematical information and makes no assertion about effective computability, definability, or actual support size. A meaningful non-flattening problem must prohibit trivial reindexing by specifying the allowed translations and the semantic information they must preserve.

## 2. Soundness is separate from reflection

The original interface defines an obstruction predicate freely. KRR expresses witness completeness but says nothing by itself about false positive witnesses.

We define Sound(S) to mean:

    Small(J) and Obstruct(q, J) imply not Exact(S).

With Sound and KRR, Lean proves:

    Exact(S) <-> not HasResidualWitness(S).

Soundness alone does not imply KRR. A simple formally checked counterexample records this logical boundary. A more substantive counterexample appears below.

## 3. An explicit tower over the ordinary integers

Consider the inverse tower with group Z at every stage and bonding map multiplication by 3. On the product P = Z^N define the additive homomorphism:

    delta(a)(n) = a(n) - 3 a(n+1).

Let b be the constant sequence 1. We study the lifting equation delta(a) = b.

Every finite prefix is soluble. Set the terminal value a(N)=0 and work backwards. The explicit lift is:

    a(n) = 1 + 3 + ... + 3^(N-n-1), for n < N.

The code uses a recursive geometric sum, so no integer division or rounding is involved. Every finite set of equation indices is contained in a finite prefix. Lean proves solvability for arbitrary finite sets as well as prefixes.

A global lift would satisfy, for every n:

    2 a(0) + 1 = 3^n (2 a(n) + 1).

Thus every power of 3 divides the fixed integer 2 a(0)+1. An integer with this divisibility property is zero. Since 2 a(0)+1 cannot be zero for an integer a(0), a global lift does not exist.

This is not a counterexample to first-order compactness. First-order satisfiability permits a model to vary. Our lifting problem requires values in the fixed, standard group Z. Allowing a larger model changes the problem.

## 4. A genuine quotient obstruction

Define the additive quotient:

    C = P / range(delta).

The class [b] is zero exactly when b has a lift. Lean constructs this quotient and proves [b] != 0.

For a finite prefix, the actual operator is:

    delta_N : Z^(N+1) -> Z^N.

Backward substitution works for every finite right-hand side, so delta_N is surjective and its entire cokernel vanishes. The restrictions of variables and output coordinates commute with delta and delta_N. They therefore induce well-defined homomorphisms on cokernels. Lean proves:

    [b] != 0, but restriction_N([b]) = 0 for every N.

This is not an ad hoc predicate called an obstruction. It is a specified nonzero element in an explicitly constructed additive quotient with formally checked restriction maps.

For a countable inverse system of abelian groups, the standard product-difference complex computes the derived inverse limit. Its degree-one cohomology is this cokernel, and degrees above one vanish. The external reference is the Stacks Project, Lemma 15.88.1, tag 07KV:

    https://stacks.math.columbia.edu/tag/07KV

The present Lean files establish the explicit cokernel mathematics, not an isomorphism to Mathlib's implementation of R^1 lim. That identification remains a separate formal obligation. No claim of novelty is made for this classical construction.

## 5. Why finite depth does not guarantee finite support

The finite-prefix test system has Exact equal to global lifting. Its degree-zero tests ask whether a finite prefix lacks a lift, and its degree-one tests ask whether the corresponding finite cokernel class is nonzero. Higher degrees have no terms in this explicit two-term model.

Lean proves that no finite prefix detects an obstruction, while Exact fails. Therefore this explicit, sound finite-prefix residual system does not satisfy KRR.

The nonexistence argument itself is a finite proof about the infinite tower. Finite proof length and finite support of a restricted diagram are different notions. The counterexample excludes detection by the specified finite-prefix restrictions, not the existence of a finite mathematical certificate.

This refutes the suggestion that merely allowing a first derived layer automatically makes finite support sufficient. It does not refute every possible interpretation of the earlier underspecified BDO schema. Other admissible diagrams or other kinds of certificates would be different principles and must be specified separately.

In a second test system, local pieces are either a finite prefix or the whole countable tower. Assign the whole tower support size aleph0 and let its degree-one test inspect [b]. Lean proves the exact equivalence:

    supportedSystem.KRRAt(kappa) <-> aleph0 < kappa.

This is a classification of one declared test system, not a characterization of a large cardinal. It separates the amount of support required from the homological degree at which the obstruction lives.

## 6. Uniform arithmetic classification

For a natural number m >= 2, define delta_m(a)(n) = a(n) - m a(n+1). For any integer c, Lean proves:

    (exists a : N -> Z, delta_m(a) = constant(c)) <-> (m-1) divides c.

The necessary direction uses the identity:

    (m-1)a(0) + c = m^n ((m-1)a(n) + c).

Its left side is forced to vanish. The sufficient direction is the explicit constant lift a(n)=-t when c=(m-1)t.

Equivalently, the class of constant(c) in the explicit product cokernel vanishes exactly on the ideal (m-1)Z. Formal controls include m=2,c=1 (vanishes), m=3,c=1 (nonzero), and m=3,c=2 (vanishes). The theorem is uniform in all m>=2 and all integers c, not inferred from those controls.

## 7. A forward theorem with the existence assumption exposed

Let I index constraints, V index variables, and A be the fixed set of allowed values. Each constraint i has a specified scope scope(i) contained in V and a predicate on assignments V -> A. The locality hypothesis says that changing an assignment outside its scope cannot affect satisfaction.

Assume:

    |A| < kappa;
    |scope(i)| < kappa for each i;
    every subset J of I of size < kappa has an assignment satisfying its constraints;
    there exists a fine kappa-complete ultrafilter U on P_kappa(I).

Fineness means that the pieces containing a particular constraint form a U-large set. Kappa-completeness means closure under intersections of fewer than kappa filter-large sets.

Lean proves that the whole constraint system has an assignment in the same fixed value set A.

Proof outline: choose a satisfying assignment for each small piece. At each variable, kappa-completeness and the bound on |A| force one value to occur on a U-large set. These choices define a global assignment. For a given constraint, intersect the fewer-than-kappa agreement sets for its scope and the fine set of pieces containing that constraint. A piece in this intersection transfers local satisfaction to the global assignment by locality.

The contrapositive gives a genuinely small unsatisfiable subsystem. The development also encodes this conclusion as KRR0At for the concrete constraint class.

HasFineCompleteUltrafilter is defined as a proposition. It is not declared as an axiom or proved universally. The theorem therefore isolates, rather than conceals, the foundational existence input.

The implementation uses Mathlib's CardinalInterFilter and Ultrafilter definitions. Documentation:

    https://leanprover-community.github.io/mathlib4_docs/Mathlib/Order/Filter/CardinalInter.html
    https://leanprover-community.github.io/mathlib4_docs/Mathlib/Order/Filter/Ultrafilter/Defs.html

## 8. What a genuine ZFC-extension claim still requires

The admissible system class, formula complexity, support notion, and permitted translations must be fixed independently of the desired reflection conclusion. Any claimed large-cardinal comparison requires both an accurately stated external principle and actual implication proofs. A statement about arbitrary Lean types is not automatically an internal first-order theorem about models of ZFC.

This block supplies a refuted finite-support candidate, a uniform algebraic classification, and a conditional compactness bridge. It does not supply a new set-theoretic axiom, an independence result, or a relative-consistency theorem.
