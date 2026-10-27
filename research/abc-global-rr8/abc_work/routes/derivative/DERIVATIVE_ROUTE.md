# Route D: arithmetic derivatives and integral nondegeneracy

## Contract and ancestry

The target remains full integer ABC: for every epsilon > 0, there is C_epsilon such that every positive primitive a+b=c satisfies c <= C_epsilon rad(abc)^(1+epsilon). A fixed exponent or an average bound does not complete it.

Base archive: ABC_Square_Kernel_Reverse_Realization_2026-10-25.zip, SHA-256 f9e5f22f454acf335f7267e6b69d0ee7c06394bf8744c3c3652fb9dec8ac9b59. Base PROOF_NOTE.md SHA-256 8327e169e70cedfd7576187cd0c6b2e2a46211916241540761b6c3b517484b27.

This route asks whether a small vector in an integer additivity kernel can be projected or lifted to a comparably small vector with nonzero arithmetic Wronskian. It does not presume that such a lift exists.

## Primary-source check

Hector Pasten, *Arithmetic derivatives through geometry of numbers*, arXiv:2106.16165v3, 11 December 2021, checked 25 October 2026. Primary text: https://arxiv.org/html/2106.16165v3. Published DOI: https://doi.org/10.4153/S0008439521000990.

Theorem 2.6 bounds the product of norms of independent integer derivations by omega(abc)c log(c)/(2 log 2). This supplies small vectors, without ensuring their Wronskians are nonzero. Theorem 3.3 gives c/log(c) <= rad(abc)||psi||/log 2 for a nonzero Wronskian. Conjecture 3.9 excludes triples whose entries are {1,N,q}, q prime, and seeks one exponent eta < 1. Lemma 4.1 then yields fixed-exponent ABC for M > 1/(1-eta). Conversely, Theorem 4.5 assumes fixed-exponent ABC with 1 < M < 2 and derives small derivatives for eta > 1-(2-M)/(4M). Thus a statement using just one unspecified eta < 1 must not be presented as the full every-epsilon ABC inequality. The source's informal equivalence language must be read with these exact exponent dependencies.

Source extraction and application were checked. No external theorem beyond these stated source results is used in the elementary propositions below. No historical novelty claim is made.

## Elementary exact image theorem for the a=1 slice

Give each prime p an integer coordinate z_p, with coordinates outside the prime factors of bc set to zero, and define

D_z(n) = sum_{p|n} v_p(n) (n/p) z_p.

For n>1, let

G(n) = gcd_{p|n} [v_p(n)n/p].

The image of the map z -> D_z(n) is exactly G(n) Z. Divisibility in one direction is immediate. The converse is Bezout's identity for the finitely many displayed coefficients.

Now take b>1 and c=b+1. Since b and c are coprime, their prime coordinates are disjoint. For the additivity condition D_z(b)=D_z(c), the Wronskian W(1,b) equals this common derivative. Consequently its image on the integer additivity kernel is exactly

lcm(G(b),G(c)) Z.

In particular, among derivations with W != 0, the minimum possible absolute W is exactly L=lcm(G(b),G(c)). This statement concerns W values, without asserting that a vector achieving the minimum has a small coordinate norm.

Writing U(n)=n/rad(n), each coefficient v_p(n)n/p is divisible by U(n). Therefore U(b)|G(b), U(c)|G(c), and coprimality implies

U(b)U(c) | L.

For R=rad(bc), this gives L >= bc/R. Recovering a radical lower bound from this identity still requires an independent smallness estimate.

Let S(n)=sum_{p|n} v_p(n)n/p. If B=max|z_p| and W!=0, then

B >= max{L/S(b), L/S(c)}.

Indeed, |W| >= L while |D_z(n)| <= B S(n) on each side. This is a useful exact lower bound on the cost of an integral lift.

## Decisive non-excluded counterexample to naive projection

For 1+48=49, coordinates are (z_2,z_3,z_7)=(x,y,z). The additivity condition is

96x+16y=14z, equivalently 48x+8y=7z.

Reducing modulo 8 forces 8|z. Nondegeneracy is z!=0, so every nondegenerate vector has norm at least 8. The vector (1,1,8) attains norm 8 and has W=112. Here G(48)=16, G(49)=14, L=112, S(49)=14.

If z=0, y=-6x. Thus the shortest nonzero additivity vector is (1,-6,0), norm 6, and it is degenerate. There is no nondegenerate vector of comparable claimed square-root threshold sqrt(49)=7. Both 48 and 49 are composite, so this example lies outside the prime exception in Conjecture 3.9.

This refutes the finite universal assertion that taking a shortest nonzero additivity vector automatically provides nonzero W, or that every such triple admits a nondegenerate vector with norm <=sqrt(c). It does not refute an eventual theorem with constants, nor Pasten's conjecture, nor ABC. A rational perturbation can leave the W=0 hyperplane, but clearing denominators must restore the divisibility 8|z. Ordinary real projection does not pay this integral cost.

## Four exact comparisons

| Triple | Shortest nonzero height | Minimum nondegenerate height | Minimum absolute W |
|---|---:|---:|---:|
| 1+36=37 | 3 | 12 | 12 |
| 1+48=49 | 6 | 8 | 112 |
| 1+80=81 | 4 | 4 | 432 |
| 1+108=109 | 1 | 108 | 108 |

For the first and fourth examples the prime exception applies. All entries follow from direct linear equations, and verify.py independently enumerates complete cubes containing every vector of smaller norm. The nondegenerate-height lower bounds also follow from L/S(c), with explicit attaining witnesses. No asymptotic inference is made from this table.

Command: `python3 abc_work/routes/derivative/verify.py`.

## Route disposition and next unresolved implication

Outcome: an exact image theorem and explicit obstruction to a proposed small-vector/projection bridge. Full ABC is unresolved.

The projection-only construction is closed as a proof mechanism without additional arithmetic estimates. The broader derivative route remains open. The unresolved obligation is a uniform upper bound on the minimum coordinate norm of an integer lift outside the W=0 sublattice, strong enough in its exponent to imply the requested every-epsilon radical bound. The exact image theorem does not bound that norm from above.

Potential continuation: compare the covolume and successive minima of the W=0 sublattice with its ambient additivity lattice, retaining the integer quotient and the exponent dependencies. A plain product-of-minima estimate cannot single out the required nondegenerate vector. No uniform improvement was proved here.

Review provenance: self-derived proof, source comparison, exact finite computation. No Lean compilation and no independent expert review.
