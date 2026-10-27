import PaperX.RepresentationLimits

/-! Actual matrix representations modulo change of basis.  The equivalence
relation uses invertible matrices, and coefficient maps reduce those matrices.
Finite coefficients give finite individual conjugacy classes even when the
source group is infinite. -/
set_option autoImplicit false
namespace PaperX.RepresentationClasses
open PaperX.RepresentationLimits
variable {R : Type*} [CommRing R] {G : Type*} [Group G]
  {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- Conjugation by an actual invertible matrix. -/
def conjugate (u : (Matrix ι ι R)ˣ) (ρ : MatrixRep R G ι) : MatrixRep R G ι where
  toFun g := (u : Matrix ι ι R) * ρ g * (↑(u⁻¹) : Matrix ι ι R)
  map_one' := by simp
  map_mul' g h := by simp [map_mul, mul_assoc]

@[simp] theorem conjugate_apply (u : (Matrix ι ι R)ˣ)
    (ρ : MatrixRep R G ι) (g : G) :
    conjugate u ρ g = (u : Matrix ι ι R) * ρ g * (↑(u⁻¹) : Matrix ι ι R) := rfl

@[simp] theorem conjugate_one (ρ : MatrixRep R G ι) : conjugate 1 ρ = ρ := by
  apply MonoidHom.ext
  intro g
  simp [conjugate]

@[simp] theorem conjugate_mul (u v : (Matrix ι ι R)ˣ)
    (ρ : MatrixRep R G ι) : conjugate (u * v) ρ = conjugate u (conjugate v ρ) := by
  apply MonoidHom.ext
  intro g
  simp [conjugate, mul_assoc]

/-- Equality after a single invertible change of basis. -/
def Conjugate (ρ σ : MatrixRep R G ι) : Prop :=
  ∃ u : (Matrix ι ι R)ˣ, conjugate u ρ = σ

theorem conjugate_refl (ρ : MatrixRep R G ι) : Conjugate ρ ρ :=
  ⟨1, conjugate_one ρ⟩

theorem conjugate_symm {ρ σ : MatrixRep R G ι} (h : Conjugate ρ σ) : Conjugate σ ρ := by
  obtain ⟨u, rfl⟩ := h
  exact ⟨u⁻¹, by rw [← conjugate_mul]; simp⟩

theorem conjugate_trans {ρ σ τ : MatrixRep R G ι}
    (h : Conjugate ρ σ) (k : Conjugate σ τ) : Conjugate ρ τ := by
  obtain ⟨u, rfl⟩ := h
  obtain ⟨v, rfl⟩ := k
  exact ⟨v * u, conjugate_mul v u ρ⟩

def conjugacySetoid (R : Type*) [CommRing R] (G : Type*) [Group G]
    (ι : Type*) [Fintype ι] [DecidableEq ι] : Setoid (MatrixRep R G ι) where
  r := Conjugate
  iseqv := ⟨conjugate_refl, conjugate_symm, conjugate_trans⟩

/-- Isomorphism classes of finite free matrix representations. -/
def ClassRep (R : Type*) [CommRing R] (G : Type*) [Group G]
    (ι : Type*) [Fintype ι] [DecidableEq ι] := Quotient (conjugacySetoid R G ι)

def classOf (ρ : MatrixRep R G ι) : ClassRep R G ι := Quotient.mk _ ρ

@[simp] theorem classOf_eq {ρ σ : MatrixRep R G ι} :
    classOf ρ = classOf σ ↔ Conjugate ρ σ := Quotient.eq

theorem classOf_surjective : Function.Surjective (classOf (R := R) (G := G) (ι := ι)) :=
  Quotient.mk_surjective

/-- A change of coefficients reduces the actual basis matrix. -/
theorem changeCoefficients_conjugate {S : Type*} [CommRing S] (f : R →+* S)
    (u : (Matrix ι ι R)ˣ) (ρ : MatrixRep R G ι) :
    changeCoefficients f (conjugate u ρ) =
      conjugate (Units.map f.mapMatrix.toMonoidHom u) (changeCoefficients f ρ) := by
  apply MonoidHom.ext
  intro g
  change f.mapMatrix ((u : Matrix ι ι R) * ρ g * (↑(u⁻¹) : Matrix ι ι R)) = _
  simp only [map_mul]
  rfl

theorem changeCoefficients_conjugacy {S : Type*} [CommRing S] (f : R →+* S)
    {ρ σ : MatrixRep R G ι} (h : Conjugate ρ σ) :
    Conjugate (changeCoefficients f ρ) (changeCoefficients f σ) := by
  obtain ⟨u, hu⟩ := h
  refine ⟨Units.map f.mapMatrix.toMonoidHom u, ?_⟩
  rw [← changeCoefficients_conjugate, hu]

def changeClassCoefficients {S : Type*} [CommRing S] (f : R →+* S) :
    ClassRep R G ι → ClassRep S G ι :=
  Quotient.map (changeCoefficients f) (fun _ _ h => changeCoefficients_conjugacy f h)

@[simp] theorem changeClassCoefficients_classOf {S : Type*} [CommRing S]
    (f : R →+* S) (ρ : MatrixRep R G ι) :
    changeClassCoefficients f (classOf ρ) = classOf (changeCoefficients f ρ) := rfl

variable (I : Ideal R)

def reduceClass (c : ClassRep R G ι) (k : ℕ) : ClassRep (R ⧸ I ^ k) G ι :=
  changeClassCoefficients (Ideal.Quotient.mk (I ^ k)) c

def transitionClass {j k : ℕ} (h : j ≤ k) :
    ClassRep (R ⧸ I ^ k) G ι → ClassRep (R ⧸ I ^ j) G ι :=
  changeClassCoefficients (Ideal.Quotient.factorPow I h)

@[simp] theorem reduceClass_classOf (ρ : MatrixRep R G ι) (k : ℕ) :
    reduceClass I (classOf ρ) k = classOf (reduce I ρ k) := rfl

@[simp] theorem transitionClass_classOf {j k : ℕ} (h : j ≤ k)
    (ρ : MatrixRep (R ⧸ I ^ k) G ι) :
    transitionClass I h (classOf ρ) = classOf (transition I h ρ) := rfl

@[simp] theorem transitionClass_reduceClass (c : ClassRep R G ι)
    {j k : ℕ} (h : j ≤ k) : transitionClass I h (reduceClass I c k) = reduceClass I c j := by
  obtain ⟨ρ, rfl⟩ := classOf_surjective c
  simp

@[simp] theorem transitionClass_self {k : ℕ} (c : ClassRep (R ⧸ I ^ k) G ι) :
    transitionClass I (Nat.le_refl k) c = c := by
  obtain ⟨ρ, rfl⟩ := classOf_surjective c
  simp

/-- Individual classes are finite over a finite coefficient ring.  No finiteness
or finite generation of the source group is needed. -/
theorem finite_class_fiber [Finite R] (c : ClassRep R G ι) :
    Finite {ρ : MatrixRep R G ι // classOf ρ = c} := by
  obtain ⟨σ, rfl⟩ := classOf_surjective c
  let F : (Matrix ι ι R)ˣ → {ρ : MatrixRep R G ι // classOf ρ = classOf σ} :=
    fun u => ⟨conjugate u σ, classOf_eq.mpr (conjugate_symm ⟨u, rfl⟩)⟩
  apply Finite.of_surjective F
  intro ρ
  obtain ⟨u, hu⟩ := conjugate_symm (classOf_eq.mp ρ.property)
  exact ⟨u, Subtype.ext hu⟩

end PaperX.RepresentationClasses
