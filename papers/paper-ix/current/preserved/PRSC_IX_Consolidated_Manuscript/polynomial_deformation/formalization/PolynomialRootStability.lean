module
public import PolynomialPadicUnique
public import PolynomialCoefficientPerturbation

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialRootStability
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialPadicLift Komorebi.PolynomialPadicUnique
open Komorebi.PolynomialCoefficientPerturbation Komorebi.PolynomialSurjectiveStep
variable {d e : ℕ}

/-- Two integer representatives of the same p-adic residue are congruent as integers. -/
theorem integer_congruent_of_common_padic (p n : ℕ) [Fact (Nat.Prime p)]
    (a : ℤ_[p]) (x y : ℤ)
    (hx : (p : ℤ_[p])^n ∣ a - (x : ℤ_[p]))
    (hy : (p : ℤ_[p])^n ∣ a - (y : ℤ_[p])) :
    (p : ℤ)^n ∣ x - y := by
  apply (int_pow_dvd_iff p n (x-y)).mpr
  have h := dvd_sub hy hx
  simpa only [sub_sub_sub_cancel_left, Int.cast_sub] using h

/-- A smooth exact p-adic root has a nearby root after any sufficiently divisible
integer coefficient perturbation. The system may be rectangular. -/
theorem exists_nearby_perturbed_root (p M : ℕ) [Fact (Nat.Prime p)] (hM : 1 ≤ M)
    (c : ℤ) (hc : (p : ℤ)^M ∣ c)
    (F H : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (a : Fin d → ℤ_[p]) (ha : ∀ i, padicEval p F a i = 0)
    (hax : ∀ i, (p : ℤ_[p]) ∣ a i - (x i : ℤ_[p])) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, padicEval p (perturb c F H) b i = 0) ∧
      (∀ i, (p : ℤ_[p])^M ∣ b i - a i) := by
  let y := truncInt p M a
  have hy : ∀ i, (p : ℤ)^M ∣ evalSystem F y i := truncInt_root p M F a ha
  have hay : ∀ i, (p : ℤ_[p])^M ∣ a i - (y i : ℤ_[p]) :=
    truncInt_precision p M a
  have hyx : ∀ i, (p : ℤ) ∣ y i - x i := by
    intro i
    have hy1 : (p : ℤ_[p])^1 ∣ a i - (y i : ℤ_[p]) :=
      (pow_dvd_pow (p : ℤ_[p]) hM).trans (hay i)
    simpa only [pow_one] using integer_congruent_of_common_padic p 1 (a i) (y i) (x i)
      hy1 (by simpa only [pow_one] using hax i)
  have hJy : Function.Surjective (digitJacobian p F y) := by
    rw [digitJacobian_eq p F x y hyx]
    exact hJ
  obtain ⟨b, hb, hby⟩ := exists_padic_root_perturb p M hM c hc F H y hy hJy
  refine ⟨b, hb, ?_⟩
  intro i
  have h := dvd_sub (hby i) (hay i)
  simpa only [sub_sub_sub_cancel_right] using h

/-- In a smooth square residue ball, every selected root of F+cH agrees with
the original root to the full coefficient-perturbation precision. -/
theorem perturbed_roots_congruent (p L M : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (hLM : L ≤ M) (c : ℤ) (hc : (p : ℤ)^M ∣ c)
    (F H : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (a b : Fin d → ℤ_[p])
    (ha : ∀ i, padicEval p F a i = 0)
    (hb : ∀ i, padicEval p (perturb c F H) b i = 0)
    (hax : ∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p]))
    (hbx : ∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) :
    ∀ i, (p : ℤ_[p])^M ∣ b i - a i := by
  have hM : 1 ≤ M := hL.trans hLM
  have hax1 : ∀ i, (p : ℤ_[p]) ∣ a i - (x i : ℤ_[p]) := by
    intro i
    exact (dvd_pow_self (p : ℤ_[p]) (by omega : L ≠ 0)).trans (hax i)
  obtain ⟨b', hb', hb'a⟩ := exists_nearby_perturbed_root p M hM c hc F H x hJ a ha hax1
  have hb'x : ∀ i, (p : ℤ_[p])^L ∣ b' i - (x i : ℤ_[p]) := by
    intro i
    have h := dvd_add ((pow_dvd_pow (p : ℤ_[p]) hLM).trans (hb'a i)) (hax i)
    simpa only [sub_add_sub_cancel] using h
  have hp : (p : ℤ) ∣ c := (dvd_pow_self (p : ℤ) (by omega : M ≠ 0)).trans hc
  have hJG : Function.Surjective (digitJacobian p (perturb c F H) x) := by
    rw [digitJacobian_perturb_eq p c hp F H x]
    exact hJ
  have heq := padic_root_unique p L hL (perturb c F H) x hJG b b' hb hb' hbx hb'x
  simpa only [heq] using hb'a

/-- The perturbed square root exists uniquely in the original residue ball,
and retains the entire coefficient-perturbation precision around the original root. -/
theorem exists_unique_nearby_perturbed_root (p L M : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (hLM : L ≤ M) (c : ℤ) (hc : (p : ℤ)^M ∣ c)
    (F H : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (a : Fin d → ℤ_[p]) (ha : ∀ i, padicEval p F a i = 0)
    (hax : ∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) :
    ∃! b : Fin d → ℤ_[p],
      (∀ i, padicEval p (perturb c F H) b i = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) ∧
      (∀ i, (p : ℤ_[p])^M ∣ b i - a i) := by
  have hax1 : ∀ i, (p : ℤ_[p]) ∣ a i - (x i : ℤ_[p]) := by
    intro i
    exact (dvd_pow_self (p : ℤ_[p]) (by omega : L ≠ 0)).trans (hax i)
  obtain ⟨b, hb, hba⟩ := exists_nearby_perturbed_root p M (hL.trans hLM) c hc
    F H x hJ a ha hax1
  have hbx : ∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p]) := by
    intro i
    have h := dvd_add ((pow_dvd_pow (p : ℤ_[p]) hLM).trans (hba i)) (hax i)
    simpa only [sub_add_sub_cancel] using h
  refine ⟨b, ⟨hb, hbx, hba⟩, ?_⟩
  intro b' hb'
  have hp : (p : ℤ) ∣ c := (dvd_pow_self (p : ℤ) (by omega : M ≠ 0)).trans hc
  have hJG : Function.Surjective (digitJacobian p (perturb c F H) x) := by
    rw [digitJacobian_perturb_eq p c hp F H x]
    exact hJ
  exact padic_root_unique p L hL (perturb c F H) x hJG b' b hb'.1 hb hb'.2.1 hbx

/-- Starting only with a lower square root, construct the original root and
the uniquely determined nearby perturbed root, including the full displacement bound. -/
theorem exists_root_and_unique_perturbation (p L M : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (hLM : L ≤ M) (c : ℤ) (hc : (p : ℤ)^M ∣ c)
    (F H : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃ a : Fin d → ℤ_[p],
      (∀ i, padicEval p F a i = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) ∧
      ∃! b : Fin d → ℤ_[p],
        (∀ i, padicEval p (perturb c F H) b i = 0) ∧
        (∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) ∧
        (∀ i, (p : ℤ_[p])^M ∣ b i - a i) := by
  obtain ⟨a, ha, hax⟩ := exists_padic_root p L hL F x hx hJ
  exact ⟨a, ha, hax, exists_unique_nearby_perturbed_root p L M hL hLM c hc F H x hJ a ha hax⟩

end Komorebi.PolynomialRootStability
