# Projector-Resolved ABC Attack IX: Sparse-Prony and Entropy-Barrier Addendum

## Status

This addendum develops the signed arithmetic COS program beyond dual filtering and Christoffel optimization.

It proves four structural facts.

1. A strong `abc` exception lies in an extremely sparse spectral regime. General mixing cannot be the finishing mechanism.
2. The shift-Krylov rank is exactly the number of occupied arithmetic residues, up to the chosen polynomial degree.
3. The complete assignment distribution can be recovered from twice that many consecutive transform samples by a Prony recurrence.
4. A Galois reindexing always removes a catastrophically small target interpolation denominator in at least one cyclotomic coordinate.

These results strengthen the compression and extraction side of the program. They do not prove the `abc` conjecture.

## 1. Assignment signal

Let `G` be a finite cyclic channel of order `n`. Let `N(x)` be the number of ternary prime assignments producing residue `x`, and let

\[
M=\sum_{x\in G}N(x)=3^s,
\]

where `s` is the number of variable support primes.

Define

\[
\mu(x)=\frac{N(x)}M
\]

and its normalized transform

\[
m(k)=\sum_{x\in G}\mu(x)e^{2\pi ikx/n}.
\]

Let

\[
E=\{x:N(x)>0\},
\qquad
r=|E|.
\]

Then

\[
r\le M.
\]

The target count is recovered by

\[
N(h)=\frac Mn\sum_{k=0}^{n-1}m(k)e^{-2\pi ikh/n}.
\]

## 2. Sparse-energy barrier

Parseval gives

\[
\sum_{k=0}^{n-1}|m(k)|^2
=
\frac n{M^2}\sum_xN(x)^2.
\]

Cauchy-Schwarz on the occupied residues gives

\[
\sum_xN(x)^2
\ge
\frac{M^2}{r}.
\]

Therefore

\[
\boxed{
\sum_{k=0}^{n-1}|m(k)|^2
\ge
\frac nr.
}
\]

Since `m(0)=1`,

\[
\boxed{
\sum_{k\ne0}|m(k)|^2
\ge
\frac nr-1
\ge
\frac nM-1.
}
\]

This is the sparse-energy barrier.

A distribution supported on far fewer than `n` residues cannot have a small transverse periodogram. Large nontrivial spectral energy is forced by support sparsity itself.

A corresponding peak bound is

\[
\boxed{
\max_{k\ne0}|m(k)|
\ge
\sqrt{
\frac{n/r-1}{n-1}
}.
}
\]

The synthetic transition seen in Attack IX is now explained exactly. Mixing begins only when the assignment entropy

\[
s\log3
\]

reaches the channel entropy

\[
\log n.
\]

Before that point, a large nontrivial periodogram is unavoidable.

## 3. Strong exceptions are on the sparse side

For a primitive triple, write

\[
a=Ar_a,
\qquad
b=Br_b,
\qquad
c=Cr_c,
\]

where the `r` variables are radicals. Put

\[
R=r_ar_br_c,
\qquad
Q=ABC=\frac{abc}{R}.
\]

Assume that for some fixed `epsilon > 0`,

\[
c>R^{1+\varepsilon}.
\]

Because `ab >= c-1`,

\[
Q=\frac{abc}{R}
\ge
\frac{c(c-1)}R.
\]

For sufficiently large `c`,

\[
Q>\frac12R^{1+2\varepsilon}.
\]

For every `delta > 0`,

\[
\frac Q{\varphi(Q)}
\ll_\delta R^\delta.
\]

This follows by separating the finitely many small primes and using

\[
(1-1/p)^{-1}\le p^\delta
\]

for all sufficiently large primes.

Likewise, for every `eta > 0`,

\[
3^{\omega(R)}\ll_\eta R^\eta.
\]

The joint powerful-channel group has size

\[
|G_Q|=\varphi(Q),
\]

while the number of variable prime assignments is at most

\[
M=3^{\omega(S)}\le3^{\omega(R)}.
\]

Choose `delta=eta=epsilon/2`. Then every sufficiently large strong exception satisfies

