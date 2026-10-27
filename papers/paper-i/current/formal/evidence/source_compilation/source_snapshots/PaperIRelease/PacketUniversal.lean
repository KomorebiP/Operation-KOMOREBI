import KomorebiVerification.ExactCoordinates
import KomorebiVerification.PaperIBlockCompletion

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperIRelease.PacketUniversal
open Komorebi.Foundation Komorebi.Foundation.LinearProjectorFamily
universe u v w x y
variable {R : Type u} [CommSemiring R]
variable {M : Type v} [AddCommMonoid M] [Module R M]
variable {N : Type w} [AddCommMonoid N] [Module R N]
variable {ι : Type x} [Fintype ι]
variable (P : LinearProjectorFamily R M ι)

/-- Projection with its actual range as codomain. -/
def packetProjection (i : ι) : M →ₗ[R] (P.proj i).range := (P.proj i).rangeRestrict

/-- Extend linear maps out of every packet by the finite sum. -/
def assembleOut (f : (i : ι) → (P.proj i).range →ₗ[R] N) : M →ₗ[R] N :=
  ∑ i, (f i).comp (packetProjection P i)

@[simp] theorem assembleOut_packet (f : (i : ι) → (P.proj i).range →ₗ[R] N)
    (i : ι) (m : (P.proj i).range) : assembleOut P f m = f i m := by
  classical
  rw [assembleOut, LinearMap.sum_apply, Finset.sum_eq_single i]
  · change f i (packetProjection P i m) = f i m
    congr 1
    apply Subtype.ext
    obtain ⟨x, hx⟩ := m.property
    change P.proj i m = m
    rw [← hx]
    exact P.idempotent i x
  · intro j _ hji
    change f j (packetProjection P j m) = 0
    have hz : packetProjection P j m = 0 := by
      apply Subtype.ext
      obtain ⟨x, hx⟩ := m.property
      change P.proj j m = 0
      rw [← hx]
      exact P.orthogonal hji x
    rw [hz, map_zero]
  · simp

/-- Existence and uniqueness of extension from the actual packet inclusions. -/
theorem unique_packet_extension (f : (i : ι) → (P.proj i).range →ₗ[R] N) :
    ∃! g : M →ₗ[R] N, ∀ (i : ι) (m : (P.proj i).range), g (m : M) = f i m := by
  refine ⟨assembleOut P f, assembleOut_packet P f, ?_⟩
  intro g hg
  ext m
  rw [← P.complete m, map_sum, map_sum]
  apply Finset.sum_congr rfl
  intro i _
  exact (hg i ⟨P.proj i m, ⟨m, rfl⟩⟩).trans
    (assembleOut_packet P f i ⟨P.proj i m, ⟨m, rfl⟩⟩).symm

/-- Assemble linear maps into the packets using actual synthesis. -/
def assembleIn (f : (i : ι) → N →ₗ[R] (P.proj i).range) : N →ₗ[R] M :=
  P.rangeSynthesis.comp (LinearMap.pi f)

@[simp] theorem packet_assembleIn (f : (i : ι) → N →ₗ[R] (P.proj i).range)
    (i : ι) (n : N) : packetProjection P i (assembleIn P f n) = f i n := by
  exact congrFun (P.rangeAnalysis_rangeSynthesis (fun j => f j n)) i

/-- Existence and uniqueness of assembly into actual packet ranges. -/
theorem unique_packet_lift (f : (i : ι) → N →ₗ[R] (P.proj i).range) :
    ∃! g : N →ₗ[R] M, ∀ i n, packetProjection P i (g n) = f i n := by
  refine ⟨assembleIn P f, packet_assembleIn P f, ?_⟩
  intro g hg
  ext n
  apply P.exactPacketCoordinates.injective
  funext i
  exact (hg i n).trans (packet_assembleIn P f i n).symm

/-- A linear map is determined by all its transfer blocks. -/
theorem transferBlock_ext {κ : Type y} [Fintype κ]
    (Q : LinearProjectorFamily R N κ) (U V : M →ₗ[R] N)
    (h : ∀ j i, transferBlock P Q U j i = transferBlock P Q V j i) : U = V := by
  rw [← transferBlock_reconstruction_linearMap P Q U,
    ← transferBlock_reconstruction_linearMap P Q V]
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro i _
  exact h j i

/-- The full blockwise intertwining equivalence, with distinct source and target packets. -/
theorem block_intertwining_iff {κ : Type y} [Fintype κ]
    (Q : LinearProjectorFamily R N κ) (T : Module.End R M)
    (S : Module.End R N) (U : M →ₗ[R] N) :
    U.comp T = S.comp U ↔ ∀ j i,
      (∑ b, (transferBlock P Q U j b).comp (transferBlock P P T b i)) =
      ∑ d, (transferBlock Q Q S j d).comp (transferBlock P Q U d i) := by
  constructor
  · intro h j i
    rw [← transferBlock_comp_linearMap P P Q T U,
      ← transferBlock_comp_linearMap P Q Q U S, h]
  · intro h
    apply transferBlock_ext P Q
    intro j i
    rw [transferBlock_comp_linearMap P P Q T U,
      transferBlock_comp_linearMap P Q Q U S]
    exact h j i

end Komorebi.PaperIRelease.PacketUniversal
