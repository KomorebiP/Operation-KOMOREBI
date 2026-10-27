module
public import Mathlib.LinearAlgebra.FreeModule.PID
public import Mathlib.LinearAlgebra.Dimension.Constructions
public import Mathlib.Data.ZMod.Basic
public import Mathlib.Tactic

@[expose] public section
set_option autoImplicit false
set_option linter.unusedSimpArgs false
namespace KomorebiPadic
open scoped BigOperators

/-- A generating list of length n, encoded by its surjective synthesis map. -/
def HasGenerators (R M : Type*) [Semiring R] [AddCommMonoid M] [Module R M]
    (n : ℕ) : Prop :=
  ∃ g : Fin n → M, Function.Surjective (Fintype.linearCombination R g)

/-- Quotients cannot require more generators than a given generating list. -/
theorem HasGenerators.map {R M N : Type*} [CommRing R] [AddCommGroup M]
    [AddCommGroup N] [Module R M] [Module R N] {n : ℕ}
    (h : HasGenerators R M n) (f : M →ₗ[R] N) (hf : Function.Surjective f) :
    HasGenerators R N n := by
  obtain ⟨g,hg⟩ := h
  refine ⟨fun i => f (g i), ?_⟩
  intro y
  obtain ⟨x,rfl⟩ := hf y
  obtain ⟨a,ha⟩ := hg x
  refine ⟨a,?_⟩
  simpa [Fintype.linearCombination_apply, map_sum, map_smul] using congrArg f ha

/-- Every submodule of a d-coordinate free residue module has at most d generators.
The proof lifts to an integer lattice, so no reduction to a field discards torsion. -/
theorem zmod_submodule_generators (m d : ℕ)
    (U : Submodule (ZMod m) (Fin d → ZMod m)) :
    ∃ n ≤ d, HasGenerators (ZMod m) U n := by
  classical
  let red : (Fin d → ℤ) →ₗ[ℤ] (Fin d → ZMod m) := {
    toFun := fun z i => (z i : ZMod m)
    map_add' := by intro x y; ext i; simp
    map_smul' := by intro a x; ext i; simp [Int.cast_smul_eq_zsmul] }
  let V : Submodule ℤ (Fin d → ℤ) := (U.restrictScalars ℤ).comap red
  let f : V →ₗ[ℤ] U := {
    toFun := fun x => ⟨red x.val, x.property⟩
    map_add' := by intro x y; apply Subtype.ext; exact red.map_add x.val y.val
    map_smul' := by intro a x; apply Subtype.ext; exact red.map_smul a x.val }
  have hf : Function.Surjective f := by
    intro u
    choose z hz using fun i : Fin d => ZMod.intCast_surjective (u.val i)
    have he : red z = u.val := by funext i; exact hz i
    have hv : z ∈ V := by change red z ∈ U; rw [he]; exact u.property
    refine ⟨⟨z,hv⟩,?_⟩
    apply Subtype.ext
    exact he
  obtain ⟨n,b⟩ := Submodule.basisOfPid (Pi.basisFun ℤ (Fin d)) V
  have hn : n ≤ d := by
    have h := Submodule.finrank_le V
    rw [Module.finrank_eq_card_basis b, Fintype.card_fin, Module.finrank_fin_fun] at h
    exact h
  refine ⟨n,hn,fun i => f (b i),?_⟩
  intro u
  obtain ⟨v,hv⟩ := hf u
  refine ⟨fun i => ((b.repr v) i : ZMod m),?_⟩
  calc
    Fintype.linearCombination (ZMod m) (fun i => f (b i))
        (fun i => ((b.repr v) i : ZMod m)) = f (∑ i, (b.repr v) i • b i) := by
      simp only [Fintype.linearCombination_apply, map_sum, map_smul, Int.cast_smul_eq_zsmul]
    _ = u := by rw [b.sum_repr, hv]

/-- A submodule lying in the image of d free coordinates has at most d generators. -/
theorem zmod_submodule_of_range_generators {M : Type*} [AddCommGroup M]
    (m d : ℕ) [Module (ZMod m) M] (f : (Fin d → ZMod m) →ₗ[ZMod m] M)
    (U : Submodule (ZMod m) M) (hU : U ≤ f.range) :
    ∃ n ≤ d, HasGenerators (ZMod m) U n := by
  let V := U.comap f
  let q : V →ₗ[ZMod m] U := LinearMap.codRestrict U (f.comp V.subtype)
    (fun x => x.property)
  have hq : Function.Surjective q := by
    intro u
    obtain ⟨x,hx⟩ := LinearMap.mem_range.mp (hU u.property)
    have hm : x ∈ V := by change f x ∈ U; rw [hx]; exact u.property
    exact ⟨⟨x,hm⟩,Subtype.ext hx⟩
  obtain ⟨n,hn,hg⟩ := zmod_submodule_generators m d V
  exact ⟨n,hn,hg.map q hq⟩

/-- A concrete finite spanning envelope is enough for a residue-module bound. -/
theorem zmod_submodule_of_span_generators {M : Type*} [AddCommGroup M]
    (m d : ℕ) [Module (ZMod m) M] (g : Fin d → M)
    (U : Submodule (ZMod m) M) (hU : U ≤ Submodule.span (ZMod m) (Set.range g)) :
    ∃ n ≤ d, HasGenerators (ZMod m) U n := by
  apply zmod_submodule_of_range_generators m d (Fintype.linearCombination (ZMod m) g) U
  simpa only [Fintype.range_linearCombination] using hU

end KomorebiPadic
