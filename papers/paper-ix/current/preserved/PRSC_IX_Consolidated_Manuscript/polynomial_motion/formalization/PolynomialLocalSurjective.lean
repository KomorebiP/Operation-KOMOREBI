module
public import PolynomialPadicUnique
public import Mathlib.NumberTheory.Padics.ProperSpace

@[expose] public section
noncomputable section
set_option autoImplicit false

open Filter Topology

namespace Komorebi.PolynomialLocalSurjective
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialPadicLift Komorebi.PolynomialPadicUnique

variable {d e : ℕ}

/-- The actual p-adic residue ball about an integer vector. -/
def residueBall (p L : ℕ) [Fact (Nat.Prime p)] (x : Fin d → ℤ) :
    Set (Fin d → ℤ_[p]) :=
  {a | ∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])}

theorem isClosed_residueBall (p L : ℕ) [Fact (Nat.Prime p)] (x : Fin d → ℤ) :
    IsClosed (residueBall p L x) := by
  simp only [residueBall, ← Ideal.mem_span_singleton,
    ← PadicInt.norm_le_pow_iff_mem_span_pow, Set.ofPred_forall]
  exact isClosed_iInter (fun i =>
    isClosed_le (((continuous_apply i).sub continuous_const).norm) continuous_const)

theorem isCompact_residueBall (p L : ℕ) [Fact (Nat.Prime p)] (x : Fin d → ℤ) :
    IsCompact (residueBall p L x) :=
  (isClosed_residueBall p L x).isCompact

/-- All canonical integer truncations converge to the original p-adic vector. -/
theorem truncInt_tendsto (p L : ℕ) [Fact (Nat.Prime p)] (t : Fin d → ℤ_[p]) :
    Tendsto (fun n i => (truncInt p (L+n) t i : ℤ_[p])) atTop (𝓝 t) := by
  apply tendsto_pi_nhds.mpr
  intro i
  rw [Metric.tendsto_atTop]
  intro ε hε
  obtain ⟨N, hN⟩ := PadicInt.exists_pow_neg_lt p hε
  refine ⟨N, ?_⟩
  intro n hn
  have hd : (p : ℤ_[p])^N ∣ t i - (truncInt p (L+n) t i : ℤ_[p]) :=
    dvd_trans (pow_dvd_pow (p : ℤ_[p]) (by omega)) (truncInt_precision p (L+n) t i)
  have hb := (PadicInt.norm_le_pow_iff_mem_span_pow
    (t i - (truncInt p (L+n) t i : ℤ_[p])) N).mpr
    (Ideal.mem_span_singleton.mpr hd)
  rw [dist_comm, dist_eq_norm]
  exact lt_of_le_of_lt hb hN

/-- Subtracting a constant target does not alter the actual reduced Jacobian. -/
theorem digitJacobian_sub_C (q : ℕ) (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x : Fin d → ℤ) (y : Fin e → ℤ) :
    digitJacobian q (fun i => F i - MvPolynomial.C (y i)) x =
      digitJacobian q F x := by
  ext u i
  simp [digitJacobian]

/-- Every sufficiently close integer output has a p-adic preimage in the base ball. -/
theorem exists_integer_target_preimage (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) (y : Fin e → ℤ)
    (hy : ∀ i, (p : ℤ)^L ∣ y i - evalSystem F x i) :
    ∃ a : Fin d → ℤ_[p], padicEval p F a = (fun i => (y i : ℤ_[p])) ∧
      a ∈ residueBall p L x := by
  have hx : ∀ i, (p : ℤ)^L ∣
      evalSystem (fun i => F i - MvPolynomial.C (y i)) x i := by
    intro i
    simpa only [evalSystem, MvPolynomial.eval_sub, MvPolynomial.eval_C, neg_sub] using
      (dvd_neg.mpr (hy i))
  have hJ' : Function.Surjective
      (digitJacobian p (fun i => F i - MvPolynomial.C (y i)) x) := by
    rw [digitJacobian_sub_C]
    exact hJ
  obtain ⟨a, ha, hax⟩ := exists_padic_root p L hL
    (fun i => F i - MvPolynomial.C (y i)) x hx hJ'
  refine ⟨a, ?_, hax⟩
  funext i
  have hi := ha i
  rw [MvPolynomial.eval₂_sub, MvPolynomial.eval₂_C] at hi
  exact sub_eq_zero.mp hi

/-- The compact image contains every p-adic output in the corresponding residue ball.
Integer truncations are used only as output approximations, so no compatibility
of chosen preimages is assumed. -/
theorem exists_padic_preimage (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) (t : Fin e → ℤ_[p])
    (ht : ∀ i, (p : ℤ_[p])^L ∣ t i - (evalSystem F x i : ℤ_[p])) :
    ∃ a : Fin d → ℤ_[p], padicEval p F a = t ∧ a ∈ residueBall p L x := by
  have hcont : Continuous (padicEval p F) := continuous_pi (continuous_padicEval p F)
  have hclosed : IsClosed (padicEval p F '' residueBall p L x) :=
    ((isCompact_residueBall p L x).image hcont).isClosed
  have hmem : ∀ n, (fun i => (truncInt p (L+n) t i : ℤ_[p])) ∈
      padicEval p F '' residueBall p L x := by
    intro n
    have hy : ∀ i, (p : ℤ)^L ∣ truncInt p (L+n) t i - evalSystem F x i := by
      intro i
      apply (int_pow_dvd_iff p L _).mpr
      have hd := dvd_trans (pow_dvd_pow (p : ℤ_[p]) (Nat.le_add_right L n))
        (truncInt_precision p (L+n) t i)
      simpa only [Int.cast_sub, sub_sub_sub_cancel_left] using dvd_sub (ht i) hd
    obtain ⟨a, ha, hax⟩ := exists_integer_target_preimage p L hL F x hJ
      (truncInt p (L+n) t) hy
    exact ⟨a, hax, ha⟩
  have htarget := hclosed.mem_of_tendsto (truncInt_tendsto p L t) (Eventually.of_forall hmem)
  obtain ⟨a, hax, ha⟩ := htarget
  exact ⟨a, ha, hax⟩

#print axioms residueBall
#print axioms isClosed_residueBall
#print axioms isCompact_residueBall
#print axioms truncInt_tendsto
#print axioms digitJacobian_sub_C
#print axioms exists_integer_target_preimage
#print axioms exists_padic_preimage

end Komorebi.PolynomialLocalSurjective
