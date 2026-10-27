# Micro OSL Dataset Specification v0.1.1

## 1. Purpose

The dataset is generated from executable finite systems rather than collected prose. Every record is derived in this order:

1. Select a typed finite world and a legal initial state.
2. Select a formal operator program.
3. Execute the program exactly.
4. Compute all observable answers from the final state.
5. Render the initial state and program as controlled natural language.
6. Render one question and its exact answer.
7. Attach reproducibility, transformation, and evaluation metadata.

This direction of construction prevents the prose from becoming the source of truth. A model sees text, but evaluation is grounded in the formal execution.

## 2. Semantic worlds

The worlds are separate types. Operators from one world cannot be applied in another.

### 2.1 Algebra world

State:

```text
left  in {false, true}
right in {false, true}
```

There are four legal states.

Operators:

| Operator | Exact effect |
|---|---|
| `flip_left` | Negate `left` |
| `flip_right` | Negate `right` |
| `set_left` | Set `left` to true |
| `clear_left` | Set `left` to false |
| `set_right` | Set `right` to true |
| `clear_right` | Set `right` to false |

Queries report the left status, right status, or whether both registers have the same status.

Declared exact laws include:

\[
F_L^2=I,
\qquad
F_R^2=I,
\qquad
S_L^2=S_L,
\qquad
F_LF_R=F_RF_L.
\]

Order is deliberately significant for operations on the same register. For example, setting and then flipping the left register is not the same transformation as flipping and then setting it.

### 2.2 Provenance world

State:

```text
a in {none, observed, reported, imagined, inferred, quarantined, endorsed}
b in {none, observed, reported, imagined, inferred, quarantined, endorsed}
```

There are 49 legal states.

Operators:

```text
observe_a       observe_b
tell_a_b        tell_b_a
imagine_a       imagine_b
infer_a         infer_b
quarantine_a    quarantine_b
endorse_a       endorse_b
```

Important transition rules:

- Observation assigns direct `observed` provenance.
- Telling transfers an existing claim and marks the receiver as `reported`.
- Imagination assigns `imagined` without direct observation.
- Inference changes an existing record to `inferred`.
- Quarantine changes an existing record to `quarantined`.
- Endorsement changes a reported or quarantined record to `endorsed`.
- Missing preconditions make the relevant transition a no-op rather than an undefined program.

Queries report each agent's exact provenance status, whether it counts as direct observation, and whether it is permitted for planning. `observed`, `inferred`, and `endorsed` are plannable. Other statuses are not.

Declared laws include observation idempotence, quarantine idempotence, and commutation of the two agents' independent imagination operations.

### 2.3 Resource world

State:

```text
cap       in {0, 1, 2}
proof     in {absent, available, consumed}
relay_a   in {false, true}
relay_b   in {false, true}
last      in {none, authorized, rejected}
```

There are 108 legal states.

Operators:

```text
grant_one        grant_two        revoke
use_cap_a        use_cap_b
issue_proof
consume_proof_a  consume_proof_b
```

Capability use consumes one remaining use and opens the selected relay. Use with no remaining capability is rejected. A proof token can be consumed exactly once. Reuse of an absent or consumed proof is rejected. Rejection updates the last-decision field but does not open the relay.

Queries report remaining capability count, proof status, each relay status, and the last authorization decision.

Declared laws include revocation idempotence, one-use grant idempotence, and commutation of a two-use grant with proof issuance.

## 3. Exact contextual equivalence

For a world with legal state set \(S\), a program \(p\) induces a total transformation

\[
T_p:S\rightarrow S.
\]

Two programs are equivalent precisely when

\[
p\equiv q
\quad\Longleftrightarrow\quad
T_p(s)=T_q(s)
\text{ for every }s\in S.
\]

The generator enumerates every legal state and hashes the complete ordered output signature. The `canonical_transform_id` therefore identifies an exact complete transformation, not equality on a sampled starting state. For non-equivalent programs the executor can return a concrete witness state where their outputs differ.

This v0.1 quotient uses complete state equality as its observation doctrine. Later experiments may deliberately coarsen the doctrine to task, causal, or audit observables, but those should receive different quotient identifiers.

## 4. Rendering

Each formal trace can be expressed through five renderer families:

| Renderer | Style |
|---|---|
| `direct` | Initial state followed by direct event sentences |
| `narrative` | Episode prose with temporal connectors |
| `dialogue` | Monitor statements and an evaluator question |
| `log` | Initial-state and numbered-event audit entries |
| `passive` | Ledger or protocol phrasing with passive framing |

The normal training lexicon uses names such as Mira and Niko and nouns such as lamps, gate reports, passes, and relays. The lexical split uses disjoint names and nouns such as beacons, portal claims, credits, and channels.

