import PaperXII.CompanionForests
import Mathlib.Topology.Algebra.ContinuousMonoidHom
import Mathlib.Topology.Algebra.Group.Subgroup

/-! Concrete effectivity for compatible continuous representations.
Targets are actual inverse-limit groups with the subspace topology of the product.
Admissibility consists of specified finite-level predicates preserved by reduction.
This does not identify the limit with a particular adic matrix group or establish
arithmetic local conditions that have no supplied finite-level description. -/
set_option autoImplicit false
namespace PaperXII.InverseLimitRepresentations

open ContinuousMonoidHom PaperX.Compactness

variable {Γ : Type} [Group Γ] [TopologicalSpace Γ]
    {G : ℕ → Type} [∀ n, Group (G n)] [∀ n, TopologicalSpace (G n)]

/-- The actual subgroup of compatible tuples, with its inherited product-subspace topology. -/
def limit (q : ∀ n, G (n + 1) →ₜ* G n) : Subgroup (∀ n, G n) where
  carrier := {x | ∀ n, q n (x (n + 1)) = x n}
  one_mem' := by intro n; exact map_one (q n)
  mul_mem' := by
    intro x y hx hy n
    change q n (x (n + 1) * y (n + 1)) = x n * y n
    rw [map_mul, hx n, hy n]
  inv_mem' := by
    intro x hx n
    change q n (x (n + 1))⁻¹ = (x n)⁻¹
    rw [map_inv, hx n]

/-- Continuous projection from the actual limit group. -/
def coordinate (q : ∀ n, G (n + 1) →ₜ* G n) (n : ℕ) : limit q →ₜ* G n where
  toFun x := x.val n
  map_one' := rfl
  map_mul' _ _ := rfl
  continuous_toFun := (continuous_apply n).comp continuous_subtype_val

/-- Assemble a compatible family of continuous representations into one continuous representation. -/
def assemble (q : ∀ n, G (n + 1) →ₜ* G n) (ρ : ∀ n, Γ →ₜ* G n)
    (hρ : ∀ n, (q n).comp (ρ (n + 1)) = ρ n) : Γ →ₜ* limit q where
  toFun g := ⟨fun n ↦ ρ n g, fun n ↦ DFunLike.congr_fun (hρ n) g⟩
  map_one' := by apply Subtype.ext; funext n; exact map_one (ρ n)
  map_mul' g h := by apply Subtype.ext; funext n; exact map_mul (ρ n) g h
  continuous_toFun := (continuous_pi (fun n ↦ (ρ n).continuous)).subtype_mk _

/-- Reconstructed representations have exactly the supplied finite reductions. -/
theorem coordinate_assemble (q : ∀ n, G (n + 1) →ₜ* G n) (ρ : ∀ n, Γ →ₜ* G n)
    (hρ : ∀ n, (q n).comp (ρ (n + 1)) = ρ n) (n : ℕ) :
    (coordinate q n).comp (assemble q ρ hρ) = ρ n := by
  ext g
  rfl

/-- Agreement of all reductions determines the entire continuous representation. -/
theorem ext_of_coordinates (q : ∀ n, G (n + 1) →ₜ* G n)
    (ρ σ : Γ →ₜ* limit q)
    (h : ∀ n, (coordinate q n).comp ρ = (coordinate q n).comp σ) : ρ = σ := by
  apply ContinuousMonoidHom.ext
  intro g
  apply Subtype.ext
  funext n
  exact DFunLike.congr_fun (h n) g

