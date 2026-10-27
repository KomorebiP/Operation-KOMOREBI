import KomorebiLSM.StrictRationalGeometry
import KomorebiLSM.BernsteinGridSearch
import KomorebiLSM.ConvexMargin
import Mathlib.Data.Rat.Encodable

set_option autoImplicit false
namespace Komorebi.LSM.StrictRationalSearch
open scoped BigOperators Matrix
open LorentzCylinder RobustOrientedMargin RationalTransform
open TensorBernsteinCertificate RationalBernsteinMargin RationalBernsteinTermination
open BernsteinGridSearch StrictRationalGeometry
noncomputable section

/-- A complete finite description: rational affine transform, margin, common depth and all grid arrays. -/
abbrev Candidate (nf na : ℕ) := Parameters ℚ × ℚ × Σ N : ℕ,
  Fin nf → Fin na → Bool → Bool → GridData N

instance candidateEncodable (nf na : ℕ) : Encodable (Candidate nf na) := by
  unfold Candidate Parameters
  infer_instance

variable {nf na ni n : ℕ}
def transform (c : Candidate nf na) : RationalTransform.RationalMatrix := affineMatrix c.1
def margin (c : Candidate nf na) : ℚ := c.2.1
def depth (c : Candidate nf na) : ℕ := c.2.2.1
def grids (c : Candidate nf na) := c.2.2.2

def Valid (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) : Prop :=
  (transform c).det≠0 ∧ 0<margin c ∧
  (∀ j,StrictVector (transform c *ᵥ z j)) ∧
  ∀ i a which left, gridValid
    (testPolynomial (rationalConjugated (transform c) (G i a)) (margin c) which left)
    square (depth c) (grids c i a which left)

/-- Every submitted test is a finite rational sign or finitely supported polynomial comparison. -/
instance decidableValid (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) : Decidable (Valid G z c) := by
  rcases c with ⟨q,kappa,N,d⟩
  unfold Valid transform margin depth grids StrictVector
  dsimp only
  infer_instance

def certificate (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c) (i : Fin nf) (a : Fin na) :
    Certificate (rationalConjugated (transform c) (G i a)) (margin c) where
  orientationWitness left :=
    (toUniform _ _ (grids c i a false left) (h.2.2.2 i a false left)).toSubdivision
  squareGapWitness left :=
    (toUniform _ _ (grids c i a true left) (h.2.2.2 i a true left)).toSubdivision

