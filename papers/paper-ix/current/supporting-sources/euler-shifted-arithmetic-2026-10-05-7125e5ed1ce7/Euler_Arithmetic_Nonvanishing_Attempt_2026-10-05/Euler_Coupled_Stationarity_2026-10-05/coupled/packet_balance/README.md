# Joint Euler cancellation and stationarity: actual packet ledger

This calculation follows the value, stationary point, and curvature together on the actual terminal-161 deep chart. It finds a concrete reason that separate analyses lose information: at the third input, keeping the previous stationary point gives value valuation **74**, while moving to the new stationary point gives **80**. The six extra bits come from cancellation with the displacement correction.

The calculation does not close universal Euler simplicity. It identifies the coupled structure and the actual unit obstruction that remains.

## Inputs and exact contract

Write

r=(17659+2^18 T)2^640-161,
x=10202+2^15 Z,
H_T(Z)=G_r(x)/2^178.

The three ordinary integer inputs are T=0, T=718787533, and T=437396180251114280047565. The last is the least residue of the previously certified tau917 modulo2^80. Their differences from tau917 have valuations0,30,80 respectively.

All arithmetic is exact integer or rational arithmetic. Coefficients are calculated modulo2^320. Each actual depth is checked to have true terminal161 and mu=-154. The scalar packet cutoffs are270,276,284. The inequality

3(Q+1)+1-s2(r)-mu >=320

proves the complete omitted scalar tail vanishes. Localization leaves83 nonzero packets in each case. Local polynomial degrees above21 vanish because the substitution contributes2^(15n). The source satisfies coefficient valuation at least its degree. These are proved truncations, not observed numerical stabilization.

The input checkpoint archive has SHA256
`ea627109549edd95eaf764800135de0f9bf92b2cb6b1dc7b4662117ef6df8766`.
The included prior recenter JSON is used to choose one fixed input, not to replace fresh actual Euler arithmetic.

## Joint result

For each T, the half derivative H_T'/2 has affine reduction with unit slope, hence has a unique stationary point c(T) on this chart. Its residue is computed to141bits. Values below refer to this point, with the precision qualification below.

| T | v2(H_T(c)) | H_T'(c)/2 | v2(H_T''(c)) | Lower/upper value imbalance valuation |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0 modulo2^141 | 1 | 18 |
| 718787533 | 30 | 0 modulo2^141 | 1 | 48 |
| 437396180251114280047565 | 80 | 0 modulo2^141 | 1 | 98 |

The lower q<161 and upper q>=161 packet groups both have raw value valuation160 and raw Z-derivative valuation168. Their second derivatives have raw valuations186 and179, respectively. Thus the upper group controls the curvature. In each of these actual models packet161 alone supplies the leading curvature layer, while all other packets have higher curvature valuation.

Stationarity cancels the two slopes. Value cancellation is a separate unit equation. Dividing the two group values by2^160 gives units L0,U0. Dividing their raw Z-derivatives by2^168 gives units D0,E0. At stationarity,

D0+E0=0,

but a root additionally requires L0+U0=0. The measured relative value obstruction

K=1+U0/L0

has valuations18,48,98. It does not vanish merely because the slope obstruction vanishes.

The determinant tracks both conditions at once:

Delta=L0*E0-U0*D0=-(L0+U0)*D0

at the stationary point. Its valuation is therefore exactly the same18,48,98. This is an exact algebraic relation using actual Euler group units, with the finite residues and their precision recorded in the data.

## Rational residue table

The following are residues modulo2^16 for the T=0 input. Each group contribution is a dyadic rational because dividing an individual group by the final content need not be integral.

| Group | H contribution | H'/2 contribution | H'' contribution |
| --- | --- | --- | --- |
| Lower packets | 10260459197/262144 | 110062947/2048 | 19712 |
| Upper packets | 226611523/262144 | 24154781/2048 | 15778 |
| Total | 40005 | 0 | 35490 |

The two slope fractions sum to65536, while the value fractions sum to40005. This is an explicit actual-Euler countertest to the claim that stationary cancellation alone forces value cancellation.

`normalized_rational_residues.csv` supplies the same table for every retained packet and group at all three inputs. `packet_residues.csv` also records16-bit leading-unit residues and exact valuation data. `packet_ledger.json` retains the full canonical modular numerators and denominator exponents.

## Cancellation by valuation layer

Packets are grouped by their valuations before summation. No conclusion is based on an arbitrary q-order of accumulation. For T=0, the first value layers are:

