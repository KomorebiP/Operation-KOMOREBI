import KomorebiLSM.WeightedReconciliation
import Mathlib.Analysis.Normed.Module.Basic

/-! P21: reconcile in one object space and transport the norm through the actual
realizable subspace. Ambient redundant coordinates are not assumed valid. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.Reconciliation
universe u v w

structure LinearAtlas (X : Type u) (C : Type v)
    [AddCommGroup X] [Module ℝ X] [AddCommGroup C] [Module ℝ C] where
  analysis : X →ₗ[ℝ] C
  synthesis : C →ₗ[ℝ] X
  reconstruct : ∀ x, synthesis (analysis x)=x

namespace LinearAtlas
variable {X : Type u} [AddCommGroup X] [Module ℝ X]
variable {C : Type v} [AddCommGroup C] [Module ℝ C]
variable {D : Type w} [AddCommGroup D] [Module ℝ D]

abbrev Coeff (a : LinearAtlas X C) := LinearMap.range a.analysis

def encode (a : LinearAtlas X C) : X →ₗ[ℝ] a.Coeff := a.analysis.rangeRestrict

def decode (a : LinearAtlas X C) : a.Coeff →ₗ[ℝ] X := a.synthesis.domRestrict a.analysis.range

@[simp] theorem decode_encode (a : LinearAtlas X C) (x : X) : a.decode (a.encode x)=x :=
  a.reconstruct x

@[simp] theorem encode_decode (a : LinearAtlas X C) (c : a.Coeff) : a.encode (a.decode c)=c := by
  apply Subtype.ext
  obtain ⟨x,hx⟩ := c.property
  change a.analysis (a.synthesis c.val)=c.val
  rw [← hx,a.reconstruct]

theorem decode_injective (a : LinearAtlas X C) : Function.Injective a.decode := by
  intro x y h
  have h' := congrArg a.encode h
  simpa only [encode_decode] using h'

theorem decode_surjective (a : LinearAtlas X C) : Function.Surjective a.decode := by
  intro x
  exact ⟨a.encode x,a.decode_encode x⟩

def transport (a : LinearAtlas X C) (b : LinearAtlas X D) : a.Coeff →ₗ[ℝ] b.Coeff :=
  b.encode.comp a.decode

@[simp] theorem decode_transport (a : LinearAtlas X C) (b : LinearAtlas X D) (c : a.Coeff) :
    b.decode (a.transport b c)=a.decode c := b.decode_encode (a.decode c)

/-- The repaired output lies in the realizable subspace even for an arbitrary
ambient input. -/
def repaired (a : LinearAtlas X C) (L : X →ₗ[ℝ] X) : C →ₗ[ℝ] C :=
  a.analysis.comp (L.comp a.synthesis)

theorem repaired_consistent (a : LinearAtlas X C) (L : X →ₗ[ℝ] X) (c : C) :
    a.repaired L c ∈ a.analysis.range := ⟨L (a.synthesis c), rfl⟩

theorem repaired_intertwines (a : LinearAtlas X C) (b : LinearAtlas X D)
    (L : X →ₗ[ℝ] X) (c : C) :
    b.repaired L (b.analysis (a.synthesis c)) = b.analysis (a.synthesis (a.repaired L c)) := by
  simp only [repaired, LinearMap.comp_apply, a.reconstruct, b.reconstruct]

def objectFit (a : LinearAtlas X C) (G : C →ₗ[ℝ] C) : X →ₗ[ℝ] X :=
  a.synthesis.comp (G.comp a.analysis)

end LinearAtlas

section Norms
variable {X : Type u} [NormedAddCommGroup X] [NormedSpace ℝ X]
variable {C : Type v} [AddCommGroup C] [Module ℝ C]
variable {D : Type w} [AddCommGroup D] [Module ℝ D]

/-- This constructs a genuine normed additive group, not just a displayed formula. -/
noncomputable def LinearAtlas.coeffNormed (a : LinearAtlas X C) : NormedAddCommGroup a.Coeff :=
  NormedAddCommGroup.induced _ X a.decode a.decode_injective

noncomputable def LinearAtlas.coeffNormedSpace (a : LinearAtlas X C) :
    letI := a.coeffNormed
    NormedSpace ℝ a.Coeff := by
  letI := a.coeffNormed
  exact NormedSpace.induced ℝ a.Coeff X a.decode

theorem LinearAtlas.pullback_norm (a : LinearAtlas X C) (c : a.Coeff) :
    letI := a.coeffNormed
    ‖c‖=‖a.synthesis c.val‖ := rfl

theorem LinearAtlas.transport_isometry (a : LinearAtlas X C) (b : LinearAtlas X D) :
    letI := a.coeffNormed
    letI := b.coeffNormed
    Isometry (a.transport b) := by
  letI := a.coeffNormed
  letI := b.coeffNormed
  apply Isometry.of_dist_eq
  intro c d
  change dist (b.decode (a.transport b c)) (b.decode (a.transport b d)) = dist (a.decode c) (a.decode d)
  rw [a.decode_transport b, a.decode_transport b]

