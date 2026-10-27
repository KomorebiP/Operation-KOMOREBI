# Source and Claim Map

## Single source object

`gibbs_projector_closed.py` contains the signal definition, closed Fourier coefficients, Gibbs asymptotic, edge functional, projectors, finite dictionary search, robustness studies, all figures and tables, KaTeX/LaTeX generation, PDF compilation, mathematical assertions, and release metadata.

## Exact mathematical layer

- closed Fourier coefficients of the degree-five smooth seed and interval mask;
- Dirichlet-kernel local scaling and the Gibbs constant;
- out-of-band edge-amplitude functional;
- complementary idempotent packet projectors;
- exact synthesis `Q_5 P_S + P_J = I` on the declared model space;
- finite dyadic interval selection and half-gap stability;
- exact endpoint/symmetric-difference perturbation equality;
- exact dyadic, polyphase, and Haar reconstructions.

## Numerical certificate layer

- finite partial-sum overshoot converging to the Gibbs constant;
- finite-grid projector residuals;
- sampled exact reconstruction;
- noise and endpoint perturbation studies;
- negative controls and model-mismatch residuals.

## Logical boundary

The construction circumvents Gibbs ringing by changing the representation: the discontinuity packet is retained exactly and only the smooth packet is passed through the finite Fourier projector. The classical global Fourier partial sum is not altered and still exhibits Gibbs behavior. The release does not claim that arbitrary discontinuities are automatically known, that one finite dictionary is universal, or that every oscillatory numerical artifact has been solved.
