# Exact Streaming Block / Packet / Polyphase Decomposition for SKAT

**Status:** formal research note, v0.1  
**Date:** 2026-09-23

## 1. Setup

Let

\[
G\in\mathbb R^{n\times m},
\qquad
W=\operatorname{diag}(w_1,\ldots,w_m),\quad w_j\ge0,
\]

and let \(Q_X\in\mathbb R^{n\times p}\) have orthonormal columns spanning
the null-model covariates.  Define

\[
M_X=I-Q_XQ_X^\top,
\qquad
A=M_XGW^{1/2},
\qquad
K=AA^\top=M_XGWG^\top M_X.
\]

Partition the variants into disjoint blocks

\[
\{1,\ldots,m\}=J_1\sqcup\cdots\sqcup J_B.
\]

Write \(G_b=G_{[:,J_b]}\), \(W_b=W_{J_b,J_b}\), and

\[
A_b=M_XG_bW_b^{1/2}.
\]

Then

\[
A=[A_1\ \cdots\ A_B].
\]

The purpose of the streaming formulation is to make the **device working
set depend on block sizes and Krylov width, not on total variant count \(m\)**.

---

## 2. Exact variant-block Gram theorem

### Theorem 2.1 — Additive block Gram identity

\[
\boxed{
K
=
AA^\top
=
\sum_{b=1}^B A_bA_b^\top.
}
\]

Equivalently,

\[
\boxed{
K
=
M_X
\left(
\sum_{b=1}^B G_bW_bG_b^\top
\right)
M_X.
}
\]

### Proof

Because \(A\) is the horizontal concatenation of the column blocks \(A_b\),

\[
AA^\top
=
[A_1\ \cdots\ A_B]
\begin{bmatrix}
A_1^\top\\
\vdots\\
A_B^\top
\end{bmatrix}
=
\sum_b A_bA_b^\top.
\]

The second identity follows from
\(A_b=M_XG_bW_b^{1/2}\) and \(M_X^\top=M_X=M_X^2\).

### Consequence

If an \(n\times n\) sample Gram matrix fits in the chosen accumulator
location, the full weighted SKAT kernel can be built exactly by streaming
one variant block at a time.  No \(n\times m\) factor needs to be resident.

---

## 3. Exact one-pass matrix-free sample action

### Theorem 3.1 — Streaming kernel action

For every block vector \(V\in\mathbb R^{n\times s}\),

\[
\boxed{
KV
=
M_X
\sum_{b=1}^B
G_bW_bG_b^\top
M_XV.
}
\]

Thus the exact action \(V\mapsto KV\) can be evaluated by:

1. \(U\leftarrow M_XV\);
2. \(Y\leftarrow0\);
3. for each variant block \(b\):
   \[
   T_b\leftarrow G_b^\top U,
   \qquad
   Y\leftarrow Y+G_b(W_bT_b);
   \]
4. return \(M_XY\).

### Proof

Substitute the additive identity of Theorem 2.1 into \(KV\) and use
associativity.

### Corollary 3.2 — Memory independence from \(m\)

If at most \(c\) variants are resident and the Krylov block has width \(s\),
the algebraic working set is

\[
O(nc+ns+cs+np),
\]

independent of total variant count \(m\).

Total arithmetic still scales with \(m\); **working memory does not**.

This is the central GPU out-of-core result.

---

## 4. Exact streamed factor actions

Block Golub--Kahan needs only the two actions \(AV\) and \(A^\top U\).

Partition \(V\in\mathbb R^{m\times s}\) conformally:

\[
V=
\begin{bmatrix}
V_1\\
\vdots\\
V_B
\end{bmatrix}.
\]

### Theorem 4.1 — Streaming \(AV\)

\[
\boxed{
AV
=
M_X\sum_{b=1}^B
G_bW_b^{1/2}V_b.
}
\]

Hence one pass over variant blocks suffices.

### Theorem 4.2 — Streaming \(A^\top U\)

For \(U\in\mathbb R^{n\times s}\),

\[
\boxed{
(A^\top U)_b
=
W_b^{1/2}G_b^\top M_XU.
}
\]

Each right-coordinate block can be produced and consumed independently.

### Corollary 4.3 — Streaming Golub--Kahan equivalence

Any exact-arithmetic algorithm whose only access to \(A\) is through
products \(AV\) and \(A^\top U\) produces **identical iterates** when these
products are replaced by Theorems 4.1 and 4.2.

Therefore factor-first block Golub--Kahan, restarted bidiagonalization,
and related matrix-free singular-spectrum algorithms inherit the same
mathematics without requiring \(A\) to fit on device.

