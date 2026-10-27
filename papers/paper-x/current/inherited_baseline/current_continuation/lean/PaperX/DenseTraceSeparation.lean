import PaperX.FiniteSeparation
import Mathlib.RepresentationTheory.Character
import Mathlib.Topology.Algebra.Module.Basic
import Mathlib.Tactic.FunProp

/-! Density and conjugacy input for finite trace separation.
Density of arithmetic Frobenius classes and character independence for general
Galois representations are hypotheses, not axioms or asserted new results. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.DenseTraceSeparation

open scoped BigOperators
open PaperX.FiniteSeparation
universe u v w z
variable {K : Type u} [Field K] [TopologicalSpace K] [IsTopologicalRing K] [T2Space K]
variable {I : Type v} [Fintype I] {G : Type w} [TopologicalSpace G] {X : Type z}

/-- Restriction along a dense map preserves independence of continuous functions. -/
theorem independent_dense_restriction (f : I → G → K)
    (hc : ∀ i, Continuous (f i)) (hi : LinearIndependent K f)
    (s : X → G) (hd : DenseRange s) :
    LinearIndependent K (fun i => f i ∘ s) := by
  rw [Fintype.linearIndependent_iff]
  intro c hzero
  apply (Fintype.linearIndependent_iff.mp hi) c
  have hcont : Continuous (fun g => ∑ i, c i * f i g) := by fun_prop
  have heq : (fun g => ∑ i, c i * f i g) = (fun _ => (0 : K)) := by
    apply hd.equalizer hcont continuous_const
    funext x
    simpa [Function.comp_def] using congrFun hzero x
  funext g
  simpa using congrFun heq g

/-- Only the conjugacy saturation must be dense. Chosen representatives themselves
need not be a dense subset of a noncommutative group. -/
theorem independent_conjugacy_samples [Group G] (f : I → G → K)
    (hc : ∀ i, Continuous (f i)) (hi : LinearIndependent K f)
    (s : X → G)
    (hd : DenseRange (fun p : X × G => p.2 * s p.1 * p.2⁻¹))
    (hconj : ∀ i g x, f i (g * s x * g⁻¹) = f i (s x)) :
    LinearIndependent K (fun i x => f i (s x)) := by
  rw [Fintype.linearIndependent_iff]
  intro c hzero
  apply (Fintype.linearIndependent_iff.mp hi) c
  have hcont : Continuous (fun g => ∑ i, c i * f i g) := by fun_prop
  have heq : (fun g => ∑ i, c i * f i g) = (fun _ => (0 : K)) := by
    apply hd.equalizer hcont continuous_const
    funext p
    simpa [Function.comp_def, hconj] using congrFun hzero p.1
  funext g
  simpa using congrFun heq g

/-- The exact finite conclusion under explicit topological and character inputs. -/
theorem finite_conjugacy_separator [Group G] [DecidableEq I]
    (f : I → G → K) (hc : ∀ i, Continuous (f i)) (hi : LinearIndependent K f)
    (s : X → G)
    (hd : DenseRange (fun p : X × G => p.2 * s p.1 * p.2⁻¹))
    (hconj : ∀ i g x, f i (g * s x * g⁻¹) = f i (s x)) :
    ∃ v : I → X, Function.Injective v ∧
      (sampleMatrix (fun i x => f i (s x)) v).det ≠ 0 :=
  exists_nonsingular_samples _ (independent_conjugacy_samples f hc hi s hd hconj)

/-- Specialization to actual representation characters, with varying finite dimensions.
Character invariance under conjugation is proved by Mathlib, not assumed. -/
theorem representation_trace_separator [Group G] [DecidableEq I]
    (n : I → ℕ) (ρ : ∀ i, Representation K G (Fin (n i) → K))
    (hc : ∀ i, Continuous (ρ i).character)
    (hi : LinearIndependent K (fun i => (ρ i).character))
    (s : X → G)
    (hd : DenseRange (fun p : X × G => p.2 * s p.1 * p.2⁻¹)) :
    ∃ v : I → X, Function.Injective v ∧
      (sampleMatrix (fun i x => (ρ i).character (s x)) v).det ≠ 0 := by
  apply finite_conjugacy_separator _ hc hi s hd
  intro i g x
  exact (ρ i).char_conj (s x) g

end PaperX.DenseTraceSeparation
