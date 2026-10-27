# Independent review of the full prescribed coefficient recurrence

Date: 2026-10-05. Reviewer: radix_review. Scope: the frozen main proof, its inherited packet inputs, current checker and evidence; the corrected source-product note is reviewed separately below. Author files were not edited. The fixed target is `stationary_separation/TARGET.md`.

**Verdict: the auxiliary identities, valuation statements and precision claims in the current main proof are proved as written. They do not exclude an actual double zero.** The two nonzero forcing jets are balanced by the two nonzero coefficient-index jets. The universal Euler critical-value nonvanishing target remains open.

## Exact scope and obligations

All uniform claims here concern ordinary parameters

\[
r=(17659+2^{18}T)2^{640}-161,\qquad T\geq0,
\]

with true terminal 161, and the chart \(x=10202+2^{15}Z\), \(Z\in\mathbb Z_2\). Statements at a stationary point impose the additional condition \(G_x=0\). No extrapolation from the three finite controls is used.

| Obligation | Independent finding |
|---|---|
| Beta-only cubic and full cutoff | Exact formal identities, including every cross-boundary term |
| Transfer of products and derivatives | Operator composition and full ordinary derivative both retained |
| Actual forcing | \(E/2^{155}\equiv3\pmod8\) on the chart; \(v_2(E_x)=156\), \(E_x/2^{156}\equiv3\pmod4\) at stationarity |
| Actual nonlinear source square | \(H^2A/2^{307}\equiv5\pmod8\), \(v_2((H^2A)_x)=306\) on the chart |
| Linear and nonlinear remainders | \(v_2(R)\ge159\), \(v_2(R_x)\ge158\), \(v_2(N),v_2(N_x)\ge3r\) |
| Numerical precision | Sufficient for every reported valuation and low unit; does not identify an exact center from a finite residue |
| Double-zero exclusion | Not obtained: the exact equations remain compatible with \(G=G_x=0\) |

## Algebraic reconstruction

For \(g=\sqrt t\coth\sqrt t\) and \(f=(\sqrt t/\sinh\sqrt t)^2\), the identities \(\theta f=f(1-g)\) and \(g^2=f+t\) give

\[
(\theta f-f)^2-tf^2-f^3=0.
\]

Writing \(f=p+t^rB\), \(a=\theta p-p\), \(W=(r-1)B+\theta B\), direct expansion gives

\[
F_r+2aW-(2tp+3p^2)B+t^r[W^2-(t+3p)B^2]-t^{2r}B^3=0.
\]

The numerator defining \(F_r\) has zero coefficients below degree \(r\), so it is a finite rational polynomial after division by \(t^r\). Using \(\beta_1=-1/3\), \(\beta_2=1/15\), the degree-one terms in both linear kernels cancel, and their degree-two coefficients are exactly \(2/15\) and \((2r-3)/15\).

The identity \(P_i(x)P_j(x-i)=P_{i+j}(x)\) proves \(T_kT_l=T_{kl}\). It gives no pointwise product law for \(T_kA\). With \(\sigma=2^{154}/\beta_r\), the normalization and signs yield exactly

\[
E=2V+(2r+1)G-R-N,
\qquad E_x=2V_x+(2r+1)G_x-R_x-N_x.
\]

The second equation differentiates both the packet polynomial and the shifted source. The coefficient multiplier \(q\) in \(V\) is not ordinary differentiation in \(x\).

## Valuation reconstruction

The imported tangent proof supplies \(V/2^{154}\equiv3\pmod8\), and at stationarity \(V_x/2^{155}\equiv7\pmod8\). I checked its decisive cancellation: after using \(G_x=0\), the normalized contributions from packets 0, 2 and 162 are \(-1,4,4\pmod8\); their sum is 7. The upper packet cannot be discarded.

The global bounds \(G,V\in2^{153}\mathbb Z_2\) and \(G_x,V_x\in2^{151}\mathbb Z_2\) follow from the actual coefficient estimates and

