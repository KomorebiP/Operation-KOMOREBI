# Independent audit of the next Euler continuation

Date: 2026-10-05. This review was derived from the raw proofs and exact Euler source definitions by a separate reviewer. Author proof files were not edited. Exact reviewed revisions are recorded in `SOURCE_HASHES.json`; execution provenance is in `certified_run/manifest.json`.

## Normalized target and primary verdict

The global target is: for every ordinary integer Euler depth `r>=1`, every zero of the exact normalized restricted series `G_r` in `Z_2` is simple.

**Primary verdict: incomplete, with the smallest remaining implication being arithmetic noncancellation on the surviving critical strata.** No error was found in the three new narrower results under their stated hypotheses. The higher-address theorem proves new universal conditional simplicity families. The terminal-161 phase argument yields a single necessary finite parameter class. The epsilon-family theorem proves that its enlarged analytic family actually contains one transverse double-root member; it does not show that the discrete arithmetic Euler value avoids that member.

No exact singular Euler index, all-precision interpolation of the actual undepleted index family, or new Lean verification is established by this continuation.

## Claim cards

1. **Regular lower addresses.** An actual Euler wall has certified true terminal `j`, first-record complement `k=j-a`, `t=v2(k)`, and `L=Theta(k)+delta`. The lower address `a` is regular and `t>=Theta(a)`. For `delta>=1`, repeated roots are excluded from all emerged complement balls and can only lie on the strata in equation (6). In particular all roots are simple when `0<=D=t-Theta(a)<v2(a!)`. Equality walls `delta=0` are simple without that band. The claim is about actual Euler coefficients subject to certified terminal hypotheses, not arbitrary formal unit perturbations or all odd multipliers without terminal certification.

2. **Terminal 161 phases.** For every positive odd ordinary integer `B` such that `r=B*2^L-161` has actual terminal 161, a repeated dyadic root must have `L=640`. It must satisfy `B=Bstar mod 2^935` and `x=Xstar mod 2^932`, with the canonical residues in `combined_frontier.json`. Both side phases are completely resolved: `L=639` has one simple root; `L=641` has three. Since `Bstar` has bitlength 933, every admissible positive odd `B<2^932` is excluded, and the stronger exact interval is `0<B<Bstar`.

3. **Independent epsilon deformation.** Fix a single ordinary Euler index having the stated terminal-161 packet bounds and the stated depleted quadratic chart. On `epsilon=2^24 eta`, the critical value `Phi(eta)` is a bijective isometry of `Z_2`. There is exactly one parameter `eta_*` with a double root in that chart. The actual Euler chart is singular precisely when `eta_*=2^(2r-25)`. The source-coordinate refinement removes common-zero denominators on this chart, but supplies no nonvanishing theorem for its final logarithmic derivative.

## Dependency graph

The source packet formula, exact carry valuation, integral source `A`, and restricted convergence are supplied and proved in `sources/euler_v4.md`, Sections 1–3 and 9. The first-record and true-terminal shift identities are proved in `carry_audit/CARRY_ADDRESS_AUDIT.md`. These feed the exact prefix split used in the regular-address proof. The regular complement atlas is the consequence of the source's skeleton separation and regular-wall theorem.

The terminal-161 argument additionally depends on the previously audited address-one theorem, the finite parameter theorem VI.7 in the inherited v6 manuscript, and the earlier 917-bit recenter proof and coefficient certificate. I read the actual VI.7 statement and proof: it supplies a coefficientwise congruence **on parity balls**, with individual low-packet congruences and a parity-tail cutoff. Its true-terminal hypothesis is essential. The new phase proof does not turn that result into a global Gauss congruence or an all-precision parameter identity.

The epsilon argument depends on the exact undepletion identity, terminal-161 scalar bounds, and the explicit depleted quadratic-chart hypothesis. The latter is an assumed/certified input for each covered fixed index, not a conclusion for every multiplier.

The inherited Bernoulli denominator and duplication facts enter through the project-local exact source proofs. This audit did not perform a new external literature review, reconstruct all inherited Euler coefficients, or independently repeat the earlier 1096-bit original-index reconstruction.

## Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Exact Euler normalization in the prefix split | Passed | Cocycle of packet coefficients and true-terminal shift give a unit coefficient on `P_a G_(r+a)` and prefix scale `2^(delta+D)` |
| Lower prefix is an analytic unit for regular `a` | Passed | `c_0=1`; all other retained scalar valuations are strictly positive |
| Lower normalized derivative and complement atlas | Passed | Affine chart reductions are coefficientwise linear; division by the prefix unit preserves the reduction |
| No repeated root on an emerged complement ball | Passed | Exact displacement plus dyadic parity contradicts equality of the two derivative-term valuations |
| Factorial-width simplicity band and critical-scale formula | Passed | `min(g_l+h_l)=v2(a!)`; digit sums give the displayed binomial-valuation correction |
| Equality-wall derivative exclusion | Passed | `2^t` divides `k`, with `t>=4`, so the binary falling polynomial has zero derivative |
| Side-phase atlas coverage | Passed | All 76 leaves are disjoint and their exact dyadic measures sum to one in each atlas |
| Side-phase coefficient certificates | Passed | Independent affine reconstruction reproduces every complete constant/linear reduction |
| Middle-phase elimination without nonunit division | Passed | Wronskian first forces odd `Y`; only then is `A(Y)` inverted |
| 64-to-61-bit precision transfer | Passed | Odd-chart content 4 and chart exponent 1 give derivative valuation 3 |
| Composition into the 935-bit `B` class | Passed | Exact integer substitution, canonical residue bounds, low-bit compatibility, and inherited certificate hash checked |
| Joint epsilon Gauss convergence | Passed | Uniform geometric denominator bounds give an integral joint restricted remainder |
| Critical-point motion and critical-value isometry | Passed | Parameter half-derivative loss is one bit; motion has a 14-bit gain and cannot cancel the parameter increment |
| Double-root multiplicity exactly two | Passed | Quadratic Taylor coefficient remains odd after translation |
| Source-coordinate unit denominators | Passed | The `q=1` term uniquely dominates; `P_160` has Gauss content 159 on the deep chart |
| Exact avoidance of the arithmetic epsilon parameter | Not addressed | No proof of `eta_* != 2^(2r-25)` in all covered cases |
| Remaining terminal/higher-address critical strata | Not addressed | The present results retain unit cancellation cases and irregular lower addresses |

## Detailed reconstruction: regular addresses

Write `S` for the actual prefix through `q=a-1`, and `Q=P_a/S`. Since `S` reduces coefficientwise to 1, it is invertible in the integral restricted algebra. The exact equation is

`G_r/S = u Q(x) F(x-a) + 2^(delta+D)`, where `F=G_(r+a)`.

On a lower ball centered at `ell`, separation gives `v(Q)=g_ell+s` and `v(Q')=g_ell`, where `s=v(x-ell)`. The second formula remains valid after division by `S`: after affine normalization the reduction is still `Z`. At a root neither `Q` nor `F` is zero. If it were a repeated root, the nonzero term `Q'F` forces the other derivative term to be nonzero too, so valuation equality gives `v(F)=s+v(F')`.

On an emerged complement ball this means `v(x-alpha_i-a)=s`. The root-value equation then implies `delta-d_i=2s+g_ell-D>H_i`. Since the translated ball contains `ell`, its integer center difference `i+a-ell` is a positive multiple of `2^H_i` strictly smaller than `2^(H_i+1)`; hence it equals `2^H_i`. The exact complement-root displacement is strictly deeper. Thus `v(alpha_i+a-ell)=H_i`. If `s>H_i`, the two distances cannot coincide; if `s=H_i`, subtraction of odd units makes the other distance strictly deeper. This is a complete exclusion.

On a root-free complement ball the root-value equation forces `g_ell+s=D`. Since `D<t<=H_i`, this also fixes `v(i+a-ell)=s`. If `d_i>delta`, both derivative contributions to `F'` have valuation greater than `delta`, contradicting the necessary `v(F')=delta-s`. Therefore `d_i<=delta`, the skeleton derivative dominates the even derivative of `V`, and `delta=d_i+s`. This proves all three necessary conditions, not their sufficiency.