The renderer never changes the formal program. Random wording choices are controlled by a stored seed derived from the dataset generator.

### 4.1 Audited nuisance markers

Every story, including renaming story overrides, begins with a reusable pair of
alphabetic pseudoword case markers:

```text
Case markers bavel and bovir were assigned before review.
```

The pair is a deterministic function only of the rendering seed and lexicon.
It does not read the world, state, program, query, answer, or split. It is
therefore presentation entropy rather than semantic information. The marker is
stored in `metadata.surface_marker` and validation checks that the story prefix
and lexicon-specific pool agree.

Each lexicon has two pools of sixteen tokens, giving 256 reusable combinations.
The train and lexical marker vocabularies are disjoint. All 64 marker tokens,
the training nonces, and the evaluation nonces occupy distinct buckets under
the frozen 2,048-bucket tokenizer. No numeric case identifier is inserted into
model input.

This layer is needed because some finite strata otherwise have too little exact
surface support. For example, a fixed algebra composition and query originally
had only four initial states times five renderers, or twenty exact train-lexicon
inputs. With the 256 nuisance combinations it has 5,120 exact realizations.
Markers are deliberately reused across states, answers, worlds, and splits, so
they cannot identify an example or encode a label. Matched renaming training
pairs, evaluation triplets, and every member of a counterfactual bundle use the
same marker.

## 5. Record format

Each JSONL line is one question-answer record. A representative record is:

```json
{
  "id": "rec_...",
  "split": "heldout_pair",
  "world": "resources",
  "semantic_id": "sem_...",
  "renderer": "narrative",
  "story": "The episode began with ...",
  "question_id": "cap_remaining",
  "question": "How many bounded passes remain?",
  "answer": "one",
  "answer_text": "one",
  "metadata": {
    "lexicon": "train",
    "program_length": 2,
    "split_role": "evaluation",
    "evaluation_family": "heldout_pair",
    "heldout_composition": ["grant_two", "use_cap_a"]
  },
  "initial_state": {},
  "program": [{"op": "grant_two"}, {"op": "use_cap_a"}],
  "canonical_transform_id": "resources:...",
  "state_trace": [{}, {}, {}],
  "final_state": {}
}
```

The formal fields are retained by default for audit, supervised arms, and structural evaluation. The answer-only loader must expose only `story`, `question`, and `answer` to the optimization objective. It must not encode formal fields as input.

Field roles:

| Field | Role |
|---|---|
| `id` | Content-addressed rendered record identity |
| `semantic_id` | Identity of world, initial state, and formal program |
| `canonical_transform_id` | Complete state-map equivalence class |
| `state_trace` | Initial and every intermediate formal state |
| `metadata` | Split-specific diagnostics and pairing information |
| `metadata.surface_marker` | Audited label-independent presentation marker |

Every record carries a non-optional `metadata.split_role` value. `train`,
`renaming_train`, and `renaming_scrambled_train` are `training`,
`iid_validation` is `validation`, and every
reported test shard is `evaluation`. This is a protocol boundary, not merely a
label. Validation and training code must select shards through these roles.

`answer` always stores the canonical formal label. This keeps the output class space stable across lexicons. `answer_text` stores the lexically rendered form, such as `active` for the canonical algebra answer `lit` in the lexical split. Neural targets use the canonical `answer` field.

## 6. Evaluation splits

### Train

Programs have lengths in the configured training range. Programs containing sealed pair, triple, or multi-step law patterns are rejected. Transformations reserved for held-out pair and triple tests are also excluded.

### Renaming train

`renaming_train` contains calibrated nonce-command episodes used only to teach
the episode-local binding mechanism. It uses the training nonce vocabulary and
is optimization data, never reported evaluation data. The same sealed
composition and reserved-transformation exclusions used by `train` apply here.
Every target program contains at least two distinct operators so its
calibration alignment admits a nonidentity negative control.

### Scrambled renaming train

`renaming_scrambled_train` is paired one-to-one with `renaming_train`. Each
pair shares `pair_id`, formal semantics, answer, question, operator mapping,
target commands, rendering seed, nuisance marker, and target-episode text. The
scrambled member applies a deterministic nonidentity permutation to nonce
labels only inside the calibration demonstrations. Target commands remain
unchanged.

Every used nonce occurs once per diagnostic state in the calibration block.
Permuting those labels therefore preserves the exact model-token multiset and
format of the complete story. This shard is a matched negative control for
learning from calibration alignment rather than merely recognizing the
calibration format or nonce vocabulary.

### IID validation

