# Sources, conventions and unresolved priority

**Komorebi P. · Reviewed reading edition · 13 November 2026**

This record separates known methods, checked convention translations and
unresolved priority. The internal proofs use finite-dimensional linear
algebra and fermionic anticommutation relations. No unavailable external
theorem is used to fill a load-bearing proof step.

## Matrix-vector recovery

Diana Halikias and Alex Townsend, *Structured matrix recovery from
matrix-vector products*, [arXiv:2212.09841v2](https://arxiv.org/html/2212.09841v2),
29 May 2023; *Numerical Linear Algebra with Applications* 31(1), e2531
(2024), [DOI 10.1002/nla.2531](https://doi.org/10.1002/nla.2531).

Definition 2 and Lemma 3, equation (1), give the parameter-count lower
bound $\lceil p/N\rceil$ for a linearly parameterized $N$-state family.
After the present dimension proof, this specializes to
$\lceil21/9\rceil=3$. That lower bound is a **formal corollary not stated**
for this particular family. The general recovery setup and least-squares
inversion are prior methods. The inspected source does not supply the
displayed molecular family or its specific probe/frame certificate:
**partial or adjacent result only** for that construction.

The Cornell primary record for Diana Halikias's 2025 dissertation,
[*Structured matrix recovery and approximation from matrix-vector products*](https://hdl.handle.net/1813/117505),
was inspected at metadata/abstract level. The full 269-page dissertation
was not reviewed. Its contents remain a priority-check target; no claim
that it omits this construction is made.

## Electronic operator and frozen-core conventions

The following official PySCF module sources were inspected as unversioned
web snapshots on the project review date. No release-specific source hash
is claimed for these external pages.

- [FCI `contract_2e`](https://pyscf.org/_modules/pyscf/fci/direct_spin1.html): its $E_{pq}E_{rs}$ identity includes the $\delta_{qr}E_{ps}$ contraction. The API's absorbed tensor differs from physical chemists' ERIs; the energy path absorbs the one-body part with factor $1/2$.
- [Integral `restore`](https://pyscf.org/_modules/pyscf/ao2mo/addons.html): chemists' notation, within-pair symmetry and pair-packed fourfold/eightfold storage agree with the declared input convention.
- [CAS `h1e_for_cas`](https://pyscf.org/_modules/pyscf/mcscf/casci.html): a doubled closed-shell core density contributes a potential to the active one-body matrix and a separate core energy. This project's electronic-energy convention omits the nuclear constant consistently.

The project translation is checked independently by exact ladder,
Jordan–Wigner and spin-free-product constructions. The source websites
may change; the internally defined operator and the saved computation
inputs remain pinned. The positivity of true Coulomb ERIs follows from
their nonnegative Coulomb self-energy form. A converse realization theorem
for arbitrary positive integral tensors is not used.

## A different tomography problem

Artur Czerwiński, *Minimal number of observables for quantum tomography of
systems with evolution given by double commutators*, *Quantum Studies:
Mathematics and Foundations* 4, 287–294 (2017),
[DOI 10.1007/s40509-017-0101-6](https://doi.org/10.1007/s40509-017-0101-6).

Its introductory setup, Theorem 1 and equations (5)–(9) reconstruct an
unknown initial density matrix under a known generator, using scalar
expectations over time. Our unknown is the operator, and the outputs are
complete action vectors. Its theorem is **inapplicable** as a proof of our
three-query statement, and **partial or adjacent result only** as background
for double-commutator notation.

Particle-hole duality, vectorization, double commutators, Choi reshuffling
and the resolvent identity are established tools. The new conditional
model-error note uses elementary resolvent algebra and makes no novelty
claim for that general argument.

## Search coverage and remaining obligation

The retained source record documents English web/arXiv searches using
chemistry, operator-recovery, particle-hole, Choi and double-commutator
vocabulary. The matrix-recovery references and the neighboring tomography
problem supplied a second search strategy. Exact source extraction and
manuscript translation were checked for the stated comparisons.

There was no comprehensive forward-citation search, MathSciNet or zbMATH
coverage, chemistry indexing database search, or exhaustive review of
unitary-group and active-space inverse-Hamiltonian literature. This editorial
review does not replace those missing searches. A failed search cannot
establish novelty.

The exact normal form, explicit minimum-count probe construction and
spin-preserving information-separation example are candidate contributions.
**Originality, priority and publication significance remain unestablished.**
The internal correctness review and replay results have a different scope
from that unresolved literature question.
