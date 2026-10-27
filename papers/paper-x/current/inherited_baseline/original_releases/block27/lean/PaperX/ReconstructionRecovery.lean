import PaperX.MonodromyReconstruction
import PaperX.UnipotentLogarithm
import PaperX.WeilMorphisms

/-! Recover both pieces of the original datum from reconstructed actions on
cubic nilpotence classes. A supplied group element must have trivial original
finite action in both data and nonzero cocycle parameter. This theorem does
not assert that such an arithmetic sample exists. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ReconstructionRecovery
open PaperX.WeilData PaperX.WeilMorphisms
open PaperX.MonodromyReconstruction PaperX.NilpotentExponential
open PaperX.UnipotentLogarithm
variable {K G : Type*} [Field K] [CharZero K] [Group G] {ν : G →* Kˣ}
variable {V W : Type*} [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

/-- An actual reconstructed-action intertwiner recovers the monodromy relation
from a single supplied nonzero unipotent sample. -/
theorem recover_monodromy {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (hD : D.N ^ 3 = 0) (hE : E.N ^ 3 = 0)
    (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1) (htu : t.value u ≠ 0)
    (f : V →ₗ[K] W)
    (hf : ∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x)) :
    E.N ∘ₗ f = f ∘ₗ D.N := by
  apply (expN_intertwines_iff hD hE f htu).mp
  ext x
  simpa [unipotent, hDu, hEu] using (hf u x).symm

/-- Once monodromy is recovered, inverse exponentials recover the original group action. -/
theorem recover_group {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (f : V →ₗ[K] W)
    (hN : E.N ∘ₗ f = f ∘ₗ D.N)
    (hf : ∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x))
    (g : G) (x : V) : f (D.r g x) = E.r g (f x) := by
  apply (expEquiv E.nilpotent (t.value g)).injective
  have hc := expN_intertwines D.nilpotent E.nilpotent f hN (t.value g)
  change expN E.N (t.value g) (f (D.r g x)) = expN E.N (t.value g) (E.r g (f x))
  calc
    _ = f (expN D.N (t.value g) (D.r g x)) := LinearMap.congr_fun hc _
    _ = _ := hf g x

/-- The recovered map is equivariant for both the original Weil action and N. -/
def recoverHom {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (hD : D.N ^ 3 = 0) (hE : E.N ^ 3 = 0)
    (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1) (htu : t.value u ≠ 0)
    (f : V →ₗ[K] W)
    (hf : ∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x)) : Hom D E where
  map := f
  group_eq := recover_group t f (recover_monodromy t hD hE u hDu hEu htu f hf) hf
  monodromy_eq x :=
    (LinearMap.congr_fun (recover_monodromy t hD hE u hDu hEu htu f hf) x).symm

/-- Under explicit cubic and sample hypotheses, reconstructed-action intertwiners
are exactly the maps respecting both components of the original datum. -/
theorem reconstruct_intertwiner_iff {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (hD : D.N ^ 3 = 0) (hE : E.N ^ 3 = 0)
    (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1) (htu : t.value u ≠ 0)
    (f : V →ₗ[K] W) :
    (∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x)) ↔
      (∀ g x, f (D.r g x) = E.r g (f x)) ∧ E.N ∘ₗ f = f ∘ₗ D.N := by
  constructor
  · intro hf
    have hn := recover_monodromy t hD hE u hDu hEu htu f hf
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
    (t : TwistedCocycle ν) (hD : D.N ^ 3 = 0) (hE : E.N ^ 3 = 0)
    (u : G) (hDu : D.r u = 1) (hEu : E.r u = 1) (htu : t.value u ≠ 0)
    (hρ : reconstruct D t = reconstruct E t) : D = E := by
  have hf : ∀ g x, (LinearMap.id : V →ₗ[K] V) (reconstruct D t g x) =
      reconstruct E t g ((LinearMap.id : V →ₗ[K] V) x) := by
    intro g x
    simp only [LinearMap.id_apply, hρ]
  have h := (reconstruct_intertwiner_iff t hD hE u hDu hEu htu LinearMap.id).mp hf
  apply datum_ext
  · ext g x
    exact h.1 g x
  · simpa only [LinearMap.id_comp, LinearMap.comp_id] using h.2.symm

end PaperX.ReconstructionRecovery
