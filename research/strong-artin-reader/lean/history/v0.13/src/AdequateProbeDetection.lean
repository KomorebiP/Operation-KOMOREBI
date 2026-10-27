import ProjectorProbeSurjectivity
import Mathlib.RepresentationTheory.Irreducible
import Mathlib.RepresentationTheory.Submodule
import Mathlib.RingTheory.Artinian.Module
import Mathlib.RingTheory.Finiteness.Basic

open scoped MonoidAlgebra

namespace Komorebi.StrongArtin.AdequateProbeDetection

open Komorebi.StrongArtin.ProjectorProbeSurjectivity

noncomputable section

variable {k G V ι : Type*} [Field k] [Group G]
  [Fintype G]
  [AddCommGroup V] [Module k V]
  [MulAction G ι]

/-- The common kernel of a covariant probe family, packaged as an invariant
submodule of the representation. -/
def jointKernelInvtSubmodule
    (ρ : Representation k G V)
    (probe : ι → Module.Dual k V)
    (hcov : ∀ g i v, probe (g • i) (ρ g v) = probe i v) :
    ρ.invtSubmodule where
  val := ⨅ i, LinearMap.ker (probe i)
  property := by
    rw [Representation.mem_invtSubmodule]
    intro g v hv
    change ρ g v ∈ (⨅ i, LinearMap.ker (probe i))
    rw [Submodule.mem_iInf]
    intro i
    rw [LinearMap.mem_ker]
    have hmem : v ∈ LinearMap.ker (probe (g⁻¹ • i)) := by
      exact (iInf_le (fun j => LinearMap.ker (probe j)) (g⁻¹ • i)) hv
    have hz : probe (g⁻¹ • i) v = 0 := LinearMap.mem_ker.mp hmem
    have hc := hcov g (g⁻¹ • i) v
    simpa [smul_smul] using hc.trans hz

omit [Fintype G] in
@[simp] theorem mem_jointKernelInvtSubmodule_iff
    (ρ : Representation k G V)
    (probe : ι → Module.Dual k V)
    (hcov : ∀ g i v, probe (g • i) (ρ g v) = probe i v)
    (v : V) :
    v ∈ (jointKernelInvtSubmodule ρ probe hcov : Submodule k V) ↔
      ∀ i : ι, probe i v = 0 := by
  change v ∈ (⨅ i, LinearMap.ker (probe i)) ↔ _
  simp

/-- The representation-theoretic spectral-projector clause: every simple
invariant packet is seen by at least one probe. -/
def DetectsEverySimplePacket
    (ρ : Representation k G V)
    (probe : ι → Module.Dual k V) : Prop :=
  ∀ S : ρ.invtSubmodule, IsAtom S →
    ∃ i : ι, ∃ x : V, x ∈ (S : Submodule k V) ∧ probe i x ≠ 0

/-- A finite-dimensional representation of a finite group has a simple
invariant packet inside every nonzero invariant submodule. No modular
semisimplicity assumption is used. -/
theorem exists_simple_invtSubmodule_le_nonzero
    [FiniteDimensional k V]
    (ρ : Representation k G V)
    (K : ρ.invtSubmodule) (hK : K ≠ ⊥) :
    ∃ S : ρ.invtSubmodule, IsAtom S ∧ S ≤ K := by
  have hkG : IsArtinianRing k[G] := IsArtinianRing.of_finite k k[G]
  let _ : IsArtinianRing k[G] := hkG
  have hfin : Module.Finite k[G] ρ.asModule :=
    Module.Finite.of_restrictScalars_finite k k[G] ρ.asModule
  let _ : Module.Finite k[G] ρ.asModule := hfin
  have hart : IsArtinian k[G] ρ.asModule := by infer_instance
  let _ : IsArtinian k[G] ρ.asModule := hart
  have hmap : ρ.mapSubmodule K ≠ ⊥ := by
    intro hbot
    have heq : ρ.mapSubmodule K = ρ.mapSubmodule (⊥ : ρ.invtSubmodule) := by
      simpa using hbot
    exact hK ((ρ.mapSubmodule).injective heq)
  obtain ⟨A, hAatom, hAK⟩ :=
    (eq_bot_or_exists_atom_le (ρ.mapSubmodule K)).resolve_left hmap
  let S : ρ.invtSubmodule := (ρ.mapSubmodule).symm A
  refine ⟨S, ?_, ?_⟩
  · exact ((ρ.mapSubmodule).symm.isAtom_iff A).2 hAatom
  · rw [← (ρ.mapSubmodule).le_iff_le]
    simpa [S] using hAK

/-- **Adequacy detection implies joint separation.** A covariant probe family
which detects every simple invariant packet has zero joint kernel on a finite-
dimensional representation of a finite group. -/
theorem separates_of_detectsEverySimplePacket
    [FiniteDimensional k V]
    (ρ : Representation k G V)
    (probe : ι → Module.Dual k V)
    (hcov : ∀ g i v, probe (g • i) (ρ g v) = probe i v)
    (hdet : DetectsEverySimplePacket ρ probe) :
    ∀ v : V, (∀ i : ι, probe i v = 0) → v = 0 := by
  intro v hv
  by_contra hv0
  let K : ρ.invtSubmodule := jointKernelInvtSubmodule ρ probe hcov
  have hvK : v ∈ (K : Submodule k V) := by
    exact (mem_jointKernelInvtSubmodule_iff ρ probe hcov v).2 hv
  have hK : K ≠ ⊥ := by
    intro hbot
    have hvbot : v ∈ (⊥ : Submodule k V) := by
      simpa [hbot] using hvK
    exact hv0 ((Submodule.mem_bot k).mp hvbot)
  obtain ⟨S, hSatom, hSK⟩ := exists_simple_invtSubmodule_le_nonzero ρ K hK
  obtain ⟨i, x, hxS, hxne⟩ := hdet S hSatom
  have hxK : x ∈ (K : Submodule k V) := hSK hxS
  have hxzero : probe i x = 0 :=
    (mem_jointKernelInvtSubmodule_iff ρ probe hcov x).1 hxK i
  exact hxne hxzero

/-- Hence the dual probe map is surjective under the actual simple-packet
spectral detection clause. -/
theorem dual_probeMap_surjective_of_detectsEverySimplePacket
    [FiniteDimensional k V]
    (ρ : Representation k G V)
    (probe : ι → Module.Dual k V)
    (hcov : ∀ g i v, probe (g • i) (ρ g v) = probe i v)
    (hdet : DetectsEverySimplePacket ρ probe) :
    Function.Surjective (probeEvalMap probe).dualMap := by
  apply dual_probeMap_surjective_of_separates probe
  exact separates_of_detectsEverySimplePacket ρ probe hcov hdet

end
end Komorebi.StrongArtin.AdequateProbeDetection

#print axioms Komorebi.StrongArtin.AdequateProbeDetection.exists_simple_invtSubmodule_le_nonzero
#print axioms Komorebi.StrongArtin.AdequateProbeDetection.separates_of_detectsEverySimplePacket
#print axioms Komorebi.StrongArtin.AdequateProbeDetection.dual_probeMap_surjective_of_detectsEverySimplePacket
