import PaperX.PacketCohomology
import Mathlib.Algebra.Homology.ShortComplex.ModuleCat
import Mathlib.Algebra.Homology.ShortComplex.HomologicalComplex
import Mathlib.LinearAlgebra.Dimension.Constructions

/-!
Explicit bridge from the quotient used in this release to Mathlib's categorical
homology, including windows of arbitrary homological/cochain complexes.
-/
set_option autoImplicit false
namespace PaperX.ComplexCohomology

open CategoryTheory
open PaperX.Cohomology PaperX.PacketCohomology
open scoped DirectSum BigOperators
universe u v w
variable {R : Type u} [CommRing R]

def ofShortComplex (S : ShortComplex (ModuleCat.{v} R)) : Triple.{u,v} R where
  X₀ := S.X₁
  X₁ := S.X₂
  X₂ := S.X₃
  d₀ := S.f.hom
  d₁ := S.g.hom
  square := ModuleCat.hom_ext_iff.mp S.zero

def toShortComplex (C : Triple.{u,v} R) : ShortComplex (ModuleCat.{v} R) :=
  ShortComplex.moduleCatMk C.d₀ C.d₁ C.square

/-- Our explicit quotient agrees with the standard ModuleCat homology object. -/
noncomputable def standardHomologyEquiv (S : ShortComplex (ModuleCat.{v} R)) :
    S.homology ≃ₗ[R] H (ofShortComplex S) :=
  S.moduleCatHomologyIso.toLinearEquiv

noncomputable def quotientHomologyEquiv (C : Triple.{u,v} R) :
    (toShortComplex C).homology ≃ₗ[R] H C :=
  (toShortComplex C).moduleCatHomologyIso.toLinearEquiv

/-- The decomposition also applies to Mathlib's standard short-complex homology. -/
noncomputable def standardPacketEquiv {ι : Type w} [Fintype ι]
    (C : Triple.{u,v} R) (P : Resolution C ι) :
    (toShortComplex C).homology ≃ₗ[R] ⨁ i, H (packet (P.projectors i)) :=
  (quotientHomologyEquiv C).trans (cohomologyPacketEquiv P)

/-- A window from a genuine graded complex, with the library's endpoint convention. -/
noncomputable def window {κ : Type w} {c : ComplexShape κ}
    (K : HomologicalComplex (ModuleCat.{v} R) c) (r : κ) : Triple.{u,v} R :=
  ofShortComplex (K.sc r)

/-- This checks the meaning of H^r for arbitrary shapes, including degrees 0,1,2. -/
noncomputable def gradedHomologyEquiv {κ : Type w} {c : ComplexShape κ}
    (K : HomologicalComplex (ModuleCat.{v} R) c) (r : κ) :
    K.homology r ≃ₗ[R] H (window K r) :=
  standardHomologyEquiv (K.sc r)

noncomputable def gradedPacketEquiv {κ ι : Type w} {c : ComplexShape κ} [Fintype ι]
    (K : HomologicalComplex (ModuleCat.{v} R) c) (r : κ)
    (P : Resolution (window K r) ι) :
    K.homology r ≃ₗ[R] ⨁ i, H (packet (P.projectors i)) :=
  (gradedHomologyEquiv K r).trans (cohomologyPacketEquiv P)

/-- Over a field, finite-dimensional cohomologies have the expected sum of dimensions.
This is derived from the equivalence, not assumed as a substitute for it. -/
theorem dimension_sum {F : Type u} [Field F] {ι : Type w} [Fintype ι]
    (C : Triple.{u,v} F) (P : Resolution C ι)
    [∀ i, FiniteDimensional F (H (packet (P.projectors i)))] :
    Module.finrank F (H C) = ∑ i, Module.finrank F (H (packet (P.projectors i))) := by
  rw [(cohomologyPiEquiv P).finrank_eq, Module.finrank_pi_fintype]


/-- A morphism of genuine short complexes yields the corresponding cochain map. -/
def ofShortMap {S T : ShortComplex (ModuleCat.{v} R)} (f : S ⟶ T) :
    ChainMap (ofShortComplex S) (ofShortComplex T) where
  left := f.τ₁.hom
  middle := f.τ₂.hom
  right := f.τ₃.hom
  comm₀ := ModuleCat.hom_ext_iff.mp f.comm₁₂
  comm₁ := ModuleCat.hom_ext_iff.mp f.comm₂₃

