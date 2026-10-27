# Rounded posterior parameters with a finite precision guarantee

Author: Komorebi P.

## Target and exact contract

This block extends the v11 rounded gain solver with an output representation.
For the same exact rational model and fixed complete self-adjoint packets, and
positive rational tolerances epsilon and delta, the implemented program returns:

- the represented gain and its passing posterior-error certificate;
- a dyadic ball for every mean entry and covariance entry;
- a computed output precision;
- the guarantee that every returned radius is at most delta.

The represented probability law remains the Joseph Gaussian determined by the
returned gain and the input model. The ball arrays enclose its parameters.
The covariance-center matrix is not used to define another Gaussian.
Consequently this extension adds no unaccounted perturbation to the law certified
at tolerance epsilon. Delta controls parameter representation accuracy, separately
from the distribution-error tolerance epsilon.

## Objects and arithmetic graph

Let H, L, N, sigma, m, y be the exact model data, with sigma > 0. Write

    P = L L^T,   R = N N^T + sigma I,   v = y - Hm.

For any represented gain B define

    A_B = I - BH,
    mu_B = m + Bv,
    C_B = A_B P A_B^T + B R B^T.

The evaluator computes balls for these expressions using exactly the inherited
rounded input, product, sum, subtraction and addition nodes. In particular it
evaluates the covariance using the Joseph expression above, rather than dropping
its second term or substituting a posterior covariance formula valid only at the
exact Kalman gain. Model factors are rounded inside this output graph too.

PosteriorOutput.lean defines the rational specification, the actual dyadic graph,
and a matching precision-independent budget graph. There is no inverse covariance,
eigendecomposition or square-root computation in the output evaluator.

## Soundness and sufficient precision

For each scalar graph node, the retained budget calculus proves

    |x| <= M,   |x - center_p| <= radius_p <= k 2^(-p).

The new proofs compose these bounds through the complete mean and covariance
graphs. If k_i and k_ij are the terminal radius coefficients, define

    K(B) = sum_i k_i + sum_ij k_ij.

All coefficients are nonnegative. Thus every terminal coefficient is at most K.
For delta > 0, the actual output policy computes

    p_out = 1 + floor_log_2(ceil_nat(K(B)/delta)).

The inherited integer-log bound proves K(B) 2^(-p) <= delta for every p >= p_out.
Hence every mean and covariance radius is at most delta at all such precisions.
No assertion that successive rounded centers, radii or scores are monotone is
needed. The bound is sufficient and may be conservative.

`evaluate_encloses` proves enclosure at any natural precision.
`evaluate_grid` proves both centers and radii lie on that precision's dyadic grid.
`evaluate_radii_le` proves quantitative sufficiency for every p >= p_out.
`represent_spec` combines enclosure and the requested radius guarantee.
Finite empty coordinate types remain covered by these universal Lean statements;
the Python producer retains its positive-dimension contract and dimension cap 8.

## Probability semantics

PosteriorOutputSemantics.lean checks the real-coordinate embeddings against the
pre-existing definitions `gainMean`, `gainJoseph` and `RationalModel.approximation`.
It proves, as an equality of actual measures,

    approximation(M,B) = Gaussian(real(mu_B), real(C_B)).

It also derives positive semidefiniteness of C_B from the factor-coded prior and
positive noise floor, including singular priors. `represented_real_errors` gives
absolute entrywise bounds by delta in the real coordinate space.

These semantic equalities matter: an interval arithmetic identity by itself does
not identify the probability law whose parameters are being enclosed.

## The canonical program

`Komorebi.PosteriorOutput.run` rejects delta <= 0, then runs the retained rounded
solver at epsilon. On success it evaluates `represent` at the returned gain.
`run_terminates` proves successful return with `ResultValid` for positive epsilon,
positive delta, positive noise floor and valid packet families. `run_sound` proves
validity for every successful return without separately assuming valid model data.

`ResultValid` contains both checker results, the actual posterior Wasserstein
bound, the two parameter-enclosure predicates, all radius bounds, the computed
precision equality, and equality of the returned arrays with the actual evaluator.
Thus the output theorem concerns the returned arrays, not unrelated witnesses.

The ideal finite termination theorem and the Python producer's finite resource
caps are different contracts. A cap failure prevents success-proof export.

## Why interval arrays are necessary for this contract

A valid exact singular covariance is

    C = [[1/4, 3/4], [3/4, 9/4]] = (1/2,3/2)(1/2,3/2)^T.

Rounding each exact entry downward at one fractional bit gives

    D = [[0, 1/2], [1/2, 2]].

For z=(-3,1), z^T D z = -1, so D is not positive semidefinite. Nonetheless the
balls obtained by rounding those exact entries still enclose C entrywise.
PosteriorOutputBoundary.lean records the valid input, computed rounded centers,
invalid center covariance, and surviving interval enclosure.

This refutes a tempting stronger output claim. Entrywise containment does not
certify that the matrix of interval centers defines a valid Gaussian covariance.
A separately rounded factor representation or sampler needs its own law and
transport-error proof. It is not included in this release.

## Verification scope and remaining goal

The verification receipt is authoritative about compilation and axiom coverage.
New examples check output bit counts, all centers and radii, actual program
returns, and the combined certificate. Independent exact diagnostics compare the
output graph with direct Joseph-factor scalar sums, at six matrix cases and five
fixed precisions, plus three output tolerances. This finite check is diagnostic,
not a universal theorem or performance benchmark.

This block closes parameter enclosure and output precision sufficiency for the
first-release contract. It does not close model-changing adaptation, sequential
filtering, uncertain-input semantics, parser/exporter refinement, IEEE-754 or
bounded-word execution, an executable sampler, performance superiority, or
literature priority. The architecture's larger adaptive and efficiency goals
remain separate work.
