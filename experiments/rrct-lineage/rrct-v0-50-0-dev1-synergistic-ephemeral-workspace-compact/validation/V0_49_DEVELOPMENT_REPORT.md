# RRCT v0.49 Development Report

## Scope

This report records exposed development work before the frozen holdout.

Development seeds were `49001` and `49007`. Both separately initialized transformer dyads learned every shared and private task with exact accuracy 1.0.

## Principal development finding

The first candidate hypothesis failed at the early recurrent state `h1`.

Although the average report Jacobian had the expected centered rank four, its direct scores did not reliably recover the two task factors, the two agents' spaces aligned poorly, and removing the candidate component had little effect on final task performance.

This is treated as a negative result rather than a workspace success.

A qualitatively different representation appeared at the final decision state `h3`:

- report Jacobian rank four;
- perfect factor-report scores;
- cross-agent alignment R² approximately 0.98;
- selective report-space ablation;
- a broader rank-eight Jacobian-informed space that supported all shared tasks while largely excluding private roles;
- successful shared-state patching and one-step transmission between agents;
- reconstruction from persistent local evidence after another recurrent round.

## Important non-specificity result

A same-rank PCA basis performed essentially as well as the Jacobian-informed basis on the development seeds. The frozen holdout therefore includes PCA equivalence as a required endpoint rather than omitting the control.

The v0.49 result can establish a shared late residual-access manifold. It cannot, on this evidence, establish that the Jacobian lens uniquely identifies that manifold or that the state is a persistent distributed J-space.

## Development defects corrected

- The initial model was too large for the CPU execution window and was reduced before holdout selection.
- The first candidate analysis examined only the early recurrent state and failed. Stage scanning was added before freezing.
- The initial report-only space changed factor reports but did not reliably redirect flexible heads. The broader frozen rank-eight construction therefore uses all shared output-head Jacobian rows.
- A proposed persistent-patch interpretation was rejected after recurrent local evidence restored the original state.

No holdout model was trained before the protocol and thresholds were frozen.
