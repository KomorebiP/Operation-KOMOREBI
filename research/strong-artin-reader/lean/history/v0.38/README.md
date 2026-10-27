# v0.38 — Effective noncommutative matrix lifting

The next matrix lifting block is Lean-checked **under an explicit, finite inverse-derivative certificate**. It applies when the power derivative has a certified inverse over Q_p, even if its reduction modulo p is singular. The finite test proves existence of a unique actual p-adic matrix root in a prescribed sufficiently deep residue class.

Strong Artin remains open. Derivatives singular over Q_p and general shallow resonant prefixes are not classified here.

Let p be prime, n>0, d>0, and A,U in GL_n(Z_p). Define the full matrix power derivative

\[
D_A(X)=\sum_{i=0}^{d-1}A^iXA^{d-1-i}.
\]

Supply s>=0 and an n²-by-n² matrix B over Z_p such that, as operators on Mat_n(Q_p),

\[
BD_A=D_AB=p^s I.
\]

The Lean certificate checks these identities on the matrix units; linearity extends them to all matrices. In particular Q=p^{-s}B is a genuine two-sided inverse. No commuting restriction is imposed on X.

For **m>s**, the main result is

\[
\boxed{\begin{aligned}
&\exists!F\in\mathrm{GL}_n(\mathbf Z_p),\quad F\equiv A\pmod{p^m},\quad F^d=U\\
&\qquad\Longleftrightarrow\qquad
B\,\operatorname{vec}(U-A^d)\equiv0\pmod{p^{m+s}}.
\end{aligned}}
\]

Here B acts on the vector of matrix entries; it is not ordinary n-by-n multiplication. Any consistent ordering of pairs of indices can be used. The executable examples use row-major order.

`matrix_unit_root_finite_iff` states the right-hand side using only reductions of A, U and B in the finite ring Z/(p^(m+s)). `matrix_power_unique_iff` covers arbitrary integral matrix targets. The finite condition is necessary and sufficient; it does not assume successful lifting at every depth.

The inverse certificate itself is an exact algebraic input. This release does not give a terminating certificate-discovery procedure for arbitrary black-box p-adic inputs, or formalize automatic inversion from a determinant hypothesis. The supplied exact-rational generator computes and checks certificates for 2-by-2 rational/integer centers.

## Resonant, noncommuting control

Over Z_2 let

\[
A=\begin{pmatrix}1&1\\0&1\end{pmatrix},\qquad
B=\begin{pmatrix}
2&0&-1&0\\-1&2&1&-1\\0&0&2&0\\0&0&-1&2
\end{pmatrix}.
\]

Lean verifies BD_A=D_AB=4I for the square map. Thus s=2, and m=3 gives an exact test modulo 32 for roots congruent to A modulo 8. The derivative modulo 2 has the nonzero identity matrix in its kernel, so the earlier bijective-residual-derivative criterion does not apply.

Lean checks

\[
F=\begin{pmatrix}1&1\\8&1\end{pmatrix},\qquad
F^2=\begin{pmatrix}9&2\\16&9\end{pmatrix},\qquad AF\ne FA.
\]

It also proves that U_bad=[[1,10],[0,1]] has no square root congruent to A modulo 8. Its mismatch is 8E_12 and B vec(U_bad-A²)=(0,16,0,0), which fails the modulo-32 test. Thus residual compatibility alone is insufficient even in this certified sector.

## Evidence and continuation

Read PROOF.md for the argument and exact hypotheses, PROOF_LEDGER.md for evidence, SELF_REVIEW.md for the audit, and RESEARCH_BOUNDARY.md before continuing. `src/` contains seven new Lean modules. `base/` preserves the exact v0.37 checkpoint, including its historical parent.

Replay with the pinned portable Lean kit:

```sh
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier rebuilds all new-source dependencies and audits every named new declaration. It reuses the pinned Mathlib cache and authenticates, rather than recompiles, the historical checkpoint.
