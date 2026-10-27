# Euler address-one continuation — 5 October 2026

Universal Euler simplicity remains open. This checkpoint proves a structural exclusion theorem for address-one walls, extends one actual terminal-161 family exclusion, and corrects an invalid descent inference in the preceding conversation. No Lean compiler was run.

## Exact target

For every positive ordinary integer r and every x in Z₂, prove G_r(x)=0 implies G_r′(x)≠0, with the signed Euler packet definition retained in `sources/euler_v4.md`. A counterexample must be an actual Euler residual. A freely chosen analytic complement is only a control against a proposed proof mechanism.

## Proved structural advance

Assume the true terminal is j, the last lower minimizing address is one, and the outer wall chart is certified. Write k=j−1=2^t c, with c odd, and δ=L−Θ(k). Every root is simple unless it lies in a root-free regular-complement disc and satisfies

    v₂(x)=t−4,
    δ=k−5−s₂(c−1)−v₂ binom(c−1,b),  0≤b<c.

Equivalently the only potentially singular outer scales are

    L=4k+t−4−v₂ binom(c−1,b).

All charts containing a root of the complement, and the boundary δ=0, are proved simple. For each b at most eight skeleton discs remain. These are necessary conditions, not assertions that a repeated Euler root exists.

| True terminal | Possible critical δ | Possible critical L | Required v₂(x) |
|---|---|---|---|
| 129 | 123 | 515 | 3 |
| 161 | 152, 153, 154 | 639, 640, 641 | 1 |

At terminal 161 and L=640, the structural reduction leaves x≡66,70,74,78,82,86,90,94 modulo 128. The inherited arithmetic of the specific multiplier progression below narrows this further to its existing deep chart.

Read `transversality/address_one_theorem.md` for the source-normalized derivative proof and an exact artificial countermodel showing why the remaining Euler coefficient information is necessary.

## New uniform arithmetic exclusion

For every ordinary integer T with 0≤T<2^914, put

    B=17659+2^18 T,
    r=B 2^640−161.

Then G_r and G_r′ have no common zero anywhere in Z₂. The exact larger interval is 0≤T<τ₉₁₇, whose 915-bit endpoint is stored in `local_parameter/recenter_1096.json`.

The new local template has 1096 global coefficient bits and 917 joint parameter/critical-point bits. It is valid only on the retained 450-bit parameter cylinder. Outside that cylinder, the preceding complete certificate supplies the exclusion. True terminal 161 is established uniformly throughout the displayed interval by the finite carry cutoff, rather than inferred from the form of the index.

This is a computer-assisted theorem using the inherited Euler packet and skeleton identities, the retained old certificate, the newly proved local stability theorem, and complete finite coefficient data. It does not enumerate the interval or infer exact singularity from a modular zero.

Read `local_parameter/RECENTER_PROOF.md` for the argument. The fresh actual-index checks at three cylinder parameters compare all 74 local coefficients modulo 2^918. An independent review reconstructs the critical residue pair using a different Jacobian-Newton lift. The standalone replay reproduces every scientific field of the saved certificate.

## Necessary correction

The record identity e_j(q)=Θ(j)−Θ(j−q) and the regular-complement theorem are correct. The stronger bound 3a+1≤v₂(k) is proved. But rewriting the same r with a smaller wall label does not reduce its true terminal: remote carries remain in the new odd multiplier.

For example, r=2^103−33=(2^98−1)2^5−1 has inner label 1 but true terminal 33. Also the regular smaller address 3 can still give the multiple lower residue X²(X−1). Consequently the earlier assertion that all multiple-lower-root descent was essentially closed is withdrawn. See `carry_audit/CARRY_ADDRESS_AUDIT.md`.

## Reproduce

From this directory, with Python 3.10 or newer and its standard library:

```text
python3 local_parameter/recenter_certificate.py --precision 1096 --out fresh_certificate.json
python3 local_parameter/verify_recenter.py
python3 independent_review/check_stored_arithmetic.py
```

The constructor should be given a fresh output path. The verifier refreshes its verification JSON. Original historical archives were not edited. Relevant inherited sources are included at their executed relative paths.

`evidence/replay_1096/manifest.json` records the bounded standalone replay and pinned inputs. `SHA256_MANIFEST.json` records package integrity. Neither a successful command nor a manifest is a universal proof certificate.

## Exact remaining work

1. Prove noncancellation for the actual Bernoulli/factorial units on the remaining address-one critical strata. The regular atlas and source alone are insufficient, as the exact artificial control demonstrates.
2. Resolve the surviving terminal-161 class T≡τ₉₁₇ modulo 2^917, the other outstanding multiplier phases, and terminal-129 critical families. More recentering is executable under its finite bounds, but more bits alone do not prove universal nonintersection.
3. Construct an analytic multiplicity-descent theorem for higher addresses that retains the full multiplier carry data. A decreasing combinatorial label is not such a theorem.

The finite recentering route remains open. Its next executable step is to use the new residue as the center and recompute the actual Euler units, while checking every precision and cutoff hypothesis. A decisive uniform advance needs an arithmetic noncancellation invariant or a justified model through the nonunit boundary, rather than an assertion of indefinite lifting.
