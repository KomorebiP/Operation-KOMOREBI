import PaperX.FormalCharts
import PaperX.Zeta
import Mathlib.RingTheory.LocalRing.ResidueField.Basic

/-! Actual local algebra maps out of a finite-variable power-series ring.
Finite nilpotent evaluation is bridged to ideal-image coordinates, and then to
the previously proved counts and rational series. -/
set_option autoImplicit false
namespace PaperX.SmoothMaps
open PaperX.FormalCharts

variable {R S : Type*} [CommRing R] [CommRing S]

/-- A power-series parameter is a nonunit. -/
theorem variable_nonunit [IsLocalRing R] (d : ℕ) (i : Fin d) :
    MvPowerSeries.X i ∈ IsLocalRing.maximalIdeal (MvPowerSeries (Fin d) R) := by
  change ¬ IsUnit (MvPowerSeries.X i : MvPowerSeries (Fin d) R)
  simp [MvPowerSeries.isUnit_iff_constantCoeff]

/-- Reduction of a nilpotent-parameter map is its constant-coefficient map. -/
theorem residue_map_eq [IsLocalRing S] [Algebra R S] {d : ℕ}
    (f : MvPowerSeries (Fin d) R →ₐ[R] S)
    (hnil : ∀ i, IsNilpotent (f (MvPowerSeries.X i))) :
    (IsLocalRing.residue S).comp f.toRingHom =
      ((IsLocalRing.residue S).comp (algebraMap R S)).comp MvPowerSeries.constantCoeff := by
  apply nilpotent_hom_ext d
  · intro r
    simp only [RingHom.comp_apply, AlgHom.toRingHom_eq_coe, RingHom.coe_coe,
      MvPowerSeries.constantCoeff_C]
    exact congrArg (IsLocalRing.residue S) (f.commutes r)
  · intro i
    simp only [RingHom.comp_apply, MvPowerSeries.constantCoeff_X, map_zero]
    exact ((hnil i).map (IsLocalRing.residue S)).eq_zero
  · intro i
    exact (hnil i).map (IsLocalRing.residue S)

/-- Nilpotent parameter images give a local map when the coefficient map is local. -/
theorem nilpotent_map_isLocal [IsLocalRing R] [IsLocalRing S] [Algebra R S]
    [IsLocalHom (algebraMap R S)] {d : ℕ}
    (f : MvPowerSeries (Fin d) R →ₐ[R] S)
    (hnil : ∀ i, IsNilpotent (f (MvPowerSeries.X i))) : IsLocalHom f.toRingHom := by
  constructor
  intro p hp
  apply MvPowerSeries.isUnit_iff_constantCoeff.mpr
  apply isUnit_of_map_unit (algebraMap R S)
  apply (IsLocalRing.residue_ne_zero_iff_isUnit _).mp
  have he := congrArg (fun h : MvPowerSeries (Fin d) R →+* IsLocalRing.ResidueField S => h p)
    (residue_map_eq f hnil)
  change IsLocalRing.residue S (f p) =
    IsLocalRing.residue S (algebraMap R S (MvPowerSeries.constantCoeff p)) at he
  rw [← he]
  exact (IsUnit.map (IsLocalRing.residue S) hp).ne_zero

variable (R)
section Local
variable [IsLocalRing R]

/-- The actual quotient at positive depth is nontrivial. -/
theorem quotient_nontrivial (n : ℕ) : Nontrivial (R ⧸ IsLocalRing.maximalIdeal R ^ (n+1)) := by
  apply Ideal.Quotient.nontrivial_iff.mpr
  exact ne_top_of_le_ne_top (IsLocalRing.maximalIdeal.isMaximal R).ne_top
    (Ideal.pow_le_self (Nat.succ_ne_zero n))
attribute [local instance] quotient_nontrivial

/-- Positive-depth quotients remain local rings. -/
theorem quotient_local (n : ℕ) : IsLocalRing (R ⧸ IsLocalRing.maximalIdeal R ^ (n+1)) := by
  let : IsLocalHom (Ideal.Quotient.mk (IsLocalRing.maximalIdeal R ^ (n+1))) :=
    IsLocalHom.of_surjective _ Ideal.Quotient.mk_surjective
  exact IsLocalRing.of_surjective _ Ideal.Quotient.mk_surjective
attribute [local instance] quotient_local

/-- The coefficient quotient map is local. -/
theorem quotient_map_local (n : ℕ) :
    IsLocalHom (algebraMap R (R ⧸ IsLocalRing.maximalIdeal R ^ (n+1))) := by
  exact IsLocalHom.of_surjective _ Ideal.Quotient.mk_surjective
attribute [local instance] quotient_map_local

/-- Actual local coefficient-preserving maps; n=0 denotes precision one. -/
def Point (d n : ℕ) :=
  {f : MvPowerSeries (Fin d) R →ₐ[R] (R ⧸ IsLocalRing.maximalIdeal R ^ (n+1)) //
    IsLocalHom f.toRingHom}

/-- Every positive-depth coordinate is genuinely nilpotent in the quotient. -/
theorem coordinate_nilpotent (n : ℕ)
    (x : PaperX.Counting.Coordinate (IsLocalRing.maximalIdeal R) (n+1) 1) :
    IsNilpotent x.val := by
  obtain ⟨a, ha, hx⟩ := Submodule.mem_map.mp x.property
  rw [pow_one] at ha
  refine ⟨n+1, ?_⟩
  change Ideal.Quotient.mk _ a = x.val at hx
  rw [← hx, ← map_pow, Ideal.Quotient.eq_zero_iff_mem]
  exact Ideal.pow_mem_pow ha _

