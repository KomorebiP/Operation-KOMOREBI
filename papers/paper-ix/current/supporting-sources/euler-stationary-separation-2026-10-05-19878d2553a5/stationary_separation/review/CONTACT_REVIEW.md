# Independent review of actual source contact and exterior cancellation

Date: 2026-10-05. Reviewer: radix_review. Author files were read only. Scope: `contact/SOURCE_CONTACT_AND_EXTERIOR.md`, its exact source and chart dependencies, checker and current certified run. The fixed target remains `stationary_separation/TARGET.md`.

**Verdict: the source-contact and exterior claims are proved as written.** The actual logarithmic mismatch has a unique zero on each admitted chart. Its coincidence with the Euler stationary center is equivalent to the unresolved zero critical value. The proposed strict exterior dominance is false for the actual family, but this is not an Euler counterexample and does not settle universal nonvanishing.

The quantifiers are the admitted ordinary parameters \(r=(17659+2^{18}T)2^{640}-161\), \(T\ge0\), with true terminal 161, and \(x=10202+2^{15}Z\), \(Z\in\mathbb Z_2\). The three computed controls do not provide coverage of that infinite family.

## Source elimination and normalization

The cancellation of the last packet factor gives, for \(q\ge1\),

\[
P_q(x)A(x-q)=P_{q-1}(x)\frac{9^{x-q+1}-1}{8}.
\]

Together with the zeroth packet this proves \(8QG=9^{x+1}U-V\), with the definitions in the note and \(Q=(x+1)(2x+1)\). Restricted convergence follows from the fixed-parameter scalar decay. The chart has \(Q\) a unit. The normalized source-free tails \(u=2^{-153}U\), \(v=2^{-153}V\) are restricted units, so their inverses and logarithmic derivatives introduce no common-zero exception.

