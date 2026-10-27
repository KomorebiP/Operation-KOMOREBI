import Mathlib.RepresentationTheory.Homological.GroupCohomology.LowDegree
import Mathlib.Algebra.Field.ZMod
import Mathlib.Data.Fintype.Perm

/-!
# Low-degree cohomology for groups of invertible finite order

The averaging argument is connected to Mathlib's actual cohomology of the
inhomogeneous cochain complex through `H1π` and `H1_induction_on`.
-/

noncomputable section

set_option maxHeartbeats 800000

namespace PaperXII.FiniteGroupCohomology

open CategoryTheory Representation groupCohomology

universe u

variable {K G : Type u} [Field K] [Group G] [Fintype G]

/-- An explicit primitive for a one-cocycle. -/
def averagingPrimitive (A : Rep K G) (f : cocycles₁ A) : A :=
  - (Fintype.card G : K)⁻¹ • ∑ g : G, f g

/-- Summing the cocycle identity over a finite group. -/
theorem cocycle_sum_identity (A : Rep K G) (f : cocycles₁ A) (g : G) :
    (Fintype.card G : K) • f g = (∑ h : G, f h) - A.ρ g (∑ h : G, f h) := by
  have h := congrArg (fun q : G → A => ∑ h : G, q h)
    (funext ((mem_cocycles₁_iff (f : G → A)).mp f.property g))
  simp only [Finset.sum_add_distrib, Finset.sum_const, Finset.card_univ,
    ← map_sum, ← Nat.cast_smul_eq_nsmul K] at h
  have hshift : (∑ h : G, f (g * h)) = ∑ h : G, f h :=
    Fintype.sum_equiv (Equiv.mulLeft g) _ _ (fun _ => rfl)
  rw [hshift] at h
  exact eq_sub_iff_add_eq.mpr (by simpa only [add_comm] using h.symm)

/-- Averaging produces an actual coboundary, with no dimension assumption. -/
theorem averagingPrimitive_spec (A : Rep K G) (hcard : (Fintype.card G : K) ≠ 0)
    (f : cocycles₁ A) (g : G) :
    A.ρ g (averagingPrimitive A f) - averagingPrimitive A f = f g := by
  calc
    A.ρ g (averagingPrimitive A f) - averagingPrimitive A f =
        (Fintype.card G : K)⁻¹ • ((∑ h : G, f h) - A.ρ g (∑ h : G, f h)) := by
      simp only [averagingPrimitive]
      rw [LinearMap.map_smul]
      simp only [neg_smul, smul_sub]
      abel
    _ = (Fintype.card G : K)⁻¹ • ((Fintype.card G : K) • f g) := by
      rw [← cocycle_sum_identity A f g]
    _ = f g := by rw [smul_smul, inv_mul_cancel₀ hcard, one_smul]

/-- All one-cocycles are coboundaries for a group of invertible order. -/
theorem cocycles₁_eq_coboundaries₁ (A : Rep K G)
    (hcard : (Fintype.card G : K) ≠ 0) : cocycles₁ A = coboundaries₁ A := by
  apply le_antisymm
  · intro f hf
    refine ⟨averagingPrimitive A ⟨f, hf⟩, ?_⟩
    funext g
    exact averagingPrimitive_spec A hcard ⟨f, hf⟩ g
  · exact coboundaries₁_le_cocycles₁ A

/-- Every element of Mathlib's first group cohomology is zero. -/
theorem h1_eq_zero (A : Rep K G) (hcard : (Fintype.card G : K) ≠ 0)
    (x : groupCohomology A 1) : x = 0 := by
  induction x using H1_induction_on with
  | h f =>
    apply (H1π_eq_zero_iff f).mpr
    rw [← cocycles₁_eq_coboundaries₁ A hcard]
    exact f.property

/-- The first cohomology group itself is the zero module. -/
theorem h1_subsingleton (A : Rep K G) (hcard : (Fintype.card G : K) ≠ 0) :
    Subsingleton (groupCohomology A 1) :=
  ⟨fun x y => (h1_eq_zero A hcard x).trans (h1_eq_zero A hcard y).symm⟩

omit [Fintype G] in
/-- Vanishing of degree zero is precisely vanishing of actual invariants. -/
theorem h0_subsingleton_iff_invariants_eq_bot (A : Rep K G) :
    Subsingleton (groupCohomology A 0) ↔ A.ρ.invariants = ⊥ :=
  (H0Iso A).toLinearEquiv.toEquiv.subsingleton_congr.trans
    Submodule.subsingleton_iff_eq_bot

omit [Fintype G] in
/-- A usable zero-invariants criterion for degree-zero cohomology. -/
theorem h0_subsingleton_of_fixed_eq_zero (A : Rep K G)
    (hfixed : ∀ v : A, (∀ g : G, A.ρ g v = v) → v = 0) :
    Subsingleton (groupCohomology A 0) := by
  apply (h0_subsingleton_iff_invariants_eq_bot A).mpr
  apply (Submodule.eq_bot_iff _).mpr
  intro v hv
  exact hfixed v ((mem_invariants A.ρ v).mp hv)

/-- The symmetric group on three letters has order invertible in `F₇`. -/
theorem s3_order_nonzero : (Fintype.card (Equiv.Perm (Fin 3)) : ZMod 7) ≠ 0 := by
  norm_num [Fintype.card_perm, Nat.factorial]
  decide

/-- Actual first group cohomology vanishes for every `F₇` representation of `S₃`. -/
theorem s3_h1_subsingleton (A : Rep (ZMod 7) (Equiv.Perm (Fin 3))) :
    Subsingleton (groupCohomology A 1) := by
  have : Fact (Nat.Prime 7) := ⟨by decide⟩
  exact h1_subsingleton A s3_order_nonzero

end PaperXII.FiniteGroupCohomology
