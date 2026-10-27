# Stratified Relational Workspace Theory integration

This KM36 distribution includes **Stratified Relational Workspace Theory
(SRWT) 1.0.0** as a separate companion research repository.

The complete companion is located at:

```text
stratified-relational-workspace-theory/
```

It contains the 209-page monograph *Stratified Relational Workspace Theory: A
Core-Transfer Framework for Distributed Cognition, Collaboration, and
Epistemic Systems*, its modular and frozen monolithic LaTeX sources,
deterministic mathematical regression suites, theorem and priority indexes,
GitHub workflows, citation metadata, review guidance, and release tooling.

## Why it belongs beside Komorebi Math

SRWT studies when heterogeneous components support a persistent shared
workspace rather than replicated storage, centralized control, or mere
correlation. Its structural layer uses many objects already native to the
Komorebi program: local state spaces, transfer maps, exact and approximate
shared cores, holonomy, transfer Laplacians, gauge changes, reconstruction
frames, coarse-graining, gluing, residuals, and finite certification gates.

The integration is therefore a **typed companion relationship**, not an API
merge and not an assertion that a cognitive workspace is identical to every
resolved mathematical object.

| SRWT concept | Closest Komorebi realization or theory layer | Boundary |
|---|---|---|
| heterogeneous local state spaces | resolved sorts, packet systems, and realization strata | a local state space is not automatically a normalized Komorebi stratum |
| local access and transfer maps | `PacketMorphism`, `PacketOperator`, `TransferGraph`, analysis-synthesis maps | semantic and causal interpretations remain application-specific |
| exact shared core | compatible global sections, holonomy-fixed cores, equalizer-style consistency | existence of a structural core does not establish operational efficacy |
| approximate workspace | transfer Laplacian, spectral near-kernel, leakage and stability diagnostics | numerical near-consistency is not exact descent |
| gauge-invariant identity | representation groupoids and finite gauge transport | coordinate invariance does not determine personhood or consciousness |
| coalition reconstruction | `AnalysisSynthesisSystem`, frame operators, recovery certificates | coalition sufficiency depends on the declared observation model |
| gluing and workspaces of workspaces | finite holonomy, atlas descent, refinement towers | structural gluing and causal gluing are distinct gates |
| coarse-graining robustness | packet refinement, coarsening, support transport, named residuals | coarse-graining may preserve a core while changing coalition counts |
| causal efficacy and reentry | dynamics and nonlinear modules plus SRWT intervention tests | no general causal certificate is inferred from static transfer alone |
| empirical certification | SRWT verification and matched-null protocols | the release is a theoretical framework, not an empirical certification of a real collaboration |

## Executable finite crosswalk

The file

```text
komorebi-math/examples/stratified_relational_workspace_crosswalk.py
```

uses the existing Komorebi Math API to verify two finite structural examples:

1. a two-dimensional abstract core distributed over three one-dimensional
   local observations, where no singleton is sufficient and every two-node
   coalition reconstructs the core; and
2. a three-chart transport triangle with trivial fundamental holonomy,
   invariance under gauge change, and a deliberately perturbed negative
   control detected as a gluing failure.

Run it from the KM36 root with:

```powershell
$env:PYTHONPATH = ".\komorebi-math\src"
python .\komorebi-math\examples\stratified_relational_workspace_crosswalk.py
```

This crosswalk concerns finite structural geometry only. It does not certify
causal efficacy, reentry, agency, self-maintenance, consciousness, personhood,
or moral status.

## Verification

From the extracted KM36 root:

```powershell
python .\VERIFY_RELATIONAL_WORKSPACE_INTEGRATION.py
```

For a clean-copy rebuild and full PDF audit of the companion repository:

```powershell
python .\VERIFY_RELATIONAL_WORKSPACE_INTEGRATION.py --strict
```

The strict option runs the companion's own `scripts/repo.py verify --strict`
in a temporary copy so that the integrated source tree remains byte-for-byte
identical to the user-supplied GitHub-ready repository.

## Primary entry points

- Companion README: `stratified-relational-workspace-theory/README.md`
- Canonical monograph: `stratified-relational-workspace-theory/monograph/Stratified_Relational_Workspace_Theory.pdf`
- Canonical modular source: `stratified-relational-workspace-theory/monograph/Stratified_Relational_Workspace_Theory.tex`
- Frozen monolithic source: `stratified-relational-workspace-theory/archive/v1.0.0/Stratified_Relational_Workspace_Theory_monolithic.tex`
- Statement index: `stratified-relational-workspace-theory/audits/statement_index.md`
- Priority register: `stratified-relational-workspace-theory/audits/priority_register.csv`
- Review guide: `stratified-relational-workspace-theory/docs/REVIEW_GUIDE.md`
- Komorebi Math crosswalk: `komorebi-math/docs/RELATIONAL_WORKSPACE_THEORY.md`

## API and license boundary

No file under `komorebi-math/src/komorebi_math/` is modified. The frozen
131-symbol stable Python namespace is unchanged. The `komorebi-stratified/`
and `polyphase-float/` trees are also preserved unchanged.

SRWT 1.0.0 is publicly readable but presently all rights reserved. Inclusion
inside KM36 does not merge its license with Komorebi Math, Komorebi Stratified,
or Polyphase Float. See `LICENSE_MAP.md`.

## Status boundary

The companion describes a formal theory and a falsifiable certification
architecture. Its repository labels the monograph a complete preprint with
external mathematical and empirical review pending. It does not infer
consciousness, personhood, moral status, or unrestricted autonomy from
structural coherence, agency, persistence, or self-maintenance.
