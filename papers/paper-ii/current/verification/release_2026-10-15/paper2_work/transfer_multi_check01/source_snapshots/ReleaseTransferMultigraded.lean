import ReleaseTransferScalar
import Mathlib.Data.Finsupp.Weight
import Mathlib.RingTheory.MvPowerSeries.Inverse

/-! Exact multigraded walks and rationality. Each edge has a nonzero finitely
supported natural exponent vector. Total degree provides a finiteness bound but
the coefficient model retains the full exponent vector, not its specialization.
-/
set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseTransferMultigraded
open TransferZeta TransferZeta.PositiveWeightedMultigraph
universe u v w z
variable {V : Type u} {E : Type v} {σ : Type w} {R : Type z}

structure Graph (V : Type u) (E : Type v) (σ : Type w) where
  source : E → V
  target : E → V
  weight : E → (σ →₀ ℕ)
  weight_ne_zero : ∀ e, weight e ≠ 0

variable (G : Graph V E σ)

def natGraph : PositiveWeightedMultigraph V E where
  source := G.source
  target := G.target
  weight := fun e ↦ (G.weight e).degree
  weight_pos := fun e ↦ Nat.pos_of_ne_zero (fun h ↦
    G.weight_ne_zero e ((Finsupp.degree_eq_zero_iff _).mp h))

def vectorWeight (es : List E) : σ →₀ ℕ := (es.map G.weight).sum

@[simp] theorem vectorWeight_nil : vectorWeight G [] = 0 := rfl
@[simp] theorem vectorWeight_cons (e : E) (es : List E) :
    vectorWeight G (e :: es) = G.weight e + vectorWeight G es := rfl

theorem degree_vectorWeight (es : List E) :
    (vectorWeight G es).degree = (natGraph G).pathWeight es := by
  induction es with
  | nil => simp [vectorWeight]
  | cons e es ih => simp [vectorWeight_cons, map_add, ih, natGraph, pathWeight]

abbrev ExactWalk (s t : V) (n : σ →₀ ℕ) :=
  {es : List E // (natGraph G).IsWalk s t es ∧ vectorWeight G es = n}

noncomputable instance [Fintype E] [DecidableEq V] (s t : V) (n : σ →₀ ℕ) :
    Fintype (ExactWalk G s t n) :=
  Fintype.ofInjective (fun x : ExactWalk G s t n ↦
    (⟨x.val, x.property.1, by rw [← degree_vectorWeight, x.property.2]⟩ :
      (natGraph G).ExactWalk s t n.degree)) (by
        intro x y h
        exact Subtype.ext (congrArg Subtype.val h))

abbrev EmptyWalk (s t : V) (n : σ →₀ ℕ) :=
  {_x : Unit // s = t ∧ n = 0}

abbrev FirstTail (s t : V) (n : σ →₀ ℕ) :=
  Σ e : E, {_x : ExactWalk G (G.target e) t (n - G.weight e) //
    G.source e = s ∧ G.weight e ≤ n}

def firstEdgeEquiv (s t : V) (n : σ →₀ ℕ) :
    ExactWalk G s t n ≃ EmptyWalk s t n ⊕ FirstTail G s t n where
  toFun x := by
    rcases x with ⟨es, hw, hn⟩
    cases es with
    | nil => exact Sum.inl ⟨(), hw, hn.symm⟩
    | cons e es =>
      have he : G.weight e + vectorWeight G es = n := hn
      have hle : G.weight e ≤ n := by rw [← he]; exact le_self_add
      have hrest : vectorWeight G es = n - G.weight e :=
        eq_tsub_of_add_eq (by simpa [add_comm] using he)
      exact Sum.inr ⟨e, ⟨⟨es, hw.2, hrest⟩, hw.1, hle⟩⟩
  invFun x := by
    rcases x with h | ⟨e, ⟨⟨es, hw, hn⟩, hs, hle⟩⟩
    · exact ⟨[], h.property.1, h.property.2.symm⟩
    · exact ⟨e :: es, ⟨hs, hw⟩, by
        rw [vectorWeight_cons, hn, add_tsub_cancel_of_le hle]⟩
  left_inv x := by
    rcases x with ⟨es, hw, hn⟩
    cases es <;> rfl
  right_inv x := by
    rcases x with h | ⟨e, ⟨⟨es, hw, hn⟩, hs, hle⟩⟩
    · rfl
    · rfl

variable [Fintype E] [DecidableEq V] [DecidableEq σ] [CommRing R]
variable (m : E → R)

noncomputable def coefficient (s t : V) (n : σ →₀ ℕ) : R :=
  ∑ x : ExactWalk G s t n, ReleaseTransferScalar.walkMultiplicity m x.val

theorem coefficient_firstEdge (s t : V) (n : σ →₀ ℕ) :
    coefficient G m s t n = (if s = t ∧ n = 0 then 1 else 0) +
      ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
        m e * coefficient G m (G.target e) t (n - G.weight e) else 0 := by
  classical
  let f : EmptyWalk s t n ⊕ FirstTail G s t n → R :=
    Sum.elim (fun _ ↦ 1)
      (fun x ↦ m x.1 * ReleaseTransferScalar.walkMultiplicity m x.2.val.val)
  have hfirst : coefficient G m s t n = ∑ x, f x := by
    apply Fintype.sum_equiv (firstEdgeEquiv G s t n)
    intro x
    rcases x with ⟨es, hw, hn⟩
    cases es <;> rfl
  rw [hfirst, Fintype.sum_sum_type]
  change (∑ _x : EmptyWalk s t n, (1 : R)) +
    (∑ x : FirstTail G s t n, m x.1 * ReleaseTransferScalar.walkMultiplicity m x.2.val.val) = _
  have hempty : (∑ _x : EmptyWalk s t n, (1 : R)) =
      if s = t ∧ n = 0 then 1 else 0 := by
    by_cases h : s = t ∧ n = 0 <;> simp [EmptyWalk, h]
  rw [hempty]
  congr 1
  rw [Fintype.sum_sigma]
  apply Finset.sum_congr rfl
  intro e _
  by_cases h : G.source e = s ∧ G.weight e ≤ n
  · rw [ite_eq_left h, coefficient, Finset.mul_sum]
    apply Fintype.sum_equiv (Equiv.subtypeUnivEquiv fun _ ↦ h)
    intro x
    rfl
  · rw [ite_eq_right h]
    apply Finset.sum_eq_zero
    intro x _
    exact False.elim (h x.property)

end Komorebi.PaperII.ReleaseTransferMultigraded
