import PadicMatrixTowerLimit

/-! A genuine p-adic matrix root theorem. Finite-level nonresonance is enough
for the infinite coefficient tower, with uniqueness in the fixed residue fibre. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
variable (p : ℕ) [Fact (Nat.Prime p)] (n : Type) [Fintype n] [DecidableEq n]

theorem exists_unique_padic_frobenius_root (d : ℕ)
    (Fbar : (Matrix n n (ZMod p))ˣ) (U : (Matrix n n ℤ_[p])ˣ)
    (h0 : padicUnitReduction p n 0 U = Fbar^d)
    (hN : Nonresonant n Fbar d) :
    ∃! F : (Matrix n n ℤ_[p])ˣ,
      padicUnitReduction p n 0 F = Fbar ∧ F^d = U := by
  obtain ⟨F, hF, huniq⟩ := exists_unique_compatible_root_tower p n d Fbar
    (fun r => padicUnitReduction p n r U) (padicUnitReduction_compatible p n U) h0 hN
  let L := unitLimit p n F hF.2.1
  have hL : ∀ r, padicUnitReduction p n r L = F r := unitLimit_spec p n F hF.2.1
  refine ⟨L, ⟨(hL 0).trans hF.1, ?_⟩, ?_⟩
  · apply padicUnit_ext p n
    intro r
    rw [map_pow, hL, hF.2.2 r]
  · intro V hV
    have hVpow : ∀ r, (padicUnitReduction p n r V)^d = padicUnitReduction p n r U := by
      intro r
      rw [← map_pow, hV.2]
    have he := huniq (fun r => padicUnitReduction p n r V)
      ⟨hV.1, padicUnitReduction_compatible p n V, hVpow⟩
    apply padicUnit_ext p n
    intro r
    exact (congrFun he r).trans (hL r).symm

/-- In particular, matrix targets in the principal congruence subgroup have
unique prime-to-p roots in that same subgroup. -/
theorem identity_residue_unique_padic_root (d : ℕ) (hd : (d : ZMod p) ≠ 0)
    (U : (Matrix n n ℤ_[p])ˣ) (h0 : padicUnitReduction p n 0 U = 1) :
    ∃! F : (Matrix n n ℤ_[p])ˣ,
      padicUnitReduction p n 0 F = 1 ∧ F^d = U := by
  exact exists_unique_padic_frobenius_root p n d 1 U (by simpa using h0)
    (nonresonant_identity n d hd)

/-- The nonsemisimple unipotent-adjoint sector, with degree prime to p. -/
theorem unipotent_adjoint_unique_padic_root (d : ℕ)
    (Fbar : (Matrix n n (ZMod p))ˣ) (U : (Matrix n n ℤ_[p])ˣ)
    (h0 : padicUnitReduction p n 0 U = Fbar^d)
    (hT : IsNilpotent (adjoint n Fbar - 1)) (hd : (d : ZMod p) ≠ 0) :
    ∃! F : (Matrix n n ℤ_[p])ˣ,
      padicUnitReduction p n 0 F = Fbar ∧ F^d = U :=
  exists_unique_padic_frobenius_root p n d Fbar U h0
    (nonresonant_of_unipotent_adjoint n Fbar d hT hd)

end Komorebi.StrongArtin.FrobeniusTower