`iid_validation` uses familiar lengths, lexicon, operators, and grammar
families. Standard and full presets may use it for best-checkpoint selection;
the confirmatory preset records it as a diagnostic while evaluating the fixed
final checkpoint after an identical eight-epoch budget. It must never be pooled
into reported test metrics.

### IID test

`iid_test` is generated independently from `iid_validation` and is the only
reported IID estimate. Exact rendered inputs are deduplicated against all
training shards, validation, and earlier clean evaluation shards. High IID test
accuracy is still not evidence of a reusable operator language.

### Lexical

Formal structures remain familiar while names, nouns, state descriptions, and query vocabulary are changed. `answer_text` changes with the lexicon, while the scored `answer` remains canonical so the task does not introduce impossible unseen output classes. This tests whether success survives a controlled input-language shift.

### Held-out pair

Every primitive is present elsewhere, but selected ordered pairs are excluded from training. The frozen pairs are:

| World | Held-out pairs |
|---|---|
| Algebra | `flip_left,set_right` and `clear_left,flip_right` |
| Provenance | `observe_a,imagine_b` and `observe_b,quarantine_a` |
| Resources | `grant_two,use_cap_a` and `issue_proof,use_cap_b` |

Records are assigned by a deterministic world/query stratum plan. World counts
differ by at most one and query counts within a world differ by at most one,
apart from unavoidable incomplete final cycles.

### Held-out triple

Selected ordered triples are excluded from training:

| World | Held-out triples |
|---|---|
| Algebra | `set_left,flip_right,flip_left` and `clear_right,flip_left,flip_right` |
| Provenance | `observe_a,tell_a_b,quarantine_b` and `observe_b,tell_b_a,endorse_a` |
| Resources | `grant_two,use_cap_a,use_cap_b` and `issue_proof,consume_proof_a,consume_proof_b` |

### Law

Records alternate between the two sides of declared exact laws. Law identifiers, law kind, side, and paired program are retained in metadata. Evaluation checks both task answers and consistency across equivalent programs.

### Length

Training uses lengths one through four in standard and full configurations. The length split begins at five. Standard ends at eight and full ends at twelve. This isolates extrapolation in execution depth.

### Counterfactual

Records are generated in complete matched bundles. One formal operation is replaced while the initial state, renderer, and wording seed are held fixed. For every query in that world, the bundle contains a base record and a counterfactual record. The bundle is retained only if at least one query answer changes. This supplies both affected and unaffected queries from the same intervention whenever the world permits them.

Metadata includes:

- `pair_id`
- `variant` as base or counterfactual
- `intervention_index`
- `changed_query_ids`
- `bundle_query_ids`
- `query_expected_to_change`

Complete bundle sizes are six records for algebra, twelve for provenance, and ten for resources. Every nonempty counterfactual shard includes at least one complete bundle from every configured world. Further bundles are selected to minimize the spread in world-level record counts until the requested size is reached or exceeded. Bundles are never truncated, so small smoke targets can round up substantially.

### Renaming

Each evaluation episode produces a matched triplet with `canonical`, `renamed`,
and `scrambled` variants. All three records share their world, initial state, formal
program, renderer context, question, exact answer, trace, final state, and
canonical transformation. They differ only in how the target program is
presented. The canonical member uses ordinary lexical-shift descriptions. The
renamed member supplies exact before-and-after calibration demonstrations and
then gives nonce commands. The scrambled member preserves the renamed member's
target commands, story format, and exact model-token multiset while
deterministically permuting nonce labels only in calibration demonstrations.

All three members carry the same `pair_id` and an explicit `variant`. The
renamed and scrambled members carry identical `operator_mapping`,
`target_commands`, `render_seed`, and `nonce_pool: evaluation` metadata.
`calibration_label_permutation` is identity for `renamed` and nonidentity for
`scrambled`, which gives metrics enough information to compare the matched
positive and negative controls.

The mapping changes by episode. Evaluation nonces come from a pool that is
strictly disjoint from the `renaming_train` pool. The two pools are also
collision-free within and across pools under the frozen 2,048-bucket tokenizer,
so no evaluation nonce can inherit a training-nonce embedding. The
demonstrations identify the active transformations for that episode. Every
target contains at least two distinct operators. Requested shard size is
required to be divisible by three because triplets are never truncated. The
configuration is rejected otherwise, so generated cardinality never silently
differs from the request. Smoke requests 12 records,
standard and confirmatory request 1,998, and full requests 9,999.

### Balancing and clean-input policy

`iid_validation`, `iid_test`, lexical, held-out pair, held-out triple, law, and
length shards use deterministic balanced world/query plans. Renaming balances
triplet bundles rather than individual variants. Counterfactual generation uses
complete all-query bundles and chooses bundle counts to minimize record-count
imbalance across worlds.