/-- The forest consists of actual admissible continuous finite-level representations. -/
def forest (q : ∀ n, G (n + 1) →ₜ* G n) (A : ∀ n, (Γ →ₜ* G n) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((q n).comp ρ)) : Tower where
  Level n := {ρ : Γ →ₜ* G n // A n ρ}
  parent n ρ := ⟨(q n).comp ρ.val, hA n ρ.val ρ.property⟩

/-- Complete realizations are continuous representations satisfying every finite admissibility condition. -/
def Complete (q : ∀ n, G (n + 1) →ₜ* G n) (A : ∀ n, (Γ →ₜ* G n) → Prop) :=
  {ρ : Γ →ₜ* limit q // ∀ n, A n ((coordinate q n).comp ρ)}

/-- A complete realization reduces to a branch of its declared admissible forest. -/
def toBranch (q : ∀ n, G (n + 1) →ₜ* G n) (A : ∀ n, (Γ →ₜ* G n) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((q n).comp ρ))
    (ρ : Complete q A) : Branch (forest q A hA) where
  value n := ⟨(coordinate q n).comp ρ.val, ρ.property n⟩
  compatible n := by
    apply Subtype.ext
    ext g
    exact (ρ.val g).property n

/-- A branch reconstructs an actual continuous representation satisfying all finite conditions. -/
def fromBranch (q : ∀ n, G (n + 1) →ₜ* G n) (A : ∀ n, (Γ →ₜ* G n) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((q n).comp ρ))
    (b : Branch (forest q A hA)) : Complete q A :=
  ⟨assemble q (fun n ↦ (b.value n).val)
    (fun n ↦ congrArg Subtype.val (b.compatible n)), fun n ↦ by
      change A n (b.value n).val
      exact (b.value n).property⟩

/-- Reduction and reconstruction are inverse on complete representations. -/
theorem fromBranch_toBranch (q : ∀ n, G (n + 1) →ₜ* G n) (A : ∀ n, (Γ →ₜ* G n) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((q n).comp ρ)) (ρ : Complete q A) :
    fromBranch q A hA (toBranch q A hA ρ) = ρ := by
  apply Subtype.ext
  apply ext_of_coordinates q
  intro n
  rfl

/-- Reconstruction and reduction are inverse on branches. -/
theorem toBranch_fromBranch (q : ∀ n, G (n + 1) →ₜ* G n) (A : ∀ n, (Γ →ₜ* G n) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((q n).comp ρ)) (b : Branch (forest q A hA)) :
    toBranch q A hA (fromBranch q A hA b) = b := by
  apply CompanionForests.branch_ext
  intro n
  apply Subtype.ext
  ext g
  rfl

/-- The effectivity equivalence is constructed, not assumed as an interface field. -/
def realizationEquiv (q : ∀ n, G (n + 1) →ₜ* G n) (A : ∀ n, (Γ →ₜ* G n) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((q n).comp ρ)) :
    Complete q A ≃ Branch (forest q A hA) where
  toFun := toBranch q A hA
  invFun := fromBranch q A hA
  left_inv := fromBranch_toBranch q A hA
  right_inv := toBranch_fromBranch q A hA

/-- Finite nonempty admissible levels yield an actual continuous limit representation. -/
theorem exists_complete (q : ∀ n, G (n + 1) →ₜ* G n) (A : ∀ n, (Γ →ₜ* G n) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((q n).comp ρ))
    [∀ n, Finite {ρ : Γ →ₜ* G n // A n ρ}]
    (hne : ∀ n, Nonempty {ρ : Γ →ₜ* G n // A n ρ}) : Nonempty (Complete q A) := by
  let _ : ∀ n, Finite ((forest q A hA).Level n) := fun n ↦ inferInstanceAs
    (Finite {ρ : Γ →ₜ* G n // A n ρ})
  obtain ⟨b⟩ := CompanionForests.branch_exists (forest q A hA) hne
  exact ⟨fromBranch q A hA b⟩

/-- The constructed representation retains a declared fixed residual representation. -/
theorem exists_complete_with_root (q : ∀ n, G (n + 1) →ₜ* G n)
    (A : ∀ n, (Γ →ₜ* G n) → Prop)
    (hA : ∀ n ρ, A (n + 1) ρ → A n ((q n).comp ρ))
    [∀ n, Finite {ρ : Γ →ₜ* G n // A n ρ}]
    (hne : ∀ n, Nonempty {ρ : Γ →ₜ* G n // A n ρ})
    (root : Γ →ₜ* G 0) (hroot : ∀ ρ, A 0 ρ → ρ = root) :
    ∃ ρ : Complete q A, (coordinate q 0).comp ρ.val = root := by
  obtain ⟨ρ⟩ := exists_complete q A hA hne
  exact ⟨ρ, hroot _ (ρ.property 0)⟩

/-- Claim 10.4 for the concrete realization model: an empty level rules out completion. -/
theorem empty_level_no_complete (q : ∀ n, G (n + 1) →ₜ* G n)
    (A : ∀ n, (Γ →ₜ* G n) → Prop) (n : ℕ)
    (h : ¬ Nonempty {ρ : Γ →ₜ* G n // A n ρ}) : ¬ Nonempty (Complete q A) := by
  rintro ⟨ρ⟩
  exact h ⟨⟨(coordinate q n).comp ρ.val, ρ.property n⟩⟩

/-- All declared finite Frobenius labels survive reconstruction. -/
theorem finite_labels_preserved (q : ∀ n, G (n + 1) →ₜ* G n)
    (A : ∀ n, (Γ →ₜ* G n) → Prop) (ρ : Complete q A)
    {Ω : Type*} {L : ℕ → Type*} (frob : Ω → Γ)
    (label : ∀ n, G n → L n) (spine : ∀ n, Ω → L n)
    (hlabel : ∀ n σ, A n σ → ∀ v, label n (σ (frob v)) = spine n v) :
    ∀ n v, label n ((ρ.val (frob v)).val n) = spine n v := by
  intro n v
  exact hlabel n ((coordinate q n).comp ρ.val) (ρ.property n) v

/-- Simultaneous concrete reconstruction with coefficient groups varying across the index set. -/
theorem simultaneous_complete {I : Type} (H : I → ℕ → Type)
    [∀ i n, Group (H i n)] [∀ i n, TopologicalSpace (H i n)]
    (q : ∀ i n, H i (n + 1) →ₜ* H i n) (A : ∀ i n, (Γ →ₜ* H i n) → Prop)
    (hA : ∀ i n ρ, A i (n + 1) ρ → A i n ((q i n).comp ρ))
    [∀ i n, Finite {ρ : Γ →ₜ* H i n // A i n ρ}]
    (hne : ∀ i n, Nonempty {ρ : Γ →ₜ* H i n // A i n ρ}) :
    Nonempty (∀ i, Complete (q i) (A i)) := by
  classical
  exact ⟨fun i ↦ Classical.choice (exists_complete (q i) (A i) (hA i) (hne i))⟩

end PaperXII.InverseLimitRepresentations