---

## 5. Exact two-pass dual action

The variant-space normal operator is

\[
H=A^\top A.
\]

### Theorem 5.1 — Two-pass streamed dual action

For \(V\in\mathbb R^{m\times s}\),

\[
\boxed{
HV=A^\top(AV).
}
\]

Using Theorems 4.1 and 4.2 gives an exact two-pass algorithm:

- pass 1 over variants: form \(Y=AV\in\mathbb R^{n\times s}\);
- pass 2: emit the blocks
  \[
  (HV)_b=W_b^{1/2}G_b^\top M_XY.
  \]

The full \(m\times s\) right vector may live in host memory, pinned memory,
mapped storage, or another device.  Only one right block must be device-resident.

This is the natural form for **variant-space polyphase Krylov**.

---

## 6. Exact 2D sample/variant tiling

A variant block \(G_b\in\mathbb R^{n\times c}\) may itself be too large.
Partition samples into row tiles \(I_1,\ldots,I_R\).

Let

\[
H_b=G_bW_b^{1/2}.
\]

Residualization requires only the small core

\[
R_b=Q_X^\top H_b.
\]

### Theorem 6.1 — Two-pass residualized tile construction

The core can be accumulated by sample tiles:

\[
\boxed{
R_b=\sum_r Q_{X,I_r}^\top H_{b,I_r}.
}
\]

After \(R_b\) is known,

\[
\boxed{
A_{b,I_r}
=
H_{b,I_r}-Q_{X,I_r}R_b.
}
\]

Therefore every sample-Gram tile satisfies

\[
\boxed{
K_{I_r,I_s}
=
\sum_b
A_{b,I_r}A_{b,I_s}^\top.
}
\]

No complete \(G_b\), \(A_b\), or \(K\) is mathematically required in
working memory.

With sample tile height \(t\) and variant block width \(c\), the dominant
working set is

\[
O(tc+pc+t^2),
\]

again independent of \(n\) and \(m\) except through the chosen tile sizes
and backing-store passes.

---

## 7. Packet and phase decomposition

There are two useful packet notions and they should not be conflated.

### 7.1 Matrix packets

Group variants into declared phases

\[
\mathcal P_1,\ldots,\mathcal P_H
\]

such as LD blocks, windows, annotation groups, or frequency bands.

Define

\[
A_h=M_XG_{\mathcal P_h}W_{\mathcal P_h}^{1/2},
\qquad
K_h=A_hA_h^\top.
\]

Then

\[
\boxed{
K=\sum_{h=1}^H K_h.
}
\]

Each \(K_hV\) is itself streamable by subblocks.

### 7.2 Variant-space polyphase operator

Let

\[
H=A^\top A
\]

and let \(P_h\) project onto variant phase \(h\).

Define the exact phase-coupling graph by

\[
g\to h
\quad\Longleftrightarrow\quad
P_hHP_g\ne0.
\]

The previously established polyphase light-cone result states that after
\(k\) applications of \(H\), information starting in phase \(g\) can reach
only phases connected to \(g\) by transfer paths of length at most \(k\).

Because every \(HV\) is streamable by Theorem 5.1, **light-cone scheduling
and out-of-core execution compose exactly**.

Only active frontier phases need to be transferred to the device.

---

## 8. Streaming-polyphase composition theorem

### Theorem 8.1 — Exact memory-bounded polyphase Krylov

Assume an exact phase graph and an exact matrix-free Krylov algorithm for
\(H=A^\top A\).  At iteration \(k\), let \(\mathcal F_k\) denote the phases
inside the exact light cone of the current start packets.

Then the Krylov update can be evaluated exactly by streaming only variant
blocks contained in the active phase frontier \(\mathcal F_k\), together
with any phase blocks required to produce the corresponding \(A\)-action.

No phase outside the exact light cone can change the iteration at step \(k\).

### Interpretation

This combines two independent savings:

- **space:** only one variant subblock is device-resident;
- **time/I/O:** phases outside the exact frontier need not be visited.

The first saving holds for any partition.
The second requires exact zero couplings or an explicitly approximate
thresholded graph.

---

## 9. Phase-local rank allocation

If \(R\) is a newly generated Krylov residual and

\[
R_h=P_hR,
\]

then

\[
r_h=\operatorname{rank}(R_h)
\]

is the minimum exact number of basis directions required in phase \(h\).

Thus the working block width should be local:

\[
s_h=r_h,
\]

not a global worst-case width.

Combined with streaming, phase \(h\)'s device memory is governed by

