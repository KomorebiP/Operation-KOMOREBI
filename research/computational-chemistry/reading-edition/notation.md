# Notation, units and reading routes

**Komorebi P. · Reader's guide · 13 November 2026**

The starting point is a finite matrix problem. A Hamiltonian tells us how
an electronic state changes. Here an oracle returns its complete action
on a chosen state vector. Known integral symmetries constrain the possible
Hamiltonians, making recovery from a small number of actions possible.

## Choose a route

| Goal | Read next |
|---|---|
| Understand the model and its 21 parameters | [Normal form](normal-form.md) |
| Inspect the exact probes, proof and error bounds | [Three-query recovery](three-queries.md) |
| Understand the comparison with spin information | [Exact response separation](spin-comparison.md) |
| Identify the molecular input and measured errors | [Declared H10-derived model](frozen-core.md) |
| Relate a reduced calculation to a full model | [Conditional model-error bridge](model-error.md) |
| Run the code and inspect certificates | [Replay guide](reproduce.md) |
| Check review coverage and remaining obligations | [Review report](review.md) |
| Check attribution and the limits of the novelty search | [Sources](literature.md) |

## Symbols used across the notes

| Symbol | Meaning and size |
|---|---|
| $h$ | Real symmetric 3-by-3 one-electron input matrix. |
| $g_{pqrs}$ | Real two-electron integrals in chemists' notation, with eightfold pair symmetry. |
| $H$ | A 9-by-9 Hamiltonian in the determinant basis, except in the full-model bridge, where its larger target space is explicitly defined. |
| $X$ | A 3-by-3 array representing alpha-hole and beta-electron coordinates. |
| $U_h$ | Orthogonal signed permutation from row-vectorized $X$ to determinant coordinates. |
| $t,K,C$ | The unique normal-form parameters: scalar $t$, traceless symmetric 3-by-3 $K$, and symmetric 5-by-5 $C$. |
| $T_a$ | Five fixed traceless symmetric 3-by-3 basis matrices. |
| $V$ | The fixed 9-by-3 raw probe matrix; $V^{\mathsf T}V=3I_3$. |
| $Y$ | The observed 9-by-3 action cache, in the same row and probe order as $V$. |
| $M$ | The 27-by-21 linear coefficient map for the three actions. |
| $G,B$ | The 21-by-21 operator and action Gram matrices. The code's action Gram field is named `K`; it is not the one-body parameter. |
| $\epsilon,d,r_H$ | Aggregate raw action-error cap, least-squares residual norm, and a sufficient Hamiltonian-error radius. |
| $b,\widehat b,\delta$ | True real source, observed real source, and their Euclidean error cap. |
| $E,\eta,z$ | Real evaluation energy, positive broadening, and $z=E+i\eta$. |
| $g,\widehat g,R_g$ | Complex source responses and a certified disk radius. In these expressions $g$ is a scalar response, not the four-index integral tensor. |
| $\rho_b,\ell_b$ | Broadened source-resolved density and its pi-scaled value: $\ell_b=\pi\rho_b=-\operatorname{Im}(g)$. |

The response symbol $g$ and the integral symbol $g_{pqrs}$ are distinguished
by their indices and context. Hats denote estimates or observed sources;
they do not imply a physically admissible integral decomposition.

## Norms and positivity

For a vector, $\|x\|$ is its Euclidean norm. For a matrix,
$\|A\|_F=\sqrt{\sum_{i,j}|A_{ij}|^2}$ is the Frobenius norm, while
$\|A\|_2$ is the induced operator norm. They are different, and
$\|A\|_2\le\|A\|_F$ is used in the response bound.

A real symmetric matrix is **positive semidefinite**, written $C\succeq0$,
when $x^{\mathsf T}Cx\ge0$ for every real $x$. Positive definite,
written $C\succ0$, means strict inequality for every nonzero $x$.
“Not positive semidefinite” includes negative definite and indefinite
matrices; “indefinite” alone means that both signs occur.

A Gram matrix records inner products. Positive integral Gram tensors
provide a useful algebraic relaxation of physical Coulomb integrals.
Their positivity is not a proof of realization by actual common orbitals.
It also does not require the Hamiltonian itself to be positive semidefinite:
one-body terms and the energy origin remain unrestricted.

## Units and interpretation

With dimensionless state vectors and electronic energies in Hartree,
the Hamiltonian, action cache, action errors and broadening have energy
units. Responses and source-resolved densities have inverse-energy units.
Probe and source norms, and source-error caps, are dimensionless.

A **determinant** is an antisymmetric basis state with specified occupied
spin orbitals. A **Slater source** here is one exact determinant vector.
It is different from a vector obtained by annihilating an electron in an
approximate many-electron neutral state.

**Frozen core** means retaining a fixed occupation for selected orbitals
and projecting onto the remaining active configurations. Agreement of the
projected formula with a direct projection validates that finite model.
It does not show that the discarded configurations have no effect on the
full response.

The parameter $\eta>0$ smooths spectral poles. Its choice is part of the
evaluation problem; the estimates deteriorate as it decreases. None of
these notes asserts a zero-broadening limit.

## Accessible reading

The notes have a compact, keyboard-operable contents disclosure, labeled
tables and ordinary source/download links. Display equations and code
blocks can scroll horizontally without widening the page. Equations are
typeset with the site's MathJax accessibility support; the surrounding
prose defines the quantities and the probe matrix also has a text table.

Use **On this page** to jump within a note and **Explore the chemistry
notes** to choose another. These disclosures and the download links work
without JavaScript. Without the math renderer, TeX source remains visible;
it is not claimed to be fully typeset in that mode. The site's
[accessibility guidance](https://KomorebiP.github.io/Operation-KOMOREBI/collection/ACCESSIBILITY.html)
provides the reporting route for barriers. Automated browser checks do
not replace testing with real assistive technology.
