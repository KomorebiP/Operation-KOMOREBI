# Realistic SKAT simulation audit — v0.9

Date: 2026-09-23

## Purpose

Validate the full streaming/deep-tail path on the project's established
rare-variant SKAT simulation machinery rather than only on abstract matrix
families.

The tested path is

raw genotype matrix
-> per-variant centering/scaling
-> covariate residualization
-> rare-variant weights
-> streamed sample kernel
-> eigenspectrum
-> K-COS deep-tail evaluation.

## Historical copy-LD simulator defect

The historical strong-copy-LD benchmark allocated the genotype matrix using

`G = np.empty((n,m), dtype=np.float64)`

and then accumulated haplotypes with `+=`.

Because `np.empty` has unspecified initial contents, that implementation was
not a valid reproducible simulator.

v0.9 repairs the generator by using a zero-initialized matrix.  Earlier
copy-LD benchmark numbers are therefore retained only as historical evidence.

The separate latent-Gaussian LD generator did not have this defect.

## Scenarios

Four deterministic simulation regimes were tested:

1. latent-Gaussian moderate LD, n=600, m=3000;
2. latent-Gaussian strong LD, n=600, m=3000;
3. corrected strong copy-LD, n=600, m=3000;
4. corrected strong copy-LD, n=1000, m=5000.

Median adjacent within-block r^2 ranged from
0.0069
to
0.8298.

The large corrected copy-LD case had rank 996 and effective
spectral rank 353.027.

## Raw-genotype streaming invariance

Resident block sizes 31, 127, and 509 were tested for every scenario.

Maximum relative discrepancy between the streamed kernel and the fully
materialized weighted/residualized factor reference:

6.611e-16.

## Phenotype-space algebra

One hundred Gaussian-null residual draws per scenario were evaluated through
the factor, sample-kernel, and eigencoordinate forms.

Worst relative discrepancy:

8.318e-16.

## Realistic deep tails

The ordinary scenario battery used tilt fractions 0.90, 0.97, and 0.99.

The n=1000, m=5000 corrected copy-LD case was additionally pushed through
0.995, 0.997, 0.999, and 0.9995.

Deepest high-resolution full-spectrum reference:

log10(p) = -457.973916.

Worst absolute K-COS/reference discrepancy across all realistic LD tail tests:

3.209e-12 decades.

## Evidence label

- algebraic streaming equivalence: proved separately, numerically reproduced;
- realistic-LD behavior: finite synthetic validation;
- deep-tail accuracy: computationally verified on the stated spectra/queries;
- simulation code correction: confirmed implementation defect and repair.

This does not establish that these generators reproduce every feature of
population sequencing data.  External cohort replication remains separate.
Finite-sample logistic/Bernoulli calibration also remains a separate
statistical problem.

## Numerical warning observed during deepest adaptive refinement

At the deepest corrected copy-LD queries, NumPy emitted overflow warnings while
evaluating an intermediate conservative growth sum inside the adaptive
certificate planner.  Those candidate bounds became infinite and were not
accepted as final certificates.  The returned K-COS results retained finite
certified relative bounds between roughly 4e-9 and 9e-9 and agreed with the
higher-resolution exact-spectrum tilted reference.  The warning is retained as
an implementation-hardening target rather than hidden.
