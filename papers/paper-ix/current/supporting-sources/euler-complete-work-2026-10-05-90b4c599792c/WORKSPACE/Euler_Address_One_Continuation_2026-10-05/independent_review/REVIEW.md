# Independent audit of the address-one exclusion and recentered parameter certificate

Date: 2026-10-05. Reviewer: a fresh delegated proof-audit session, with a separately delegated arithmetic replay. Author files were read without modification. The reviewer independently reconstructed the critical implications from the raw proofs and packet definitions; agreement with the authors is not itself evidence of correctness.

**Normalized target.** For every ordinary integer depth `r >= 1`, every root of the actual signed Euler residual `G_r` in `Z_2` is simple. Here `G_r=2^(-mu_r) sum_q 8^q(beta_(r+q)/beta_r)P_q A(.-q)`, `mu_r=min_q(3q+s2(r+q)-s2(r))`, the coefficient ring is the restricted Tate algebra `Z_2<X>`, and differentiation is formal/analytic differentiation in the argument.

**Primary verdict: incomplete, with the smallest missing implication identified below.** Neither audited artifact proves the normalized universal target, and both correctly disclaim that conclusion. I found no failed implication in their narrower assertions under their explicitly stated inherited Euler hypotheses. The structural address-one theorem is proved from its displayed hypotheses. The recentered finite interval result is a valid computer-assisted deduction conditional on the inherited exact packet/source identities and the old global certificate, as the manuscript states.

## Audited claims and exact revisions

The structural claim quantifies over genuine address-one walls: `j` is the true terminal label, the last lower minimizing address is exactly 1, `k=j-1=2^t c` with `c` odd, `t>=4`, `D=t-4`, and the specified normalized recurrence and regular complement form hold. For `delta>=1`, any multiple dyadic root must lie in a root-free complement disc and satisfy `v2(x)=v2(i+1)=D` and `delta=d_i+D`. The `delta=0` boundary is simple. These are necessary conditions, not existence claims for the surviving strata.

The numerical-family claim concerns precisely

```
B=17659+2^18 T,   r=B*2^640-161,
0 <= T < tau_917,
```

where `tau_917` is the canonical residue in `recenter_1096.json`. For every such ordinary integer `T` and every `x in Z_2`, `G_r(x)` and `G_r'(x)` do not vanish simultaneously. In particular it covers `0 <= T < 2^914`. It is not a bound on all depths below a corresponding height.

SHA256 fingerprints of the reviewed input revisions:

| File | SHA256 |
|---|---|
| `transversality/address_one_theorem.md` | `67a7736c71c91f81a2c52076f06779b5d83fd59ddc5b57d9142311a78511c4ab` |
| `local_parameter/RECENTER_PROOF.md` | `37bf4469d01b5cf877ca59e729bd9591396783f104ae8c98edac71ca5803fdad` |
| `local_parameter/recenter_1096.json` | `aa12bbb7247da8967cc459964b9273748fd624825fb456a2b7b9b8401acbd2cd` |
| `local_parameter/recenter_certificate.py` | `0fbbc41817a9417cf0dde8d73a8101f6c000a8af81b0d972b38b824ac03814fc` |
| `local_parameter/verify_recenter.py` | `c5f77186d0d4daef4160cd40caa149d170305577590cad38776892360f3d3713` |
| `local_parameter/RECENTER_VERIFICATION.json` | `802e63a04788cb7dd35ef346a1527a8b0e93184482ac3fca64bfeee1614bc517` |
| `sources/euler_v4.md` | `e3df890f066359ee9b0398b3547f0637a11bc6440d91f44e9a6547319e853c49` |
| `sources/finite_parameter.md` | `7905bcb5bf0e2056cdba4336496b2b5790b2545d0fa31a1f86cd762995f501c2` |
| `sources/completion_boundary.md` | `bc144f8123128daed1275dda91afdb801df3b38f8ad8e505327d8a66dafeec72` |
| inherited `fast_certificate_629.json` | `925bee779dc609ca69a089904c5dacd11833defe2341546f64bb3086d28234e1` |

The inherited certificate is in `recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate/`.

## Dependency graph

