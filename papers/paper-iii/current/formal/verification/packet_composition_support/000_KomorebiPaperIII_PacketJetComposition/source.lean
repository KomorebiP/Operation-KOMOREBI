/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIII.ContinuousPacketJets
import Mathlib.Analysis.Calculus.ContDiff.Comp

/-!
# Finite partition composition of actual packet jets

This is the packet expansion of mathlib's iterated Frechet derivative
composition theorem. `OrderedFinpartition n` lists the nonempty blocks of a
partition in the canonical order of their greatest elements. Every original
input slot and every intermediate packet label is retained. No symmetry
quotient or unproved combinatorial coefficient is inserted.
-/

set_option autoImplicit false
noncomputable section
open scoped BigOperators ContDiff

namespace Komorebi.PaperIII.PacketCoordinates
universe u v w z i j l
variable {K : Type u} [NontriviallyNormedField K]
variable {X : Type v} {Y : Type w} {Z : Type z}
variable [NormedAddCommGroup X] [NormedSpace K X]
variable [NormedAddCommGroup Y] [NormedSpace K Y]
variable [NormedAddCommGroup Z] [NormedSpace K Z]
variable {I : Type i} {J : Type j} {L : Type l}
variable [Fintype I] [Fintype J] [Fintype L]

/-- The complete finite partition formula for the literal range jet of a
composition, including every intermediate packet label and order zero. -/
theorem iteratedPacketJet_comp
    (P : System K X I) (M : System K Y J) (Q : System K Z L)
    (hM : ∀ j, Continuous (M.projector j))
    (hQ : ∀ l, Continuous (Q.projector l))
    (f : X → Y) (g : Y → Z) (n : Nat) (x : X)
    (hf : ContDiffAt K n f x) (hg : ContDiffAt K n g (f x))
    (gamma : L) (alpha : Fin n → I)
    (xs : (k : Fin n) → LinearMap.range (P.projector (alpha k))) :
    (iteratedPacketJet P Q hQ (g ∘ f) n x gamma alpha xs : Z) =
      ∑ c : OrderedFinpartition n, ∑ beta : Fin c.length → J,
        (iteratedPacketJet M Q hQ g c.length (f x) gamma beta
          (fun a => iteratedPacketJet P M hM f (c.partSize a) x (beta a)
            (fun k => alpha (c.emb a k))
            (fun k => xs (c.emb a k))) : Z) := by
  classical
  simp only [iteratedPacketJet_apply_coe]
  rw [iteratedFDeriv_comp hg hf le_rfl]
  simp only [FormalMultilinearSeries.taylorComp, sum_apply,
    FormalMultilinearSeries.compAlongOrderedFinpartition_apply,
    OrderedFinpartition.applyOrderedFinpartition_apply, ftaylorSeries, map_sum]
  apply Finset.sum_congr rfl
  intro c _
  have expansion := multilinear_input_expansion M
    (iteratedFDeriv K c.length g (f x)).toMultilinearMap
    (fun a => iteratedFDeriv K (c.partSize a) f x
      (fun k => (xs (c.emb a k) : X)))
  simpa only [map_sum, Function.comp_def, ContinuousMultilinearMap.coe_coe] using
    congrArg (Q.projector gamma) expansion

/-- A composite jet vanishes when every labelled partition has a zero outer
jet or at least one zero inner jet. This is a sufficient vanishing condition. -/
theorem iteratedPacketJet_comp_eq_zero_of
    (P : System K X I) (M : System K Y J) (Q : System K Z L)
    (hM : ∀ j, Continuous (M.projector j))
    (hQ : ∀ l, Continuous (Q.projector l))
    (f : X → Y) (g : Y → Z) (n : Nat) (x : X)
    (hf : ContDiffAt K n f x) (hg : ContDiffAt K n g (f x))
    (gamma : L) (alpha : Fin n → I)
    (hvanish : ∀ c : OrderedFinpartition n, ∀ beta : Fin c.length → J,
      iteratedPacketJet M Q hQ g c.length (f x) gamma beta = 0 ∨
        ∃ a : Fin c.length,
          iteratedPacketJet P M hM f (c.partSize a) x (beta a)
            (fun k => alpha (c.emb a k)) = 0) :
    iteratedPacketJet P Q hQ (g ∘ f) n x gamma alpha = 0 := by
  classical
  apply ContinuousMultilinearMap.ext
  intro xs
  apply Subtype.ext
  change (iteratedPacketJet P Q hQ (g ∘ f) n x gamma alpha xs : Z) = 0
  rw [iteratedPacketJet_comp P M Q hM hQ f g n x hf hg gamma alpha xs]
  apply Finset.sum_eq_zero
  intro c _
  apply Finset.sum_eq_zero
  intro beta _
  rcases hvanish c beta with houter | ⟨a, hinner⟩
  · simp only [houter, ContinuousMultilinearMap.zero_apply, Submodule.coe_zero]
  · have harg :
        iteratedPacketJet P M hM f (c.partSize a) x (beta a)
          (fun k => alpha (c.emb a k)) (fun k => xs (c.emb a k)) = 0 := by
      rw [hinner]
      rfl
    exact congrArg (fun z : LinearMap.range (Q.projector gamma) => (z : Z))
      ((iteratedPacketJet M Q hQ g c.length (f x) gamma beta).map_coord_zero a harg)

/-- Nonzero composite-jet support is contained in the structural partition
support. Cancellation can prevent the converse, which is not asserted. -/
theorem iteratedPacketJet_comp_support
    (P : System K X I) (M : System K Y J) (Q : System K Z L)
    (hM : ∀ j, Continuous (M.projector j))
    (hQ : ∀ l, Continuous (Q.projector l))
    (f : X → Y) (g : Y → Z) (n : Nat) (x : X)
    (hf : ContDiffAt K n f x) (hg : ContDiffAt K n g (f x))
    (gamma : L) (alpha : Fin n → I)
    (hnonzero : iteratedPacketJet P Q hQ (g ∘ f) n x gamma alpha ≠ 0) :
    ∃ c : OrderedFinpartition n, ∃ beta : Fin c.length → J,
      iteratedPacketJet M Q hQ g c.length (f x) gamma beta ≠ 0 ∧
        ∀ a : Fin c.length,
          iteratedPacketJet P M hM f (c.partSize a) x (beta a)
            (fun k => alpha (c.emb a k)) ≠ 0 := by
  classical
  by_contra hex
  apply hnonzero
  apply iteratedPacketJet_comp_eq_zero_of P M Q hM hQ f g n x hf hg gamma alpha
  intro c beta
  by_cases houter : iteratedPacketJet M Q hQ g c.length (f x) gamma beta = 0
  · exact Or.inl houter
  · right
    have hnot : ¬ ∀ a : Fin c.length,
        iteratedPacketJet P M hM f (c.partSize a) x (beta a)
          (fun k => alpha (c.emb a k)) ≠ 0 := by
      intro hall
      exact hex ⟨c, beta, houter, hall⟩
    obtain ⟨a, ha⟩ := not_forall.mp hnot
    exact ⟨a, not_not.mp ha⟩

end Komorebi.PaperIII.PacketCoordinates
