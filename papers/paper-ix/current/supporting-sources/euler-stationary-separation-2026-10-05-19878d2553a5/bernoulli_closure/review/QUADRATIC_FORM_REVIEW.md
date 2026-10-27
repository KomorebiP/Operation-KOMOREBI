# Independent review of the Bernoulli quadratic-form theorem

**Normalized claim.** For every x in Z_2, the form
`p -> L_x(p^2)`, where `L_x(U^n)=D(x+n)`, is anisotropic on the nonzero
polynomials in Q_2[U] of degree at most 3, and has a nonzero isotropic
polynomial of degree exactly 4. For the actual moment functional
`U^n -> 2B_(2(r+n))`, the corresponding assertions hold for ordinary
`r>=10` and `r>=16`, respectively.

**Primary verdict: proved as written.** The external Bernoulli recurrence is
an authenticated input recorded in the companion source record; this review
independently reconstructs its normalization, even contraction, operator
extension, mod-8 calculation, and transfer to actual moments. No identity
between these norms and the Euler critical scalar is established. In
particular this verdict is not a verdict on Euler simplicity.

Reviewer: `/root/cross_cartier_review`, independently reading the raw proof and
checker. No author file was edited by the reviewer. The author incorporated one
minor requested domain clarification: the integer moment formula is stated for
ordinary **nonnegative** integers n. No substantive mathematical correction was
needed. No Lean compilation was performed.

## Dependency graph and domain

1. The companion proof establishes that the defining Mahler series for D
   converges to a restricted integral analytic function, with
   `D(z)=1+4z+16R(z)` and R integral. Thus D is a unit at every dyadic input.
2. The authenticated monic Bernoulli recurrence, under `X=2y+1` and then
   `U=X^2`, gives the stated coefficients a_n,b_n and orthogonal norms.
3. Dividing the monic polynomials by `c_n=4^n(n!)^2` gives a bounded Jacobi
   operator on c_0, with unit diagonal Gram entries and `J=I+4K`.
4. The operator power J^x interpolates multiplication at ordinary nonnegative
   integers. Continuity on the dense ordinary indices identifies its matrix
   coefficients with the prescribed shifted moments D(x+n).
5. Its first two binomial terms determine the Gram matrix modulo 8. Elementary
   parity gives four-dimensional anisotropy and the explicit fifth-coordinate
   square-root construction gives isotropy.
6. Actual undepleted moments differ sufficiently little at the stated r
   thresholds to preserve exactly those Gram congruences.

The source functional is Q_2-linear on finite polynomials. The use of c_0 is a
controlled operator extension, not an unproved extension of the original
moment functional to arbitrary unbounded series. All bilinear sums in that
completion converge with an explicit unit norm bound.

## Obligation matrix

| Obligation | Status | Reason |
|---|---|---|
| Centering and scaling the Bernoulli recurrence | Passed | The lower coefficient acquires factor 4, giving `rho_n=-n^4/(4n^2-1)` and zero diagonal |
| Even contraction and monic norm normalization | Passed | Applying multiplication by X twice gives `b_n=rho_(2n)+rho_(2n+1)` and `a_n=rho_(2n)rho_(2n-1)` |
| Unit norm congruence `u_n=5^n mod8` | Passed | `u_n/u_(n-1)=a_n/(16n^4)=5 mod8`; u_0=1 |
| Bounded extension on c_0 | Passed | Uniformly integral tridiagonal entries preserve c_0; diagonal unit form is continuous |
| Analytic interpolation of the Gram matrix | Passed | Binomial operator series converges uniformly and agrees with the prescribed moments on dense ordinary indices |
| Mod-8 diagonal and mod-4 off-diagonal formula | Passed | `J^x=I+4xK mod8`, with diagonal K odd |
| Anisotropy for degree at most 3 | Passed | Primitive coordinate parity is exhaustive, with the four-odd case nonzero modulo 8 |
| Exact degree-4 isotropic vector | Passed | The displayed discriminant unit is 1 modulo 8 and has an actual dyadic square root |
| Actual-moment thresholds r>=10 and r>=16 | Passed | Basis denominator loss is at most 16 and 28 respectively, leaving precision at least 3 |
| Finite computation interpretation | Passed | Checker verifies the claimed examples and patterns, without promoting finite zeros to exact roots |
| Identification with Euler stationary nonvanishing | Not addressed | The proof explicitly leaves the norm representation missing |