\[
O(nc_h+n r_h+c_hr_h),
\]

rather than by a global \(O(nm)\) factor or a uniform phase width.

---

## 10. Low-rank inter-phase messages

If a phase coupling admits

\[
P_hHP_g=U_{hg}V_{hg}^\top
\]

of exact rank \(r_{hg}\), then its action is

\[
P_hHP_gx
=
U_{hg}(V_{hg}^\top x).
\]

Only the two interface factors need to be stored or transferred.

This can reduce communication even when the phase itself is large.

The earlier reference implementation showed a storage win but not a Python
wall-clock win; a fused/batched GPU kernel is the correct engineering target.

---

## 11. Exact QR-core update under streamed column additions

Suppose

\[
A=QR,
\qquad Q^\top Q=I,
\]

and a new variant block \(U\) is appended.

Compute

\[
C=Q^\top U,
\qquad
F=U-QC,
\qquad
F=Q_\perp R_\perp.
\]

Then

\[
[A,U]
=
[Q,Q_\perp]
\begin{pmatrix}
R&C\\
0&R_\perp
\end{pmatrix}.
\]

Therefore the updated nonzero spectrum is exactly the spectrum of the
small core Gram.

The projections \(Q^\top U\) and residual block \(F\) may themselves be
formed by streamed subblocks when \(U\) is too large for device memory.

---

## 12. Solver hierarchy

The resulting SKAT decomposition portfolio is:

| Structural regime | Exact representation |
|---|---|
| \(K\) fits | additive block-Gram accumulation |
| \(K\) does not fit / only matvecs needed | one-pass streamed \(KV\) |
| \(A\) does not fit | streamed \(AV\), \(A^\top U\) |
| neither \(A_b\) nor \(K\) tile fits | 2D sample/variant tiling |
| low numerical rank | block Golub--Kahan / range core |
| sparse phase graph | polyphase frontier Krylov |
| low-rank phase interfaces | compressed messages |
| overlapping windows / added variants | exact QR-core updates |
| final tail evaluation | spectral packets / K-COS |

The layers are composable rather than mutually exclusive.

---

## 13. Device-memory planning law

Let:

- \(c\): resident variant count,
- \(s\): Krylov block width,
- \(p\): covariate rank,
- \(d\): bytes per floating scalar.

Ignoring allocator/library workspace, an exact streamed sample-space action
has working memory of order

\[
\boxed{
d\,[nc+2ns+cs+np+O(ps+c)].
}
\]

The corresponding full factor alone costs

\[
d\,nm.
\]

Hence, for fixed \(n,p,s,c\),

\[
\frac{M_{\mathrm{stream}}}{M_{\mathrm{full\ factor}}}
=
O\!\left(\frac{c}{m}+\frac{s}{m}+\frac{p}{m}\right).
\]

As \(m\to\infty\), device memory remains bounded while full-factor storage
grows linearly.

This is the formal statement of the GPU-memory workaround.

---

## 14. Claim boundary

The following ingredients are classical numerical linear algebra:

- block matrix multiplication,
- Gram accumulation,
- out-of-core matvecs,
- Golub--Kahan/Lanczos,
- QR,
- low-rank factor application.

The research contribution should **not** be framed as inventing blocking.

The candidate Komorebi contribution is the resolved synthesis:

\[
\boxed{
\text{streamed exact factor actions}
+
\text{phase light cones}
+
\text{minimal phase rank}
+
\text{low-rank messages}
+
\text{exact update cores}
+
\text{deep-tail spectral packets}.
}
\]

The key conceptual point is that the storage decomposition, structural
polyphase decomposition, spectral compression, and tail compression are
different axes and can all be active simultaneously.

---

# v0.5 extension: certified approximate light cones

Let `P_h` be orthogonal phase projectors, define

\[
\rho(X)_g=\|P_gX\|_F,
\qquad
\mathcal B_{hg}=\|P_hHP_g\|_2.
\]

Then

\[
\rho(H^kX)\le\mathcal B^k\rho(X).
\]

If `H_0` retains a symmetric subset of complete phase blocks and
`B_0` is the corresponding transfer matrix, then

\[
\rho((H^k-H_0^k)X)
\le
(\mathcal B^k-\mathcal B_0^k)\rho(X).
\]

This gives a certified approximate light cone and extends to arbitrary finite
Krylov polynomials. See `APPROXIMATE_LIGHTCONE_THEOREM.tex` and
`PROOF_AUDIT_APPROXIMATE_LIGHTCONE.md` for the complete proof and boundary.