Finally `P_a` is the falling factorial times an odd-valued factor. Its minimum pointwise valuation is `v2(a!)`, attained at `x=a`, and its minimum on each lower ball is `g_ell+h_ell`. This proves the band. The critical scale identity follows directly from `d_i=k-1-t-s2(b)-s2(c-1-b)` for `i=2^t b+rho`. I found no missing endpoint or sign in these deductions.

## Detailed reconstruction: all terminal-161 phases

The inherited address-one theorem leaves `L=639,640,641`. The lower polynomial at these phases is uniformly `[2,19,84,16,32,64] mod 128`, with unique root `90 mod 128`. Derivative cancellation and skeleton separation then leave only the skeleton ball `90+128 Z_2`, whose derivative valuation is 153. Hence a repeated root requires `delta=153`, or `L=640`.

The stronger side atlases independently certify their complete root counts:

| Phase | Leaves | Maximum removed content | Simple-root balls | Derivative valuations |
|---|---:|---:|---|---|
| `L=639` | 33 | 158 | `26+64 Z_2` | 152 |
| `L=641` | 43 | 160 | `58,90,122+128 Z_2` | 152, 153, 152 |

All maximum contents are strictly below the 180-bit coefficient precision. The parity-ball congruence suffices because every certified leaf lies in a parity ball. The independent checker uses exact `Fraction` measures, pairwise residue disjointness, and a new affine Horner routine to recover each coefficient reduction. It does not infer coverage from sampled values.

For `L=640`, dividing the 224-bit local coefficient model by `2^160` leaves 64 bits. Differentiating the resulting integral `Y`-series preserves those 64 bits. The independently reconstructed polynomial `W=A C'-C A'` has the two certified reductions

`W(2Z)/16 = 1 mod 2`, and `W(1+2Z)/16 = 1+Z mod 2`.

The surviving odd chart has 60 coefficient bits after dividing by 16; lifting `Z` through 60 bits gives `Y=1+2Z` through 61 bits. Equivalently `v2(W')=4-1=3`, so a 64-bit zero determines 61 bits of `Y`. The recovered residues are exactly

`Y = 1875189377982927951 mod 2^61`,

`B = 606767000650532091 mod 2^61`.

The inversion of `A` is valid because `A=Y mod 2` and only odd `Y` remains. Since integral restricted polynomials are 1-Lipschitz, the 61 known `Y` bits are enough to compute `-C/A mod 2^61`. No hidden extra `Y` precision is used.

The residues imply `B=17659 mod 2^18` and `x=10202 mod 2^15`, exactly the entry conditions for the earlier recenter theorem. Thus `Bstar=17659+2^18 tau917` and `Xstar=10202+2^15 zeta917`. I checked both full integers, the inherited coefficient-file hash, low-bit compatibility with the new 61-bit pair, canonical bounds, modulus exponents 935 and 932, and `bitlength(Bstar)=933`. A finite necessary residue does not assert an exact singular parameter at `Bstar`.

## Detailed reconstruction: epsilon family and source units

Let `b_q(x)=gammahat_q P_q(x) A(x-q)`. The exact rational expansion gives

`Gtilde=(1-epsilon)Ghat+epsilon S+2^155 epsilon^2 R0`,

where `S=sum 4^q b_q`. For `1<=q<161`, the scalar valuation in `R0` is at least `153+2q-155=2q-2`; for `q>=161` it is at least `2q-155`, tending to infinity. Each denominator is a geometric restricted series `(1-4^q epsilon)^(-1)`, with integral joint coefficients and growing epsilon-degree valuations. These estimates establish joint Gauss convergence, not just convergence at individual parameter values. The `q=0` remainder is identically zero.

After `epsilon=2^24 eta` and `x=10202+2^15 Z`, the exact identity is

`K_eta=(1-2^24 eta)Khat+eta W+2^25 eta^2 R1`.

Here `W=S/2^154` reduces coefficientwise to 1. Localization makes its nonconstant `Z` coefficients divisible by `2^15`. The same localization makes `dR1/dZ` divisible by `2^15`. Integral joint restricted series have integral parameter divided differences, so the three terms in the difference of half-derivatives have valuation gains at least 24, 14, and 39. Consequently the critical point satisfies

`v(c(eta)-c(theta)) >= v(eta-theta)+14`.

