# Scope of the reproduced finite assertions

This inventory describes the unmodified existing sources. The observed counts are 48 pytest cases and 118 named exact appendix checks. The 48 cases arise from 40 test functions in seven modules; invalid-edge and nonprime-input parameterizations account for the additional cases. This inventory adds no tests.

## Original release experiments and tests

| Family | Finite scope |
|---|---|
| Packet reconstruction | Release experiment: one seeded normal vector of length 97, moduli 2, 3, 4, 6, 8, 12. Tests: seeded length 101, moduli 1 through 16. |
| Nested refinement | Release carrier length 128; pairs (2,4), (2,8), (3,6), (3,12), (4,8), (4,12), (6,12). Tests also use length 137 and two specified coarse/fine cases. |
| Projector identities | Integer projectors of length 77 for moduli 2, 3, 4, 5, 8, 12; floating Fourier tests for orders 1 through 10. The release record stores completeness/idempotence maxima for orders 2, 3, 4, 5, 8, 12. |
| CRT | Release cases (length,a,b) = (145,4,3), (193,8,3), (241,4,5), (321,8,5). Tests cover five coprime pairs, all 102 corresponding residue pairs, on length 3ab+1 carriers. |
| Operator transport | One seeded integer 24 by 24 operator with entries from -4 through 4 and refinement 2 to 6; DFT eigenline examples of orders 3, 5, 7. |
| Weighted transfer | One three-vertex, six-edge graph; exact rational generating function versus dynamic-programming coefficients for weights 0 through 30 inclusive. |
| Modular inverse | Release supplied 3 by 3 families at (prime,depth) = (2,10), (3,8), (5,7). Tests cover one 3 by 3 family modulo 2^d for d=1 through 10, and one 2 by 2 family modulo 3^d for d=1 through 7. |
| Dyadic/Smith | Fixed valuation, sign-projector, denominator and delay examples; sign projectors at primes 3, 5, 7, 11, 13; diagonal Smith examples at 2^6 and 2^5; three brute-force two-coordinate cases, with 64+81+16=161 candidate inputs. |
| Stability | Fixed coarse spectrum [0.4,0.8,1.3], specified replications and one entry perturbation of 0.09; power indices at most 9; one complex resolvent parameter 3.1+0.7i. |
| Smith chart | Fixed inverse/symmetry inputs and orbit orders 2, 4, 8, 16, 32 at radius 0.73. |
| Input contracts | Prescribed invalid shapes, moduli, primes, integrality, positivity, finite-value, involution and power examples. |

Exact integer, rational, symbolic and modular assertions are distinguished from NumPy floating residuals in the source. NumPy `default_rng` seeds are 20260726 for the release experiments and 1 and 77 for the pertinent tests. The appendix uses no randomness.

The nine-row CSV is a selected summary of the full JSON record. `run_all.py` compares the full record as well as all nine summary rows. `run_experiments()` computes records; its body alone does not assert every numerical residual threshold. Passing the whole documented sequence should not be shortened to a claim that every general theorem has been established computationally.

## Exact visual appendix

| Family | Finite scope or symbolic assertion |
|---|---|
| Residue projectors | Exact integer matrices for (n,q) = (16,2), (16,4), (16,8), (12,3), (7,4), (0,3); four refinement pairs on 24 addresses. |
| Coordinate transport | Exact permutation/operator identities in Q^8, including all four coarse blocks and an explicit scalar-aggregation counterexample. |
| Fourier | All nine entries for N=3 in F_7 and 144 periodic comparisons on n=0 through 47; explicit boundary examples in F_2 and F_3 x F_3. |
| CRT | All 12 labels and all 12 selectors on 36 addresses; one noncoprime incompatible pair. |
| Weighted inverse | Supplied 2 by 2 integral model; exact two-sided inverse and pruning comparisons modulo 2^L for L=1 through 8; modulo-32 display; wrong-order and insufficient-cutoff counterexamples. |
| Cutoffs | 192 instances: depth 1 through 24 and lower weight 1 through 8. |
| Zeta/walks | Symbolic determinant/adjugate; independent rational-series and recurrence coefficients through weight 24; literal walk enumeration for weights 0 through 10; six displayed weight-five walks. |
| Zero-weight boundary | 101 distinct words with zero weight, k=0 through 100. The textual all-k argument is separate. |
| Local denominators | Supplied exact 2 by 2 rational projectors; primes 2, 3, 5, 7, 11; sharp delay examples at depths 1 through 5. |
| Smith fibres | Complete domain/target enumeration for (base,depth,weights) = (2,0,(1,2)), (2,1,(1,2)), (2,2,(1,2)), (2,3,(1,2)), (2,4,(1,2)), (3,2,(0,1)), (4,2,(1,2)). The composite base 4 is intentional. |
| Smith coordinate transport | Supplied unimodular transform modulo 8; all 64 input points in each coordinate system, with eight solutions. The three-coordinate modulo-64 example evaluates the diagonal formula, without brute force over 64^3 points. |
| FIR/polyphase | One zero-extended finite convolution example and exact phase reinterleaving. |
| Smith chart orbit | Eight algebraic points at radius 1/2; exact roundtrips and eight half-turn identities. Decimal coordinates arise only when drawing. |
| Defects and resolvents | Exact rational matrix model, powers 1 through 8, infinity-norm majorant with rho=2; rational spectral parameters -1, 0, 3, 21/10, 201/100; poles 1 and 2 excluded. |
| Invalid input | Four specified rejection checks. |

The generated `EXACT_CHECKS.json` records each of the 118 names, its Boolean outcome and its finite scope. Its model hash equals the shipped model hash. Equality of all 22 generated TikZ files verifies that the shipped appendix plates follow their supplied generator and data in the tested environment; it does not turn finite illustrations into general proofs.
