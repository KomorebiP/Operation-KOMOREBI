# Hilbert 12 ambient dual slice: reading note

**Working mathematical note · Focused review: 27 October 2026**

The [original note](../../research/hilbert12-ambient-dual-slice/H12_Ambient_Dual_Slice_Research_Note.md) contains substantive finite algebra despite having only two files. Its analytic comparison remains open. Lean is not needed to state or check these elementary finite identities; the note's whole analytic argument has not been certified by this review.

## Make the Gauss-cube specialization explicit

Section 3 defines a cubic character by

$$
(\chi(1),\ldots,\chi(6))=(1,\omega,\omega^2,\omega^2,\omega,1),
\qquad \omega^2+\omega+1=0,
\qquad J=2+3\omega.
$$

For a nonzero residue $r$ modulo seven, put

$$
g_r(z)=\sum_{k=1}^6\chi(k)z^{rk},
\qquad G_r=g_r(\zeta_7),
$$

where exponents of $z$ are reduced modulo seven and $\zeta_7$ is a primitive seventh root of unity. The original checker obtains the coefficient vector $(6J,-J,-J,-J,-J,-J,-J)$ in the cyclic group ring. Thus the exact intermediate identity is

$$
g_r(z)^3=7J-J\Phi_7(z),
\qquad \Phi_7(z)=1+z+\cdots+z^6,
\qquad z^7=1.
$$

After specializing to $z=\zeta_7$, the relation $\Phi_7(\zeta_7)=0$ gives $G_r^3=7J$. The scalar identity is **not** an identity in the larger ring with only $z^7=1$: evaluation at $z=1$ gives zero on the left, while $7J$ is nonzero. The original code already retains the correction term; this note makes the passage between the two rings explicit.

The new exact check covers all six nonzero residue classes. It neither selects a cube-root branch nor identifies an elliptic-gamma value with an algebraic one. The inherited divisor theorem, analytic period carries, and normalized special-value comparison require their own evidence.

## Review boundary

The [focused review](../SOUNDNESS_REVIEW_2026-10-27.md) records this clarification, the finite fixed-vector check, and the limited review provenance. The original source and its historical evidence remain intact. The work remains in active development with the existing completion and confidence labels.

[Original checker](../../research/hilbert12-ambient-dual-slice/h12_ambient_dual_slice_verify.py) · [Recorded run](../../verification/audits/soundness-2026-10-27/run/manifest.json) · [Research index](../../research/README.md)
