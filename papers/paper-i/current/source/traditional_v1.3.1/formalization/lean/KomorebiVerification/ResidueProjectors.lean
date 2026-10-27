import KomorebiVerification.FibreRefinement

/-!
# Residue-class projectors and exact refinement

This file turns the constructive fibre masks from `Komorebi.Packet` into
genuine linear endomorphisms on sequences indexed by `Nat`.  It then proves
the arithmetic compatibility needed to refine residue classes modulo `N`
into residue classes modulo `N * M`.
-/

set_option autoImplicit false

namespace Komorebi
namespace Residue

universe u v

/-- The address of a natural number in its residue class modulo a positive
modulus. -/
def residueAddress (N : Nat) (hN : 0 < N) : Nat → Fin N :=
  fun n => ⟨n % N, Nat.mod_lt n hN⟩

/-- The finer residue address modulo `N * M`. -/
def fineAddress (N M : Nat) (hN : 0 < N) (hM : 0 < M) : Nat → Fin (N * M) :=
  residueAddress (N * M) (Nat.mul_pos hN hM)

/-- Forget the fine component of a residue modulo `N * M`, retaining only
its residue modulo `N`. -/
def mergeAddress (N M : Nat) (hN : 0 < N) : Fin (N * M) → Fin N :=
  fun s => ⟨s.val % N, Nat.mod_lt s.val hN⟩

/-- Reducing modulo `N * M` and then modulo `N` agrees with reducing directly
modulo `N`.  This is the arithmetic input to projector refinement. -/
theorem merge_fineAddress
    (N M : Nat) (hN : 0 < N) (hM : 0 < M) :
    mergeAddress N M hN ∘ fineAddress N M hN hM = residueAddress N hN := by
  funext n
  apply Fin.ext
  exact Nat.mod_mul_right_mod n N M

/-- Function-level residue refinement, obtained from the independent modular
arithmetic lemma and the pointwise fibre decomposition. -/
theorem residueFibre_refinement
    {A : Type v} [AddCommMonoid A]
    (N M : Nat) (hN : 0 < N) (hM : 0 < M)
    (r : Fin N) (x : Nat → A) :
    Packet.fibreProj (residueAddress N hN) r x =
      ∑ s : Fin (N * M),
        if mergeAddress N M hN s = r then
          Packet.fibreProj (fineAddress N M hN hM) s x
        else 0 := by
  rw [← merge_fineAddress N M hN hM]
  change
    Packet.fibreProj
        (fun n => mergeAddress N M hN (fineAddress N M hN hM n)) r x = _
  exact Packet.fibreProj_refinement
    (fineAddress N M hN hM) (mergeAddress N M hN) r x

/-- The residue mask as an actual linear endomorphism of `A`-valued
sequences. -/
def residueProj
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (hN : 0 < N) (r : Fin N) : Module.End R (Nat → A) :=
  Packet.fibreLinearProj (R := R) (M := A) (residueAddress N hN) r

@[simp] theorem residueProj_apply
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (hN : 0 < N) (r : Fin N) (x : Nat → A) :
    residueProj (R := R) (A := A) N hN r x =
      Packet.fibreProj (residueAddress N hN) r x := rfl

/-- Exact refinement of a coarse residue projector into all fine residue
projectors lying above it. -/
theorem residueProj_refinement
    {R : Type u} {A : Type v}
    [Semiring R] [AddCommMonoid A] [Module R A]
    (N M : Nat) (hN : 0 < N) (hM : 0 < M) (r : Fin N) :
    residueProj (R := R) (A := A) N hN r =
      ∑ s : Fin (N * M),
        if mergeAddress N M hN s = r then
          residueProj (R := R) (A := A) (N * M) (Nat.mul_pos hN hM) s
        else 0 := by
  change
    Packet.fibreLinearProj (R := R) (M := A) (residueAddress N hN) r = _
  rw [← merge_fineAddress N M hN hM]
  change
    Packet.fibreLinearProj (R := R) (M := A)
        (fun n => mergeAddress N M hN (fineAddress N M hN hM n)) r =
      ∑ s : Fin (N * M),
        if mergeAddress N M hN s = r then
          Packet.fibreLinearProj (R := R) (M := A)
            (fineAddress N M hN hM) s
        else 0
  exact Packet.fibreLinearProj_refinement
    (fineAddress N M hN hM) (mergeAddress N M hN) r

#print axioms merge_fineAddress
#print axioms residueFibre_refinement
#print axioms residueProj_refinement

end Residue
end Komorebi
