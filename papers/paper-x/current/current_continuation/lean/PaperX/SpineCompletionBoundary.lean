import PaperX.InverseLimitLocalConditions
import PaperX.ClassBranchLifting

/-!
The closure and occupancy premises do different work.  Allowing every finite
class does not force an arbitrary integral property, whereas an empty tower
satisfies every closure statement vacuously and has no realization.  These
boundary statements use actual representation classes and compatible families.
-/
set_option autoImplicit false

namespace PaperX.SpineCompletionBoundary
open PaperX.RepresentationLimits PaperX.RepresentationClasses PaperX.ClassCompletion
open PaperX.InverseLimitLocalConditions PaperX.Compactness PaperX.ClassBranchLifting

variable {R G ι : Type} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
variable (I : Ideal R)

/-- Every actual representation class is allowed. -/
def allClasses : ClassConditions (G := G) (ι := ι) I where
  allowed _ _ := True
  downward _ _ _ := True.intro

/-- No actual representation class is allowed. -/
def emptyClasses : ClassConditions (G := G) (ι := ι) I where
  allowed _ _ := False
  downward _ _ h := h

/-- The constant identity action is an actual integral representation. -/
def trivialRepresentation : MatrixRep R G ι where
  toFun _ := 1
  map_one' := rfl
  map_mul' _ _ := (one_mul 1).symm

/-- All precisions of the unrestricted class condition are occupied. -/
theorem allClasses_occupied (k : ℕ) :
    ∃ c, (allClasses (G := G) (ι := ι) I).allowed k c :=
  ⟨classOf (reduce I (trivialRepresentation (R := R) (G := G) (ι := ι)) k),
    True.intro⟩

/-- For a finite source group and finite quotient coefficients, unrestricted
levels also satisfy the finiteness premise. -/
theorem allClasses_finite (k : ℕ) [Finite G] [Finite (R ⧸ I^k)] :
    Finite {c // (allClasses (G := G) (ι := ι) I).allowed k c} := by
  let : Finite (MatrixRep (R ⧸ I^k) G ι) :=
    Finite.of_injective DFunLike.coe DFunLike.coe_injective
  let : Finite (ClassRep (R ⧸ I^k) G ι) :=
    Finite.of_surjective classOf classOf_surjective
  infer_instance

/-- Even an actual compatible family in occupied levels need not satisfy an
arbitrarily prescribed local relation. -/
theorem compatible_family_fails_false [IsAdicComplete I R] :
    ∃ f : Family R I G ι,
      (∀ k, (allClasses I).allowed k (classOf (f.maps k))) ∧
      ¬ (fun _ : MatrixRep R G ι => False) (reconstruct I f) :=
  ⟨reduceFamily I trivialRepresentation, (fun _ => True.intro), not_false⟩

/-- Inverse-limit closure cannot be omitted just because every class is allowed
and every precision is occupied. -/
theorem allClasses_not_closed_false [IsAdicComplete I R] :
    ¬ InverseLimitClosed I (allClasses (G := G) (ι := ι) I) (fun _ => False) := by
  intro h
  obtain ⟨f, hf, hfalse⟩ := compatible_family_fails_false (G := G) (ι := ι) I
  exact hfalse (h f hf)

/-- No universally valid rule can infer all local relations from admissible
finite classes alone. -/
theorem not_all_local_relations_follow [IsAdicComplete I R] :
    ¬ (∀ P : MatrixRep R G ι → Prop,
      ∀ f : Family R I G ι,
        (∀ k, (allClasses I).allowed k (classOf (f.maps k))) → P (reconstruct I f)) := by
  intro h
  exact allClasses_not_closed_false (G := G) (ι := ι) I (h (fun _ => False))

/-- Every local relation is inverse-limit closed for the empty allowed tower,
because there is no compatible allowed family. -/
theorem emptyClasses_closed [IsAdicComplete I R] (P : MatrixRep R G ι → Prop) :
    InverseLimitClosed I (emptyClasses I) P := by
  intro f hf
  exact False.elim (hf 1)

/-- The empty allowed tower has no occupied level, at any precision. -/
theorem emptyClasses_unoccupied (k : ℕ) :
    ¬ ∃ c, (emptyClasses (G := G) (ι := ι) I).allowed k c := by
  rintro ⟨c, hc⟩
  exact hc

/-- In particular, the empty tower has no integral realization. -/
theorem emptyClasses_no_realization :
    ¬ ∃ ρ : MatrixRep R G ι,
      ∀ k, (emptyClasses I).allowed k (classOf (reduce I ρ k)) := by
  rintro ⟨ρ, hρ⟩
  exact hρ 1

/-- Closure alone supplies no finite-level occupancy. -/
theorem closure_without_occupancy [IsAdicComplete I R] :
    (∀ P : MatrixRep R G ι → Prop, InverseLimitClosed I (emptyClasses I) P) ∧
      ¬ ∃ c, (emptyClasses (G := G) (ι := ι) I).allowed 1 c :=
  ⟨emptyClasses_closed I, emptyClasses_unoccupied I 1⟩

/-- An integral representation gives an actual compatible branch of conjugacy
classes; this construction requires no compactness or choice of frames. -/
def classBranchOfRepresentation (ρ : MatrixRep R G ι) :
    Branch (classTower (G := G) (ι := ι) I) where
  value k := classOf (reduce I ρ k)
  compatible k := by
    change transitionClass I (Nat.le_succ k) (classOf (reduce I ρ (k + 1))) = _
    rw [transitionClass_classOf, transition_reduce]

/-- Every pair of precisions in this branch has the required reduction, not
only consecutive levels. -/
theorem classBranchOfRepresentation_compatible (ρ : MatrixRep R G ι)
    {j k : ℕ} (h : j ≤ k) :
    transitionClass I h ((classBranchOfRepresentation I ρ).value k) =
      (classBranchOfRepresentation I ρ).value j := by
  change transitionClass I h (classOf (reduce I ρ k)) = classOf (reduce I ρ j)
  rw [transitionClass_classOf, transition_reduce]

/-- An integral realization therefore provides a compatible branch in precisely
the supplied admissible classes. -/
theorem classBranchOfRepresentation_allowed
    (C : ClassConditions (G := G) (ι := ι) I) (ρ : MatrixRep R G ι)
    (hρ : ∀ k, C.allowed k (classOf (reduce I ρ k))) :
    ∀ k, C.allowed k ((classBranchOfRepresentation I ρ).value k) := hρ

end PaperX.SpineCompletionBoundary