| Raw valuation layer | Packets q | Valuation of layer sum | Valuation of cumulative sum |
| --- | --- | --- | --- |
| 154 | 0,1 | 158 | 158 |
| 158 | 2 | 158 | 160 |
| 160 | 161 | 160 | 166 |
| 164 | 3,162 | 166 | 168 |
| 168 | 4 | 168 | 170 |
| 170 | 163 | 170 | 171 |
| 171 | 5 | 171 | 174 |
| 174 | 164 | 174 | 175 |
| 175 | 6 | 175 | 177 |
| 177 | 165 | 177 | 178 |

All later value layers leave the last valuation178 unchanged at T=0. For the two deeper inputs, further cancellations raise it to208 and258. The derivative ledger instead continues to the full retained precision. The curvature ledger starts at179 from packet161 and stays there.

The full layer-by-layer tables are in `valuation_layers.csv`, separately for value, half derivative, and second derivative.

## Why the point must move with the cancellation

At the new parameter, evaluate both at its own stationary point and at the previous parameter's stationary point:

| Old to new input | Parameter displacement valuation | Stationary displacement valuation | Frozen-point value valuation | Moving critical value valuation | Correction valuation |
| --- | --- | --- | --- | --- | --- |
| T0 to T30 | 0 | 7 | 14 | 30 | 14 |
| T30 to T80 | 30 | 37 | 74 | 80 | 74 |
| T0 to T80 | 0 | 7 | 14 | 80 | 14 |

At T30 to T80, the lower and upper group displacement corrections individually have normalized valuation27. They cancel to valuation74 in their sum. That total correction then cancels the frozen value through valuation80. An analysis that freezes the stationary point would miss this.

The factor is2 times the stationary displacement valuation, because the quadratic Taylor coefficient is H''/2, a unit. It is not2 times the displacement plus1.

## The reusable finite coupling relation

The uniform finite multiplier template gives

Phi(T,Z)=B(T)H_T(Z)=H0(Z)+T*H1(Z) (mod2^142),

with B(T)=17659+2^18 T. Fresh actual Euler coefficients at all three inputs agree coefficientwise with this finite model. At P=320 the finite-template inequality gives the budget641-ceil(log2(2(161+640)+1))=630bits before normalization, exceeding320.

The coefficient certificate gives:

- H1 is a unit everywhere.
- H1'/2^8 is a unit everywhere; its nonconstant coefficients are even.
- Q=Phi_Z/2 has an affine mod2 reduction with unit Z-slope.

Consequently Q_T=H1'/2 has valuation7. For two parameters separated by valuation n, the stationary equation and the isometry property imply a stationary-point displacement of valuation n+7, for0<=n<134, so that the displacement is visible within the141 retained bits.

For the moving critical value D(T)=Phi(T,c(T)), the direct parameter term has valuation n, while the point-motion correction has valuation2n+14. Thus D changes with valuation n. This finite coupling law follows from the displayed coefficient conditions; the three input comparisons test it in two different displacement regimes.

These statements concern the certified finite model and the actual arithmetic shadows at the stated precision. They do not assert an all-precision continuous interpolation of the undepleted integer-index family.

## Precision at an unknown exact stationary point

Each stored raw residue is calculated exactly modulo2^320 at the canonical stationary residue representative. The true c(T) is known modulo2^141.

Individual group values therefore have only309 certified raw bits at the exact point, because their Z-derivatives start at valuation168. The individual scaled value units L0,U0 have149bits. Individual slopes and curvatures retain320rawbits, as independently checked from the coefficients.

The total critical value retains all320rawbits: its linear variation vanishes and the quadratic displacement error is beyond320. Thus the normalized critical value has142bits. The leading valuations0,30,80 are decisive.

The unit-balance record explicitly separates representative precision152, individual value-unit precision149, and derivative-unit precision152. The obstruction itself safely retains152bits through the dependence-aware identities. Indeed F=L0+U0 is known to160bits and has valuation at least18. Therefore F/L0 is known to at least min(160,149+18)=160bits, and -F*D0 to at least min(160,152+18)=160bits. Recording152 obstruction bits is conservative. This does not give152bits for L0 or U0 separately.

## Reproduce and verify

Run `python build_ledger.py`, `python export_tables.py`, and `python verify_ledger.py`. Everything needed is included. The independent verifier reconstructs retained packet coefficients by direct binomial Taylor expansion of global skeleton polynomials, uses separate Bernoulli/source implementations, checks every omitted local packet's valuation bound, independently lifts each stationary residue, and verifies the cumulative valuation layers and point-motion countertests.

The bounded replay contract and manifest are under `computation_contract.json` and `certified_run/`. The source coefficient certificate is exact arithmetic. No Lean compiler was run.
