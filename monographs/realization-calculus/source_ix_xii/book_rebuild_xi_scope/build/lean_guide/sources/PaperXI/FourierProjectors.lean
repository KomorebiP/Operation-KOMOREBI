import PaperXI.CyclicAction

/-! Finite Fourier projectors derived from cyclic representation laws and a
primitive additive character. No idempotence or orthogonality is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FourierProjectors
open scoped BigOperators
open PaperXI.CyclicAction
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {M : ℕ} [NeZero M]

def projector (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (j : ZMod M) : Module.End K V :=
  PaperXI.FourierCovariance.fourierOperator (operator ρ) ψ j

theorem projector_formula (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (j : ZMod M) :
    projector ρ ψ j = (M : K)⁻¹ • ∑ a : ZMod M, ψ (-j * a) • operator ρ a := rfl

theorem character_sum (ψ : AddChar (ZMod M) K) (hψ : ψ.IsPrimitive) (t : ZMod M) :
    (∑ a : ZMod M, ψ (t * a)) = if t = 0 then (M : K) else 0 := by
  simpa [mul_comm] using AddChar.sum_mulShift t hψ

/-- Every projected vector has the declared inertia character. -/
theorem action_projector (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (j b : ZMod M) :
    operator ρ b * projector ρ ψ j = ψ (j * b) • projector ρ ψ j := by
  have hs : (∑ a : ZMod M, ψ (-j * a) • operator ρ (b + a)) =
      ψ (j * b) • ∑ a : ZMod M, ψ (-j * a) • operator ρ a := by
    rw [Finset.smul_sum]
    apply Fintype.sum_equiv (Equiv.addLeft b)
    intro a
    change ψ (-j * a) • operator ρ (b + a) =
      ψ (j * b) • (ψ (-j * (b + a)) • operator ρ (b + a))
    simp only [smul_smul, ← AddChar.map_add_eq_mul]
    congr 2
    ring
  rw [projector_formula, mul_smul_comm, Finset.mul_sum]
  simp_rw [mul_smul_comm, ← operator_add]
  rw [hs]
  exact smul_comm _ _ _

theorem projector_product (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (hψ : ψ.IsPrimitive) (hM : (M : K) ≠ 0)
    (i j : ZMod M) :
    projector ρ ψ i * projector ρ ψ j = if i = j then projector ρ ψ j else 0 := by
  rw [projector_formula ρ ψ i, smul_mul_assoc, Finset.sum_mul]
  simp_rw [smul_mul_assoc, action_projector, smul_smul, ← AddChar.map_add_eq_mul]
  have h : ∀ a : ZMod M, -i * a + j * a = (j - i) * a := by intro a; ring
  simp_rw [h]
  rw [← Finset.sum_smul, character_sum ψ hψ]
  by_cases hij : i = j
  · subst j; simp [hM, smul_smul]
  · have hji : j - i ≠ 0 := sub_ne_zero.mpr (Ne.symm hij)
    simp [hji, hij]

theorem projector_idempotent (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (hψ : ψ.IsPrimitive) (hM : (M : K) ≠ 0)
    (j : ZMod M) : projector ρ ψ j ^ 2 = projector ρ ψ j := by
  simpa [pow_two] using projector_product ρ ψ hψ hM j j

theorem projector_orthogonal (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (hψ : ψ.IsPrimitive) (hM : (M : K) ≠ 0)
    {i j : ZMod M} (hij : i ≠ j) : projector ρ ψ i * projector ρ ψ j = 0 := by
  simpa [hij] using projector_product ρ ψ hψ hM i j

theorem projector_complete (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (hψ : ψ.IsPrimitive) (hM : (M : K) ≠ 0) :
    (∑ j : ZMod M, projector ρ ψ j) = 1 := by
  have hs (a : ZMod M) : (∑ j : ZMod M, ψ (-j * a)) =
      if a = 0 then (M : K) else 0 := by
    simpa [mul_comm, neg_mul, mul_neg] using character_sum ψ hψ (-a)
  simp only [projector_formula, ← Finset.smul_sum]
  rw [Finset.sum_comm]
  simp_rw [← Finset.sum_smul, hs]
  simp [hM, smul_smul]

end PaperXI.FourierProjectors