## Reconstructed normalization and mod-8 argument

With the source convention `P_(n+1)=(y+1/2)P_n-t_nP_(n-1)`, the coefficient
is `t_n=-n^4/[4(2n+1)(2n-1)]`. The monic affine transform multiplies this
coefficient by 4 and makes the diagonal zero. Its even moment sequence is
`4^n B_(2n)(1/2)=(2-4^n)B_(2n)=D(n)`. There is no missing sign or power of
2. The initial contracted norm check is

    P_1=U+1/3,
    L_0(P_1^2)=16/45,
    u_1=L_0((P_1/4)^2)=1/45=5 mod8.

For n>=1, cancellation in `a_n/(16n^4)` leaves an odd fourth power over
`(4n-3)(4n-1)^2(4n+1)`. This denominator is 5 modulo 8, so the quotient is
5 modulo 8. For b_n the even fourth-power term is zero modulo 8; the odd
term is `-1/3=5 mod8`. The off-diagonal coefficients in the normalized basis
are `4(n+1)^2` and `a_n/(4n^2)`, both divisible by 4. Consequently the
Jacobi diagonal is 5 modulo 8 and `K=(J-I)/4` has odd diagonal.

The c_0 operator series converges because each term has norm at most `2^-2h`
pointwise for x in Z_2. Uniform convergence gives continuity in x; stronger
restricted analytic convergence also follows from the factorial denominator
bound on the binomial polynomials. The diagonal bilinear form
`sum u_n v_n w_n` is continuous on c_0 by the nonarchimedean convergence
criterion. For finite basis vectors, its weighted entry is
`u_i (J^x)_(i,j)`. All terms of degree h>=2 in J^x vanish modulo 8, giving

    M_x(i,i)=(1+4x)5^i mod8,
    M_x(i,j)=0 mod4 for i!=j.

The equality with L_x follows on dense ordinary indices and then for every
dyadic x by continuity. This passage does not use real positivity or a Haar
measure change of variables.

After scaling a nonzero polynomial to primitive integral e-coordinates, the
cross terms in its norm vanish modulo 8. If exactly one, two, or three of
four coordinates are odd, the norm is nonzero modulo 4. If all four are odd,
the norm is `(1+4x)(1+5+1+5)=4 mod8`. These alternatives exhaust primitive
vectors, including lower-degree polynomials padded with zero coordinates.

For the proposed degree-4 vector, the coordinates of w are `(1,0,1,1,2)`.
Its diagonal contributions give
`C=(1+4x)(1+1+5+4)=3(1+4x) mod8`, while
`A=5(1+4x) mod8` and `b in4 Z_2`. Hence
`(b/A)^2-C/A=1 mod8`. An odd dyadic square root exists; substituting
`y=-b/A+t` gives an exact zero of the quadratic. The e_4 coefficient is
exactly 2, so the resulting polynomial has degree exactly 4. This construction
does not conflict with a nonzero determinant of the bilinear Gram matrix.

## Transfer to actual Bernoulli moments

For ordinary r>=1 and n>=0, the undepletion identity is exact and its
denominator is a unit. Since D(r+n) is a unit, the actual moment difference
has valuation exactly `2(r+n)-1`, in particular at least `2r-1`. Each P_n is
integral by its monic recurrence. Dividing the product P_i P_j by c_i c_j
loses at most

    4(m-1)+4v_2((m-1)!)

