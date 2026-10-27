# Upstream integration audit

This package was designed after a read-only audit of the latest available
Komorebi research artifacts. It does not silently equate their claims.

| Source | What it already supplies | G1 use | Explicitly deferred |
| --- | --- | --- | --- |
| RRCT v0.61 multispace convergence | Frozen-model geometry estimators, null patterns, layer discovery, protocol discipline | Invocation-aware layer selection and claim-boundary patterns | RRCT spaces do not define or train this recurrent workspace |
| OSL Discovery Bridge v0.1.0 | Exact finite-world execution, equivalence, counterexamples, certificate replay | Reserved as a held-out semantic oracle after G1 is frozen | OSL labels and outcomes cannot select G1 layers, directions, rank, or gates |
| OSL HF causal v0.2.1 hotfix | Synthetic traces, structural split ideas, auxiliary objectives, causal diagnostics | Leakage-audit and late-binding design lessons | Its supervised one-step transition is not treated as inference recurrence |
| Arithmetic J-Space Training Lab v0.4.0 | Deterministic online data, matched interventions, resume and assay patterns | Shared-state, counterfactual-control, and exact-resume patterns | Its tiny decoder and arithmetic target are not imported as evidence for Qwen G1 |

No upstream behavioral label, answer, OSL state, operator identity, lens vector,
or success result is used to fit the G1 workspace. The only trained parameters
are the newly initialized workspace parameters in this package.

The clean later interface is one-way: freeze G1 first, then use held-out OSL
traces and exact state/equivalence oracles to test whether its latent dynamics
carry compositional semantics.
