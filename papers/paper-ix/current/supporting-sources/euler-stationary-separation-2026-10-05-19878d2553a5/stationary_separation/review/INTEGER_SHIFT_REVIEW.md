# Independent review of the integer-shift contact identities

Date: 2026-10-05. Reviewer: radix_review. This is a focused, read-only audit of the separate integer-shift continuation; it does not change the earlier coefficient or contact reviews.

**Verdict: the exact identities and stated uniform units pass.** They retain nonzero shifted-source and index-jet terms with matching valuations 154 and 155. They do not exclude an actual double contact.

## Exact identity and derivative

The distinction \(Q(x)=x(2x-1)\), \(D(x)=Q(x+1)\) is correct. Direct product cancellation gives

\[
Q(x)P_n(x-1)=Q(x-n)P_n(x).
\]

The source denominator is \(D(x-n)\), so its expansion is

\[
D(x-n)=D(x)-(4x+1)n+2n(n-1).
\]

Consequently the coefficient of \(V\) in the source identity is exactly \(-(4x+1)\). The two source resummations are

\[
2U-(4x+1)V+DG=(9^{x+1}C_9-C_1)/8,
\qquad 8QG(x-1)=9^xC_9-C_1.
\]

Subtracting nine times the second relation from eight times the first proves equation (6):

\[
2U-(4x+1)V+DG=9QG(x-1)+C_1.
\]

The cancellations are analytic identities, with no division by a polynomial asserted at its zero. Restricted convergence permits ordinary differentiation. The derivative in equation (8) retains both \(9QG'(x-1)\) and \(9Q'G(x-1)\), as required, and every other product derivative has the correct coefficient and sign. No half-shift value is used.

## Uniform arithmetic and all relevant remainders

On the actual chart \(x=10202+2^{15}Z\), the first two plain-transform packets give, after division by \(2^{154}\),

\[
C_1/2^{154}\equiv1+11\cdot7\equiv14\pmod{16},
\quad
C_9/2^{154}\equiv1+11\cdot7\cdot9\equiv6\pmod{16}.
\]

Packet 2 begins at valuation 158; subsequent packets are more divisible. Thus both transforms have valuation 155 and units respectively 7 and 3 modulo 8. At \(x-1\), source packets 1 and 0 contribute respectively 3 and 6 modulo 8 after division by \(2^{153}\). Every other packet has value valuation at least 159, proving \(G(x-1)/2^{153}\equiv1\pmod8\).

The inherited index-jet units are \(V/2^{154}\equiv3\) and \(U/2^{159}\equiv7\pmod8\). Hence equation (6) has valuation 154 and unit 5 modulo 8 on both sides. On its right, the normalized contributions are 7 and \(2\cdot7\), with sum 5 modulo 8. The shifted nonzero source is balanced by the surviving index jet.

The exact finite integer product and derivative recurrence confirms

\[
P'_{161}(10202)/2^{153}\equiv5\pmod8,
\qquad P'_{161}(10201)/2^{152}\equiv3\pmod8.
\]

For completeness, their uniformity admits a direct coefficientwise verification. At either integer center, no even falling factor has valuation greater than 7, so every affine factor, after removing its constant valuation, has \(Z\)-slope divisible by \(2^8\). Thus

\[
v_2([Z^k]P_{161}(x_0+2^{15}Z))\ge v_2(P_{161}(x_0))+8k.
\]

After differentiating and dividing by \(2^{15}\), all nonconstant derivative coefficients have valuation at least \(v_2(P_{161}(x_0))+1\). Here the packet values have valuations 160 and 159. This is more than sufficient to preserve both displayed derivative units modulo 8 throughout the chart.

