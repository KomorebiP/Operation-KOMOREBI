# V0.3 sparse affine product task

This staging module removes both shortcuts in the v0.2 task: episodes contain
neither complete primitive transition tables nor length-1 terminal targets in
the key arm.  Five partial demonstrations identify each primitive exactly, but
a table-cell lookup executor cannot take the first query step.

The implementation is isolated at
`src/komorebi_neuralese/sparse_task.py`.  It is a separate API boundary from the
v0.2 dense `EpisodeBatch`/`EpisodeGenerator`; integration should dispatch on a
new task name such as `sparse_affine_product`.

## Observable episode

The visible state is a four-attribute product state

\[
x=(x_0,x_1,x_2,x_3)\in \mathbb F_5^4,
\]

so there are 625 possible states.  Attribute 0 may be called the `focal_label`
and attributes 1--3 the `payload` for stratified transport assays, but all four
attributes are symmetric in task generation.

There are two anonymous operator slots.  The nominal learner-facing
`SparseModelInputs` dataclass supplies exactly:

| Field | Shape | Role |
|---|---:|---|
| `demo_inputs` | `[B, 2, 5, 4]` | Five context examples per slot |
| `demo_outputs` | `[B, 2, 5, 4]` | Corresponding outputs |
| `start_attributes` | `[B, 4]` | Query start |
| `op_slots` | `[B, L]` | Anonymous composition word |

`target_attributes[B,4]` lives in the separate supervision/audit batch and is
the only supervised target.  Context IDs, context fingerprints, family/split
labels, ground-truth operators, and attribution masks do not exist on
`SparseModelInputs`.  Integration code must call `project_model_inputs(batch)`
and pass only the returned object to a model.  The projection copies all four
visible arrays into independent immutable storage, so it cannot retain a back
reference to the supervision envelope.  `solve_model_inputs` demonstrates
that the exact affine oracle needs no hidden field.

The key arm, `sparse_compositional_terminal`, requires `L >= 2` and exposes no
intermediate targets.  Ten observed transition rows out of two 625-row tables
is **0.8% transition-cell coverage**.  Dense tables, canonical identities,
coordinate maps, and traces are absent from the batch schema.

## Primitive families

`family="monomial"` is the clean 8D representability control.  Its primitives
have the form

\[
F(x)=P_{\pm}x+b \pmod 5,
\]

where each row and column of `P_signed` has one nonzero entry in `{+1,-1}`.
The frozen finite catalog has 240 primitives: all 24 coordinate permutations,
each with ten deterministic sign/translation variants.  For lexicographic
permutation index `q` and variant `v`, `k=10q+v`; signs come from the
namespace-bound SHA-256 stream and the bias is the base-5 decoding of
`(137*k + 43) mod 625`.  The full mathematical family has 240,000 maps; the
frozen 240-map subset defines this benchmark.

`family="shear"` is the harder nonlinear boundary family:

\[
y_t=x_t+c x_s+b \pmod 5,\qquad y_j=x_j\ (j\ne t),
\]

for `t != s`, `c in {1,2,3,4}`, and `b in F_5`.  Its 240 possible primitives
are all enumerated.  These maps are invertible and sparsely attributable, but a
generic shear is not a linear action on the simple 8D coordinate torus.  A
failure of an 8D linear recurrence on this family is therefore not evidence
against sparse operator inference.  It should be reported as a harder OOD
stress test, not used as the 8D qualification gate.

## Exact sparse identifiability

For each slot the context fixes an affine frame of five inputs

\[
a,\ a+r_1,\ldots,a+r_4,
\]

where the rows `r_i` form an invertible matrix over GF(5).  Appending a constant
1 to each input makes a 5 by 5 invertible design matrix.  Therefore the five
input/output pairs uniquely determine all coefficients of `y=A x+b` by exact
modular Gaussian elimination.  `infer_affine_map`, `solve_episode`, and
`solve_batch` implement this constructive certificate.  Tests recover every
one of the 240 frozen primitives in both families.

The query sampler rejects any path whose slot/input transition cell appears in
the demonstrations.  Consequently `direct_lookup_execute` returns unknown on
the first step.  Under an arbitrary permutation-table hypothesis, that first
unseen row has `625 - 5 = 620` feasible outputs consistent with the observed
rows.  Thus lookup evidence is non-identifying, even though affine inference is
unique.

