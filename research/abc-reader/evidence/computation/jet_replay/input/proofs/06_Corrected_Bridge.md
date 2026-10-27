# The corrected global bridge and its unresolved hypotheses

The local results in this block are statements about explicitly defined series
and determinants. They neither prove nor disprove the existence of a different,
suitable arithmetic realization.

The comparison still needs a nonzero algebraic witness, or a rigorously defined
adelic determinant line with a proved arithmetic-degree identity. Coexistence of
complex, de Rham, and p-adic realizations is not itself such an identity.

## One elementary, correctly normalized certificate

For selected ranks r, put s_r=r(r+1)/2. Suppose that for every primitive triple
there is a nonzero integer W with

\[
Q^{s_r}\mid W,
\qquad
|W|\le C_r (ab)^{s_r}R^{E_r}(\log(3c))^{A_r}.
\]

Then

\[
(c/R)^{s_r}=(Q/(ab))^{s_r}
\le C_rR^{E_r}(\log(3c))^{A_r}.
\]

If E_r/s_r tends to zero along the chosen ranks, this implies ABC.
The constants may depend on r but not on a,b,c.

The logarithm absorption must be done without assuming ABC: after taking roots,
write c <= C R^{1+eta} (log(3c))^a. For a target epsilon>eta choose
0<delta<(epsilon-eta)/(1+epsilon). A fixed power of log(3c) is at most
K_delta c^delta. Rearrangement gives exponent (1+eta)/(1-delta)<1+epsilon.

The existence of W, its nonvanishing, its full local divisibility, and its global
height bound are ALL unproved for the present determinant candidate. This
certificate is an interface specification, not a new proof of any of its hypotheses.

## Alternative output-sector target

It is enough, and exactly equivalent to ABC, to prove

\[
M_c\le K_\varepsilon R_aR_bR^\varepsilon.
\]

The inherited Attack XI reduction separates M_c into epsilon_2 K W C and
retains the still-unproved radical-scale estimate for its W C factor.
This block does not reverify the arithmetic factorization or silently promote
an inherited computational identity to a new Lean theorem.

## Mandatory gates for the next block

1. Specify an actual global arithmetic object, not a collection of local scalars.
2. Prove that the chosen local determinant lies in the correct realization of that object.
3. Preserve the input/output and radical normalizations exactly.
4. Prove a nonzero algebraic scalar or a nonzero determinant-line section.
5. Bound every finite denominator and every archimedean conjugate or norm.
6. Demonstrate a new quantitative gain on c/R, not on the false Q=R^{o(1)} target.

No theorem in this block supplies these global gates.
