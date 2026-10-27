import PrimePowerCoefficientTower

/-! One residual nonresonance condition yields unique compatible roots at every
positive prime-power level. No per-level vanishing hypothesis is supplied. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
variable (p : ℕ) [Fact (Nat.Prime p)] (n : Type) [Fintype n] [DecidableEq n]

/-- Compatibility at all adjacent coefficient levels. -/
abbrev Compatible (U : ∀ r, MatrixUnits p n r) : Prop :=
  ∀ r, down p n r (U (r+1)) = U r

/-- Uniqueness at each level is derived from the unchanged residual norm. -/
theorem unique_root_at_every_level (d : ℕ) (Fbar : (Matrix n n (ZMod p))ˣ)
    (U : ∀ r, MatrixUnits p n r) (hU : Compatible p n U)
    (h0 : U 0 = Fbar^d) (hN : Nonresonant n Fbar d) :
    ∀ r, ∃! F : MatrixUnits p n r, red p n r F = Fbar ∧ F^d = U r := by
  intro r
  induction r with
  | zero =>
    refine ⟨Fbar, ⟨red_zero p n Fbar, h0.symm⟩, ?_⟩
    intro y hy
    exact (red_zero p n y).symm.trans hy.1
  | succ r ih =>
    obtain ⟨F, hF, huniq⟩ := ih
    have hp : down p n r (U (r+1)) = F^d := (hU r).trans hF.2.symm
    obtain ⟨F', hF', huniq'⟩ := unique_next_root p n r d F (U (r+1)) hp (hF.1 ▸ hN)
    refine ⟨F', ⟨?_, hF'.2⟩, ?_⟩
    · exact (red_down p n r F').symm.trans ((congrArg (red p n r) hF'.1).trans hF.1)
    · intro y hy
      apply huniq' y
      refine ⟨huniq (down p n r y) ⟨?_, ?_⟩, hy.2⟩
      · exact (red_down p n r y).trans hy.1
      · rw [← map_pow, hy.2, hU r]

/-- A full compatible tower, not just unrelated roots at each finite precision. -/
theorem exists_unique_compatible_root_tower (d : ℕ) (Fbar : (Matrix n n (ZMod p))ˣ)
    (U : ∀ r, MatrixUnits p n r) (hU : Compatible p n U)
    (h0 : U 0 = Fbar^d) (hN : Nonresonant n Fbar d) :
    ∃! F : ∀ r, MatrixUnits p n r,
      F 0 = Fbar ∧ Compatible p n F ∧ ∀ r, (F r)^d = U r := by
  have h := unique_root_at_every_level p n d Fbar U hU h0 hN
  choose F hF hu using h
  refine ⟨F, ⟨(red_zero p n (F 0)).symm.trans (hF 0).1, ?_, fun r => (hF r).2⟩, ?_⟩
  · intro r
    apply hu r (down p n r (F (r+1)))
    constructor
    · exact (red_down p n r (F (r+1))).trans (hF (r+1)).1
    · rw [← map_pow, (hF (r+1)).2, hU r]
  · intro V hV
    have hred : ∀ r, red p n r (V r) = Fbar := by
      intro r
      induction r with
      | zero => exact (red_zero p n (V 0)).trans hV.1
      | succ r ih => rw [← red_down, hV.2.1 r, ih]
    funext r
    exact hu r (V r) ⟨hred r, hV.2.2 r⟩

/-- All prime-to-characteristic degrees work for a unipotent residual adjoint action. -/
theorem unipotent_adjoint_unique_tower (d : ℕ) (Fbar : (Matrix n n (ZMod p))ˣ)
    (U : ∀ r, MatrixUnits p n r) (hU : Compatible p n U)
    (h0 : U 0 = Fbar^d) (hT : IsNilpotent (adjoint n Fbar - 1))
    (hd : (d : ZMod p) ≠ 0) :
    ∃! F : ∀ r, MatrixUnits p n r,
      F 0 = Fbar ∧ Compatible p n F ∧ ∀ r, (F r)^d = U r :=
  exists_unique_compatible_root_tower p n d Fbar U hU h0
    (nonresonant_of_unipotent_adjoint n Fbar d hT hd)

/-- A substantive all-depth sector: arbitrary target matrices congruent to the identity. -/
theorem identity_residue_unique_tower (d : ℕ) (hd : (d : ZMod p) ≠ 0)
    (U : ∀ r, MatrixUnits p n r) (hU : Compatible p n U) (h0 : U 0 = 1) :
    ∃! F : ∀ r, MatrixUnits p n r,
      F 0 = 1 ∧ Compatible p n F ∧ ∀ r, (F r)^d = U r := by
  exact exists_unique_compatible_root_tower p n d 1 U hU (by simpa using h0)
    (nonresonant_identity n d hd)

end Komorebi.StrongArtin.FrobeniusTower
