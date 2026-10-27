module
public import KnillLaflammeSufficiency
import all KnillLaflammeSufficiency
public import Mathlib.Data.Matrix.Basis
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII fifth block.
Necessity via a rank-one Gram rigidity argument on actual finite Kraus maps.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.KnillLaflamme
open scoped BigOperators ComplexOrder
open Matrix

/-- Every row of a matrix with a rank-one Gram matrix is proportional to its generator. -/
theorem rank_one_gram_rigidity {q J : Type*} [Fintype q] [DecidableEq q]
    [Fintype J] [DecidableEq J] (A : Matrix J q ℂ) (p : q → ℂ)
    (hgram : A.conjTranspose*A = Matrix.vecMulVec (star p) p) :
    ∃ z : J → ℂ, ∀ j t, A j t = z j*p t := by
  by_cases hp : p=0
  · have hA : A=0 := Matrix.conjTranspose_mul_self_eq_zero.mp (by simpa [hp] using hgram)
    exact ⟨fun _ => 0, by simp [hA]⟩
  · obtain ⟨t,ht⟩ : ∃ t, p t ≠ 0 := Function.ne_iff.mp hp
    refine ⟨fun j => A j t / p t, ?_⟩
    intro j s
    let v : q → ℂ := Pi.single s (p t) - Pi.single t (p s)
    have hpv : p ⬝ᵥ v = 0 := by
      simp [v, dotProduct_sub, dotProduct_single, mul_comm]
    have hav : A *ᵥ v=0 := by
      apply (Matrix.conjTranspose_mul_self_mulVec_eq_zero A v).mp
      rw [hgram]
      ext u
      change (∑ x, star (p u) * p x * v x) = 0
      simp_rw [mul_assoc]
      rw [← Finset.mul_sum]
      change star (p u) * (p ⬝ᵥ v) = 0
      rw [hpv, mul_zero]
    have heq : A j s*p t - A j t*p s=0 := by
      simpa [v, Matrix.mulVec_sub, Matrix.mulVec_single, mul_comm] using congrFun hav j
    change A j s = (A j t / p t) * p s
    field_simp [ht]
    linear_combination heq


variable {n I J : Type*} [Fintype n] [DecidableEq n]
    [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]

/-- A Kraus decomposition of a rank-one operator map has proportional Kraus operators. -/
theorem kraus_rank_one_rigidity (A : J → Matrix n n ℂ) (P : Matrix n n ℂ)
    (hmap : ∀ rho, noise A rho=P*rho*star P) :
    ∃ z : J → ℂ, ∀ j, A j=z j • P := by
  let X : Matrix J (n × n) ℂ := fun j t => A j t.1 t.2
  let p : n × n → ℂ := fun t => P t.1 t.2
  have hgram : X.conjTranspose*X=Matrix.vecMulVec (star p) p := by
    ext ⟨a,b⟩ ⟨c,d⟩
    have hh := congrArg (fun M : Matrix n n ℂ => M c a) (hmap (Matrix.single d b 1))
    simpa [X, p, noise, Matrix.mul_apply, Matrix.conjTranspose_apply, Matrix.star_apply,
      Matrix.single_apply, ite_and, Matrix.sum_apply, Matrix.vecMulVec, mul_comm] using hh
  obtain ⟨z,hz⟩ := rank_one_gram_rigidity X p hgram
  refine ⟨z, fun j => ?_⟩
  ext a b
  exact hz j (a,b)

