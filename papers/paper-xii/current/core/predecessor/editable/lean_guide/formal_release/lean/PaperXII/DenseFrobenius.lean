import Mathlib.LinearAlgebra.Matrix.Charpoly.Coeff
import Mathlib.Topology.Algebra.Group.Matrix
import Mathlib.Topology.Algebra.ContinuousMonoidHom
import Mathlib.Topology.Separation.Hausdorff

/-! Dense Frobenius conjugacy classes determine the actual characteristic polynomial
of a continuous matrix representation. Coefficient continuity is proved from the
principal-minor formula; no topology on a polynomial space is assumed. -/
set_option autoImplicit false

namespace PaperXII.DenseFrobenius

open Matrix

variable {R X Γ Ω ι : Type*} [CommRing R] [TopologicalSpace R]
    [IsTopologicalRing R] [TopologicalSpace X] [Fintype ι] [DecidableEq ι]

/-- Every characteristic-polynomial coefficient is a continuous function of the matrix. -/
theorem continuous_charpoly_coeff {A : X → Matrix ι ι R} (hA : Continuous A) (k : ℕ) :
    Continuous (fun x ↦ (A x).charpoly.coeff k) := by
  classical
  cases subsingleton_or_nontrivial R with
  | inl hR =>
    exact continuous_of_const (fun _ _ ↦ Subsingleton.elim _ _)
  | inr hR =>
    by_cases hk : k ≤ Fintype.card ι
    · have hformula (x : X) :=
        Matrix.charpoly_coeff_eq_sum_minors (A x) (Fintype.card ι - k) (Nat.sub_le _ _)
      have hind : Fintype.card ι - (Fintype.card ι - k) = k := Nat.sub_sub_self hk
      simp only [hind] at hformula
      simp_rw [hformula]
      refine continuous_const.mul (continuous_finsetSum _ fun s _ ↦ ?_)
      exact (hA.matrix_submatrix Subtype.val Subtype.val).matrix_det
    · have hzero (x : X) : (A x).charpoly.coeff k = 0 :=
        Polynomial.coeff_eq_zero_of_natDegree_lt (by
          rw [Matrix.charpoly_natDegree_eq_dim]
          exact Nat.lt_of_not_ge hk)
      simp_rw [hzero]
      exact continuous_const

variable [Group Γ]

/-- The actual union of conjugacy classes of the declared good Frobenius elements. -/
def conjugacySaturation (frob : Ω → Γ) (good : Ω → Prop) : Set Γ :=
  {g | ∃ v, good v ∧ ∃ h, g = h * frob v * h⁻¹}

/-- Each good Frobenius lies in its conjugacy saturation. -/
theorem frobenius_mem_saturation (frob : Ω → Γ) (good : Ω → Prop)
    (v : Ω) (hv : good v) : frob v ∈ conjugacySaturation frob good := by
  exact ⟨v, hv, 1, by simp⟩

/-- Increasing the good set increases the union of Frobenius conjugacy classes. -/
theorem conjugacySaturation_mono (frob : Ω → Γ) {good₁ good₂ : Ω → Prop}
    (hgood : ∀ v, good₁ v → good₂ v) :
    conjugacySaturation frob good₁ ⊆ conjugacySaturation frob good₂ := by
  rintro g ⟨v, hv, h, heq⟩
  exact ⟨v, hgood v hv, h, heq⟩

variable [TopologicalSpace Γ]

omit [IsTopologicalRing R] in
/-- Actual conjugation in the source group leaves a representation's characteristic polynomial fixed. -/
theorem charpoly_conjugate (ρ : Γ →ₜ* GL ι R) (g h : Γ) :
    (ρ (h * g * h⁻¹)).val.charpoly = (ρ g).val.charpoly := by
  rw [map_mul, map_mul, map_inv]
  change ((ρ h).val * (ρ g).val * ((ρ h)⁻¹).val).charpoly = _
  simpa only [Matrix.coe_units_inv] using
    Matrix.charpoly_units_conj (ρ h) (ρ g).val

/-- Continuity of each polynomial coefficient follows from continuity of the actual representation. -/
theorem continuous_rep_charpoly_coeff (ρ : Γ →ₜ* GL ι R) (k : ℕ) :
    Continuous (fun g ↦ (ρ g).val.charpoly.coeff k) :=
  continuous_charpoly_coeff (Units.continuous_val.comp ρ.continuous) k

omit [IsTopologicalRing R] in
/-- Equality on good Frobenius elements gives equality on their entire conjugacy saturation. -/
theorem charpoly_eq_on_saturation (ρ σ : Γ →ₜ* GL ι R)
    (frob : Ω → Γ) (good : Ω → Prop)
    (hpoly : ∀ v, good v → (ρ (frob v)).val.charpoly = (σ (frob v)).val.charpoly) :
    Set.EqOn (fun g ↦ (ρ g).val.charpoly) (fun g ↦ (σ g).val.charpoly)
      (conjugacySaturation frob good) := by
  rintro g ⟨v, hv, h, rfl⟩
  dsimp only
  rw [charpoly_conjugate, charpoly_conjugate, hpoly v hv]

/-- A dense set of good Frobenius conjugacy classes determines every characteristic polynomial. -/
theorem charpoly_eq_of_dense_frobenius [T2Space R] (ρ σ : Γ →ₜ* GL ι R)
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good))
    (hpoly : ∀ v, good v → (ρ (frob v)).val.charpoly = (σ (frob v)).val.charpoly) :
    ∀ g, (ρ g).val.charpoly = (σ g).val.charpoly := by
  intro g
  apply Polynomial.ext
  intro k
  have hcoeff := Continuous.ext_on hdense
    (continuous_rep_charpoly_coeff ρ k) (continuous_rep_charpoly_coeff σ k)
    (fun x hx ↦ congrArg (fun P : Polynomial R ↦ P.coeff k)
      (charpoly_eq_on_saturation ρ σ frob good hpoly hx))
  exact congrFun hcoeff g

/-- Matching a common coefficient-field polynomial spine implies equality everywhere.
The ring homomorphism need not be continuous: the mapped polynomials are fixed values. -/
theorem common_spine_charpoly_eq [T2Space R] {L : Type*} [CommRing L]
    (ρ σ : Γ →ₜ* GL ι R) (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good))
    (emb : L →+* R) (P : Ω → Polynomial L)
    (hρ : ∀ v, good v → (ρ (frob v)).val.charpoly = (P v).map emb)
    (hσ : ∀ v, good v → (σ (frob v)).val.charpoly = (P v).map emb) :
    ∀ g, (ρ g).val.charpoly = (σ g).val.charpoly :=
  charpoly_eq_of_dense_frobenius ρ σ frob good hdense
    (fun v hv ↦ (hρ v hv).trans (hσ v hv).symm)

end PaperXII.DenseFrobenius
