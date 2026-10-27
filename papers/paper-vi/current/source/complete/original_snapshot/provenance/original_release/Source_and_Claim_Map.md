# Source and Claim Map

## Paper

**Projector-Resolved Seed Calculus VI: Transfer Semigroups — Stochastic, Bayesian, Fractional, and PDE Realizations**  
**Author:** Komorebi P.

The individual paper contains no local bibliography or citation commands. External references for the collected series remain in the separate series ledger.

## Internal theorems proved in the paper

- exact packet reconstruction of finite semigroups;
- packet block-convolution law;
- reducing-packet theorem;
- finite-dimensional Laplace-resolvent formula;
- exact generator intertwining and its semigroup consequence;
- Duhamel refinement-defect identity and norm bound;
- exact Markov lumping and the discrete telescoping defect formula;
- finite conditional-expectation projector and nested tower laws;
- orthogonal martingale-difference packet decomposition;
- Bayesian packet evidence and exact posterior reconstruction;
- necessary and sufficient finite Bayesian refinement criterion;
- exact information-loss-packet factorization and norm certificate;
- canonical coarsest partition sufficient for a finite likelihood family;
- multiplicative Bayesian composition;
- nonlinear Bayesian semigroup and replicator generator;
- elementary Bayesian stability bound;
- finite-dimensional spectral fractional semigroup theorem;
- square-root subordination by spectral reduction;
- exact fractional intertwining resolvent formula for bounded nonnegative self-adjoint refinement systems;
- gap-free Holder and common-gap linear certificates for fractional refinement defects;
- fractional-semigroup Duhamel identity and summable-tower corollary;
- exact nodal Green identity for the one-dimensional Dirichlet second-difference operator;
- second-order low-mode eigenvalue bound;
- finite-state Feynman-Kac formula;
- Schur-Feshbach projected-resolvent identity;
- exact retained-state memory equation and memory-kernel Laplace transform;
- finite survival, density, and hazard identities.

## Classical inputs reorganized in the common operator language

- Markov semigroups and random walks;
- exact Markov lumpability;
- conditional expectation and martingale differences;
- Ornstein-Uhlenbeck/Hermite spectral modes;
- conjugate Beta-binomial updating;
- hidden Markov filtering;
- spectral fractional powers;
- Green and heat operators;
- Feynman-Kac transfer;
- Schur complements and Feshbach elimination;
- survival and hazard functions.

Its programmatic contribution is the exact placement of these ingredients inside one seed, packet, transfer, refinement, defect, and reconstruction language.

## Numerical certificates

The release records CPU calculations for:

- packet-semigroup block convolution;
- exact and perturbed Markov lumping;
- Bayesian composition, packet reconstruction, and flow differentiation;
- conditional-expectation towers and Hermite orthogonality;
- fractional semigroup composition and scalar subordination;
- fractional intertwining, gap-free and common-gap certificates, and fractional-semigroup refinement;
- exact nodal Green reconstruction and low-mode convergence;
- finite path enumeration for Feynman-Kac transfer;
- Feshbach and memory-kernel Laplace identities;
- exact and defective semigroup refinement;
- hidden Markov normalization;
- survival monotonicity and nonnegative hazard.

These calculations support the finite statements and implementation. They do not prove the continuum conjectures.

## Conjectural statements

- transfer-semigroup realization on completed infinite-dimensional spaces;
- uniform refinement control for unbounded generator towers;
- latent-packet closure and finite realization of limiting memory kernels.

## Boundaries

- A partition is not automatically Markov-lumpable.
- Bayesian update remains nonlinear even though exponential likelihoods form a semigroup.  Its finite all-prior coarsening law is now characterized exactly; infinite disintegration and asymptotic sufficiency remain separate.
- Spectral fractional powers need not be local.  Fractional naturality is proved here only for bounded nonnegative self-adjoint refinement systems; unbounded and nonnormal cases require separate domain and resolvent hypotheses.
- The exact nodal Green identity is specific to the stated one-dimensional second-difference model.
- Exact hidden-state elimination generally produces memory rather than a local Markov generator.
- No GPU benchmark is reported in Paper VI.
