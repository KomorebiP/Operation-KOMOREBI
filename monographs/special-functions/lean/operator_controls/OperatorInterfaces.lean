import CoupledOperator
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (c : Fin 2 → ℂ) (hc : c ≠ 0) :
    (∃ H : (ℂ → ℂ) → (ℂ → ℂ), ∀ X : EntireInput,
      s.entireField c X = H (entireProjection c X)) ↔
    s.q = s.a ∧ s.r = s.b ∧ ∃ γ : ℂ, γ ≠ 0 ∧ c = ![γ,-γ] := by
  rw [← s.autonomous_iff_scalar_functional c, s.autonomous_nonzero_classification hs c hc]

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (c : Fin 2 → ℂ) (hc : c ≠ 0) :
    (∃ H : ScalarGerm → ScalarGerm, ∀ X : LocalInput,
      s.localField c X = H (localProjection c X)) ↔
    s.q = s.a ∧ s.r = s.b ∧ ∃ γ : ℂ, γ ≠ 0 ∧ c = ![γ,-γ] := by
  rw [← s.germ_autonomous_iff_scalar_functional c, s.germ_autonomous_nonzero_classification hs c hc]

example : halfScales.GermAutonomous ![1,-1] :=
  (halfScales.germ_autonomous_iff_entire halfScales_positive _).mpr
    (ordered_rows_autonomous _ _ rfl rfl (by simp))

example (u v : ℂ → ℂ) : halfScales.rowField ![1,-1] u v = 0 :=
  halfScales.ordered_rows_field_zero _ rfl rfl (by simp) u v

example : let s : Komorebi.SpecialFunctions.Coupled.Scales := ⟨2,3,2,3⟩
    s.Autonomous ![1,-1] := by
  exact ordered_rows_autonomous _ _ rfl rfl (by simp)

example : halfScales.Autonomous 0 := halfScales.zero_row_autonomous

example : ¬halfScales.Autonomous ![1,0] := by
  intro h
  have hh := halfScales.autonomous_row_sum_zero halfScales_positive _ h
  norm_num at hh

example : let s : Komorebi.SpecialFunctions.Coupled.Scales := ⟨1/2,1/4,1/4,1/2⟩
    s.U = s.V ∧ ∀ c : Fin 2 → ℂ, c ≠ 0 → ¬s.Autonomous c := by
  dsimp only
  constructor
  · apply (components_equal_iff_unordered_rows _ (by norm_num [positive]) (by norm_num)).mpr
    exact Or.inr ⟨rfl,rfl⟩
  · intro c hc
    exact no_nonzero_autonomous_if_rows_differ _ (by norm_num [positive]) (by norm_num) c hc

example (P : Matrix (Fin 2) (Fin 2) ℂ) (hP : IsUnit P) :
    ¬∀ i, halfScales.GermAutonomous (P i) :=
  halfScales.no_invertible_constant_germ_decoupling halfScales_positive P hP

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (c : Fin 2 → ℂ)
    (X Y : LocalInput) (hu : X.u =ᶠ[𝓝 (0 : ℂ)] Y.u) (hv : X.v =ᶠ[𝓝 (0 : ℂ)] Y.v) :
    s.localField c X = s.localField c Y := s.local_field_respects_component_germs c X Y hu hv
