import Mathlib.RepresentationTheory.Intertwining
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic

/-!
# The actual standard representation of `S₃`

The coordinates used here are the basis `(1,-1,0), (0,1,-1)` of the
sum-zero submodule of the three-letter permutation representation.
All constructions work over an arbitrary commutative coefficient ring.
-/

namespace PaperXII.S3Standard

open Matrix

instance primeSeven : Fact (Nat.Prime 7) := ⟨by decide⟩

abbrev Group := Equiv.Perm (Fin 3)
abbrev Space (k : Type*) := Fin 2 → k

variable (k : Type*) [CommRing k]

/-- Coordinate inclusion into the three-letter permutation module. -/
def embed : Space k →ₗ[k] (Fin 3 → k) where
  toFun v := ![v 0, -v 0 + v 1, -v 1]
  map_add' v w := by ext i; fin_cases i <;> simp <;> ring
  map_smul' c v := by ext i; fin_cases i <;> simp [mul_add]

/-- The inverse coordinates on sum-zero vectors. -/
def project : (Fin 3 → k) →ₗ[k] Space k where
  toFun w := ![w 0, -w 2]
  map_add' v w := by ext i; fin_cases i <;> simp [add_comm]
  map_smul' c v := by ext i; fin_cases i <;> simp

@[simp] theorem project_embed (v : Space k) : project k (embed k v) = v := by
  ext i
  fin_cases i <;> simp [project, embed]

theorem embed_sum_zero (v : Space k) : ∑ i, embed k v i = 0 := by
  simp [embed, Fin.sum_univ_succ]

theorem embed_project {w : Fin 3 → k} (hw : ∑ i, w i = 0) :
    embed k (project k w) = w := by
  have h : w 0 + w 1 + w 2 = 0 := by simpa [Fin.sum_univ_succ, add_assoc] using hw
  ext i
  fin_cases i <;> simp [embed, project]
  linear_combination -h

