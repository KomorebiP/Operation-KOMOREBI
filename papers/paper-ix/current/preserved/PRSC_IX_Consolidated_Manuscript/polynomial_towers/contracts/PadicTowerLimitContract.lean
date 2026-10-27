module
public import PadicTowerLimit

@[expose] public section
noncomputable section
set_option autoImplicit false
open Filter Topology
namespace Komorebi.PadicTowerLimitContract

/-- Compatibility alone supplies the actual p-adic limit; convergence and the
retention of all residues are conclusions. -/
theorem explicit_vector_limit {ι : Type*} (p L : ℕ) [Fact (Nat.Prime p)]
    (z : ℕ → ι → ℤ)
    (hstep : ∀ n i, (p : ℤ)^(L+n) ∣ z (n+1) i - z n i) :
    ∃ a : ι → ℤ_[p],
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 a) ∧
      ∀ n i, (p : ℤ_[p])^(L+n) ∣ a i - (z n i : ℤ_[p]) := by
  exact PadicTowerLimit.compatible_vector_tower_limit p L z hstep

end Komorebi.PadicTowerLimitContract
