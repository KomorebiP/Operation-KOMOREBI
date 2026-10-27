module
public import PolynomialLocalInverse
public import PolynomialParameterSystem

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialParameterChart
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialPadicLift Komorebi.PolynomialPadicUnique
open Komorebi.PolynomialLocalSurjective Komorebi.PolynomialLocalInverse
open Komorebi.PolynomialParameterSystem
variable {e q : ℕ}

/-- The target with zero polynomial residual and the prescribed free coordinates. -/
def chartTarget (p L : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (t : residueBall p L (freePart x)) :
    residueBall p L (evalSystem (augmented F) x) :=
  ⟨join 0 t.val, by
    intro i
    refine Fin.addCases (fun j => ?_) (fun j => ?_) i
    · simpa only [join_solved, Pi.zero_apply, evalSystem_augmented, zero_sub] using
        dvd_neg.mpr ((int_pow_dvd_iff p L _).mp (hx j))
    · simpa only [evalSystem_augmented, join_free] using t.property j⟩

theorem continuous_chartTarget (p L : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i) :
    Continuous (chartTarget p L F x hx) := by
  apply Continuous.subtype_mk
  exact continuous_join.comp (continuous_const.prodMk continuous_subtype_val)

def chartPoint (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : residueBall p L (freePart x)) : residueBall p L x :=
  (localHomeomorph p L hL (augmented F) x
    (augmented_jacobian_surjective p F x hJ)).symm (chartTarget p L F x hx t)

theorem chartPoint_spec (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : residueBall p L (freePart x)) :
    padicEval p F (chartPoint p L hL F x hx hJ t).val = 0 ∧
      freePart (chartPoint p L hL F x hx hJ t).val = t.val := by
  apply (padicEval_augmented_iff p F _ t.val).mp
  exact localHomeomorph_symm_eval p L hL (augmented F) x
    (augmented_jacobian_surjective p F x hJ) (chartTarget p L F x hx t)

theorem chartPoint_root (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : residueBall p L (freePart x)) :
    padicEval p F (chartPoint p L hL F x hx hJ t).val = 0 :=
  (chartPoint_spec p L hL F x hx hJ t).1

theorem chartPoint_free (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : residueBall p L (freePart x)) :
    freePart (chartPoint p L hL F x hx hJ t).val = t.val :=
  (chartPoint_spec p L hL F x hx hJ t).2

theorem chartPoint_unique (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : residueBall p L (freePart x)) (z : residueBall p L x)
    (hz : padicEval p F z.val = 0) (ht : freePart z.val = t.val) :
    z = chartPoint p L hL F x hx hJ t := by
  apply (localHomeomorph p L hL (augmented F) x
    (augmented_jacobian_surjective p F x hJ)).injective
  apply Subtype.ext
  change padicEval p (augmented F) z.val =
    padicEval p (augmented F) (chartPoint p L hL F x hx hJ t).val
  rw [padicEval_augmented, padicEval_augmented, hz, ht,
    chartPoint_root, chartPoint_free]

theorem continuous_chartPoint (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x)) :
    Continuous (chartPoint p L hL F x hx hJ) :=
  (localHomeomorph p L hL (augmented F) x
    (augmented_jacobian_surjective p F x hJ)).symm.continuous.comp
      (continuous_chartTarget p L F x hx)

theorem chartPoint_congruent (p L N : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t u : residueBall p L (freePart x))
    (htu : ∀ j, (p : ℤ_[p])^N ∣ t.val j - u.val j) :
    ∀ i, (p : ℤ_[p])^N ∣ (chartPoint p L hL F x hx hJ t).val i -
      (chartPoint p L hL F x hx hJ u).val i := by
  apply localHomeomorph_symm_congruent p L N hL (augmented F) x
    (augmented_jacobian_surjective p F x hJ)
  intro i
  change (p : ℤ_[p])^N ∣ join (0 : Fin e → ℤ_[p]) t.val i - join 0 u.val i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i
  · simp only [join_solved, sub_self, dvd_zero]
  · simpa only [join_free] using htu j

def chartPhi (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : residueBall p L (freePart x)) : Fin e → ℤ_[p] :=
  solvedPart (chartPoint p L hL F x hx hJ t).val

theorem continuous_chartPhi (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x)) :
    Continuous (chartPhi p L hL F x hx hJ) :=
  continuous_solvedPart.comp (continuous_subtype_val.comp
    (continuous_chartPoint p L hL F x hx hJ))

theorem chartPoint_graph (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : residueBall p L (freePart x)) :
    join (chartPhi p L hL F x hx hJ t) t.val =
      (chartPoint p L hL F x hx hJ t).val := by
  rw [← chartPoint_free p L hL F x hx hJ t]
  exact join_parts _

theorem chartGraph_iff (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : residueBall p L (freePart x)) (z : residueBall p L x) :
    (padicEval p F z.val = 0 ∧ freePart z.val = t.val) ↔
      z.val = join (chartPhi p L hL F x hx hJ t) t.val := by
  rw [chartPoint_graph]
  constructor
  · rintro ⟨hz, ht⟩
    exact congrArg Subtype.val (chartPoint_unique p L hL F x hx hJ t z hz ht)
  · intro h
    rw [h]
    exact chartPoint_spec p L hL F x hx hJ t

theorem chartPoint_congruent_iff (p L N : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t u : residueBall p L (freePart x)) :
    (∀ j, (p : ℤ_[p])^N ∣ t.val j - u.val j) ↔
      (∀ i, (p : ℤ_[p])^N ∣ (chartPoint p L hL F x hx hJ t).val i -
        (chartPoint p L hL F x hx hJ u).val i) := by
  constructor
  · exact chartPoint_congruent p L N hL F x hx hJ t u
  · intro h j
    have ht := congrFun (chartPoint_free p L hL F x hx hJ t) j
    have hu := congrFun (chartPoint_free p L hL F x hx hJ u) j
    simpa only [freePart] using (ht ▸ hu ▸ h (Fin.natAdd e j))

/-- The whole root locus is continuously and uniquely parameterized by its free coordinates. -/
def parameterHomeomorph (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x)) :
    residueBall p L (freePart x) ≃ₜ {z : residueBall p L x // padicEval p F z.val = 0} where
  toFun t := ⟨chartPoint p L hL F x hx hJ t, chartPoint_root p L hL F x hx hJ t⟩
  invFun z := ⟨freePart z.val.val, fun j => z.val.property (Fin.natAdd e j)⟩
  left_inv t := Subtype.ext (chartPoint_free p L hL F x hx hJ t)
  right_inv z := by
    apply Subtype.ext
    exact (chartPoint_unique p L hL F x hx hJ _ z.val z.property rfl).symm
  continuous_toFun := by
    apply Continuous.subtype_mk
    exact continuous_chartPoint p L hL F x hx hJ
  continuous_invFun := by
    apply Continuous.subtype_mk
    exact continuous_freePart.comp (continuous_subtype_val.comp continuous_subtype_val)

#print axioms chartTarget
#print axioms continuous_chartTarget
#print axioms chartPoint
#print axioms chartPoint_spec
#print axioms chartPoint_root
#print axioms chartPoint_free
#print axioms chartPoint_unique
#print axioms continuous_chartPoint
#print axioms chartPoint_congruent
#print axioms chartPhi
#print axioms continuous_chartPhi
#print axioms chartPoint_graph
#print axioms chartGraph_iff
#print axioms chartPoint_congruent_iff
#print axioms parameterHomeomorph

end Komorebi.PolynomialParameterChart
