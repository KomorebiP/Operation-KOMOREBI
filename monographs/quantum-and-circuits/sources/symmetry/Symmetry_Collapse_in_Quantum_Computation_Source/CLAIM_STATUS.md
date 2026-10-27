# Theorem and evidence status

## Proved from the project records and reproduced in the monograph

- invariant quantum packet theorem;
- invariant-basis exact simulation theorem;
- polynomial packet-simulation theorem;
- fixed-charge polynomial-time corollaries;
- Hamiltonian and circuit leakage bounds;
- state, density-operator, measurement, and channel packet identities;
- compressed-representation simulation principle under declared hypotheses;
- exact and approximate time-dependent packet simulation theorems;
- moving-frame collapse under efficient frame access.

## Derived in the monograph

- permutation-symmetric qubit collapse to Dicke coordinates;
- fixed-local-dimension permutation-symmetric qudit collapse;
- polynomial orbit-quotient quantum-walk simulation;
- fixed-particle bosonic and fermionic polynomial-time simulation;
- hybrid packet/representation decision criterion;
- compiler and validation protocol for symmetry collapse;
- sparse reachable packet-graph collapse and bounded-excitation corollary;
- Schur-commutant collapse for fixed local dimension;
- qubit permutation-invariant density-operator compression to O(n^3) block parameters;
- particle-number scaling phase diagram from polynomial to exponential regimes.

## Recorded computation

- floating-point reconstruction of structurally exact weight-two packet/full-state dynamics;
- floating-point rank-two moving-frame reconstruction check;
- total-spin commutant parameter-count checks;
- exact-weight-two scaling benchmark;
- parity, modulo-four, half-filled, and symmetry-breaking control tables;
- finite Forrelation experiments used to illustrate global interference.

## Contextual external result

- order-six entangled quantum Latin realizations exist, while non-entangled mutually orthogonal quantum Latin squares of order six do not.

## Open

- universal efficiently discoverable packetization;
- representation-independent classical interference-compression lower bounds;
- guaranteed polynomial adaptive packet growth with efficiently accessible small discarded tails;
- efficient discovery of noncircular moving frames;
- efficient Schur-block compilation for broad permutation-covariant channels;
- broad hybrid Gaussian/tensor/stabilizer closure theorems;
- classification of the maximal quantum circuit families admitting symmetry-collapse simulation.

## Completion review

- The adaptive discarded-state certificate is proved in the written text. It gives global error accounting for unnormalized adaptive projection trajectories and does not assert polynomial retained size.
- Exact rational validation passes 308 assertions over 27 fixed-weight examples on one through six qubits, integer dimension checks through twelve qubits, and the two-step discarded-state example.
- Numerical reconstruction passes the declared 2e-12 tolerance, with maximum observed residual 2.532e-16. These are numerical checks, not exact arithmetic.
- Twenty-one boundary controls verify invalid-input rejection, strict support preservation, and complex-valued updates of real input states.
- No symmetry Lean formalization is supplied or claimed.
