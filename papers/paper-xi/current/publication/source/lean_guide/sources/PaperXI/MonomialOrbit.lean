import PaperXI.MonomialAction
import Mathlib.RepresentationTheory.Intertwining
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.LinearAlgebra.DirectSum.Basis

/-! Decomposition of an actual monomial representation along actual invariant
basis orbits. The direct sum and its representation equivalence are constructed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonomialOrbit
open scoped DirectSum
open scoped Classical

variable {G X I Y V : Type*} [Group G] [Fintype Y]
variable [AddCommGroup V] [Module ℂ V]
variable (ρ : Representation ℂ G V) (b : Module.Basis X ℂ V)
variable (p : G →* Equiv.Perm X) (c : G → X → ℂˣ)
variable (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x))
variable (e : I × Y ≃ X) (q : I → G →* Equiv.Perm Y)
variable (he : ∀ g i y, p g (e (i,y)) = e (i,q i g y))

/-- Each invariant orbit has the actual restricted basis action. -/
def block (i : I) : Representation ℂ G (Y → ℂ) :=
  MonomialAction.representation (Pi.basisFun ℂ Y) (q i) (fun g y => c g (e (i,y)))
    (fun y => MonomialAction.weight_one b p c ρ hρ (e (i,y)))
    (fun g h y => by
      rw [MonomialAction.weight_mul b p c ρ hρ, he])

@[simp] theorem block_basis (i : I) (g : G) (y : Y) :
    block ρ b p c hρ e q he i g (Pi.basisFun ℂ Y y) =
      (c g (e (i,y)) : ℂ) • Pi.basisFun ℂ Y (q i g y) :=
  MonomialAction.representation_basis _ _ _ _ _ g y

@[simp] theorem block_single (i : I) (g : G) (y : Y) :
    block ρ b p c hρ e q he i g (Pi.single y 1) =
      (c g (e (i,y)) : ℂ) • Pi.single (q i g y) 1 := by
  simpa only [Pi.basisFun_apply] using block_basis ρ b p c hρ e q he i g y

/-- The basis of the literal direct sum of orbit spaces. -/
def sumBasis : Module.Basis (I × Y) ℂ (⨁ _ : I, Y → ℂ) :=
  (DFinsupp.basis (fun _ : I => Pi.basisFun ℂ Y)).reindex (Equiv.sigmaEquivProd I Y)

@[simp] theorem sumBasis_apply (i : I) (y : Y) :
    sumBasis (I := I) (Y := Y) (i,y) =
      DirectSum.lof ℂ I (fun _ => Y → ℂ) i (Pi.basisFun ℂ Y y) := by
  simp [sumBasis, DFinsupp.basis]
  rfl

/-- The actual basis reindexing, not a dimension-only comparison. -/
def linearEquiv : V ≃ₗ[ℂ] (⨁ _ : I, Y → ℂ) :=
  b.equiv sumBasis e.symm

@[simp] theorem linearEquiv_basis (i : I) (y : Y) :
    linearEquiv b e (b (e (i,y))) = sumBasis (I := I) (Y := Y) (i,y) := by
  simp [linearEquiv]

/-- Every original group operator is intertwined with the direct sum of
constructed orbit actions. -/
theorem intertwines (g : G) (v : V) :
    linearEquiv b e (ρ g v) =
      Representation.directSum (block ρ b p c hρ e q he) g (linearEquiv b e v) := by
  have h : (linearEquiv b e).toLinearMap.comp (ρ g) =
      (Representation.directSum (block ρ b p c hρ e q he) g).comp
        (linearEquiv b e).toLinearMap := by
    apply b.ext
    intro x
    obtain ⟨⟨i,y⟩, rfl⟩ := e.surjective x
    simp [hρ, he, Representation.directSum]
  exact DFunLike.congr_fun h v

/-- Representation equivalence with the actual direct sum of orbit modules. -/
def representationEquiv : Representation.Equiv ρ
    (Representation.directSum (block ρ b p c hρ e q he)) := by
  let F : Representation.IntertwiningMap ρ (Representation.directSum (block ρ b p c hρ e q he)) :=
    ⟨(linearEquiv b e).toLinearMap, fun g => LinearMap.ext (intertwines ρ b p c hρ e q he g)⟩
  exact F.ofBijective (linearEquiv b e).bijective

/-- Each constructed interaction summand has the actual coordinate dimension. -/
theorem block_finrank : Module.finrank ℂ (Y → ℂ) = Fintype.card Y := by
  simp

end PaperXI.MonomialOrbit