theorem candidate_exists (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (T : RealMatrix) (hT : IsUnit T.det) (hmass : MassPreserving T)
    (hinit : ∀ j,0<slack (operator T (rationalState (z j)))) (eta : ℝ) (heta : 0<eta)
    (hmargin : ∀ i a u,u∈Set.Icc (-1 : ℝ) 1 → eta≤sigma (conjugated T (G i a) u)) :
    ∃ c : Candidate nf na, Valid G z c := by
  obtain ⟨q,kappa,hk,hq,hi,hm⟩ := rational_strict_sector G (fun j => rationalState (z j))
    T hT hmass hinit eta heta hmargin
  have hcombined : ∀ ia : Fin nf × Fin na, ∀ u, u∈Set.Icc (-1 : ℝ) 1 →
      (kappa : ℝ)<sigma (PolynomialGram.operatorPolynomial
        (fun k => RationalBernsteinMargin.matrixOperator (rationalConjugated (affineMatrix q) (G ia.1 ia.2) k)) u) :=
    fun ia => hm ia.1 ia.2
  obtain ⟨N,hN⟩ := strict_family_eventual
    (fun ia : Fin nf × Fin na => rationalConjugated (affineMatrix q) (G ia.1 ia.2)) kappa hcombined
  let c : Candidate nf na := ⟨q,kappa,N,fun i a which left =>
    ofUniform (hN N le_rfl (i,a) which left).some⟩
  refine ⟨c,isUnit_iff_ne_zero.mp hq,hk,?_,?_⟩
  · intro j
    rw [strictVector_iff_slack,← operator_rationalState]
    exact hi j
  · intro i a which left
    exact ofUniform_valid (hN N le_rfl (i,a) which left).some

/-- This formal semidecision uses the explicit finite checker, not an existence oracle.
Mathlib's polynomial representation is noncomputable; no Lean-VM extraction is claimed. -/
def search (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) : ℕ → Option (Candidate nf na) :=
  BernsteinGridSearch.search (Valid G z)

theorem search_sound (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (budget : ℕ) (c : Candidate nf na)
    (h : search G z budget=some c) : Valid G z c :=
  BernsteinGridSearch.search_sound _ h

/-- A strict actual real sector gives a finite search stage and a stable sound return thereafter. -/
theorem conditional_search (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (T : RealMatrix) (hT : IsUnit T.det) (hmass : MassPreserving T)
    (hinit : ∀ j,0<slack (operator T (rationalState (z j)))) (eta : ℝ) (heta : 0<eta)
    (hmargin : ∀ i a u,u∈Set.Icc (-1 : ℝ) 1 → eta≤sigma (conjugated T (G i a) u)) :
    ∃ budget c, Valid G z c ∧ ∀ b,budget≤b → search G z b=some c :=
  BernsteinGridSearch.search_eventually _
    (candidate_exists G z T hT hmass hinit eta heta hmargin)

/-- These are the supplied complete families under the returned actual rational similarity. -/
def families (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (c : Candidate nf na) : Fin nf → ConvexMargin.Family (Fin na) n ℂ :=
  fun i a k => RationalBernsteinMargin.matrixOperator (rationalConjugated (transform c) (G i a) k)

def initials (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) : Fin ni → State ℂ :=
  fun j => operator (castMatrix (transform c)) (rationalState (z j))

theorem valid_unit (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c) : IsUnit (transform c).det :=
  isUnit_iff_ne_zero.mpr h.1

theorem transform_mass (c : Candidate nf na) : MassPreserving (castMatrix (transform c)) := by
  change MassPreserving (castMatrix (affineMatrix c.1))
  rw [← affineMatrix_cast]
  exact affineMatrix_mass _

/-- The fixed input families retain their independently checked exact integrated mass. -/
def OriginalMass (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix) : Prop :=
  ∀ i a y, ((∑ k : Fin n,UniformIntervalMoments.moment k • operator (castMatrix (G i a k))) y).1=y.1

theorem valid_feasible (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c) (hm : OriginalMass G)
    (i : Fin nf) : families G c i∈ConvexMargin.feasible (fun _ _ => (margin c : ℝ)) := by
  constructor
  · intro a u hu
    exact (certificate G z c h i a).margin u hu
  · intro a y
    change ((∑ k : Fin n,UniformIntervalMoments.moment k • families G c i a k) y).1=y.1
    simp only [families,rational_conjugated_coefficient (transform c) (valid_unit G z c h)]
    exact conjugate_mass _ (unit_castMatrix _ (valid_unit G z c h)) (transform_mass c)
      (fun k => operator (castMatrix (G i a k))) (fun k => UniformIntervalMoments.moment k) (hm i a) y

theorem valid_initial (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c)
    (hz : ∀ j,z j 0=1) (j : Fin ni) : initials z c j∈(probabilityCone (V := ℂ)).base := by
  have hp := (strictVector_iff_slack _).mp (h.2.2.1 j)
  rw [← operator_rationalState] at hp
  refine ⟨?_,?_⟩
  · change ‖(initials z c j).2‖≤(initials z c j).1
    change 0<(initials z c j).1-‖(initials z c j).2‖ at hp
    linarith
  · change (operator (castMatrix (transform c)) (rationalState (z j))).1=1
    rw [mass_preserving_operator _ (transform_mass c)]
    change (z j 0 : ℝ)=1
    exact_mod_cast hz j

/-- Every returned complete-family convex combination is an actual density instrument. -/
def hullInstrument (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c) (hm : OriginalMass G)
    (F : ConvexMargin.Family (Fin na) n ℂ) (hF : F∈convexHull ℝ (Set.range (families G c))) :
    ContinuousInstrument.DensityInstrument (A := Fin na) (probabilityCone (V := ℂ)) UniformIntervalMoments.measure :=
  ConvexMargin.instrument (fun _ _ => (margin c : ℝ)) F
    (ConvexMargin.hull_feasible (families G c) _ (valid_feasible G z c h hm) hF)
    (fun _ _ _ => by exact_mod_cast h.2.1.le)

/-- Complete operator and initial convex hulls use independent coefficients and have all-horizon laws. -/
theorem returned_hull_probability (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c) (hm : OriginalMass G)
    (hz : ∀ j,z j 0=1) (F : ConvexMargin.Family (Fin na) n ℂ)
    (hF : F∈convexHull ℝ (Set.range (families G c)))
    (y : State ℂ) (hy : y∈convexHull ℝ (Set.range (initials z c)))
    (policy : ContinuousRecords.Policy (A := Fin na) (Y := ℝ)) (N : ℕ) :
    MeasureTheory.IsProbabilityMeasure (ContinuousRecords.recordLaw
      (hullInstrument G z c h hm F hF) policy y N) :=
  ContinuousRecords.recordLaw_probability _ policy
    ⟨y,ConvexMargin.hull_initial (initials z c) (valid_initial G z c h hz) hy⟩ N

/-- The complete conditional result connects the same returned finite description to actual hull laws. -/
theorem conditional_search_with_hulls
    (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (hm : OriginalMass G) (hz : ∀ j,z j 0=1)
    (T : RealMatrix) (hT : IsUnit T.det) (hmass : MassPreserving T)
    (hinit : ∀ j,0<slack (operator T (rationalState (z j)))) (eta : ℝ) (heta : 0<eta)
    (hmargin : ∀ i a u,u∈Set.Icc (-1 : ℝ) 1 → eta≤sigma (conjugated T (G i a) u)) :
    ∃ (budget : ℕ) (c : Candidate nf na) (h : Valid G z c),
      (∀ b,budget≤b → search G z b=some c) ∧
      ∀ (F : ConvexMargin.Family (Fin na) n ℂ)
        (hF : F∈convexHull ℝ (Set.range (families G c)))
        (y : State ℂ) (_hy : y∈convexHull ℝ (Set.range (initials z c)))
        (policy : ContinuousRecords.Policy (A := Fin na) (Y := ℝ)) (N : ℕ),
        MeasureTheory.IsProbabilityMeasure (ContinuousRecords.recordLaw
          (hullInstrument G z c h hm F hF) policy y N) := by
  obtain ⟨budget,c,h,hstable⟩ := conditional_search G z T hT hmass hinit eta heta hmargin
  exact ⟨budget,c,h,hstable,returned_hull_probability G z c h hm hz⟩

/-- The same coordinate change acts linearly on every complete real coefficient family. -/
def transformFamily (T : RealMatrix) : ConvexMargin.Family (Fin na) n ℂ →ₗ[ℝ]
    ConvexMargin.Family (Fin na) n ℂ where
  toFun F a k := conjugate T (F a k)
  map_add' F H := by
    funext a k
    apply ContinuousLinearMap.ext
    intro y
    simp [conjugate]
  map_smul' r F := by
    funext a k
    apply ContinuousLinearMap.ext
    intro y
    simp [conjugate]

def sourceFamilies (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix) :
    Fin nf → ConvexMargin.Family (Fin na) n ℂ := fun i a k => operator (castMatrix (G i a k))

def sourceInitials (z : Fin ni → Fin 3 → ℚ) : Fin ni → State ℂ := fun j => rationalState (z j)

theorem source_hull_mapped (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c)
    (F : ConvexMargin.Family (Fin na) n ℂ) (hF : F∈convexHull ℝ (Set.range (sourceFamilies G))) :
    transformFamily (castMatrix (transform c)) F∈convexHull ℝ (Set.range (families G c)) := by
  let L := transformFamily (castMatrix (transform c)) (na := na) (n := n)
  have himage : L F∈convexHull ℝ (L '' Set.range (sourceFamilies G)) := by
    rw [← L.image_convexHull]
    exact ⟨F,hF,rfl⟩
  have heq : (fun i => L (sourceFamilies G i)) = families G c := by
    funext i a k
    exact (rational_conjugated_coefficient (transform c) (valid_unit G z c h) (G i a) k).symm
  rw [← Set.range_comp',heq] at himage
  exact himage

theorem source_initial_hull_mapped (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na)
    (y : State ℂ) (hy : y∈convexHull ℝ (Set.range (sourceInitials z))) :
    operator (castMatrix (transform c)) y∈convexHull ℝ (Set.range (initials z c)) := by
  let L := (operator (castMatrix (transform c))).toLinearMap
  have himage : L y∈convexHull ℝ (L '' Set.range (sourceInitials z)) := by
    rw [← L.image_convexHull]
    exact ⟨y,hy,rfl⟩
  rw [← Set.range_comp'] at himage
  change operator (castMatrix (transform c)) y∈convexHull ℝ (Set.range (initials z c)) at himage
  exact himage

theorem source_family_action (T : RealMatrix) (hT : IsUnit T.det)
    (F : ConvexMargin.Family (Fin na) n ℂ) (a : Fin na) (u : ℝ) (y : State ℂ) :
    operator T (PolynomialGram.operatorPolynomial (F a) u y) =
      PolynomialGram.operatorPolynomial ((transformFamily T F) a) u (operator T y) := by
  have he : operator T⁻¹ (operator T y)=y := (atlas T hT).symm_apply_apply y
  change operator T (PolynomialGram.operatorPolynomial (F a) u y) =
    PolynomialGram.operatorPolynomial (fun k => conjugate T (F a k)) u (operator T y)
  simp only [PolynomialGram.operatorPolynomial,sum_apply,smul_apply,map_sum,map_smul]
  apply Finset.sum_congr rfl
  intro k _
  apply congrArg (fun w : State ℂ => u^(k : ℕ) • w)
  change operator T (F a k y) = operator T (F a k (operator T⁻¹ (operator T y)))
  rw [he]

/-- Soundness applies to the original supplied-family hull in the returned actual atlas domain. -/
theorem source_hull_preserves (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c) (hm : OriginalMass G)
    (F : ConvexMargin.Family (Fin na) n ℂ) (hF : F∈convexHull ℝ (Set.range (sourceFamilies G)))
    (a : Fin na) (u : ℝ) (hu : u∈Set.Icc (-1 : ℝ) 1) (y : State ℂ)
    (hy : y∈(atlasCone (atlas (castMatrix (transform c)) (unit_castMatrix _ (valid_unit G z c h)))).carrier) :
    PolynomialGram.operatorPolynomial (F a) u y∈
      (atlasCone (atlas (castMatrix (transform c)) (unit_castMatrix _ (valid_unit G z c h)))).carrier := by
  have hFh := source_hull_mapped G z c h F hF
  have hf := ConvexMargin.hull_feasible (families G c) (fun _ _ => (margin c : ℝ))
    (valid_feasible G z c h hm) hFh
  change operator (castMatrix (transform c)) (PolynomialGram.operatorPolynomial (F a) u y)∈cone
  rw [source_family_action _ (unit_castMatrix _ (valid_unit G z c h))]
  apply preserves_of_normalized _ _ hy
  intro v hv
  have hs := (hf.1 a u hu).trans (sigma_le _ v hv)
  have hk : (0 : ℝ)<margin c := by exact_mod_cast h.2.1
  change ‖(PolynomialGram.operatorPolynomial ((transformFamily (castMatrix (transform c)) F) a) u (1,v)).2‖≤_
  change (margin c : ℝ)≤
    (PolynomialGram.operatorPolynomial ((transformFamily (castMatrix (transform c)) F) a) u (1,v)).1-
      ‖(PolynomialGram.operatorPolynomial ((transformFamily (castMatrix (transform c)) F) a) u (1,v)).2‖ at hs
  linarith

theorem source_hull_initial_domain (G : Fin nf → Fin na → Fin n → RationalTransform.RationalMatrix)
    (z : Fin ni → Fin 3 → ℚ) (c : Candidate nf na) (h : Valid G z c) (hz : ∀ j,z j 0=1)
    (y : State ℂ) (hy : y∈convexHull ℝ (Set.range (sourceInitials z))) :
    y∈(atlasCone (atlas (castMatrix (transform c)) (unit_castMatrix _ (valid_unit G z c h)))).base := by
  have hi := ConvexMargin.hull_initial (initials z c) (valid_initial G z c h hz)
    (source_initial_hull_mapped z c y hy)
  exact hi

end
end Komorebi.LSM.StrictRationalSearch
