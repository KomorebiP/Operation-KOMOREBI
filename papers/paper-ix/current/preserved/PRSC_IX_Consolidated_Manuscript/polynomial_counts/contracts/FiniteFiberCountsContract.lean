module
public import FiniteFiberCounts

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteFiberCountsContract

/-- The rank refers to the range of the supplied prime-field linear map. -/
theorem explicit_fiber_and_obstruction_counts (p : ℕ) [Fact (Nat.Prime p)]
    {d e : ℕ} (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p))
    (b : Fin e → ZMod p) (h : ∃ t, b + A t = 0) :
    Nat.card {t : Fin d → ZMod p // b + A t = 0} =
      p ^ (d - Module.finrank (ZMod p) A.range) ∧
    Nat.card ((Fin e → ZMod p) ⧸ A.range) =
      p ^ (e - Module.finrank (ZMod p) A.range) := by
  exact ⟨FiniteFiberCounts.fiber_card_of_nonempty p A b
    (by rcases h with ⟨t, ht⟩; exact ⟨⟨t, ht⟩⟩),
    FiniteFiberCounts.cokernel_card p A⟩

/-- Translation is explicitly free and transitive, not merely an equal count. -/
theorem explicit_free_transitive (p : ℕ) [Fact (Nat.Prime p)] {d e : ℕ}
    (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p)) (b : Fin e → ZMod p)
    (u t : {t : Fin d → ZMod p // b + A t = 0}) :
    ∃! v : A.ker, FiniteFiberCounts.translate A b v u = t := by
  exact FiniteFiberCounts.translate_exists_unique A b u t

end Komorebi.FiniteFiberCountsContract
