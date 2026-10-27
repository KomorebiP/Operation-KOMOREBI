import Mathlib.RingTheory.AdjoinRoot
import Mathlib.Algebra.CharP.Lemmas
import Mathlib.Data.ZMod.Basic
import Mathlib.RingTheory.RootsOfUnity.PrimitiveRoots
import Mathlib.Algebra.Polynomial.Degree.IsMonicOfDegree

open Polynomial

namespace Komorebi.StrongArtin.CyclicDefect

noncomputable section

/-- The scalar quotient-character deformation polynomial around the residual
trivial character. -/
def defectPolynomial (p : ℕ) (R : Type*) [CommRing R] : R[X] :=
  (X + C 1) ^ p - C 1

variable (p : ℕ) [Fact p.Prime]

/-- In residue characteristic `p`, the cyclic defect polynomial is exactly `X^p`.
Thus the `p` characteristic-zero branches coalesce into one nonreduced residual
fiber rather than remaining `p` distinct residual labels. -/
theorem defectPolynomial_zmod_eq_X_pow :
    defectPolynomial p (ZMod p) = (X : (ZMod p)[X]) ^ p := by
  rw [defectPolynomial]
  rw [add_pow_char]
  simp

/-- The exact special-fiber algebra for the prime-cyclic scalar defect. -/
abbrev SpecialFiber := AdjoinRoot ((X : (ZMod p)[X]) ^ p)

/-- Its distinguished cyclic-defect parameter. -/
abbrev u : SpecialFiber p := AdjoinRoot.root ((X : (ZMod p)[X]) ^ p)

omit [Fact p.Prime] in
/-- The cyclic defect parameter is nilpotent of order at most `p`. -/
theorem u_pow_eq_zero : (u p) ^ p = 0 := by
  change AdjoinRoot.root ((X : (ZMod p)[X]) ^ p) ^ p = 0
  have h := AdjoinRoot.eval₂_root ((X : (ZMod p)[X]) ^ p)
  simpa using h

/-- The special fiber has vector-space dimension exactly `p` over `F_p`. -/
theorem specialFiber_finrank :
    Module.finrank (ZMod p) (SpecialFiber p) = p := by
  let pb := AdjoinRoot.powerBasis' ((monic_X : (X : (ZMod p)[X]).Monic).pow p)
  rw [PowerBasis.finrank pb]
  simp [pb]


/-- The distinguished defect parameter is genuinely nonzero. Together with
`u_pow_eq_zero`, this identifies a nontrivial nilpotent direction in the special
fiber. -/
theorem u_ne_zero : u p ≠ 0 := by
  change AdjoinRoot.mk ((X : (ZMod p)[X]) ^ p) X ≠ 0
  apply AdjoinRoot.mk_ne_zero_of_natDegree_lt ((monic_X : (X : (ZMod p)[X]).Monic).pow p)
  · exact X_ne_zero
  · rw [natDegree_X, natDegree_X_pow]
    exact (Fact.out : p.Prime).one_lt

omit [Fact p.Prime] in
/-- Every algebra map from the special fiber to a reduced `F_p`-algebra kills
its nilpotent cyclic coordinate. -/
theorem algHom_u_eq_zero {S : Type*} [CommRing S] [Algebra (ZMod p) S]
    [IsReduced S] (φ : SpecialFiber p →ₐ[ZMod p] S) :
    φ (u p) = 0 := by
  apply eq_zero_of_pow_eq_zero (n := p)
  rw [← map_pow, u_pow_eq_zero p, map_zero]

omit [Fact p.Prime] in
/-- The special fiber has only one reduced-valued geometric point: any two
`F_p`-algebra maps from it to a reduced target agree. The multiplicity survives
only as nilpotent thickness. -/
theorem algHom_ext_reduced {S : Type*} [CommRing S] [Algebra (ZMod p) S]
    [IsReduced S] (φ ψ : SpecialFiber p →ₐ[ZMod p] S) : φ = ψ := by
  apply AdjoinRoot.algHom_ext
  rw [algHom_u_eq_zero p φ, algHom_u_eq_zero p ψ]


omit [Fact p.Prime] in
/-- Every `p`th root of unity gives a characteristic-zero branch of the same
cyclic defect polynomial after translating the residual point from `1` to `0`. -/
theorem primitiveRoot_branch_is_root {K : Type*} [CommRing K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) (j : ℕ) :
    (defectPolynomial p K).eval (ζ ^ j - 1) = 0 := by
  simp only [defectPolynomial, eval_sub, eval_pow, eval_add, eval_X, eval_C, sub_add_cancel]
  rw [← pow_mul, Nat.mul_comm j p, pow_mul, hζ.pow_eq_one, one_pow, sub_self]

