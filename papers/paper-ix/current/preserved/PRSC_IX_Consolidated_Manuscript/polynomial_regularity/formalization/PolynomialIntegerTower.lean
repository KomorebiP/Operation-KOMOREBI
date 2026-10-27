module
public import PolynomialSurjectiveStep

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialIntegerTower
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialSurjectiveStep
variable {d e : ℕ}

/-- Surjectivity of the actual reduced Jacobian produces a single compatible
sequence of integer polynomial solutions at every higher precision. The initial
point is kept exactly, and no primality assumption on the positive base is needed. -/
theorem exists_compatible_tower (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian q F x)) :
    ∃ z : ℕ → Fin d → ℤ,
      z 0 = x ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ evalSystem F (z n) i) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ (z (n+1) - z n) i) ∧
      (∀ n, Function.Surjective (digitJacobian q F (z n))) := by
  let State (n : ℕ) :=
    {y : Fin d → ℤ // (∀ i, (q : ℤ)^(L+n) ∣ evalSystem F y i) ∧
      Function.Surjective (digitJacobian q F y)}
  have advance (n : ℕ) (y : State n) :
      ∃ w : State (n+1), ∀ i, (q : ℤ)^(L+n) ∣ (w.val - y.val) i := by
    obtain ⟨w, hcong, hroot, hsurj⟩ :=
      one_step_lift q (L+n) hq (by omega) F y.val y.property.1 y.property.2
    refine ⟨⟨w, ?_, hsurj⟩, hcong⟩
    simpa only [Nat.add_assoc] using hroot
  let next (n : ℕ) (y : State n) : State (n+1) := Classical.choose (advance n y)
  let initial : State 0 := ⟨x, by simpa only [Nat.add_zero] using hx, hJ⟩
  let state : (n : ℕ) → State n := fun n => Nat.rec initial (fun k y => next k y) n
  refine ⟨fun n => (state n).val, rfl, ?_, ?_, ?_⟩
  · exact fun n => (state n).property.1
  · intro n
    exact Classical.choose_spec (advance n (state n))
  · exact fun n => (state n).property.2

/-- Adjacent compatibility implies compatibility between any two levels,
with the modulus at the earlier level. -/
theorem tower_pairwise_congruent (q L : ℕ) (z : ℕ → Fin d → ℤ)
    (hstep : ∀ n i, (q : ℤ)^(L+n) ∣ (z (n+1) - z n) i)
    (m n : ℕ) (hmn : m ≤ n) :
    ∀ i, (q : ℤ)^(L+m) ∣ (z n - z m) i := by
  induction n, hmn using Nat.le_induction with
  | base =>
    intro i
    simp
  | succ n hmn ih =>
    intro i
    have hs : (q : ℤ)^(L+m) ∣ (z (n+1) - z n) i :=
      dvd_trans (pow_dvd_pow (q : ℤ) (Nat.add_le_add_left hmn L)) (hstep n i)
    have hsum := dvd_add hs (ih i)
    simpa only [Pi.sub_apply, sub_add_sub_cancel] using hsum

/-- Every level of a compatible integer tower retains the initial residue. -/
theorem tower_initial_congruent (q L : ℕ) (z : ℕ → Fin d → ℤ)
    (hstep : ∀ n i, (q : ℤ)^(L+n) ∣ (z (n+1) - z n) i)
    (n : ℕ) : ∀ i, (q : ℤ)^L ∣ (z n - z 0) i := by
  simpa only [Nat.add_zero] using
    tower_pairwise_congruent q L z hstep 0 n (Nat.zero_le n)

/-- Along a positive-depth compatible tower, the finite-ring Jacobian itself
is constant, rather than only its rank or its surjectivity. -/
theorem tower_digitJacobian_eq (q L : ℕ) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (z : ℕ → Fin d → ℤ)
    (hstep : ∀ n i, (q : ℤ)^(L+n) ∣ (z (n+1) - z n) i)
    (n : ℕ) : digitJacobian q F (z n) = digitJacobian q F (z 0) := by
  apply digitJacobian_eq
  intro i
  exact dvd_trans (dvd_pow_self (q : ℤ) (by omega : L ≠ 0))
    (tower_initial_congruent q L z hstep n i)

/-- The strengthened tower certificate includes all cross-level congruences
and equality to one fixed reduced Jacobian. -/
theorem exists_compatible_tower_strong (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian q F x)) :
    ∃ z : ℕ → Fin d → ℤ,
      z 0 = x ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ evalSystem F (z n) i) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ (z (n+1) - z n) i) ∧
      (∀ m n, m ≤ n → ∀ i, (q : ℤ)^(L+m) ∣ (z n - z m) i) ∧
      (∀ n, digitJacobian q F (z n) = digitJacobian q F x) ∧
      (∀ n, Function.Surjective (digitJacobian q F (z n))) := by
  obtain ⟨z, hz0, hroot, hstep, hsurj⟩ := exists_compatible_tower q L hq hL F x hx hJ
  refine ⟨z, hz0, hroot, hstep, ?_, ?_, hsurj⟩
  · exact fun m n hmn => tower_pairwise_congruent q L z hstep m n hmn
  · intro n
    rw [← hz0]
    exact tower_digitJacobian_eq q L hL F z hstep n

end Komorebi.PolynomialIntegerTower
