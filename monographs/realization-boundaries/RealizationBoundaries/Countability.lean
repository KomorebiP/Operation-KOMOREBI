import RealizationBoundaries.NormalForms
import RealizationBoundaries.PairedPrimes
import Mathlib.Data.DFinsupp.Encodable
import Mathlib.Data.Rat.Encodable

/-! # Countability of the actual infinite groups -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- A faithful finite-support encoding, not a finite truncation. -/
def finiteSupportCode (x : finiteSupport) : Π₀ p : Prime, Coordinate p := by
  classical
  refine ⟨x.val, Trunc.mk ⟨x.property.toFinset.val, ?_⟩⟩
  intro p
  by_cases hp : x.val p = 0
  · exact Or.inr hp
  · exact Or.inl (by simpa [support] using hp)

@[simp] theorem finiteSupportCode_apply (x : finiteSupport) (p : Prime) :
    finiteSupportCode x p = x.val p := rfl

theorem finiteSupportCode_injective : Function.Injective finiteSupportCode := by
  intro x y h
  apply Subtype.ext
  exact congrArg (fun f : Π₀ p : Prime, Coordinate p => (f : Ambient)) h

instance finiteSupport_countable : Countable finiteSupport :=
  finiteSupportCode_injective.countable

instance normalForm_countable (S : Set Prime) : Countable (NormalForm S) :=
  Countable.of_equiv (ℚ × finiteSupport) (NormalForm.pairEquiv S).symm

/-- Countability does not require infinite selected support; uniqueness does. -/
instance selectorGroup_countable (S : Set Prime) : Countable (selectorGroup S) := by
  apply Function.Surjective.countable (f := normalEvaluate S)
  intro x
  obtain ⟨r, d, h⟩ := normalForm_exists S x
  exact ⟨(r,d), Subtype.ext h.symm⟩

/-- For an arbitrary countable rational subspace, choose representatives and record
only the residual finite-support correction. No effectiveness of choice is claimed. -/
def preimageCountableCode (W : Submodule ℚ TailSpace) (x : preimage W) : W × finiteSupport := by
  let w : W := preimageProjection W x
  let y := (preimageProjection_surjective W w).choose
  have hy := (preimageProjection_surjective W w).choose_spec
  refine (w, ⟨x.val - y.val, ?_⟩)
  apply (quotientMap_eq_iff _ _).mp
  exact (congrArg Subtype.val hy).symm

theorem preimageCountableCode_injective (W : Submodule ℚ TailSpace) :
    Function.Injective (preimageCountableCode W) := by
  intro x y h
  have hw : preimageProjection W x = preimageProjection W y := congrArg Prod.fst h
  have hd := congrArg (fun z : W × finiteSupport => z.2.val) h
  dsimp [preimageCountableCode] at hd
  rw [hw] at hd
  exact Subtype.ext ((sub_left_inj.mp hd))

instance preimage_countable (W : Submodule ℚ TailSpace) [Countable W] :
    Countable (preimage W) :=
  (preimageCountableCode_injective W).countable

/-- The unit at one prime gives infinitely many distinct points of D. -/
def primeSeed (p : Prime) : finiteSupport :=
  ⟨cut {p} (fun _ => 1), cut_mem_finiteSupport {p} (fun _ => 1)⟩

theorem primeSeed_injective : Function.Injective primeSeed := by
  classical
  intro p q h
  by_contra hpq
  have heq := congrArg (fun x : finiteSupport => x.val p) h
  simp [primeSeed, cut, hpq] at heq

instance finiteSupport_infinite : Infinite finiteSupport :=
  Infinite.of_injective (fun n => primeSeed (primeAt n))
    (primeSeed_injective.comp primeAt_injective)

instance preimage_infinite (W : Submodule ℚ TailSpace) : Infinite (preimage W) := by
  let f : finiteSupport → preimage W := fun x => ⟨x.val, finiteSupport_le_preimage W x.property⟩
  apply Infinite.of_injective f
  intro x y h
  have hv : (f x).val = (f y).val := congrArg (fun z : preimage W => z.val) h
  exact Subtype.ext hv

/-- Countability of a preimage is equivalent to countability of its rational quotient. -/
theorem preimage_countable_iff (W : Submodule ℚ TailSpace) :
    Countable (preimage W) ↔ Countable W := by
  constructor
  · intro h
    let := h
    exact (preimageProjection_surjective W).countable
  · intro h
    let := h
    infer_instance

theorem paired_countably_infinite (a : ℕ → Bool) :
    Countable (pairedGroup a) ∧ Infinite (pairedGroup a) := by
  change Countable (selectorGroup (pairedSelector a)) ∧
    Infinite (preimage (selectorLine (pairedSelector a)))
  exact ⟨inferInstance, inferInstance⟩

end RealizationBoundaries
