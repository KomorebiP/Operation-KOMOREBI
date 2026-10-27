import PaperXI.ResidueWeil
import PaperXI.RamificationSeparation
import Mathlib.Topology.Algebra.InfiniteSum.NatInt
import Mathlib.Basic.Real.Basic

/-! Conductor sums from actual maximal-ideal congruence groups. For a finite
Galois extension with discrete valuation these are the lower-numbering expressions.
No change-of-extension theorem, absolute Weil comparison, or Hasse--Arf integrality
is inferred from this definition. Finite support is proved under the stated
Noetherian/finite faithful action conditions. -/
set_option autoImplicit false
noncomputable section
open scoped Classical BigOperators
namespace PaperXI.ValuationConductor
open PaperXI.ValuationRamification PaperXI.ResidueWeil

variable (R D : Type*) [CommRing R] [IsLocalRing R] [Group D] [MulSemiringAction D R]

abbrev residue : D →* RingAut (IsLocalRing.ResidueField R) :=
  MulSemiringAction.toRingAut D (IsLocalRing.ResidueField R)

/-- The lower group embeds into the degree-zero part of the actual residue pullback. -/
def lift (F : RingAut (IsLocalRing.ResidueField R)) (i : ℕ) :
    lower R D i →* Pullback (residue R D) F where
  toFun g := ⟨(g.val, 1), by
    change residue R D g.val = F ^ (0 : ℤ)
    rw [zpow_zero]
    exact lower_le_inertia R D i g.property⟩
  map_one' := rfl
  map_mul' _ _ := rfl

@[simp] theorem lift_degree (F : RingAut (IsLocalRing.ResidueField R))
    (i : ℕ) (g : lower R D i) : degree (residue R D) F (lift R D F i g) = 1 := rfl

variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- These are fixed spaces for actual congruence-group operators. -/
def fixed (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) (i : ℕ) : Submodule ℂ V :=
  Representation.invariants (ρ.comp (lift R D F i))

/-- Zeroth lower fixed space is exactly the degree-kernel fixed space. -/
theorem fixed_zero (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) :
    fixed R D F ρ 0 = Representation.invariants (ρ.comp (degree (residue R D) F).ker.subtype) := by
  ext v
  constructor
  · intro hv w
    have hg : w.val.val.1 ∈ lower R D 0 := by
      rw [lower_zero_eq_residue_kernel]
      exact (inertiaEquiv (residue R D) F w).property
    have hh := hv ⟨w.val.val.1, hg⟩
    have he : lift R D F 0 ⟨w.val.val.1, hg⟩ = w.val := by
      apply Subtype.ext
      exact Prod.ext rfl w.property.symm
    change ρ w.val v = v
    simpa only [MonoidHom.comp_apply, he] using hh
  · intro hv g
    exact hv ⟨lift R D F 0 g, rfl⟩

def codimension (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) (i : ℕ) : ℕ :=
  Module.finrank ℂ V - Module.finrank ℂ (fixed R D F ρ i)

/-- The conventional lower-numbering weight is derived from actual subgroup orders. -/
def summand (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) (i : ℕ) : ℝ :=
  (Nat.card (lower R D i) : ℝ) / (Nat.card (lower R D 0) : ℝ) * codimension R D F ρ i

def swan (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) : ℝ :=
  ∑' i : ℕ, summand R D F ρ (i+1)

def artin (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) : ℝ :=
  (codimension R D F ρ 0 : ℝ) + swan R D F ρ

/-- First-group triviality forces every positive-depth term to vanish. -/
theorem positive_fixed_top (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V)
    (ht : ∀ g : lower R D 1, ρ (lift R D F 1 g) = 1) (i : ℕ) :
    fixed R D F ρ (i+1) = ⊤ := by
  apply top_unique
  intro v _ g
  have hg : g.val ∈ lower R D 1 := positive_le_one R D (Nat.le_add_left 1 i) g.property
  exact LinearMap.congr_fun (ht ⟨g.val, hg⟩) v

theorem tame_summand_zero (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V)
    (ht : ∀ g : lower R D 1, ρ (lift R D F 1 g) = 1) (i : ℕ) :
    summand R D F ρ (i+1) = 0 := by
  unfold summand codimension
  rw [positive_fixed_top R D F ρ ht i]
  simp