| Conclusion | Required arrows and leaves |
|---|---|
| Restricted integral residual and actual normalization | Exact signed-Euler generating identity; beta/Bernoulli formula; denominator valuation; finite carry minimum. Internal derivations in `euler_v4.md`, with classical Bernoulli input. |
| Regular complement atlas | Genuine terminal shift and lower-minimum hypothesis; factorization into skeleton and restricted units; separating-ball partition; coefficientwise affine Hensel argument. |
| Address-one derivative exclusion | The atlas + source quotient `Q=P_1/A` + simultaneous value/derivative valuation equations + a dyadic parity contradiction. All critical arrows independently reconstructed. |
| Recentered finite model | Actual center packets + finite Bernoulli stability + factorial-unit stability + integral parity-ball tail. |
| One retained congruence | Complete normalized coefficient arrays + integral half derivative + nonsingular two-variable reduction + exhaustive lift or parameter elimination. Exact computation leaf, freshly replayed. |
| All arguments `x in Z_2` | Old lower-root and skeleton reduction, old cubic derivative-address reduction, and rejection of the other address. Raw proof reviewed; the finite reductions were independently checked from the old complete records. |
| Every integer in the asserted interval | A uniform carry-minimizer cutoff on that interval + exact carry formulas + old exclusion outside the retained cylinder + new exclusion inside it. This arrow is a proof, not sampling. |
| Universal simplicity | Requires noncancellation for actual Euler units on every surviving critical stratum, including the retained unbounded parameter class. **Not addressed by these certificates.** |

No circular dependency was found in the two narrower arguments. An arbitrary representation `r=B2^L-j` cannot substitute for the true-terminal premise.

## Obligation matrix

| Obligation | Status | Finding |
|---|---|---|
| Exact object and coefficient domain | Passed | Uses actual integer-index Euler packets in `Z_2<X>`; no all-precision interpolation substituted. |
| Address-one true-terminal hypothesis | Passed | Present explicitly in final setup; indispensable. |
| Source quotient and derivative units | Passed | `C=1 mod4`, `Q=-x mod4`, hence `Q'` is a unit and `v2(Q(x))=v2(x)`. |
| Emerged-disc exclusion | Passed | Equality of two valuations forces a parity contradiction in the unique translated disc containing zero. |
| Root-free derivative comparison | Passed | Both relative valuation cases are covered, with no ignored cancellation case. |
| Exceptional `delta` and `L` formulas | Passed | Recomputed by binary complementation and factorial digit sums. |
| `delta=0` boundary | Passed | Complement is a unit and has even derivative, so the total derivative is a unit. |
| Artificial unit counterexample | Passed | Exact double-zero construction is valid and is explicitly not an Euler counterexample. |
| Bernoulli unit continuity at finite precision | Passed | The undepletion condition is explicit and sufficient. |
| Factorial offset and relative precision | Passed | One zero offset supplies `Bc/B`; all other odd units are stable at the stated budget. |
| Infinite packet tail | Passed | Parity content gives uniform cutoff `q>=2P`, using true normalization. |
| Content and derivative precision loss | Passed | `1096 -> 918 -> 917`; chain-rule scaling does not cost additional bits for a necessary exact-zero condition. |
| Complete coefficient degree cutoff | Passed | Local degree at least 74 vanishes at global precision 1096. |
| Exact arithmetic replay | Passed | Fresh constructor matches retained data; independent Newton lift and all trace prefixes agree. |
| Old global coverage | Conditional inheritance, checked interface | Symbolic coverage proof and stored reductions checked; no fresh independent implementation of every inherited Euler coefficient routine. |
| Whole ordinary integer interval | Passed | Uniform terminal proof supplied; checking only the center would not suffice, and is not what the proof does. |
| Universal target / all-precision extension | Not addressed | No arithmetic nonintersection for the unbounded retained class; the stated finite Bernoulli boundary prevents the proposed automatic closure. |
| Lean/kernel verification | Out of scope | None run or inferred. |

## Decisive independent derivations

### Address-one emerged discs

At a multiple root, with `s=v2(x)`, the source-normalized recurrence gives

```
v2(F(x-1))=delta+D-s=s+v2(F'(x-1)).
```

On an emerged complement disc, set `beta=alpha_i+1` and `z=v2(x-beta)`. The exact atlas gives `v2(F)=d_i+z` and `v2(F')=d_i`, hence `z=s` and `delta-d_i=2s-D`. Since `z>=h_i>D`, one gets `s>=h_i` and `delta-d_i>h_i`.

