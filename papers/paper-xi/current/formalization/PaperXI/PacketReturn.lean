import PaperXI.FrobeniusPeriod
import Mathlib.LinearAlgebra.Eigenspace.Triangularizable

/-! The actual return operator on a packet and its nonzero eigenline. The
claim that this line is the whole packet is deliberately not assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PacketReturn
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusPeriod
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

theorem power_mem (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) (n : ℕ) {v : V} (hv : v ∈ packet ρ j) :
    (F ^ n) v ∈ packet ρ (((q ^ n : (ZMod M)ˣ) : ZMod M) * j) := by
  induction n with
  | zero => simpa using hv
  | succ n ih =>
    simpa [pow_succ', mul_assoc] using forward_mem ρ F q h _ ih

theorem return_mem (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j) :
    (F ^ period q j) v ∈ packet ρ j := by
  simpa only [return_label] using power_mem ρ F q h j (period q j) hv

def closingOperator (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) :
    Module.End ℂ (packet ρ j) where
  toFun v := ⟨(F ^ period q j) v, return_mem ρ F q h j v.property⟩
  map_add' v w := by ext; simp
  map_smul' c v := by ext; simp

/-- Every nonzero finite-dimensional packet contains a return eigenvector,
with nonzero closing scalar because Frobenius is invertible. -/
theorem exists_closing_eigenvector [FiniteDimensional ℂ V]
    (ρ : Action (K := ℂ) (V := V) (M := M)) (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    {j : ZMod M} (hj : packet ρ j ≠ ⊥) :
    ∃ (c : ℂ) (v : V), c ≠ 0 ∧ v ∈ packet ρ j ∧ v ≠ 0 ∧
      (F ^ period q j) v = c • v := by
  have : Nontrivial (packet ρ j) := Submodule.nontrivial_iff_ne_bot.mpr hj
  obtain ⟨c, hc⟩ := (closingOperator ρ F q h j).exists_eigenvalue
  obtain ⟨w, hw⟩ := hc.exists_hasEigenvector
  have hne : (w : V) ≠ 0 := by
    intro hz
    apply hw.2
    exact Subtype.ext hz
  have heq : (F ^ period q j) (w : V) = c • (w : V) :=
    congrArg Subtype.val hw.apply_eq_smul
  have hc0 : c ≠ 0 := by
    intro hz
    rw [hz, zero_smul] at heq
    exact hne ((F ^ period q j).injective (heq.trans (map_zero _).symm))
  exact ⟨c, w, hc0, w.property, hne, heq⟩

end PaperXI.PacketReturn
