import Mathlib.Data.Multiset.Sort
import Mathlib.Algebra.BigOperators.Group.Multiset.Basic
import Mathlib.Data.Quot
import Mathlib.Tactic

/-! The block-multiset part of Paper XI, Theorem 2.5.
An atom is an isomorphism class. A block retains its strictly positive monodromy
length. Mapping atoms does not discard lengths, multiplicities, or repetitions.
This module contains no local-Weil or Langlands-classification existence axiom. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.AtomicMultiset

@[ext] structure Block (A : Type*) where
  atom : A
  length : ℕ
  length_pos : 0 < length

variable {A B C : Type*}

def blockMap (f : A → B) (b : Block A) : Block B :=
  ⟨f b.atom, b.length, b.length_pos⟩

@[simp] theorem blockMap_atom (f : A → B) (b : Block A) :
    (blockMap f b).atom = f b.atom := rfl

@[simp] theorem blockMap_length (f : A → B) (b : Block A) :
    (blockMap f b).length = b.length := rfl

@[simp] theorem blockMap_id (b : Block A) : blockMap id b = b := by
  cases b; rfl

@[simp] theorem blockMap_comp (g : B → C) (f : A → B) (b : Block A) :
    blockMap g (blockMap f b) = blockMap (g ∘ f) b := rfl

def extend (f : A → B) : Multiset (Block A) →+ Multiset (Block B) where
  toFun s := s.map (blockMap f)
  map_zero' := Multiset.map_zero _
  map_add' := Multiset.map_add _

@[simp] theorem extend_singleton (f : A → B) (b : Block A) :
    extend f {b} = {blockMap f b} := rfl

@[simp] theorem extend_cons (f : A → B) (b : Block A) (s : Multiset (Block A)) :
    extend f (b ::ₘ s) = blockMap f b ::ₘ extend f s := Multiset.map_cons _ _ _

@[simp] theorem extend_card (f : A → B) (s : Multiset (Block A)) :
    (extend f s).card = s.card := Multiset.card_map _ _

@[simp] theorem extend_id (s : Multiset (Block A)) : extend id s = s := by
  change s.map (blockMap id) = s
  simp only [show blockMap (id : A → A) = id from funext blockMap_id, Multiset.map_id]

@[simp] theorem extend_comp (g : B → C) (f : A → B) (s : Multiset (Block A)) :
    extend g (extend f s) = extend (g ∘ f) s := by
  exact Multiset.map_map _ _ _

/-- There is only one additive extension with the declared value on every block. -/
theorem extend_unique (f : A → B) (F : Multiset (Block A) →+ Multiset (Block B))
    (hF : ∀ b, F {b} = {blockMap f b}) : F = extend f := by
  apply DFunLike.ext
  intro s
  induction s using Multiset.induction_on with
  | empty => simp
  | @cons b s ih =>
      have hs : b ::ₘ s = ({b} : Multiset (Block A)) + s := rfl
      rw [hs, map_add, map_add, hF, ih, extend_singleton]

/-- Equal-sized repeated atoms cannot be lost if the atomic assignment is injective. -/
theorem extend_injective (f : A → B) (hf : Function.Injective f) :
    Function.Injective (extend f) := by
  apply Multiset.map_injective
  intro b c h
  apply Block.ext
  · apply hf
    exact congrArg Block.atom h
  · exact congrArg (fun x : Block B => x.length) h

/-- An inverse atomic assignment gives an inverse on all finite block multisets. -/
def extendEquiv (e : A ≃ B) : Multiset (Block A) ≃+ Multiset (Block B) where
  toFun := extend e
  invFun := extend e.symm
  left_inv s := by
    rw [extend_comp]
    have h : (e.symm ∘ e : A → A) = id := by funext a; exact e.symm_apply_apply a
    rw [h, extend_id]
  right_inv s := by
    rw [extend_comp]
    have h : (e ∘ e.symm : B → B) = id := by funext a; exact e.apply_symm_apply a
    rw [h, extend_id]
  map_add' := (extend e).map_add

/-- Weighted total dimension: the chain length multiplies the atom dimension. -/
def dimension (dim : A → ℕ) (s : Multiset (Block A)) : ℕ :=
  (s.map (fun b => b.length * dim b.atom)).sum

theorem dimension_extend (f : A → B) (dA : A → ℕ) (dB : B → ℕ)
    (hdim : ∀ a, dB (f a) = dA a) (s : Multiset (Block A)) :
    dimension dB (extend f s) = dimension dA s := by
  simp only [dimension, extend, AddMonoidHom.coe_mk, ZeroHom.coe_mk, Multiset.map_map]
  congr 1
  apply Multiset.map_congr rfl
  intro b _
  exact congrArg (b.length * ·) (hdim b.atom)

/-- The atom map descends along the given isomorphism relations. -/
def descend {sA : Setoid A} {sB : Setoid B} (f : A → B)
    (hf : ∀ a a', sA.r a a' → sB.r (f a) (f a')) :
    Quotient sA → Quotient sB := Quotient.map f hf

@[simp] theorem descend_mk {sA : Setoid A} {sB : Setoid B} (f : A → B)
    (hf : ∀ a a', sA.r a a' → sB.r (f a) (f a')) (a : A) :
    descend f hf (Quotient.mk sA a) = Quotient.mk sB (f a) := rfl

/-- Atomwise twisting commutes with block assembly when it commutes on atoms. -/
theorem extend_natural (f : A → B) (tA : A → A) (tB : B → B)
    (hf : ∀ a, f (tA a) = tB (f a)) (s : Multiset (Block A)) :
    extend f (extend tA s) = extend tB (extend f s) := by
  rw [extend_comp, extend_comp]
  rw [show f ∘ tA = tB ∘ f from funext hf]

end PaperXI.AtomicMultiset
