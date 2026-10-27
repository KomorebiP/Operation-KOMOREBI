# Catalan packet computation audit

Series 08, 9 October 2026. These computations are finite evidence. They do not prove that Catalan's constant is irrational, a uniform valuation estimate, or a uniform gcd growth estimate. External recurrence attribution is a separate literature question.

## Decision and arithmetic contract

The historical program was copied byte for byte to `computations/catalan_packet_audit.py`. Its SHA-256 is `4a59096f9c3a0222e6523e5183292678c36b68089bd0bf3103fc3da090db1a7c`. The input copy remained unchanged during all recorded runs.

The recurrence has initial values

\[
u_0=1,\quad u_1=7/4,\quad v_0=0,\quad v_1=13/8.
\]

For \(n\geq1\), put

\[
\begin{aligned}
p(n)&=20n^2-8n+1,\\
q(n)&=3520n^6+5632n^5+2064n^4-384n^3-156n^2+16n+7,\\
A_n&=(2n+1)^2(2n+2)^2p(n),\\
C_n&=(2n-1)^2(2n)^2p(n+1).
\end{aligned}
\]

Both sequences obey \(A_ny_{n+1}=q(n)y_n+C_ny_{n-1}\). Let \(T_n=16^nu_n\), and let

\[
S_{n,m}=\sum_{i=0}^m\binom miT_{n+i}.
\]

All decisions use arbitrary precision integers or exact `fractions.Fraction` rationals. The large Pascal scan operates in \(\mathbb Z/(2^{128})\). Decimal strings and logarithms are rounded display values only. No random sampling or seed is used.

## Verified finite results

| Check | Actual tested family | Result |
|---|---|---|
| Historical default reproduction | Original defaults, without source edits | Output JSON reproduced byte for byte |
| Wronskian | \(0\leq n\leq200\) | All exact equalities pass |
| Integer \(T\) recurrence | \(0\leq n\leq10000\) in the default scan | Every exact division has zero remainder |
| Large valuation scan | \(1\leq n\leq2000\), \(0\leq m\leq4n\) | 8,006,000 pairs, maximum valuation 31, a witness at \((1466,2113)\) |
| Residue precision | Same 8,006,000 pairs modulo \(2^{128}\) | No zero residues, so all scanned valuations are exact |
| Independent rational recurrence | \(0\leq n\leq500\) | All \(u,v\) match, \(T_n\) integral and positive, \(8L_{2n}^2 16^n v_n\) integral |
| Direct sum versus Pascal | \(1\leq n\leq100\), \(0\leq m\leq4n\) | Every residue and valuation agrees at all 20,300 pairs |
| Direct large witness | Five pairs around \((1466,2113)\) | Exact integer sum at the stated witness has valuation 31 |
| Half-binomial normalization | \(0\leq n\leq50\), all \(0\leq j\leq n\) | All 1,326 direct product summands and the resulting \(u_n\) agree with the recurrence |
| Continuant normalization | \(2\leq n\leq13\), five rational initial families | All 60 exact continuant expressions agree with forward recurrence |
| Precision ceiling branch | \(1\leq n\leq3\), \(0\leq m\leq4n\), modulus \(2^4\) | Eight zero residues correctly flagged unresolved. True direct maximum is 6, rather than the clipped reported value 4 |
| Cleared gcds | Five historical pairs | Exact gcds and factorizations reproduced |
| Raw filter intervals | \(1\leq n\leq20\), \(0\leq m\leq4n\) | All 860 forms certified nonzero. A proposed sign pattern fails at 138 pairs |

The first-occurrence argmax in the historical large scan is defined by its loop order, increasing \(m\), then increasing \(n\). No uniqueness claim is made about the maximum. The independent direct grid uses increasing \(n\), then increasing \(m\). Its maximum is 20 at \((52,6)\).

The historical and fresh default result files both have SHA-256 `cff3c696e26525197c3e043e8bd9f102e73490dc1606a052e061d92ae4ca88c3`. The fresh default run took about 9.85 seconds on the recorded environment. Runtime is descriptive and not a performance guarantee.

## Why the modular valuations are exact

If a nonzero integer \(x\) has a nonzero residue \(r\pmod {2^B}\), then \(v_2(r)<B\) and \(v_2(x)=v_2(r)\). A zero residue only gives \(v_2(x)\geq B\). The historical program tracks zero residues and withholds its `exact_below_precision` flag whenever any occur.