for indices below m. This is 16 for m=4 and 28 for m=5. The proposed
thresholds leave respectively `2*10-1-16=3` and `2*16-1-28=3` bits of
valuation. Thus the actual Gram matrices retain the exact congruences used
in both arguments. No sharpness in the ordinary threshold r is claimed;
the sharpness statement concerns the polynomial degree.

## Source and computation checks

The project source authentication is in
`nonintersection/BERNOULLI_HANKEL_SEPARATION.md`, section 2: Dilcher--Jiu,
arXiv:2105.01880v1, 5 May 2021, recurrence (2.4) and the proof of Proposition
3.1 on printed page 8. That record explicitly identifies the convention and
negative t_n. This review used that authenticated project record and checked
its entire normalization chain. A fresh reviewer retrieval of the primary PDF
returned `DisabledError`; no new independent PDF authentication or local PDF
hash is claimed. The parent has separately read the primary sources.

The checker was read and replayed with the bounded experiment runner into
`review/quadratic_replay`. It produced results byte-identical to
`root/certified_run/results.json`. Both manifests validate against the project
root. The replay verifies 448 Gram congruences, 6,720 primitive modulo-4
coordinate patterns, and four 40-bit isotropic lifts. Bernoulli numbers are
constructed independently from their rational recurrence rather than supplied
from the Jacobi formula. The square-root loop preserves the required congruence
at every bit; its output is supporting evidence for the exact existence proof.

No finite test was used as a substitute for the universal quantifiers. The
anisotropy enumeration is correctly exhaustive for the finite residue test:
each of 28 matrices checks the 240 primitive vectors among 256 modulo-4
vectors. Squares modulo 8 are determined by coordinates modulo 4, and every
off-diagonal norm term vanishes modulo 8.

## Exact revisions

Paths are relative to the project root.

| Artifact | SHA256 |
|---|---|
| bernoulli_closure/root/BERNOULLI_QUADRATIC_FORM.md | ffd3beafa4c293b090753fcd51a538a8920f886515e7b652fc9b34f5c206e01e |
| bernoulli_closure/root/check_quadratic_form.py | b58ca73893739c6e8899df1da874e2e26e8a69ab9d91c45bf3cf2a32a7b08412 |
| bernoulli_closure/root/contract.json | 5255588931fefe5be69bad38e4558aede48ada41bbc7e39fbbfef8ba8293149e |
| bernoulli_closure/root/certified_run/manifest.json | c9ca43c1f29f8dcb03b9d187f77b3536dd4e71c10e0498840a27bc26c6e0558f |
| bernoulli_closure/root/certified_run/results.json | 88ce8fdea4c7c4d5284cbb80349f28c06431fbe5aebf891457be475a8ab6c19d |
| bernoulli_closure/nonintersection/BERNOULLI_HANKEL_SEPARATION.md | 551af0af45e7f2b13976cd63922234bc29afa837d5f0649b22eabfa16fa76b78 |
| bernoulli_closure/review/quadratic_replay/manifest.json | 662a5ad6fc5f271ca7aeb526d6e0d28a8db75262b4d727bb5064407f9579a184 |
| bernoulli_closure/review/quadratic_replay/results.json | 88ce8fdea4c7c4d5284cbb80349f28c06431fbe5aebf891457be475a8ab6c19d |

## Remaining Euler implication

The theorem gives a sufficient nonvanishing certificate **if** the actual
critical scalar is represented as the norm of a nonzero polynomial of degree
at most 3, with the exact functional and normalization controlled. Such a
representation has not been proved. Degree 4 is already isotropic, so an
unrestricted norm representation alone would not suffice. The next meaningful
check is the proposed exact weighted representation, not additional numerical
sampling of these already controlled moment forms.

Self-review: conservative proofreading covered this whole report. No
mathematical-token change or unresolved local notation issue remains.