At a fixed `Z`, the value difference is `(eta-theta)` times a unit. Motion from one critical point to the other has valuation at least twice the displayed distance because the stationary Taylor expansion has no linear term. If `n=v(eta-theta)>=0`, that error has valuation at least `2n+28>n`. Therefore the parameter increment cannot cancel it, proving the isometry exactly. Its finite residue maps are bijections; compatible lifting gives surjectivity on `Z_2`. Translation preserves the odd quadratic coefficient because the tail is divisible by 4, so the singular root has multiplicity exactly two.

For the source-coordinate addition, on even arguments `q=1` has valuation 153 in both `U` and `V`; `q=0` has valuation 154; the remaining lower terms have valuation at least 155; all upper terms have valuation at least `v2(160!)=158`. On the deep chart the upper bound is coefficientwise stronger: `P_160` has content `v2(90!)+v2(69!)+7=152+7=159`. Thus `U0=U/2^153` and `V0=V/2^153` are analytic units there. The exact identity

`G=2^150 (V0/D) [9^(x+1)U0/V0-1]`

preserves zero multiplicity. Together with the logarithmic derivative equation it gives an equivalent simultaneous-root test without extraneous common zeros. It does not show that logarithmic derivative is nonzero. The generalized address-one valuation `v2(k!)=delta+4+nu` was also checked algebraically.

## Computation and provenance

I audited the supplied generator and verifier code. The author's phase verifier checks 678 scalar coefficients and 584 source coefficients by a separate arithmetic route, then the leaf reductions and critical residue. I did not rerun that larger arithmetic reconstruction. The higher-address checker tests exact finite integer identities, not actual Bernoulli coefficients. The epsilon code's independent eta truncation is valid: degree `m>=2` has normalized valuation at least `26m-27`, so omitted `m>=5` terms have valuation at least 103, above the 94 retained coefficient bits.

My new checker imports no inherited arithmetic code. It verifies the stored mathematical reductions and finite lifts with exact integers. The authoritative bounded run is:

`python next/review/check_stored_outputs.py next/review/certified_run/STORED_OUTPUT_CHECKS.json`

It passed all 76 side leaves, both middle leaves, the W reconstruction and 61-bit lift, the 935/932-bit composition, and both 93-bit epsilon joint lifts. For the latter it checks all four successors at every stage, independently recomputes the depleted critical value, and checks 15 selected isometry pairs per fixed index. Those pairs are corroboration only; the universal isometry is proved above. It also checks the declared input/output hashes in the supplied epsilon and higher-address manifests. The bounded runner manifest validated successfully with `--root`.

Full hashes of the exact proof revisions, coefficients, recenter input, review script, and review output are in `SOURCE_HASHES.json`. The three principal proof hashes are:

| Proof | SHA256 |
|---|---|
| `higher_address/regular_address_transversality.md` | `d9d70efcbfdba6fb28fd91ff4a473af4464752aa9382212c5fa8aaa0acac4d2d` |
| `unit_identity/epsilon_critical_manifold.md` | `d82392057e664032d0a3500f810a131f03d16d32906c9e1c79625e2473ffdd06` |
| `critical_phases/PROOF.md` | `cb255f4def823afb188f3a681b481d913d45b12fcc782604ccdab804271d1de7` |

## Exact remaining gap and strongest safe statement

The new proofs establish the regular-address exclusion and simplicity band, fully resolve the two side phases of terminal 161, and place every possible terminal-161 tangency in one finite cylinder modulo `2^935` in the multiplier. They establish a unique transverse singular member in each covered independent epsilon deformation and remove the common-zero ambiguity in the corresponding source coordinate.

Universal Euler simplicity still requires arithmetic exclusion on the surviving cylinder and the remaining higher/irregular critical strata. In the epsilon formulation the missing assertion is precisely that the unique singular deformation parameter cannot equal the actual `2^(2r-25)`. Neither isometry, arbitrarily large finite agreement, source-unit invertibility, nor finite congruence uniqueness supplies that assertion. The cheapest useful next mathematical check is a proved noncancellation or relative-valuation bound for that arithmetic equality; merely adding more digits to the same finite cylinder does not close the gap.