theorem tame_swan_zero (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V)
    (ht : ∀ g : lower R D 1, ρ (lift R D F 1 g) = 1) : swan R D F ρ = 0 := by
  simp only [swan, tame_summand_zero R D F ρ ht, tsum_zero]

/-- The original irreducible dimension argument no longer needs tame orbit induction. -/
theorem tame_irreducible_dimension [FiniteDimensional ℂ V] (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) [Representation.IsIrreducible ρ]
    (ht : ∀ g : lower R D 1, ρ (lift R D F 1 g) = 1)
    (hdim : 1 < Module.finrank ℂ V) :
    fixed R D F ρ 0 = ⊥ ∧ swan R D F ρ = 0 ∧ artin R D F ρ = (Module.finrank ℂ V : ℝ) := by
  have hf : fixed R D F ρ 0 = ⊥ := by
    rw [fixed_zero]
    exact NormalInertia.fixed_eq_bot_of_dimension_gt_one ρ (degree (residue R D) F).ker hdim
  refine ⟨hf, tame_swan_zero R D F ρ ht, ?_⟩
  unfold artin codimension
  rw [hf, tame_swan_zero R D F ρ ht]
  simp

/-- Unramified one-dimensional representations retain conductor zero. -/
theorem tame_artin_dichotomy [FiniteDimensional ℂ V] (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) [Representation.IsIrreducible ρ]
    (ht : ∀ g : lower R D 1, ρ (lift R D F 1 g) = 1) :
    artin R D F ρ = if (degree (residue R D) F).ker ≤ ρ.ker then 0 else
      (Module.finrank ℂ V : ℝ) := by
  rw [artin, tame_swan_zero R D F ρ ht, add_zero]
  unfold codimension
  rw [fixed_zero, NormalInertia.fixed_codimension]
  split_ifs <;> simp

/-- A trivial congruence subgroup has the full fixed space. -/
theorem fixed_top_of_lower_bot (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) (i : ℕ)
    (hi : lower R D i = ⊥) : fixed R D F ρ i = ⊤ := by
  apply top_unique
  intro v _ g
  have hg : g.val = 1 := by simpa only [hi, Subgroup.mem_bot] using g.property
  have he : lift R D F i g = 1 := by apply Subtype.ext; exact Prod.ext hg rfl
  change ρ (lift R D F i g) v = v
  simp [he]

/-- Finite support follows from Krull separation and finite faithful ring action. -/
theorem summable_summands [IsNoetherianRing R] [Finite D] [FaithfulSMul D R]
    (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) :
    Summable (summand R D F ρ) := by
  obtain ⟨N, hN⟩ := RamificationSeparation.eventually_trivial R D
  apply summable_of_ne_finset_zero (s := Finset.range N)
  intro i hi
  have hh : N ≤ i := by simpa only [Finset.mem_range, not_lt] using hi
  unfold summand codimension
  rw [fixed_top_of_lower_bot R D F ρ i (hN i hh)]
  simp

/-- The inertia denominator is nonzero, so the zeroth conventional weight is one. -/
theorem zeroth_summand [Finite D] (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) :
    summand R D F ρ 0 = (codimension R D F ρ 0 : ℝ) := by
  unfold summand
  have hc : (Nat.card (lower R D 0) : ℝ) ≠ 0 := by
    exact_mod_cast (Nat.card_pos : 0 < Nat.card (lower R D 0)).ne'
  rw [div_self hc, one_mul]

/-- The split Artin definition equals the full convergent lower-numbering sum. -/
theorem artin_eq_full_sum [IsNoetherianRing R] [Finite D] [FaithfulSMul D R]
    (F : RingAut (IsLocalRing.ResidueField R))
    (ρ : Representation ℂ (Pullback (residue R D) F) V) :
    artin R D F ρ = ∑' i : ℕ, summand R D F ρ i := by
  have h := (summable_summands R D F ρ).sum_add_tsum_nat_add 1
  simpa only [Finset.sum_range_one, zeroth_summand, artin, swan] using h

end PaperXI.ValuationConductor
