import DiagonalResonantHorizon

namespace Komorebi.StrongArtin.EffectiveResonance.Controls

theorem cube_horizon_at_residue : scalarHorizon 3 3 1 = 3 := by
  norm_num [scalarHorizon, padicValNat_self]

theorem square_horizon_at_depth_four : scalarHorizon 2 2 4 = 5 := by
  norm_num [scalarHorizon, padicValNat_self]

theorem nine_power_horizon : scalarHorizon 3 9 1 = 5 := by
  have hv : padicValNat 3 9 = 2 := by
    change padicValNat 3 (3 ^ 2) = 2
    exact padicValNat.prime_pow 2
  norm_num [scalarHorizon, hv]

theorem cube_ten_above_four :
    ∃! z : PadicInt 3, z ^ 3 = 10 ∧ PadicInt.toZModPow 2 z = 4 := by
  have ha : IsUnit (4 : PadicInt 3) := PadicInt.isUnit_iff.mpr
    (PadicInt.norm_natCast_eq_one_iff.mpr (by decide))
  have h := (scalar_deep_prefix_root_iff (p := 3) 3 (by decide) (10 : PadicInt 3) 4 ha 2
    (by norm_num [padicValNat_self])).mpr (by rw [padicValNat_self]; norm_num [map_ofNat]; decide)
  simpa only [map_ofNat] using h

theorem no_cube_one_above_four :
    ¬ ∃ z : PadicInt 3, z ^ 3 = 1 ∧ PadicInt.toZModPow 2 z = 4 := by
  have ha : IsUnit (4 : PadicInt 3) := PadicInt.isUnit_iff.mpr
    (PadicInt.norm_natCast_eq_one_iff.mpr (by decide))
  have h := scalar_deep_prefix_exists_iff 3 (by decide) (1 : PadicInt 3) 4 ha 2
    (by norm_num [padicValNat_self])
  have hn := (not_congr h).mpr (by rw [padicValNat_self]; norm_num [map_ofNat]; decide)
  simpa only [map_ofNat] using hn

theorem no_square_one_above_nine :
    ¬ ∃ z : PadicInt 2, z ^ 2 = 1 ∧ PadicInt.toZModPow 4 z = 9 := by
  have ha : IsUnit (9 : PadicInt 2) := PadicInt.isUnit_iff.mpr
    (PadicInt.norm_natCast_eq_one_iff.mpr (by decide))
  have h := scalar_deep_prefix_exists_iff 2 (by decide) (1 : PadicInt 2) 9 ha 4
    (by norm_num [padicValNat_self])
  have hn := (not_congr h).mpr (by rw [padicValNat_self]; norm_num [map_ofNat]; decide)
  simpa only [map_ofNat] using hn

theorem horizon_witness_is_finite_root : (10 : ZMod 27) ^ 3 = 1 := by decide

theorem horizon_witness_can_die :
    ¬ ∃ z : PadicInt 3, z ^ 3 = 1 ∧ PadicInt.toZModPow 3 z = 10 := by
  have ha : IsUnit (10 : PadicInt 3) := PadicInt.isUnit_iff.mpr
    (PadicInt.norm_natCast_eq_one_iff.mpr (by decide))
  have h := scalar_deep_prefix_exists_iff 3 (by decide) (1 : PadicInt 3) 10 ha 3
    (by norm_num [padicValNat_self])
  have hn := (not_congr h).mpr (by rw [padicValNat_self]; norm_num [map_ofNat]; decide)
  simpa only [map_ofNat] using hn

theorem diagonal_cube_example :
    ∃ F : (Matrix (Fin 2) (Fin 2) (PadicInt 3))ˣ,
      F.val ^ 3 = Matrix.diagonal ![10, 28] ∧
      (PadicInt.toZModPow 2).mapMatrix F.val = Matrix.diagonal ![4, 1] := by
  have ha : ∀ i : Fin 2, IsUnit (![4, 1] i : PadicInt 3) := by
    intro i
    fin_cases i
    · exact PadicInt.isUnit_iff.mpr (PadicInt.norm_natCast_eq_one_iff.mpr (by decide))
    · exact isUnit_one
  have hcert : ∀ i : Fin 2, ∃ b : ZMod (3 ^ scalarHorizon 3 3 2),
      b ^ 3 = PadicInt.toZModPow (scalarHorizon 3 3 2) (![10, 28] i) ∧
      (ZMod.cast b : ZMod (3 ^ 2)) = PadicInt.toZModPow 2 (![4, 1] i) := by
    have hs : scalarHorizon 3 3 2 = 3 := by norm_num [scalarHorizon, padicValNat_self]
    rw [hs]
    intro i
    fin_cases i
    · refine ⟨4, ?_, ?_⟩
      · norm_num [map_ofNat]; decide
      · norm_num [map_ofNat]; decide
    · refine ⟨1, ?_, ?_⟩
      · norm_num [map_ofNat]; decide
      · norm_num [map_ofNat]
  have heq : (fun i : Fin 2 => PadicInt.toZModPow 2 (![4, 1] i : PadicInt 3)) = ![4, 1] := by
    funext i
    fin_cases i <;> norm_num [map_ofNat]
  simpa only [heq] using exists_diagonal_matrix_unit_root 3 (by decide)
    (![10, 28] : Fin 2 → PadicInt 3) ![4, 1] ha 2 (by decide) hcert

end Komorebi.StrongArtin.EffectiveResonance.Controls
