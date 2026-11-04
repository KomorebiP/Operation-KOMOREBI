import CoupledScalarReduction
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example : (scalarScales (1 / 2) (1 / 4)).U = (scalarScales (1 / 2) (1 / 4)).V :=
  scalar_components_equal _ _

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (h : s.q = s.b ∧ s.r = s.a) : s.U = s.V :=
  (s.components_equal_iff_unordered_rows hs hc).mpr (Or.inr h)

example : let s : Komorebi.SpecialFunctions.Coupled.Scales := ⟨1 / 2, 1 / 4, 1 / 3, 3 / 8⟩
    s.p = s.k ∧ s.U ≠ s.V := by
  dsimp only
  constructor
  · norm_num [p,k]
  · intro he
    have hh := (components_equal_iff_unordered_rows _
      (by norm_num [Komorebi.SpecialFunctions.Coupled.Scales.positive])
      (by norm_num)).mp he
    norm_num [sameUnorderedRows] at hh

example (z : ℂ) : halfScales.U z = (Real.sqrt 2 : ℂ) * Complex.sinh (z / (Real.sqrt 2 : ℂ)) :=
  (canonical_half_sinh z).1

example : halfScales.U 0 = 0 := by simpa using (canonical_half_sinh 0).1

example : unequalScales.lowerType unequalScales_positive unequalScales_strict 1 =
    2 * unequalScales.lowerType unequalScales_positive unequalScales_strict 0 :=
  unequal_type_proportions.1

example (z : ℂ) (hz : ‖z‖ ≤ 1) :
    ‖unequalScales.U z - (z + (2 / 75 : ℂ) * z ^ 3 + (88 / 234375 : ℂ) * z ^ 5 +
      (18814 / 8544921875 : ℂ) * z ^ 7)‖ ≤ ‖z‖ ^ 9 / 8 :=
  (unequal_degree_seven_error z hz).1

example : surfaceCrossScale (1 / 2) (1 / 4) (1 / 2) 1 = 1 := by norm_num [surfaceCrossScale]

example {q r b t : ℝ} (hq : 0 < q) (hr : 0 < r) (hb : 0 < b)
    (hq1 : q < 1) (hr1 : r < 1) (hb1 : b < 1) (ht : 0 < t)
    (hbudget : (1 - q ^ t) * (1 - b ^ t) < r ^ t) :
    ∃ hs : (orderSurfaceScales q r b t).positive,
      ∃ hc : (orderSurfaceScales q r b t).q < 1 ∧ (orderSurfaceScales q r b t).r < 1 ∧
        (orderSurfaceScales q r b t).a < 1 ∧ (orderSurfaceScales q r b t).b < 1,
      (orderSurfaceScales q r b t).characteristicExponent hs hc = t ∧
        ∀ i : Fin 2, (orderSurfaceScales q r b t).radialOrder i = t :=
  order_surface_realization hq hr hb hq1 hr1 hb1 ht hbudget