/-- The three-letter permutation representation. -/
def permutationRep : Representation k Group (Fin 3 → k) where
  toFun g :=
    { toFun := fun w i => w (g⁻¹ i)
      map_add' := fun _ _ => rfl
      map_smul' := fun _ _ => rfl }
  map_one' := by ext w i; rfl
  map_mul' g h := by ext w i; rfl

theorem permutation_sum (g : Group) (w : Fin 3 → k) :
    ∑ i, permutationRep k g w i = ∑ i, w i := by
  exact Equiv.sum_comp g.symm w

/-- The standard representation in the displayed two-dimensional coordinates. -/
def rep : Representation k Group (Space k) where
  toFun g := (project k).comp ((permutationRep k g).comp (embed k))
  map_one' := by
    apply LinearMap.ext
    intro v
    exact project_embed k v
  map_mul' g h := by
    apply LinearMap.ext
    intro v
    funext i
    change project k (permutationRep k (g * h) (embed k v)) i =
      project k (permutationRep k g (embed k (project k (permutationRep k h (embed k v))))) i
    rw [embed_project k (by rw [permutation_sum, embed_sum_zero])]
    rfl

theorem rep_apply (g : Group) (v : Space k) :
    rep k g v = project k (permutationRep k g (embed k v)) := rfl

theorem embed_rep (g : Group) (v : Space k) :
    embed k (rep k g v) = permutationRep k g (embed k v) := by
  change embed k (project k (permutationRep k g (embed k v))) = _
  exact embed_project k (by rw [permutation_sum, embed_sum_zero])

/-- The corresponding actual matrix representation. -/
def matrixRep : Group →* Matrix (Fin 2) (Fin 2) k :=
  LinearMap.toMatrixAlgEquiv'.toMonoidHom.comp (rep k)

theorem matrixRep_mulVec (g : Group) (v : Space k) :
    matrixRep k g *ᵥ v = rep k g v := by
  exact LinearMap.toMatrix'_mulVec (rep k g) v

def transposition : Group := Equiv.swap 0 1
def cycle : Group := Equiv.swap 0 1 * Equiv.swap 1 2

@[simp] theorem transposition_inv_zero : transposition⁻¹ (0 : Fin 3) = 1 := by decide
@[simp] theorem transposition_inv_two : transposition⁻¹ (2 : Fin 3) = 2 := by decide
@[simp] theorem cycle_inv_zero : cycle⁻¹ (0 : Fin 3) = 2 := by decide
@[simp] theorem cycle_inv_two : cycle⁻¹ (2 : Fin 3) = 1 := by decide

theorem group_cases (g : Group) :
    g = 1 ∨ g = transposition ∨ g = cycle ∨ g = cycle ^ 2 ∨
      g = transposition * cycle ∨ g = transposition * cycle ^ 2 := by
  revert g
  decide

theorem transposition_inv : transposition⁻¹ = transposition := by decide
theorem cycle_inv : cycle⁻¹ = cycle ^ 2 := by decide

theorem rep_transposition :
    rep k transposition = Matrix.toLin' !![-1, 1; 0, 1] := by
  apply LinearMap.ext
  intro v
  change ![embed k v (transposition⁻¹ (0 : Fin 3)),
    -(embed k v (transposition⁻¹ (2 : Fin 3)))] = _
  rw [transposition_inv_zero, transposition_inv_two]
  ext i
  fin_cases i <;> simp [embed, Matrix.toLin'_apply, Matrix.mulVec, dotProduct,
    Fin.sum_univ_succ, Matrix.cons_val]

theorem rep_cycle : rep k cycle = Matrix.toLin' !![0, -1; 1, -1] := by
  apply LinearMap.ext
  intro v
  change ![embed k v (cycle⁻¹ (0 : Fin 3)), -(embed k v (cycle⁻¹ (2 : Fin 3)))] = _
  rw [cycle_inv_zero, cycle_inv_two]
  ext i
  fin_cases i <;> simp [embed, Matrix.toLin'_apply, Matrix.mulVec, dotProduct,
    Fin.sum_univ_succ, Matrix.cons_val, add_comm]

theorem matrixRep_transposition : matrixRep k transposition = !![-1, 1; 0, 1] := by
  change LinearMap.toMatrix' (rep k transposition) = _
  rw [rep_transposition, LinearMap.toMatrix'_toLin']

theorem matrixRep_cycle : matrixRep k cycle = !![0, -1; 1, -1] := by
  change LinearMap.toMatrix' (rep k cycle) = _
  rw [rep_cycle, LinearMap.toMatrix'_toLin']

/-- The actual sum-zero submodule in the permutation module. -/
def sumZero : Submodule k (Fin 3 → k) where
  carrier := {w | ∑ i, w i = 0}
  zero_mem' := by simp
  add_mem' hx hy := by
    change ∑ i, _ = 0 at hx hy ⊢
    simp only [Pi.add_apply, Finset.sum_add_distrib, hx, hy, add_zero]
  smul_mem' c w hw := by
    change ∑ i, w i = 0 at hw
    change ∑ i, c • w i = 0
    rw [← Finset.smul_sum, hw, smul_zero]

/-- The displayed coordinates give a linear equivalence onto all sum-zero vectors. -/
def sumZeroEquiv : Space k ≃ₗ[k] sumZero k where
  toFun v := ⟨embed k v, embed_sum_zero k v⟩
  invFun w := project k w
  left_inv := project_embed k
  right_inv w := by apply Subtype.ext; exact embed_project k w.property
  map_add' v w := by apply Subtype.ext; exact (embed k).map_add v w
  map_smul' c v := by apply Subtype.ext; exact (embed k).map_smul c v

@[simp] theorem sumZeroEquiv_coe (v : Space k) :
    (sumZeroEquiv k v : Fin 3 → k) = embed k v := rfl

/-- Restriction of the permutation action to its actual sum-zero submodule. -/
def standardRep : Representation k Group (sumZero k) where
  toFun g :=
    { toFun := fun w => ⟨permutationRep k g w, by
        change ∑ i, permutationRep k g w i = 0
        rw [permutation_sum]
        exact w.property⟩
      map_add' := fun _ _ => rfl
      map_smul' := fun _ _ => rfl }
  map_one' := by apply LinearMap.ext; intro w; apply Subtype.ext; rfl
  map_mul' g h := by apply LinearMap.ext; intro w; apply Subtype.ext; rfl

/-- Equivalence with the actual standard representation, including equivariance. -/
def standardEquiv : (rep k).Equiv (standardRep k) :=
  Representation.Equiv.mk (sumZeroEquiv k) (by
    intro g
    apply LinearMap.ext
    intro v
    apply Subtype.ext
    exact embed_rep k g v)

/-- The matrix representation is faithful over every nontrivial coefficient ring. -/
theorem matrixRep_faithful [Nontrivial k] : Function.Injective (matrixRep k) := by
  apply (injective_iff_map_eq_one (matrixRep k)).2
  intro g hg
  have h01 := congrArg (fun A : Matrix (Fin 2) (Fin 2) k => A 0 1) hg
  have h10 := congrArg (fun A : Matrix (Fin 2) (Fin 2) k => A 1 0) hg
  rcases group_cases g with h | h | h | h | h | h
  · exact h
  all_goals subst g
  all_goals norm_num [map_mul, map_pow, matrixRep_transposition, matrixRep_cycle,
    Matrix.mul_apply, Fin.sum_univ_succ, pow_two] at h01
  all_goals norm_num [map_mul, map_pow, matrixRep_transposition, matrixRep_cycle,
    Matrix.mul_apply, Fin.sum_univ_succ, pow_two] at h10

theorem rep_faithful [Nontrivial k] : Function.Injective (rep k) := by
  intro g h hgh
  apply matrixRep_faithful k
  exact congrArg LinearMap.toMatrix' hgh

/-- Coefficient extension agrees with the same standard matrices over the new ring. -/
theorem matrixRep_map {l : Type*} [CommRing l] (f : k →+* l) (g : Group) :
    (matrixRep k g).map f = matrixRep l g := by
  have hs : (!![-1, 1; 0, 1] : Matrix (Fin 2) (Fin 2) k).map f =
      (!![-1, 1; 0, 1] : Matrix (Fin 2) (Fin 2) l) := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp
  have ht : (!![0, -1; 1, -1] : Matrix (Fin 2) (Fin 2) k).map f =
      (!![0, -1; 1, -1] : Matrix (Fin 2) (Fin 2) l) := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp
  rcases group_cases g with h | h | h | h | h | h
  all_goals subst g
  all_goals simp only [map_one, map_mul, map_pow, matrixRep_transposition, matrixRep_cycle,
    Matrix.map_mul, Matrix.map_pow, Matrix.map_one _ f.map_zero f.map_one, hs, ht]

end PaperXII.S3Standard