/-- Restrict a genuine chain endomorphism to the selected window. -/
noncomputable def windowMap {κ : Type w} {c : ComplexShape κ}
    (K : HomologicalComplex (ModuleCat.{v} R) c) (r : κ) (p : K ⟶ K) :
    ChainMap (window K r) (window K r) :=
  ofShortMap ((HomologicalComplex.shortComplexFunctor _ c r).map p)

/-- The image at every degree, with its restricted differential, is a genuine
Mathlib HomologicalComplex, not only a three-term stand-in. -/
def imageComplex {κ : Type w} {c : ComplexShape κ}
    (K : HomologicalComplex (ModuleCat.{v} R) c) (p : K ⟶ K) :
    HomologicalComplex (ModuleCat.{v} R) c where
  X i := ModuleCat.of R (LinearMap.range (p.f i).hom)
  d i j := ModuleCat.ofHom (rangeMap (K.d i j).hom (p.f i).hom (p.f j).hom
    (ModuleCat.hom_ext_iff.mp (p.comm i j)))
  shape := by
    intro i j hij
    apply ModuleCat.hom_ext
    apply LinearMap.ext
    intro x
    apply Subtype.ext
    change (K.d i j).hom x.val = 0
    rw [K.shape i j hij]
    rfl
  d_comp_d' := by
    intro i j k _ _
    apply ModuleCat.hom_ext
    apply LinearMap.ext
    intro x
    apply Subtype.ext
    exact LinearMap.congr_fun (ModuleCat.hom_ext_iff.mp (K.d_comp_d i j k)) x.val

noncomputable def imageHomologyEquiv {κ : Type w} {c : ComplexShape κ}
    (K : HomologicalComplex (ModuleCat.{v} R) c) (r : κ) (p : K ⟶ K) :
    (imageComplex K p).homology r ≃ₗ[R] H (packet (windowMap K r p)) :=
  standardHomologyEquiv ((imageComplex K p).sc r)

/-- Build the window resolution directly from actual chain endomorphisms. -/
noncomputable def chainResolution {κ ι : Type w} {c : ComplexShape κ} [Fintype ι]
    (K : HomologicalComplex (ModuleCat.{v} R) c) (r : κ) (P : ι → (K ⟶ K))
    (hid : ∀ i, ((P i).f r).hom.comp ((P i).f r).hom = ((P i).f r).hom)
    (hort : ∀ i j, i ≠ j → ((P i).f r).hom.comp ((P j).f r).hom = 0)
    (hsum : ∑ i, ((P i).f r).hom = LinearMap.id) : Resolution (window K r) ι where
  projectors i := windowMap K r (P i)
  idempotent := hid
  orthogonal := hort
  complete := hsum

/-- The literal manuscript statement using Mathlib's genuine graded complexes
and its standard homology objects on BOTH sides. -/
noncomputable def chainCohomologyPacketEquiv {κ ι : Type w} {c : ComplexShape κ} [Fintype ι]
    (K : HomologicalComplex (ModuleCat.{v} R) c) (r : κ) (P : ι → (K ⟶ K))
    (hid : ∀ i, ((P i).f r).hom.comp ((P i).f r).hom = ((P i).f r).hom)
    (hort : ∀ i j, i ≠ j → ((P i).f r).hom.comp ((P j).f r).hom = 0)
    (hsum : ∑ i, ((P i).f r).hom = LinearMap.id) :
    K.homology r ≃ₗ[R] ⨁ i, (imageComplex K (P i)).homology r :=
  (gradedHomologyEquiv K r).trans
    ((cohomologyPiEquiv (chainResolution K r P hid hort hsum)).trans
      ((LinearEquiv.piCongrRight (fun i => (imageHomologyEquiv K r (P i)).symm)).trans
        (DirectSum.linearEquivFunOnFintype R ι
          (fun i => (imageComplex K (P i)).homology r)).symm))

end PaperX.ComplexCohomology
