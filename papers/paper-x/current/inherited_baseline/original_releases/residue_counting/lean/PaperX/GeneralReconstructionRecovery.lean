import PaperX.MonodromyReconstruction
import PaperX.LogarithmicRecovery
import PaperX.ReconstructionRecovery
import PaperX.WeilMorphisms

/-! Recover the original group action and monodromy from reconstructed actions
for arbitrary nilpotence orders. A supplied common sample must have trivial
original action and a nonzero cocycle value. Arithmetic existence of such a
sample, and attachment to arbitrary Galois representations, remain separate. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.GeneralReconstructionRecovery
open PaperX.WeilData PaperX.WeilMorphisms
open PaperX.MonodromyReconstruction PaperX.NilpotentExponential
open PaperX.LogarithmicRecovery
variable {K G : Type*} [Field K] [CharZero K] [Group G] {ν : G →* Kˣ}
variable {V W : Type*} [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

/-- An actual reconstructed-action intertwiner recovers the monodromy relation
from a single supplied nonzero unipotent sample. -/
theorem recover_monodromy {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν)
    (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1) (htu : t.value u ≠ 0)
    (f : V →ₗ[K] W)
    (hf : ∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x)) :
    E.N ∘ₗ f = f ∘ₗ D.N := by
  apply (expN_intertwines_iff D.nilpotent E.nilpotent f htu).mp
  ext x
  simpa [unipotent, hDu, hEu] using (hf u x).symm

/-- Once monodromy is recovered, inverse exponentials recover the original group action. -/
theorem recover_group {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (f : V →ₗ[K] W)
    (hN : E.N ∘ₗ f = f ∘ₗ D.N)
    (hf : ∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x))
    (g : G) (x : V) : f (D.r g x) = E.r g (f x) :=
  PaperX.ReconstructionRecovery.recover_group t f hN hf g x

/-- The recovered map is equivariant for both the original Weil action and N. -/
def recoverHom {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν)
    (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1) (htu : t.value u ≠ 0)
    (f : V →ₗ[K] W)
    (hf : ∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x)) : Hom D E where
  map := f
  group_eq := recover_group t f (recover_monodromy t u hDu hEu htu f hf) hf
  monodromy_eq x :=
    (LinearMap.congr_fun (recover_monodromy t u hDu hEu htu f hf) x).symm

/-- Under the explicit common-sample hypotheses, reconstructed-action intertwiners
are exactly the maps respecting both components of the original datum. -/
theorem reconstruct_intertwiner_iff {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν)
    (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1) (htu : t.value u ≠ 0)
    (f : V →ₗ[K] W) :
    (∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x)) ↔
      (∀ g x, f (D.r g x) = E.r g (f x)) ∧ E.N ∘ₗ f = f ∘ₗ D.N := by
  constructor
  · intro hf
    have hn := recover_monodromy t u hDu hEu htu f hf
    exact ⟨recover_group t f hn hf, hn⟩
  · rintro ⟨hr, hn⟩ g x
    have hc := expN_intertwines D.nilpotent E.nilpotent f hn (t.value g)
    change f (expN D.N (t.value g) (D.r g x)) =
      expN E.N (t.value g) (E.r g (f x))
    calc
      _ = expN E.N (t.value g) (f (D.r g x)) := (LinearMap.congr_fun hc _).symm
      _ = _ := congrArg (expN E.N (t.value g)) (hr g x)

/-- With the sample hypotheses fixed, equal reconstructed representations
recover equal original actions and equal monodromy operators. -/
theorem datum_eq_of_reconstruct_eq {D E : Datum ν V}
    (t : TwistedCocycle ν)
    (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1) (htu : t.value u ≠ 0)
    (hρ : reconstruct D t = reconstruct E t) : D = E := by
  have hf : ∀ g x, (LinearMap.id : V →ₗ[K] V) (reconstruct D t g x) =
      reconstruct E t g ((LinearMap.id : V →ₗ[K] V) x) := by
    intro g x
    simp only [LinearMap.id_apply, hρ]
  have h := (reconstruct_intertwiner_iff t u hDu hEu htu LinearMap.id).mp hf
  apply datum_ext
  · ext g x
    exact h.1 g x
  · simpa only [LinearMap.id_comp, LinearMap.comp_id] using h.2.symm


/-- A reconstructed-action projector automatically respects the original
monodromy and group action under the same sample hypotheses. -/
theorem projector_commutes_original {D : Datum ν V}
    (t : TwistedCocycle ν) (u : G) (hDu : D.r u = 1) (htu : t.value u ≠ 0)
    (P : Module.End K V)
    (hP : ∀ g, P * reconstruct D t g = reconstruct D t g * P) :
    (∀ g, P * D.r g = D.r g * P) ∧ D.N * P = P * D.N := by
  have hf : ∀ g x, P (reconstruct D t g x) = reconstruct D t g (P x) :=
    fun g x => LinearMap.congr_fun (hP g) x
  have h := (reconstruct_intertwiner_iff t u hDu hDu htu P).mp hf
  exact ⟨fun g => LinearMap.ext (h.1 g), h.2⟩

/-- A reconstructed equivalence recovers the actual local invariant spaces,
without any uniform bound on the two nilpotence orders. -/
def recoveredFixedEquiv {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1)
    (htu : t.value u ≠ 0) (e : V ≃ₗ[K] W)
    (he : ∀ g x, e (reconstruct D t g x) = reconstruct E t g (e x))
    (H : Subgroup G) : fixedKernel D H ≃ₗ[K] fixedKernel E H :=
  let h := (reconstruct_intertwiner_iff t u hDu hEu htu e.toLinearMap).mp he
  fixedEquiv e h.1 (fun x => (LinearMap.congr_fun h.2 x).symm) H

theorem recovered_localCharpoly [FiniteDimensional K V] [FiniteDimensional K W]
    {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1)
    (htu : t.value u ≠ 0) (e : V ≃ₗ[K] W)
    (he : ∀ g x, e (reconstruct D t g x) = reconstruct E t g (e x))
    (H : Subgroup G) [H.Normal] (φ : G) :
    localCharpoly D H φ = localCharpoly E H φ := by
  have h := (reconstruct_intertwiner_iff t u hDu hEu htu e.toLinearMap).mp he
  exact localCharpoly_equiv e h.1 (fun x => (LinearMap.congr_fun h.2 x).symm) H φ

end PaperX.GeneralReconstructionRecovery