The generator rejects exact `(story, question)` overlap with every training
shard for every validation and evaluation record. It also deduplicates exact
rendered inputs across clean shards, which makes IID validation and IID test
operationally independent at the rendered-input level. Semantic reuse remains
allowed when the purpose of a split requires it.

## 7. Dataset files

The generator exports the authoritative split groups:

```text
TRAINING_SPLITS   = train, renaming_train, renaming_scrambled_train
VALIDATION_SPLITS = iid_validation
EVALUATION_SPLITS = iid_test, lexical, heldout_pair, heldout_triple,
                    law, length, counterfactual, renaming
```

Loaders and reports should use these constants rather than infer roles from
filename position.

Generation writes one file per split:

```text
train.jsonl
renaming_train.jsonl
renaming_scrambled_train.jsonl
iid_validation.jsonl
iid_test.jsonl
lexical.jsonl
heldout_pair.jsonl
heldout_triple.jsonl
law.jsonl
length.jsonl
counterfactual.jsonl
renaming.jsonl
manifest.json
```

The manifest format is `micro-osl-jsonl-v1.1`. It records schema version
`0.1.1`, generator version `0.1.1`, the resolved generator configuration,
record count, byte-level SHA-256, and semantic SHA-256 for every shard. JSON
serialization and line endings are canonicalized for reproducibility. The
semantic digest projects away record ID, renderer, story wording, question
wording, rendered answer text, lexicon metadata, and nuisance-marker metadata.
It retains the formal state, program, query, canonical answer, transformation
identifiers, pairing, intervention, and other protocol-semantic metadata. It is therefore distinct
from the byte hash and stable under surface-only rerendering.

## 8. Required integrity checks

Before training, validation must confirm:

1. Every record parses and has a unique record identifier within its split.
2. Every state and program is legal for its world.
3. Re-execution reproduces the complete stored state trace and final state.
4. The stored answer matches the exact query answer after rendering.
5. `canonical_transform_id` matches the exhaustive transformation signature.
6. All declared laws hold on every legal state.
7. Counterfactual records form complete all-query bundles and their change metadata are exact.
8. Renaming episodes contain identifiable demonstrations and valid mappings.
9. Correct and scrambled renaming training shards form exact one-to-one matched controls.
10. Renaming evaluation records form complete canonical/renamed/scrambled triplets.
11. Scrambled controls preserve target text, format, and exact model-token multisets while changing only calibration alignment.
12. Training and evaluation nonce vocabularies are disjoint.
13. Every shard has the correct training, validation, or evaluation role.
14. Balanced shards satisfy their world and query count tolerances.
15. Clean validation and evaluation shards have zero exact rendered overlap with training.
16. Every story has a valid lexicon-specific nuisance marker, and matched bundles share it.
17. Train-like records do not contain sealed held-out compositions or their reserved complete transformations.
18. Manifest schema, counts, and hashes match files on disk.

## 9. Leakage policy

The following are treated as leakage failures:

- A transformation reserved for the held-out pair/triple tests appears in training under another program.
- A renderer or metadata field deterministically reveals the answer.
- A nuisance marker falls outside its declared lexicon pool or disagrees across a matched bundle.
- Formal fields reach the answer-only model input.
- An evaluation nonce appears in either renaming training shard, or a training nonce appears in evaluation.
- A renaming training pair or evaluation triplet is incomplete or differs in formal semantics.
- A scrambled control changes target commands, token multiset, story format, or anything outside calibration label alignment.
- Counterfactual variants cross train and test boundaries.
- An exact rendered input is shared by training and a clean validation or test shard.
- An untracked near-duplicate violates the declared purpose of its split.

Majority, question-conditioned majority, and TF-IDF controls must be run before interpreting neural performance. If a lexical control solves a hard split, that split must be repaired before a scientific run.

Some semantic trace reuse is intentional outside the held-out transformation tests. IID estimates ordinary resampling, lexical reuse isolates the input-language change, law records include a familiar side as a control, and counterfactual and renaming records deliberately hold formal structure fixed while changing one factor. Validation reports both counts and rates for semantic-query and exact-rendered-input overlap with training per split. Exact rendered overlap is a hard zero for every clean shard. The held-out pair/triple transformation boundary remains a hard zero-overlap rule.

## 10. Scope limits

The text is coherent but controlled. It does not yet represent the breadth or ambiguity of unrestricted language. Exact finite equivalence is a strength for adjudicating this experiment, but success here does not by itself establish operator emergence in large general-purpose models or real-world environments.
