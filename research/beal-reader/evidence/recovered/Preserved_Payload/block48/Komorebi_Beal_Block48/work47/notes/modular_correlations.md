# Block47: modular correlation audit and two exact residue restrictions

Status: exact finite computations and a source-code audit. No new Hilbert form has been eliminated. No fresh Magma computation of a Hilbert modular form space was performed.

## 1. What the published elimination actually keeps

The audited revision is `e88f914c577ab6cf9a45e5cdd82c1993477fb423` of [PV's repository](https://github.com/lucasvillagra/GFE-5p3/tree/e88f914c577ab6cf9a45e5cdd82c1993477fb423). We fetched `Codes/MagmaCode.m`, `Codes/GPcode.gp`, and `Outputs/Data.txt` through the GitHub connector. Local copies are in `work47/source_records/`.

`NewformBound` selects `Factorisation(l*OK)[1][1]`, obtains one Hecke eigenvalue, and replaces it by its minimal polynomial. It then takes resultants against the possible trace polynomials and combines these by lcm. `TheoremABound` takes a gcd of these rational integers across auxiliary primes. The boundary routines similarly use norms, minimal polynomials, and resultants.

Consequently, the calculation is a necessary-condition relaxation. It does not retain:

- a fixed prime of the newform coefficient field above seven across the different auxiliary primes;
- a fixed residue embedding into an algebraic closure of F7;
- simultaneous trace data at both primes of K above a split rational prime;
- an explicit parameter label attached to each computed trace polynomial.

This is not a correctness error in the published exclusions. Relaxation can preserve additional candidates but cannot invalidate an exclusion. The script's use of one split prime and its successive norm operations gives a concrete place to investigate a stronger computation.

There are important limits to the proposed improvement. Seven is inert in K=Q(sqrt(5)), so a coefficient field equal to K has only one prime above seven. Its two residue embeddings are related by seventh-power Frobenius. Moreover, for the Frey family the two split-prime traces are algebraic conjugates. A candidate satisfying the same equivariance may satisfy the second-prime test automatically. Thus one must examine each surviving form before claiming that a lost label causes that particular survivor.

The public revision provides no individual coefficient-field definitions or Hecke-eigenvalue exports for indexed forms 3,9,12 at level 3^2(sqrt(5))^2, or 65,78 at level 3^3(sqrt(5))^2. The paper gives aggregate coefficient-field counts, not those labels. We have not assigned fields or primes above seven to those forms. The smallest-level forms are described as CM forms, but this alone does not identify every coefficient field or an embedding.

Theorem 7.8 in [PV, arXiv:2512.17845v1](https://arxiv.org/html/2512.17845v1) states the modular attachment conditional on irreducibility and does not exclude seven in its statement. This note does not independently replay every hypothesis of its cited modularity and level-lowering results. In particular, the conditional consequences below explicitly assume the modular comparison and the standard multiplicative-prime comparison.

## 2. Exact audit of the available finite data

Run:

```text
python3 work47/computations/modular_correlations.py --output work47/verification/modular_correlations.json
```

The parser reads all 37 tuples in the author's `Data.txt`, using a strict parser for monic polynomials of degree one or two. The auxiliary prime seven is omitted from the mod-seven comparison. For the other 36 primes it computes every polynomial root in F49=F7[u]/(u^2-5). Boundary traces are compared after the appropriate residue-degree transformation a -> a^2-2q^f where necessary.

These computations are exact **on the imported polynomial data**. The original GP script recognizes p-adic approximations with `algdep`; this run does not independently certify those imported polynomials at all primes. Independent integer point counts were performed at eleven and nineteen as detailed below.

At q=11 the regular trace set has 15 distinct elements of F49. The coefficient-conjugate pairs (a,a^7) give 15 ordered pairs, whereas forgetting the correlation gives 225 ordered pairs. This is an exact information-loss demonstration using genuine source data. It is not a claim that any of the 210 extra pairs occurs for a surviving modular form.

An additional limitation is visible: at each of the 21 listed auxiliary primes at least 139, the regular trace set is already all of F49. At those particular primes the imported scalar-trace test cannot exclude an F49-valued eigenvalue. No assertion is made about every larger prime. A refinement should therefore target a correlation, a boundary condition, or a representation invariant beyond the scalar support; merely increasing the number of large scalar-trace tests can be ineffective.

A separate synthetic control has two auxiliary supports `{P0}` and `{P1}`. Both individual tests are nonempty but their intersection is empty. This checks the quantifier distinction only, and is explicitly not a Hilbert-form elimination example.

## 3. A parameter-convention issue that matters for lanes

Exact point counts for equation (32),

    y^2 = 5x^6 - 12x^5 + 10t x^3 + t^2,

at all t in F11 minus {0,1} reproduce the complete unlabelled polynomial multiset in `Data.txt`. Their individual labels agree with the hypergeometric values in the paper's Table 7.4 after t -> t^{-1}, rather than at the same t. For example:

- Equation (32) at t=3 has N1=11 and N2=163, yielding the trace polynomial X^2-X-1. This is also consistent with the full degree-four polynomial in Table 7.1.
- Table 7.4 assigns X^2-5 to its t=3 and X^2-X-1 to its t=4; 4 is the inverse of 3 modulo eleven.

Eight of the nine nondegenerate labels differ under the identity map; all nine agree after inversion. This is a demonstrated convention mismatch between these two labelled calculations, not a claim that the published unlabelled elimination is wrong. It is consistent with exchanging the hypergeometric upper and lower parameters. The exact general dictionary must be resolved before attaching refined residue lanes to the GP output. The direct Beal-model computations below avoid this issue entirely.

## 4. Exact local trace-zero restrictions on the Beal model

Let A^3+B^5=C^7 be a hypothetical primitive positive solution and use

    J_AB = Jac(Z^2 = X^6+10BX^3+12AX+5B^2).

Suppose its rank-two representation modulo seven is congruent to a parallel-weight-two, trivial-nebentypus modular representation. At a good prime q the determinant of this modular representation is q modulo seven.

The words “trace zero” below mean the trace of this **rank-two** representation, not the scalar trace of the full four-dimensional Jacobian representation. Seven is inert in K, so a rank-two trace-zero representation with determinant q has, after restriction of scalars, the degree-four Frobenius polynomial

    (T^2+q)^2 mod 7.

The direct certificate checks this full polynomial identity, in addition to checking the roots of the extracted rank-two trace polynomial.

### Proposition: restriction at eleven

If the congruent rank-two modular representation has trace zero at a prime of K above eleven, then 11 divides A.

Proof. If eleven does not divide C, the discriminant identity already recorded in Block46 shows good reduction. Enumerate all pairs (A,B) in F11^2 satisfying A^3+B^5 != 0. There are exactly 110 such pairs. Exact point counts over F11 and F121 give the degree-four Frobenius polynomial for each. Its reduction is (T^2+11)^2 precisely for the ten pairs with A=0. Thus a good-reduction trace-zero match forces A=0 modulo eleven.

If eleven divides C, the usual multiplicative-prime comparison from the modular method gives a modular trace congruent to +12 or -12. Neither is zero modulo seven. This excludes the remaining branch. QED, subject to the stated modular comparison and multiplicative-prime comparison.

The finite calculation is small and fully retained in the JSON. In the A=0 lane, every polynomial is exactly T^4+22T^2+121. In the B=0 lane, the five distinct rank-two trace polynomials are

    X^2-4X-16, X^2+X-1, X^2+11X+29,
    X^2+X-31, X^2-9X+19.

None has zero as a root modulo seven. The nine regular trace polynomials are also all recorded and likewise exclude zero.

As a conditional CM consequence, a modular form with CM by K(sqrt(-3)) has trace zero at either prime above eleven, since eleven splits in K and those primes are inert in the CM quadratic extension. Hence a congruence to such a form forces 11|A. This is a divisibility restriction, not an elimination of the CM form. It applies to the CM category without needing an unverified numerical form-index dictionary.

### Proposition: restriction at nineteen

If the congruent rank-two modular representation has trace zero at a prime of K above nineteen, then 19 divides B.

Proof. There are 342 pairs (A,B) in F19^2 with A^3+B^5 != 0. The transformations

    (A,B) -> (u^5 A,u^3 B),  u in F19^*,

correspond to isomorphisms X -> uX, Z -> u^3 Z of the curves. They partition the 342 pairs into 21 explicitly enumerated orbits. Exact point counts over F19 and F361 for one representative per orbit show that the reduction of the degree-four polynomial is (T^2+19)^2 exactly when B=0. The B=0 orbit has 18 elements and polynomial T^4+38T^2+361. If nineteen divides C, the multiplicative-prime comparison gives +/-20, again nonzero modulo seven. QED under the same comparison hypotheses.

We do not identify any indexed CM survivor as having a zero trace at nineteen without the appropriate CM-field or Hecke-eigenvalue data. This proposition is ready to apply when that data is certified.

### Point-count formula

For a smooth sextic Z^2=f(X) over Fq of odd characteristic, the script counts affine points with the quadratic character and counts the points at infinity from the leading coefficient. If N1 and N2 are its counts over Fq and Fq^2, set

    s1=q+1-N1,
    s2=(s1^2-(q^2+1-N2))/2.

Then the full Frobenius polynomial is

    T^4-s1 T^3+s2 T^2-q s1 T+q^2.

For the RM family the trace polynomial is X^2-s1 X+(s2-2q), reduced to degree one when both conjugate traces coincide. The script does not use a zero four-dimensional trace as a substitute for a zero rank-two trace: it also checks s2=2q modulo seven and the full polynomial identity.

## 5. Concrete next computation and limits

Export, for each surviving form, its exact coefficient-field polynomial, maximal order or integral model, the prime ideals above seven, and Hecke values at both base primes above the selected split auxiliary primes. Retain the map from each Hecke value to the same residue field. Compare these records with the direct curve tables, with the same modular candidate and the same prime/embedding throughout. Use the local restrictions above to label surviving branches such as 11|A rather than returning only “form survives.”

No surviving modular form is eliminated here. The candidate-field exports are genuinely missing, and no amount of rearranging the present transcript supplies them. In addition, compatible local divisibility conditions at finitely many auxiliary primes need not contradict a global solution. The result of this block is a validated refinement target, exact local restrictions, and a demonstrated parameter-labelling risk that must be fixed before implementing a certified combined sieve.

## Source and artifact provenance

- Pinned `Codes/MagmaCode.m`: SHA256 `1604d9a52c2cb600fd8eaebd389f32c9fcdb0bc5b7c0f63ef658b8a9181bf76a`.
- Pinned `Codes/GPcode.gp`: SHA256 `e03daf70df2bc66acd58c7f4efe5e6f04dfb6f10d591cf1786264d4ab9692481`.
- Pinned `Outputs/Data.txt`: SHA256 `61c72fec10c3cd39874f57a39f3603c081e14ad34a4b2be1d6f6a5eb83c43fdd`.
- Code: `work47/computations/modular_correlations.py`.
- Exact output: `work47/verification/modular_correlations.json`.
- Full stdout: `work47/verification/modular_correlations.stdout.txt`.

Initial public web requests for the repository/raw paths failed. The connector directory listing established the correct `Codes/` and `Outputs/` paths and retrieved the files successfully. No Magma or PARI/GP execution was available. Python standard-library exact arithmetic was used for the finite checks. This note has not yet received an independent adversarial proof audit.
