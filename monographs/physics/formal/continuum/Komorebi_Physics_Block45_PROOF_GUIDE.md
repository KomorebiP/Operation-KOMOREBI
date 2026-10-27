# Block 45 proof guide

## Objective

Upgrade fixed-time finite-cutoff convergence to one quadratic error envelope valid for all times in a compact interval, then isolate the exact stability inequality needed for cutoff removal.

## 1. Closed-ball exponential estimate

The four-spinor endomorphism algebra is finite dimensional. The Banach-algebra exponential is analytic, its Fréchet derivative is continuous, and every closed operator-norm ball is compact. The derivative norm therefore has a finite maximum on the ball. The mean-value theorem gives a Lipschitz constant on that ball.

## 2. Hilbert generator residual

The mass term cancels exactly. The remaining residual is the sum of the three sine-quotient errors times fixed Clifford operators. Each scalar sine-quotient residual is `O(h²)`, so their finite operator sum is `O(h²)`.

## 3. Compact time window

For `|t| ≤ T`, convergence of the lattice Hamiltonian gives one eventual operator ball containing both `-it H_h` and `-it H`. The closed-ball Lipschitz theorem then converts the generator residual into a propagator residual with one constant independent of `t` throughout the window.

## 4. Finite packet

Choose one mode constant for each mode in the fixed finite support. Finite eventual intersection makes all mode estimates hold simultaneously. Mode embedding is isometric, and the operator norm controls action on the fixed amplitude. Summing the finitely many bounds yields one packet constant.

## 5. Cutoff removal inequality

For norm-preserving linear evolutions `U_h(t)` and `U(t)`, insert a finite approximation `g`:

```text
U_h(t)f - U(t)f
= U_h(t)(f-g)
  + (U_h(t)g-U(t)g)
  + U(t)(g-f).
```

Exact norm preservation makes the two tail terms equal to `‖f-g‖`, producing the coefficient two.

## Boundary

The block proves a compact-time envelope, not the sharp self-adjoint Duhamel constant. It does not yet construct the full Fourier-diagonal propagators on all torus `L²` or instantiate the two-tail theorem to remove the cutoff.
