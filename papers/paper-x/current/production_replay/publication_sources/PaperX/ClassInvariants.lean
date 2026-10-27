import PaperX.RepresentationClasses
import PaperX.RepresentationTopology

/-! Characteristic polynomials, trivial subgroup actions and actual finite-level
continuity are invariant under the matrix conjugacy used in representation
classes.  In particular one continuous representative suffices for every frame. -/
set_option autoImplicit false
namespace PaperX.ClassInvariants
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.RepresentationTopology
open scoped Topology
variable {R : Type*} [CommRing R] {G : Type*} [Group G]
  {ι : Type*} [Fintype ι] [DecidableEq ι]

@[simp] theorem charpoly_conjugate (u : (Matrix ι ι R)ˣ)
    (ρ : MatrixRep R G ι) (g : G) : (conjugate u ρ g).charpoly = (ρ g).charpoly := by
  change ((u : Matrix ι ι R) * ρ g * (↑(u⁻¹) : Matrix ι ι R)).charpoly = _
  rw [Matrix.charpoly_mul_comm, ← mul_assoc]
  simp

@[simp] theorem det_conjugate (u : (Matrix ι ι R)ˣ)
    (ρ : MatrixRep R G ι) (g : G) : (conjugate u ρ g).det = (ρ g).det := by
  change ((u : Matrix ι ι R) * ρ g * (↑(u⁻¹) : Matrix ι ι R)).det = _
  exact Matrix.det_units_conj u (ρ g)

theorem charpoly_conjugacy {ρ σ : MatrixRep R G ι} (h : Conjugate ρ σ) (g : G) :
    (ρ g).charpoly = (σ g).charpoly := by
  obtain ⟨u, hu⟩ := h
  rw [← hu, charpoly_conjugate]

/-- The characteristic polynomial of the actual conjugacy class. -/
noncomputable def classCharpoly (c : ClassRep R G ι) (g : G) : Polynomial R :=
  Quotient.lift (fun ρ : MatrixRep R G ι => (ρ g).charpoly)
    (fun _ _ h => charpoly_conjugacy h g) c

@[simp] theorem classCharpoly_classOf (ρ : MatrixRep R G ι) (g : G) :
    classCharpoly (classOf ρ) g = (ρ g).charpoly := rfl

theorem classCharpoly_changeCoefficients {S : Type*} [CommRing S] (f : R →+* S)
    (c : ClassRep R G ι) (g : G) :
    classCharpoly (changeClassCoefficients f c) g = (classCharpoly c g).map f := by
  obtain ⟨ρ, rfl⟩ := classOf_surjective c
  change (Matrix.map (ρ g) f).charpoly = (ρ g).charpoly.map f
  exact Matrix.charpoly_map _ _

/-- Triviality on a specified subgroup is unchanged by change of basis. -/
theorem trivial_conjugacy {ρ σ : MatrixRep R G ι} (h : Conjugate ρ σ) (H : Subgroup G) :
    (∀ g, g ∈ H → ρ g = 1) ↔ (∀ g, g ∈ H → σ g = 1) := by
  have forward : ∀ {τ υ : MatrixRep R G ι}, Conjugate τ υ →
      (∀ g, g ∈ H → τ g = 1) → (∀ g, g ∈ H → υ g = 1) := by
    intro τ υ ht hu g hg
    obtain ⟨u, he⟩ := ht
    rw [← he, conjugate_apply, hu g hg]
    simp
  exact ⟨forward h, forward (conjugate_symm h)⟩

def ClassTrivial (H : Subgroup G) (c : ClassRep R G ι) : Prop :=
  Quotient.lift (fun ρ : MatrixRep R G ι => ∀ g, g ∈ H → ρ g = 1)
    (fun _ _ h => propext (trivial_conjugacy h H)) c

@[simp] theorem classTrivial_classOf (H : Subgroup G) (ρ : MatrixRep R G ι) :
    ClassTrivial H (classOf ρ) ↔ ∀ g, g ∈ H → ρ g = 1 := Iff.rfl

variable [TopologicalSpace G]

/-- A finite family of locally constant entries is locally constant as a matrix. -/
theorem finiteRepContinuous_matrix (ρ : MatrixRep R G ι) (h : FiniteRepContinuous ρ) :
    FiniteContinuous ρ := by
  intro x
  have he : ∀ᶠ y in 𝓝 x, ∀ i j, ρ y i j = ρ x i j :=
    Filter.eventually_all.mpr (fun i => Filter.eventually_all.mpr (fun j => h i j x))
  exact he.mono (fun _ hy => funext (fun i => funext (hy i)))

theorem finiteRepContinuous_conjugate (u : (Matrix ι ι R)ˣ)
    {ρ : MatrixRep R G ι} (h : FiniteRepContinuous ρ) :
    FiniteRepContinuous (conjugate u ρ) := by
  intro i j x
  filter_upwards [finiteRepContinuous_matrix ρ h x] with y hy
  simp only [conjugate_apply, hy]

theorem finiteRepContinuous_conjugacy {ρ σ : MatrixRep R G ι} (h : Conjugate ρ σ) :
    FiniteRepContinuous ρ ↔ FiniteRepContinuous σ := by
  have forward : ∀ {τ υ : MatrixRep R G ι}, Conjugate τ υ →
      FiniteRepContinuous τ → FiniteRepContinuous υ := by
    intro τ υ ht hc
    obtain ⟨u, he⟩ := ht
    rw [← he]
    exact finiteRepContinuous_conjugate u hc
  exact ⟨forward h, forward (conjugate_symm h)⟩

theorem finiteContinuous_of_classOf_eq {ρ σ : MatrixRep R G ι}
    (h : classOf ρ = classOf σ) (hc : FiniteRepContinuous σ) : FiniteRepContinuous ρ :=
  (finiteRepContinuous_conjugacy (classOf_eq.mp h)).mpr hc

/-- Actual continuity of a class is independent of its chosen matrix frame. -/
def ClassContinuous (c : ClassRep R G ι) : Prop :=
  Quotient.lift (fun ρ : MatrixRep R G ι => FiniteRepContinuous ρ)
    (fun _ _ h => propext (finiteRepContinuous_conjugacy h)) c

@[simp] theorem classContinuous_classOf (ρ : MatrixRep R G ι) :
    ClassContinuous (classOf ρ) ↔ FiniteRepContinuous ρ := Iff.rfl

end PaperX.ClassInvariants
