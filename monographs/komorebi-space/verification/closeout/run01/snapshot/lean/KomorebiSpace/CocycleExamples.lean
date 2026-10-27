import KomorebiSpace.NonabelianExtensionFibers
import KomorebiSpace.ViewBoundaryExamples
import Mathlib.GroupTheory.Perm.Fin

set_option autoImplicit false

/-!
# Loop cocycles: conjugacy classes versus automorphisms

On the one-view category with C2 loops, constant group coefficients give
involutions up to conjugacy. The formal statements retain automorphisms
and distinguish cocycle existence from trivializability.
-/
universe u
namespace KomorebiSpace
open CategoryTheory GroupViewSystem
namespace CocycleExamples
open ViewBoundaryExamples (LoopView)

variable (H : Type u) [Group H]

def loopCoefficients : GroupViewSystem LoopView (fun _ => H) where
  pull := fun _ => MonoidHom.id H
  pull_id := by intros; rfl
  pull_comp := by intros; rfl

variable {H}
def involutionCocycle (p : H) (hp : p * p = 1) : (loopCoefficients H).Cocycle where
  edge := fun f => if f then p else 1
  edge_id := by intro v; rfl
  edge_comp := by
    intro v w z f g
    change (if Bool.xor f g then p else 1) = (if f then p else 1) * (if g then p else 1)
    cases f <;> cases g <;> simp [hp]

/-- Every loop cocycle is determined by its nonidentity loop value. -/
theorem loop_value_square (c : (loopCoefficients H).Cocycle) :
    c.edge (show LoopView.only ⟶ LoopView.only from true) *
      c.edge (show LoopView.only ⟶ LoopView.only from true) = 1 := by
  have he := c.edge_comp (show LoopView.only ⟶ LoopView.only from true)
    (show LoopView.only ⟶ LoopView.only from true)
  change c.edge (show LoopView.only ⟶ LoopView.only from false) =
    c.edge (show LoopView.only ⟶ LoopView.only from true) *
      c.edge (show LoopView.only ⟶ LoopView.only from true) at he
  exact he.symm.trans (c.edge_id LoopView.only)

theorem loop_cocycle_reconstruction (c : (loopCoefficients H).Cocycle) :
    involutionCocycle (c.edge (show LoopView.only ⟶ LoopView.only from true))
      (loop_value_square c) = c := by
  apply GroupViewSystem.Cocycle.ext
  intro v w f
  cases v; cases w; cases f
  · exact (c.edge_id LoopView.only).symm
  · rfl

