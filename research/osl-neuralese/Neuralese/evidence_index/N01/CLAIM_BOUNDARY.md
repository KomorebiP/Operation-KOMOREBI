# Claim boundary for v0.3.0

## Supported

The sealed Stage A primary supports one narrow engineering conclusion:

> In the supplied-table, explicit 8x8 operator architecture, sign-canonical QR
> makes each realized recurrent operator approximately orthogonal and prevents
> latent-norm explosion or collapse through 2,048 tested steps. This hard
> stability guarantee did not jointly yield seed-reliable learned execution,
> latent closure, or cross-context causal state semantics.

All 12 `hard_correct` seeds produced finite depth-2,048 trajectories. The mean
median endpoint/start norm ratio was 1.0000098, mean P95 transient gain was
1.0000930, mean minimum singular value was 0.9999996, and mean P95
orthogonality defect was `3.11e-7`. These confirm an architectural property;
they do not show that stability was learned.

Correct anonymous composition targets had a descriptive average association
with hard-arm depth-64 behavior: 0.4840 for `hard_correct` versus 0.1955 for
`hard_shuffled`, a paired mean difference of 0.2886. The frozen gate failed
because only 7/12 seed pairs cleared its per-seed margin. The post-hoc
100,000-resample paired-bootstrap 95% interval, [0.1143, 0.4744], is
exploratory and does not revise that decision.

The primary completed 48 cells and six transport pairs, consumed 49,152,000
directly conditioned examples, recorded zero split violations, and passed the
fail-closed exact table oracle. A post-hoc replay of `hard_correct`, seed 300,
reproduced every parameter tensor byte and every metric exactly. This is a
deterministic replay, not an independent scientific replication.

## Failed primary claims

The conjunctive primary failed: **8 of 26 gates passed**.

- H1 stability and execution: 7/16 passed. The QR stability/integrity checks
  passed; every positive learned-execution criterion failed its required seed
  fraction, and hard missed the frozen behavior margin against soft.
- H2 anonymous closure: 0/6 passed.
- H3 cross-context state semantics: 1/4 passed. Only the low wrong-state
  negative control passed.

Thus **all frozen positive learned-semantic gates failed**. At D4 depth 64,
`hard_correct` reached 0.4840 versus 0.9054 for `soft_correct`; the paired
mean difference was -0.4214. Soft's depth-2,048 endpoint/start norm ratio was
approximately `7.06e-19`, so its better finite-horizon execution coexisted
with eventual contraction.

## Split-qualified interpretation

All 40,320 finite permutation maps are partitioned into disjoint
24,192/8,064/8,064 train/dev/test sets. Every sampled training word had every
nonempty contiguous subword action in train. The broad depth assay holds out
the two supplied primitive tables; a separate split-conditioned assay also
requires the word's complete finite action to hash to test.

Neither condition establishes a globally novel abstract group element. D4
actions can be regenerated algebraically from train actions. The model also
receives complete transition tables, and an exact transpose-and-compose
solution exists.

## Transport boundary

Across six hard-arm seed pairs, affine alignment reached 0.8495 D4 state-patch
accuracy, versus 0.1218 for shuffled-pair fitting and 0.1069 for a random map.
Discrete source decoding followed by target re-embedding reached 0.9088. Stage
A does not establish transport richer than the eight-state codebook.

## Stage B boundary

The sparse GF(5)^4 code is an audited scaffold, not a trained result. Monomial
has 0/96 held-out primitive collisions in the bounded same-context length-2--4
training language; shear has 86/96 and is unsafe for that claim. Pooling train
generators gives all 96 held-out primitives in both families witnesses by depth
3, so neither supports unbounded novelty.

## Not established

V0.3 does not establish:

- a learned invariant metric: Stage A hard QR fixes `G = I`
- a clean one-factor or compute-matched hard-versus-soft causal contrast
- formal noninferiority or null-hypothesis significance testing
- exact or seed-reliable learned latent algebra
- cross-context causally executable state semantics
- transport beyond discrete state identity
- spontaneous Neuralese or operator discovery without full tables
- an unconstrained or pretrained language-model mechanism
- unbounded reasoning, autonomous improvement, awareness, or consciousness

The authoritative records are
`results/v0.3.0/stage_a_primary_v3/GATES.json` and
`results/v0.3.0/stage_a_primary_v3/RECEIPT.json`, under protocol SHA-256
`ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf`.

