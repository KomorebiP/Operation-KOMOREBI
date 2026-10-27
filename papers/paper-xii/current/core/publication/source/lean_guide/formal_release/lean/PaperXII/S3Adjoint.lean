import PaperXII.S3Standard
import Mathlib.LinearAlgebra.Trace
import Mathlib.RepresentationTheory.Subrepresentation
import Mathlib.GroupTheory.Perm.Sign

/-!
# Trace-zero adjoint of the standard representation of S₃ over F₇

The adjoint space is the actual kernel of matrix trace. Its action is actual
conjugation by the standard matrices. The displayed equivalence intertwines
the sign representation plus the standard representation with this action.
-/

namespace PaperXII.S3Adjoint

open S3Standard

abbrev K := ZMod 7
abbrev Mat := Matrix (Fin 2) (Fin 2) K

def traceZero : Submodule K Mat := LinearMap.ker (Matrix.traceLinearMap (Fin 2) K K)

abbrev Adj := traceZero

/-- The full conjugation representation on two-by-two matrices. -/
def conjugation : Representation K Group Mat where
  toFun g := LinearMap.mulLeftRight K (matrixRep K g, matrixRep K g⁻¹)
  map_one' := by ext X i j; simp [LinearMap.mulLeftRight]
  map_mul' g h := by
    ext X i j
    simp [LinearMap.mulLeftRight, mul_assoc]

@[simp] theorem conjugation_apply (g : Group) (X : Mat) :
    conjugation g X = matrixRep K g * X * matrixRep K g⁻¹ := rfl

/-- Trace-zero matrices are preserved by conjugation. -/
def adjointSubrepresentation : Subrepresentation conjugation where
  toSubmodule := traceZero
  apply_mem_toSubmodule g X hX := by
    change Matrix.trace (matrixRep K g * X * matrixRep K g⁻¹) = 0
    rw [Matrix.trace_mul_cycle]
    rw [← map_mul, inv_mul_cancel, map_one, one_mul]
    exact hX

/-- The actual trace-zero adjoint representation. -/
def adjoint : Representation K Group Adj := adjointSubrepresentation.toRepresentation

@[simp] theorem adjoint_apply (g : Group) (X : Adj) :
    (adjoint g X : Mat) = matrixRep K g * X.val * matrixRep K g⁻¹ := rfl

/-- Trace-zero matrix coordinates. -/
def W (a b c : K) : Mat := !![a, b; c, -a]

@[simp] theorem trace_W (a b c : K) : Matrix.trace (W a b c) = 0 := by
  simp [W, Matrix.trace, Fin.sum_univ_succ]

/-- The scalar character is the actual permutation sign, reduced modulo 7. -/
def signValue (g : Group) : K := (((Equiv.Perm.sign g : ℤˣ) : ℤ) : K)

@[simp] theorem signValue_one : signValue 1 = 1 := by simp [signValue]

@[simp] theorem signValue_mul (g h : Group) :
    signValue (g * h) = signValue g * signValue h := by simp [signValue]

def signRep : Representation K Group K where
  toFun g := signValue g • LinearMap.id
  map_one' := by ext; simp
  map_mul' g h := by ext; simp [mul_comm]

@[simp] theorem signRep_apply (g : Group) (x : K) : signRep g x = signValue g * x := rfl

/-- Columns `W(2,3,4)`, `W(1,1,2)`, `W(1,5,6)`. -/
def decompositionMap : (K × Space K) →ₗ[K] Adj where
  toFun z := ⟨W (2*z.1 + z.2 0 + z.2 1) (3*z.1 + z.2 0 + 5*z.2 1)
    (4*z.1 + 2*z.2 0 + 6*z.2 1), trace_W _ _ _⟩
  map_add' z w := by
    apply Subtype.ext
    ext i j
    fin_cases i <;> fin_cases j <;> simp [W] <;> ring
  map_smul' c z := by
    apply Subtype.ext
    ext i j
    fin_cases i <;> fin_cases j <;> simp [W] <;> ring

/-- The inverse coefficients of the three displayed columns. -/
def decompositionInverse : Adj →ₗ[K] (K × Space K) where
  toFun X := (X.val 0 0 + X.val 0 1 + 6 * X.val 1 0,
    ![3 * X.val 0 0 + 5 * X.val 0 1, 3 * X.val 0 0 + 2 * X.val 1 0])
  map_add' X Y := by
    apply Prod.ext
    · simp; ring
    · ext i; fin_cases i <;> simp <;> ring
  map_smul' c X := by
    apply Prod.ext
    · simp; ring
    · ext i; fin_cases i <;> simp <;> ring

