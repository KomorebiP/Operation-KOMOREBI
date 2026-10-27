# Infinite diagonal formalization: target contract

Base checkpoint: diagonal-formalization-base-01. The authoritative parent is the final publication ZIP with SHA-256 67e308826abe33873e1d99d6fcf70bb14df65d6b511597b295b0bf430520a990. Its Lean sources are recorded individually in BASELINE.json. This continuation does not change that finished publication.

The goal is kernel-checked counterparts of all three printed results in proofs/PRINTED_DIAGONAL_THEOREMS.tex, with no admitted proofs, new project axioms, unsafe declarations, or substitution of finite checks for infinite statements. Pinned compiler: Lean 4.34.0-rc2. Pinned mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Permitted standard axioms: propext, Classical.choice, Quot.sound.

## Exact targets

1. Proposition 30.1. On the actual real Hilbert space l2 over positive integer coordinates, T u at n is u_n/n and w_n=1/n. For every natural m>=1 and alpha=m^(-2), construct a_n=m^2/(m^2+n^2), prove square summability and equality with the universal unique regularized correction. Its residual is v_n=n/(m^2+n^2). Define actual infinite squared norms A_m and B_m. Prove m/4<=A_m<=4m/3, 1/(4(m+1))<=B_m<=2/m, and, for every K>=m, nonnegative omitted tails bounded by m^4/(3K^3) and 1/K.
2. Corollary 30.3. For b_n=1/n^2, construct the minimum-norm preimage a_dagger_n=1/n and the exact regularized correction c_n=m^2/(n(m^2+n^2)). For arbitrary Hilbert noise of norm <=delta with 0<delta<=1, use the literal integer schedule m=ceil(delta^(-2/3)), alpha=m^(-2), and prove error <=sqrt(2/m)+delta*m/2 <=(sqrt(2)+1)*delta^(1/3). Conditional scalar scheduling lemmas are useful progress but do not complete the actual Hilbert application.
3. Theorem 30.2. Prove A_m/m -> pi/4 and m*B_m -> pi/4, identify the actual infinite budget profile at M_m=sqrt(A_m), then transfer the limit to all real M -> infinity: M*beta(T,w,M) -> pi/4. Compare the hard-prefix correction at its actual norm budget, with limiting product 1. A selected subsequence or a finite numerical fit does not complete this target.

## Index convention

Lean natural index j=0,1,... represents printed coordinate n=j+1. Prefix length K consists of j in Finset.range K. Every source must preserve this shift explicitly.

## Work ownership and routes

The actual l2 construction, sharp series estimates, and noisy rounding estimate are joint dependencies, not alternative proofs of the same statement. The first route for series estimates is exact monotone integral/telescoping comparison; alternatives may use the pinned library's summability and tail inequalities after checking their hypotheses. The asymptotic route follows compact-interval Riemann convergence plus uniform tails; a closed-form hyperbolic-sum route is an alternative only if supported by exact pinned results.

A proof file is provisional until it compiles in the pinned environment with warnings rejected and its precise declaration/axiom inventory reviewed. No counts in the completed publication are changed during exploration. Failed compiler attempts and useful partial lemmas are retained. A completed declaration is not promoted to completion of the whole printed theorem until every listed obligation is matched.