/-- The local quotient maximal ideal is exactly the positive-depth coordinate image. -/
theorem coordinate_iff_maximal (n : ℕ)
    (x : R ⧸ IsLocalRing.maximalIdeal R ^ (n+1)) :
    x ∈ Submodule.map (IsLocalRing.maximalIdeal R ^ (n+1)).mkQ
      (IsLocalRing.maximalIdeal R ^ 1) ↔
    x ∈ IsLocalRing.maximalIdeal (R ⧸ IsLocalRing.maximalIdeal R ^ (n+1)) := by
  rw [← IsLocalRing.map_maximalIdeal_of_surjective
    (Ideal.Quotient.mk (IsLocalRing.maximalIdeal R ^ (n+1))) Ideal.Quotient.mk_surjective]
  rw [Ideal.mem_map_iff_of_surjective _ Ideal.Quotient.mk_surjective, Submodule.mem_map]
  simp only [pow_one]
  rfl

/-- A local map must send every formal parameter into the positive-depth ideal. -/
noncomputable def parameters (d n : ℕ) (f : Point R d n) :
    PaperX.Counting.WeightedChart (IsLocalRing.maximalIdeal R) (fun _ : Fin d => 1) (n+1) := by
  let : IsLocalHom f.val.toRingHom := f.property
  exact fun i => ⟨f.val (MvPowerSeries.X i), (coordinate_iff_maximal R n _).mpr
    (map_nonunit f.val.toRingHom _ (variable_nonunit d i))⟩

/-- Evaluation of any parameter tuple gives an actual local algebra homomorphism. -/
noncomputable def fromParameters (d n : ℕ)
    (a : PaperX.Counting.WeightedChart (IsLocalRing.maximalIdeal R) (fun _ : Fin d => 1) (n+1)) :
    Point R d n :=
  ⟨nilAeval (fun i => (a i).val) (fun i => coordinate_nilpotent R n (a i)), by
    apply nilpotent_map_isLocal
    intro i
    simpa using coordinate_nilpotent R n (a i)⟩

/-- The missing smooth formal-map-to-parameter equivalence, with both inverses. -/
noncomputable def pointEquiv (d n : ℕ) : Point R d n ≃
    PaperX.Counting.WeightedChart (IsLocalRing.maximalIdeal R) (fun _ : Fin d => 1) (n+1) where
  toFun := parameters R d n
  invFun := fromParameters R d n
  left_inv f := by
    apply Subtype.ext
    apply nilpotent_algHom_ext
    · intro i; simp [fromParameters, parameters]
    · intro i; simp only [fromParameters, nilAeval_X]
      exact coordinate_nilpotent R n (parameters R d n f i)
  right_inv a := by
    funext i
    apply Subtype.ext
    simp [parameters, fromParameters]



/-- Every local point is continuous in the actual maximal-ideal adic topologies. -/
theorem point_continuous (d n : ℕ) (f : Point R d n) :
    @Continuous _ _ (IsLocalRing.maximalIdeal (MvPowerSeries (Fin d) R)).adicTopology
      (IsLocalRing.maximalIdeal (R ⧸ IsLocalRing.maximalIdeal R ^ (n+1))).adicTopology f.val := by
  let : IsLocalHom f.val.toRingHom := f.property
  exact PaperX.Reconstruction.local_map_continuous f.val.toRingHom

/-- Zero constant coefficient; coefficient m>=1 counts the actual local maps at precision m. -/
noncomputable def pointZeta (d : ℕ) : PowerSeries ℚ :=
  PowerSeries.mk fun m => if m = 0 then 0 else (Nat.card (Point R d (m-1)) : ℚ)

end Local

/-- Actual local maps on the smooth formal component, counted at every positive precision. -/
theorem smooth_point_count [IsDomain R] [IsDiscreteValuationRing R]
    [Finite (R ⧸ IsLocalRing.maximalIdeal R)] (d n : ℕ) :
    Nat.card (Point R d n) = Nat.card (R ⧸ IsLocalRing.maximalIdeal R) ^ (d*n) := by
  rw [Nat.card_congr (pointEquiv R d n)]
  simpa [PaperX.Counting.residueCard] using
    PaperX.Counting.smooth_chart_count (IsLocalRing.maximalIdeal R)
      (IsDiscreteValuationRing.not_a_field R) d (n+1)

/-- The smooth deformation zeta formula now counts actual homomorphisms. -/
theorem smooth_point_zeta [IsDomain R] [IsDiscreteValuationRing R]
    [Finite (R ⧸ IsLocalRing.maximalIdeal R)] (d : ℕ) :
    pointZeta R d = PowerSeries.X *
      (1 - PowerSeries.C ((Nat.card (R ⧸ IsLocalRing.maximalIdeal R) : ℚ)^d) * PowerSeries.X)⁻¹ := by
  rw [← PaperX.Zeta.smooth_zeta_formula]
  ext m
  simp [pointZeta, PaperX.Zeta.modelZeta, PaperX.Zeta.weightedCoeff, smooth_point_count]

end PaperX.SmoothMaps
