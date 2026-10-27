module
public import PolynomialPrescribedIntegerTower
public import PolynomialParameterPath
public import PolynomialPrescribedTowerUnique
public import PolynomialPrescribedContract
public import PolynomialPrescribedPadicTower

@[expose] public section
noncomputable section
set_option autoImplicit false
open scoped BigOperators
open Filter Topology

namespace Komorebi.PolynomialParameterTowerContracts
open MvPolynomial
variable {m k e : ℕ}

/-- The expanded contract quantifies over every compatible exact integer parameter path.
Surjectivity is imposed only at the initial point, on the actual solved derivative columns. -/
theorem actual_integer_path_tower (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ eval x (F i))
    (hJ : ∀ r : Fin e → ZMod q, ∃ u : Fin m → ZMod q,
      ∀ i, ∑ j, (eval x (pderiv (Fin.castAdd k j) (F i)) : ZMod q) * u j = r i)
    (t : ℕ → Fin k → ℤ) (ht0 : ∀ j, t 0 j = x (Fin.natAdd m j))
    (ht : ∀ n j, (q : ℤ)^(L+n) ∣ t (n+1) j - t n j) :
    ∃ z : ℕ → Fin (m + k) → ℤ,
      z 0 = x ∧
      (∀ n j, z n (Fin.natAdd m j) = t n j) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ eval (z n) (F i)) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ z (n+1) i - z n i) ∧
      (∀ n, PolynomialPrescribedContract.actualSolvedMap q F (z n) =
        PolynomialPrescribedContract.actualSolvedMap q F x) := by
  have hs : Function.Surjective (PolynomialPrescribedSystem.solvedJacobian q F x) := by
    intro r
    obtain ⟨u, hu⟩ := hJ r
    exact ⟨u, funext hu⟩
  obtain ⟨z, hz0, hfree, hroot, hstep, hfixed⟩ :=
    PolynomialPrescribedIntegerTower.exists_prescribed_tower q L hq hL F x hx hs t
      (funext ht0) ht
  exact ⟨z, hz0, fun n j => congrFun (hfree n) j, hroot, hstep, hfixed⟩

/-- No approximation path is assumed: every p-adic target in the initial ball
has a compatible integer path with exact initial value and all requested precisions. -/
theorem arbitrary_padic_parameter_path (p L : ℕ) [Fact (Nat.Prime p)]
    (x : Fin k → ℤ) (τ : Fin k → ℤ_[p])
    (hτ : ∀ j, (p : ℤ_[p])^L ∣ τ j - (x j : ℤ_[p])) :
    ∃ t : ℕ → Fin k → ℤ,
      t 0 = x ∧
      (∀ n j, (p : ℤ)^(L+n) ∣ t (n+1) j - t n j) ∧
      (∀ n j, (p : ℤ_[p])^(L+n) ∣ τ j - (t n j : ℤ_[p])) ∧
      Tendsto (fun n j => (t n j : ℤ_[p])) atTop (𝓝 τ) := by
  exact PolynomialParameterPath.exists_parameter_path p L x τ hτ

/-- With e solved variables for e equations, equal prescribed parameters force
uniqueness throughout the initial ball. All polynomial evaluations are explicit. -/
theorem actual_square_parameter_uniqueness (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ) (x : Fin (e + k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ eval x (F i))
    (hJ : ∀ r : Fin e → ZMod p, ∃ u : Fin e → ZMod p,
      ∀ i, ∑ j, (eval x (pderiv (Fin.castAdd k j) (F i)) : ZMod p) * u j = r i)
    (b c : Fin (e + k) → ℤ_[p])
    (hb : ∀ i, eval₂ (Int.castRingHom ℤ_[p]) b (F i) = 0)
    (hc : ∀ i, eval₂ (Int.castRingHom ℤ_[p]) c (F i) = 0)
    (hbx : ∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p]))
    (hcx : ∀ i, (p : ℤ_[p])^L ∣ c i - (x i : ℤ_[p]))
    (ht : ∀ j, b (Fin.natAdd e j) = c (Fin.natAdd e j)) : b = c := by
  have hs : Function.Surjective (PolynomialPrescribedSystem.solvedJacobian p F x) := by
    intro r
    obtain ⟨u, hu⟩ := hJ r
    exact ⟨u, funext hu⟩
  exact PolynomialPrescribedTowerUnique.prescribed_root_unique p L hL F x hx hs
    b c hb hc hbx hcx (funext ht)