Pascal evolution is valid because

\[
S_{n,m+1}=S_{n,m}+S_{n+1,m}.
\]

The in-place update proceeds from low to high \(n\), so each right neighbor is still the previous-row value. The initial row contains \(T_0,\ldots,T_{5N}\), sufficient for all \(n\leq N,m\leq4n\). The exact number of checked pairs is \(\sum_{n=1}^N(4n+1)=2N^2+3N\). These statements explain the implemented finite assertion. They do not turn it into an all-index theorem.

## Certified value intervals

The independent code constructs a rational interval for \(G\) from an Euler transform. For \(a_k=(2k+1)^{-2}\), use the positive difference convention \(\Delta a_k=a_k-a_{k+1}\). The elementary integral identity

\[
\Delta^j a_0=\int_0^1(1-x^2)^j(-\log x)\,dx
\]

implies \(0\leq\Delta^j a_0\leq1\). Integrating the geometric sum gives

\[
G=\sum_{j=0}^{\infty}\frac{\Delta^j a_0}{2^{j+1}}.
\]

The integral form of \(G\) follows by integrating its absolutely summable odd-square reciprocal series. The positive Euler series permits monotone interchange with the integral. Keeping \(j=0,\ldots,1000\) therefore leaves a certified tail in \([0,2^{-1001}]\). All retained differences are computed as exact rationals, and their bounds are checked.

The exact interval endpoints are in `independent_final/results.json`. Error signs and diagnostic logs use this interval, rather than an unverified floating value of \(G\). The interval proof is the elementary analytic reduction above. The code only checks its finite rational portion. This separation matters.

## The failed sign guess

We tested the exploratory guess

\[
\operatorname{sign}F_{n,m}=(-1)^m,\qquad
F_{n,m}=8(-1)^n\sum_{i=0}^m\binom mi16^{n+i}(u_{n+i}G-v_{n+i}).
\]

The guess is false. At \((n,m)=(1,1)\), exact coefficients give

\[
F_{1,1}=\frac{173056}{9}-20992G>0.
\]

Its positivity is certified by the rational interval for \(G\). The guessed sign was negative. There are 138 such mismatches among the 860 tested pairs. All 860 forms are nevertheless certified nonzero. Full mismatch indices and exact interval bounds for the smallest counterexample are retained in `sign_hypothesis_failure.json`.

This was a diagnostic guess introduced in this audit. It was not an authenticated theorem from Eskandari or Zudilin. Its failure does not refute either source. Any universal sign or nonvanishing statement used in the monograph needs its own written argument with its actual hypotheses.

The initial independent run included an overly broad interpretation label, “finite verified pattern only.” Its raw result already listed every mismatch. The final source and final rerun replace that interpretation with explicit falsification. Both initial and corrected runs remain immutable. Use `independent_final/` as the publication evidence.

## Cleared denominator decomposition

Let

\[
U=\sum_i\binom miT_{n+i},\quad
V=\sum_i\binom mi16^{n+i}v_{n+i},\quad
Q=8L_{2(n+m)}^2,\quad D=\operatorname{den}(V).
\]

For the tested pairs, \(D\mid Q\). Since \(U\) is integral and \(V\) is reduced,

\[
\gcd(QU,QV)=\frac QD\gcd(U,\operatorname{num}V).
\]

The common sign \((-1)^n\) has no effect on the gcd. This exact identity separates redundant clearance from common content in the minimally cleared pair.

| \((n,m)\) | Redundant scale \(Q/D\) | Minimal pair gcd | Cleared gcd |
|---|---:|---:|---:|
| \((20,66)\) | 1,703,936 | 8 | 13,631,488 |
| \((30,100)\) | 129,499,136 | 4 | 517,996,544 |
| \((50,166)\) | 2,779,250,688 | 8 | 22,234,005,504 |
| \((70,232)\) | 5,257,560,064 | 64 | 336,483,844,096 |
| \((100,332)\) | 1,084,227,584 | 8 | 8,673,820,672 |

These five rows cannot establish asymptotic growth or a uniform upper or lower bound. In particular, decreasing sampled logarithmic ratios are observations, not proofs of subexponential content growth.

## Public reproduction commands

From the unpacked source bundle root, with Python 3.12 or a compatible Python providing the standard-library features used:

