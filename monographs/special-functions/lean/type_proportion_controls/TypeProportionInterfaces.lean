import CoupledTypeProportions
noncomputable section
open Filter Set
open scoped Topology Matrix
open Komorebi.SpecialFunctions.Coupled.Scales

example : Tendsto (fun R : ℝ => (((1 : ℝ) / 2) * (R - 1)) ^ ((1 : ℝ) / 2) /
    R ^ ((1 : ℝ) / 2)) atTop (𝓝 (((1 : ℝ) / 2) ^ ((1 : ℝ) / 2))) :=
  affine_power_ratio_tendsto (by norm_num) 1 _

example {x y : Fin 2 → ℝ} (hxy : x ≤ y)
    (hd : dotProduct ![2, 1] x = dotProduct ![2, 1] y) : x = y :=
  positive_dot_rigidity (by intro i; fin_cases i <;> norm_num) hxy hd

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    ∃ τlo τhi : ℝ, 0 < τlo ∧ τlo ≤ τhi ∧
      s.lowerType hs hc = τlo • s.normalizedCharacteristicVector (s.characteristicExponent hs hc) ∧
      s.upperType hs hc = τhi • s.normalizedCharacteristicVector (s.characteristicExponent hs hc) :=
  s.canonical_positive_type_proportions hs hc

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.lowerType hs hc 0 / s.lowerType hs hc 1 =
      s.upperType hs hc 0 / s.upperType hs hc 1 := (s.canonical_type_ratios hs hc).1

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (h : ∃ τ : ℝ, Tendsto (s.growthRatio hs hc 1) atTop (𝓝 τ)) :
    ∃ τ : ℝ, 0 < τ ∧ Tendsto (fun R : ℝ => fun j : Fin 2 => s.growthRatio hs hc j R)
      atTop (𝓝 (τ • s.normalizedCharacteristicVector (s.characteristicExponent hs hc))) :=
  s.canonical_type_limit_vector hs hc 1 h

example (s : Komorebi.SpecialFunctions.Coupled.Scales) (hs : s.positive)
    (hc : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    (∃ τ : ℝ, Tendsto (fun R : ℝ => Real.log (s.maximumModulus 0 R) /
        R ^ (s.characteristicExponent hs hc)) atTop (𝓝 τ)) ↔
      (∃ τ : ℝ, Tendsto (fun R : ℝ => Real.log (s.maximumModulus 1 R) /
        R ^ (s.characteristicExponent hs hc)) atTop (𝓝 τ)) :=
  s.canonical_maximum_type_limit_equivalence hs hc 0 1