/-- The final target is an actual polynomial root for every arbitrary p-adic
parameter in the initial ball, reached by a constructed compatible integer tower.
The branching count uses explicitly constrained residue vectors at every level. -/
theorem arbitrary_padic_target_tower (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ eval x (F i))
    (hJ : ∀ r : Fin e → ZMod p, ∃ u : Fin m → ZMod p,
      ∀ i, ∑ j, (eval x (pderiv (Fin.castAdd k j) (F i)) : ZMod p) * u j = r i)
    (τ : Fin k → ℤ_[p])
    (hτ : ∀ j, (p : ℤ_[p])^L ∣ τ j - (x (Fin.natAdd m j) : ℤ_[p])) :
    ∃ (z : ℕ → Fin (m + k) → ℤ) (b : Fin (m + k) → ℤ_[p]),
      z 0 = x ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ eval (z n) (F i)) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ z (n+1) i - z n i) ∧
      (∀ n, PolynomialPrescribedContract.actualSolvedMap p F (z n) =
        PolynomialPrescribedContract.actualSolvedMap p F x) ∧
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 b) ∧
      (∀ i, eval₂ (Int.castRingHom ℤ_[p]) b (F i) = 0) ∧
      (∀ j, b (Fin.natAdd m j) = τ j) ∧
      (∀ n i, (p : ℤ_[p])^(L+n) ∣ b i - (z n i : ℤ_[p])) ∧
      (∀ n (v : Fin k → ZMod p),
        Nat.card (PolynomialPrescribedContract.ActualResidues p (L+n) F (z n) v) =
          p^(m-e)) := by
  have hs : Function.Surjective (PolynomialPrescribedSystem.solvedJacobian p F x) := by
    intro r
    obtain ⟨u, hu⟩ := hJ r
    exact ⟨u, funext hu⟩
  obtain ⟨z, b, hz0, hroot, hstep, hfixed, hlim, hb, hfree, hprecision, hcard⟩ :=
    PolynomialPrescribedPadicTower.exists_prescribed_padic_root_with_tower p L hL
      F x hx hs τ hτ
  refine ⟨z, b, hz0, hroot, hstep, hfixed, hlim, hb,
    fun j => congrFun hfree j, hprecision, ?_⟩
  intro n v
  rw [Nat.card_congr (PolynomialPrescribedContract.actualResidueEquiv p (L+n) F (z n) v)]
  exact hcard n v

/-- The supplied-path version retains each prescribed integer parameter exactly;
it does not merely reach some root with the same p-adic parameter limit. -/
theorem supplied_path_actual_endpoint (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ) (x : Fin (m + k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ eval x (F i))
    (hJ : ∀ r : Fin e → ZMod p, ∃ u : Fin m → ZMod p,
      ∀ i, ∑ j, (eval x (pderiv (Fin.castAdd k j) (F i)) : ZMod p) * u j = r i)
    (t : ℕ → Fin k → ℤ) (ht0 : ∀ j, t 0 j = x (Fin.natAdd m j))
    (ht : ∀ n j, (p : ℤ)^(L+n) ∣ t (n+1) j - t n j)
    (τ : Fin k → ℤ_[p])
    (htlim : Tendsto (fun n j => (t n j : ℤ_[p])) atTop (𝓝 τ)) :
    ∃ (z : ℕ → Fin (m + k) → ℤ) (b : Fin (m + k) → ℤ_[p]),
      z 0 = x ∧
      (∀ n j, z n (Fin.natAdd m j) = t n j) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ eval (z n) (F i)) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ z (n+1) i - z n i) ∧
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 b) ∧
      (∀ i, eval₂ (Int.castRingHom ℤ_[p]) b (F i) = 0) ∧
      (∀ j, b (Fin.natAdd m j) = τ j) ∧
      (∀ n i, (p : ℤ_[p])^(L+n) ∣ b i - (z n i : ℤ_[p])) := by
  have hs : Function.Surjective (PolynomialPrescribedSystem.solvedJacobian p F x) := by
    intro r
    obtain ⟨u, hu⟩ := hJ r
    exact ⟨u, funext hu⟩
  obtain ⟨z, b, hz0, hfree, hroot, hstep, _, hlim, hb, hbτ, hprecision, _⟩ :=
    PolynomialPrescribedPadicTower.exists_root_with_prescribed_path p L hL F x hx hs
      t (funext ht0) ht τ htlim
  exact ⟨z, b, hz0, fun n j => congrFun (hfree n) j, hroot, hstep, hlim,
    hb, fun j => congrFun hbτ j, hprecision⟩

end Komorebi.PolynomialParameterTowerContracts
