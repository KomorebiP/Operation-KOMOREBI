import PaperX.CompletionExamples

/-! A finite occupied representation node can die at the next precision, even
while other branches of the same forest survive. The computations below are
kernel checked over Z/4 and Z/8, not universal arithmetic occupancy assertions. -/
set_option autoImplicit false
namespace PaperX.CompletionObstructions
open scoped Matrix
open PaperX.RepresentationLimits PaperX.CompletionExamples

instance fourLarge : Fact (1 < 4) := ⟨by decide⟩
instance eightLarge : Fact (1 < 8) := ⟨by decide⟩

def node4 : Matrix (Fin 2) (Fin 2) (ZMod 4) := !![1,2;2,3]
def red8 : ZMod 8 →+* ZMod 4 := ZMod.castHom (by decide) (ZMod 4)

theorem node4_involution : node4 * node4 = 1 := by decide +kernel

theorem node4_polynomial : node4.charpoly = Polynomial.X^2 - 1 := by
  rw [Matrix.charpoly_fin_two]
  have ht : node4.trace = 0 := by decide +kernel
  have hd : node4.det = -1 := by decide +kernel
  rw [ht, hd]
  simp [sub_eq_add_neg]

def nodeRepresentation : MatrixRep (ZMod 4) C2 (Fin 2) where
  toFun g := if g = 1 then 1 else node4
  map_one' := by decide +kernel
  map_mul' := by decide +kernel

theorem node_generator : nodeRepresentation generator = node4 := by decide +kernel

/-- The obstruction is trace and determinant at the next dyadic precision. -/
theorem lifted_trace_forces_wrong_det : ∀ a b c d : ZMod 8,
    red8 a = 1 → red8 b = 2 → red8 c = 2 → red8 d = 3 →
    a + d = 0 → a*d-b*c ≠ -1 := by
  decide +kernel

theorem no_matrix_lift (B : Matrix (Fin 2) (Fin 2) (ZMod 8))
    (hB : B.map red8 = node4) : B.charpoly ≠ Polynomial.X^2 - 1 := by
  intro hp
  have ht : B.trace = 0 := by
    have H := congrArg (fun p : Polynomial (ZMod 8) => p.coeff 1) hp
    simpa [Matrix.charpoly_fin_two, Polynomial.coeff_one] using H
  have hd : B.det = -1 := by
    have H := congrArg (fun p : Polynomial (ZMod 8) => p.coeff 0) hp
    simpa [Matrix.charpoly_fin_two, Polynomial.coeff_one] using H
  have hij := fun i j => congrArg (fun A : Matrix (Fin 2) (Fin 2) (ZMod 4) => A i j) hB
  apply lifted_trace_forces_wrong_det (B 0 0) (B 0 1) (B 1 0) (B 1 1)
    (hij 0 0) (hij 0 1) (hij 1 0) (hij 1 1)
  · simpa [Matrix.trace, Fin.sum_univ_succ] using ht
  · simpa [Matrix.det_fin_two] using hd

/-- This is an actual representation node without a next-level child having the
same selected polynomial, not just an unrelated scalar root example. -/
theorem no_representation_lift : ¬ ∃ ρ : MatrixRep (ZMod 8) C2 (Fin 2),
    changeCoefficients red8 ρ = nodeRepresentation ∧
    (ρ generator).charpoly = Polynomial.X^2-1 := by
  rintro ⟨ρ,hr,hp⟩
  have hB : (ρ generator).map red8 = node4 := by
    exact (congrArg (fun τ => τ generator) hr).trans node_generator
  exact no_matrix_lift (ρ generator) hB hp

end PaperX.CompletionObstructions
