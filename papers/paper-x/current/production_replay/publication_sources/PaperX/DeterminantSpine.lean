import PaperX.ClassCompletion
import PaperX.ClassInvariants
import PaperX.CommonSpine

/-! The determinant part of a prescribed common spine is an actual invariant
of matrix representation classes. Equality at every coefficient precision
recovers its integral value; coefficient change then recovers a separately
specified common value in the local coefficient field. No arithmetic
interpretation of the other local packet entries is asserted here. -/
set_option autoImplicit false
namespace PaperX.DeterminantSpine
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.ClassCompletion PaperX.ClassInvariants

variable {R : Type*} [CommRing R] {G : Type*} [Group G]
  {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- The actual determinant character, including multiplicativity. -/
def determinantCharacter (ρ : MatrixRep R G ι) : G →* R :=
  Matrix.detMonoidHom.comp ρ

@[simp] theorem determinantCharacter_apply (ρ : MatrixRep R G ι) (g : G) :
    determinantCharacter ρ g = (ρ g).det := rfl

theorem determinant_conjugacy {ρ σ : MatrixRep R G ι}
    (h : Conjugate ρ σ) (g : G) : (ρ g).det = (σ g).det := by
  obtain ⟨u, hu⟩ := h
  rw [← hu, det_conjugate]

/-- Determinant evaluated on the actual quotient by matrix conjugacy. -/
noncomputable def classDet (c : ClassRep R G ι) (g : G) : R :=
  Quotient.lift (fun ρ : MatrixRep R G ι => (ρ g).det)
    (fun _ _ h => determinant_conjugacy h g) c

@[simp] theorem classDet_classOf (ρ : MatrixRep R G ι) (g : G) :
    classDet (classOf ρ) g = (ρ g).det := rfl

theorem determinant_changeCoefficients {S : Type*} [CommRing S]
    (f : R →+* S) (ρ : MatrixRep R G ι) (g : G) :
    (changeCoefficients f ρ g).det = f ((ρ g).det) := by
  exact (f.map_det (ρ g)).symm

theorem classDet_changeCoefficients {S : Type*} [CommRing S]
    (f : R →+* S) (c : ClassRep R G ι) (g : G) :
    classDet (changeClassCoefficients f c) g = f (classDet c g) := by
  obtain ⟨ρ, rfl⟩ := classOf_surjective c
  exact determinant_changeCoefficients f ρ g

/-- Separatedness suffices to recover the entire prescribed determinant. -/
theorem determinant_detected (I : Ideal R) [IsHausdorff I R]
    (ρ : MatrixRep R G ι) (g : G) (d : R)
    (h : ∀ k, (reduce I ρ k g).det = Ideal.Quotient.mk (I^k) d) :
    (ρ g).det = d := by
  apply scalar_ext I
  intro k
  exact (determinant_changeCoefficients (Ideal.Quotient.mk (I^k)) ρ g).symm.trans (h k)

/-- Prescribing determinant values on every allowed conjugacy class makes
those values hold for every integral realization of those classes. -/
theorem class_realization_has_determinant {R G ι : Type}
    [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
    (I : Ideal R) [IsHausdorff I R]
    (C : ClassConditions (G := G) (ι := ι) I)
    (ρ : MatrixRep R G ι)
    (hρ : ∀ k, C.allowed k (classOf (reduce I ρ k)))
    (δ : G → R)
    (spec : ∀ k c, C.allowed k c → ∀ g,
      classDet c g = Ideal.Quotient.mk (I^k) (δ g)) :
    ∀ g, (ρ g).det = δ g := by
  intro g
  apply determinant_detected I ρ g (δ g)
  intro k
  exact spec k _ (hρ k) g

/-- Local integral and common coefficient values are compared only after
embedding both into the local coefficient ring. -/
theorem determinant_base_change {K E : Type*} [CommRing K] [CommRing E]
    (inc : R →+* K) (emb : E →+* K) (ρ : MatrixRep R G ι) (g : G)
    (localδ : R) (commonδ : E)
    (hlocal : (ρ g).det = localδ) (hcommon : inc localδ = emb commonδ) :
    (changeCoefficients inc ρ g).det = emb commonδ := by
  rw [determinant_changeCoefficients, hlocal, hcommon]

/-- The determinant entry of a common spine follows from its finite class
specification and its integral coefficient comparison. -/
theorem class_realization_has_common_determinant {R G ι K E : Type}
    [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
    [CommRing K] [CommRing E]
    (I : Ideal R) [IsHausdorff I R]
    (C : ClassConditions (G := G) (ι := ι) I)
    (ρ : MatrixRep R G ι)
    (hρ : ∀ k, C.allowed k (classOf (reduce I ρ k)))
    (inc : R →+* K) (emb : E →+* K)
    (localδ : G → R) (commonδ : G → E)
    (integrality : ∀ g, inc (localδ g) = emb (commonδ g))
    (spec : ∀ k c, C.allowed k c → ∀ g,
      classDet c g = Ideal.Quotient.mk (I^k) (localδ g)) :
    ∀ g, (changeCoefficients inc ρ g).det = emb (commonδ g) := by
  intro g
  exact determinant_base_change inc emb ρ g (localδ g) (commonδ g)
    (class_realization_has_determinant I C ρ hρ localδ spec g) (integrality g)

end PaperX.DeterminantSpine
