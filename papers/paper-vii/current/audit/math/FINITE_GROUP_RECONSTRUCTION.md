# Independent reconstruction of the finite-group projector dependency

Verdict: **proved as written**, for the normalized finite-group claims at strengthened source lines365–425, by this elementary reconstruction. This is independent mathematical audit evidence. It does not authenticate an exact page or theorem in Serre and does not add a new result to the manuscript.

The reviewed strengthened file SHA-256 is `60162de34683f382ad1046777ee5b1e8e0b87b94c3e23b8022ec6df2b77ee416`. Assume a finite group `G`, a finite-dimensional complex Hilbert space `H`, and a unitary representation `U`. Let `pi_lambda` be the chosen irreducible unitary representations in chosen orthonormal bases. Every denominator `|G|` is positive because a group is nonempty.

## Complete reducibility and the exact averaging identity

If `V` is invariant under every `U(g)`, then `V^perp` is invariant too: for `x` in `V^perp` and `v` in `V`, the inner product of `U(g)x` with `v` vanishes because `U(g)^*v=U(g^-1)v` lies in `V`. Repeatedly split off a minimal nonzero invariant subspace. Finite-dimensional induction gives an orthogonal direct sum of irreducibles, grouped as

`H = direct-sum_mu (V_mu tensor M_mu)`,

with `U(g) = direct-sum_mu (pi_mu(g) tensor I_M_mu)`. An absent irreducible has zero multiplicity. For `H=0`, the direct sum is empty and all projector assertions reduce to zero identities.

For an arbitrary linear map `B:V_lambda -> V_mu`, put

`A(B) = (1/|G|) sum_g pi_mu(g) B pi_lambda(g)^*`.

Replacing `g` by `hg` proves `pi_mu(h) A(B)=A(B) pi_lambda(h)` for every `h`. If the two irreducibles are inequivalent, this intertwiner is zero: a nonzero intertwiner has invariant kernel and image, hence is an isomorphism. For equal chosen representations, every commuting endomorphism is scalar. To see the latter directly over `C`, take an eigenvalue `c`; the nonzero kernel of `A-cI` is invariant and hence the whole irreducible space. Its scalar is `Tr(B)/d_lambda`, because trace is preserved under each unitary conjugation. Thus

- `A(B)=0` for inequivalent `mu,lambda`;
- `A(B)=(Tr(B)/d_lambda) I` for `mu=lambda`.

The argument uses only finite complex linear algebra, including existence of a complex eigenvalue, and unitary averaging. It makes no assertion about an infinite-dimensional, nonunitary, compact-group, or distributional extension.

## Index and normalization check

Take `B` with its only nonzero entry at row `b` and column `j`. The `(a,i)` entry of the average is

`(1/|G|) sum_g [pi_mu(g)]_ab conjugate([pi_lambda(g)]_ij)`.

For equal irreducibles `Tr(B)=delta_bj`; the identity entry is `delta_ai`. Therefore the exact coefficient identity is

`(1/|G|) sum_g conjugate([pi_lambda(g)]_ij) [pi_mu(g)]_ab
 = delta_lambda,mu delta_a,i delta_b,j / d_lambda`.

In the unequal case both sides are zero, so no dimension is canceled across distinct representation types.

The manuscript coefficient

`[pi_lambda(g^-1)]_ji`

is precisely `conjugate([pi_lambda(g)]_ij)` by unitarity. Consequently

`E_ij^lambda=(d_lambda/|G|) sum_g [pi_lambda(g^-1)]_ji U(g)`

acts on the `mu` summand as zero when `mu!=lambda`, and as the matrix unit `|i><j| tensor I_M_lambda` when `mu=lambda`. The inverse/index order and the factor `d_lambda/|G|` therefore agree with the target-first matrix-unit convention. Reversing `i,j` here would reverse the resulting matrix unit.

On each actual summand, ordinary matrix multiplication and adjoint give exactly

`E_ij^lambda E_kl^mu = delta_lambda,mu delta_jk E_il^lambda`,

`(E_ij^lambda)^* = E_ji^lambda`.

These identities then hold on the entire orthogonal direct sum.

Finally, summing `E_ii^lambda` over `i` gives

`P_lambda=(d_lambda/|G|) sum_g conjugate(chi_lambda(g)) U(g)`.

It is identity on the `lambda` isotypic summand and zero on every other summand. Hence `P_lambda^*=P_lambda`, `P_lambda P_mu=delta_lambda,mu P_lambda`, and `sum_lambda P_lambda=I_H`. Zero multiplicities produce zero projectors and cause no exception. This reconstructs the precise load-bearing implication used in strengthened sections3,7 and the Choi isotypic corollary.

## Obligation matrix

| Obligation | Status |
|---|---|
| Actual finite unitary representation and complete invariant decomposition | Passed by invariant orthogonal complements and finite induction |
| Schur intertwiner/scalar step | Passed by invariant kernel/image and a complex eigenvalue |
| Averaging normalization `1/|G|` and dimension factor | Passed |
| Conjugation versus inverse and exact `ji` coefficient order | Passed |
| Matrix-unit multiplication and adjoint on each summand | Passed |
| Central isotypic range, Hermiticity, orthogonality, completeness | Passed |
| Missing irreducibles and zero-dimensional ambient space | Passed |
| Exact Serre source/theorem authentication or novelty assertion | Out of scope; no such claim made |

There is no remaining mathematical implication for this finite-group dependency at the stated level. Exact bibliographic attribution is separate from this reconstruction.
