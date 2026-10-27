import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper V, first block. Checked source; see the bundled build and axiom audit.
Pointwise partition identities are not by themselves the l2 bounded-operator bridge.
-/

open scoped BigOperators

namespace KomorebiPaperV

section Packets
variable {I R V : Type*} [DecidableEq R] [Zero V]

def packet (phase : I → R) (r : R) (x : I → V) : I → V :=
  fun i => if phase i = r then x i else 0

theorem packet_idempotent (phase : I → R) (r : R) (x : I → V) :
    packet phase r (packet phase r x) = packet phase r x := by
  funext i
  by_cases h : phase i = r <;> simp [packet, h]

theorem packet_annihilate (phase : I → R) (r s : R) (hne : r ≠ s)
    (x : I → V) : packet phase r (packet phase s x) = 0 := by
  funext i
  by_cases hr : phase i = r
  · simp [packet, hr, hne]
  · simp [packet, hr]
end Packets

section FinitePackets
variable {I R S V : Type*} [Fintype R] [DecidableEq R] [AddCommMonoid V]

theorem packet_complete (phase : I → R) (x : I → V) (i : I) :
    (∑ r : R, packet phase r x i) = x i := by
  classical
  calc
    (∑ r : R, packet phase r x i) = packet phase (phase i) x i := by
      apply Finset.sum_eq_single (phase i)
      · intro b _ hb
        simp [packet, Ne.symm hb]
      · simp
    _ = x i := by simp [packet]

omit [Fintype R] in
theorem packet_refinement [Fintype S] [DecidableEq S]
    (fine : I → S) (coarsen : S → R) (r : R) (x : I → V) (i : I) :
    packet (coarsen ∘ fine) r x i =
      ∑ s : S, if coarsen s = r then packet fine s x i else 0 := by
  classical
  symm
  calc
    (∑ s : S, if coarsen s = r then packet fine s x i else 0) =
        (if coarsen (fine i) = r then packet fine (fine i) x i else 0) := by
      apply Finset.sum_eq_single (fine i)
      · intro b _ hb
        simp [packet, Ne.symm hb]
      · simp
    _ = packet (coarsen ∘ fine) r x i := by
      simp [packet]
end FinitePackets

section AddressEquivalence
variable {I R Q V : Type*}

def analyzeAddress (e : I ≃ R × Q) (x : I → V) : R → Q → V :=
  fun r q => x (e.symm (r, q))

def synthesizeAddress (e : I ≃ R × Q) (c : R → Q → V) : I → V :=
  fun i => c (e i).1 (e i).2

theorem address_synthesize_analyze (e : I ≃ R × Q) (x : I → V) :
    synthesizeAddress e (analyzeAddress e x) = x := by
  funext i
  simp [synthesizeAddress, analyzeAddress]

theorem address_analyze_synthesize (e : I ≃ R × Q) (c : R → Q → V) :
    analyzeAddress e (synthesizeAddress e c) = c := by
  funext r q
  simp [synthesizeAddress, analyzeAddress]
end AddressEquivalence

section IntegerResidues
variable {V : Type*} [AddCommMonoid V]

def residuePacket (N : ℕ) (r : ZMod N) (x : ℤ → V) : ℤ → V :=
  packet (fun n : ℤ => (n : ZMod N)) r x

theorem residuePacket_idempotent (N : ℕ) (r : ZMod N) (x : ℤ → V) :
    residuePacket N r (residuePacket N r x) = residuePacket N r x := by
  exact packet_idempotent (fun n : ℤ => (n : ZMod N)) r x

theorem residuePacket_complete (N : ℕ) [NeZero N] (x : ℤ → V) (n : ℤ) :
    (∑ r : ZMod N, residuePacket N r x n) = x n := by
  exact packet_complete (fun n : ℤ => (n : ZMod N)) x n
end IntegerResidues

end KomorebiPaperV
