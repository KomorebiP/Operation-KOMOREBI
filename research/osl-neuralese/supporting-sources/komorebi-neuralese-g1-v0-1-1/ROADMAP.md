# From G1 toward an Astra-class system

“Astra-class” is treated here as an engineering target: a system with durable
latent state, compositional reasoning, grounded planning, reliable memory,
bounded tool use, calibrated uncertainty, and strong safety controls. It is not
a consciousness claim.

| Gate | Decisive question | Evidence required | Current status |
| --- | --- | --- | --- |
| G1 — recurrent workspace | Does model-mediated latent feedback carry causally useful reusable state? | Frozen-backbone training, late-binding queries, no-injection/shuffle/no-feedback interventions, held-out and replicated gates | Implemented here; target-machine execution pending |
| G2 — architecture value | Does recurrence outperform an independently trained, parameter- and compute-matched non-feedback architecture? | Paired initializations, learning curves, uncertainty intervals, depth and layer holdouts | Needed after G1 feedback-use evidence |
| G3 — semantic grounding | Does the frozen state track exact OSL transitions and equivalence classes without label-guided space selection? | Held-out OSL oracle, counterexamples, path equivalence, intervention transfer | Machinery exists upstream; integration deliberately deferred |
| G4 — compositional Neuralese | Are reusable latent operators sparse, bindable, transportable, and more predictive than nuisance-matched null spaces? | RRCT/JLENS discovery freeze, causal patch/rescue, novel compositions | Partial measurement machinery exists; learned operators not established |
| G5 — planning and memory | Can the system maintain goals, branch, recover, and use episodic/semantic memory in a closed sandbox? | Long-horizon task suite, provenance, rollback, adversarial evaluation | Needed |
| G6 — controlled agency | Can tools be used reliably under permissions, budgets, audit, and shutdown constraints? | Capability and safety cases, red-team results, containment tests | Needed |
| G7 — scale and robustness | Do results persist across models, domains, seeds, distribution shifts, and resource limits? | Multi-model replications and external review | Needed |

G1 comes first because every later Neuralese claim assumes that an internal
state can survive, update, and matter causally. If G1 fails, geometry alone is
not enough; the recurrent mechanism or task must be revised before OSL binding
or larger-scale agency work is justified.