theorem decompositionInverse_map (z : K × Space K) :
    decompositionInverse (decompositionMap z) = z := by
  apply Prod.ext
  · change (2*z.1 + z.2 0 + z.2 1) + (3*z.1 + z.2 0 + 5*z.2 1) +
      6*(4*z.1 + 2*z.2 0 + 6*z.2 1) = z.1
    ring_nf
    simp only [show (29 : K) = 1 by decide, show (14 : K) = 0 by decide,
      show (42 : K) = 0 by decide]
    simp
  · ext i
    fin_cases i <;> simp [decompositionMap, decompositionInverse, W] <;> ring_nf <;> simp only [show (21 : K) = 0 by decide, show (8 : K) = 1 by decide,
      show (28 : K) = 0 by decide, show (14 : K) = 0 by decide,
      show (7 : K) = 0 by decide, show (15 : K) = 1 by decide] <;> simp

theorem decompositionMap_inverse (X : Adj) :
    decompositionMap (decompositionInverse X) = X := by
  have ht : X.val 0 0 + X.val 1 1 = 0 := by
    simpa [traceZero, LinearMap.mem_ker, Matrix.trace, Fin.sum_univ_succ] using X.property
  apply Subtype.ext
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [decompositionMap, decompositionInverse, W] <;> ring_nf <;> simp only [show (21 : K) = 0 by decide, show (8 : K) = 1 by decide,
      show (28 : K) = 0 by decide, show (14 : K) = 0 by decide,
      show (7 : K) = 0 by decide, show (36 : K) = 1 by decide] <;> simp
  exact neg_eq_iff_add_eq_zero.mpr ht

/-- The full linear equivalence, before recording equivariance. -/
def decompositionLinearEquiv : (K × Space K) ≃ₗ[K] Adj :=
  { decompositionMap with
    invFun := decompositionInverse
    left_inv := decompositionInverse_map
    right_inv := decompositionMap_inverse }

@[simp] theorem signValue_transposition : signValue transposition = -1 := by decide

@[simp] theorem signValue_cycle : signValue cycle = 1 := by decide

theorem decomposition_transposition (z : K × Space K) :
    decompositionMap ((signRep.prod (rep K)) transposition z) =
      adjoint transposition (decompositionMap z) := by
  apply Subtype.ext
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [decompositionMap, W, Representation.prod, signRep_apply,
      adjoint_apply, transposition_inv, matrixRep_transposition, rep_transposition,
      Matrix.toLin'_apply, Matrix.mul_apply, dotProduct,
      Fin.sum_univ_succ] <;> apply sub_eq_zero.mp <;> ring_nf <;>
    simp only [show (7 : K) = 0 by decide, show (14 : K) = 0 by decide] <;> simp

theorem decomposition_cycle (z : K × Space K) :
    decompositionMap ((signRep.prod (rep K)) cycle z) =
      adjoint cycle (decompositionMap z) := by
  apply Subtype.ext
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [decompositionMap, W, Representation.prod, signRep_apply,
      adjoint_apply, cycle_inv, matrixRep_cycle, rep_cycle, pow_two,
      Matrix.toLin'_apply, Matrix.mul_apply, dotProduct,
      Fin.sum_univ_succ] <;> apply sub_eq_zero.mp <;> ring_nf <;>
    simp only [show (7 : K) = 0 by decide] <;> simp

/-- The coordinate map intertwines the actions for every element of S₃. -/
theorem decomposition_equivariant (g : Group) (z : K × Space K) :
    decompositionMap ((signRep.prod (rep K)) g z) = adjoint g (decompositionMap z) := by
  have hm (g h : Group)
      (hg : ∀ z, decompositionMap ((signRep.prod (rep K)) g z) = adjoint g (decompositionMap z))
      (hh : ∀ z, decompositionMap ((signRep.prod (rep K)) h z) = adjoint h (decompositionMap z)) :
      ∀ z, decompositionMap ((signRep.prod (rep K)) (g*h) z) =
        adjoint (g*h) (decompositionMap z) := by
    intro z
    simp only [map_mul, Module.End.mul_apply]
    rw [hg, hh]
  have ht2 := hm cycle cycle decomposition_cycle decomposition_cycle
  rw [← pow_two] at ht2
  rcases group_cases g with h | h | h | h | h | h
  · subst g; simp
  · subst g; exact decomposition_transposition z
  · subst g; exact decomposition_cycle z
  · subst g; exact ht2 z
  · subst g; exact hm transposition cycle decomposition_transposition decomposition_cycle z
  · subst g; exact hm transposition (cycle ^ 2) decomposition_transposition ht2 z

