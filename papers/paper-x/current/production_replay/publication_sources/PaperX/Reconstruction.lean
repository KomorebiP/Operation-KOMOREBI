import Mathlib.RingTheory.AdicCompletion.RingHom
import Mathlib.RingTheory.LocalRing.RingHom.Basic
import Mathlib.Topology.Algebra.Nonarchimedean.AdicTopology

/-!
Paper X Block 02. The represented-point reconstruction theorem is implemented
using actual Mathlib ring homomorphisms and ideal-power quotients, rather than
an assumed bijection of sets. Completeness is an explicit coefficient-ring
hypothesis. Locality and adic continuity are proved separately below.
The universal lifting theorem is Mathlib's IsAdicComplete.liftRingHom.
-/
set_option autoImplicit false
namespace PaperX.Reconstruction

variable {R S : Type*} [CommRing R] [CommRing S]

/-- Compatible maps at all ideal-power precisions. Level zero is the trivial
quotient and is included solely to match Mathlib's indexing. -/
@[ext] structure RingFamily (R : Type*) [CommRing R] (I : Ideal S) where
  maps : (n : ℕ) → R →+* S ⧸ I ^ n
  compatible : ∀ {m n : ℕ} (h : m ≤ n),
    (Ideal.Quotient.factorPow I h).comp (maps n) = maps m

variable (I : Ideal S)

def reduce (F : R →+* S) : RingFamily R I where
  maps n := (Ideal.Quotient.mk (I ^ n)).comp F
  compatible := by
    intro m n h
    ext x
    simp

noncomputable def reconstruct [IsAdicComplete I S] (f : RingFamily R I) : R →+* S :=
  IsAdicComplete.liftRingHom I f.maps f.compatible

theorem reconstruct_reduces [IsAdicComplete I S] (f : RingFamily R I) (n : ℕ) :
    (Ideal.Quotient.mk (I ^ n)).comp (reconstruct I f) = f.maps n :=
  IsAdicComplete.mk_comp_liftRingHom I f.maps f.compatible n

theorem reconstruct_unique [IsAdicComplete I S] (f : RingFamily R I) (F : R →+* S)
    (h : ∀ n, (Ideal.Quotient.mk (I ^ n)).comp F = f.maps n) :
    F = reconstruct I f :=
  IsAdicComplete.eq_liftRingHom I f.maps f.compatible F h

theorem reconstruct_reduce [IsAdicComplete I S] (F : R →+* S) :
    reconstruct I (reduce I F) = F :=
  (reconstruct_unique I (reduce I F) F (fun _ => rfl)).symm

theorem reduce_reconstruct [IsAdicComplete I S] (f : RingFamily R I) :
    reduce I (reconstruct I f) = f := by
  ext n x
  exact congrArg (fun F : R →+* S ⧸ I ^ n => F x) (reconstruct_reduces I f n)

/-- The genuine ring-map version of Paper X's inverse-limit reconstruction. -/
noncomputable def ringReconstructionEquiv [IsAdicComplete I S] :
    (R →+* S) ≃ RingFamily R I where
  toFun := reduce I
  invFun := reconstruct I
  left_inv := reconstruct_reduce I
  right_inv := reduce_reconstruct I

/-- Completeness does not assert existence of compatible finite maps. -/
theorem ring_maps_nonempty_iff [IsAdicComplete I S] :
    Nonempty (R →+* S) ↔ Nonempty (RingFamily R I) :=
  ⟨fun ⟨F⟩ => ⟨reduce I F⟩, fun ⟨f⟩ => ⟨reconstruct I f⟩⟩

/-- Precomposition is compatible with reconstruction, giving source naturality. -/
def precompose {T : Type*} [CommRing T] (f : RingFamily R I) (g : T →+* R) :
    RingFamily T I where
  maps n := (f.maps n).comp g
  compatible := by
    intro m n h
    rw [← RingHom.comp_assoc, f.compatible h]

theorem reconstruct_precompose [IsAdicComplete I S]
    {T : Type*} [CommRing T] (f : RingFamily R I) (g : T →+* R) :
    reconstruct I (precompose I f g) = (reconstruct I f).comp g := by
  symm
  apply reconstruct_unique
  intro n
  rw [← RingHom.comp_assoc, reconstruct_reduces]
  rfl

/-- Locality of the first positive precision suffices to make the lift local. -/
theorem reconstruct_isLocal [IsAdicComplete I S] (f : RingFamily R I)
    (h : IsLocalHom (f.maps 1)) : IsLocalHom (reconstruct I f) := by
  have hc : IsLocalHom ((Ideal.Quotient.mk (I ^ 1)).comp (reconstruct I f)) := by
    rw [reconstruct_reduces]
    exact h
  let := hc
  exact isLocalHom_of_comp (reconstruct I f) (Ideal.Quotient.mk (I ^ 1))

/-- A local map of local rings preserves every power of the maximal ideal. -/
theorem local_map_preserves_powers [IsLocalRing R] [IsLocalRing S]
    (F : R →+* S) [IsLocalHom F] (n : ℕ) :
    (IsLocalRing.maximalIdeal R ^ n).map F ≤ IsLocalRing.maximalIdeal S ^ n := by
  rw [Ideal.map_pow]
  exact Ideal.pow_right_mono (IsLocalRing.map_maximalIdeal_le F) n