For \(F=9^{x+1}u/v-1\) and \(M=L+u'/u-v'/v\), direct differentiation yields \(M=F'/(1+F)\). Since \(F\) is a nonzero constant times an analytic unit times \(G\), the simultaneous equations \(G=G_x=0\) are exactly \(F=M=0\).

I independently checked the sign and every scaling in the exterior:

\[
W=UV'-U'V-LUV=-UV M,
\]

\[
2^{-305}(UV'-U'V)=\sum_{i<j}(9^{-i}-9^{-j})(v_i d_j-d_i v_j),
\quad d_i=2v_i'.
\]

The normalized logarithmic term is \(2Luv\). It is essential and is not an exterior minor.

## Uniform leading units and the infinite pair tail

The decisive packet calculation was reconstructed directly. Write \(x=90+128a\), \(a=79+256Z\). Removing the factor \(x-90\) from the falling product in \(P_{160}\) leaves valuation

\[
v_2(90!)+v_2(69!)=86+66=152
\]

and normalized odd part \(-5\cdot5\equiv7\pmod8\) at 90. Moving to \(90+128a\), the pair with differences \(\pm64\) multiplies it by \(1-4a^2\equiv5\pmod8\); all other paired and unpaired factors multiply it by 1 modulo 8. The logarithmic derivative correction from the \(\pm64\) pair is \(8a^2/(4a^2-1)\), and all the remaining corrections are also divisible by 8. The odd packet factors contribute 1 modulo 8 and more divisible derivative terms. Therefore

\[
v_2(P_{160})=159,\qquad P'_{160}/2^{152}\equiv3\pmod8.
\]

These are coefficientwise statements on the affine chart: after removing constant valuations, the local slopes are sufficiently divisible, and the denominators used above are restricted units.

The inherited actual coefficients then give

\[
v_0=2,\ d_0=0,\quad v_1\equiv5,\ d_1/2\equiv1,\quad
v_2(v_{161})=6,\ d_{161}\equiv3\pmod8.
\]

Here \(v_2(v_{161})\) denotes valuation, not the packet with index 2. The two retained pairs have normalized valuations 4 and 5 and respective units 3 and 1 modulo 8. Their sum divided by \(2^4\) is \(3+2=5\pmod8\).

The rest of the pair sum is coefficientwise divisible by \(2^8\). This includes the potentially close pair \((1,161)\), whose weight has valuation \(3+v_2(160)=8\), and the pairs involving packet 2 or 162, whose derivative gain supplies the required bound. The lower ranges have the stated scalar bounds. The upper range factors through \(P_{162}\), with local value valuation 160 and ordinary derivative valuation 153. Beyond the next scalar carry, the additional falling factors supply at least one factor 2 per two factors, and differentiation can remove at most one of these factors. This controls the entire tail even using only coefficient integrality. Scalar decay also justifies convergence and rearrangement of the double series.

Finally \(u\equiv v\equiv7\), \(2u'\equiv2v'\equiv5\), \(L/8\equiv5\pmod8\). Consequently

\[
v_2(W_{\rm geo})=v_2(LUV)=309,
\qquad W_{\rm geo}/2^{309}\equiv LUV/2^{309}\equiv5\pmod8.
\]

The strict-dominance proposal fails after retaining the actual logarithmic term.

## The two centers and the exact residual scalar

Put \(B=Q/v\), \(A_{\rm crit}=K_Z/2\), \(D=B_Z/(2B)\). The normalized derivative calculation gives

\[
2B'/B=2Q'/Q-2v'/v\equiv7\pmod8,
\qquad D/2^{13}\equiv7\pmod8.
\]

The derivative of \(v\) in \(Z\) has coefficientwise valuation 14, from packet 161; \(Q_Z\) has valuation 15. Hence these are restricted-series bounds, sufficient to control differences and roots, rather than merely pointwise congruences.

From the source identity,

\[
F=2^{28}BK,\qquad
M=\frac{2^{14}B}{1+F}\bigl(A_{\rm crit}+DK\bigr).
\]

The inherited quadratic chart has \(A_{\rm crit}\) with odd affine coefficient and even higher coefficients. The correction \(DK\) is coefficientwise divisible by \(2^{13}\). Thus \(J=A_{\rm crit}+DK\) has an odd divided difference everywhere on \(\mathbb Z_2\), is an isometry and has a unique zero \(\zeta\). All the other factors in the displayed expression for \(M\) are nonzero. This proves existence and uniqueness of the actual mismatch zero.

At the Euler stationary center \(c\), let \(\Phi=K(c)\). Then \(J(c)=D(c)\Phi\). Isometry gives the exact identity

\[
v_2(\zeta-c)=13+v_2(\Phi),
\]

including infinity on both sides. In particular \(\zeta=c\) if and only if \(\Phi=0\). For \(\Phi\ne0\), the inherited unit quadratic distance law gives

\[
v_2(K(\zeta)-\Phi)=26+2v_2(\Phi)>v_2(\Phi),
\quad v_2(F(\zeta))=28+v_2(\Phi).
\]

The exterior normalization independently gives

\[
W(c)=2^{333}\Theta(c)\Phi,
\quad \Theta=-\frac{uQ(D/2^{13})}{1+F}\equiv1\pmod8.
\]

Indeed \(-7\cdot7\cdot7\equiv1\pmod8\). Thus the first 24 bits of cancellation relative to the separate valuation-309 terms are automatic at stationarity; all further cancellation is exactly the unknown critical scalar. An upper bound on its valuation is not produced. Equivalently, \(F(\zeta)=0\) would force \(G=G_x=0\) at \(\zeta\), hence \(\zeta=c\). The two-center formulation preserves the original obstruction precisely.

## Computation and precision audit

I reran the current checker on exactly the three specified controls. All assertions pass, and the mathematical output agrees exactly with the pinned result after removing the runtime-only `seconds` field. The current manifest validates. The source-free \(U,V\) are assembled directly from packets, and the complete exterior polynomial is built with the logarithmic term. Its zero is lifted independently of the zero of \(K_Z/2\).

| \(v_2(\Phi)\) | \(v_2(\zeta-c)\) | \(v_2(W(c))\) | \(v_2(F(\zeta))\) |
|---:|---:|---:|---:|
| 0 | 13 | 333 | 28 |
| 30 | 43 | 363 | 58 |
| 91 | 104 | 424 | 119 |

The 384-bit source-free coefficients leave 231 bits after division by \(2^{153}\), and 217 bits for twice the ordinary derivatives after the further 14-bit division. The exterior is computed to 200 normalized bits. Its coefficientwise factor \(2^{15}\) leaves 185 bits for its zero; the independent Euler critical center has 205 bits. Both exceed every displayed center-distance valuation.

Omitted scalar coefficients vanish at 384 bits even after ordinary differentiation because the packet derivative is integral. Omitted local degrees begin with slope factor \(2^{390}\); normalization and differentiation still leave more than 200 bits. At the true Euler center, substitution by the 205-bit representative changes the normalized exterior only at valuation at least 220. At the exterior center, \(F_Z\) is divisible by \(2^{29}\), so even its global first-derivative bound makes substitution by a 185-bit representative stable beyond 200 bits; vanishing of \(F_Z\) at the true center strengthens this further. Raw valuation 424 does not conflict with 384-bit input precision: the product's known factors and the normalized computation leave sufficient absolute precision.

Replay commands, from the workspace root:

```sh
python3 stationary_separation/contact/check_source_contact.py /tmp/radix_review_contact_replay.json
python3 audit_helpers/validate_manifest.py stationary_separation/contact/certified_run/manifest.json --root /workspace/scratch/fa86fc5a0e51
```

## Exact revision pins

All hashes are SHA256; contact paths below are relative to `stationary_separation/`.

| Artifact | Hash |
|---|---|
| `contact/SOURCE_CONTACT_AND_EXTERIOR.md` | `92e57af24ff9b7cbeb4e350e28e9c0c46c5993f8743755b484d3e3b9762289cb` |
| `contact/check_source_contact.py` | `b75d211132eeb29da9b0bde50db5141008a5fb5beffd0529514d67765ca4ce7e` |
| `contact/computation_contract.json` | `2df28955f1fb37a5ae9b2d3d75f730e657904a5ff8ce4ca36edcffc5395d4f12` |
| `contact/certified_run/manifest.json` | `ac69c5b6acd467388b8245ec2e67625b086553e6b479735c7bff56d59ad5eba5` |
| `contact/certified_run/results.json` | `40fdbe63a84c143f87151f7e45ba2e615bf662a5434a85f7012b1a195f10f244` |
| inherited `next/unit_identity/epsilon_critical_manifold.md` | `d82392057e664032d0a3500f810a131f03d16d32906c9e1c79625e2473ffdd06` |
| inherited `CARRY_ADAPTED_SEPARATION.md` | `d18c3b64b54ea55c3139e1b9ee39c23bfcd6bbaea1827c5d69ea2224bb404e6e` |
| inherited `CONSTRAINED_TANGENT_AND_CONTIGUOUS_CONTACT.md` | `84e3cf9cd9394fe2d4a1847ccf1011785cd9f6c2c8bc0262b55d3c64f329f0b2` |
| imported `fast_parameter_certificate.py` | `0cd496447400a883da1c151296c3164ce265b362cd7dbbe6b785c9101c0881d6` |
| imported `build_parameter_certificate.py` | `b8a06660d533e4812d072f5b04e1332a3572557d74aae76abce3104568018076` |
| imported `check_critical_value.py` | `c92e9ccbe0b33ce39100943c64b872b3a5d0bea9a5e3bc26d3b317106f9ac043` |

No substantive correction is required in the audited note. The universal assertion \(\zeta\ne c\), equivalently the actual critical-value nonvanishing assertion, remains unproved.
