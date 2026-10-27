import PaperX.Counting
import PaperX.Reconstruction
import Mathlib.RingTheory.MvPowerSeries.Equiv
import Mathlib.RingTheory.MvPowerSeries.Evaluation
import Mathlib.Topology.UniformSpace.DiscreteUniformity

/-! Finite-variable formal power-series maps into nilpotent thickenings.
The uniqueness argument is algebraic, so it does not assume the desired
map-to-parameter correspondence or hide a continuity hypothesis. -/
set_option autoImplicit false
namespace PaperX.FormalCharts

variable {R S : Type*} [CommRing R] [CommRing S]

/-- A map killing a power of X only sees a finite truncation. -/
theorem hom_eq_on_trunc (f : PowerSeries R →+* S) (n : ℕ)
    (hn : f PowerSeries.X ^ n = 0) (p : PowerSeries R) :
    f p = f (p.trunc n : PowerSeries R) := by
  conv_lhs => rw [p.eq_X_pow_mul_shift_add_trunc n]
  simp [hn]

/-- Algebraic uniqueness for one variable with nilpotent image. -/
theorem univariate_hom_ext (f g : PowerSeries R →+* S)
    (hC : ∀ r, f (PowerSeries.C r) = g (PowerSeries.C r))
    (hX : f PowerSeries.X = g PowerSeries.X)
    (hnil : IsNilpotent (f PowerSeries.X)) : f = g := by
  obtain ⟨n, hn⟩ := hnil
  have hg : g PowerSeries.X ^ n = 0 := by rw [← hX]; exact hn
  have hp : ∀ p : Polynomial R, f (p : PowerSeries R) = g (p : PowerSeries R) := by
    intro p
    induction p using Polynomial.induction_on' with
    | add p q hp hq => simpa using congrArg₂ (· + ·) hp hq
    | monomial n r => simp [PowerSeries.monomial_eq_C_mul_X_pow, hC, hX]
  ext p
  rw [hom_eq_on_trunc f n hn, hom_eq_on_trunc g n hg]
  exact hp _

@[simp] theorem finSucc_symm_C (d : ℕ) (r : R) :
    (MvPowerSeries.finSuccEquiv R d).symm (PowerSeries.C (MvPowerSeries.C r)) =
      MvPowerSeries.C r := by
  apply (MvPowerSeries.finSuccEquiv R d).injective
  simp

@[simp] theorem finSucc_symm_X (d : ℕ) :
    (MvPowerSeries.finSuccEquiv R d).symm PowerSeries.X = MvPowerSeries.X 0 := by
  apply (MvPowerSeries.finSuccEquiv R d).injective
  simp

@[simp] theorem finSucc_symm_C_X (d : ℕ) (i : Fin d) :
    (MvPowerSeries.finSuccEquiv R d).symm (PowerSeries.C (MvPowerSeries.X i)) =
      MvPowerSeries.X i.succ := by
  apply (MvPowerSeries.finSuccEquiv R d).injective
  simp

