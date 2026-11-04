# Statement correspondence review

**Recorded 4 November 2026 · Komorebi P.**

**Primary verdict: proved as written within the exact finite-polynomial scope.**

This is an internal source-correspondence review with author and peer passes. It is not an externally independent audit. The reviewers inspected the literal definitions, proof terms as written, upstream theorem statements, domain conversions, boundary cases and reading-page claims. The source files below are the reviewed working-tree artifacts on repository base `97b0e5e0b57f485096b163e33586d4c11b2932a3`.

## Normalized claim and dependency graph

Let Φ be the constructed rational linear equivalence sending X^k to the descending Pochhammer polynomial of degree k. Let P select ordinary coefficient degrees by residue, let Q = Φ P Φ⁻¹, and let ι extend rational coefficients to complex coefficients.

The companion proves the actual finite-polynomial projector laws, degree-preserving coordinate equivalence, inverse second-Stirling formula, complex Fourier substitution identity, and the comparison A ι Φ⁻¹ = ι Φ⁻¹ Q. It also constructs p ⋆ q = Φ(Φ⁻¹p · Φ⁻¹q) and proves its algebraic laws and complete cyclic packet convolution.

The dependency chain is: finite coefficient masks and an actual polynomial basis equivalence supply Q. Primitive-root character orthogonality and the coefficient formula for actual polynomial composition supply A. The coefficient-extension identity and inverse coordinate law identify their encoded outputs. Ordinary polynomial multiplication and complete packet reconstruction supply the transported product and convolution. No circular source dependence or unproved polynomial-equivalence premise was found.

## Obligations

| Obligation | Result | Evidence and boundary |
|---|---|---|
| Finite-support domain | Passed | `Polynomial.coeff.filter` remains finitely supported. Both sides of Φ are ℚ[X]. |
| Coordinate direction | Passed | `basisMonomials.equiv fallingBasis` sends X^k to the falling factorial. Φ(X²)=X²−X and Φ⁻¹(X²)=X²+X. |
| Inverse laws and constants | Passed | Supplied by the constructed linear equivalence and the actual degree-zero basis vector. |
| Degree convention | Passed | Both natural degree and actual degree are proved, with the zero polynomial treated separately. |
| Actual falling projector | Passed | Q literally conjugates the concrete coefficient mask by Φ. The selected coefficients belong to Φ⁻¹p. |
| Reconstruction and refinement | Passed | Reconstruction requires N>0. Refinement requires M>0 and N dividing M. The proved form is the filtered-address sum. |
| Fourier sign and exponents | Passed | The negative integer exponent is used literally. Quotients of powers handle k<r without natural subtraction. |
| Fourier substitution | Passed | The average uses actual polynomial composition, and every coefficient is compared. |
| Root and address conditions | Passed | Primitivity and r<N are present. N=1 is included. Removing the canonical bound or primitivity changes the result. |
| Rational and complex carriers | Passed | The comparison is in ℂ[X] after rational coordinate encoding and coefficient extension. |
| Transported multiplication | Passed | The concrete product is rational bilinear, associative, commutative and unital. Basis degrees add. |
| Cyclic convolution | Passed | Polynomial induction proves homogeneous packet multiplication, and complete finite reconstruction gives every input-packet interaction. |
| Displayed fifth-power example | Passed in explicit controls | The full inverse polynomial and evaluations 600, 244, 180 at four are checked. |

## Controls and compiler evidence

The positive controls distinguish the two directions of Φ, ordinary and falling degree, Fourier normalization and sign, and cyclic wraparound under the transported product. The false-equality controls reject reverse conjugation, ordinary-projector reuse, a nonprimitive root, omitted normalization, zero-modulus reconstruction, the wrong character sign and ordinary-product reuse. A separate unfinished-proof control checks warning rejection.

An early parallel control attempt collided with a production rebuild and failed on a missing import. Those runs supplied no acceptance evidence. The controls were rerun after the build settled, and the official replay uses an isolated fresh directory. The [recorded native replay](verification/2026-11-04/run.json) is the authoritative compiler and axiom evidence for the bound sources.

## Remaining scope

The exact signatures do not include an abstract construction of ℚ(ζ_N), signed-first-Stirling matrix entries, cyclic permutation trace formulas, the arithmetic-progression reindexing of refinement, concrete finite-difference or translation operators, constructive Newton interpolation, spectral-projector formulas, the Δ derivation rule, the extension of Φ to arbitrary coefficient rings, or infinite-series and analytic identities. The semiring generality of the coefficient masks and product helpers does not broaden the rational coefficient domain of Φ.

The named theorem count includes supporting lemmas, explicit counterexamples and the earlier classical Stirling identity restated as a helper. The separately retained generic transport declarations and positive controls are excluded from that count.

## Reviewed source hashes

| Source | SHA-256 |
|---|---|
| `KomorebiPolynomial/PolynomialPackets.lean` | `b8a87aafca23419a944b0d0c1523fea29c73cdca43824f470bcc60daea48ff2e` |
| `KomorebiPolynomial/FallingFactorial.lean` | `738d0af44593ecac91f66ab2ef10c5a5b59b6b97073afdef8c1c4567358b4231` |
| `KomorebiPolynomial/FallingPackets.lean` | `521ec82995b480c81c030ce782b6caf1d4244f16a1f33cdab273a66be73c7904` |
| `KomorebiPolynomial/RootsOfUnity.lean` | `bcc4912e934ae8452c8888a2a7993ec84adc5465208f6400c8555f068d643379` |
| `KomorebiPolynomial/FourierBridge.lean` | `4b2a9dcba0125d2dd390874b4499e124d65daf7e5d33ff1adffc943e26d18192` |
| `KomorebiPolynomial/FallingProduct.lean` | `41132f005a33300e1142adb789cc91eff1fb4bd54dd60eed207d153bf27a6c28` |

[Exact statements and dependencies](CLAIM_MAP.json) · [Pinned source checks](SOURCE_DEPENDENCIES.md)
