import PaperXI.SymplecticHeisenbergUniqueness
import Mathlib.Tactic.Ring

/-! Actual finite central extensions from bilinear factor sets.  The extension,
commutator, central character and Stone--von Neumann endpoint are distinct data.
No multiplication law, irrep, dimension or initial intertwiner is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BilinearHeisenberg

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

@[ext] structure Element (c : LinearMap.BilinForm K V) where
  vector : V
  central : K

variable (c : LinearMap.BilinForm K V)

instance instMul : Mul (Element c) :=
  ⟨fun h k => ⟨h.vector + k.vector, h.central + k.central + c h.vector k.vector⟩⟩
instance instOne : One (Element c) := ⟨⟨0, 0⟩⟩
instance instInv : Inv (Element c) :=
  ⟨fun h => ⟨-h.vector, -h.central + c h.vector h.vector⟩⟩

@[simp] theorem mul_vector (h k : Element c) :
    (h * k).vector = h.vector + k.vector := rfl
@[simp] theorem mul_central (h k : Element c) :
    (h * k).central = h.central + k.central + c h.vector k.vector := rfl
@[simp] theorem one_vector : (1 : Element c).vector = 0 := rfl
@[simp] theorem one_central : (1 : Element c).central = 0 := rfl
@[simp] theorem inv_vector (h : Element c) : h⁻¹.vector = -h.vector := rfl
@[simp] theorem inv_central (h : Element c) :
    h⁻¹.central = -h.central + c h.vector h.vector := rfl

instance instGroup : Group (Element c) where
  mul_assoc h k l := by
    ext <;> simp only [mul_vector, mul_central, map_add, LinearMap.add_apply]
    · abel
    · ring
  one_mul h := by ext <;> simp
  mul_one h := by ext <;> simp
  inv_mul_cancel h := by ext <;> simp

def i : Multiplicative K →* Element c where
  toFun z := ⟨0, z.toAdd⟩
  map_one' := rfl
  map_mul' z w := by ext <;> simp

def q : Element c →* Multiplicative V where
  toFun h := Multiplicative.ofAdd h.vector
  map_one' := rfl
  map_mul' _ _ := rfl

@[simp] theorem i_vector (z : Multiplicative K) : (i c z).vector = 0 := rfl
@[simp] theorem i_central (z : Multiplicative K) : (i c z).central = z.toAdd := rfl
@[simp] theorem q_apply (h : Element c) : (q c h).toAdd = h.vector := rfl

/-- This is the actual short exact central extension of the additive space. -/
def datum : CentralExtension.Datum (Multiplicative K) (Element c) (Multiplicative V) where
  i := i c
  q := q c
  i_injective := by
    intro z w h
    exact congrArg Multiplicative.ofAdd (congrArg Element.central h)
  q_surjective := fun v => ⟨⟨v.toAdd, 0⟩, rfl⟩
  range_i_eq_ker_q := by
    ext h
    constructor
    · rintro ⟨z, rfl⟩
      rfl
    · intro hq
      have hv : h.vector = 0 := congrArg Multiplicative.toAdd hq
      exact ⟨Multiplicative.ofAdd h.central, by ext <;> simp [hv]⟩
  central z h := by
    ext <;> simp [add_comm]

/-- The commutator is calculated from multiplication, not postulated. -/
theorem commutator (h k : Element c) :
    h * k * h⁻¹ * k⁻¹ = i c (Multiplicative.ofAdd
      (c h.vector k.vector - c k.vector h.vector)) := by
  ext <;> simp only [mul_vector, mul_central, inv_vector, inv_central, i_vector,
    i_central, map_add, map_neg, LinearMap.add_apply,
    LinearMap.neg_apply]
  · abel
  · change _ = c h.vector k.vector - c k.vector h.vector
    ring

theorem centralCommutator (h k : Element c) :
    CentralExtension.centralCommutator (datum c) h k =
      Multiplicative.ofAdd (c h.vector k.vector - c k.vector h.vector) := by
  apply (datum c).i_injective
  rw [CentralExtension.i_centralCommutator]
  exact commutator c h k

/-- Finiteness is derived from the actual underlying coordinates. -/
instance instFinite [Finite K] [Finite V] : Finite (Element c) :=
  Finite.of_injective (fun h : Element c => (h.vector, h.central))
    (fun _ _ h => Element.ext (congrArg Prod.fst h) (congrArg Prod.snd h))

theorem order : Nat.card (Element c) = Nat.card K * Nat.card V := by
  have h := CentralExtension.natCard_eq (datum c)
  change Nat.card (Element c) = Nat.card K * Nat.card V at h
  exact h

variable (b : LinearMap.BilinForm K V)
variable (hc : ∀ x y, c x y - c y x = b x y)

include hc in
theorem source_commutator (h k : Element c) :
    CentralExtension.centralCommutator (datum c) h k =
      Multiplicative.ofAdd (b ((datum c).q h).toAdd ((datum c).q k).toAdd) := by
  rw [centralCommutator, hc]
  rfl

variable [Fintype V] (hb : b.SeparatingLeft)
variable (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
include b hc hb hψ

/-- Existence on an actual simple ideal, with dimension derived by finite
Stone--von Neumann.  Only the form and factor set are supplied. -/
theorem exists_irreducible :
    let B : Type _ := CentralCharacter.Algebra (datum c) (SymplecticCentralExtension.scalarCharacter ψ)
    letI : Ring B := inferInstance
    letI : Algebra ℂ B := inferInstance
    ∃ I : Ideal B, ∃ σ : Representation ℂ (Element c) I,
      Representation.IsIrreducible σ ∧
      (∀ t : K, σ (i c (Multiplicative.ofAdd t)) = ψ t •
        (LinearMap.id : Module.End ℂ I)) ∧
      Module.finrank ℂ I = Nat.sqrt (Fintype.card V) :=
  SymplecticHeisenbergUniqueness.exists_irreducible
    (datum c) b hb (source_commutator c b hc) ψ hψ

variable {W U : Type*} [AddCommGroup W] [Module ℂ W] [AddCommGroup U] [Module ℂ U]

/-- Uniqueness compares representations of the same specified middle group. -/
theorem exists_equiv (σ : Representation ℂ (Element c) W)
    (τ : Representation ℂ (Element c) U)
    [Representation.IsIrreducible σ] [Representation.IsIrreducible τ]
    (hσ : ∀ t : K, σ (i c (Multiplicative.ofAdd t)) = ψ t • LinearMap.id)
    (hτ : ∀ t : K, τ (i c (Multiplicative.ofAdd t)) = ψ t • LinearMap.id) :
    Nonempty (Representation.Equiv σ τ) :=
  SymplecticHeisenbergUniqueness.exists_equiv
    (datum c) b hb (source_commutator c b hc) ψ hψ σ τ hσ hτ

theorem finrank_sqrt (σ : Representation ℂ (Element c) W)
    [Representation.IsIrreducible σ]
    (hσ : ∀ t : K, σ (i c (Multiplicative.ofAdd t)) = ψ t • LinearMap.id) :
    Module.finrank ℂ W = Nat.sqrt (Fintype.card V) :=
  SymplecticHeisenbergUniqueness.finrank_sqrt
    (datum c) b hb (source_commutator c b hc) ψ hψ σ hσ

end PaperXI.BilinearHeisenberg
