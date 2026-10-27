# Ground Hermite channel and preservation of the RH front

Let
\[
g_{s,c}(u)=(2\pi s)^{-1/4}\exp\!\left(-\frac{(u-c)^2}{4s}\right),
\qquad s>0.
\]
For every complex \(z\), direct completion of the square gives
\[
\int_{\mathbb R} g_{s,c}(u)e^{uz}\,du
=
K_s e^{cz+s z^2},
\qquad
K_s=2\sqrt{\pi s}(2\pi s)^{-1/4}.
\]

Consequently, for the pole-free zero heat packet
\[
\widetilde\Theta_t(u)
=
\sum_\rho \rho(1-\rho)
 e^{t(\rho-1/2)^2+u(\rho-1/2)},
\]
normal convergence permits the formal identity
\[
\boxed{
\langle \widetilde\Theta_t,g_{s,c}\rangle
=
K_s\widetilde\Theta_{t+s}(c).
}
\]
The ground Hermite coefficient is therefore another copy of the same zero heat
field, evaluated at a later positive heat time.  It has the same horizontal
zero front.

This has two consequences.

1. Stable Hermite compression fixes the conditioning of the physical carrier.
2. It cannot, by itself, supply the missing arithmetic contraction: its lowest
   coefficient still contains the full RH obstruction.

Higher Hermite coefficients are obtained by polynomial differential operations
on the same heat field.  They do not remove the ground channel.

This identity is an analytic derivation, not a Lean-certified theorem in the
present bundle.
