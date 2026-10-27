# RRCT v0.28.0.dev1 handoff

## Authoritative result

v0.28 fills the intervention-provenance gap identified by v0.27. The learner is
no longer given the exact executed private perturbation. It receives four
anonymous prospective handle commitments, six anonymous 8-D process streams,
and mixed sensory transitions. It must discover one replicated handle×source
interaction and the paired internal/sensory rank without labels or projectors.

Frozen untouched seeds 5401, 5407, 5413, and 5419 pass all 19 primary gates.
Every seed recovers the exact hidden pair and rank two. See:

- `validation/V0_28_DEVELOPMENT_PROTOCOL.md`
- `validation/V0_28_PREOUTCOME_FREEZE.json`
- `validation/v0.28_intervention_provenance_development/intervention_provenance_summary.json`
- `validation/V0_28_DEVELOPMENT_NOTES.md`
- `validation/V0_28_POSTOUTCOME_VERIFICATION.json`

## Verification snapshot

- 258 tests passed, 2 skipped, 89 parametrized subtests passed.
- Deterministic CLI verification passed at `0.28.0.dev1`.
- 97 frozen files audited after outcomes with zero mismatches.
- Four aggregate artifacts audited with zero mismatches.
- Frozen v0.26 remains preserved as a failure.

## Reproduce local verification

POSIX:

```bash
python -m pip install -e .
python -m rrct.cli verify
python -m pytest -q -W error
```

PowerShell:

```powershell
py -m pip install -e .
py -m rrct.cli verify
py -m pytest -q -W error
```

The official result directories are immutable evidence. Do not rerun official
commands into existing `validation/v0.28_seed_parts/` or
`validation/v0.28_intervention_provenance_development/` directories.

## Claim boundary

This is a bounded functional causal-authorship result. It retains
harness-generated prospective commitments, and the discovered batch model is
not installed inside `RRCTAgent`. It does not establish phenomenal
consciousness, subjective awareness, sentience, valence, suffering, autonomy,
or moral status.

## Next major gap

Integrate the discovered provenance/boundary state into the live agent as an
online, globally available, persistent-but-revisable self-model. Secretly switch
or disconnect routes midstream and require the agent to revise its boundary for
successful memory, prediction, and control. Frozen-boundary, no-broadcast,
deranged-update, and replay controls should fail selectively.
