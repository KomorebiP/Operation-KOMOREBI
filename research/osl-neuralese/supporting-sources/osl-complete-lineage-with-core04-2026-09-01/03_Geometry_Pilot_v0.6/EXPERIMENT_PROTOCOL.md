# OSL Emergent Operator Geometry Pilot v0.6

## Question

Can repeated natural-language descriptions generated from an executable provenance algebra induce a transferable latent representation of that algebra in a small sequence model, without supplying the symbolic state directly?

## Matched training arms

1. **Answer only** receives sentence stories, natural-language questions, and final answers.
2. **State supervised** receives the same data plus auxiliary supervision for the complete agent-by-fact provenance state.
3. **Operator regularized** additionally receives pairs of surface-different stories whose operator paths yield the same formal state. Their latent representations are encouraged to agree.

All arms use the same architecture, vocabulary, optimizer family, training stories, validation stories, and frozen holdout stories.

## Hidden algebra

The finite world contains four agents, six facts, and four operations:

- `observe(a,f)` creates direct-observation provenance
- `tell(a,b,f)` transports accessible content while preserving its original source
- `imagine(a,f)` creates simulated provenance
- `infer(a,f)` creates inferred provenance

The precedence relation is:

```text
observed > communicated > inferred > simulated > none
```

This gives exact finite laws such as observation idempotence, simulation absorption by observation, and commutation of independent events.

## Training and holdout

Training stories contain one to three events. Holdouts include:

- same-length independently generated stories
- four-to-six-event unseen compositions
- held-out sentence templates using an already-seen vocabulary
- combined longer compositions and held-out syntax
- explicit multi-agent communication chains

The final holdout seeds are fixed in `CONFIG.json` and sealed before final model training and evaluation.

## Primary measurements

- answer accuracy on all holdout families
- class-balanced linear decodability of formal provenance state from the frozen story latent
- latent similarity for operator-equivalent story pairs
- accuracy of fitted affine latent transition maps on held-out transitions
- transition-map advantage over no-op and shuffled-operator controls

## Predeclared endpoints

- E01: all arms exceed a nontrivial in-distribution threshold
- E02: answer-only training shows nontrivial longer-composition generalization
- E03: answer-only latents contain linearly decodable formal status
- E04: explicit state supervision improves OOD state decodability
- E05: operator regularization improves path invariance over state supervision alone; the quotient loss is applied every fourth answer batch and includes a negative-pair anti-collapse term
- E06: fitted operator maps beat a no-op transition predictor in every arm
- E07: operator regularization improves long-chain answer accuracy over answer-only training
- E08: no result is represented as perfect open-ended emergence

## Claim boundary

This is a deterministic synthetic pilot using small GRU encoders. It can establish that a generated sentence environment creates pressure for provenance-sensitive latent structure and can compare how explicit scaffolding changes that structure. It cannot establish the same mechanism in frontier language models, universal symbol emergence, or a general AI-native language.

## Baseline controls

The final analysis also includes:

- a per-query-type majority baseline
- a TF-IDF word/bigram classifier with no recurrent state
- the executable symbolic oracle used only as an upper-bound integrity check

The endpoint thresholds are encoded in the sealed experiment source. The experiment may fail individual endpoints; failures are reported rather than repaired post-outcome.
