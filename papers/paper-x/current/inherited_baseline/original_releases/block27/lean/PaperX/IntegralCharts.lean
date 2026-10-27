import PaperX.SmoothMaps

/-! Integral local maps are reconstructed from the finite parameter evaluations.
Completeness is required explicitly; it is not inferred from finite counts. -/
set_option autoImplicit false
namespace PaperX.IntegralCharts
open PaperX.FormalCharts PaperX.SmoothMaps

variable {R : Type*} [CommRing R] [IsLocalRing R]

/-- Reducing a maximal-ideal element at any precision produces a nilpotent. -/
theorem parameter_reduction_nilpotent (x : IsLocalRing.maximalIdeal R) (n : ℕ) :
    IsNilpotent (Ideal.Quotient.mk (IsLocalRing.maximalIdeal R ^ n) x.val) := by
  refine ⟨n, ?_⟩
  rw [← map_pow, Ideal.Quotient.eq_zero_iff_mem]
  exact Ideal.pow_mem_pow x.property n

/-- Evaluate a fixed integral tuple at each finite precision, including the
trivial precision-zero quotient to match the completion API. -/
noncomputable def finiteEvaluation {d : ℕ} (a : Fin d → IsLocalRing.maximalIdeal R) (n : ℕ) :
    MvPowerSeries (Fin d) R →ₐ[R] (R ⧸ IsLocalRing.maximalIdeal R ^ n) :=
  nilAeval (fun i => Ideal.Quotient.mk _ (a i).val)
    (fun i => parameter_reduction_nilpotent (a i) n)

@[simp] theorem finiteEvaluation_X {d : ℕ}
    (a : Fin d → IsLocalRing.maximalIdeal R) (n : ℕ) (i : Fin d) :
    finiteEvaluation a n (MvPowerSeries.X i) = Ideal.Quotient.mk _ (a i).val := by
  exact nilAeval_X _ _ _

/-- The evaluations commute with every quotient reduction. -/
theorem finiteEvaluation_compatible {d : ℕ}
    (a : Fin d → IsLocalRing.maximalIdeal R) {m n : ℕ} (h : m ≤ n) :
    (Ideal.Quotient.factorPow (IsLocalRing.maximalIdeal R) h).comp
      (finiteEvaluation a n).toRingHom = (finiteEvaluation a m).toRingHom := by
  apply nilpotent_hom_ext d
  · intro r
    change Ideal.Quotient.factorPow (IsLocalRing.maximalIdeal R) h
      (finiteEvaluation a n (MvPowerSeries.C r)) = finiteEvaluation a m (MvPowerSeries.C r)
    rw [MvPowerSeries.c_eq_algebraMap, (finiteEvaluation a n).commutes r, (finiteEvaluation a m).commutes r]
    rfl
  · intro i
    change Ideal.Quotient.factorPow (IsLocalRing.maximalIdeal R) h
      (finiteEvaluation a n (MvPowerSeries.X i)) = finiteEvaluation a m (MvPowerSeries.X i)
    simp
  · intro i
    simpa only [RingHom.comp_apply, AlgHom.toRingHom_eq_coe, RingHom.coe_coe,
      finiteEvaluation_X] using (parameter_reduction_nilpotent (a i) n).map
        (Ideal.Quotient.factorPow (IsLocalRing.maximalIdeal R) h)

noncomputable def evaluationFamily {d : ℕ} (a : Fin d → IsLocalRing.maximalIdeal R) :
    PaperX.Reconstruction.RingFamily (MvPowerSeries (Fin d) R) (IsLocalRing.maximalIdeal R) where
  maps n := (finiteEvaluation a n).toRingHom
  compatible := finiteEvaluation_compatible a