/-- Expand the corrected code map as a genuine composite Kraus family. -/
theorem corrected_kraus_family (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (R : J → Matrix n n ℂ)
    (hcorrect : ∀ rho, P*rho*P=rho → noise R (noise E rho)=rho) :
    ∃ z : J × I → ℂ, ∀ r a, R r*E a*P=z (r,a) • P := by
  have hmap (rho : Matrix n n ℂ) :
      noise (fun ra : J × I => R ra.1*E ra.2*P) rho=P*rho*star P := by
    have hrho : P*(P*rho*P)*P=P*rho*P := by
      simp only [← mul_assoc, hP.isIdempotentElem.eq]
      rw [mul_assoc (P*rho), hP.isIdempotentElem.eq]
    have heq : noise (fun ra : J × I => R ra.1*E ra.2*P) rho =
        noise R (noise E (P*rho*P)) := by
      simp only [noise, Fintype.sum_prod_type, star_mul, hP.isSelfAdjoint.star_eq,
        Finset.mul_sum, Finset.sum_mul, mul_assoc]
    rw [heq, hcorrect _ hrho, hP.isSelfAdjoint.star_eq]
  obtain ⟨z,hz⟩ := kraus_rank_one_rigidity (fun ra : J × I => R ra.1*E ra.2*P) P hmap
  exact ⟨z, fun r a => hz (r,a)⟩

/-- Necessary Knill-Laflamme Gram matrix derived from actual trace-preserving recovery. -/
theorem gram_of_recovery (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (R : J → Matrix n n ℂ)
    (hR : (∑ r, star (R r)*R r)=1)
    (hcorrect : ∀ rho, P*rho*P=rho → noise R (noise E rho)=rho) :
    ∃ C : Matrix I I ℂ, C.PosSemidef ∧
      ∀ a b, P*star (E a)*E b*P=C a b • P := by
  obtain ⟨z,hz⟩ := corrected_kraus_family P hP E R hcorrect
  let Z : Matrix J I ℂ := fun r a => z (r,a)
  refine ⟨Z.conjTranspose*Z, Matrix.posSemidef_conjTranspose_mul_self Z, ?_⟩
  intro a b
  have heq : P*star (E a)*E b*P = ∑ r, star (R r*E a*P)*(R r*E b*P) := by
    calc
      _ = P*star (E a)*(∑ r, star (R r)*R r)*E b*P := by rw [hR, mul_one]
      _ = _ := by
        simp only [Finset.mul_sum, Finset.sum_mul, star_mul,
          hP.isSelfAdjoint.star_eq, mul_assoc]
  rw [heq]
  simp_rw [hz, star_smul, hP.isSelfAdjoint.star_eq, smul_mul_assoc,
    mul_smul_comm, smul_smul, hP.isIdempotentElem.eq]
  simp only [Matrix.mul_apply, Matrix.conjTranspose_apply, Finset.sum_smul, Z]


/-- Exact correction on the code operator space by a finite trace-preserving Kraus map. -/
def Correctable (P : Matrix n n ℂ) (E : I → Matrix n n ℂ) : Prop :=
  ∃ m : ℕ, ∃ R : Fin m → Matrix n n ℂ,
    (∑ r, star (R r)*R r)=1 ∧
    ∀ rho, P*rho*P=rho → noise R (noise E rho)=rho

/-- Finite Knill-Laflamme necessary-and-sufficient criterion for a Kraus channel. -/
theorem correctable_iff_gram (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (hE : (∑ a, star (E a)*E a)=1) :
    Correctable P E ↔ ∃ C : Matrix I I ℂ, C.PosSemidef ∧
      ∀ a b, P*star (E a)*E b*P=C a b • P := by
  constructor
  · rintro ⟨m,R,hR,hcorrect⟩
    exact gram_of_recovery P hP E R hR hcorrect
  · rintro ⟨C,hC,hgram⟩
    let K : Data n I := ⟨P,hP,E,C,hC,hgram⟩
    obtain ⟨R,hR,hcorrect⟩ := K.exists_recovery hE
    let e := Fintype.equivFin (Option K.diagonal.Active)
    refine ⟨Fintype.card (Option K.diagonal.Active), fun r => R (e.symm r), ?_, ?_⟩
    · exact (e.symm.sum_comp (fun a => star (R a)*R a)).trans hR
    · intro rho hrho
      change (∑ r, R (e.symm r)*noise E rho*star (R (e.symm r)))=rho
      exact (e.symm.sum_comp (fun a => R a*noise E rho*star (R a))).trans (hcorrect rho hrho)

/-- Failure of scalar Gram compression is a certified obstruction to any exact recovery. -/
theorem not_correctable_of_nonscalar (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (hE : (∑ a, star (E a)*E a)=1)
    (a b : I) (hab : ∀ c : ℂ, P*star (E a)*E b*P ≠ c • P) :
    ¬ Correctable P E := by
  intro hc
  obtain ⟨C,_,hgram⟩ := (correctable_iff_gram P hP E hE).mp hc
  exact hab (C a b) (hgram a b)

/-- Cross-error terms are scalar after the very same recovery, not a newly chosen decoder. -/
theorem recovery_cross_from_scalar (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (R : J → Matrix n n ℂ) (z : J × I → ℂ)
    (hz : ∀ r a, R r*E a*P=z (r,a) • P)
    (rho : Matrix n n ℂ) (hrho : P*rho*P=rho) (a b : I) :
    noise R (E a*rho*star (E b)) = (∑ r, z (r,a)*star (z (r,b))) • rho := by
  have heq (r : J) : R r*(E a*rho*star (E b))*star (R r) =
      (R r*E a*P)*rho*star (R r*E b*P) := by
    rw [star_mul, star_mul, hP.isSelfAdjoint.star_eq]
    calc
      _ = (R r*E a)*(P*rho*P)*(star (E b)*star (R r)) := by rw [hrho]; noncomm_ring
      _ = _ := by noncomm_ring
  simp only [noise, heq, hz, star_smul, hP.isSelfAdjoint.star_eq,
    smul_mul_assoc, mul_smul_comm, smul_smul, hrho, Finset.sum_smul]
  apply Finset.sum_congr rfl
  intro r _
  rw [mul_comm]

end KomorebiPaperVII.KnillLaflamme

/-! Complete declaration-level trust audit. -/
#print axioms KomorebiPaperVII.KnillLaflamme.rank_one_gram_rigidity
#print axioms KomorebiPaperVII.KnillLaflamme.kraus_rank_one_rigidity
#print axioms KomorebiPaperVII.KnillLaflamme.corrected_kraus_family
#print axioms KomorebiPaperVII.KnillLaflamme.gram_of_recovery
#print axioms KomorebiPaperVII.KnillLaflamme.correctable_iff_gram
#print axioms KomorebiPaperVII.KnillLaflamme.not_correctable_of_nonscalar
#print axioms KomorebiPaperVII.KnillLaflamme.recovery_cross_from_scalar
