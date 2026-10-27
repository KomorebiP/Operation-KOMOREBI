# Threshold-free Euler congruences and optimal dyadic periods

For a power-of-two rank \(N=2^a\) and an address \(0\le j<N\), define the normalized reciprocal coefficients by
\[
C_{N,j}(n)
=(Nn)!\,[t^{Nn}]
\left(j!\sum_{m\ge0}\frac{t^{Nm}}{(Nm+j)!}\right)^{-1},
\qquad n\ge0.
\]
Thus \(C_{N,j}(0)=1\). The original generalized Euler coefficients are
\[
E_{Nn}^{(N,j)}=j!\,C_{N,j}(n).
\]
Write \(v_2\) for the dyadic valuation, with \(v_2(0)=+\infty\), and let
\[
\Delta_u F(n)=F(n+u)-F(n).
\]

## 1. All rows, all orders, all power-of-two ranks

For every \(N=2^a\), every \(0\le j<N\), and every \(n\ge0\), \(k\ge1\), and \(u\ge1\),
\[
\boxed{
 v_2\!\left(\Delta_u^k C_{N,j}(n)\right)
 \ge k\bigl(1+v_2(u)\bigr).
}
\]
Consequently,
\[
 v_2\!\left(\Delta_u^k E_{Nn}^{(N,j)}\right)
 \ge k\bigl(1+v_2(u)\bigr)+v_2(j!).
\]
In the second formula, the difference operator acts on the row variable \(n\). These bounds have no starting-row restriction.

## 2. Exact difference valuations at ranks two, four, and eight

For every lane at \(N\in\{2,4,8\}\), there is a constant \(b_{N,j}\) such that, for every \(n\ge0\) and \(H\ge1\),
\[
\boxed{
 v_2\!\left(C_{N,j}(n+H)-C_{N,j}(n)\right)
 =v_2(H)+b_{N,j}.
}
\]
For the original coefficients, put \(B_{N,j}=b_{N,j}+v_2(j!)\). Then
\[
\boxed{
 v_2\!\left(E_{N(n+H)}^{(N,j)}-E_{Nn}^{(N,j)}\right)
 =v_2(H)+B_{N,j}.
}
\]
The entries below are ordered by \(j=0,1,\ldots,N-1\).

| Rank \(N\) | Normalized shifts \(b_{N,j}\) | Original Euler shifts \(B_{N,j}\) |
|---|---|---|
| \(2\) | \(1,2\) | \(1,2\) |
| \(4\) | \(1,1,4,2\) | \(1,1,5,3\) |
| \(8\) | \(1,1,1,1,4,3,2,2\) | \(1,1,2,2,7,6,6,6\) |

### Optimal periods

For every precision \(r\ge1\), the least positive row period of the original coefficients modulo \(2^r\) is exactly
\[
\boxed{
 P_{N,j}(r)=2^{\max(0,r-B_{N,j})}.
}
\]
It holds from row zero and cannot be shortened. In the actual Euler subscript, the corresponding shift is \(NP_{N,j}(r)\); at rank four it is \(4P_{4,j}(r)\).

When \(r>B_{N,j}\), the rows \(0\le n<P_{N,j}(r)\) enumerate every residue in
\[
 j!+2^{B_{N,j}}\mathbb Z/2^r\mathbb Z
\]
exactly once. When \(r\le B_{N,j}\), there is one residue and the least row period is one.

### Dyadic interpolation and exact image

The Newton series
\[
 \widetilde C_{N,j}(x)
 =\sum_{k\ge0}\Delta_1^k C_{N,j}(0)\binom{x}{k}
\]
converges uniformly on \(\mathbb Z_2\), giving a continuous interpolation. For the lanes in the table, it satisfies
\[
 v_2\!\left(\widetilde C_{N,j}(x)-\widetilde C_{N,j}(y)\right)
 =v_2(x-y)+b_{N,j}
 \qquad(x\ne y).
\]
Therefore
\[
 x\longmapsto
 \frac{\widetilde C_{N,j}(x)-1}{2^{b_{N,j}}}
\]
is a bijective isometry of \(\mathbb Z_2\). In particular, the exact interpolation images are
\[
 \widetilde C_{N,j}(\mathbb Z_2)=1+2^{b_{N,j}}\mathbb Z_2,
 \qquad
 j!\widetilde C_{N,j}(\mathbb Z_2)=j!+2^{B_{N,j}}\mathbb Z_2.
\]

## 3. An infinite family of exact laws at every larger rank

For every \(N=2^a\ge4\) and every lower-half address \(0\le j<N/2\),
\[
\boxed{
 v_2\!\left(C_{N,j}(n+H)-C_{N,j}(n)\right)=v_2(H)+1
 \qquad(n\ge0,\ H\ge1).
}
\]
All the period and interpolation conclusions above apply with
\[
 b_{N,j}=1,
 \qquad B_{N,j}=1+v_2(j!).
\]
Thus these normalized interpolations biject \(\mathbb Z_2\) onto \(1+2\mathbb Z_2\).

## 4. Boundary of the exact law

The uniform higher-difference lower bound applies to every address at every power-of-two rank. The stronger exact metric law does not automatically extend to every upper-half address. Exact rational calculations give:

| \((N,j)\) | \(v_2(C_{N,j}(1)-C_{N,j}(0))\) | \(v_2(C_{N,j}(2)-C_{N,j}(0))\) | Prediction from the naive exact law |
|---|---:|---:|---:|
| \((16,9)\) | \(5\) | \(7\) | \(6\) |
| \((32,18)\) | \(6\) | \(6\) | \(7\) |
| \((32,19)\) | \(5\) | \(7\) | \(6\) |

These are failures of that additional exact-law proposal. They preserve the universal lower bound and the proved conjecture.

## Proof dependencies and validation

The universal bound follows from the power-of-two Hurwitz reciprocal theorem. The exact laws follow from its bound
\(v_2(\Delta_1^k C_{N,j}(0))\ge k\), together with finitely many exact Newton coefficients. The criterion is
\[
 v_2(a_1)=b,
 \qquad
 v_2(a_k)\ge b+1+\lfloor\log_2 k\rfloor
 \quad(k\ge2),
\]
where \(a_k=\Delta_1^k C(0)\). The generic bound covers every remaining order after the finitely checked orders. Vandermonde's identity then gives every higher Newton term a valuation at least one greater than that of the leading first-difference term.

The proofs and exact coefficient verifiers are recorded in [SHARP_PERIOD_LEMMA.md](SHARP_PERIOD_LEMMA.md), [low_mahler_verified.json](low_mahler_verified.json), and [all_rank_extensions_verified.json](all_rank_extensions_verified.json). Mathematical audits and exact computations support these claims. No new Lean compilation is claimed. These theorems concern Euler congruences; the separate universal simplicity problem for Euler-tail residuals remains open.
