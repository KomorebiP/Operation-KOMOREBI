module
public import Mathlib.LinearAlgebra.Basis.VectorSpace
public import Mathlib.LinearAlgebra.Dimension.Constructions
public import Mathlib.Logic.Equiv.Fintype
public import Mathlib.Algebra.Field.ZMod

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialMinorSelection

variable {K : Type*} [Field K] {d e q : ℕ}

/-- A surjective finite-dimensional linear map has a surjective square selection
of its actual coordinate columns. -/
theorem exists_selected_columns
    (A : (Fin d → K) →ₗ[K] (Fin e → K)) (hA : Function.Surjective A) :
    ∃ s : Fin e → Fin d, Function.Injective s ∧
      Function.Surjective (fun u : Fin e → K => ∑ k, u k • A (Pi.single (s k) 1)) := by
  classical
  let v : Fin d → (Fin e → K) := fun i => A (Pi.single i 1)
  have hv : Submodule.span K (Set.range v) = ⊤ := by
    apply eq_top_iff.mpr
    intro y _
    obtain ⟨x, rfl⟩ := hA y
    have hsum : ∑ i, x i • v i = A x := by
      dsimp [v]
      simp only [← map_smul, ← map_sum]
      congr 1
      simpa only [Pi.basisFun_repr, Pi.basisFun_apply] using
        (Pi.basisFun K (Fin d)).sum_repr x
    rw [← hsum]
    exact Submodule.sum_mem _ (fun i _ => Submodule.smul_mem _ _
      (Submodule.subset_span (Set.mem_range_self i)))
  obtain ⟨κ, a, ha, hspan, hli⟩ := exists_linearIndependent' K v
  let : Fintype κ := Fintype.ofInjective a ha
  let b : Module.Basis κ K (Fin e → K) := Module.Basis.mk hli (by rw [hspan, hv])
  have hcard : Fintype.card κ = e := by
    rw [← Module.finrank_eq_card_basis b, Module.finrank_pi, Fintype.card_fin]
  let ε : Fin e ≃ κ := Fintype.equivOfCardEq (by simp only [Fintype.card_fin, hcard])
  let c : Module.Basis (Fin e) K (Fin e → K) := b.reindex ε.symm
  refine ⟨a ∘ ε, ha.comp ε.injective, ?_⟩
  intro y
  refine ⟨fun i => c.repr y i, ?_⟩
  simpa only [c, Module.Basis.reindex_apply, Equiv.symm_symm, b,
    Module.Basis.mk_apply, Function.comp_apply, v] using c.sum_repr y

/-- A coordinate selection can be extended to a permutation, putting a
surjective square block in the first coordinates. -/
theorem exists_permuted_columns
    (A : (Fin (e + q) → K) →ₗ[K] (Fin e → K)) (hA : Function.Surjective A) :
    ∃ σ : Equiv.Perm (Fin (e + q)),
      Function.Surjective (fun u : Fin e → K =>
        ∑ k, u k • A (Pi.single (σ (Fin.castAdd q k)) 1)) := by
  obtain ⟨s, hs, hsurj⟩ := exists_selected_columns A hA
  obtain ⟨σ, hσ⟩ := Equiv.Perm.exists_extending_pair (Fin.castAdd q) s
    (Fin.castAdd_injective e q) hs
  refine ⟨σ, ?_⟩
  simpa only [hσ] using hsurj

/-- Prime-field form used for an actual polynomial Jacobian modulo p. -/
theorem exists_prime_permuted_columns (p : ℕ) [Fact (Nat.Prime p)]
    (A : (Fin (e + q) → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p))
    (hA : Function.Surjective A) :
    ∃ σ : Equiv.Perm (Fin (e + q)),
      Function.Surjective (fun u : Fin e → ZMod p =>
        ∑ k, u k • A (Pi.single (σ (Fin.castAdd q k)) 1)) :=
  exists_permuted_columns A hA

end Komorebi.PolynomialMinorSelection
