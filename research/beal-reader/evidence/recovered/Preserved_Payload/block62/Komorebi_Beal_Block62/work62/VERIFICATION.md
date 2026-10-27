# Verification contract and observed scientific checks

The exact original Block61 verifier was restored and observed returning
PASS_DECLARED_CHECKS with its selected nested predecessor chain before development.
Its retained run record is in this directory's verification/ subdirectory.

The six new production programs were run and returned their declared success
statuses before packaging. The release verifier reruns them in a fresh scratch
copy, deletes each generated result first, and compares complete JSON content.
It checks inherited source bytes, all payload bytes, and deliberate rejection of
altered arithmetic and payload inputs. The final fresh-extracted archive replay
is a separate external JSON record so the package does not hash its own report.

|Assertion|Coverage|
|---|---:|
|Good-equation residue pairs|49,200 in both implementations|
|Degree-one counts|1,025 in each implementation|
|Degree-two counts after justified filtering|188 in each implementation|
|Independent smoothness gcds|49,200|
|Base normalized coefficient/character candidates|119,952 in each implementation|
|Added low-h parameter choices|7,056 in each implementation|
|Exhaustive residual (D,b,c) matrix triples in F49^3|117,649|
|Matrix triples with nonrational input|117,306|
|Base independent twisted symbols|144|
|Base inverse-generator transport checks|144|
|Base independent natural symbols|33|
|Additional checker twisted evaluations, including reproduced old columns|126|
|Additional natural symbols at43,113,127|9|

The two new counting primes211,239 contribute14,456 admissible pairs. Earlier
29,43,491 data contribute34,744 freshly reproduced pairs. Each implementation
uses its own count field and canonicalization. This is not direct degree-two
counting of every one of the49,200 pairs: identical curves are reused and the
split-prime N1 residual filter makes some N2 computations unnecessary. Null N2
entries record that boundary explicitly.

The independent checker imports no primary arithmetic. It uses theta^2=theta-d
fields, explicit square-root multiplicities, discrete-log curve canonicalization,
polynomial gcds, inverse cyclotomic coordinates and conjugate norm products,
direct seventh-power symbols, and coefficient trace/norm enumeration. The low-h
checker imports ONLY that separate implementation, not primary code. The matrix
identity has a single executable checker plus its universal algebraic proof.

All production code requires Python3.10+ standard library only. Numerical
tolerances, random seeds, GPU computations, Lean compilations and independent
mathematical review are absent. The verifier records its actual environment,
commands, wall limits, runtimes, input/output hashes and exit statuses. Timeouts
are inconclusive, not mathematical failures or contradictions.
