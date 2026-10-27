import MachineTheory.Behavior
import Mathlib.Data.Fintype.Powerset

/-! Reviewed Core v0.2, Theorem 3.1. Empty candidate sets and contradictory evidence are retained. -/
namespace Komorebi.MachineTheory

structure EvidenceAlgebra (Ω : Type*) where
  events : Set (Set Ω)
  univ_mem : Set.univ ∈ events
  inter_mem : ∀ E ∈ events, ∀ F ∈ events, E ∩ F ∈ events

namespace EvidenceAlgebra
variable {Ω Y : Type*} (E : EvidenceAlgebra Ω)
abbrev Event := {e : Set Ω // e ∈ E.events}
def total : E.Event := ⟨Set.univ, E.univ_mem⟩
def meet (e f : E.Event) : E.Event := ⟨e.val ∩ f.val, E.inter_mem _ e.property _ f.property⟩
def filter (e : E.Event) (V : Set Ω) : Set Ω := V ∩ e.val

def signature (t : Ω → Y) (V : Set Ω) : E.Event → Set Y :=
  fun e => t '' (V ∩ e.val)

@[simp] theorem signature_total (t : Ω → Y) (V : Set Ω) :
    E.signature t V E.total = t '' V := by
  simp [signature, total]

/-- A later correction is another coordinate of the original signature. -/
theorem signature_filter (t : Ω → Y) (V : Set Ω) (e f : E.Event) :
    E.signature t (E.filter e V) f = E.signature t V (E.meet e f) := by
  simp only [signature, filter, meet, Set.inter_assoc]

/-- Core 3.1, congruence for every permitted intersection filter. -/
theorem signature_congruence (t : Ω → Y) {V W : Set Ω}
    (h : E.signature t V = E.signature t W) (e : E.Event) :
    E.signature t (E.filter e V) = E.signature t (E.filter e W) := by
  funext f
  rw [E.signature_filter, E.signature_filter, h]

/-- The actual memory type contains attainable correction signatures only. -/
abbrev Memory (t : Ω → Y) := Attained (E.signature t)

def remember (t : Ω → Y) (V : Set Ω) : E.Memory t := record (E.signature t) V

noncomputable def update (t : Ω → Y) (e : E.Event) (s : E.Memory t) : E.Memory t := by
  let V := Classical.choose s.property
  exact E.remember t (E.filter e V)

/-- Choice of a realizing candidate set cannot alter the updated memory. -/
@[simp] theorem update_remember (t : Ω → Y) (e : E.Event) (V : Set Ω) :
    E.update t e (E.remember t V) = E.remember t (E.filter e V) := by
  apply Subtype.ext
  apply E.signature_congruence t
  exact Classical.choose_spec (E.remember t V).property

def read (t : Ω → Y) (s : E.Memory t) : Set Y := s.val E.total

@[simp] theorem read_remember (t : Ω → Y) (V : Set Ω) :
    E.read t (E.remember t V) = t '' V := E.signature_total t V

/-- The signature representation works after *every finite* evidence sequence. -/
theorem memory_finite_continuation (t : Ω → Y) (events : List E.Event) (V : Set Ω) :
    run (E.update t) events (E.remember t V) =
      E.remember t (run E.filter events V) := by
  induction events generalizing V with
  | nil => rfl
  | cons e events ih =>
    simp only [run_cons, E.update_remember]
    exact ih _

theorem memory_readout_continuation (t : Ω → Y) (events : List E.Event) (V : Set Ω) :
    E.read t (run (E.update t) events (E.remember t V)) =
      t '' (run E.filter events V) := by
  rw [E.memory_finite_continuation, E.read_remember]

/-- Every other exact deterministic memory must retain the whole signature. -/
theorem any_exact_memory_separates (t : Ω → Y) {M : Type*}
    (r : Set Ω → M) (readout : M → Set Y) (step : E.Event → M → M)
    (hq : ∀ V, readout (r V) = t '' V)
    (hs : ∀ e V, step e (r V) = r (E.filter e V)) :
    FiberConstant r (E.signature t) := by
  intro V W h
  funext e
  change t '' (E.filter e V) = t '' (E.filter e W)
  rw [← hq, ← hq, ← hs, ← hs, h]

/-- Strong minimality: a surjection from every exact initialized memory to signatures. -/
theorem memory_universal_property (t : Ω → Y) {M : Type*}
    (r : Set Ω → M) (readout : M → Set Y) (step : E.Event → M → M)
    (hq : ∀ V, readout (r V) = t '' V)
    (hs : ∀ e V, step e (r V) = r (E.filter e V)) :
    ∃ d : Attained r → E.Memory t, Function.Surjective d ∧
      ∀ V, d (record r V) = E.remember t V := by
  have hf : FiberConstant r (E.remember t) := by
    intro V W h
    exact Subtype.ext (E.any_exact_memory_separates t r readout step hq hs V W h)
  obtain ⟨d, hd⟩ := (decoder_exists_iff r (E.remember t)).mpr hf
  refine ⟨d, ?_, hd⟩
  intro s
  obtain ⟨V, hV⟩ := s.property
  refine ⟨record r V, ?_⟩
  rw [hd]
  exact Subtype.ext hV

/-- Core 3.1, finite cardinality bound on attained states, not whole ambient M. -/
theorem memory_minimal_card [Fintype Ω] (t : Ω → Y) {M : Type*}
    (r : Set Ω → M) (readout : M → Set Y) (step : E.Event → M → M)
    (hq : ∀ V, readout (r V) = t '' V)
    (hs : ∀ e V, step e (r V) = r (E.filter e V)) :
    Fintype.card (E.Memory t) ≤ Fintype.card (Attained r) := by
  classical
  obtain ⟨d, hd, _⟩ := E.memory_universal_property t r readout step hq hs
  exact Fintype.card_le_of_surjective d hd

/-- Contradiction is retained, rather than replaced by an arbitrary model. -/
@[simp] theorem signature_empty (t : Ω → Y) :
    E.signature t ∅ = fun _ => ∅ := by
  funext e
  simp [signature]

end EvidenceAlgebra
end Komorebi.MachineTheory
