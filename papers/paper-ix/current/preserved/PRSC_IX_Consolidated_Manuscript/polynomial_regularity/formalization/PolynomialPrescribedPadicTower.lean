module
public import PolynomialPrescribedIntegerTower
public import PolynomialPrescribedTowerLimit
public import PolynomialPrescribedTowerUnique

@[expose] public section
noncomputable section
set_option autoImplicit false

open Filter Topology

namespace Komorebi.PolynomialPrescribedPadicTower

open Komorebi.PolynomialObstruction Komorebi.PolynomialPadicLift
open Komorebi.PolynomialPrescribedSystem Komorebi.PolynomialPrescribedLifts
open Komorebi.PolynomialParameterSystem (freePart)

variable {m k e : ℕ}

/-- Every supplied compatible parameter path admits an actual polynomial tower
and exact p-adic endpoint. The tower is constructed from initial solved-block
surjectivity; it is not an input. Every parameter digit remains admissible. -/
theorem exists_root_with_prescribed_path (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m+k)) ℤ) (x : Fin (m+k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (t : ℕ → Fin k → ℤ) (ht0 : t 0 = freePart x)
    (ht : ∀ n j, (p : ℤ)^(L+n) ∣ t (n+1) j - t n j)
    (τ : Fin k → ℤ_[p])
    (htlim : Tendsto (fun n i => (t n i : ℤ_[p])) atTop (𝓝 τ)) :
    ∃ (z : ℕ → Fin (m+k) → ℤ) (b : Fin (m+k) → ℤ_[p]),
      z 0 = x ∧
      (∀ n, freePart (z n) = t n) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ evalSystem F (z n) i) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ (z (n+1) - z n) i) ∧
      (∀ n, solvedJacobian p F (z n) = solvedJacobian p F x) ∧
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 b) ∧
      (∀ i, padicEval p F b i = 0) ∧ freePart b = τ ∧
      (∀ n i, (p : ℤ_[p])^(L+n) ∣ b i - (z n i : ℤ_[p])) ∧
      (∀ n v, Nat.card (PrescribedLifts p (L+n) F (z n) v) = p^(m-e)) := by
  obtain ⟨z, hz0, hfree, hroot, hstep, hfixed⟩ :=
    PolynomialPrescribedIntegerTower.exists_prescribed_tower p L
      (Fact.out : Nat.Prime p).pos hL F x hx hJ t ht0 ht
  obtain ⟨b, hlim, hprecision, hb, hbτ⟩ :=
    PolynomialPrescribedTowerLimit.prescribed_tower_limit p L F z t τ
      hroot hstep hfree htlim
  refine ⟨z, b, hz0, hfree, hroot, hstep, hfixed, hlim, hb, hbτ, hprecision, ?_⟩
  intro n v
  apply PolynomialPrescribedStep.prescribed_lift_card p (L+n) (by omega) F (z n)
    (hroot n)
  rw [hfixed n]
  exact hJ

/-- Any p-adic parameter in the initial residue ball has an exact root reached
by a compatible integer polynomial tower. No parameter path or solution tower
is assumed: both are constructed, with all precisions and per-digit counts. -/
theorem exists_prescribed_padic_root_with_tower (p L : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (F : Fin e → MvPolynomial (Fin (m+k)) ℤ)
    (x : Fin (m+k) → ℤ) (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (τ : Fin k → ℤ_[p])
    (hτ : ∀ j, (p : ℤ_[p])^L ∣ τ j - ((freePart x j : ℤ) : ℤ_[p])) :
    ∃ (z : ℕ → Fin (m+k) → ℤ) (b : Fin (m+k) → ℤ_[p]),
      z 0 = x ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ evalSystem F (z n) i) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ (z (n+1) - z n) i) ∧
      (∀ n, solvedJacobian p F (z n) = solvedJacobian p F x) ∧
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 b) ∧
      (∀ i, padicEval p F b i = 0) ∧ freePart b = τ ∧
      (∀ n i, (p : ℤ_[p])^(L+n) ∣ b i - (z n i : ℤ_[p])) ∧
      (∀ n v, Nat.card (PrescribedLifts p (L+n) F (z n) v) = p^(m-e)) := by
  obtain ⟨t, ht0, ht, _, htlim⟩ :=
    PolynomialParameterPath.exists_parameter_path p L (freePart x) τ hτ
  obtain ⟨z, b, hz0, _, hroot, hstep, hfixed, hlim, hb, hbτ, hprecision, hcard⟩ :=
    exists_root_with_prescribed_path p L hL F x hx hJ t ht0 ht τ htlim
  exact ⟨z, b, hz0, hroot, hstep, hfixed, hlim, hb, hbτ, hprecision, hcard⟩

/-- Root existence with prescribed arbitrary p-adic parameters, retaining the
initial residue class, follows from the actual tower construction. -/
theorem exists_prescribed_padic_root (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m+k)) ℤ) (x : Fin (m+k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (τ : Fin k → ℤ_[p])
    (hτ : ∀ j, (p : ℤ_[p])^L ∣ τ j - ((freePart x j : ℤ) : ℤ_[p])) :
    ∃ b : Fin (m+k) → ℤ_[p],
      (∀ i, padicEval p F b i = 0) ∧ freePart b = τ ∧
      (∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) := by
  obtain ⟨z, b, hz0, _, _, _, _, hb, hbτ, hprecision, _⟩ :=
    exists_prescribed_padic_root_with_tower p L hL F x hx hJ τ hτ
  refine ⟨b, hb, hbτ, ?_⟩
  simpa only [Nat.add_zero, hz0] using hprecision 0

/-- In the square solved case, every prescribed p-adic parameter has exactly
one root in the original ball, independent of all lifting choices. -/
theorem exists_unique_prescribed_padic_root (p L : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) (F : Fin e → MvPolynomial (Fin (e+k)) ℤ)
    (x : Fin (e+k) → ℤ) (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (solvedJacobian p F x))
    (τ : Fin k → ℤ_[p])
    (hτ : ∀ j, (p : ℤ_[p])^L ∣ τ j - ((freePart x j : ℤ) : ℤ_[p])) :
    ∃! b : Fin (e+k) → ℤ_[p],
      (∀ i, padicEval p F b i = 0) ∧ freePart b = τ ∧
      (∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) := by
  obtain ⟨b, hb, hbτ, hbx⟩ := exists_prescribed_padic_root p L hL F x hx hJ τ hτ
  refine ⟨b, ⟨hb, hbτ, hbx⟩, ?_⟩
  intro c hc
  exact PolynomialPrescribedTowerUnique.prescribed_root_unique p L hL F x hx hJ
    c b hc.1 hb hc.2.2 hbx (hc.2.1.trans hbτ.symm)

end Komorebi.PolynomialPrescribedPadicTower
