# Block31: least correlated reachable submodules

## Claim and domain
Let R be a commutative ring, V an R-module, v an initial vector, and T_d an
R-linear endomorphism for each digit d. The generic theorem permits an arbitrary
alphabet. The mask application uses Fin p. Define run so that a list is read in
its written order: run [d0,d1] v = T_d1(T_d0(v)).

Define Reach = span_R {run(w,v) : w is a finite digit word}.
Then Reach contains v, is invariant under every T_d, and is contained in every
invariant R-submodule containing v. Its initial state and restricted endomorphisms
are inherited by subtype inclusion. Ordered words commute exactly with inclusion.
This is correlated linear reachability, not initial-orbit enumeration and not
observational minimization.

## Proof of invariance and leastness
Every orbit generator run(w,v) is mapped by T_d to run(w++[d],v). Thus every digit
maps an orbit generator into Reach. Since T_d is linear, it maps their complete
R-span into Reach. The empty word supplies v. Conversely, an invariant submodule
containing v contains every word iterate by induction, hence their span. This
proves leastness without any field or division assumption.

## Finite construction and p-adic digit bound
Put U_0=0 and

  U_(n+1) = U_n + R v + sum_d T_d(U_n).

Here sum denotes the submodule supremum, not a union of the carrier sets. The
operator is monotone and inflationary. Its fixed points are exactly the invariant
submodules containing v. Every iterate is contained in every such fixed point.

Suppose V is finite and |V|=p^b for a prime p. By the quotient-cardinality theorem,
|U| divides |V| for every submodule U. Thus |U|=p^e for a unique 0<=e<=b. Proper
submodule inclusion strictly increases cardinality and therefore strictly increases
e. If two consecutive iterates agree, all later iterates agree. Consequently an
unstable b-th iterate would force b+1 strict p-power exponent increases, impossible
under e<=b. Therefore U_b is fixed, and leastness gives U_b=Reach.

No enumeration of p^b vectors is needed in this mathematical construction. The
bound b counts closure rounds, not runtime, arithmetic operations, or a formal
complexity bound for an implementation of submodule arithmetic.

## Integration with the already checked ideal and cyclic mask machines
The ambient V is the actual IdealMaskState, with unchanged seed and digit maps.
Blocks29-30 prove |V|=p^(sum_i c_i), so b=sum_i c_i supplies an explicit finite
closure bound. The new state is the subtype Reach inside this ideal module.
Its embedding into the predecessor cyclic state is ideal inclusion followed by
the inverse of the existing cyclic-to-ideal additive equivalence. Initial states,
steps, every word, and output commute with that embedding.

The ideal module itself has its existing R-linear inclusion into the original
full degree-profile coordinate space. The generic theorem

  f(Reach_M) = Reach_N

is proved for every linear simulation f preserving the seed and intertwining
all digit maps. Applying it to that inclusion shows the image of the new module
is the globally least invariant R-submodule of the full profile space containing
the original seed. Leastness is not limited to coordinate-ideal products or to
submodules chosen by one numerical basis algorithm.

For prime p, r>0, integer masks A,B, p not dividing B(0), and equal constants
modulo p^r, the canonical series F is already constructed. Composing with the
predecessor output yields output(n)=coeff_n(F) for all n. The output is independent
of any supplied series oracle. Positive-precision output compatibility is retained.

## Exact cardinality information
Reach has p^e elements where e=log_p |Reach| and e<=b. A smaller e is a genuine
reduction of mathematical ambient state cardinality. The present theorem does not
choose canonical independent generators, invariant factors, or transition matrices.
Those are the next presentation problem, distinct from identifying the submodule.

## Decisive witnesses
Over Z/5, v=(1,1,0) and T(x)=(0,0,x0-x1) have

  Reach = {(a,a,0): a in Z/5}.

The R-linear equivalence a |-> (a,a,0) proves |Reach|=5. The old least ideal
product is the full three-coordinate space, of cardinality125. Every vector in
the new correlated module maps to zero. These are production Lean theorems.

Reach is not generally the orbit set. With initial1 and identity transitions on
Z/5, the orbit set is {1}, whereas Reach=Z/5 and includes0. Also, if output is the
zero functional, all five reachable-linear states are observationally identical.
Thus reachability alone does not discharge the future observability quotient.
