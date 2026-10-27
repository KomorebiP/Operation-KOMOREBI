import PaperX.CompletionAssembly

/-! Source-faithful quantifiers for every required packet. Carriers and local
closure are supplied. Completion never forces their independent occupancy. -/
set_option autoImplicit false
namespace PaperX.IndexedExistenceBoundary
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationForests
open PaperX.SystemCompletion PaperX.CompletionAssembly PaperX.JointOccupancy

variable {Λ G ι P : Type} [Group G] [TopologicalSpace G] [Fintype ι] [DecidableEq ι]
variable (O : Λ → Type) [∀ l, CommRing (O l)] (I : (l : Λ) → Ideal (O l))
variable [∀ l, IsAdicComplete (I l) (O l)]
variable (C : (l : Λ) → Conditions (G := G) (ι := ι) (I l))
variable (finite : ∀ l k, Finite {ρ : MatrixRep (O l ⧸ (I l)^k) G ι // (C l).allowed k ρ})
variable (continuous : ∀ l k ρ, (C l).allowed k ρ → FiniteRepContinuous ρ)
variable (Local : (l : Λ) → MatrixRep (O l) G ι → Prop)
variable (stable : ∀ l ρ, Realizes (I l) (C l) ρ → Local l ρ)
variable (K V J : P → Type) [∀ p, Field (K p)] [∀ p, CharZero (K p)]
variable [∀ p, AddCommGroup (V p)] [∀ p, Module (K p) (V p)]
variable [∀ p, FiniteDimensional (K p) (V p)]
variable (T : (p : P) → J p → Module.End (K p) (V p))
variable (a : (p : P) → J p → K p) (indices : (p : P) → List (J p))
variable (hs : ∀ p j, PaperX.SpectralProjectors.Split (T p j))
variable (hc : ∀ p i j, Commute (T p i) (T p j))

include finite continuous stable hs hc in
/-- Residual companions, every higher depth, and every supplied required packet
are separate and jointly necessary/sufficient under the stated closure input. -/
theorem all_required_packets_iff :
    (∃ ρ : (l : Λ) → MatrixRep (O l) G ι,
      SystemRealizes O I C ρ ∧
      (∀ l, AdicRepContinuous (I l) (ρ l) ∧ Local l (ρ l)) ∧
      ∀ p, Occupied (T p) (a p) (indices p)) ↔
    (∀ l, ∃ τ, (C l).allowed 1 τ) ∧
    (∀ l k, 2 ≤ k → ∃ τ, (C l).allowed k τ) ∧
    ∀ p, LinearMap.trace (K p) (V p) (joint (T p) (a p) (indices p)) ≠ 0 := by
  constructor
  · rintro ⟨ρ, hρ, _, hp⟩
    refine ⟨fun l => ⟨reduce (I l) (ρ l) 1, hρ l 1⟩,
      fun l k _ => ⟨reduce (I l) (ρ l) k, hρ l k⟩, ?_⟩
    intro p
    exact (occupied_iff_trace_ne_zero (T p) (a p) (hs p) (hc p) (indices p)).mp (hp p)
  · rintro ⟨h1, hh, hp⟩
    have hall : ∀ l k, ∃ τ, (C l).allowed k τ := fun l =>
      (residual_and_higher_iff_all (I l) (C l)).mp ⟨h1 l, hh l⟩
    obtain ⟨ρ, hρ, hl⟩ := continuous_system_completion O I C finite hall continuous Local stable
    refine ⟨ρ, hρ, hl, ?_⟩
    intro p
    exact (occupied_iff_trace_ne_zero (T p) (a p) (hs p) (hc p) (indices p)).mpr (hp p)

end PaperX.IndexedExistenceBoundary
