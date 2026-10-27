# OSL Discovery Bridge v0.1.0

The Discovery Bridge adds the missing bounded operator admission layer between an untrusted proposal and OSL-Core 0.3.

The newest canonical language release remains OSL v0.5 with OSL-Core 0.3. The later OSL Emergent Operator Geometry v0.6, Micro-Emergence v0.1.1, HuggingFace Causal v0.2.1, and Operand-Slot v0.3.1 packages are experimental lines. They do not supersede the language release. This package is a sidecar development toward OSL-Core 0.4.

## What changed

OSL-Core 0.3 can quarantine a neural proposal, but trusted origin and relevance attestations are enough to admit it. It does not independently determine whether a proposed operator is uniquely identified or whether its algebraic claims are true.

The bridge now performs six steps:

1. Validate a typed finite-world proposal, validate the source-digest format, and commit to that digest.
2. Enumerate every primitive program through a declared maximum depth.
3. Quotient programs by their exact transformation on every legal state.
4. Keep only transformation classes consistent with every demonstration.
5. Exhaustively test each claimed law and return a separating state when it fails.
6. Admit only a unique, nonidentity, nonprimitive derived transformation.

An admission certificate embeds the normalized proposal, is deterministic, and is content addressed. The registry replays the complete certificate before accepting it, then stores it in a hash-chained entry. An optional trusted tip detects suffix truncation. The adapter also requires a successful replay before rendering the decision as valid OSL-Core 0.3 source.

## Decisions

| Status | OSL decision | Meaning |
| --- | --- | --- |
| `ADMITTED` | admit | Exactly one bounded quotient class fits and every claimed law passes |
| `AMBIGUOUS` | quarantine | More than one class fits and a separating state is returned |
| `UNSATISFIABLE` | reject | No class fits or demonstrations contradict one another |
| `REJECTED_FALSE_LAW` | reject | The transformation is identified but a claimed law has a counterexample |
| `REJECTED_NONNOVEL` | reject | The proposal is equivalent to the identity or one existing primitive |

## Quick verification

```powershell
$Root="C:\path\to\OSL_Discovery_Bridge_v0.1.0"; Set-Location $Root; python verify_release.py
```

To include the cross-package interpreter replay, append `--osl-core C:\path\to\operator_symbolic_ai_language_paper_v0.5\reference`.

## Use the bridge

```powershell
$Root="C:\path\to\OSL_Discovery_Bridge_v0.1.0"; Set-Location $Root; python -m osl_discovery synthesize examples\flip_both_proposal.json generated\flip_both_certificate.json; python -m osl_discovery verify examples\flip_both_proposal.json generated\flip_both_certificate.json; python -m osl_discovery register generated\flip_both_certificate.json generated\OPERATOR_REGISTRY.jsonl; python -m osl_discovery emit-osl examples\flip_both_proposal.json generated\flip_both_certificate.json generated\flip_both_admission.osl
```

The positive example discovers `flip_both`. It collapses the equivalent spellings `flip_left; flip_right` and `flip_right; flip_left` into one transformation identifier, proves involution and commutation claims on all four legal algebra states, and emits an admission trace accepted by OSL-Core 0.3.

The partial example stays quarantined. The inconsistent example is rejected.

`python -m osl_discovery verify-registry generated\OPERATOR_REGISTRY.jsonl --expected-tip <trusted-tip>` checks both the replayable contents and an externally retained chain tip.

## Upstream Core boundary

The included adapter proves compatibility with the OSL-Core 0.3 interpreter, not the soundness of its independent receipt kernel. A read-only audit found that the v0.5 kernel accepts an empty, nonterminal trace and does not resolve an execution's capability digest back to a live matching grant. `CORE_0.3_AUDIT.md` records the concrete boundary and the recommended refinement target. Discovery certificates and registry admission do not rely on that kernel.

## Scientific boundary

This release establishes exact bounded synthesis and admission relative to the included finite worlds, primitive vocabulary, and declared depth. It does not establish that a neural model invented the operator internally. It does not prove open-world discovery, arbitrary-program correctness, universal noninterference, awareness, or consciousness.

Read `FORMAL_NOTES.md` for the finite guarantees, `UPSTREAM_AUDIT.md` for the experimental findings that motivated this bridge, and `CORE_0.3_AUDIT.md` for the upstream formal-runtime gap.
