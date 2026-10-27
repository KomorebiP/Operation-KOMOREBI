# Independent staged correction audit

Date: 2026-10-07. This review supplements `CLAIM_AUDIT.md`; it does not replace or edit the hash-pinned raw-source audit. The numerical task stages corrected files under `release/Komorebi_Quadratic_Form_KCOS_Final_2026-10-07/engine`.

**Normalized claim.** Within the supported positive central backend domain, authoritative logarithmic endpoints are serialized outward; acceptance proves the exact requested multiplicative tolerance using directed arithmetic; and the matrix bridge retains those outer endpoints without ambient-precision loss.

**Final primary verdict: conditional on a named input.** The corrected finite-input positive central route meets its stated enclosure and multiplicative-accuracy contract conditional on correctness of `mpmath.iv` 1.3.0's interval operations, the recorded exact binary endpoint representation, and Python's integer/Decimal arithmetic. All identified serialization, acceptance and input-domain gaps are repaired in the hash-pinned final revisions below. The first staged patch had repaired ambient-precision endpoint parsing and point-arithmetic acceptance; a subsequent source check discovered the remaining ordinary-`str(iv)` serialization gap, which was repaired before this final verdict.

## Fresh decisive serialization evidence

Installed `mpmath/libmp/libmpi.py` defines `mpi_str` by printing both binary endpoints with ordinary `to_str` at `prec_to_dps(prec)+5` decimal digits. This supplies enough digits to recover the same binary value, but the resulting literal decimal may lie inside an endpoint. `ctx_iv.py` uses this function for `ivmpf.__str__`.

At `iv.dps=15`, `iv.mpf(0.1)` represents the exact binary64 singleton

`3602879701896397 / 36028797018963968`.

Its printed interval is

`[0.10000000000000000555, 0.10000000000000000555]`.

Exact Python `Fraction` comparisons prove that this literal interval excludes the exact binary64 input. A second witness, `iv.mpf(1)/3`, prints both endpoints slightly inward relative to its exact binary bounds. These are executed exact comparisons, not comparisons against a rounded numerical reference.

## Already reviewed repairs

| Obligation | First staged patch result |
|---|---|
| Preserve literal tail endpoint strings through matrix wrapper | Passed. `_parse_log_interval` returns strings, and the combined bracket uses them directly. |
| Exact requested tolerance | Passed. Validation uses `Decimal`, and acceptance parses the original decimal tolerance with interval arithmetic. |
| Directed width and ratio decision | Passed. `iv.expm1(iv.log(10)*(right-left))` supplies an interval; acceptance uses `ratio.b <= tolerance.a`. |
| Conservative subordinate tolerance | Passed. Directed multiplication supplies a lower budget for each endpoint-tail solve. |
| Tail-domain checks | Passed. Coefficients, query, tilt, support and Chernoff-domain inequalities are checked using directed interval endpoints. |
| Serializer of underlying IV endpoints | Initially failed. `str(iv)` was still used for authoritative endpoints and norm caps. |
| Concurrent interval calls | Scope restriction. `mpmath.iv` has a shared global precision context; these routines must be run sequentially or guarded by a lock. |
| Floating summary fields | Display only. `log10_lower`, `log10_upper`, float width and float ratio fields are not authoritative outward bounds; the literal directed interval is the numerical contract. |

The earlier ambient-precision counterexample was executed successfully after the numerical task exposed its dependency directory. In the original helper, `[-1.00000000000000000001,-0.99999999999999999999]` becomes `[-1,-1]` with zero width. In the first staged helper the literal endpoints are retained and the directed ratio upper is approximately `4.6051701859880913681e-20`; a requested `1e-20` is rejected consistently at ambient point precisions 10, 15 and 50 digits.

The negative-threshold restriction also has an executed raw-source witness: `interval_positive_logsf('-1', ['0.02']*80, theta_decimal='1', upper_decimal='10', eta_decimal='2', K=128, interval_dps=60)` returns `passed_positive_sum=True` and a log10 interval approximately `[0.00837400943, 0.01131716573]`. Since the quadratic form is nonnegative, its true tail at `q=-1` is exactly one and its log10 probability is exactly zero. Thus the unguarded raw entry point is refuted outside the positive-support query contract. The staged nonnegative-query guard repairs this boundary.

## Required outward conversion

For each finite internal binary endpoint `(sign, mantissa, exponent, bitcount)`, form its exact integer numerator and power-of-two denominator. Convert that ratio to a decimal under `ROUND_FLOOR` for a lower endpoint and `ROUND_CEILING` for an upper endpoint. This proves outward decimal enclosure without depending on decimal display round trips. Apply this conversion to every authoritative backend interval, spectral norm cap, final spectral endpoint, ratio upper and width upper. Preserve already serialized literal endpoints subsequently.

The first staged review did not modify source files during the numerical task's hash-pinned test runs. The serializer witnesses and exact correction were communicated immediately to that task and the parent.

## Final patch review, 2026-10-07