omit [Fact p.Prime] in
/-- A primitive `p`th root produces `p` pairwise distinct translated branches
`ζ^j - 1`, indexed by `j : Fin p`. -/
theorem primitiveRoot_branches_injective {K : Type*} [CommRing K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    Function.Injective (fun j : Fin p => ζ ^ (j : ℕ) - 1) := by
  intro i j hij
  apply Fin.ext
  exact hζ.pow_inj i.isLt j.isLt (sub_left_injective hij)


/-- The characteristic-zero/generic algebra carrying the cyclic scalar branches. -/
abbrev GenericFiber (K : Type*) [CommRing K] := AdjoinRoot (defectPolynomial p K)

omit [Fact p.Prime] in
/-- Evaluation at the translated root `ζ^j - 1` defines one generic branch. -/
noncomputable def branchHom {K : Type*} [CommRing K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) (j : Fin p) :
    GenericFiber p K →ₐ[K] K :=
  AdjoinRoot.liftAlgHom (defectPolynomial p K) (AlgHom.id K K) (ζ ^ (j : ℕ) - 1)
    (by simpa [Polynomial.eval₂_id] using primitiveRoot_branch_is_root p ζ hζ (j : ℕ))

omit [Fact p.Prime] in
/-- The `p` generic evaluation maps are pairwise distinct. -/
theorem branchHom_injective {K : Type*} [CommRing K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    Function.Injective (branchHom p ζ hζ) := by
  intro i j hij
  apply primitiveRoot_branches_injective p ζ hζ
  have hroot := DFunLike.congr_fun hij (AdjoinRoot.root (defectPolynomial p K))
  simpa [branchHom] using hroot


/-- The defect polynomial is monic of degree exactly `p`. -/
theorem defectPolynomial_isMonicOfDegree {R : Type*} [CommRing R] [Nontrivial R] :
    IsMonicOfDegree (defectPolynomial p R) p := by
  rw [defectPolynomial]
  have hpow := (isMonicOfDegree_X_add_one (1 : R)).pow p
  have hpow' : IsMonicOfDegree ((X + C (1 : R)) ^ p) p := by
    simpa using hpow
  apply hpow'.sub
  rw [natDegree_C]
  exact (Fact.out : p.Prime).pos

/-- The generic cyclic-defect algebra is finite free of rank `p`. -/
theorem genericFiber_finrank {K : Type*} [Field K] :
    Module.finrank K (GenericFiber p K) = p := by
  let pb := AdjoinRoot.powerBasis' (defectPolynomial_isMonicOfDegree p (R := K)).monic
  rw [PowerBasis.finrank pb]
  exact (defectPolynomial_isMonicOfDegree p (R := K)).natDegree_eq

/-- The special-fiber nilpotent has exact order `p`: the `(p-1)`st power is
nonzero while the `p`th power vanishes. -/
theorem u_pow_pred_ne_zero : (u p) ^ (p - 1) ≠ 0 := by
  change AdjoinRoot.mk ((X : (ZMod p)[X]) ^ p) (X ^ (p - 1)) ≠ 0
  apply AdjoinRoot.mk_ne_zero_of_natDegree_lt ((monic_X : (X : (ZMod p)[X]).Monic).pow p)
  · exact ((monic_X : (X : (ZMod p)[X]).Monic).pow (p - 1)).ne_zero
  · rw [natDegree_X_pow, natDegree_X_pow]
    exact Nat.sub_one_lt (Fact.out : p.Prime).ne_zero


/-- Any coefficient reduction into the prime field sends the universal cyclic
defect polynomial to the single residual polynomial `X^p`. -/
theorem map_defectPolynomial_to_zmod {R : Type*} [CommRing R]
    (φ : R →+* ZMod p) :
    (defectPolynomial p R).map φ = (X : (ZMod p)[X]) ^ p := by
  rw [defectPolynomial, Polynomial.map_sub, Polynomial.map_pow, Polynomial.map_add,
    Polynomial.map_X, Polynomial.map_C, map_one]
  exact defectPolynomial_zmod_eq_X_pow p

/-- Over every nontrivial coefficient ring, the cyclic defect algebra is finite
free of rank `p`; this is the algebraic flatness input for retaining the cyclic
direction during patching. -/
theorem defectAlgebra_free {R : Type*} [CommRing R] [Nontrivial R] :
    Module.Free R (AdjoinRoot (defectPolynomial p R)) :=
  (defectPolynomial_isMonicOfDegree p (R := R)).monic.free_adjoinRoot

/-- The same algebra is finite over the coefficient ring. -/
theorem defectAlgebra_finite {R : Type*} [CommRing R] [Nontrivial R] :
    Module.Finite R (AdjoinRoot (defectPolynomial p R)) :=
  (defectPolynomial_isMonicOfDegree p (R := R)).monic.finite_adjoinRoot


omit [Fact p.Prime] in
/-- In the generic defect algebra, the translated coordinate `1+u` is a
`p`th root of unity. -/
theorem one_add_genericRoot_pow_eq_one {K : Type*} [Field K] :
    (AdjoinRoot.root (defectPolynomial p K) + 1) ^ p = 1 := by
  have h := AdjoinRoot.mk_self (f := defectPolynomial p K)
  rw [defectPolynomial, map_sub, map_pow, map_add, AdjoinRoot.mk_X, AdjoinRoot.mk_C] at h
  exact sub_eq_zero.mp h


omit [Fact p.Prime] in
/-- Evaluation formula for the cyclic defect polynomial. -/
theorem eval₂_defectPolynomial {R S : Type*} [CommRing R] [CommRing S]
    (φ : R →+* S) (x : S) :
    (defectPolynomial p R).eval₂ φ x = (x + φ 1) ^ p - φ 1 := by
  rw [defectPolynomial, Polynomial.eval₂_sub, Polynomial.eval₂_pow,
    Polynomial.eval₂_add, Polynomial.eval₂_X, Polynomial.eval₂_C]

omit [Fact p.Prime] in
/-- Twisting the generic cyclic coordinate by any `p`th root of unity preserves
the defining equation. -/
theorem twisted_genericRoot_is_root {K : Type*} [Field K]
    (ζ : K) (hζ : ζ ^ p = 1) :
    (defectPolynomial p K).eval₂
      (AdjoinRoot.of (defectPolynomial p K))
      ((AdjoinRoot.of (defectPolynomial p K) ζ) *
        (AdjoinRoot.root (defectPolynomial p K) + 1) - 1) = 0 := by
  rw [eval₂_defectPolynomial]
  rw [map_one, sub_add_cancel, mul_pow]
  rw [← map_pow, hζ, map_one, one_mul, one_add_genericRoot_pow_eq_one p, sub_self]


/-- The quotient-character twist is an algebra endomorphism of the generic
defect algebra. -/
noncomputable def twistHom {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    AdjoinRoot (defectPolynomial p K) →ₐ[K] AdjoinRoot (defectPolynomial p K) :=
  AdjoinRoot.liftAlgHom (defectPolynomial p K)
    (Algebra.ofId K (AdjoinRoot (defectPolynomial p K)))
    ((AdjoinRoot.of (defectPolynomial p K) ζ) *
      (AdjoinRoot.root (defectPolynomial p K) + 1) - 1)
    (by simpa using twisted_genericRoot_is_root p ζ hζ.pow_eq_one)

omit [Fact p.Prime] in
@[simp] theorem twistHom_root {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    twistHom p ζ hζ (AdjoinRoot.root (defectPolynomial p K)) =
      (AdjoinRoot.of (defectPolynomial p K) ζ) *
        (AdjoinRoot.root (defectPolynomial p K) + 1) - 1 := by
  simp [twistHom]


omit [Fact p.Prime] in
@[simp] theorem twistHom_of {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) (a : K) :
    twistHom p ζ hζ (AdjoinRoot.of (defectPolynomial p K) a) =
      AdjoinRoot.of (defectPolynomial p K) a := by
  rw [← AdjoinRoot.algebraMap_eq]
  exact (twistHom p ζ hζ).commutes a

/-- Twisting by `ζ` after twisting by `ζ⁻¹` is the identity. -/
theorem twistHom_comp_inv {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    (twistHom p ζ hζ).comp (twistHom p ζ⁻¹ hζ.inv) =
      AlgHom.id K (AdjoinRoot (defectPolynomial p K)) := by
  apply AdjoinRoot.algHom_ext
  simp only [AlgHom.comp_apply, twistHom_root, twistHom_of, map_sub, map_mul, map_add, map_one, AlgHom.id_apply]
  rw [sub_add_cancel, ← mul_assoc, ← map_mul, inv_mul_cancel₀ (hζ.ne_zero (Fact.out : p.Prime).ne_zero),
    map_one, one_mul]
  simp

/-- Twisting by `ζ⁻¹` after twisting by `ζ` is the identity. -/
theorem twistHom_inv_comp {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    (twistHom p ζ⁻¹ hζ.inv).comp (twistHom p ζ hζ) =
      AlgHom.id K (AdjoinRoot (defectPolynomial p K)) := by
  apply AdjoinRoot.algHom_ext
  simp only [AlgHom.comp_apply, twistHom_root, twistHom_of, map_sub, map_mul, map_add, map_one, AlgHom.id_apply]
  rw [sub_add_cancel, ← mul_assoc, ← map_mul, mul_inv_cancel₀ (hζ.ne_zero (Fact.out : p.Prime).ne_zero),
    map_one, one_mul]
  simp

/-- The quotient-character twist acts by an algebra automorphism on the generic
defect algebra. -/
noncomputable def twistEquiv {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    AdjoinRoot (defectPolynomial p K) ≃ₐ[K] AdjoinRoot (defectPolynomial p K) :=
  AlgEquiv.ofAlgHom (twistHom p ζ hζ) (twistHom p ζ⁻¹ hζ.inv)
    (twistHom_comp_inv p ζ hζ) (twistHom_inv_comp p ζ hζ)


omit [Fact p.Prime] in
/-- On a generic evaluation branch, applying one quotient twist multiplies the
underlying `p`th root by `ζ`; at the translated coordinate this is the next
cyclic branch value. -/
theorem branchHom_comp_twist_root {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) (j : Fin p) :
    ((branchHom p ζ hζ j).comp (twistHom p ζ hζ))
      (AdjoinRoot.root (defectPolynomial p K)) =
        ζ ^ ((j : ℕ) + 1) - 1 := by
  simp only [AlgHom.comp_apply, twistHom_root]
  rw [map_sub, map_mul, map_add, map_one]
  simp only [branchHom, AdjoinRoot.liftAlgHom_root, AdjoinRoot.liftAlgHom_of,
    AlgHom.id_apply]
  rw [sub_add_cancel]
  simp [pow_succ']


omit [Fact p.Prime] in
/-- Away from the wrap point, one twist sends the `j`th generic evaluation map
to the `(j+1)`st one. -/
theorem branchHom_comp_twist_eq_succ_of_lt {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) (j : Fin p)
    (hj : (j : ℕ) + 1 < p) :
    (branchHom p ζ hζ j).comp (twistHom p ζ hζ) =
      branchHom p ζ hζ ⟨(j : ℕ) + 1, hj⟩ := by
  apply AdjoinRoot.algHom_ext
  rw [branchHom_comp_twist_root p ζ hζ j]
  simp [branchHom]

/-- At the last branch, one further twist wraps to branch zero. -/
theorem branchHom_comp_twist_last_eq_zero {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p) :
    (branchHom p ζ hζ ⟨p - 1, Nat.sub_one_lt (Fact.out : p.Prime).ne_zero⟩).comp
      (twistHom p ζ hζ) =
      branchHom p ζ hζ ⟨0, (Fact.out : p.Prime).pos⟩ := by
  apply AdjoinRoot.algHom_ext
  rw [branchHom_comp_twist_root p ζ hζ]
  simp only [branchHom, AdjoinRoot.liftAlgHom_root]
  rw [Nat.sub_add_cancel (Fact.out : p.Prime).one_le, hζ.pow_eq_one]
  simp

end
end Komorebi.StrongArtin.CyclicDefect

#print axioms Komorebi.StrongArtin.CyclicDefect.defectPolynomial_zmod_eq_X_pow
#print axioms Komorebi.StrongArtin.CyclicDefect.u_pow_eq_zero
#print axioms Komorebi.StrongArtin.CyclicDefect.specialFiber_finrank

#print axioms Komorebi.StrongArtin.CyclicDefect.u_ne_zero
#print axioms Komorebi.StrongArtin.CyclicDefect.algHom_u_eq_zero
#print axioms Komorebi.StrongArtin.CyclicDefect.algHom_ext_reduced

#print axioms Komorebi.StrongArtin.CyclicDefect.primitiveRoot_branch_is_root
#print axioms Komorebi.StrongArtin.CyclicDefect.primitiveRoot_branches_injective

#print axioms Komorebi.StrongArtin.CyclicDefect.branchHom_injective

#print axioms Komorebi.StrongArtin.CyclicDefect.defectPolynomial_isMonicOfDegree
#print axioms Komorebi.StrongArtin.CyclicDefect.genericFiber_finrank
#print axioms Komorebi.StrongArtin.CyclicDefect.u_pow_pred_ne_zero

#print axioms Komorebi.StrongArtin.CyclicDefect.map_defectPolynomial_to_zmod
#print axioms Komorebi.StrongArtin.CyclicDefect.defectAlgebra_free
#print axioms Komorebi.StrongArtin.CyclicDefect.defectAlgebra_finite

#print axioms Komorebi.StrongArtin.CyclicDefect.twistHom_comp_inv
#print axioms Komorebi.StrongArtin.CyclicDefect.twistEquiv

#print axioms Komorebi.StrongArtin.CyclicDefect.branchHom_comp_twist_root

#print axioms Komorebi.StrongArtin.CyclicDefect.branchHom_comp_twist_eq_succ_of_lt
#print axioms Komorebi.StrongArtin.CyclicDefect.branchHom_comp_twist_last_eq_zero
