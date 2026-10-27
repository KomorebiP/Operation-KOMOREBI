import PaperXI.SchurScalar
import PaperXI.RepresentationStability
import Mathlib.LinearAlgebra.TensorProduct.Map
import Mathlib.LinearAlgebra.TensorProduct.Basis

/-!
# Reverse Clifford tensor irreducibility

The prescribed extension factor is tensored with an irreducible quotient
representation. The resulting action is irreducible; no irreducibility of the
tensor product is assumed. The argument uses Jacobson density on the actual
normal-subgroup action.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.GallagherTensorIrreducibility58

open Representation
open scoped TensorProduct MonoidAlgebra

variable {G W : Type*} [Group G] [AddCommGroup W] [Module ℂ W]
variable [FiniteDimensional ℂ W]

/-- An actual finite-dimensional complex irreducible action spans all operators. -/
theorem algebraAction_surjective (ρ : Representation ℂ G W) [IsIrreducible ρ] :
    Function.Surjective ρ.asAlgebraHom := by
  classical
  intro F
  let M := ρ.asModule
  let E := ρ.asModuleEquiv
  let T : M →ₗ[ℂ] M := E.symm.toLinearMap.comp (F.comp E.toLinearMap)
  let T' : Module.End (Module.End ℂ[G] M) M :=
    { toFun := T
      map_add' := T.map_add
      map_smul' := by
        intro a x
        obtain ⟨c, rfl⟩ :=
          (IsSimpleModule.algebraMap_end_bijective_of_isAlgClosed
            (A := ℂ[G]) (V := M) ℂ).surjective a
        exact T.map_smul c x }
  let b := Module.finBasis ℂ M
  obtain ⟨r, hr⟩ := jacobson_density T' (Finset.univ.image b)
  refine ⟨r, ?_⟩
  have he : T = (E.symm.toLinearMap.comp ((ρ.asAlgebraHom r).comp E.toLinearMap)) := by
    apply b.ext
    intro i
    have h := hr (b i) (Finset.mem_image.mpr ⟨i, Finset.mem_univ i, rfl⟩)
    exact h
  ext w
  have h := LinearMap.congr_fun he (E.symm w)
  have hh := congrArg E h
  simpa [T] using hh.symm

variable {U Q : Type*} [AddCommGroup U] [Module ℂ U] [Group Q]

omit [FiniteDimensional ℂ W] in
/-- Stability under the first-factor group action implies stability under its
actual group-algebra action. -/
theorem stable_tensor_algebra (ρ : Representation ℂ G W)
    (S : Submodule ℂ (W ⊗[ℂ] U))
    (hS : ∀ g x, x ∈ S → TensorProduct.map (ρ g) LinearMap.id x ∈ S)
    (r : ℂ[G]) (x : W ⊗[ℂ] U) (hx : x ∈ S) :
    TensorProduct.map (ρ.asAlgebraHom r) LinearMap.id x ∈ S := by
  induction r using MonoidAlgebra.induction_on with
  | of g => simpa using hS g x hx
  | add a b ha hb =>
    simpa only [map_add, TensorProduct.map_add_left, LinearMap.add_apply] using S.add_mem ha hb
  | smul c a ha =>
    simpa only [map_smul, TensorProduct.map_smul_left, LinearMap.smul_apply] using S.smul_mem c ha

/-- On an irreducible finite-dimensional first factor, every operator on that
factor preserves any subspace stable under the group action. -/
theorem stable_tensor_end (ρ : Representation ℂ G W) [IsIrreducible ρ]
    (S : Submodule ℂ (W ⊗[ℂ] U))
    (hS : ∀ g x, x ∈ S → TensorProduct.map (ρ g) LinearMap.id x ∈ S)
    (F : Module.End ℂ W) (x : W ⊗[ℂ] U) (hx : x ∈ S) :
    TensorProduct.map F LinearMap.id x ∈ S := by
  obtain ⟨r, rfl⟩ := algebraAction_surjective ρ F
  exact stable_tensor_algebra ρ S hS r x hx

omit [FiniteDimensional ℂ W] in
/-- A basis coefficient is extracted by an actual first-factor rank-one operator. -/
theorem map_rankOne {ι : Type*} [DecidableEq ι] (b : Module.Basis ι ℂ W)
    (i : ι) (w : W) (x : W ⊗[ℂ] U) :
    TensorProduct.map ((b.coord i).smulRight w) LinearMap.id x =
      w ⊗ₜ[ℂ] (TensorProduct.equivFinsuppOfBasisLeft b x i) := by
  induction x using TensorProduct.induction_on with
  | zero => simp
  | add x y hx hy => simp [hx, hy, TensorProduct.tmul_add]
  | tmul v u =>
    simp [TensorProduct.smul_tmul]

