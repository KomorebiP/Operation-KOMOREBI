import PaperX.CompletionBoundary
import Mathlib.RingTheory.Ideal.Quotient.Index

/-! Concrete populated representation forests. The example fixes a cyclic group
of order two and a characteristic polynomial, rather than defining an abstract
realization map as an assumption. Finite-level matrices may have multiple lifts. -/
set_option autoImplicit false
namespace PaperX.CompletionExamples
open scoped Matrix
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationForests
abbrev C2 := Multiplicative (ZMod 2)
instance c2Topology : TopologicalSpace C2 := ⊥
instance c2Discrete : DiscreteTopology C2 := ⟨rfl⟩

def signValue (g : C2) : ℤ := if g.toAdd = 0 then 1 else -1

theorem sign_one : signValue 1 = 1 := by decide +kernel

theorem sign_mul : ∀ g h : C2, signValue (g*h) = signValue g * signValue h := by
  decide +kernel

def signRep : MatrixRep ℤ C2 (Fin 2) where
  toFun g := !![1,0;0,signValue g]
  map_one' := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [sign_one]
  map_mul' g h := by
    ext i j
    fin_cases i <;> fin_cases j <;>
      simp [Matrix.mul_apply, Fin.sum_univ_succ, sign_mul]

def generator : C2 := Multiplicative.ofAdd 1

theorem integer_charpoly : (signRep generator).charpoly = Polynomial.X^2 - 1 := by
  rw [Matrix.charpoly_fin_two]
  norm_num [signRep, signValue, generator, Matrix.trace, Fin.sum_univ_succ, Matrix.det_fin_two]
  ring

variable {R : Type} [CommRing R] (I : Ideal R)

noncomputable def target : Polynomial R := Polynomial.X^2 - 1

/-- All actual C2 representations with the prescribed generator polynomial. -/
def involutionConditions : Conditions (G := C2) (ι := Fin 2) I where
  allowed k ρ := (ρ generator).charpoly = (target (R := R)).map (Ideal.Quotient.mk (I^k))
  downward := by
    intro j k hjk ρ hρ
    change ((ρ generator).map (Ideal.Quotient.factorPow I hjk)).charpoly = _
    rw [Matrix.charpoly_map, hρ, Polynomial.map_map]
    simp

/-- Every precision is populated by an actual reduced sign representation. -/
theorem involution_levels_nonempty (k : ℕ) :
    ∃ ρ, (involutionConditions I).allowed k ρ := by
  refine ⟨changeCoefficients (Int.castRingHom (R ⧸ I^k)) signRep, ?_⟩
  change ((signRep generator).map (Int.castRingHom (R ⧸ I^k))).charpoly =
    (target (R := R)).map (Ideal.Quotient.mk (I^k))
  rw [Matrix.charpoly_map, integer_charpoly]
  simp [target]

/-- Unlike arbitrary profinite source groups, this finite source makes the set
of all finite-matrix representations finite. -/
theorem involution_levels_finite (hI : I.FG) [Finite (R ⧸ I)] (k : ℕ) :
    Finite {ρ : MatrixRep (R ⧸ I^k) C2 (Fin 2) // (involutionConditions I).allowed k ρ} := by
  let : Finite (R ⧸ I^k) := Ideal.finite_quotient_pow hI k
  let : Finite (MatrixRep (R ⧸ I^k) C2 (Fin 2)) :=
    Finite.of_injective (fun ρ : MatrixRep (R ⧸ I^k) C2 (Fin 2) => (ρ : C2 → _))
      DFunLike.coe_injective
  infer_instance

/-- This instantiates the representation-forest existence theorem, including
continuity and the recovered full characteristic polynomial. -/
theorem involution_forest_realized [IsAdicComplete I R] (hI : I.FG) [Finite (R ⧸ I)] :
    ∃ ρ : MatrixRep R C2 (Fin 2),
      Realizes I (involutionConditions I) ρ ∧ AdicRepContinuous I ρ ∧
      (ρ generator).charpoly = target := by
  obtain ⟨ρ,hρ,hc⟩ := exists_continuous_realization I (involutionConditions I)
    (involution_levels_finite I hI) (involution_levels_nonempty I)
    (fun _ τ _ i j g => by simp [nhds_discrete])
  refine ⟨ρ,hρ,hc,?_⟩
  exact PaperX.CommonSpine.charpoly_detected I ρ generator target hρ

/-- Concrete actual 3-adic realization of the complete-ring hypotheses. -/
instance threePrime : Fact (Nat.Prime 3) := ⟨by norm_num⟩
instance threeResidueFinite : Finite (ℤ_[3] ⧸ IsLocalRing.maximalIdeal ℤ_[3]) :=
  Finite.of_equiv (ZMod 3) (PadicInt.residueField (p := 3)).symm.toEquiv

theorem actual_three_adic_forest :
    ∃ ρ : MatrixRep ℤ_[3] C2 (Fin 2),
      Realizes (IsLocalRing.maximalIdeal ℤ_[3])
        (involutionConditions (IsLocalRing.maximalIdeal ℤ_[3])) ρ ∧
      AdicRepContinuous (IsLocalRing.maximalIdeal ℤ_[3]) ρ ∧
      (ρ generator).charpoly = Polynomial.X^2-1 := by
  exact involution_forest_realized _ (IsNoetherian.noetherian _)

/-- The reconstructed polynomial rules out the identity generator in char. zero. -/
theorem nontrivial_generator [CharZero R] (ρ : MatrixRep R C2 (Fin 2))
    (hρ : (ρ generator).charpoly = Polynomial.X^2-1) : ρ generator ≠ 1 := by
  intro h
  have H := congrArg (fun p : Polynomial R => p.coeff 0) hρ
  rw [h, Matrix.charpoly_fin_two] at H
  norm_num at H

end PaperX.CompletionExamples