```sh
python3 computations/catalan_packet_audit.py --scan-n 2000 --precision-bits 128 --output fresh_default_results.json
python3 computations/independent_audit_final.py --output-dir fresh_independent
python3 computations/witness_and_precision_audit.py --output-dir fresh_witness
python3 computations/half_binomial_audit.py --output fresh_half_binomial_results.json
python3 computations/continuant_audit.py --output fresh_continuant_results.json
```

Use new output paths. The first command should reproduce the historical output exactly. The independent script imports `computations/catalan_packet_audit.py` only for cross-comparison. Its separately indexed rational recurrence, multiplicative binomial witness sums, and exact Catalan interval provide additional checks. They do not eliminate all shared-formula risk.

The continuant command checks the Chapter 3 normalization for \(n=2,\ldots,13\) on the two historical sequences and initial pairs \((0,1)\), \((1,0)\), and \((-3/7,5/11)\). It uses exact `Fraction` rationals. Its 60 successful instances corroborate the implementation of the continuant expression. The universal statement has a separate written induction and does not follow from the finite run. The recurrence coefficients remain a shared source input. The authoritative release run is `continuant_final/`. The earlier successful run in `continuant/` is retained. A later caption added an explicit diagram notation bridge, changing the contextual manuscript bytes declared by that first run. The mathematical formula and executable inputs did not change. The final small run passed against the current contextual source and its manifest validated with `--root`.

No third-party mathematics library is required. Python 3.12.14 was used in the recorded runs. Floating logarithms can vary in their last displayed digit on another platform. Exact integers, rational strings, signs and valuations are the load-bearing results.

## Executed commands and provenance

The complete actual child argument arrays, UTC timestamps, hardware, input hashes before and after, output hashes, elapsed times, resource caps and exit statuses are in each `manifest.json`. The recording commands used this absolute runner:

```text
/root/.codex/plugins/cache/openai-curated-remote/mathbox/3.2.0/skills/computation-audit/scripts/run_experiment.py
```

with project root:

```text
/workspace/scratch/fd5253a691e7/catalan_set
```

The runner is a provenance helper, not required by the public commands. It records no scientific conclusion from an exit status. It enforced wall-clock, log-byte, address-space, CPU-time and CPU-affinity caps. The cooperative numerical thread cap is recorded separately. There is no Git repository revision for this assembled research bundle, and the manifests explicitly record that limitation.

Seven completed manifests are retained, including the superseded first continuant run. Each validated when recorded. The six current run records consist of the first five runs and `continuant_final/`, whose declared inputs match the release sources. The prior `continuant/` context hash no longer matches the revised caption and is explicitly historical, rather than fresh evidence for the final manuscript bytes. The output hashes and pinned inputs were checked. The initial independent manifest is retained for history. The final independent manifest is the current interpretive record. Complete absolute recording-command argument arrays and validator commands for the first five runs are additionally collected in `provenance_recording_commands.json`. Both continuant runs record their actual child commands, input hashes, output hashes and resource limits in their own manifests, with their respective mathematical contracts in `continuant_contract.json` and `continuant_final_contract.json`.

The half-binomial check uses

\[
u_n=\sum_{j=0}^n\binom nj\binom{n-\tfrac12}{j}\binom{n+j-\tfrac12}{j}.
\]

The separate literature audit identifies this normalization with Krattenthaler and Rivoal, arXiv:0810.1927, Lemma 3, equation (3.1). The computation constructs each generalized binomial coefficient by exact products, rather than assuming the identity. It checks that \(4^j\) times each half-binomial coefficient is integral, that \(16^n\) times each summand is integral, and that the sum equals the independently constructed recurrence value for every \(n=0,\ldots,50\). A universal denominator lemma and source identity remain separate written evidence.

## Residual risks and status

Status: implementation and finite assertions verified in the stated ranges. The proposed odd-filter sign pattern is falsified. Default historical output is reproduced exactly.

The recurrence formulas shared across constructions require the separate source contract. Positivity and integrality at tested indices cannot replace their universal proofs. The bounded valuation grid cannot settle \(v_2(S_{n,m})=o(n+m)\), nor any stronger uniform estimate. The five gcd samples cannot justify a universal asymptotic content law. A valid irrationality argument still needs integer linear forms, nonvanishing, and a strict globally justified decay margin after all required denominator clearing and content cancellation.
