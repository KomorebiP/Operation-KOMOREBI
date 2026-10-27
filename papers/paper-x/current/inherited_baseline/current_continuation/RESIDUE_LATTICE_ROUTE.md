# Actual additive residue counting

The starting point is the predecessor's discrepancy theorem for each fixed full lattice, uniform over all affine translations. We use its actual count and actual covolume.

For full lattices L0 contained in L, the residue object is the genuine quotient L/(L0 restricted to L). Its cardinal is the relative subgroup index by definition. Mathlib's proved covolume/index identity makes this cardinal the covolume ratio and proves it is finite. An explicit equivalence sends the fiber of the class of a to the affine coset a+L0. Thus one constant works for every residue class simultaneously, with leading density volume(D)/(covol(L) times the quotient cardinal).

For nonzero integral ideals M contained in J in any number field, both lattices and the norm-cone boundary atlas are supplied internally. No geometric counting hypothesis remains in the ideal-fiber theorem. An explicit equivalence between the actual algebraic integers of J and its Euclidean lattice identifies residue equality exactly with x-a in M. The resulting cardinal is a count of actual integers satisfying that congruence and the actual cone truncation.

The weighted counting definitions are also tied to actual points: bounded regions contain finitely many lattice points, and the sum of residue weights multiplied by fiber cardinalities equals the finite sum of those weights over the actual points. General weights have a leading coefficient given by their finite residue sum; zero mean is a necessary explicit hypothesis for the cancellation wrapper. Nontriviality on an arbitrary norm-character codomain is not substituted for zero mean on the actual residue image.

## Verification history

ResidueLatticeFibers passed strict compilation on attempt 2. Attempt 1 exposed unused-section warnings, a coset beta-reduction rewrite issue, and an omitted explicit quotient-submodule argument to mk_surjective. These were corrected without changing the mathematical hypotheses.

ResidueLatticeIdeal passed on attempt 1. ResidueLatticeIdealPoints passed on attempt 2 after supplying the explicit number-field parameter to mixedEmbedding_injective.

ResidueLatticePointSums passed on attempt 2. Attempt 1 exposed unused proof-variable warnings, the preferred proof-local instance declaration style, and an untyped Subtype.val congruence that selected the wrong subtype. The final explicit map proves the actual finite-set injection and finite fiber decomposition.

ResidueLatticeWeights passed strict compilation on attempt 9. Earlier expanded concrete proof applications reached deterministic elaboration heartbeat limits. The successful version proves a common weighted-estimate predicate over an abstract finite index type and then instantiates it with the actual quotient fibers. An independent 10,000-heartbeat statement-only probe passed, showing that the prior timeouts were in proof-term unification or reduction, not the mathematical statement. No mathematical hypothesis changed. A subsequent optional binder cleanup was interrupted and reversed exactly, restoring the checked attempt-9 source and object. Superseded diagnostic and refactoring runs were interrupted and are not passed verification.

All seven modules are frozen and strictly compiled. ResidueLatticeIdealWeights and ResidueLatticeNormCounts passed on their first attempts. Final source/object hashes, passing logs, declaration names, and exact counts are recorded in privatechecks/residue_final_freeze.json. There are 31 theorem declarations and 15 definitions or abbreviations. Independent release replay and transitive axiom checking are managed by the audit lane.

## Scope boundary

These are additive residue counts of actual ideal-lattice generators. They do not identify the quotient with an arbitrary multiplicative norm-residue codomain. Converting them to ideal counts requires the relevant torsion-orbit and norm-sign arguments. Pulling back a nontrivial character does not automatically give zero mean on the actual finite norm image. Arithmetic prime occurrence and the full Paper X Claim 9.1 remain separate.

## Main quantitative statements

Let Q = L/L0, h = card(Q), and d = dim_R(E). For every bounded measurable D carrying the proved finite Lipschitz boundary atlas in L0-coordinates, one C >= 0 satisfies, simultaneously for every c in Q and real t >= 1,

    |# {x in L : [x] = c and x in t D}
       - t^d volume(D)/(h covolume(L))|
      <= C (t^(d-1) + 1).

For every complex weight w on Q, the weighted cardinal sum is exactly the finite sum of w([x]) over those actual lattice points. The same C gives

    |sum_x w([x]) - t^d volume(D)/(h covolume(L)) sum_c w(c)|
      <= (sum_c |w(c)|) C (t^(d-1) + 1).

Thus a zero finite residue sum cancels the main term. The WeightedEstimate and ZeroMeanEstimate definitions express precisely these displayed inequalities; they do not hide an additional arithmetic assumption.

For nonzero integral ideals M <= J, the actual number-field cone supplies the atlas, boundedness, measurability, full lattice, and dimension equality. Its residue points are identified with algebraic integers x in J satisfying x-a in M. The final norm-threshold wrapper reparametrizes t = X^(1/d), so its boundary exponent is exactly 1-1/d. The underlying counts remain actual subtype cardinalities throughout, including before any weight is supplied.