\[
\boxed{
\frac{|G_Q|}{M}
\gg_\varepsilon
R^{1+\varepsilon}.
}
\]

Consequently,

\[
\boxed{
\sum_{\chi\ne1}|\widehat\mu(\chi)|^2
\gg_\varepsilon
R^{1+\varepsilon}.
}
\]

### Interpretation

The hardest `abc` regime is not an expansion regime. It is an ultra-sparse regime.

The assignment measure cannot approach uniformity on the joint powerful modulus because it has only `R^{o(1)}` atoms inside a group whose size is polynomially larger than `R`.

Signed COS remains useful, but its role changes:

\[
\boxed{
\text{exact compression and leaf extraction, not uniform mixing.}
}
\]

## 4. Exact shift-Krylov rank

Let `T` denote cyclic shift in transform space and set

\[
S_d=
\begin{bmatrix}
m&Tm&\cdots&T^dm
\end{bmatrix}.
\]

For `x in E`, write

\[
\alpha_x=e^{2\pi ix/n}.
\]

Then

\[
m(k+j)
=
\sum_{x\in E}
\frac{N(x)}M
\alpha_x^k\alpha_x^j.
\]

Hence

\[
S_d=UV_d,
\]

where

\[
U_{k,x}=\frac{N(x)}M\alpha_x^k
\]

and

\[
(V_d)_{x,j}=\alpha_x^j.
\]

The columns of `U` are independent Fourier columns. The matrix `V_d` is a Vandermonde matrix on distinct roots.

Therefore

\[
\boxed{
\operatorname{rank}S_d
=
\min\{r,d+1\}.
}
\]

This removes one possible ambiguity from the SVD route.

There is no hidden exact rank collapse before degree `r`. Small singular values at lower degree measure conditioning and approximate algebraic structure, not exact innovation reduction.

## 5. Prony reconstruction theorem

Define the occupied-residue polynomial

\[
A(z)=\prod_{x\in E}(z-\alpha_x)
=
\sum_{j=0}^{r}a_jz^j.
\]

Because `A(alpha_x)=0` for every occupied residue,

\[
\begin{aligned}
\sum_{j=0}^{r}a_jm(k+j)
&=
\sum_{x\in E}\frac{N(x)}M\alpha_x^k
\sum_{j=0}^{r}a_j\alpha_x^j\\
&=0.
\end{aligned}
\]

Thus the transform satisfies the exact recurrence

\[
\boxed{
\sum_{j=0}^{r}a_jm(k+j)=0
\qquad
\text{for every }k.
}
\]

The first `2r` consecutive transform samples determine the minimal recurrence through a Hankel nullspace. Its roots recover the occupied residues, and a Vandermonde solve recovers the multiplicities.

## Sparse-Prony theorem

The complete arithmetic assignment distribution is determined by `2r` consecutive characteristic samples.

Since

\[
r\le M=3^s
\]

and

\[
3^{\omega(R)}=R^{o(1)},
\]

we obtain

\[
\boxed{
2r=R^{o(1)}.
}
\]

So the entire joint radical-assignment signal has subpolynomial spectral sampling complexity.

This is a genuine compression theorem. It does not yet control the height of an occupied target.

## 6. Exact Christoffel limit

The collision Gramian satisfies

\[
c^*G_dc
=
\frac n{M^2}
\sum_{x\in E}N(x)^2|P(\alpha_x)|^2.
\]

If the target `h` is absent, degree `r` permits a polynomial vanishing on all occupied residues while taking value one at the target. Therefore

\[
\lambda_r(h)=0.
\]

If the target is present, degree `r-1` permits the Lagrange filter that is one at `h` and zero at every other occupied residue. Therefore

\[
\boxed{
\lambda_{r-1}(h)
=
\frac n{M^2}N(h)^2.
}
\]

The Christoffel-COS bound becomes exact:

\[
\frac M{\sqrt n}\sqrt{\lambda_{r-1}(h)}
=N(h).
\]