/-- Every ring map with nilpotent parameter images is determined by constants
and parameters. No topology on the source or target is assumed. -/
theorem nilpotent_hom_ext (d : ℕ)
    (f g : MvPowerSeries (Fin d) R →+* S)
    (hC : ∀ r, f (MvPowerSeries.C r) = g (MvPowerSeries.C r))
    (hX : ∀ i, f (MvPowerSeries.X i) = g (MvPowerSeries.X i))
    (hnil : ∀ i, IsNilpotent (f (MvPowerSeries.X i))) : f = g := by
  induction d with
  | zero =>
    ext p
    have hp : MvPowerSeries.C (MvPowerSeries.constantCoeff p) = p :=
      (MvPowerSeries.isEmptyEquiv (Fin 0) R).left_inv p
    rw [← hp]
    exact hC _
  | succ d ih =>
    let E := MvPowerSeries.finSuccEquiv R d
    let f' := f.comp E.symm.toRingHom
    let g' := g.comp E.symm.toRingHom
    have hcoeff : f'.comp PowerSeries.C = g'.comp PowerSeries.C := by
      apply ih
      · intro r
        simpa [f', g', E] using hC r
      · intro i
        simpa [f', g', E] using hX i.succ
      · intro i
        simpa [f', E] using hnil i.succ
    have heq : f' = g' := by
      apply univariate_hom_ext
      · intro p
        exact congrArg (fun h : MvPowerSeries (Fin d) R →+* S => h p) hcoeff
      · simpa [f', g', E] using hX 0
      · simpa [f', E] using hnil 0
    ext p
    have hh := congrArg (fun h : PowerSeries (MvPowerSeries (Fin d) R) →+* S => h (E p)) heq
    simpa [f', g', E] using hh



/-- Evaluation at finitely many nilpotents, with discrete auxiliary topologies.
This is an actual ring homomorphism supplied by Mathlib's evaluation theorem. -/
noncomputable def nilEval {d : ℕ} (φ : R →+* S) (a : Fin d → S)
    (ha : ∀ i, IsNilpotent (a i)) : MvPowerSeries (Fin d) R →+* S := by
  let : UniformSpace R := ⊥
  let : UniformSpace S := ⊥
  apply MvPowerSeries.eval₂Hom (φ := φ) (a := a) continuous_of_discreteTopology
  exact ⟨fun i => (ha i).isTopologicallyNilpotent, by simp⟩

@[simp] theorem nilEval_C {d : ℕ} (φ : R →+* S) (a : Fin d → S)
    (ha : ∀ i, IsNilpotent (a i)) (r : R) :
    nilEval φ a ha (MvPowerSeries.C r) = φ r := by
  let : UniformSpace R := ⊥
  let : UniformSpace S := ⊥
  unfold nilEval
  rw [MvPowerSeries.coe_eval₂Hom]
  exact MvPowerSeries.eval₂_C φ a r

@[simp] theorem nilEval_X {d : ℕ} (φ : R →+* S) (a : Fin d → S)
    (ha : ∀ i, IsNilpotent (a i)) (i : Fin d) :
    nilEval φ a ha (MvPowerSeries.X i) = a i := by
  let : UniformSpace R := ⊥
  let : UniformSpace S := ⊥
  unfold nilEval
  rw [MvPowerSeries.coe_eval₂Hom]
  exact MvPowerSeries.eval₂_X φ a i

/-- Coefficient-preserving evaluation into an R-algebra. -/
noncomputable def nilAeval [Algebra R S] {d : ℕ} (a : Fin d → S)
    (ha : ∀ i, IsNilpotent (a i)) : MvPowerSeries (Fin d) R →ₐ[R] S where
  __ := nilEval (algebraMap R S) a ha
  commutes' r := nilEval_C _ a ha r

@[simp] theorem nilAeval_X [Algebra R S] {d : ℕ} (a : Fin d → S)
    (ha : ∀ i, IsNilpotent (a i)) (i : Fin d) :
    nilAeval (R := R) a ha (MvPowerSeries.X i) = a i := nilEval_X (algebraMap R S) a ha i

/-- Parameter images determine the actual algebra map, not a separately
postulated equivalence. -/
theorem nilpotent_algHom_ext [Algebra R S] {d : ℕ}
    (f g : MvPowerSeries (Fin d) R →ₐ[R] S)
    (hX : ∀ i, f (MvPowerSeries.X i) = g (MvPowerSeries.X i))
    (hnil : ∀ i, IsNilpotent (f (MvPowerSeries.X i))) : f = g := by
  have H := nilpotent_hom_ext d f.toRingHom g.toRingHom
    (fun r => (f.commutes r).trans (g.commutes r).symm) hX hnil
  ext p
  exact congrArg (fun h : MvPowerSeries (Fin d) R →+* S => h p) H

/-- Exact universal property for nilpotent parameter images. -/
noncomputable def nilpotentParameterEquiv [Algebra R S] (d : ℕ) :
    {f : MvPowerSeries (Fin d) R →ₐ[R] S // ∀ i, IsNilpotent (f (MvPowerSeries.X i))} ≃
    (Fin d → {x : S // IsNilpotent x}) where
  toFun f i := ⟨f.val (MvPowerSeries.X i), f.property i⟩
  invFun a := ⟨nilAeval (fun i => (a i).val) (fun i => (a i).property), by
    intro i; simpa using (a i).property⟩
  left_inv f := by
    apply Subtype.ext
    apply nilpotent_algHom_ext
    · simp
    · simpa using f.property
  right_inv a := by
    funext i
    exact Subtype.ext (by simp)

end PaperX.FormalCharts
