import KomorebiVerification.PaperII.ResidueFourierCRT
import KomorebiVerification.PaperII.ResultantSeparation

/-! Integral character averages preserve actual scalar submodules. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.IntegralCharacters
universe u v w
variable {O : Type u} [CommRing O]
variable {K : Type v} [Field K] [Algebra O K]
variable {V : Type w} [AddCommGroup V] [Module K V] [Module O V]
variable [IsScalarTower O K V]

/-- Stability under one linear map implies stability under every actual operator power. -/
theorem power_preserves (L : Submodule O V) (U : Module.End K V)
    (hU : ∀ x ∈ L, U x ∈ L) (k : Nat) : ∀ x ∈ L, (U ^ k) x ∈ L := by
  induction k with
  | zero => simpa
  | succ k ih =>
      intro x hx
      rw [pow_succ', Module.End.mul_apply]
      exact hU _ (ih x hx)

/-- Actual field-valued operator character average. -/
def characterAverage (N : Nat) (omega : O) (U : Module.End K V) (j : Nat) :
    Module.End K V :=
  (N : K)⁻¹ • ∑ k : Fin N,
    ((algebraMap O K omega)⁻¹ ^ (j * k.val)) • (U ^ k.val)

/-- Away from the group order, the field average is an integral linear combination of
powers, so it preserves every U-stable O-submodule, in particular every lattice. -/
theorem characterAverage_preserves (L : Submodule O V)
    (N : Nat) (hN : 0 < N) (hunit : IsUnit (N : O))
    (omega : O) (homega : IsPrimitiveRoot omega N)
    (U : Module.End K V) (hU : ∀ x ∈ L, U x ∈ L) (j : Nat) :
    ∀ x ∈ L, characterAverage N omega U j x ∈ L := by
  obtain ⟨nunit, hnunit⟩ := hunit
  obtain ⟨wunit, hwunit⟩ := homega.isUnit (Nat.ne_of_gt hN)
  have hn : (N : K)⁻¹ = algebraMap O K (↑nunit⁻¹ : O) := by
    rw [map_units_inv, hnunit, map_natCast]
  have hw : (algebraMap O K omega)⁻¹ = algebraMap O K (↑wunit⁻¹ : O) := by
    rw [map_units_inv, hwunit]
  intro x hx
  simp only [characterAverage, LinearMap.smul_apply, LinearMap.sum_apply]
  rw [hn, algebraMap_smul]
  apply L.smul_mem
  apply L.sum_mem
  intro k _
  rw [hw, ← map_pow, algebraMap_smul]
  exact L.smul_mem _ (power_preserves L U hU k.val x hx)

/-- The manuscript situation U^N=I is a specialization; no spectral conclusion is
assumed to prove integrality. -/
theorem manuscript_character_integrality (L : Submodule O V)
    (N : Nat) (hN : 0 < N) (hunit : IsUnit (N : O))
    (omega : O) (homega : IsPrimitiveRoot omega N)
    (U : Module.End K V) (_horder : U ^ N = 1)
    (hU : ∀ x ∈ L, U x ∈ L) (j : Nat) :
    ∀ x ∈ L, characterAverage N omega U j x ∈ L :=
  characterAverage_preserves L N hN hunit omega homega U hU j

end Komorebi.PaperII.IntegralCharacters
#print axioms Komorebi.PaperII.IntegralCharacters.characterAverage_preserves
