# Source and Claim Map

## Scope

Paper V is the signal-processing realization of the common calculus developed in Papers I-III. It does not redefine seed rank, the general weighted transfer calculus, nonlinear packet coordinates, obstruction packets, or holonomy. It instantiates those objects using impulses, shifts, residue projectors, filter transfer matrices, wavelet addresses, edge packets, and reflection-coefficient coordinates.

The paper contains no local bibliography. Historical comparison and priority review remain in the separate series reference ledger.

## Internally proved statements

### Signal seed and polyphase coordinates

- the impulse orbit spans finitely supported sequences and is dense in the stated sequence completions;
- residue projectors are idempotent, disjoint, and complete;
- polyphase analysis followed by synthesis is the identity;
- coarse residue packets are exact sums of their fine descendants.

Implementation: `projector_signal/polyphase.py`  
Tests: `tests/test_polyphase.py`, `tests/test_additional.py`

### FIR transfer law

For an FIR filter, the packet kernels

```text
h_ks[m] = h[Nm + k - s]
```

reconstruct the exact filtered output through packet convolution. No approximation is introduced by the coordinate transformation.

Implementation: `projector_signal/polyphase.py`  
Tests: `tests/test_polyphase.py`

### Perfect-reconstruction filter banks

- the matrix condition `R(z)E(z)=z^{-d}I` is sufficient and necessary for exact delayed reconstruction in the stated finite filter-bank setting;
- Haar analysis and synthesis reconstruct exactly;
- the Haar energy identity holds;
- the stated predict-update lifting step is exactly invertible;
- finite Haar packet trees reconstruct exactly and conserve energy.

Implementation: `projector_signal/filterbanks.py`  
Tests: `tests/test_filterbanks.py`, `tests/test_additional.py`

### Known-edge theorem

If a signal is decomposed as

```text
f = s + j
```

and the jump packet `j` is retained exactly while only `s` is approximated, then

```text
f - (Q_m s + j) = s - Q_m s.
```

The theorem extends to a finite sum of exact discontinuity packets. This is a conditional reconstruction theorem; it does not solve packet discovery.

Implementation: `projector_signal/edges.py`  
Tests: `tests/test_edges.py`

### Packet perturbation bound

The paper proves the stated estimate separating amplitude mismatch from mask symmetric-difference error. Smooth-background error is then added by the triangle inequality.

Implementation: `projector_signal/edges.py`  
Tests: `tests/test_edges.py`, `tests/test_additional.py`

### Nonlinear cyclic product law

Coefficient products in residue coordinates obey cyclic convolution of packet labels. The included nonlinear shift-filter example reconstructs exactly from the packet outputs.

Implementation: `projector_signal/nonlinear.py`  
Tests: `tests/test_nonlinear.py`

### Smith coordinates

- the Cayley transform maps normalized impedance to reflection coefficient and is inverted exactly;
- a cyclic phase rotation in the reflection disk pulls back to the stated Möbius action on impedance;
- the actions form a cyclic group;
- the two-phase action is impedance-admittance inversion;
- dyadic and odd cyclic phase selectors factor through the Chinese remainder theorem when their orders are coprime.

Implementation: `projector_signal/smith.py`  
Tests: `tests/test_smith.py`, `tests/test_additional.py`

## Classical constructions explicitly acknowledged

The following are used as classical mechanisms rather than claimed as new discoveries:

- polyphase decomposition and FIR polyphase matrices;
- perfect-reconstruction filter banks;
- Haar wavelets and finite wavelet packets;
- predict-update lifting steps;
- Fourier truncation;
- the impedance-reflection Cayley transform;
- resistance and reactance circles on the Smith chart;
- transmission-line phase rotation.

The paper's contribution is the use of one common seed, packet, transfer, refinement, and reconstruction language across these mechanisms, together with the exact known-edge and error-separation statements in that language.

## Numerical certificates

The one-dimensional, disk, and multiple-edge studies compare:

1. a global Fourier truncation;
2. an exact known-packet reconstruction;
3. where applicable, a deliberately limited positive-contrast estimator.

The sparse-representation study compares the implemented Haar packet ordering with best-magnitude Fourier truncation on one chosen test signal. It records both the regime in which Fourier is better and the regime in which the localized packet basis is better.

Implementation: `projector_signal/experiments.py`, `projector_signal/visuals.py`  
Results: `results/numerical_results.json`, `tables/numerical_summary.csv`, `tables/sparse_representation.csv`

## Conjectural or provisional statements

- stable automatic recovery of the correct edge packet over a broad piecewise-smooth class;
- a canonical adaptive packet tree minimizing reconstruction complexity subject to an error tolerance;
- optimality of the proposed symmetric Smith boundary weight;
- any universal Gibbs-elimination statement not conditioned on correct packet separation;
- historical originality of the overall organization or terminology.

## Proof boundary

The exact packet theorems answer what happens after the decomposition has been specified correctly. The main unresolved analytical problem is to derive that decomposition stably from general observations while controlling topology, amplitude, noise, smooth-background error, and model mismatch.
