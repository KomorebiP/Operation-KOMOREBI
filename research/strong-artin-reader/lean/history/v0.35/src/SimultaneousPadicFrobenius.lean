import PadicFrobeniusRoot

/-! A nonresonant pivot restriction determines a common p-adic Frobenius.
Independent solutions are not substituted for a shared root. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
variable (p : ℕ) [Fact (Nat.Prime p)] (n : Type) [Fintype n] [DecidableEq n]

theorem padic_power_injective_on_residue (d : ℕ) (Fbar : (Matrix n n (ZMod p))ˣ)
    (hN : Nonresonant n Fbar d) (F G : (Matrix n n ℤ_[p])ˣ)
    (hF : padicUnitReduction p n 0 F = Fbar)
    (hG : padicUnitReduction p n 0 G = Fbar) (hp : F^d = G^d) : F = G := by
  have h0 : padicUnitReduction p n 0 (F^d) = Fbar^d := by rw [map_pow, hF]
  obtain ⟨L, _, hu⟩ := exists_unique_padic_frobenius_root p n d Fbar (F^d) h0 hN
  exact (hu F ⟨hF, rfl⟩).trans (hu G ⟨hG, hp.symm⟩).symm

/-- Exact simultaneous matching from a pivot: target power-compatibility is necessary
and sufficient. The remaining degrees may be divisible by p. -/
theorem simultaneous_padic_roots_iff (I : Type) (i0 : I) (d : I → ℕ)
    (Fbar : (Matrix n n (ZMod p))ˣ) (U : I → (Matrix n n ℤ_[p])ˣ)
    (hU : ∀ i, padicUnitReduction p n 0 (U i) = Fbar^(d i))
    (hN : Nonresonant n Fbar (d i0))
    (hNi : ∀ i, Nonresonant n (Fbar^(d i)) (d i0)) :
    (∃! F : (Matrix n n ℤ_[p])ˣ,
      padicUnitReduction p n 0 F = Fbar ∧ ∀ i, F^(d i) = U i) ↔
      ∀ i, (U i)^(d i0) = (U i0)^(d i) := by
  constructor
  · rintro ⟨F, ⟨_, hF⟩, _⟩ i
    rw [← hF i, ← hF i0, ← pow_mul, ← pow_mul, Nat.mul_comm]
  · intro hp
    obtain ⟨F, hF, hu⟩ := exists_unique_padic_frobenius_root p n (d i0) Fbar (U i0) (hU i0) hN
    refine ⟨F, ⟨hF.1, ?_⟩, ?_⟩
    · intro i
      apply padic_power_injective_on_residue p n (d i0) (Fbar^(d i)) (hNi i)
        (F^(d i)) (U i) (by rw [map_pow, hF.1]) (hU i)
      calc
        (F^(d i))^(d i0) = (F^(d i0))^(d i) := by rw [← pow_mul, ← pow_mul, Nat.mul_comm]
        _ = (U i0)^(d i) := congrArg (fun x => x^(d i)) hF.2
        _ = (U i)^(d i0) := (hp i).symm
    · intro G hG
      exact hu G ⟨hG.1, hG.2 i0⟩

/-- On the identity residue fibre, one prime-to-p anchor handles an arbitrary
family of degrees, including defining-characteristic degrees, provided the
explicit shared-power identities hold. -/
theorem identity_family_padic_roots_iff (I : Type) (i0 : I) (d : I → ℕ)
    (hd : (d i0 : ZMod p) ≠ 0) (U : I → (Matrix n n ℤ_[p])ˣ)
    (hU : ∀ i, padicUnitReduction p n 0 (U i) = 1) :
    (∃! F : (Matrix n n ℤ_[p])ˣ,
      padicUnitReduction p n 0 F = 1 ∧ ∀ i, F^(d i) = U i) ↔
      ∀ i, (U i)^(d i0) = (U i0)^(d i) := by
  apply simultaneous_padic_roots_iff p n I i0 d 1 U
    (by simpa using hU) (nonresonant_identity n (d i0) hd)
  intro i
  simpa only [one_pow] using nonresonant_identity (k := ZMod p) n (d i0) hd

end Komorebi.StrongArtin.FrobeniusTower
