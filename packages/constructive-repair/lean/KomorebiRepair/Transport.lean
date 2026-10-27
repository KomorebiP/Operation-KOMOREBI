import KomorebiRepair.Basic

/-! # Naturality and obstruction-faithful transport
Injectivity is required only on the specified obstruction span, not on all target data.
-/
namespace KomorebiRepair

variable {k U V U' V' I : Type*} [CommRing k]
  [AddCommGroup U] [Module k U] [AddCommGroup V] [Module k V]
  [AddCommGroup U'] [Module k U'] [AddCommGroup V'] [Module k V']

theorem correction_range_maps (D : U →ₗ[k] V) (D' : U' →ₗ[k] V')
    (a : U →ₗ[k] U') (b : V →ₗ[k] V') (h : b.comp D = D'.comp a) :
    LinearMap.range D ≤ (LinearMap.range D').comap b := by
  rintro _ ⟨u, rfl⟩
  exact ⟨a u, (LinearMap.congr_fun h u).symm⟩

def obstructionTransport (D : U →ₗ[k] V) (D' : U' →ₗ[k] V')
    (a : U →ₗ[k] U') (b : V →ₗ[k] V') (h : b.comp D = D'.comp a) :
    ObstructionSpace D →ₗ[k] ObstructionSpace D' :=
  (LinearMap.range D).mapQ (LinearMap.range D') b (correction_range_maps D D' a b h)

@[simp] theorem transport_obstruction_naturality (D : U →ₗ[k] V) (D' : U' →ₗ[k] V')
    (a : U →ₗ[k] U') (b : V →ₗ[k] V') (h : b.comp D = D'.comp a) (r : V) :
    obstructionTransport D D' a b h (obstructionMap D r) = obstructionMap D' (b r) := rfl

/-- This is a preservation condition, not a new existence assumption. -/
def FaithfulOn {Q Q' : Type*} [AddCommGroup Q] [Module k Q]
    [AddCommGroup Q'] [Module k Q'] (B : Q →ₗ[k] Q') (O : Submodule k Q) : Prop :=
  ∀ z ∈ O, B z = 0 → z = 0

theorem faithfulOn_iff_injective {Q Q' : Type*} [AddCommGroup Q] [Module k Q]
    [AddCommGroup Q'] [Module k Q'] (B : Q →ₗ[k] Q') (O : Submodule k Q) :
    FaithfulOn B O ↔ Function.Injective (B.comp O.subtype) := by
  constructor
  · intro h x y hxy
    apply Subtype.ext
    apply sub_eq_zero.mp
    apply h (x.val - y.val) (O.sub_mem x.property y.property)
    change B x.val = B y.val at hxy
    rw [map_sub, hxy, sub_self]
  · intro h z hz hzero
    have heq : (B.comp O.subtype) ⟨z, hz⟩ = (B.comp O.subtype) 0 := by
      simpa only [LinearMap.comp_apply, Submodule.subtype_apply, ZeroMemClass.coe_zero,
        map_zero] using hzero
    exact congrArg Subtype.val (h heq)

/-- Target vanishing reflects source correctability when the required span is not collapsed. -/
theorem transport_faithfulness_on_obstruction_span
    (D : U →ₗ[k] V) (D' : U' →ₗ[k] V') (a : U →ₗ[k] U') (b : V →ₗ[k] V')
    (h : b.comp D = D'.comp a) (r : I → V)
    (hf : FaithfulOn (obstructionTransport D D' a b h) (obstructionSpan D r)) (i : I) :
    Correctable D' (b (r i)) ↔ Correctable D (r i) := by
  rw [correctable_iff_obstruction_zero, correctable_iff_obstruction_zero]
  constructor
  · intro hi
    exact hf _ (obstruction_mem_span D r i)
      ((transport_obstruction_naturality D D' a b h (r i)).trans hi)
  · intro hi
    rw [← transport_obstruction_naturality D D' a b h (r i), hi, map_zero]

/-- Absence of faithfulness is witnessed by a specific nonzero class that disappears. -/
theorem nonfaithful_witness {Q Q' : Type*} [AddCommGroup Q] [Module k Q]
    [AddCommGroup Q'] [Module k Q'] (B : Q →ₗ[k] Q') (O : Submodule k Q)
    (h : ¬ FaithfulOn B O) : ∃ z ∈ O, B z = 0 ∧ z ≠ 0 := by
  classical
  simp only [FaithfulOn, not_forall] at h
  obtain ⟨z, hz, hB, hn⟩ := h
  exact ⟨z, hz, hB, hn⟩

end KomorebiRepair
