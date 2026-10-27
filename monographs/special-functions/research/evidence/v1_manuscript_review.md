# SF-DISCOVERY-100 curated manuscript review

**Primary verdict: proved as written.** This verdict applies to the mathematical assertions in the five curated source sections pinned below, with their stated domains and the evidence-count convention. The assertions agree with the frozen proofs independently reviewed at this checkpoint. No unresolved mathematical defect was found in this scoped review.

Review date: 2026-10-08. Reviewer: independent proof-audit agent, read-only relative to the manuscript, frozen proofs, API, catalog, figures, and suite. The only new artifact is this report. No suite was rerun. This is an informal mathematical and transcription audit; it is not an analytic Lean certificate, an interval certificate, or a historical-priority verdict. Final PDF pagination and whole-document visual QA belong to the release builder.

## Exact curated source inputs

| File | SHA-256 |
|---|---|
| `sections/spectral_continuation.tex` | `6c369efb1f8605b39dea82e7f00b4050a705b9991447a48289c532f9202bbd3d` |
| `sections/sequence_polyphase.tex` | `0de51dfc1c45cee37d6810187c9be21e3391203b033fe62ee1560a12d65a0c0a` |
| `sections/release_status.tex` | `f52c08af245968b2365c8ff81f3bc35634530285567d4bdc895d07923aee6a2d` |
| `sections/proof_map.tex` | `83974c0777e4dddef08472019e091249b95ec80743cc5d075b66882c1661fae2` |
| `sections/arithmetic_inverse.tex` | `5d4d756ec944e32a77f790f47eb27236d5f524dea5705cc450af4515c6ad3950` |

## Spectral continuation and shifts

The curated statements retain integer N >= 2, principal branches, and zero multiplicities. The branch-cut separation supports the complex-zero beta-integral interchange on 1/N < Re(s) < 1. The root-of-unity exponential identity, the leading logarithmic term t^(1/N) - log N, the two-end Mellin subtraction, the coefficients alpha_k = (-1)^(k+1) Z_N(k), and the signs of the rational subtraction terms agree with the full proof. Small-radius poles at positive integers are canceled by sin(pi s); the only unshifted pole is simple at 1/N with residue sin(pi/N)/(N pi). The nonpositive-integer zeros, derivative Z_N'(0) = -log N, and regularized determinant N follow correctly. The exact abscissa is 1/N. The curated abscissa explanation gives the contradiction for smaller exponents; the full pinned proof also supplies the boundary argument.

For real shifts a >= 0, the printed normalization and determinant agree with the proof. For a > 0 all poles 1/N-k are genuine and simple, and their residues are sin(pi/N)/(N pi) times (1-1/N)_k a^k/k!. The alternating binomial coefficients and sine values cancel their signs. At a=0 only the leading pole remains. The determinant N E_(N,1)(a) equals N E_N(a) under the displayed series definition, with N=2 anchor 2 cosh(sqrt(a)). No ordinary convergent product of the zero coordinates is claimed.

Figure 15 was inspected directly. Its N=3 unshifted panel places the sole pole at 1/3; the shifted a>0 panel places the visible ladder at 1/3, -2/3, -5/3, -8/3, -11/3. The marked zeros are the proved nonpositive-integer zeros; neither the caption nor the legend claims that these exhaust all complex zeros. The diagram is exact theorem-location data, not a numerical zero search. All poles of these continued functions are real, as labeled.

## Sequence normalization, polyphase laws, and regimes

The factorial recurrence for A_n=(2n+1)!c_n has the correct binomial factor, contraction powers, initial value A_0=1, and now explicit range n>=1. A_1, A_2, A_3 match the recurrence and the frozen proof. The printed prefixes agree with the catalog: tangent 1,2,16,272,7936; (1,2) 1,4,160,35200,38041600; (1/2,1/2) 1,1/2,1/4,1/8,1/16; and (1/3,2/3) 1,4/9,160/729,18560/177147. The first known anchor is OEIS A000182, with OEIS indexing a(n+1) corresponding to this project's A_n, n>=0. The prefix identification does not establish novelty or a new accession.

The denominator clearing H^n D^(n(n+1)) A_n and ordered-tree exponent bound are stated as sufficient, not minimal. Figure 17 has the correct chain contribution 48 q^9 r^3, balanced contribution 80 q^5 r^5, local factors, child-size exponents, and left/right addresses.

The OGF decomposition, root projector, EGF preservation of (bn+j)! denominators, and carry exponent (j+ell-i)/b agree with the proof and API. The three-phase [1,2,-1] matrix is [[1,-t,2t],[2,1,-t],[-1,2,1]]. Figure 16 uses that matrix, input a_m=m+1 for m=0,...,11 with zero extension, and correct 14-term output 1,4,6,8,10,12,14,16,18,20,22,24,13,-12. Differentiation, repeated zero-constant integration, Hurwitz multiplication, and intrinsic nonlinear taps are correctly distinguished.

