import PaperX.SimpleModuleSeparation
import PaperX.DenseTraceSeparation

/-! Character independence for arbitrary monoids in characteristic zero.
The arithmetic Frobenius-density input remains separate. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.GeneralCharacters
open scoped BigOperators MonoidAlgebra
section Algebra
variable {K G I : Type*} [Field K] [Monoid G] [Fintype I]
variable {W : I → Type*} [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]
variable [∀ i, FiniteDimensional K (W i)]

omit [Fintype I] [∀ i, FiniteDimensional K (W i)] in
theorem module_nonisomorphic (ρ : ∀ i, Representation K G (W i))
    (hne : ∀ i j, Nonempty ((ρ i).Equiv (ρ j)) → i = j) :
    ∀ i j, Nonempty ((ρ i).asModule ≃ₗ[K[G]] (ρ j).asModule) → i = j := by
  rintro i j ⟨e⟩
  let f := (Representation.IntertwiningMap.equivLinearMapAsModule (ρ i) (ρ j)).symm
    e.toLinearMap
  exact hne i j ⟨f.ofBijective e.bijective⟩

omit [Fintype I] [∀ i, FiniteDimensional K (W i)] in
theorem module_trace (ρ : ∀ i, Representation K G (W i)) (i : I) (a : K[G]) :
    LinearMap.trace K (ρ i).asModule (Module.toModuleEnd K (ρ i).asModule a) =
      LinearMap.trace K (W i) ((ρ i).asAlgebraHom a) := by
  have h : (ρ i).asModuleEquiv.conj (Module.toModuleEnd K (ρ i).asModule a) =
      (ρ i).asAlgebraHom a := by
    apply LinearMap.ext
    intro x
    rfl
  rw [← h, LinearMap.trace_conj']

omit [∀ i, FiniteDimensional K (W i)] in
/-- A linear combination vanishing on monoid elements vanishes on the actual monoid algebra. -/
theorem combination_on_algebra (ρ : ∀ i, Representation K G (W i)) (c : I → K)
    (hc : ∀ g, ∑ i, c i * (ρ i).character g = 0) (a : K[G]) :
    ∑ i, c i * LinearMap.trace K (W i) ((ρ i).asAlgebraHom a) = 0 := by
  induction a using MonoidAlgebra.induction_linear with
  | zero => simp
  | add a b ha hb => simp [map_add, mul_add, Finset.sum_add_distrib, ha, hb]
  | single g k =>
      simp only [Representation.asAlgebraHom_single, map_smul, smul_eq_mul]
      calc
        _ = k * ∑ i, c i * (ρ i).character g := by
          rw [Finset.mul_sum]
          apply Finset.sum_congr rfl
          intro i _
          simp [Representation.character, mul_left_comm]
        _ = 0 := by rw [hc, mul_zero]

/-- No finite-group or algebraically-closed-field hypothesis is needed here. -/
theorem independent_irreducible_characters [CharZero K]
    (ρ : ∀ i, Representation K G (W i)) [∀ i, (ρ i).IsIrreducible]
    (hne : ∀ i j, Nonempty ((ρ i).Equiv (ρ j)) → i = j) :
    LinearIndependent K (fun i => (ρ i).character) := by
  classical
  have hi := PaperX.SimpleModuleSeparation.independent_module_traces
    (K := K) (module_nonisomorphic ρ hne)
  rw [Fintype.linearIndependent_iff] at hi ⊢
  intro c hc
  apply hi c
  funext a
  simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply, module_trace]
  apply combination_on_algebra ρ c
  intro g
  simpa using congrFun hc g

end Algebra

section Topological
variable {K G I : Type*} [Field K] [Group G] [Fintype I]
variable {W : I → Type*} [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]
variable [∀ i, FiniteDimensional K (W i)]

/-- Joint continuity of the actual action gives continuous characters in coordinates. -/
theorem continuous_character_of_action [TopologicalSpace G] [TopologicalSpace K]
    [IsTopologicalRing K] {n : ℕ}
    (ρ : Representation K G (Fin n → K))
    (hρ : Continuous (fun p : G × (Fin n → K) => ρ p.1 p.2)) :
    Continuous ρ.character := by
  have he (g : G) : ρ.character g =
      ∑ i : Fin n, ρ g (Pi.single i 1) i := by
    rw [Representation.character, LinearMap.trace_eq_matrix_trace K (Pi.basisFun K (Fin n))]
    simp [Matrix.trace]
  have heq : ρ.character = (fun g => ∑ i : Fin n, ρ g (Pi.single i 1) i) := funext he
  rw [heq]
  apply continuous_finsetSum
  intro i _
  exact (continuous_apply i).comp (hρ.comp (continuous_id.prodMk continuous_const))

/-- General irreducible characters give the finite separator under the sole
remaining sampling hypothesis: density of the conjugacy-saturated samples. -/
theorem irreducible_dense_separator [CharZero K]
    [TopologicalSpace G] [TopologicalSpace K] [IsTopologicalRing K] [T2Space K]
    {X : Type*} [DecidableEq I]
    (ρ : ∀ i, Representation K G (W i)) [∀ i, (ρ i).IsIrreducible]
    (hne : ∀ i j, Nonempty ((ρ i).Equiv (ρ j)) → i = j)
    (hc : ∀ i, Continuous (ρ i).character) (s : X → G)
    (hd : DenseRange (fun p : X × G => p.2 * s p.1 * p.2⁻¹)) :
    ∃ v : I → X, Function.Injective v ∧
      (PaperX.FiniteSeparation.sampleMatrix (fun i x => (ρ i).character (s x)) v).det ≠ 0 := by
  apply PaperX.DenseTraceSeparation.finite_conjugacy_separator _ hc
    (independent_irreducible_characters ρ hne) s hd
  intro i g x
  exact (ρ i).char_conj (s x) g

end Topological
end PaperX.GeneralCharacters
