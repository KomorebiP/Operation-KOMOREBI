import PaperXII.FittingTransport

/-! Kernel-checked normalization checks, including zero and empty-rank boundaries. -/
noncomputable section
namespace PaperXII
open Matrix DeterminantalIdeals
variable {R : Type*} [CommRing R]

/-- Positive-order minors of the zero relation matrix all vanish. -/
theorem minorIdeal_zero_matrix {m n : Type*} {k : ℕ} (hk : 0 < k) :
    minorIdeal (0 : Matrix m n R) k = ⊥ := by
  apply le_antisymm _ bot_le
  apply (minorIdeal_le_iff _ _ _).mpr
  intro r c
  have : Nonempty (Fin k) := ⟨⟨0,hk⟩⟩
  simp

/-- For a finite free module, low-index Fitting ideals are zero and high-index ones are the unit ideal. -/
theorem fittingIdeal_free (n j : ℕ) :
    fittingIdeal R (Fin n → R) j = if n ≤ j then ⊤ else ⊥ := by
  classical
  have hp : Presents (0 : Matrix (Fin n) (Fin 0) R) (LinearMap.id : (Fin n → R) →ₗ[R] _) := by
    refine ⟨Function.surjective_id, ?_⟩
    simp [Matrix.mulVecLin]
  rw [fittingIdeal_eq_presentation _ _ hp]
  by_cases h : n ≤ j
  · simp only [h,ite_true]
    exact presentationIdeal_eq_top _ (by simpa using h)
  · simp only [h,ite_false,presentationIdeal,Fintype.card_fin]
    exact minorIdeal_zero_matrix (by omega)

/-- The zero module has unit zeroth Fitting ideal, not the zero ideal. -/
theorem fittingIdeal_zero_module (j : ℕ) : fittingIdeal R (Fin 0 → R) j = ⊤ := by
  simp [fittingIdeal_free]

/-- The first normalization distinguishes the free rank-one module from the zero module. -/
theorem fittingIdeal_free_rank_one_zero : fittingIdeal R (Fin 1 → R) 0 = ⊥ := by
  simp [fittingIdeal_free]

/-- A one-by-one presentation records its actual relation coefficient. -/
theorem one_by_one_presentationIdeal (a : R) :
    presentationIdeal (Matrix.of fun (_ : Fin 1) (_ : Fin 1) => a) 0 = Ideal.span ({a} : Set R) := by
  change minorIdeal (Matrix.of fun (_ : Fin 1) (_ : Fin 1) => a) 1 = _
  unfold minorIdeal
  congr 1
  ext x
  constructor
  · rintro ⟨⟨r,c⟩,hx⟩
    change (Matrix.of (fun (_ : Fin 1) (_ : Fin 1) => a)).det = x at hx
    rw [Matrix.det_fin_one] at hx
    exact hx.symm
  · intro hx
    have h : x = a := Set.mem_singleton_iff.mp hx
    subst x
    refine ⟨(id,id),?_⟩
    change (Matrix.of (fun (_ : Fin 1) (_ : Fin 1) => a)).det = a
    rw [Matrix.det_fin_one]
    rfl

/-- The empty matrix boundary and a genuine 1-by-1 relation both survive non-flat coefficient maps. -/
theorem one_by_one_baseChange {S : Type*} [CommRing S] (f : R →+* S) (a : R) :
    presentationIdeal (Matrix.of fun (_ : Fin 1) (_ : Fin 1) => f a) 0 =
      Ideal.map f (presentationIdeal (Matrix.of fun (_ : Fin 1) (_ : Fin 1) => a) 0) :=
  minorIdeal_map f (Matrix.of fun (_ : Fin 1) (_ : Fin 1) => a) _

end PaperXII