omit [FiniteDimensional ℂ W] in
/-- The literal multiplicity subspace belonging to a tensor subspace. -/
def multiplicitySubspace (S : Submodule ℂ (W ⊗[ℂ] U)) : Submodule ℂ U where
  carrier := {u | ∀ w : W, w ⊗ₜ[ℂ] u ∈ S}
  zero_mem' := by intro w; simp
  add_mem' := by intro u v hu hv w; simpa [TensorProduct.tmul_add] using S.add_mem (hu w) (hv w)
  smul_mem' := by intro c u hu w; simpa [TensorProduct.tmul_smul] using S.smul_mem c (hu w)

/-- Reverse Clifford/Gallagher irreducibility on the actual tensor space.
The second factor is trivial on N and irreducible on its surjective quotient;
only the restriction of the prescribed first factor to N must be irreducible. -/
theorem tensor_irreducible (N : Subgroup G) (q : G →* Q)
    (hq : Function.Surjective q) (hN : N ≤ q.ker)
    (κ : Representation ℂ G W) (σ : Representation ℂ Q U)
    [IsIrreducible (κ.comp N.subtype)] [IsIrreducible σ] :
    IsIrreducible (κ.tprod (σ.comp q)) := by
  classical
  let : Nontrivial W := GeneratedIrreducibility.nontrivial_space (κ.comp N.subtype)
  let : Nontrivial U := GeneratedIrreducibility.nontrivial_space σ
  let b := Module.finBasis ℂ W
  let : Nonempty (Fin (Module.finrank ℂ W)) := b.index_nonempty
  let : Nontrivial (W ⊗[ℂ] U) :=
    (TensorProduct.equivFinsuppOfBasisLeft b).symm.injective.nontrivial
  apply RepresentationStability.irreducible_of_stable
  intro S hS
  have hSN : ∀ n : N, ∀ x, x ∈ S →
      TensorProduct.map ((κ.comp N.subtype) n) LinearMap.id x ∈ S := by
    intro n x hx
    have hn : q n = 1 := hN n.property
    have h := hS n x hx
    change TensorProduct.map (κ n) (σ (q n)) x ∈ S at h
    rw [hn, map_one] at h
    exact h
  have hL : RepresentationStability.Stable σ (multiplicitySubspace S) := by
    intro a u hu w
    obtain ⟨g, rfl⟩ := hq a
    have h := hS g (κ g⁻¹ w ⊗ₜ[ℂ] u) (hu (κ g⁻¹ w))
    simpa [Representation.tprod_apply] using h
  rcases RepresentationStability.eq_bot_or_top σ (multiplicitySubspace S) hL with hb | ht
  · left
    apply le_antisymm _ bot_le
    intro x hx
    have hc (i : Fin (Module.finrank ℂ W)) :
        TensorProduct.equivFinsuppOfBasisLeft b x i ∈ multiplicitySubspace S := by
      intro w
      rw [← map_rankOne b i w x]
      exact stable_tensor_end (κ.comp N.subtype) S hSN _ x hx
    have hz : TensorProduct.equivFinsuppOfBasisLeft b x = 0 := by
      ext i
      have h := hc i
      rw [hb] at h
      exact h
    exact (TensorProduct.equivFinsuppOfBasisLeft b).injective (hz.trans (map_zero _).symm)
  · right
    apply top_unique
    intro x htop
    clear htop
    induction x using TensorProduct.induction_on with
    | zero => exact S.zero_mem
    | add x y hx hy => exact S.add_mem hx hy
    | tmul w u =>
      have hu : u ∈ multiplicitySubspace S := ht ▸ Submodule.mem_top
      exact hu w

/-- The exact normal-subgroup quotient specialization used in compact types. -/
theorem quotient_tensor_irreducible (N : Subgroup G) [N.Normal]
    (κ : Representation ℂ G W) (σ : Representation ℂ (G ⧸ N) U)
    [IsIrreducible (κ.comp N.subtype)] [IsIrreducible σ] :
    IsIrreducible (κ.tprod (σ.comp (QuotientGroup.mk' N))) :=
  tensor_irreducible N (QuotientGroup.mk' N) QuotientGroup.mk_surjective
    (by intro n hn; exact (QuotientGroup.eq_one_iff n).mpr hn) κ σ

end PaperXI.GallagherTensorIrreducibility58