| Final staged file | SHA-256 |
|---|---|
| `directed_accuracy.py` | `50e3c263fd75affdcf1f00f69fea78fbd4e3532a3c55771370dc14ba4bd7365c` |
| `interval_kcos.py` | `e1fb7e4f473c7208617b24779f2caf71996137d8aa8bd35b6d1f575ad29003f8` |
| `accuracy_driven.py` | `79b050867b07a9b6e25fbaa7a7259349602f1e7038fcccef39c148b194fc71b5` |
| `verified_spectrum.py` | `e5ef7a6c8e55dd41cc10c7a62033c24708194300736ceca4c3f208b7eea9e51f` |
| `test_directed_contract.py` | `79510483e8e873bf67440d946cf51d9f8d38a70069e35db7153af313b36e0538` |

The final `_outward_binary_endpoint` forms exact integer numerators and power-of-two denominators from the finite binary endpoint tuple and divides their exact `Decimal` representations under separately specified floor/ceiling rounding. `outward_interval_string` applies the correct direction to each endpoint. The backend uses it for the final logarithmic interval, finite sum and all error-bound ledgers; the spectral verifier uses it when extracting norm caps and final spectral endpoints. Candidate eigensolver decimals remain design points checked by the spectral postcheck, so their ordinary point serialization is permitted.

The matrix bridge preserves final literal lower/upper tail strings without converting them through point arithmetic. The directed acceptance predicate is evaluated before returning a certificate. The reported ratio upper and width upper also use outward serialization. The subordinate tail tolerance is obtained from a directed lower product bound. Remaining ordinary-precision quantities choose refinement steps or report display summaries; they do not accept a certificate or change authoritative interval endpoints.

Independent executed controls in this audit used exact `Fraction` representations of binary endpoint tuples. At interval precisions 15, 50 and 120 digits, outward serialization contained both exact binary endpoints for a binary64 `0.1` singleton, positive/negative thirds and `1e-5000`. At ambient point precisions 10, 15 and 50 digits, the endpoint-collapse witness was consistently rejected at requested tolerance `1e-20`. These checks are separate from the numerical task's unit suite.

The numerical task's final records were inspected: seven finite-input manifests record unchanged input hashes and successful process exits; their suite total is 57/57 including nine new directed-contract regressions. A subsequent nonfinite-only guard correction adds the library's separate negative-infinity endpoint tag and one regression; the replacement directed suite passes 10/10, giving the final total 48 production tests plus 10 directed regressions = 58/58. The finite branch is unchanged. The original seven finite-input evidence hashes are preserved; a final source-hash sidecar records the guard amendment. The finite runs pin the previous `directed_accuracy.py` hash `6d850a3cfc09ffbbe7ce9f14acc772137c7b58f01917d7828059c22a80be1cf8` and previous test hash `1d4673ef966ef3f44f9a830d77a3f689c0cf382f1fd04a78d874dfb08e9a0f27`, rather than pretending the nonfinite amendment was included in those earlier executions.

The fresh scaled-chi-square control near `10^-5000` has requested tolerance `1e-18`, achieved directed ratio upper approximately `9.20141498e-20`, and full containment of the independent finite Erlang-expression interval. The fresh exact-binary 64-by-64 matrix control near `10^-16` has requested tolerance `1e-12` and achieved directed ratio upper approximately `2.78293919e-15`. These remain finite test cases; the earlier mathematical comparison proves their interpretation rather than unit-test success alone.

Independent nonfinite guard checks confirm outward strings for `[-inf,+inf]` and singleton negative/positive infinity and rejection of raw string `nan` endpoints. An initial check supplied `float('nan')`; `mpmath.iv` converts that value to the entire interval before serialization, so expecting a serializer exception was incorrect. Inspection of the raw tuple explains the result, and the directed acceptance rejects that entire interval. There is no NaN false certificate.

## Trust base and remaining boundaries

- The probability enclosure remains conditional on correctness of the interval library's directed arithmetic and transcendental routines. This review checks their use and exact serialization, not the complete library implementation or hardware.
- The serializer uses the exact `_mpi_` tuple representation recorded for `mpmath` 1.3.0; dependencies must stay pinned or that representation must be rechecked.
- Python arbitrary-precision integer shifts and `Decimal` floor/ceiling division are part of the trust base.
- `mpmath.iv` has shared global precision. Calls must remain sequential or acquire a shared lock. Independent subprocess test runs do not imply thread-safe concurrent API use.
- Authoritative enclosures use the outward literal `log10_interval` strings. Float summary fields can round inward and are display values.
- Supported manual backend inputs are finite decimals, positive eigenvalues, rank greater than two, `q>=0`, `U>q`, `K>=1`, and proved strict tilt-domain inequalities. The planner's supported query is stronger: `q` is above the positive spectrum's mean. Matrix acceptance needs both endpoint-tail routes to succeed and more than two positive lower coefficients.
- Unsupported inputs may raise explicit validation exceptions. The serializer handles both infinity tags and rejects raw NaN endpoints. If the interval library has already conservatively widened an invalid float to the entire real interval, that interval is serialized as such and the acceptance decision rejects it. Original finite-decimal NaN inputs are rejected before computation.
- Packetized, signed and noncentral floating routes still provide analytic bounds and finite numerical evidence. Their ledgers are not the directed machine-enclosure contract reviewed here.
- Streamed range-core/residual theorems remain exact mathematical results. A fully directed large-scale streamed matrix-to-tail implementation is outside this release's verified dense bridge.