The printed analytic regimes have their necessary hypotheses. Both positive scales below one give the finite-order entire family. A unit-scale edge with the other scale strictly between zero and one gives an entire function of infinite order; the stated lower bound has the correct q^3 and q/2 constants. The corner (1,1) gives tangent. If one positive scale exceeds one and the other is positive, the coefficient lower bound gives zero radius. Either zero scale gives T(z)=z. Figure 18 matches every boundary, including the axes overriding the exterior color. The classification and the release judgment are restricted to nonnegative real scales, with no claimed signed/complex regime classification.

The JSON catalog has 18 rows, each with 13 coordinates indexed 0 through 12. Its eight positive integer formal rows are correctly classified, including two diagonal specializations. Signed tanh is a separately identified known formal boundary, outside the nonnegative-real chart. API validation statements reflect the repaired fractional-residue and zero-phase defects.

## Arithmetic character uniformity and release scope

The final arithmetic wording correctly says: “The modulus is fixed; the constants are not asserted uniform as Q grows.” AI-4 is uniform in the prescribed sector and over the finite character set of a fixed modulus. It does not claim a modulus-independent constant. The exponent difference 1/(2 beta) is correct.

The release matrix now lists stable recovery within bounded prime classes as open. AI-3 has already ruled out a guarantee uniform over unbounded excluded primes at fixed finite precision; that impossibility is no longer mislisted as an open task. “Nonnegative real scale regime” replaces the overbroad earlier “full growth regime.” The direct-family novelty judgment is explicitly a candidate judgment, not a proof of historical priority.

The appendix map correctly assigns the five frozen proofs and their mathematical dependencies. Baseline SF-DISCOVERY-001 files are preserved as historical state and explicitly superseded where the new checkpoint closes an old question. Classical Hadamard factorization, Laplace uniqueness, orthogonal-polynomial machinery, and spectral Mellin methods are distinguished from local verified applications. Whole converted appendix typography is outside this curated-source review.

## Read-only evidence reconciliation

| Script | Principal exact | Supplemental exact | Numerical |
|---|---:|---:|---:|
| nonlinear_dilation | 1,218 | 0 | 0 |
| asymmetric_dilation | 1,811 | 0 | 0 |
| complex_depth | 301 | 0 | 3 |
| orbit_zeta | 138 | 0 | 0 |
| arithmetic_polynomials | 0 | 0 | 2,273 |
| dilation_type | 6,091 | 0 | 0 |
| arithmetic_inverse | 304 | 540 | 88 |
| multi_prime_sieve | 1,019 | 0 | 3,182 |
| spectral_continuation | 411 | 0 | 30 |
| family_lab_checks | 8,038 | 0 | 0 |
| **Total** | **19,331** | **540** | **5,576** |

The total of actual exact assertion statements is 19,331+540=19,871. Static inspection of the inverse atom loop confirms the three omitted helper assertions per recovered atom: exact square root, integral inverse power, and exact integer root. The 60 models have 180 atoms in total (4 moduli times 3 beta values times ranks 1,...,5), supplying 540 helpers without double counting. Its outer counter is 5*60+4=304.

Grouped conditions count once per executed assertion statement; orthogonality and recurrence counters are subsets of numerical totals, not additional totals. The 61 detector iteration guards are operational and excluded. The sieve report contains the claimed 102 positive parameter/depth cases, 1,395 orthogonality conditions, 381 recurrence cases, and 40 conditional pencils. API 8,038 and dilation-type 6,091 counts agree with the records. All 18 vector figures and 18 PNG previews are present.

All 25 manifest input hashes still match their current files and recorded post-run hashes. All 22 byte-identical snapshot hashes and all 10 result-report hashes match. The recorded runner status is passed with no failures; the manifest schema validation passed. This verifies the recorded bounded execution and evidence accounting, and does not turn finite checks into universal proofs.

## Corrections resolved during review

Three curated-source corrections were reported to the builder and verified after repair: the bounded-prime recovery open question, the nonnegative-real regime qualification, and n>=1 in the normalized recurrence. The earlier stale sequence snapshot was not used for the verdict: both current printed (1,2) examples and the exact catalog have 35200 and 38041600. A subsequent layout-only revision replaced three large sequence figures with the smaller figure macro and adjusted Appendix E paragraph spacing; those source revisions are included in the pins above. Frozen proofs and the API were not changed in this review. Documented prior failures remain release history, rather than being omitted from the successful-count narrative.

Historical priority remains unresolved. The official OEIS anchor was checked at https://oeis.org/A000182; no global novelty inference is drawn from that check or bounded source searches.

## Frozen mathematical comparison inputs

