# Research-connection audit

Scope: the complete sequence catalogue's stored values and index conventions;
the generalized k-step formulas; typed structural links; and ordinary formal
transfers with their shifts and coefficient domains. This is a mathematical
self-review with exact computation checks, not independent peer review of every
manuscript in the research collection.

## Claims and proof obligations

| Claim | Hypotheses and conclusion | Verdict | Decisive obligations |
| --- | --- | --- | --- |
| Weighted k-step formulas | k>=2, integer r,c>=1, n>=0; the recurrence, finite binomial and finite hypergeometric expressions give [z^n](1-c(z+...+z^k))^(-r) | Proved as written in IDENTITIES.md | Ordinary normalization, n=0, finite expansion, integer coefficients |
| Hypergeometric endpoint | The displayed sum ends at floor(m/(k+1)); lower Pochhammer factors never vanish within it | Proved as written under the stated finite convention | Earliest lower zero is after the cutoff; no automatic cancellation |
| Generic reversible transfer | Nonzero anchors over Q; leading-zero classes and shifts retained; H=B/A and K=A/B | Correct only with these stated domain conditions | Zero streams, valuation mismatch, nonunit integer anchors, exact inverse |
| Euler/Fibonacci identity | Signed even Euler values as ordinary coefficients; target F(n+1), H=1/((1-z-z^2)A) | Proved as written in the maintained source | Fibonacci shift, ordinary versus exponential coefficients, unit constant |
| Transported shift | The cited infinite normalized Euler/Fibonacci construction includes its rank-one boundary correction | Proved as written in the maintained source | Forward shift order, first coefficient, finite far-edge exclusion |
| Stored-prefix certificates | Exact forward, inverse and kernel product through the available L positions | Finite implementation evidence | No extrapolation; original indices and zero prefixes exported |

The proof dependencies are definitions and finite coefficient algebra in
Q[[z]], the negative-binomial expansion obtained from products of geometric
series, and the maintained Euler derivation. Finite tests supplement these
written arguments; they do not supply a universal proof or historical priority.

## Boundary controls

- An unshifted Fibonacci constant F(0)=0 cannot be the image of Euler a(0)=1
  under a unit lower-triangular convolution with diagonal one. The displayed
  one-step shift is required.
- A window with no stored nonzero coefficient supplies no unit anchor. A zero
  prefix is not evidence that an infinite sequence is identically zero.
- Nonzero integer anchors are units over Q but need not be units over Z. Both
  kernel integrality flags refer to the computed finite coefficients.
- Cancelling the zero upper/lower parameter at m=0 would leave an infinite
  hypergeometric series with linear coefficient 4/9 in the k=2,r=c=1 case;
  the defined finite sum is the constant one. This cancellation is rejected.
- A finite forward-shift matrix has a far-edge boundary. It is not used to
  verify the infinite transported-shift identity.

## Reproduction

From the repository root, use Python 3.12+ and Node.js:

```text
python tools/audit_sequence_library.py --oeis --output RESULT_JSON
python tools/audit_sequence_connections.py --node NODE_EXECUTABLE --output RESULT_JSON
node --test tools/test_sequence_transfer.mjs
```

The connection checker compares the JavaScript kernels against a Python
Fraction oracle built by a finite geometric-series reciprocal expansion, and
reproduces the preserved archive with its own documented controls. Its manifest
records the actual population, exclusions, tested ranges and source hashes.
Current completed evidence and observed counts are identified in
verification/sequence-library/README.md after the bounded runs finish.