There is exactly one translated skeleton disc containing zero. If `m=floor(log2 k)`, its center is `i+1=2^m` and its exponent is `h_i=m`. This includes the endpoint case when `k` is a power of two. The displacement bound therefore gives `v2(beta)=h_i`. If `s>h_i`, then `z=h_i<s`. If `s=h_i`, the two normalized units have even difference, so `z>h_i=s`. Both contradict `z=s`. This independently confirms the step where a purely ultrametric argument without the final parity distinction would have been insufficient.

On a root-free disc, `v2(F)=delta` forces `s=D`. Since `D<h_i`, also `v2(i+1)=D`. The skeleton derivative has valuation exactly `d_i`; the derivative of the perturbation has valuation at least `delta+1`, because `V=1 mod2` coefficientwise. If `d_i>delta`, both derivative terms are too divisible to satisfy the multiple-root equation. If `d_i<=delta`, the skeleton derivative dominates and `delta=d_i+D` follows.

Writing `i=2^t b+a` gives

```
d_i=k-1-t-s2(b)-s2(c-1-b),
delta=k-5-s2(b)-s2(c-1-b),
v2(a+1)=t-4.
```

Exactly eight lower-bit residues satisfy the last condition for each `b`. Furthermore

```
delta=k-5-s2(c-1)-v2(binomial(c-1,b)),
L=4k+t-4-v2(binomial(c-1,b)).
```

Thus `k=128` has only `delta=123`, `L=515`; `k=160` has only `delta=152,153,154`, `L=639,640,641`. At `delta=153` the eight translated centers are `66,70,74,78,82,86,90,94 mod128`, as stated.

At the boundary, `X` falling to length `k` reduces to `X^(k/2)(X-1)^(k/2)` and its derivative vanishes since `k/2` is even. This proves the derivative assertion for all dyadic points, not just the two residue values.

For the displayed artificial counterexample, `Q(1)=3/5`, `v2(P_16'(0))=11`, and `Q'(1)` is a unit. Consequently both constants are odd, while the defining equations give exactly `Q(1)F(0)+2^11=0` and `Q'(1)F(0)+Q(1)F'(0)=0`. It validly disproves any inference that the regular atlas and unspecified unit decorations alone ensure transversality.

### Finite recentering precision

For the cylinder `B=Bc+2^s S`, the even Bernoulli indices differ by a multiple of `2^(641+s)`. The binomial difference bound, multiplied by `2^k B_k` of valuation `k-1`, preserves at least that many bits because `k-1>=floor(log2 k)`. The midpoint factor may be removed only at `P<=2r_c-1`; the manuscript retains this hypothesis. Since `S>=0`, the center is also the smallest ordinary index on this cylinder, so that bound suffices for every member.

In the factorial quotient the offsets are `d=-321,...,2(q-161)`. For `d!=0`, stripping `2^v2(d)` leaves a unit whose variation has valuation at least `641+s-v2(d)`. The stated ceiling is conservative and sufficient. The one zero offset for upper packets leaves the odd unit `B`; hence the upper packets acquire the factor `Bc/B`, while lower packets remain fixed. True normalization ensures that multiplying relative unit errors by packet weights never loses precision.

For omitted packets, on either parity ball at least `floor(q/2)` skeleton factors are coefficientwise even. Therefore all `q>=2P` vanish modulo `2^P`, irrespective of later carry events, provided the actual normalization is integral. This controls the unbounded multiplier family to this finite precision without claiming its terminal hypothesis automatically.

At the retained center, `s=468` and `P=1096` satisfy the exact budget `641+468-13=1096`. After content division, all coefficients are known modulo `2^918`. Differentiation preserves coefficient precision; dividing the even derivative by two leaves `2^917`. An exact critical zero in the original argument necessarily gives a zero in the local argument because its chain-rule multiplier is nonzero; the implication used does not require dividing a modular derivative by `2^15`.

The mod-two equations are `1+Z^2+T=0` and `Z=0`. With variable order `(T,Z)`, their Jacobian is the identity. Therefore every solution has exactly one successor at each bit, covering all residue pairs. The retained `tau` has bitlength 915, so `2^914<=tau<2^915`, and reduces to the old 450-bit residue.