For \(C_1'\), the only packets below valuation 156 are 1 and 161; their contributions after division by \(2^{153}\) are 5 and 3 modulo 8 and cancel. All remaining packets have valuation at least 157. Hence \(v_2(C_1')\ge156\). For \(G'(x-1)\), packet 161 contributes 5 modulo 8 at scale \(2^{152}\), and the packet-1 product derivatives contribute 2 and 4. Their sum is 3 modulo 8; packet 0 begins at valuation 155 and every remaining packet is more divisible.

For \(U'\), packet 2 and packets 161 and 162 all have valuation at least 158 after their weights \(n(n-1)\). The other packets have stronger bounds. The inherited factorial derivative estimates and scalar growth control the entire remote tail, also at the neighboring source chart. Thus all bounds in (9) are uniform and are not inferred from the three controls.

Each of \(9QG'(x-1)\) and \(9Q'G(x-1)\) has valuation 153, with units 5 and 7 modulo 8. Their sum therefore has exact valuation 155. Since \(C_1'\) has valuation at least 156, it cannot cancel this leading value. At actual stationarity, the inherited constrained tangent gives \(V'/2^{155}\equiv7\pmod8\), and the complete left derivative has normalized unit

\[
-(4x+1)(V'/2^{155})-2(V/2^{154})\equiv-7-6\equiv3\pmod8.
\]

The terms \(2U'\), \(D'G\), and \(DG'\) are respectively sufficiently divisible, sufficiently divisible, and zero. The exact identity proves the same unit for the complete right derivative. The units of the two individual right terms alone determine its valuation, not this stronger modulo-8 unit after cancellation; the note correctly uses the full identity at stationarity for the latter.

At \(G=G'=0\), these identities remain consistent: their two sides have valuations 154 and 155 and the same units. Neither ordinary stationarity nor these shift relations imply that the index jets vanish.

## Evidence and precision

I replayed the current checker on exactly the fixed controls \(T=0,718787533,22831001499602523078606181325\). All assertions pass. The replay and pinned mathematical output agree exactly after removing the runtime-only `seconds` field. The current manifest validates. The checker separately assembles the shifted source, plain transforms and weighted index jets before checking both complete identities.

The global precision is 384 bits; ordinary derivatives retain 369 bits. The stationary center is known to 205 bits in \(Z\), or 220 bits in \(x\). The inherited first- and second-derivative bounds, and the same scalar and degree-25 truncation estimates as the parent checker, put all substitution and omitted-tail errors strictly beyond the displayed valuations and unit precisions. The stronger observed units for \(U'\), \(C_1'\), \(C_9'\), and the shifted derivative pair are not promoted to additional uniform theorems.

Replay commands:

```sh
python3 stationary_separation/coefficient/integer_shift/check_integer_shift.py /tmp/radix_review_integer_shift_replay.json
python3 audit_helpers/validate_manifest.py stationary_separation/coefficient/integer_shift/certified_run/manifest.json --root /workspace/scratch/fa86fc5a0e51
```

## Exact revision pins

SHA256 hashes, with paths relative to `stationary_separation/coefficient/integer_shift/`:

| Artifact | Hash |
|---|---|
| `INTEGER_SHIFT_CONTACT.md` | `f4ba0b242dfb46b8bf40dd3f1e8161c2e0064a4981f9e8183b912112f2baf2ed` |
| `check_integer_shift.py` | `9202df533714fabe98de5fceec70baa88544d4c63584309beed5a89f445c87bc` |
| `computation_contract.json` | `2777e0e45ebb23a15d2a905b165e8c6b1c772288899ed7ebd155ddc8861a9d32` |
| `certified_run/manifest.json` | `241975a29882fdcb20785eee86e96278d770b12b3d2e6ae116f7b1b51d208947` |
| `certified_run/results.json` | `4b35c52d13f8090f7fe92b83afd0cd88dee60088f132a93002ad05dbc95f6d18` |

Inherited main proof and packet-dependency hashes are pinned in `COEFFICIENT_REVIEW.md`; those artifacts are unchanged. No mathematical correction is required in this continuation. Actual critical-value nonvanishing remains open.
