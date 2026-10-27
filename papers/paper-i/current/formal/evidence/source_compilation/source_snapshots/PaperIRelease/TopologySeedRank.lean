import PaperIRelease.TopologyTransport
import Mathlib.SetTheory.Cardinal.Basic

/-! # Cardinal-valued topological seed rank and its transport laws -/

noncomputable section
open Set Function Cardinal

namespace PaperIRelease.TopologyTransport

universe u v
variable {𝕜 : Type u} {X Y : Type v} [Ring 𝕜] [TopologicalSpace 𝕜]
variable [AddCommGroup X] [Module 𝕜 X] [TopologicalSpace X]
variable [AddCommGroup Y] [Module 𝕜 Y] [TopologicalSpace Y]
variable [ContinuousAdd X] [ContinuousSMul 𝕜 X]
variable [ContinuousAdd Y] [ContinuousSMul 𝕜 Y]

/-- A seed set generates topologically when its algebraic operator hull is dense. -/
def TopologicallyGenerates (A : Set (X →L[𝕜] X)) (S : Set X) : Prop :=
  (operatorHull A S).topologicalClosure = ⊤

/-- Minimum cardinality of a densely generating seed set. For an acting
unital algebra the infimum is attained, as proved below. -/
def topologicalSeedRank (A : Set (X →L[𝕜] X)) : Cardinal.{v} :=
  ⨅ (S : {S : Set X // TopologicallyGenerates A S}), #S.1

theorem generates_univ (A : Set (X →L[𝕜] X))
    (hA : ContinuousLinearMap.id 𝕜 X ∈ A) : TopologicallyGenerates A univ := by
  have h : operatorHull A univ = ⊤ := by
    apply top_unique
    intro x _
    exact Submodule.subset_span ⟨ContinuousLinearMap.id 𝕜 X, hA, x, mem_univ x, rfl⟩
  change (operatorHull A univ).topologicalClosure = ⊤
  rw [h]
  exact top_unique (Submodule.le_topologicalClosure ⊤)

theorem seedRank_le_card {A : Set (X →L[𝕜] X)} {S : Set X}
    (hS : TopologicallyGenerates A S) : topologicalSeedRank A ≤ #S :=
  ciInf_le' (fun T : {T : Set X // TopologicallyGenerates A T} ↦ #T.1) ⟨S, hS⟩

/-- The infimum used in the definition is a minimum, including the zero
space and infinite generating cardinals. -/
theorem exists_generating_set_card_eq_seedRank (A : Set (X →L[𝕜] X))
    (hA : ContinuousLinearMap.id 𝕜 X ∈ A) :
    ∃ S : Set X, TopologicallyGenerates A S ∧ #S = topologicalSeedRank A := by
  have hmem : topologicalSeedRank A ∈
      Set.range (fun S : {S : Set X // TopologicallyGenerates A S} ↦ #S.1) :=
    csInf_mem ⟨#(univ : Set X), ⟨⟨univ, generates_univ A hA⟩, rfl⟩⟩
  obtain ⟨S, hS⟩ := hmem
  exact ⟨S.1, S.2, hS⟩

theorem generates_mono_algebra {A B : Set (X →L[𝕜] X)} {S : Set X}
    (hAB : A ⊆ B) (hS : TopologicallyGenerates A S) :
    TopologicallyGenerates B S := by
  have hHull : operatorHull A S ≤ operatorHull B S := by
    apply Submodule.span_mono
    rintro x ⟨T, hT, s, hs, rfl⟩
    exact ⟨T, hAB hT, s, hs, rfl⟩
  apply top_unique
  rw [← hS]
  exact Submodule.topologicalClosure_mono hHull

/-- Enlarging the acting algebra cannot increase topological seed rank. -/
theorem seedRank_mono_algebra {A B : Set (X →L[𝕜] X)}
    (hA : ContinuousLinearMap.id 𝕜 X ∈ A) (hAB : A ⊆ B) :
    topologicalSeedRank B ≤ topologicalSeedRank A := by
  obtain ⟨S, hS, hcard⟩ := exists_generating_set_card_eq_seedRank A hA
  rw [← hcard]
  exact seedRank_le_card (generates_mono_algebra hAB hS)

/-- Surjective continuous intertwiners cannot increase topological seed
rank. This includes the closed invariant quotient with its induced action. -/
theorem seedRank_le_of_surjective
    (f : X →L[𝕜] Y) (hf : Surjective f)
    (φ : (X →L[𝕜] X) → (Y →L[𝕜] Y))
    (A : Set (X →L[𝕜] X)) (B : Set (Y →L[𝕜] Y))
    (hA : ContinuousLinearMap.id 𝕜 X ∈ A) (hφ : ∀ T ∈ A, φ T ∈ B)
    (hintertwine : ∀ T ∈ A, f.comp T = (φ T).comp f) :
    topologicalSeedRank B ≤ topologicalSeedRank A := by
  obtain ⟨S, hS, hcard⟩ := exists_generating_set_card_eq_seedRank A hA
  calc
    topologicalSeedRank B ≤ #(f '' S) :=
      seedRank_le_card (dense_operatorHull_image f hf φ A B S hφ hintertwine hS)
    _ ≤ #S := Cardinal.mk_image_le
    _ = topologicalSeedRank A := hcard

/-- A topological linear isomorphism intertwining both action families
preserves the full cardinal-valued topological seed rank. -/
theorem seedRank_equiv
    (e : X ≃L[𝕜] Y)
    (φ : (X →L[𝕜] X) → (Y →L[𝕜] Y))
    (ψ : (Y →L[𝕜] Y) → (X →L[𝕜] X))
    (A : Set (X →L[𝕜] X)) (B : Set (Y →L[𝕜] Y))
    (hA : ContinuousLinearMap.id 𝕜 X ∈ A) (hB : ContinuousLinearMap.id 𝕜 Y ∈ B)
    (hφ : ∀ T ∈ A, φ T ∈ B) (hψ : ∀ T ∈ B, ψ T ∈ A)
    (hforward : ∀ T ∈ A, e.toContinuousLinearMap.comp T = (φ T).comp e.toContinuousLinearMap)
    (hbackward : ∀ T ∈ B, e.symm.toContinuousLinearMap.comp T = (ψ T).comp e.symm.toContinuousLinearMap) :
    topologicalSeedRank A = topologicalSeedRank B := by
  apply le_antisymm
  · exact seedRank_le_of_surjective e.symm.toContinuousLinearMap e.symm.surjective ψ B A hB hψ hbackward
  · exact seedRank_le_of_surjective e.toContinuousLinearMap e.surjective φ A B hA hφ hforward

end PaperIRelease.TopologyTransport
