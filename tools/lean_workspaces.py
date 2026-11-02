"""Prepared browser workspaces, restricted to retained reading-edition sources."""
from pathlib import Path
from lean_runner import EXTERNAL_ROOTS, imports, safe_path

RESIDUAL='papers/paper-x/current/current_continuation/lean/PaperX/Residual.lean'
COMPRESSION='monographs/proof-path-theory/formal/ProofPath/Compression.lean'
RECOVERY='monographs/proof-path-theory/formal/ProofPath/Recovery.lean'
COMPAT_SOURCE='''-- Browser compatibility: Lean 4.33 calls this lemma dif_pos.
-- Checked by Lean alongside Recovery; this is not retained paper source.
universe u
theorem dite_eq_left {α : Sort u} {p : Prop} [Decidable p]
    {t : p → α} {e : ¬ p → α} (h : p) : dite p t e = t h := by
  exact dif_pos h
'''
WORKSPACES=[
    ('paper-x-residual','Paper X · Residual partition','paper-x', [('PaperX.Residual',RESIDUAL)]),
    ('proof-path-compression','Proof Path Theory · Compression','proof-path-theory', [('ProofPath.Compression',COMPRESSION)]),
    ('proof-path-recovery','Proof Path Theory · Recovery with its local import','proof-path-theory', [('ProofPath.Compression',COMPRESSION),('ProofPath.Recovery',RECOVERY)]),
    ('paper-ii-linear-defects','Paper II · Linear defects','paper-ii', [('PaperII.LinearDefects','papers/paper-ii/current/formal/current/KomorebiVerification/PaperII/LinearDefects.lean')]),
    ('paper-iii-coordinate-naturality','Paper III · Coordinate naturality','paper-iii', [('KomorebiPaperIII.CoordinateNaturality','papers/paper-iii/current/formal/KomorebiPaperIII/CoordinateNaturality.lean')]),
    ('paper-iii-packet-coordinates','Paper III · Packet coordinates','paper-iii', [('KomorebiPaperIII.PacketCoordinates','papers/paper-iii/current/formal/KomorebiPaperIII/PacketCoordinates.lean')]),
    ('paper-vii-tensor-refinement','Paper VII · Tensor refinement','paper-vii', [('TensorRefinement','papers/paper-vii/current/source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot/formalization/TensorRefinement.lean')]),
    ('paper-ix-residue-digits','Paper IX · Retained residue lifting','paper-ix', [('ResidueLiftDigits','papers/paper-ix/current/preserved/PRSC_IX_Consolidated_Manuscript/polynomial_counts/formalization/ResidueLiftDigits.lean')]),
    ('paper-x-compactness','Paper X · Compactness','paper-x', [('PaperX.Compactness','papers/paper-x/current/current_continuation/lean/PaperX/Compactness.lean')]),
    ('paper-x-idempotent-newton','Paper X · Idempotent Newton step','paper-x', [('PaperX.IdempotentNewton','papers/paper-x/current/current_continuation/lean/PaperX/IdempotentNewton.lean')]),
    ('paper-xi-heisenberg','Paper XI · Heisenberg form','paper-xi', [('PaperXI.HeisenbergForm','papers/paper-xi/current/formalization/PaperXI/HeisenbergForm.lean')]),
    ('paper-xi-one-plus-index','Paper XI · One-plus index','paper-xi', [('PaperXI.OnePlusIndex110','papers/paper-xi/current/formalization/PaperXI/OnePlusIndex110.lean')]),
    ('paper-xii-compactness','Paper XII · Retained compactness module','paper-xii', [('PaperXII.ReuseCompactness','papers/paper-xii/current/core/publication/source/lean_guide/formal_release/lean/PaperXII/ReuseCompactness.lean')]),
    ('komorebi-space-projective','Komorebi Space · Projective example','komorebi-space', [('KomorebiSpace.ProjectiveExample','monographs/komorebi-space/lean/KomorebiSpace/ProjectiveExample.lean')]),
    ('komorebi-space-correction','Komorebi Space · Correction','komorebi-space', [('KomorebiSpace.Correction','monographs/komorebi-space/lean/KomorebiSpace/Correction.lean')]),
    ('komorebi-space-cohomology','Komorebi Space · Cohomology','komorebi-space', [('KomorebiSpace.Cohomology','monographs/komorebi-space/lean/KomorebiSpace/Cohomology.lean')]),
]


def mathlib_seeds(root,workspaces=None):
    """Use the same source registry for runtime imports and the public picker."""
    seeds=set();ids=set()
    for key,_,_,files in WORKSPACES if workspaces is None else workspaces:
        if key in ids:raise ValueError('Duplicate browser workspace: '+key)
        ids.add(key);available=set()
        for module,path in files:
            safe_path(path)
            if module in available:raise ValueError('Duplicate project module: '+module)
            for name in imports((Path(root)/path).read_text(encoding='utf-8-sig')):
                if name.startswith('Mathlib.'):seeds.add(name)
                elif name.split('.')[0] not in EXTERNAL_ROOTS and name not in available:
                    raise ValueError('Project import must precede its dependent: '+name)
            available.add(module)
    return sorted(seeds)


def mathlib_seed_groups(root):
    return {workspace[0]:seeds for workspace in WORKSPACES
            if (seeds:=mathlib_seeds(root,[workspace]))}
