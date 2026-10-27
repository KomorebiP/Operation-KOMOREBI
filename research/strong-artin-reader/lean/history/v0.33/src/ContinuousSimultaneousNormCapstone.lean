import SimultaneousFrobeniusCriterion

/-! Compute the actual inherited continuous local-gauge class. The local sources
are genuine procyclic groups; no arithmetic global-local comparison is assumed. -/
noncomputable section
namespace Komorebi.StrongArtin.Procyclic
open Komorebi.StrongArtin.SimultaneousNorm
variable {A B k V I : Type} [Ring A] [Ring B] [Field k] [AddCommGroup V] [Module k V]
variable [Finite A] [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]

/-- All action types, arbitrary prime-power restriction families. -/
theorem continuous_primePower_gauge_zero_iff_pivot
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ x y, q x=0 → q y=0 → x*y=0)
    (rho : Zhat →ₜ* Bˣ) (p : ℕ) [Fact (Nat.Prime p)] [CharP k p]
    (a : I → ℕ) (t : I → (Zhat →ₜ* Aˣ))
    (ht : ∀ i z, q (t i z) = (rho (degreeMap (p^a i) z) : B))
    (F : Aˣ) (hF : q F = (rho frobenius : B))
    (hV : ∀ i, q (t i frobenius) = q (F^(p^a i)))
    (S : SquareZeroH2.FrobeniusLinearCoordinates
      (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom) F k V)
    (i₀ : I) (hmin : ∀ i, p^a i₀ ≤ p^a i) :
    let D := SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom
    let e := fun i => S.coordinates (D.unitMismatch (t i frobenius) (F^(p^a i)) (hV i))
    D.localConjugacyObstruction (fun _ : I => Zhat)
      (SquareZeroH2.continuousSectionDatum_continuous_lift q hq hsq rho.toMonoidHom rho.continuous)
      (fun i => (degreeMap (p^a i)).toMonoidHom) (fun i => (degreeMap (p^a i)).continuous)
      (fun i => (t i).toMonoidHom) ht (fun i => (t i).continuous) = 0 ↔
    e i₀ ∈ LinearMap.range ((S.operator-1)^(p^a i₀-1)) ∧
      ∀ i, e i - ((S.operator-1)^(p^a i-p^a i₀)) (e i₀) ∈
        LinearMap.range ((S.operator-1)^(p^a i)) := by
  dsimp only
  rw [gauge_obstruction_zero_iff_explicit_norm_class_zero q hq hsq rho
    (fun i => p^a i) t ht F hF hV]
  exact S.primePower_matchingClass_zero_iff_pivot p a _ hV i₀ hmin

/-- Mixed degrees on a nilpotent eigenvalue-one kernel block, with exact normalization. -/
theorem continuous_unipotent_gauge_zero_iff_pivot
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ x y, q x=0 → q y=0 → x*y=0)
    (rho : Zhat →ₜ* Bˣ) (p : ℕ) [Fact (Nat.Prime p)] [CharP k p]
    (m a : I → ℕ) (hm : ∀ i, (m i : k) ≠ 0) (t : I → (Zhat →ₜ* Aˣ))
    (ht : ∀ i z, q (t i z) = (rho (degreeMap (m i*p^a i) z) : B))
    (F : Aˣ) (hF : q F = (rho frobenius : B))
    (hV : ∀ i, q (t i frobenius) = q (F^(m i*p^a i)))
    (S : SquareZeroH2.FrobeniusLinearCoordinates
      (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom) F k V)
    (hN : IsNilpotent (S.operator-1)) (i₀ : I) (hmin : ∀ i, p^a i₀ ≤ p^a i) :
    let D := SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom
    let e := fun i => S.coordinates (D.unitMismatch (t i frobenius) (F^(m i*p^a i)) (hV i))
    let f := normalizedUnipotentErrors S.operator hN m a p hm e
    D.localConjugacyObstruction (fun _ : I => Zhat)
      (SquareZeroH2.continuousSectionDatum_continuous_lift q hq hsq rho.toMonoidHom rho.continuous)
      (fun i => (degreeMap (m i*p^a i)).toMonoidHom)
      (fun i => (degreeMap (m i*p^a i)).continuous)
      (fun i => (t i).toMonoidHom) ht (fun i => (t i).continuous) = 0 ↔
    f i₀ ∈ LinearMap.range ((S.operator-1)^(p^a i₀-1)) ∧
      ∀ i, f i - ((S.operator-1)^(p^a i-p^a i₀)) (f i₀) ∈
        LinearMap.range ((S.operator-1)^(p^a i)) := by
  dsimp only
  rw [gauge_obstruction_zero_iff_explicit_norm_class_zero q hq hsq rho
    (fun i => m i*p^a i) t ht F hF hV]
  exact S.unipotent_matchingClass_zero_iff_pivot hN m a p hm _ hV i₀ hmin

end Komorebi.StrongArtin.Procyclic
