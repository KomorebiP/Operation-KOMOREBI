# AVOC v0.30.0 — reusable affine certificates and preflight opportunity bounds

This is the cumulative semantic-feedback branch through v0.29. Its inherited mathematical sources are unchanged. The new executable is a checked GF(5) cache and selective analyzer, not a new autonomous research agent.

## 1. Reuse the linear factorization, adjust the affine offset

A stored certificate for f(x)=A x+b has factors C,D, first offset a, second offset d and rank witnesses U,V:

    C D = A,   C a+d = b,   U A V = I_r.

For any new map g(x)=A x+b', retain C,D,a,U,V and replace the second offset by

    d' = b' - C a.

The new proof establishes exact affine equivalence and the same certified minimum intermediate width. It does not assume that a=0. Retargeting twice equals retargeting once to the last target. The two-dense-stage execution tariff is unchanged.

The importer first rechecks the stored FULL certificate against its saved signature and then checks exact equality of the current linear matrix. It constructs a proof-carrying retargeted certificate only after both succeed. Cached success flags are not inputs. Corruption of the saved bias is rejected even though the later retargeting could otherwise conceal it.

A field, dimensions and coordinate order remain part of the typed/serialized contract. Changing offsets is intentionally supported, not a semantic mismatch. Cache indexing omits the bias, but the resulting candidate's new bias is computed explicitly and proved correct.

## 2. Reselect against the current source

The current source program is retained as an option. Let

    D(n,m)=m(2n+1),
    F(n,m,r)=D(n,r)+D(r,m).

For a checked candidate of width r the selected cost is exactly

    min(originalCost, D(n,m), F(n,m,r)).

The selected program agrees with the current source on EVERY input. A syntactically different source with the same coefficients is supported. A primitive identity remains free under the existing model and is not replaced by a dense or factored implementation merely because a matching certificate exists.

Two valid certificates for the same linear map have the same minimum width. A new search cannot improve the factor tariff within this two-dense-stage class after one such certificate is available. This does not rule out sparse, shared, special-primitive or multi-stage improvements.

## 3. A cheap width floor and preflight bound

Before factor generation, classify the normalized linear matrix as zero or nonzero:

    lo=0 if A=0; otherwise lo=1.

Every exact two-stage factorization has width at least lo. No matrix-rank algorithm or factor certificate is needed for this bound.

Preflight first makes the better of the original program and its dense normal form available. Let its cost be C0. A lower bound on the eventual three-option menu is

    L=min(C0,D(n,m),F(n,m,lo)).

For N declared executions, no candidate in this menu can save more than

    N(C0-L).

If the remaining setup cost has a justified lower bound S_min and

    N(C0-L) <= S_min,

then further factor exploration cannot produce a strictly positive REMAINING net gain for this task/objective. The executed Boolean threshold is connected to this theorem for both cold generation and warm revalidation.

Passing the test is NOT a profitability guarantee. It only means the optimistic bound has not excluded positive gain. The actual width and setup may make the campaign lose money.

Preflight has already consumed work. Its charge is not refunded when it stops. It can also make cheap dense fusion available even when factor generation is skipped.

## 4. Explicit tariffs and scopes

The initial preflight charge is normalizationCost(source)+n*m. Zero declared calls or a zero-tariff incumbent skip this arithmetic preflight; parsing and validation still have physical cost outside the tariff.

Per query, a saved certificate is rechecked, its matrix compared with the current linear key, and its affine bias retargeted:

    reuseCharge = checkingCharge(n,m,r) + m*n + D(r,m).

The second Lean invocation normalizes the source again. That repeated normalization is explicitly charged; it is not silently counted only once.

Cold generation additionally pays the inherited tracked-RREF meter. Its emitted-certificate-entry tariff is

    emit(n,m,r)=r*n+r+m*r+m+r*m+n*r.

Both validation and emission tariffs are monotone in r. Thus the preflight lower costs are:

    cold_min = secondNormalization + reuseCharge(n,m,lo) + emit(n,m,lo),
    warm_min = secondNormalization + reuseCharge(n,m,lo).

The cold guarantee assumes the proposer pays at least its emitted-entry tariff. The actual Python proposer does so; universal algorithmic complexity or metering correctness of all possible proposers is not assumed proved.

Funded invalid certificates remain charged in the typed checker response. Unfunded certificate validation does not execute it. Returned per-invocation totals obey spent+remaining=credit. These are not a durable payment ledger or calibrated physical costs.

## 5. Lifecycle reuse accounting

For a simplified sequence of s sessions with common validation V, adaptation A, generation G and per-session deployment D:

    cold = s*(G+V+D),
    warm = G+s*(V+A+D).

The exact break-even condition is

    G+s*A <= s*G.

Validation is paid in every session; initial generation is not forgotten. IO, maintenance and future workload uncertainty must be added when using a richer economic model.

## 6. Checked and executed examples

The four-by-four all-ones linear map with offset (1,2,3,4) has original cost 36 and certified width-one cost 21.

New cold setup: 16 preflight + 91 generation + 133 revalidation/retarget = 240.
Warm setup: 16 preflight + 133 revalidation/retarget = 149.

Consequently:

    cold break-even: N>=16,
    warm break-even: N>=10.

At N=10 cold preflight rejects further search because its remaining lower charge 154 exceeds the maximum possible saving 150. Warm revalidation has a remaining lower charge 133, and actual total setup 149 yields net gain 1.

At N=11 cold preflight allows exploration (165>154), but the actual cold cost is 240, producing net -75. This counterexample is proved and executed.

A new offset (4,3,2,1) uses the unchanged saved certificate file and returns exactly that new offset at zero. A separate checked example uses nonzero first-stage offset 2; the correctly retargeted second offset is (2,1,0,4). Naively reusing the old factors or replacing the second bias without adjustment is invalid.

## 7. Persistent boundary

The new single-writer store contains an immutable format descriptor and checked certificate snapshots. A filename fingerprint indexes the exact field/dimension/linear key; actual matrix equality is still checked by Lean. No hash injectivity theorem is used for mathematical correctness.

Each warm query revalidates the certificate with the executed Lean checker. No factor generation occurs. The saved record is not changed to the newest query's bias. Source fingerprints reject accidental backend drift but are not signatures or remote attestation.

The Python reader, metering and filesystem adapter are independently tested, not formally refined. This is not a port of AVOC's entire crash/retry/upgrade protocol.