/-- Every Lipschitz constant is preserved in both directions. This states
coordinate equality of induced Lipschitz bounds, not merely one inequality. -/
theorem LinearAtlas.represented_lipschitz_iff (a : LinearAtlas X C) (b : LinearAtlas X D)
    (L : X → X) (K : NNReal) :
    letI := a.coeffNormed
    letI := b.coeffNormed
    LipschitzWith K (fun c : a.Coeff => b.encode (L (a.decode c))) ↔ LipschitzWith K L := by
  letI := a.coeffNormed
  letI := b.coeffNormed
  constructor
  · intro h
    apply LipschitzWith.of_dist_le_mul
    intro x y
    have hb := h.dist_le_mul (a.encode x) (a.encode y)
    change dist (b.decode (b.encode (L (a.decode (a.encode x)))))
      (b.decode (b.encode (L (a.decode (a.encode y))))) ≤
      (K:ℝ)*dist (a.decode (a.encode x)) (a.decode (a.encode y)) at hb
    simpa only [LinearAtlas.decode_encode] using hb
  · intro h
    apply LipschitzWith.of_dist_le_mul
    intro c d
    change dist (b.decode (b.encode (L (a.decode c)))) (b.decode (b.encode (L (a.decode d)))) ≤
      (K:ℝ)*dist (a.decode c) (a.decode d)
    simpa only [LinearAtlas.decode_encode] using h.dist_le_mul (a.decode c) (a.decode d)

end Norms

section Family
variable {X : Type u} [AddCommGroup X] [Module ℝ X]
variable {I : Type*} [Fintype I] {C : I → Type v}
variable [∀ i, AddCommGroup (C i)] [∀ i, Module ℝ (C i)]

noncomputable def reconciledOperator (atlas : (i : I) → LinearAtlas X (C i))
    (G : (i : I) → C i →ₗ[ℝ] C i) (w : I → ℝ) : X →ₗ[ℝ] X :=
  weightedMean w (fun i => (atlas i).objectFit (G i))

theorem coherent_reconciled_family (atlas : (i : I) → LinearAtlas X (C i))
    (G : (i : I) → C i →ₗ[ℝ] C i) (w : I → ℝ) (i j : I) (c : C i) :
    (atlas j).repaired (reconciledOperator atlas G w) ((atlas j).analysis ((atlas i).synthesis c)) =
      (atlas j).analysis ((atlas i).synthesis ((atlas i).repaired (reconciledOperator atlas G w) c)) :=
  (atlas i).repaired_intertwines (atlas j) (reconciledOperator atlas G w) c

end Family

section CoordinateObjective
variable {X : Type*} [AddCommGroup X] [Module ℝ X]
variable {I J : Type*} [Fintype I] [Fintype J]

/-- A finite matrix coordinate equivalence transports the Frobenius objective
back to actual linear operators. An orthonormal basis supplies the usual
Hilbert-space Frobenius interpretation. -/
theorem operator_frobenius_variance
    (coord : (X →ₗ[ℝ] X) ≃ₗ[ℝ] Matrix J J ℝ) (L : I → X →ₗ[ℝ] X)
    (w : I → ℝ) (total : ∑ i, w i=1) (M : X →ₗ[ℝ] X) :
    frobeniusCost w (fun i => coord (L i)) (coord M) =
      frobeniusSq (coord (M-weightedMean w L))+
      frobeniusCost w (fun i => coord (L i)) (coord (weightedMean w L)) := by
  have hmean : coord (weightedMean w L)=weightedMean w (fun i => coord (L i)) := by
    simp only [weightedMean,map_sum,map_smul]
  rw [map_sub,hmean]
  exact frobenius_variance_identity w (fun i => coord (L i)) total (coord M)

theorem operator_unique_frobenius_minimizer
    (coord : (X →ₗ[ℝ] X) ≃ₗ[ℝ] Matrix J J ℝ) (L : I → X →ₗ[ℝ] X)
    (w : I → ℝ) (total : ∑ i, w i=1) :
    ∃! M : X →ₗ[ℝ] X, ∀ N,
      frobeniusCost w (fun i => coord (L i)) (coord M) ≤
      frobeniusCost w (fun i => coord (L i)) (coord N) := by
  have hmin : ∀ N,
      frobeniusCost w (fun i => coord (L i)) (coord (weightedMean w L)) ≤
      frobeniusCost w (fun i => coord (L i)) (coord N) := by
    intro N
    rw [operator_frobenius_variance coord L w total N]
    exact le_add_of_nonneg_left (frobeniusSq_nonneg _)
  refine ⟨weightedMean w L,hmin,?_⟩
  intro M hM
  have h := hM (weightedMean w L)
  rw [operator_frobenius_variance coord L w total M] at h
  have hz : frobeniusSq (coord (M-weightedMean w L))=0 := by
    linarith [frobeniusSq_nonneg (coord (M-weightedMean w L))]
  have hc := (frobeniusSq_eq_zero_iff _).mp hz
  apply sub_eq_zero.mp
  apply coord.injective
  simpa using hc

end CoordinateObjective
end Komorebi.LSM.Reconciliation
