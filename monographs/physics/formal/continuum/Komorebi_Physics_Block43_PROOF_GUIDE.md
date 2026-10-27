# Block 43 proof guide

## 1. Bounded mode operators

The explicit Clifford actions `αx`, `αy`, `αz`, and `β` are packaged as continuous linear endomorphisms of the finite four-spinor space. The continuum and central-difference mode generators are their real-coefficient linear combinations.

The mass terms agree exactly. The generator difference is therefore the sum of the three sine-quotient residuals multiplied by fixed Clifford operators. The existing scalar estimate

\[
\frac{\sin(kh)}h-k=O(h^2)
\]

passes through continuous scalar multiplication, giving operator-norm `O(h²)` convergence.

## 2. Exponential evolution

For fixed time `t`, the exponent is

\[
-itH.
\]

The endomorphism algebra is a complete normed algebra. The exponential is defined by the Banach-algebra power series. Its analyticity gives a local `O(A-A₀)` estimate, so composition with the generator estimate yields

\[
\exp(-itH_h)-\exp(-itH)=O(h^2)
\]

in operator norm.

## 3. Exact group identities

Scalar multiples of one fixed generator commute. Hence `exp_add_of_commute` proves

\[
U(s+t)=U(s)U(t),
\qquad U(0)=I,
\qquad U(-t)U(t)=I.
\]

These are algebraic exponential identities. Hilbert norm preservation is intentionally not claimed in this block.

## 4. Fourier packet assembly

Evaluation at a fixed spinor, the algebraic-to-Hilbert spinor map, and one-mode torus embedding are continuous linear maps. The operator estimate therefore transfers to each embedded mode.

For fixed finite support, exact Fourier orthogonality gives the residual Parseval identity. Finite summation then produces the packet `O(h²)` theorem and strong `L²` convergence.
