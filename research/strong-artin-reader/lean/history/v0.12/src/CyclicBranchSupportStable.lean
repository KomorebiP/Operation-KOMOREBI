import CyclicDefectAlgebra
import CyclicSupportStable

namespace Komorebi.StrongArtin.CyclicBranchSupport

open Komorebi.StrongArtin.CyclicDefect

noncomputable section

variable (p : ℕ) [Fact p.Prime]

/-- The generic cyclic-defect branch indexed by the intrinsic quotient label
`x : ZMod p`, rather than by a chosen `Fin p` representative. -/
def branchAtLabel {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) (x : ZMod p) :
    GenericFiber p K →ₐ[K] K := by
  haveI : NeZero p := ⟨(Fact.out : p.Prime).ne_zero⟩
  exact branchHom p ζ hζ ⟨x.val, x.val_lt⟩

/-- One quotient-character twist moves the intrinsic branch label by `+1`. -/
theorem branchAtLabel_comp_twist {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) (x : ZMod p) :
    (branchAtLabel p ζ hζ x).comp (twistHom p ζ hζ) =
      branchAtLabel p ζ hζ (x + 1) := by
  apply AdjoinRoot.algHom_ext
  simp only [branchAtLabel]
  rw [branchHom_comp_twist_root p ζ hζ]
  simp only [branchHom, AdjoinRoot.liftAlgHom_root]
  rw [@ZMod.val_add p ⟨(Fact.out : p.Prime).ne_zero⟩ x 1]
  rw [ZMod.val_one_eq_one_mod, Nat.mod_eq_of_lt (Fact.out : p.Prime).one_lt]
  rw [← pow_eq_pow_mod (x.val + 1) hζ.pow_eq_one]

/-- The intrinsic label parametrization is injective: distinct quotient labels
produce distinct generic evaluation branches. -/
theorem branchAtLabel_injective {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    Function.Injective (branchAtLabel p ζ hζ) := by
  intro x y hxy
  let hnz : NeZero p := ⟨(Fact.out : p.Prime).ne_zero⟩
  have hfin := (branchHom_injective p ζ hζ) (by simpa [branchAtLabel] using hxy)
  have hval : x.val = y.val := congrArg Fin.val hfin
  exact (@ZMod.val_injective p hnz) hval

/-- Direct support-gate formulation. If at least one generic cyclic branch has
property `P`, and `P` is preserved by the quotient-twist automorphism, then
all generic cyclic branches have `P`. This is the exact finite symmetry lemma
needed by a later equivariant support/patching theorem. -/
theorem all_branches_of_nonempty_twist_stable {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p)
    (P : (GenericFiber p K →ₐ[K] K) → Prop)
    (hne : ∃ x : ZMod p, P (branchAtLabel p ζ hζ x))
    (hstable : ∀ x : ZMod p,
      P (branchAtLabel p ζ hζ x) →
      P ((branchAtLabel p ζ hζ x).comp (twistHom p ζ hζ))) :
    ∀ x : ZMod p, P (branchAtLabel p ζ hζ x) := by
  let S : Set (ZMod p) := {x | P (branchAtLabel p ζ hζ x)}
  have hSnonempty : S.Nonempty := by
    rcases hne with ⟨x, hx⟩
    exact ⟨x, hx⟩
  have hSstep : ∀ x : ZMod p, x ∈ S → x + 1 ∈ S := by
    intro x hx
    have ht := hstable x hx
    rw [branchAtLabel_comp_twist p ζ hζ x] at ht
    exact ht
  have hSuniv := Komorebi.StrongArtin.CyclicSupport.nonempty_add_one_stable_eq_univ
    p S hSnonempty hSstep
  intro x
  have hx : x ∈ S := by rw [hSuniv]; simp
  exact hx

end
end Komorebi.StrongArtin.CyclicBranchSupport

#print axioms Komorebi.StrongArtin.CyclicBranchSupport.branchAtLabel_comp_twist
#print axioms Komorebi.StrongArtin.CyclicBranchSupport.branchAtLabel_injective
#print axioms Komorebi.StrongArtin.CyclicBranchSupport.all_branches_of_nonempty_twist_stable
