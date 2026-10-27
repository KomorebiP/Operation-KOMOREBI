# Audit notes for v0.3.0

## Why v0.3 was needed

V0.2 improved finite-horizon execution but its best soft-metric arm contracted
toward zero. V0.3 asked whether exact noncontractive QR operators could repair
that failure without sacrificing learned behavior. The sealed answer is no
under the tested treatment: QR stability held to numerical precision, while
hard-arm learning was seed-bimodal and substantially worse than soft at medium
depth.

The primary passed 8/26 gates. Seven passes were stability/integrity checks; the
eighth was the low wrong-state negative control. Every frozen positive gate for
learned execution, closure, or cross-context state semantics failed.

## Protocol chronology

All calibration used development coordinates only.

1. Superseded pre-version and slow-sampler attempts are retained at
   `results/v0.3.0/stage_a_qualification_superseded_preversion/` and
   `results/v0.3.0/stage_a_qualification_superseded_slow_sampler/`.
2. A partial 4,000-step developmental path did not reliably qualify and is
   retained at `results/v0.3.0/stage_a_qualification_failed_4000/`.
3. `stage_a_calibration_8000/` and `stage_a_calibration_alternatives/`
   selected fixed-identity QR with composition weight 0.3.
4. The retained `stage_a_qualification_v3/` completed 16 cells, consumed
   16,384,000 examples with zero violations, passed the oracle, and passed 8/8
   development gates.
5. The 48-cell test protocol was sealed at `2026-09-02T21:20:29Z`, before the
   primary output existed and before test coordinates were opened.

Qualification is engineering selection, not confirmatory evidence. Its success
versus the weaker 12-seed primary exposes optimization variance and the danger
of a small qualification grid.

## Frozen integrity chain

| Object | Path | SHA-256 |
|---|---|---|
| Scientific source set | 29-file whitelist in seal | `814ea6f2301523965bf8d94dd9da8bbb598451f03e0200cae1cde2ab8de53624` |
| Coordinate partition | run receipts | `3aceaac6852f88360de0851eefc43bf46331d3b4efe3a04d0f2b9dfeff455340` |
| Qualification protocol | `protocols/V0_3_STAGE_A_QUALIFICATION.json` | `0bca42f89400904180f36872aaa4fb8040c2cb848b86e50dc084eb90a47634a0` |
| Qualification receipt | `results/v0.3.0/stage_a_qualification_v3/RECEIPT.json` | `511d706bd82f910d1817e21e99aa58823e86707b5652736fd74281e2d75e7f55` |
| Primary protocol | `protocols/V0_3_STAGE_A_PRIMARY.json` | `ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf` |
| Pre-test seal file | `protocols/V0_3_STAGE_A_PRIMARY_SEAL.json` | `84c15ffcef8553288fe3e3393e7056ca0c1cfcdd8c78639f61d0adfe6d80f5c9` |
| Primary receipt | `results/v0.3.0/stage_a_primary_v3/RECEIPT.json` | `1854d622e6154a44107da80164c77c306ac7a5472583e089e6188738b9e294e7` |
| Post-hoc record | `results/v0.3.0/stage_a_primary_v3/POSTHOC_DESCRIPTIVE.json` | `9c76604b430363c4b38872523d661156769568989313d429b3eccf4d2120669f` |
| Replay record | `results/v0.3.0/stage_a_reproducibility/REPRODUCIBILITY.json` | `455f958d518a2bdf6a8d59dae5a1b40f9ce99d09ee371e6d28be9ee100c83ced` |

These file hashes precede final manifest construction; package-level hashes may
be generated later without changing sealed scientific bytes.

## Recovery orchestration

The execution supervisor interrupted the original runner after 17 completed
cells without a scientific `FAILED` record. A bounded recovery utility first
validated the seal, protocol, code/split digests, cell configuration, and
existing artifacts. It completed only missing cells in bounded chunks, then
generated the six prespecified pairs.
`results/v0.3.0/stage_a_primary_v3/RECOVERY_EVENTS.json` records each event.

The final receipt reports 48/48 cells, six pairs, 49,152,000 accepted examples,
zero fictional direct-sampler rejections, zero split violations, and unchanged
scientific/protocol bytes.

## Split discipline and limits

Every nonempty contiguous subword action in a sampled length-1--4 training word
must hash to train. A cached exhaustive support enables direct uniform sampling
and exact receipts. This closes sampled-path leakage, not algebraic closure.
D4's finite actions remain regenerable from train actions.

The broad D4/C8/random depth assay holds out primitive tables. The separate
split-conditioned assay also makes the full terminal finite action test-ranked.
Neither makes an abstract group element globally novel. Complete transition
tables and an explicit 8x8 operator channel still make a transpose executor
available.

## Hard-versus-soft caveats

- Stage A hard QR fixes `G = I`; it does not learn a metric.
- Hard and soft arms share raw tensors, but QR changes effective initial
  operators. Initial dynamics and forward compute are not matched.
- The comparison is a whole-treatment engineering contrast, not a one-factor
  causal estimate.
- The frozen margin is not formal noninferiority or NHST.
- Exact norm preservation cannot guarantee semantic correctness.

Hard correct averaged 0.4840 at D4 depth 64; only 6/12 seeds cleared the
absolute threshold. Its correct-minus-shuffled mean was 0.2886, but only 7/12
pairs cleared the frozen margin. The 100,000-resample interval [0.1143, 0.4744]
is descriptive and does not revise failure. Soft correct reached 0.9054 at
depth 64 but contracted to about `7.06e-19` by depth 2,048.

Composition substitution (0.8636), sequential/direct agreement (0.5951), and
residual (1.1575) did not establish closure. Patch accuracy 0.2189 exceeded the
wrong-state control 0.1074 but failed its absolute and margin gates; recipient
native accuracy was 0.3333.

Affine D4 transport reached 0.8495 versus 0.1218 shuffled and 0.1069 random, but
decode/re-embed reached 0.9088. No beyond-codebook claim follows.

## Replay interpretation

Seed 300 reproduced every state tensor byte and metric. The raw checkpoint hash
differs because `torch.save` includes replay protocol metadata; the canonical
hash removes only declared provenance fields and matches. This is a
deterministic build check, not a second model-population sample.

## Sparse Stage B audit

Stage B is untrained scaffolding. Its model projection is immutable and excludes
targets, IDs, truth, and masks.

| Family | Bounded witness SHA-256 | Global witness SHA-256 | Result |
|---|---|---|---|
| Monomial | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | `d72912af618d48c6517bf4913d0099b49e7f22191a8a644a935e1d21a6c7da18` | 0/96 bounded collisions; 96/96 globally witnessed by depth 3 |
| Shear | `e24de9b50a3b06c3d958f8b19d31216d81410cd9847d23eeb04a526be9af4190` | `a8f57ab80177320b97ed9736deb1c85b523b74cf6f0efd947f40f22923bc52f3` | 86/96 bounded collisions; 96/96 globally witnessed by depth 3 |

Monomial supports only a bounded same-context length-2--4 novelty statement.
Shear does not. Neither supports unbounded novelty. No Stage B primary ran.

## Prior corrections

V0.1.1 exhausted its D4 coordinate orbit; its edits are native splice
consistency and transport largely aligns the label codebook. V0.2 added strict
primitive partitions and stronger controls but failed 6/26 gates on stability,
absolute closure, and cross-context criteria. Both archives are preserved.

