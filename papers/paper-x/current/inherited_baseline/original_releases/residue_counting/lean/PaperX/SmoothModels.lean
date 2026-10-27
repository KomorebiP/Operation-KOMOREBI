import PaperX.Digits

/-! Transfer of the canonical smooth chart along a supplied coefficient-algebra
isomorphism. Smoothness/representability are not asserted without that datum. -/
set_option autoImplicit false
namespace PaperX.SmoothModels
variable {R A B S : Type*} [CommRing R] [CommRing A] [CommRing B] [CommRing S]
variable [Algebra R A] [Algebra R B] [Algebra R S]

/-- Local coefficient-preserving maps with their actual algebra-hom structure. -/
def LocalMaps (R A S : Type*) [CommRing R] [CommRing A] [CommRing S]
    [Algebra R A] [Algebra R S] := {f : A →ₐ[R] S // IsLocalHom f.toRingHom}

/-- A declared smooth coordinate isomorphism transports all local maps, not only
some constructed subset of them. -/
noncomputable def localMapCongr (E : A ≃ₐ[R] B) : LocalMaps R A S ≃ LocalMaps R B S where
  toFun f := ⟨f.val.comp E.symm.toAlgHom, by
    let : IsLocalHom f.val.toRingHom := f.property
    constructor
    intro x hx
    have h := isUnit_of_map_unit f.val.toRingHom _ hx
    simpa using h.map E.toRingHom⟩
  invFun f := ⟨f.val.comp E.toAlgHom, by
    let : IsLocalHom f.val.toRingHom := f.property
    constructor
    intro x hx
    have h := isUnit_of_map_unit f.val.toRingHom _ hx
    simpa using h.map E.symm.toRingHom⟩
  left_inv f := by
    apply Subtype.ext
    ext p
    simp
  right_inv f := by
    apply Subtype.ext
    ext p
    simp


/-- Formal-model points at depth n+1, classified by actual ideal-image tuples. -/
noncomputable def modelPointEquiv [IsLocalRing R] {d : ℕ}
    (E : A ≃ₐ[R] MvPowerSeries (Fin d) R) (n : ℕ) :
    LocalMaps R A (R ⧸ IsLocalRing.maximalIdeal R ^ (n+1)) ≃
      PaperX.Counting.WeightedChart (IsLocalRing.maximalIdeal R) (fun _ : Fin d => 1) (n+1) :=
  (localMapCongr E).trans (PaperX.SmoothMaps.pointEquiv R d n)

/-- Integral formal-model points and d independent residue streams. -/
noncomputable def modelDigitEquiv [IsDomain R] [IsDiscreteValuationRing R]
    [IsAdicComplete (IsLocalRing.maximalIdeal R) R] {d : ℕ}
    (E : A ≃ₐ[R] MvPowerSeries (Fin d) R) {π : R} (hπ : Irreducible π)
    (s : IsLocalRing.ResidueField R → R)
    (hs : Function.RightInverse s (IsLocalRing.residue R)) :
    LocalMaps R A R ≃ (Fin d → ℕ → IsLocalRing.ResidueField R) :=
  (localMapCongr E).trans (PaperX.Digits.integralPointDigitEquiv hπ s hs d)

/-- Continuity is automatic for local maps in the maximal-ideal adic topologies. -/
theorem localMap_continuous [IsLocalRing A] [IsLocalRing S] (f : LocalMaps R A S) :
    @Continuous _ _ (IsLocalRing.maximalIdeal A).adicTopology
      (IsLocalRing.maximalIdeal S).adicTopology f.val := by
  let : IsLocalHom f.val.toRingHom := f.property
  exact PaperX.Reconstruction.local_map_continuous f.val.toRingHom

/-- Full smooth formal-model count, conditional on the specified algebra isomorphism. -/
theorem smooth_model_count [IsDomain R] [IsDiscreteValuationRing R]
    [Finite (R ⧸ IsLocalRing.maximalIdeal R)] {d : ℕ}
    (E : A ≃ₐ[R] MvPowerSeries (Fin d) R) (n : ℕ) :
    Nat.card (LocalMaps R A (R ⧸ IsLocalRing.maximalIdeal R ^ (n+1))) =
      Nat.card (R ⧸ IsLocalRing.maximalIdeal R) ^ (d*n) := by
  rw [Nat.card_congr (localMapCongr (S := R ⧸ IsLocalRing.maximalIdeal R ^ (n+1)) E)]
  exact PaperX.SmoothMaps.smooth_point_count R d n

/-- Series defined from all actual local maps of the supplied representing ring. -/
noncomputable def modelZeta [IsLocalRing R] : PowerSeries ℚ :=
  PowerSeries.mk fun m => if m = 0 then 0 else
    (Nat.card (LocalMaps R A (R ⧸ IsLocalRing.maximalIdeal R ^ m)) : ℚ)

/-- Full smooth formal-model zeta identity. -/
theorem smooth_model_zeta [IsDomain R] [IsDiscreteValuationRing R]
    [Finite (R ⧸ IsLocalRing.maximalIdeal R)] {d : ℕ}
    (E : A ≃ₐ[R] MvPowerSeries (Fin d) R) :
    modelZeta (R := R) (A := A) = PowerSeries.X *
      (1 - PowerSeries.C ((Nat.card (R ⧸ IsLocalRing.maximalIdeal R) : ℚ)^d) * PowerSeries.X)⁻¹ := by
  rw [← PaperX.SmoothMaps.smooth_point_zeta R d]
  ext m
  cases m with
  | zero => simp [modelZeta, PaperX.SmoothMaps.pointZeta]
  | succ n =>
    simp only [modelZeta, PaperX.SmoothMaps.pointZeta, PowerSeries.coeff_mk,
      Nat.add_eq_zero_iff, Nat.one_ne_zero, and_false, ↓reduceIte, Nat.add_sub_cancel]
    exact congrArg (fun k : ℕ => (k : ℚ)) (Nat.card_congr (localMapCongr
      (S := R ⧸ IsLocalRing.maximalIdeal R ^ (n+1)) E))

end PaperX.SmoothModels
