# Continue from v0.7.0

This archive is the authoritative source. All 20 v0.6.0 mathematical modules are retained unchanged.

## Completed

Do not reconstruct the guard, sentence, set coding or first-order ZFC base theory. The entire explicit ZFC theory is now present, with all finite-parameter Separation and Replacement instances, and `zfset_models_zfc` proves its modelhood in concrete ZFSet. The actual KZFC theory is this explicit base plus Theta.

`guardedSentence_iff_internal_model` decodes Theta internally in every membership structure. `model_kzfc_iff_internal` combines the exact base-axiom semantics and this internal reading. It makes no external-cardinality claims.

`zfset_models_kzfc_iff_residual` and `zfset_models_kzfc_iff_filterExtension` have no remaining unspecified-base-model premise.

## Remaining substantive obligation

Encode the semantic constraint class itself as internal sets and set-coded function assignments, with scope/domain bounds interpreted via internal injection graphs. Prove the compactness/filter-extension comparison using the explicit axioms in arbitrary models, or extract a proof in a specified first-order proof calculus. The currently proved decoding identities are not that full mathematical comparison.

Do not strengthen AxiomSemantics with a desired comparison theorem. Do not replace internally coded assignments by all external functions from an internal domain. Do not claim that the model's powerset or kappa-completeness agrees with an external one.

The existing generic layer provides internal Pairing/Foundation and Separation examples. Use the source-specific schema instantiation methods and track exactly which axioms discharge each existence construction.

## Verification

Use REPRODUCE.md. The staged verifier runs short synchronous batches under one unchanged input snapshot. There are 59 compiler commands in v0.7.0, followed by final audit checks. Start once, repeat next until all commands are recorded, finish, regenerate the manifest and validate. Historical interrupted builds and previous verdicts do not establish a current PASS.