/-- Genuine local algebra maps to the coefficient ring. -/
def IntegralPoint (d : ℕ) :=
  {f : MvPowerSeries (Fin d) R →ₐ[R] R // IsLocalHom f.toRingHom}

noncomputable def integralParameters {d : ℕ} (f : IntegralPoint (R := R) d) :
    Fin d → IsLocalRing.maximalIdeal R := by
  let : IsLocalHom f.val.toRingHom := f.property
  exact fun i => ⟨f.val (MvPowerSeries.X i), map_nonunit f.val.toRingHom _ (variable_nonunit d i)⟩

/-- A local integral map has exactly the expected finite evaluations. -/
theorem integral_map_reduces {d : ℕ} (f : IntegralPoint (R := R) d) (n : ℕ) :
    (Ideal.Quotient.mk (IsLocalRing.maximalIdeal R ^ n)).comp f.val.toRingHom =
      (finiteEvaluation (integralParameters f) n).toRingHom := by
  apply nilpotent_hom_ext d
  · intro r
    change Ideal.Quotient.mk _ (f.val (MvPowerSeries.C r)) =
      finiteEvaluation (integralParameters f) n (MvPowerSeries.C r)
    rw [MvPowerSeries.c_eq_algebraMap, f.val.commutes r, (finiteEvaluation _ n).commutes r]
    rfl
  · intro i
    simp only [RingHom.comp_apply, AlgHom.toRingHom_eq_coe, RingHom.coe_coe, finiteEvaluation_X]
    rfl
  · intro i
    exact parameter_reduction_nilpotent (integralParameters f i) n

/-- Continuity is in the maximal-ideal adic topologies, not an auxiliary discrete topology. -/
theorem integralPoint_continuous {d : ℕ} (f : IntegralPoint (R := R) d) :
    @Continuous _ _ (IsLocalRing.maximalIdeal (MvPowerSeries (Fin d) R)).adicTopology
      (IsLocalRing.maximalIdeal R).adicTopology f.val := by
  let : IsLocalHom f.val.toRingHom := f.property
  exact PaperX.Reconstruction.local_map_continuous f.val.toRingHom

variable [IsAdicComplete (IsLocalRing.maximalIdeal R) R]

/-- Build the actual integral algebra map from the compatible quotient evaluations. -/
noncomputable def integralEval {d : ℕ} (a : Fin d → IsLocalRing.maximalIdeal R) :
    MvPowerSeries (Fin d) R →ₐ[R] R :=
  PaperX.Reconstruction.reconstructAlg (IsLocalRing.maximalIdeal R) (evaluationFamily a)
    (fun n r => (finiteEvaluation a n).commutes r)

theorem integralEval_reduces {d : ℕ} (a : Fin d → IsLocalRing.maximalIdeal R) (n : ℕ) :
    (Ideal.Quotient.mk (IsLocalRing.maximalIdeal R ^ n)).comp (integralEval a).toRingHom =
      (finiteEvaluation a n).toRingHom :=
  PaperX.Reconstruction.reconstruct_reduces _ (evaluationFamily a) n

@[simp] theorem integralEval_X {d : ℕ}
    (a : Fin d → IsLocalRing.maximalIdeal R) (i : Fin d) :
    integralEval a (MvPowerSeries.X i) = (a i).val := by
  apply congrFun (IsHausdorff.funext' (IsLocalRing.maximalIdeal R)
    (f := fun _ : Unit => integralEval a (MvPowerSeries.X i))
    (g := fun _ : Unit => (a i).val) ?_) ()
  intro n _
  have h := congrArg (fun f : MvPowerSeries (Fin d) R →+* (R ⧸ IsLocalRing.maximalIdeal R ^ n) =>
    f (MvPowerSeries.X i)) (integralEval_reduces a n)
  simpa using h

/-- Locality follows from the first positive finite evaluation. -/
theorem integralEval_local {d : ℕ} (a : Fin d → IsLocalRing.maximalIdeal R) :
    IsLocalHom (integralEval a).toRingHom := by
  apply PaperX.Reconstruction.reconstruct_isLocal
  let : Nontrivial (R ⧸ IsLocalRing.maximalIdeal R ^ (0+1)) := quotient_nontrivial R 0
  let : IsLocalRing (R ⧸ IsLocalRing.maximalIdeal R ^ (0+1)) := quotient_local R 0
  let : IsLocalHom (algebraMap R (R ⧸ IsLocalRing.maximalIdeal R ^ (0+1))) := quotient_map_local R 0
  apply nilpotent_map_isLocal (finiteEvaluation a 1)
  intro i
  simpa using parameter_reduction_nilpotent (a i) 1

/-- Equality at every precision yields uniqueness of the integral map. -/
theorem integralEval_unique {d : ℕ} (f : IntegralPoint (R := R) d) :
    integralEval (integralParameters f) = f.val := by
  have h := PaperX.Reconstruction.reconstruct_unique (IsLocalRing.maximalIdeal R)
    (evaluationFamily (integralParameters f)) f.val.toRingHom (integral_map_reduces f)
  ext p
  exact congrArg (fun F : MvPowerSeries (Fin d) R →+* R => F p) h.symm

/-- Complete local formal points are precisely arbitrary tuples in the maximal ideal. -/
noncomputable def integralPointEquiv (d : ℕ) : IntegralPoint (R := R) d ≃
    (Fin d → IsLocalRing.maximalIdeal R) where
  toFun := integralParameters
  invFun a := ⟨integralEval a, integralEval_local a⟩
  left_inv f := Subtype.ext (integralEval_unique f)
  right_inv a := by
    funext i
    exact Subtype.ext (integralEval_X a i)

end PaperX.IntegralCharts