/-- The trace-zero adjoint is equivariantly the sign representation plus the standard representation. -/
noncomputable def decompositionEquiv : (signRep.prod (rep K)).Equiv adjoint :=
  Representation.Equiv.mk decompositionLinearEquiv (by
    intro g
    apply LinearMap.ext
    intro z
    exact decomposition_equivariant g z)

/-- Every invariant trace-zero matrix vanishes. -/
theorem fixed_eq_zero (X : Adj) (h : ∀ g, adjoint g X = X) : X = 0 := by
  have hs := congrArg (fun Y : Adj => Y.val 1 0) (h transposition)
  have ht := congrArg (fun Y : Adj => Y.val 0 0) (h cycle)
  have hb := congrArg (fun Y : Adj => Y.val 0 1) (h transposition)
  have htr : X.val 0 0 + X.val 1 1 = 0 := by
    simpa [traceZero, LinearMap.mem_ker, Matrix.trace, Fin.sum_univ_succ] using X.property
  simp [adjoint_apply, transposition_inv, matrixRep_transposition,
    Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_succ] at hs hb
  simp [adjoint_apply, cycle_inv, matrixRep_cycle, pow_two,
    Matrix.mul_apply, Matrix.vecMul, dotProduct, Fin.sum_univ_succ] at ht
  have hz (a : K) (ha : 2*a = 0) : a = 0 :=
    (mul_eq_zero.mp ha).resolve_left (by decide)
  have hc : X.val 1 0 = 0 := hz _ (by linear_combination -hs)
  have ha : X.val 0 0 = 0 := hz _ (by linear_combination -ht + htr + hc)
  have hd : X.val 1 1 = 0 := by linear_combination htr - ha
  have hbb : X.val 0 1 = 0 := hz _ (by linear_combination -hb + hc - ha + hd)
  apply Subtype.ext
  ext i j
  fin_cases i <;> fin_cases j <;> simp [ha, hbb, hc, hd]

/-- The inclusion of the sign coordinates in the adjoint space. -/
def signEmbedding : K →ₗ[K] Adj := decompositionMap.comp (LinearMap.inl K K (Space K))

/-- The inclusion of the standard coordinates in the adjoint space. -/
def standardEmbedding : Space K →ₗ[K] Adj :=
  decompositionMap.comp (LinearMap.inr K K (Space K))

/-- The actual sign subrepresentation of the trace-zero adjoint. -/
def signSummand : Subrepresentation adjoint where
  toSubmodule := LinearMap.range signEmbedding
  apply_mem_toSubmodule g X hX := by
    obtain ⟨a, rfl⟩ := hX
    refine ⟨signRep g a, ?_⟩
    simpa [signEmbedding, Representation.prod] using decomposition_equivariant g (a, 0)

/-- The actual standard subrepresentation of the trace-zero adjoint. -/
def standardSummand : Subrepresentation adjoint where
  toSubmodule := LinearMap.range standardEmbedding
  apply_mem_toSubmodule g X hX := by
    obtain ⟨v, rfl⟩ := hX
    refine ⟨rep K g v, ?_⟩
    simpa [standardEmbedding, Representation.prod] using decomposition_equivariant g (0, v)

/-- The paper's literal sign witness belongs to the sign subrepresentation. -/
theorem W_sign_mem : (⟨W 2 3 4, trace_W 2 3 4⟩ : Adj) ∈ signSummand := by
  exact ⟨1, by decide⟩

/-- The paper's literal standard witness belongs to the standard subrepresentation. -/
theorem W_standard_mem : (⟨W 6 4 3, trace_W 6 4 3⟩ : Adj) ∈ standardSummand := by
  exact ⟨![3, 3], by decide⟩

end PaperXII.S3Adjoint