This proves that the Christoffel hierarchy has no unresolved asymptotic issue. Its only challenge is reaching or approximating the innovation degree without unstable coefficient growth.

## 7. Galois balancing of the target filter

Suppose the target is occupied. Its Lagrange denominator is

\[
\Delta_h(E)
=
\prod_{x\in E\setminus\{h\}}
(\alpha_h-\alpha_x).
\]

This is a nonzero algebraic integer in the cyclotomic field.

For a unit `u modulo n`, the Galois automorphism sends

\[
\alpha_x\longmapsto\alpha_{ux}.
\]

Hence

\[
\sigma_u(\Delta_h(E))
=
\Delta_{uh}(uE).
\]

The product over all Galois embeddings is the absolute norm of a nonzero algebraic integer, so

\[
\prod_{u\in(\mathbb Z/n\mathbb Z)^\times}
|\Delta_{uh}(uE)|
\ge1.
\]

Therefore some unit coordinate satisfies

\[
\boxed{
|\Delta_{uh}(uE)|\ge1.
}
\]

This is the Galois-balancing theorem.

It says that a catastrophically ill-conditioned target filter in one logarithmic coordinate is never intrinsic. At least one Galois reindexing removes the small interpolation denominator.

The normalized numerator polynomial has coefficient `l1` norm at most `2^{r-1}`, so in the balanced coordinate the exact target filter satisfies

\[
\boxed{
\|c\|_1\le2^{r-1}.
}
\]

This is useful for exact and high-precision reconstruction. It is not yet a subpolynomial coefficient-height theorem because `2^r` can still be too large when `r=R^{o(1)}`.

## 8. Numerical consequences

The finite computations support the exact theorems.

### Reyssat `3^9` channel

\[
n=13122,
\qquad
M=r=9.
\]

The exact nontrivial Fourier energy is

\[
1457,
\]

which equals the sparsity lower bound

\[
\frac nr-1=1457.
\]

Thus the nine assignments occupy nine distinct residues and attain the minimum energy possible for a nine-point measure.

The original target interpolation log-discriminant is approximately

\[
-11.4075.
\]

After Galois balancing, it rises to approximately

\[
3.3764.
\]

### Reyssat `23^4` channel

\[
n=267674,
\qquad
M=r=9.
\]

The exact nontrivial energy is

\[
29740.5555\ldots,
\]

again equal to

\[
\frac nr-1.
\]

The target filter is already reasonably conditioned in the original coordinate, and the best Galois coordinate improves it further.

### Synthetic `3^9` sequence

The observed transition between eight and ten support primes occurs near

\[
3^s\approx n.
\]

At eight primes,

\[
M=6561<n=13122.
\]

At ten primes,

\[
M=59049>n.
\]

The change in periodogram behavior is therefore an entropy-saturation transition, not evidence that strong `abc` candidates should mix.

## 9. Revised canonical direction

The expanding-spectrum branch is now closed as a universal finishing mechanism.

A hypothetical strong exception lives in the opposite regime:

\[
\boxed{
\text{few assignment atoms inside an enormous powerful-modulus group.}
}
\]

The correct pipeline is now

\[
\boxed{
\begin{aligned}
&\text{signed COS samples}\\
&\longrightarrow\text{Prony annihilator}\\
&\longrightarrow\text{exact occupied residue set}\\
&\longrightarrow\text{target assignment}\\
&\longrightarrow\text{p-adic logarithmic or }S\text{-unit leaf}.
\end{aligned}
}
\]

The remaining pointwise theorem is not a spectral mixing theorem.

It is an arithmetic height theorem for the sparse leaf recovered by the spectrum.

In concrete terms, the next target is:

> Given the subpolynomial-size Prony representation of an admissible target assignment across all dyadic and odd-adic powerful channels, bound the height of that assignment by `R^{1+epsilon}`, or classify the resulting signed logarithmic leaf by an effective `S`-unit, norm-form, Hensel, generalized-Fermat, or Thue-Mahler argument.

That is the narrowest valid endpoint reached by the COS direction so far.
