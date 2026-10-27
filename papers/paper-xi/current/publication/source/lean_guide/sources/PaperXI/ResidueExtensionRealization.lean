import PaperXI.UnramifiedPolynomial
import Mathlib.FieldTheory.PrimitiveElement
import Mathlib.Algebra.Polynomial.Lifts

/-! Realization of any finite separable extension of the actual base residue field.
The monic lift and its ring/field are constructed; no ambient Galois extension,
residue embedding into an existing extension, or degree certificate is supplied. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ResidueExtensionRealization
open Polynomial IsLocalRing
variable (R : Type*) [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
variable (s : Type*) [Field s] [Algebra (ResidueField R) s]
variable [FiniteDimensional (ResidueField R) s] [Algebra.IsSeparable (ResidueField R) s]

def residueBasis : PowerBasis (ResidueField R) s :=
  Field.powerBasisOfFiniteOfSeparable (ResidueField R) s

def residuePolynomial : (ResidueField R)[X] :=
  minpoly (ResidueField R) (residueBasis R s).gen

theorem residuePolynomial_monic : (residuePolynomial R s).Monic :=
  minpoly.monic (residueBasis R s).isIntegral_gen

theorem residuePolynomial_irreducible : Irreducible (residuePolynomial R s) :=
  minpoly.irreducible (residueBasis R s).isIntegral_gen

theorem residuePolynomial_degree :
    (residuePolynomial R s).natDegree = Module.finrank (ResidueField R) s := by
  rw [residuePolynomial, (residueBasis R s).natDegree_minpoly,
    (residueBasis R s).finrank]

theorem exists_monic_lift :
    ∃ f : R[X], f.map (residue R) = residuePolynomial R s ∧
      f.natDegree = Module.finrank (ResidueField R) s ∧ f.Monic := by
  have hl : residuePolynomial R s ∈ Polynomial.lifts (residue R) :=
    (Polynomial.mem_lifts _).mpr
      (Polynomial.map_surjective (residue R) residue_surjective (residuePolynomial R s))
  obtain ⟨f, hf, hd, hm⟩ :=
    Polynomial.lifts_and_natDegree_eq_and_monic hl (residuePolynomial_monic R s)
  exact ⟨f, hf, hd.trans (residuePolynomial_degree R s), hm⟩

def liftedPolynomial : R[X] := (exists_monic_lift R s).choose

theorem liftedPolynomial_map :
    (liftedPolynomial R s).map (residue R) = residuePolynomial R s :=
  (exists_monic_lift R s).choose_spec.1

theorem liftedPolynomial_degree :
    (liftedPolynomial R s).natDegree = Module.finrank (ResidueField R) s :=
  (exists_monic_lift R s).choose_spec.2.1

instance monic : Fact (liftedPolynomial R s).Monic :=
  ⟨(exists_monic_lift R s).choose_spec.2.2⟩

instance residueIrreducible :
    Fact (Irreducible ((liftedPolynomial R s).map (residue R))) :=
  ⟨by rw [liftedPolynomial_map]; exact residuePolynomial_irreducible R s⟩

abbrev ring := AdjoinRoot (liftedPolynomial R s)
abbrev field := UnramifiedPolynomial.field (liftedPolynomial R s)

/-- The full residue field, not merely an embedded subfield, realizes s. -/
def residueEquiv : ResidueField (ring R s) ≃ₐ[ResidueField R] s :=
  (MonicResidueAlgebra.residueAlgebraEquiv (liftedPolynomial R s)).trans <|
    (AdjoinRoot.algEquivOfEq (ResidueField R) _ _ (liftedPolynomial_map R s)).trans <|
      AdjoinRoot.equiv' (residuePolynomial R s) (residueBasis R s)
        (by change aeval (AdjoinRoot.root (residuePolynomial R s)) (residuePolynomial R s) = 0
            exact AdjoinRoot.eval₂_root _)
        (minpoly.aeval _ _)

theorem rank :
    Module.finrank R (ring R s) = Module.finrank (ResidueField R) s := by
  rw [MonicResidueAlgebra.rank, liftedPolynomial_degree]

theorem field_degree :
    Module.finrank (FractionRing R) (field R s) = Module.finrank (ResidueField R) s := by
  rw [UnramifiedPolynomial.field_degree, liftedPolynomial_degree]

variable [Finite (ResidueField R)]

theorem etale : Algebra.Etale R (ring R s) :=
  UnramifiedPolynomial.etale (liftedPolynomial R s)

theorem ramificationIdx_one : (maximalIdeal (ring R s)).ramificationIdx R = 1 :=
  UnramifiedPolynomial.ramificationIdx_one (liftedPolynomial R s)

theorem source :
    Module.Finite R (ring R s) ∧ Module.Free R (ring R s) ∧
    IsDiscreteValuationRing (ring R s) ∧ Algebra.Etale R (ring R s) ∧
    Nonempty (ResidueField (ring R s) ≃ₐ[ResidueField R] s) ∧
    Module.finrank (FractionRing R) (field R s) = Module.finrank (ResidueField R) s ∧
    (maximalIdeal (ring R s)).ramificationIdx R = 1 :=
  ⟨inferInstance, inferInstance, inferInstance, etale R s, ⟨residueEquiv R s⟩,
    field_degree R s, ramificationIdx_one R s⟩

end PaperXI.ResidueExtensionRealization