def loopCocycleEquiv : (loopCoefficients H).Cocycle ≃ {p : H // p * p = 1} where
  toFun c := ⟨c.edge (show LoopView.only ⟶ LoopView.only from true), loop_value_square c⟩
  invFun p := involutionCocycle p.val p.property
  left_inv := loop_cocycle_reconstruction
  right_inv _ := rfl

@[simp] theorem involution_edge (p : H) (hp : p * p = 1) :
    (involutionCocycle p hp).edge (show LoopView.only ⟶ LoopView.only from true) = p := rfl

/-- Orbit classes distinguish conjugacy, not equality of every local object. -/
theorem loop_class_eq_iff_conjugate (p q : H) (hp : p * p = 1) (hq : q * q = 1) :
    (loopCoefficients H).orbitClass ∅ (involutionCocycle p hp) =
      (loopCoefficients H).orbitClass ∅ (involutionCocycle q hq) ↔
      ∃ a : H, a * p * a⁻¹ = q := by
  rw [GroupViewSystem.orbitClass_eq_iff]
  constructor
  · rintro ⟨a, ha⟩
    exact ⟨a.val LoopView.only,
      congrArg (fun c => c.edge (show LoopView.only ⟶ LoopView.only from true)) ha⟩
  · rintro ⟨a, ha⟩
    refine ⟨⟨fun _ => a, by intro v; exact False.elim v.property⟩, ?_⟩
    apply GroupViewSystem.Cocycle.ext
    intro v w f
    cases f
    · change a * 1 * a⁻¹ = 1; group
    · exact ha

/-- Automorphisms at an involution are its centralizer. -/
theorem loop_stabilizer_iff (p : H) (hp : p * p = 1)
    (a : (loopCoefficients H).basedGauge ∅) :
    a ∈ (loopCoefficients H).stabilizer ∅ (involutionCocycle p hp) ↔
      a.val LoopView.only * p = p * a.val LoopView.only := by
  constructor
  · intro h
    have he := congrArg
      (fun c : (loopCoefficients H).Cocycle =>
        c.edge (show LoopView.only ⟶ LoopView.only from true)) h
    change a.val LoopView.only * p * (a.val LoopView.only)⁻¹ = p at he
    exact (mul_inv_eq_iff_eq_mul).mp he
  · intro h
    apply GroupViewSystem.Cocycle.ext
    intro v w f
    cases v; cases w; cases f
    · change a.val LoopView.only * 1 * (a.val LoopView.only)⁻¹ = 1; group
    · change a.val LoopView.only * p * (a.val LoopView.only)⁻¹ = p
      exact (mul_inv_eq_iff_eq_mul).mpr h

theorem involution_trivial_iff (p : H) (hp : p * p = 1) :
    (loopCoefficients H).orbitClass ∅ (involutionCocycle p hp) =
      (loopCoefficients H).neutralClass ∅ ↔ p = 1 := by
  have ht : involutionCocycle (1 : H) (one_mul 1) = (loopCoefficients H).trivial := by
    apply GroupViewSystem.Cocycle.ext
    intro v w f
    cases f <;> rfl
  change (loopCoefficients H).orbitClass ∅ (involutionCocycle p hp) =
    (loopCoefficients H).orbitClass ∅ (loopCoefficients H).trivial ↔ _
  rw [← ht, loop_class_eq_iff_conjugate]
  constructor
  · rintro ⟨a, ha⟩
    calc
      p = a⁻¹ * (a * p * a⁻¹) * a := by group
      _ = 1 := by rw [ha]; group
  · intro hp1; exact ⟨1, by rw [hp1]; group⟩

/-- A nontrivial loop cocycle is coherent transition data but has no global trivialization. -/
theorem involution_no_section (p : H) (hp : p * p = 1) (hne : p ≠ 1) :
    ¬ Nonempty (((loopCoefficients H).twistedViews (involutionCocycle p hp)).Ambient) := by
  rintro ⟨x⟩
  have hx := x.property LoopView.only LoopView.only true
  change p * x.val LoopView.only = x.val LoopView.only at hx
  apply hne
  exact mul_right_cancel (hx.trans (one_mul _).symm)

abbrev S3 := Equiv.Perm (Fin 3)
def transposition : S3 := Equiv.swap 0 1
def otherTransposition : S3 := Equiv.swap 1 2

theorem transposition_square : transposition * transposition = 1 := by decide
theorem otherTransposition_square : otherTransposition * otherTransposition = 1 := by decide
theorem transposition_nontrivial : transposition ≠ 1 := by decide
theorem transpositions_noncommute : transposition * otherTransposition ≠ otherTransposition * transposition := by decide

def trivialObject : (loopCoefficients S3).GaugeObject ∅ := ⟨(loopCoefficients S3).trivial⟩
def nontrivialObject : (loopCoefficients S3).GaugeObject ∅ :=
  ⟨involutionCocycle transposition transposition_square⟩

def constantGauge (a : S3) : (loopCoefficients S3).basedGauge ∅ :=
  ⟨fun _ => a, by intro v; exact False.elim v.property⟩

/-- Every permutation fixes the trivial cocycle, giving a genuine automorphism arrow. -/
def trivialAutomorphism (a : S3) : trivialObject ⟶ trivialObject :=
  ⟨constantGauge a, by
    apply GroupViewSystem.Cocycle.ext
    intro v w f
    change a * 1 * a⁻¹ = 1
    group⟩

theorem trivialAutomorphism_injective : Function.Injective trivialAutomorphism := by
  intro a b h
  exact congrArg (fun f : trivialObject ⟶ trivialObject => f.change.val LoopView.only) h

def trivialAutEquiv : S3 ≃ (trivialObject ⟶ trivialObject) where
  toFun := trivialAutomorphism
  invFun f := f.change.val LoopView.only
  left_inv _ := rfl
  right_inv f := by
    apply GroupViewSystem.GaugeObject.Hom.ext
    apply Subtype.ext
    funext v
    cases v
    rfl

/-- Automorphism composition is noncommutative in this actual cocycle groupoid. -/
theorem actual_automorphisms_noncommute :
    trivialAutomorphism transposition ≫ trivialAutomorphism otherTransposition ≠
      trivialAutomorphism otherTransposition ≫ trivialAutomorphism transposition := by
  intro h
  have he := congrArg (fun f : trivialObject ⟶ trivialObject => f.change.val LoopView.only) h
  exact transpositions_noncommute he.symm

theorem same_local_fibers_inequivalent : ¬ Nonempty (trivialObject ≅ nontrivialObject) := by
  intro h
  have he := ((loopCoefficients S3).iso_nonempty_iff_class ∅ trivialObject nontrivialObject).mp h
  have hn : (loopCoefficients S3).orbitClass ∅ (involutionCocycle transposition transposition_square) =
      (loopCoefficients S3).neutralClass ∅ := he.symm
  exact transposition_nontrivial ((involution_trivial_iff transposition transposition_square).mp hn)

theorem nontrivial_cocycle_not_trivializable :
    ¬ Nonempty (((loopCoefficients S3).twistedViews nontrivialObject.labels).Ambient) :=
  involution_no_section transposition transposition_square transposition_nontrivial

/-- Framing the only view forbids every nonidentity gauge, without identifying its cocycles. -/
theorem full_framing_gauge_unique (a : (loopCoefficients S3).basedGauge Set.univ) : a = 1 := by
  apply Subtype.ext
  funext v
  exact a.property ⟨v, Set.mem_univ v⟩

/-- The finite classification is checked by kernel-reduced decidable enumeration. -/
theorem s3_involutions (p : S3) :
    p * p = 1 ↔ p = 1 ∨ p = transposition ∨ p = otherTransposition ∨ p = Equiv.swap 0 2 := by
  revert p
  decide

theorem s3_nonidentity_involutions_conjugate (p : S3) (hp : p * p = 1) (hne : p ≠ 1) :
    ∃ a : S3, a * p * a⁻¹ = transposition := by
  have h : ∀ p : S3, p * p = 1 → p ≠ 1 → ∃ a : S3, a * p * a⁻¹ = transposition := by decide
  exact h p hp hne

/-- Every object lies in one of exactly two isomorphism classes; the classes are distinct above. -/
theorem s3_orbit_dichotomy (c : (loopCoefficients S3).Cocycle) :
    (loopCoefficients S3).orbitClass ∅ c = (loopCoefficients S3).neutralClass ∅ ∨
      (loopCoefficients S3).orbitClass ∅ c =
        (loopCoefficients S3).orbitClass ∅ nontrivialObject.labels := by
  let p := c.edge (show LoopView.only ⟶ LoopView.only from true)
  have hp : p * p = 1 := loop_value_square c
  have he : involutionCocycle p hp = c := loop_cocycle_reconstruction c
  by_cases h1 : p = 1
  · left
    rw [← he]
    exact (involution_trivial_iff p hp).mpr h1
  · right
    rw [← he]
    exact (loop_class_eq_iff_conjugate p transposition hp transposition_square).mpr
      (s3_nonidentity_involutions_conjugate p hp h1)

end CocycleExamples
end KomorebiSpace