| File | SHA-256 |
|---|---|
| `new_results/dilation_type.md` | `4a438fa513b06cc729d8317c565bc2a45dc9da253964d3d9ce406a5ac6f97494` |
| `new_results/arithmetic_inverse.md` | `a8c29614a565231ac91e14c17312928ebdc40bcd5c1597e73b487f1f8b00cc81` |
| `new_results/multi_prime_sieve.md` | `5b5997c122e80bfad68cbb20698e704788e9ff6b82e72794418efde3a0df716e` |
| `new_results/spectral_continuation.md` | `d131b25e28921d79700a5b7a86e357e4f60623785c73a657664e0b7bd7c81d7b` |
| `new_results/sequence_polyphase.md` | `77186be00ffda9f1751432d869849d1388ec78a55bc5c4cbd97eeb0ebabd20c0` |
| `family_lab.py` | `7b546c1cd3159bb59634a3306c116719cd8d8d368c0046af90270c709b08cc8e` |
| `checks/family_lab_checks.py` | `d9e549133cf38cc285aa5f079c569eb381b9059c08263bee3ecb442a768cae56` |

## Catalog and evidence comparison inputs

| File | SHA-256 |
|---|---|
| `examples/sequence_catalog.json` | `2d72c1f0d5fe0baf1ea1277f32b78b45fcc45de1d58302468c6a1085cbb30823` |
| `examples/sequence_catalog.csv` | `89e6715f64b30ad0677d2cf983a46dabe8c9e8dbb16f31728f8aa2b88a96348d` |
| `evidence/v1_independent_audit.md` | `f9178eaff90445f35ed47bb8235fa2a6ca99cefcaacd1dc58ed354b647e3e4b9` |
| `evidence/release_summary.json` | `8e2caf93c3abd1ca938b25743ede06f3e98db4a05c58596d25cc9326a977c968` |
| `evidence/release-run-001/manifest.json` | `028cf0c784276975de40f149ab7e858ca125331521b4b4144ac9f4dec10a5a5f` |
| `evidence/release-run-001/summary.json` | `a06fbecf7305adf85dcdc801e64c2bc312c1a9cfd12be6ef4318c8e41486f741` |
| `evidence/release-run-001/validation.json` | `be275cecda0b0da1de0d080f5a787b16eddef5bbdd53e29d2064f915a8e9a8f1` |
| `checks/run_release.py` | `ec2e783328e246ac07521c6f4af487b202e556bf403eaf4bbcdf1edb1a550be2` |
| `checks/arithmetic_inverse.py` | `0199044e22e04014b49d51d4a0b18aa2f3efbae635721a4a483e10890f00fd79` |

## Inspected figure inputs

The PNG previews were viewed; each corresponding vector PDF is pinned for the same release artifact.

| File | SHA-256 |
|---|---|
| `figures/15_spectral_poles.png` | `3d58c71d3b329912c76c7aab4fec413df9f4ba1bda42925f2f337d8b1adb3167` |
| `figures/15_spectral_poles.pdf` | `f7968435b3d853dd7e885ddf047ca74c7ee810c28f1b0e0e0b47f04de0153e37` |
| `figures/16_polyphase.png` | `574d96dd4fed67a537badc033a0c268d7241efb6a00780f8977275512489173c` |
| `figures/16_polyphase.pdf` | `88545854645205281c3f16be482f06933a43633ea632e6aabd3f5be24308f98d` |
| `figures/17_tree_addresses.png` | `2243fce08e98c41f8a94ac348a5b86123351d622afdc3e95052c15256bf27c41` |
| `figures/17_tree_addresses.pdf` | `c7917025365729fc257f89d7409caffe64bd26dda3ad749544e4c5199b4db805` |
| `figures/18_parameter_regimes.png` | `5d13e7aabef9c765a05cb7376925f9c5aef6b6b95ef0e7a5fb9edc1e7680af77` |
| `figures/18_parameter_regimes.pdf` | `1358162d09a7b2628f1d63fcf28c0eb8513d84b2611718530fc998fe8e5c9956` |

## Final figure-width revision history

On 2026-10-08, the regime figure call changed from `\smallfig{18_parameter_regimes}` to `\smallfig[0.68]{18_parameter_regimes}`. Reversing exactly this one replacement reproduces the prior curated source SHA-256, so all mathematical text and equations are byte-identical to the previously reviewed source. The optional-width macro in `main.tex` retains default width 0.78; this call selects 0.68. The primary verdict is unchanged. No suite was rerun.

Previous report SHA-256: `60bbcb5b96ccaf44046a6542119126112f5b31f164c678e5b1bae32082e46463`. Previous sequence-section SHA-256: `9129fa52a7ab9ff101254f1e47e56fe62fe5b7309ca30623da7f55eedb932d6c`. Current sequence-section SHA-256: `0de51dfc1c45cee37d6810187c9be21e3391203b033fe62ee1560a12d65a0c0a`. The other 28 report pins remain unchanged.