/-- Continuity in the actual maximal-ideal adic topologies, not a renamed
abstract continuity assumption. -/
theorem local_map_continuous [IsLocalRing R] [IsLocalRing S]
    (F : R →+* S) [IsLocalHom F] :
    @Continuous R S (IsLocalRing.maximalIdeal R).adicTopology
      (IsLocalRing.maximalIdeal S).adicTopology F := by
  let : WithIdeal R := ⟨IsLocalRing.maximalIdeal R⟩
  let : WithIdeal S := ⟨IsLocalRing.maximalIdeal S⟩
  exact (WithIdeal.uniformContinuous_of_map_le
    (IsLocalRing.map_maximalIdeal_le F)).continuous

/-- The reconstructed ring map is local and continuous if its residual map is local. -/
theorem local_continuous_reconstruction [IsAdicComplete I S]
    [IsLocalRing R] [IsLocalRing S] (f : RingFamily R I)
    (h : IsLocalHom (f.maps 1)) :
    ∃! F : R →+* S,
      (∀ n, (Ideal.Quotient.mk (I ^ n)).comp F = f.maps n) ∧
      IsLocalHom F ∧
      @Continuous R S (IsLocalRing.maximalIdeal R).adicTopology
        (IsLocalRing.maximalIdeal S).adicTopology F := by
  let := reconstruct_isLocal I f h
  refine ⟨reconstruct I f, ⟨reconstruct_reduces I f, inferInstance,
    local_map_continuous _⟩, ?_⟩
  intro F hF
  exact reconstruct_unique I f F hF.1

/-- Scalar compatibility also survives the limit, producing algebra maps. -/
theorem reconstruct_preserves_scalars [IsAdicComplete I S]
    {B : Type*} [CommRing B] [Algebra B R] [Algebra B S]
    (f : RingFamily R I)
    (hf : ∀ n b, f.maps n (algebraMap B R b) =
      Ideal.Quotient.mk (I ^ n) (algebraMap B S b)) (b : B) :
    reconstruct I f (algebraMap B R b) = algebraMap B S b := by
  have H : (reconstruct I f).comp (algebraMap B R) = algebraMap B S := by
    apply DFunLike.coe_injective
    apply IsHausdorff.funext' I
    intro n b'
    change Ideal.Quotient.mk (I ^ n) (reconstruct I f (algebraMap B R b')) = _
    simp only [reconstruct, IsAdicComplete.mk_liftRingHom]
    exact hf n b'
  exact congrArg (fun F : B →+* S => F b) H

/-- The inverse-limit equivalence restricted to local maps. -/
noncomputable def localReconstructionEquiv [IsAdicComplete I S]
    [IsLocalRing S] (hI : I ≠ ⊤) :
    {F : R →+* S // IsLocalHom F} ≃
      {f : RingFamily R I // IsLocalHom (f.maps 1)} where
  toFun F := ⟨reduce I F.val, by
    let : Nontrivial (S ⧸ I ^ 1) :=
      Ideal.Quotient.nontrivial_iff.mpr (by simpa using hI)
    let : IsLocalHom (Ideal.Quotient.mk (I ^ 1)) :=
      IsLocalHom.of_surjective _ Ideal.Quotient.mk_surjective
    let : IsLocalHom F.val := F.property
    change IsLocalHom ((Ideal.Quotient.mk (I ^ 1)).comp F.val)
    infer_instance⟩
  invFun f := ⟨reconstruct I f.val, reconstruct_isLocal I f.val f.property⟩
  left_inv F := Subtype.ext (reconstruct_reduce I F.val)
  right_inv f := Subtype.ext (reduce_reconstruct I f.val)

/-- Coefficient-preserving reconstruction as an actual algebra homomorphism. -/
noncomputable def reconstructAlg [IsAdicComplete I S]
    {B : Type*} [CommRing B] [Algebra B R] [Algebra B S]
    (f : RingFamily R I)
    (hf : ∀ n b, f.maps n (algebraMap B R b) =
      Ideal.Quotient.mk (I ^ n) (algebraMap B S b)) : R →ₐ[B] S where
  __ := reconstruct I f
  commutes' := reconstruct_preserves_scalars I f hf

/-- The represented deformation-point version, retaining scalar compatibility,
locality, and genuine adic continuity. Representability itself is not asserted. -/
theorem represented_local_algebra_reconstruction [IsAdicComplete I S]
    {B : Type*} [CommRing B] [Algebra B R] [Algebra B S]
    [IsLocalRing R] [IsLocalRing S] (f : RingFamily R I)
    (hf : ∀ n b, f.maps n (algebraMap B R b) =
      Ideal.Quotient.mk (I ^ n) (algebraMap B S b))
    (hl : IsLocalHom (f.maps 1)) :
    ∃! F : R →ₐ[B] S,
      (∀ n, (Ideal.Quotient.mk (I ^ n)).comp F.toRingHom = f.maps n) ∧
      IsLocalHom F.toRingHom ∧
      @Continuous R S (IsLocalRing.maximalIdeal R).adicTopology
        (IsLocalRing.maximalIdeal S).adicTopology F := by
  let F := reconstructAlg I f hf
  let : IsLocalHom (reconstruct I f) := reconstruct_isLocal I f hl
  refine ⟨F, ⟨reconstruct_reduces I f, reconstruct_isLocal I f hl,
    local_map_continuous (reconstruct I f)⟩, ?_⟩
  intro G hG
  ext x
  exact congrArg (fun H : R →+* S => H x) (reconstruct_unique I f G.toRingHom hG.1)

end PaperX.Reconstruction
