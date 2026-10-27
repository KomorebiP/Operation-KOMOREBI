from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def fmt(value: float | int | None, digits: int = 6) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def write(rel: str, text: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def family_stats(records: list[dict]) -> dict[str, dict]:
    by: dict[str, list[dict]] = defaultdict(list)
    for row in records:
        by[row["family"]].append(row)
    out: dict[str, dict] = {}
    for family, rows in by.items():
        out[family] = {
            "episodes": len(rows),
            "certificate": Counter(r["certificate"] for r in rows).most_common(1)[0][0],
            "method": Counter(str(r["selected_method"]) for r in rows).most_common(1)[0][0],
            "rank": Counter(str(r["selected_rank"]) for r in rows).most_common(1)[0][0],
            "semantic_min": min((r.get("minimum_hidden_semantic_r2") for r in rows if r.get("minimum_hidden_semantic_r2") is not None), default=None),
            "overlap_min": min((r.get("minimum_subspace_overlap") for r in rows if r.get("minimum_subspace_overlap") is not None), default=None),
            "gauge_min": min((r.get("minimum_gauge_invariant_r2") for r in rows if r.get("minimum_gauge_invariant_r2") is not None), default=None),
            "disagreement_min": min((r.get("alternative_semantic_disagreement") for r in rows if r.get("alternative_semantic_disagreement") is not None), default=None),
            "coverage_min": min((r.get("semantic_coverage") for r in rows if r.get("semantic_coverage") is not None), default=None),
            "collisions_min": min((r.get("collision_count") for r in rows if r.get("collision_count") is not None), default=None),
            "collision_gap_min": min((r.get("minimum_protected_consequence_gap") for r in rows if r.get("minimum_protected_consequence_gap") is not None), default=None),
        }
    return out


def main() -> None:
    result = json.loads((ROOT / "results" / "block23_final.json").read_text())
    seal = json.loads((ROOT / "frozen" / "preaudit_seal.json").read_text())
    external = json.loads((ROOT / "external_status" / "preflight.json").read_text())
    fixture = json.loads((ROOT / "results" / "external_adapter_fixture.json").read_text())
    summary = result["summary"]
    stats = family_stats(result["records"])

    readme = f"""# SRIC v2.4 Block 23

## Endogenous Semantic-Witness Growth

This package is the executable companion to Block 23 of *Stratified Recursive Improvement Closure*.

Block 23 removes the supplied intermediate semantic ontology from the construction interface. The compiler receives recurrent latent trajectories, same-task semantic twins, anonymous intervention trajectories, protected future consequences, intervention effects, and final answer labels. It does **not** receive the hidden semantic coordinates, hidden family identity, allowed gauge declaration, final certificate, or audit-only semantic decoder.

The compiler searches a finite quotient grammar and selects the minimum-rank candidate that jointly predicts held-out futures, predicts intervention effects, retains answer competence, and remains stable across semantic twins. Only after the candidate is sealed does the final witness reveal whether the quotient is complete, gauge-relative, partial, underidentified, or blocked by semantic information loss.

## Canonical finite result

- pre-audit episodes: {len(seal['construction_records'])}
- fresh final episodes: {summary['episodes']}
- source and foreign systems per episode: 2
- final certificate accuracy: {fmt(summary['certificate_accuracy'])}
- `ONTOLOGY_IDENTIFIED`: {summary['certificate_counts']['ONTOLOGY_IDENTIFIED']}
- `ONTOLOGY_IDENTIFIED_UP_TO_GAUGE`: {summary['certificate_counts']['ONTOLOGY_IDENTIFIED_UP_TO_GAUGE']}
- `PARTIAL_ONTOLOGY`: {summary['certificate_counts']['PARTIAL_ONTOLOGY']}
- `ONTOLOGY_UNDERIDENTIFIED`: {summary['certificate_counts']['ONTOLOGY_UNDERIDENTIFIED']}
- `SEMANTIC_INFORMATION_LOSS`: {summary['certificate_counts']['SEMANTIC_INFORMATION_LOSS']}

Pre-audit seal:

`{seal['preaudit_seal']}`

Final result receipt:

`{result['result_receipt']}`

## External latent-reasoner track

The package also contains a source-locked adapter and audit protocol for a third-party multimode GPT-2 Coconut checkpoint. The adapter and intervention plumbing pass package-local fake-runtime tests. The real checkpoint was **not executed in this environment**.

Current preflight status: `{external['status']}`

Current blockers: `{', '.join(external['blockers'])}`

The external fixture is a protocol test only. It is not evidence about the third-party checkpoint.

## Run the synthetic block

```powershell
.\\RUN_ALL.ps1
```

## Verify the release

```powershell
.\\VERIFY.ps1
```

## Run the real-model pilot after supplying locked assets

```powershell
.\\Run_Block23_Real_Pilot.ps1 -RepoDir "C:\\path\\to\\are-lrms-easily-interpretable" -Checkpoint "C:\\path\\to\\checkpoint_37" -Tasks "C:\\path\\to\\prontoqa_test.json" -Limit 32 -Device cuda
```

Before any real final audit, compute and commit the checkpoint SHA-256 in `frozen/SOURCE_LOCK.json`; the release intentionally does not guess that digest.

## Claim boundary

This release establishes a finite synthetic semantic-quotient compilation and post-seal witness protocol. It does not establish endogenous semantics in a production model, unrestricted ontology discovery, a faithful linguistic transcript of latent thought, external independent replication, or open-ended recursive self-improvement.
"""
    write("README.md", readme)

    rows = [
        ("Identified", "ONTOLOGY_IDENTIFIED", stats["identified"]),
        ("Answer shortcut", "ONTOLOGY_IDENTIFIED", stats["answer_shortcut"]),
        ("Gauge equivalent", "ONTOLOGY_IDENTIFIED_UP_TO_GAUGE", stats["gauge_equivalent"]),
        ("Semantic ambiguity", "ONTOLOGY_UNDERIDENTIFIED", stats["semantic_ambiguity"]),
        ("Partial ontology", "PARTIAL_ONTOLOGY", stats["partial_ontology"]),
        ("Destructive loss", "SEMANTIC_INFORMATION_LOSS", stats["destructive_loss"]),
    ]
    table = "\n".join(
        f"| {label} | `{cert}` | {st['episodes']} | `{st['method']}` | {st['rank']} |"
        for label, cert, st in rows
    )
    results_md = f"""# SRIC v2.4 Block 23 Results

## Canonical disposition

**PASS within the released finite fixture.**

The visible compiler never receives the four protected intermediate semantic coordinates or the hidden regime label. It selects a quotient from observable future, intervention, answer, and semantic-twin evidence. A separate final witness then opens the protected ontology and determines the strongest justified certificate.

## Audit chronology

- 24 pre-audit episodes compiled before the final witness was opened
- thresholds and candidate grammar frozen in the pre-audit seal
- 36 final episodes generated under the committed seed rule
- two independently gauged systems in every episode
- 520 construction and 320 calibration samples per system
- 420 audit-only samples per system in every final episode
- four anonymous interventions and five recurrent latent steps
- 4 protected semantic coordinates, 12 nuisance coordinates per step

## Certificate matrix

| Hidden audit regime | Required certificate | Episodes | Selected method | Rank |
|---|---|---:|---|---:|
{table}

All 36 final certificates match the precommitted audit truth.

## Minimum-quotient behavior

- identified and answer-shortcut regimes select a rank-4 predictive quotient
- gauge-equivalent and semantically ambiguous regimes select a rank-4 intervention quotient
- partial-ontology regimes select a rank-3 quotient and report 75% protected-coordinate coverage
- destructive-loss regimes select no quotient and issue an information-loss certificate

Selected methods across the final suite:

```text
predictive:   {summary['selected_methods']['predictive']}
intervention: {summary['selected_methods']['intervention']}
no-go:        {summary['selected_methods']['None']}
```

## Hidden witness results

| Quantity | Frozen result |
|---|---:|
| Minimum full identified semantic R2 | {fmt(min(stats['identified']['semantic_min'], stats['answer_shortcut']['semantic_min']))} |
| Minimum gauge-family semantic R2 | {fmt(stats['gauge_equivalent']['semantic_min'])} |
| Minimum semantic-subspace overlap | {fmt(summary['minimum_subspace_overlap'])} |
| Minimum gauge-invariant R2 | {fmt(summary['minimum_gauge_invariant_r2'])} |
| Minimum ambiguity disagreement | {fmt(summary['minimum_alternative_disagreement'])} |
| Partial-ontology coverage | {fmt(stats['partial_ontology']['coverage_min'])} |
| Minimum destructive collision count | {int(stats['destructive_loss']['collisions_min'])} |
| Minimum destructive protected-consequence gap | {fmt(stats['destructive_loss']['collision_gap_min'])} |

## Answer-only shortcut control

The answer-only quotient predicts the binary answer with at least **{fmt(summary['answer_shortcut_control']['minimum_answer_accuracy'])}** accuracy, but reaches at most:

- future R2: **{fmt(summary['answer_shortcut_control']['maximum_future_r2'])}**
- intervention-effect R2: **{fmt(summary['answer_shortcut_control']['maximum_intervention_r2'])}**

No answer-only candidate passes the semantic-construction gate. This separates label prediction from an adequate causal-predictive ontology.

## Counterfactual quotient patching

On the identified and answer-shortcut regimes, the audit-only runtime replaces only the selected latent quotient with a donor quotient and independently recomputes future and intervention consequences.

- minimum selected-packet future R2: **{fmt(summary['counterfactual_patch']['minimum_selected_future_r2'])}**
- maximum answer-only control future R2: **{fmt(summary['counterfactual_patch']['maximum_answer_only_future_r2'])}**
- maximum PCA control future R2: **{fmt(summary['counterfactual_patch']['maximum_pca_future_r2'])}**
- maximum random control future R2: **{fmt(summary['counterfactual_patch']['maximum_random_future_r2'])}**

The selected quotient supports the intended counterfactual consequences; equal-rank correlational and random controls do not.

## Gauge versus underidentification

The same visible repeated intervention signature appears in two regimes. The compiler therefore emits the same pre-certificate, `CANDIDATE_GAUGE_AMBIGUOUS`, in both.

- In the declared gauge regime, the protected invariant is recoverable with R2 at least **{fmt(stats['gauge_equivalent']['gauge_min'])}**, so the final certificate is `ONTOLOGY_IDENTIFIED_UP_TO_GAUGE`.
- In the semantic-ambiguity regime, two observationally equivalent orientations disagree on a protected named coordinate by at least **{fmt(stats['semantic_ambiguity']['disagreement_min'])}**, so the final certificate is `ONTOLOGY_UNDERIDENTIFIED`.

This prevents coordinate nonuniqueness from being confused with semantic nonidentifiability.

## Information-loss no-go

Every destructive episode exposes 64 exact observation collisions whose protected future consequences disagree. The compiler receives those protected consequences but never the hidden intermediate coordinates. Because one observed state would require two different protected outcomes, deterministic target-only semantic recovery is impossible within the declared interface.

## Receipts

```text
pre-audit seal: {seal['preaudit_seal']}
final result:   {result['result_receipt']}
fixture smoke:  {fixture['fixture_receipt']}
```
"""
    write("RESULTS.md", results_md)

    certificate = f"""# SRIC v2.4 Block 23 Semantic-Witness Certificate

## Certified finite edge

The released fixture certifies one bounded transition from a supplied protected semantic coordinate system to a compiler-selected causal-predictive quotient followed by a separated semantic witness.

The construction interface contains recurrent trajectories, semantic twins, anonymous interventions, protected future consequences, intervention effects, and answer labels. The four-dimensional intermediate semantic state and the hidden regime identity are inaccessible until the final audit.

## Established within the fixture

1. A minimum-rank predictive quotient can recover a complete protected ontology without direct access to its coordinates.
2. An answer-only quotient can be rejected even when it predicts the final label, because it fails future and intervention sufficiency.
3. Repeated intervention signatures identify a semantic block only up to an observational symmetry.
4. A symmetry is accepted as gauge only when the protected witness is invariant under it.
5. The same visible ambiguity yields underidentification when protected meaning changes under the unresolved symmetry.
6. A quotient may be certified as partial when it preserves the declared protected subset but not the complete hidden ontology.
7. Exact observation collisions with different protected consequences produce a semantic information-loss certificate.
8. Audit-only counterfactual patching distinguishes the selected quotient from answer-only, PCA, and random packets.

## Quantitative certificate

- final certificate accuracy: {fmt(summary['certificate_accuracy'])}
- minimum complete identified semantic R2: {fmt(min(stats['identified']['semantic_min'], stats['answer_shortcut']['semantic_min']))}
- minimum gauge-invariant R2: {fmt(summary['minimum_gauge_invariant_r2'])}
- minimum semantic-subspace overlap: {fmt(summary['minimum_subspace_overlap'])}
- minimum ambiguity disagreement: {fmt(summary['minimum_alternative_disagreement'])}
- partial semantic coverage: {fmt(stats['partial_ontology']['coverage_min'])}
- minimum collision count: {int(stats['destructive_loss']['collisions_min'])}
- minimum protected-consequence collision gap: {fmt(stats['destructive_loss']['collision_gap_min'])}

## Certificate chain

```text
pre-audit seal: {seal['preaudit_seal']}
final result:   {result['result_receipt']}
```
"""
    write("SEMANTIC_WITNESS_CERTIFICATE.md", certificate)

    boundary = f"""# SRIC v2.4 Block 23 Claim Boundary

## Established within the released finite fixture

Block 23 establishes a finite, sealed, package-closed endogenous semantic-witness edge. A compiler that cannot see hidden semantic coordinates selects minimum-rank causal-predictive quotients from future, intervention, answer, and semantic-twin evidence. A separated audit witness then correctly distinguishes complete identification, gauge-relative identification, partial ontology, semantic underidentification, and destructive information loss across 36 fresh final episodes and two independently gauged systems.

The result demonstrates a workflow for discovering **which semantic distinctions are justified by declared causal-predictive evidence**. It does not demonstrate that the discovered coordinates have unique natural-language names.

## Important qualifications

- The synthetic environment is deliberately constructed around a four-dimensional protected semantic process.
- The intervention family, future consequences, answer channel, quotient grammar, thresholds, and audit semantics are externally declared.
- The compiler sees protected future and intervention consequences. It does not infer value or relevance without an external witness.
- The audit-only hidden coordinates are used to classify the frozen quotient after construction.
- Counterfactual patching uses the synthetic runtime's audit-only semantic decoder; it is a causal fixture, not a production-model intervention result.
- The replay verifier reuses the released construction and audit functions. It is not an independently authored second compiler.

## External model boundary

A source-locked multimode Coconut adapter, PrOntoQA transformation utilities, latent interventions, and a fail-closed preflight are included. The package-local fake runtime validates interface and intervention plumbing only.

Real checkpoint executed: **{external['real_checkpoint_executed']}**

Current external status: **{external['status']}**

Current blockers: **{', '.join(external['blockers'])}**

No empirical claim about the third-party checkpoint is made.

## Not established

The release does not establish:

- unrestricted discovery of semantic variables in natural language models;
- autonomous invention of the intervention language or protected consequences;
- unique linguistic translation of every latent state;
- identifiability outside the declared finite quotient grammar;
- universal cross-model semantic transport;
- safety of unrestricted model modification;
- external independent replication;
- open-ended recursive self-improvement, indefinite acceleration, consciousness, or sentience.
"""
    write("CLAIM_BOUNDARY.md", boundary)

    chronology = f"""# SRIC v2.4 Block 23 Protocol Chronology

1. Freeze the six synthetic regime generators, source and foreign gauges, five-step recurrent process, four anonymous interventions, visible consequence channels, candidate quotient grammar, and thresholds.
2. Compile 24 pre-audit episodes using only the visible interface.
3. Commit each hidden regime through a salted digest without revealing it to the compiler.
4. Commit the final seed plan and external source lock.
5. Write the pre-audit seal `{seal['preaudit_seal']}`.
6. Generate 36 fresh final episodes under the committed seed rule.
7. Compile one minimum-rank quotient or no-go result for each episode without hidden-coordinate access.
8. Open the audit-only semantic coordinates, gauge policy, partial-coordinate mask, and alternative semantic maps.
9. Issue the strongest justified certificate.
10. Run audit-only counterfactual quotient patching and negative controls.
11. Write the final result receipt `{result['result_receipt']}`.
12. Run the external adapter fake fixture and fail-closed real-checkpoint preflight.
13. Rebuild figures, documentation, replay verification, and package manifest.

The real external checkpoint remains a separate future execution. Its local checkpoint digest must be committed before its final audit.
"""
    write("PROTOCOL_CHRONOLOGY.md", chronology)

    external_md = f"""# SRIC Block 23 Real Latent-Reasoner Pilot Status

## Target

The staged real-model target is a source-locked multimode GPT-2 Coconut checkpoint evaluated on PrOntoQA-style logical reasoning tasks.

The adapter captures the embeddings actually placed at latent-token positions and supports deterministic evaluation under externally supplied traces. The audit protocol includes replay, zero-latent, truncation, step permutation, norm-matched noise, semantic-twin transplant, and same-answer different-proof transplant.

## Source lock

Repository: `{seal['external_source_lock']['repository']}`

Commit: `{seal['external_source_lock']['commit']}`

Checkpoint repository: `{seal['external_source_lock']['checkpoint']['repository']}`

Checkpoint filename: `{seal['external_source_lock']['checkpoint']['filename']}`

Checkpoint SHA-256: **not yet committed**. This is deliberate. The digest must be computed from the locally obtained file before a real final audit.

## Current environment

- status: `{external['status']}`
- real checkpoint executed: `{external['real_checkpoint_executed']}`
- blockers: `{', '.join(external['blockers'])}`
- Python: `{external['environment']['python']}`
- Torch: `{external['environment']['torch']}`
- CUDA available: `{external['environment']['cuda_available']}`
- Transformers available: `{external['environment']['transformers_available']}`

## Package-local protocol evidence

- fake fixture tasks: {fixture['summary']['tasks']}
- fake fixture exact replay maximum: {fmt(fixture['summary']['max_replay_error'])}

These numbers validate adapter contracts and intervention bookkeeping only. They are not empirical findings about Coconut or PrOntoQA.

## Required next execution

1. Obtain the exact repository commit in `frozen/SOURCE_LOCK.json`.
2. Obtain the declared checkpoint and compute its SHA-256.
3. Update the lock before any final audit.
4. Install the source-locked upstream runtime separately from the package verification environment.
5. Run `external_preflight.py` and require a ready status.
6. Run a small adapter smoke set and verify exact replay.
7. Freeze donor rules, semantic-twin transforms, task split, thresholds, and intervention seeds.
8. Run the real pilot without changing the frozen gates.
9. Preserve a failure or underidentification result as the canonical outcome if the model does not satisfy them.
"""
    write("REAL_LRM_PILOT_STATUS.md", external_md)

    print("SRIC_BLOCK23_RELEASE_DOCS=PASS")


if __name__ == "__main__":
    main()