## Immutable context splits

Within each family, all 240 primitive maps are SHA-ranked and paired exactly
once into 120 contexts.  Contexts are SHA-ranked into 72 train, 24 development,
and 24 test contexts under:

`komorebi-neuralese/sparse-affine-context-split/v1`

No context or primitive map is reused across splits.  Context truth and
demonstrations use frozen dataclasses and nested tuples; split manifests and
audit records are read-only or JSON-safe.  Frozen catalog digests are:

| Family | Catalog digest |
|---|---|
| `monomial` | `77d8d985a569420e1bcfdd230a6d7b36e2496498028ece9ade77a61d67fa4334` |
| `shear` | `87a40820648367a6c6fc6b03a51ce8335bed71e0dded4b3b39160563c92fa05a` |

The direct split claim is **held-out complete primitive-factor combinations
with a shared marginal factor vocabulary**.  It is not a claim that individual
attributes, coefficients, signs, or translations are absent from test after
appearing in train.  `factor_combination_audit` records both the zero-overlap
combinations and per-split marginal counts.

### Train-closure audit and claim restriction

Direct fingerprint disjointness does not imply algebraic novelty.  The exact
closure audit therefore evaluates two different scopes:

| Family | Unique maps in within-context train support, lengths 2--4 | Held-out primitives equal to one of those maps | Pooled train-generator witnesses through depth 3 |
|---|---:|---:|---:|
| `monomial` | 1,902 | **0 / 96** | **96 / 96**: 12 at depth 2, 84 at depth 3 |
| `shear` | 1,192 | **86 / 96**: 43 dev, 43 test | **96 / 96**: 95 at depth 2, 1 at depth 3 |

For shear, the 86 collisions within the prescribed training language have
minimal depths 2: 52, 3: 25, and 4: 9.  This makes shear unsafe for any claim
that development/test primitives are novel relative to the actual length-2--4
training support.  It remains only an out-of-representation diagnostic.

Monomial has no collision inside the prescribed within-context training
language and may support that narrowly bounded claim.  It does **not** support
an unbounded group-element novelty claim: after pooling primitives across
contexts, every held-out map has an exact train-word witness of length at most
three.  The same unbounded restriction applies to shear.

These are equalities of complete underlying affine maps, not assertions that
training sampled every row of a composed map.  The audit is intentionally
conservative.  `audit_train_closure` returns the counts and certificate
digests, `train_closure_witnesses` returns reconstructable exact certificates,
and `require_train_closure_safe` raises rather than silently licensing an
unsupported novelty claim.  In particular, the bounded guard passes for
monomial, fails for shear, and the global-generator guard fails for both.

## Representability and interventions

`compose_affine` and `compose_word` compute exact composed maps.  Full
625-state renderers exist only as audit utilities; rendered tables never enter
an episode.

For signed-monomial maps, `torus_encode` represents each attribute by a
cosine/sine pair.  If

\[
y_j=s_j x_{\pi(j)}+b_j,
\]

the output block receives

\[
R(2\pi b_j/5)\,\operatorname{diag}(1,s_j)
\]

from input block `pi(j)`.  `monomial_torus_matrix` builds the resulting 8 by 8
orthogonal matrix; exhaustive tests verify the action on all 625 states for all
240 primitives.

Audit-only `dependency_masks[B,2,4,4]`, `write_masks[B,2,4]`,
`update_read_masks[B,2,4]`, and `preserved_masks[B,2,4]` support attribute-level
specificity and invariance assays.  `sample_intervention` returns paired
relevant/irrelevant attribute perturbations.  These masks and context IDs live
only in the audit envelope; the typed model projection makes their exclusion
executable rather than conventional.

Primary metric names proposed by the module are:

- `terminal_exact_match`
- `attribute_accuracy`
- `demo_consistency`
- `operator_completion_exact_match`
- `direct_lookup_coverage`
- `relevant_effect_specificity`
- `irrelevant_effect_invariance`
- `preserved_attribute_accuracy`

Run the isolated tests with:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" -m pytest -q
```
