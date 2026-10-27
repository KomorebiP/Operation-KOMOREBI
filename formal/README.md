# Formalizations and proof contracts

The collection includes Lean source projects with explicit statements, imports, assumptions, and reproduction instructions. Begin with the claim map and pinned environment in the component you want to use.

The [twelve core papers](../papers/README.md) link their current paper projects. [Komorebi Space and the companion volumes](../monographs/README.md) supply further developments, and the [research programs](../research/README.md) keep their finite formal statements alongside open obligations.

## A small starting point

[Research Preview 1](research-preview-1/README.md) develops prime-power Cartier systems. Its [claim map](research-preview-1/CLAIMS.md), [mathematical note](research-preview-1/THEOREM_NOTE.md), and [reproduction instructions](research-preview-1/REPRODUCE.md) describe the exact finite-precision contract.

## Interpret a formal claim

Inspect the formal statement and its hypotheses, imported facts, coefficient system, and admissible inputs. Identify which declarations were compiled in the recorded environment. A source-only or explicitly uncompiled development retains that status. Wider analytic, physical, arithmetic, or empirical claims require their own arguments and evidence.

Current projects and historical checkpoints can have different environments and entry points. Follow each project's documented build rather than flattening separate projects into one.

A successful file-integrity check identifies exact source bytes. Fresh Lean compilation is established by a separate, revision-specific proof replay record.

[Reading guide](../docs/START_HERE.md) · [Core papers](../papers/README.md) · [Component index](../docs/COMPONENT_INDEX.md)