\[
v_2(P_q)\ge v_2(q!),\qquad
v_2(P'_q)\ge v_2(q!)-\lfloor\log_2q\rfloor.
\]

For the lowest upper packet, the latter is \(158-7=151\). Both remainder kernels start at degree two. Their factors \(8^j\), and \(v_2(P_2)=1\) on this chart, then give the stated bounds for \(R,R_x\).

For \(N\), the essential factor is \(\lambda=\sigma^{-1}=\beta_r/2^{154}\), of positive valuation. The last 640 binary digits of \(r\) already have 638 ones. After normalizing \(B,W\), the weighted coefficient kernels are integral and converge; quadratic and cubic cutoff terms retain factors \(\lambda8^rP_r\) and \(\lambda^28^{2r}P_{2r}\). Ordinary derivatives of their remaining restricted integral series are integral. Hence the bound \(3r\) is valid. In particular, the low valuation of \(H^2A\) is not the valuation of the cutoff term \(N\); the large cutoff factor must be retained.

For the actual square, \(\delta_q=\sum_{i+j=q}\gamma_i\gamma_j\). The first three coefficient valuations are 308, 308, 306. Packet 2 gives the unique lowest value valuation 307 and derivative valuation 306. The normalized value contributions of packets 0, 1 and 2 modulo 8 are 2, 4 and 7, with sum 5. The source factor in the differentiated packet 2 has higher valuation; \(P'_2\) is odd.

The entire tail was checked, rather than only the leading packets:

| Range | Value lower bound | Derivative lower bound |
|---|---:|---:|
| \(3\le q\le160\) | 315 | 311 |
| \(q=161\) | 315 | 308 |
| \(q=162\) | 314 | 307 |
| \(163\le q\le321\) | 321 | 310 |
| \(q\ge322\) | 319 | 311 |

The q=161 and q=162 derivative bounds use the unique nearest factor of valuation 7 on this chart. The last entry uses \(v_2(322!)-\lfloor\log_2322\rfloor=319-8=311\). The author's earlier displayed equality to 310 was an arithmetic typo; it has been corrected in the audited revision. The weaker bound would not have affected the theorem.

Since \(G\) is coefficientwise divisible by \(2^{178}\) on the chart, the forcing claims now follow directly. At double contact, however, the exact equations read

\[
E=2V-R-N,\qquad E_x=2V_x-R_x-N_x.
\]

Their leading valuations are respectively 155 and 156 on both sides. Thus the new units certify the balance, not a contradiction. Similarly \(H^2A\) has valuation 307 whereas \(G^2\) is divisible by \(2^{356}\); replacing the first by the second would change the actual equation.

## Computational evidence and its limits

I reran the current checker independently and validated the current manifest. The replay agrees with the pinned mathematical results exactly after removing the runtime-only `seconds` field. It checks the cubic through degree 31, 170 exact rational cutoff coefficients for ordinary cutoffs 3 through 12, and the three existing controls \(T=0,718787533,22831001499602523078606181325\). Their critical-value valuations remain 0, 30 and 91. No new parameter search is performed.

The forcing is computed through its proved identity; this is not an independent reconstruction of the enormous finite prefix. The checker uses 384 global bits, 206 normalized local bits and a critical center modulo \(2^{205}\) in \(Z\). The corresponding physical-center error is divisible by \(2^{220}\). Global second-derivative bounds 144 for \(G,V\) and 290 for \(H^2A\) put ordinary derivative substitution errors at valuations at least 364 and 510. These exceed all claimed precisions. Ordinary differentiation loses 15 bits when passing from \(Z\) to \(x\); this loss is respected.

Scalar packet tails vanish at the working precision. Local degrees at least 26 carry \(2^{390}\) before the ordinary-derivative loss, and omitted linear kernels of degree at least 129 carry \(8^{129}\). The new defensive assertions for source decay, even derivative coefficients, the affine-isometry parity and \(c\equiv20\pmod{128}\) are consistent with the established prerequisites and pass.

Replay commands, from the workspace root:

```sh
python3 stationary_separation/coefficient/check_full_recurrence.py /tmp/radix_review_coefficient_replay.json
python3 audit_helpers/validate_manifest.py stationary_separation/coefficient/certified_run_pinned/manifest.json --root /workspace/scratch/fa86fc5a0e51
```

`certified_run_pinned` is current. The earlier `certified_run` and `certified_run_final` are superseded and are not the evidence pinned by this review.

## Corrected optional source-product note

The corrected `product/NEWTON_SOURCE_PRODUCT.md` is not a dependency of the main forcing theorem. Its present claims pass a separate direct algebraic check. The source map is injective by triangular evaluation at nonnegative integers; its transported product has identity \(A\), and its transported coefficient derivative is not the ordinary derivative. The unsourced Newton product identity is stated with its own map and is not falsely conjugated into the sourced one.

For the displayed polynomial kernel

\[
h(t)=1-\frac5{24}t+\frac3{128}t^2+\frac{35}{1024}t^3,
\]

I reconstructed \(H(1)=H'(1)=0\), while \((H\star H)(1)=-5/3\). The ordinary quadratic coefficient is exactly

\[
\frac{395}{108}-\frac{475}{288}\log9,
\]

and has valuation \(-1\). This correctly disproves closure of the ordinary double-zero ideal under the transported product. It is an explicitly constructed source-kernel counterexample, not the actual Bernoulli tail and not an Euler nonvanishing result. Earlier erroneous source-conjugation claims are absent from the audited revision.

## Exact revision pins

All hashes below are SHA256.

| Artifact | Hash |
|---|---|
| `TARGET.md` | `7fa6e8993e43d6cbafdc39916924b5854cac2403089a1f82f71fe6ec1393cd2c` |
| `coefficient/FULL_RECURRENCE_CONTACT.md` | `6e7e29cdc4e0a6e0d85b630610174786f3bcff819bbd82d72cfcb68fc82b93dc` |
| `coefficient/check_full_recurrence.py` | `17218de11b33cf9da7d7dc3c2c2049fe64db55ca12bf3930ed3ad3612800f1a3` |
| `coefficient/computation_contract.json` | `3255b67c0f4d6f14e4c0090ee11b5d88648dde3a8d2dae9dc883e2ca3951da41` |
| `coefficient/certified_run_pinned/manifest.json` | `de34bcd5ef53e46d57f02c959b35395c36c7322cca3cb01c31ed2df6b176d896` |
| `coefficient/certified_run_pinned/results.json` | `2f20c8596d686c3e2fb0daca703c9c62078da8c7c38d6999c3143b921c6e6d18` |
| `coefficient/product/NEWTON_SOURCE_PRODUCT.md` | `202ff3235d81b92ad2a718fd1b5ff30b41533aa652ec2d60458284050a6fb3e1` |
| inherited `CONSTRAINED_TANGENT_AND_CONTIGUOUS_CONTACT.md` | `84e3cf9cd9394fe2d4a1847ccf1011785cd9f6c2c8bc0262b55d3c64f329f0b2` |
| inherited `check_carry_adapted.py` | `9cbc368f0f0833d705d43eeba1f4eff8298286e5db75b58a56ccd7f07986195d` |
| inherited `vendor/euler_packet_engine.py` | `c92e9ccbe0b33ce39100943c64b872b3a5d0bea9a5e3bc26d3b317106f9ac043` |

The main theorem is an exact account of the recurrence's local cancellation. A further argument excluding the actual coincidence of criticality and zero value is still required; it is not supplied by either forcing jet or by the nonlinear square unit.
