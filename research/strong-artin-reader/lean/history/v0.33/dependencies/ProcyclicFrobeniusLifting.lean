import ProfiniteCyclicGenerator

/-! Continuous procyclic representations and Frobenius lifting.
No prime-to-characteristic or same-finite-quotient condition is imposed. -/
namespace Komorebi.StrongArtin.Procyclic

@[simp] theorem fromFrobenius_naturality {H K : ProfiniteGrp.{0}}
    (q : H →ₜ* K) (h : H) : q.comp (fromFrobenius h) = fromFrobenius (q h) := by
  apply hom_ext
  simp

/-- A chosen preimage of Frobenius gives the unique continuous lift with that value. -/
theorem exists_unique_lift_with_frobenius {H K : ProfiniteGrp.{0}}
    (q : H →ₜ* K) (rho : Zhat →ₜ* K) (h : H) (hh : q h = rho frobenius) :
    ∃! l : Zhat →ₜ* H, q.comp l = rho ∧ l frobenius = h := by
  refine ⟨fromFrobenius h, ⟨?_, fromFrobenius_frobenius _⟩, ?_⟩
  · apply hom_ext
    simpa using hh
  · intro l hl
    apply hom_ext
    simpa using hl.2

/-- Projectivity of the free procyclic group, derived from the completion API. -/
theorem exists_lift_of_surjective {H K : ProfiniteGrp.{0}}
    (q : H →ₜ* K) (hq : Function.Surjective q) (rho : Zhat →ₜ* K) :
    ∃ l : Zhat →ₜ* H, q.comp l = rho := by
  obtain ⟨h, hh⟩ := hq (rho frobenius)
  obtain ⟨l, hl, _⟩ := exists_unique_lift_with_frobenius q rho h hh
  exact ⟨l, hl.1⟩

/-- Restriction to a degree-d unramified extension sends Frobenius to its d-th power. -/
noncomputable def degreeMap (d : ℕ) : Zhat →ₜ* Zhat :=
  fromFrobenius (H := Zhat) (frobenius ^ d)

@[simp] theorem degreeMap_frobenius (d : ℕ) : degreeMap d frobenius = frobenius ^ d :=
  fromFrobenius_frobenius _

@[simp] theorem degreeMap_one : degreeMap 1 = ContinuousMonoidHom.id Zhat := by
  apply hom_ext
  simp

theorem restrict_degreeMap {H : ProfiniteGrp.{0}} (rho : Zhat →ₜ* H) (d : ℕ) :
    rho.comp (degreeMap d) = fromFrobenius (rho frobenius ^ d) := by
  apply hom_ext
  simp

/-- Compare whole local representations, not only their raw matrices. -/
theorem conjugacy_iff_frobenius {H : ProfiniteGrp.{0}} (f g : Zhat →ₜ* H) (u : H) :
    (∀ z, u * f z * u⁻¹ = g z) ↔ u * f frobenius * u⁻¹ = g frobenius := by
  constructor
  · exact fun h => h frobenius
  · intro h
    let cf : Zhat →ₜ* H :=
      { toMonoidHom := (MulAut.conj u).toMonoidHom.comp f.toMonoidHom
        continuous_toFun := (continuous_const.mul f.continuous).mul continuous_const }
    have he : cf = g := hom_ext cf g h
    intro z
    exact congrArg (fun l : Zhat →ₜ* H => l z) he

/-- Simultaneous local gauge matching becomes an exact Frobenius power system. -/
theorem local_family_lifts_iff_frobenius_power_system {H K : ProfiniteGrp.{0}} {I : Type}
    (q : H →ₜ* K) (rho : Zhat →ₜ* K)
    (degree : I → ℕ) (t : I → (Zhat →ₜ* H)) :
    (∃ l : Zhat →ₜ* H, q.comp l = rho ∧
      ∃ u : I → H, (∀ i, q (u i) = 1) ∧
        ∀ i z, u i * l (degreeMap (degree i) z) * (u i)⁻¹ = t i z) ↔
    ∃ h : H, q h = rho frobenius ∧
      ∃ u : I → H, (∀ i, q (u i) = 1) ∧
        ∀ i, u i * h ^ degree i * (u i)⁻¹ = t i frobenius := by
  constructor
  · rintro ⟨l, hl, u, hu, ht⟩
    refine ⟨l frobenius, ?_, u, hu, ?_⟩
    · exact congrArg (fun f : Zhat →ₜ* K => f frobenius) hl
    · intro i
      simpa using ht i frobenius
  · rintro ⟨h, hh, u, hu, ht⟩
    refine ⟨fromFrobenius h, ?_, u, hu, ?_⟩
    · apply hom_ext
      simpa using hh
    · intro i
      apply (conjugacy_iff_frobenius ((fromFrobenius h).comp (degreeMap (degree i)))
        (t i) (u i)).mpr
      simpa using ht i

end Komorebi.StrongArtin.Procyclic