### The whole integer interval

For every positive odd `B`, binary subtraction gives `s2(B2^640-161)=s2(B)+637`. For `T<2^917`, one has `B<2^935`, hence `s2(r)<=1572`. The exact minimizer cutoff is at most 523; using 524 in the manuscript is harmless conservative enlargement. Every such `q` is far below the next `2^640` carry.

For all relevant `q`, independently of the high bits of `B`,

```
lambda_r(q)=3q+2-s2(160-q)                    (q<161),
lambda_r(q)=-154+3(q-161)+s2(q-161)           (161<=q<=524).
```

The first expression has minimum `-1` only at `q=1`; the second has minimum `-154` only at `q=161`. Thus every parameter in the proposed interval truly has terminal 161 and normalization `-154`.

The old certificate excludes critical zeros outside `T=tau_450 mod2^450`. Inside that class every nonnegative integer has the form `tau_450+2^450 S` with `S>=0`, exactly the cylinder required by recentering. A critical zero would then force `T=tau_917 mod2^917`. Since `0<=T<tau_917<2^917`, that is impossible. This establishes the actual ordinary-integer quantifier without enumerating the interval.

## Computation and external-source checks

The fresh arithmetic replay used

```
python local_parameter/recenter_certificate.py --precision 1096 --out independent_review/replay_recenter_1096.json
python independent_review/check_stored_arithmetic.py
```

The constructor completed in about 31 seconds and reproduced every retained certificate field except elapsed time. The second script imports no author modules: a full-Jacobian Newton doubling computation through precisions `2,4,...,512,917` reproduced the final pair and checked all 917 stored trace prefixes. All 74 normalized coefficients agree with the old coefficient records modulo `2^451`; the `Q_i` records equal the exact half derivatives modulo `2^917`.

The center has popcount 869. Its computed packet maximum 603 is safe, since the scalar lower bound at 604 is 1098 and thereafter increases. Local degree 74 has valuation at least `15*74=1110>=1096`; its omitted coefficients remain invisible after normalization and half differentiation. Supplementary exact checks independently confirmed the old lower root `90 mod128`, both old cubic derivative addresses, rejection of the `221` branch, and the complete 256-residue skeleton partition. Outputs are `check_stored_arithmetic.json`, `supplementary_checks.json`, and the replay JSON. The original `RECENTER_VERIFICATION.json` was inspected but its overwrite-producing script was not rerun by this reviewer.

Classical source questions were checked against the official NIST DLMF, version 1.2.8, release 2026-09-15, accessed 2026-10-05. Formula [24.10.1](https://dlmf.nist.gov/24.10.E1) supplies the Bernoulli denominator valuation `v2(B_(2m))=-1` for positive `m`; formulas [24.4.12](https://dlmf.nist.gov/24.4.E12) and [24.4.21](https://dlmf.nist.gov/24.4.E21) supply finite expansion and duplication. Their specialization yields the midpoint identity used in the manuscript. These are classical input checks, not a novelty search. The source's restriction to finite precision follows by discarding terms with `k>=P+1`, each having valuation at least `P`.

No Lean compiler, kernel artifact validation, or comprehensive independent replacement of inherited Bernoulli/source code was performed. The replay proves reproducibility and the modular lift; the separate mathematical arguments above are what justify the uniform model and its quantifiers.

## Exact remaining gap and strongest safe statement

The missing implication is **actual Euler unit noncancellation on the retained critical strata**. In the terminal-161 cylinder the new certificate leaves one congruence class modulo `2^917`; it neither constructs an exact singular Euler parameter nor proves that no ordinary integer survives every valid later test. For all address-one walls, the derivative theorem leaves the explicitly listed `delta=d_i+D` strata. The artificial unit counterexample shows that these cannot be discarded merely by citing a regular complement atlas.

The strongest safe combined statement is the finite all-`x` integer-family exclusion above, together with the universal necessary critical-stratum condition for genuine address-one walls. The least expensive relevant next step toward the universal target is to isolate the actual Euler-unit equation on those strata, with its undepletion factor retained, and prove noncancellation there. Merely increasing finite precision is further evidence for finite subfamilies, not the missing universal implication.
