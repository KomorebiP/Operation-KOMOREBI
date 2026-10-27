import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Projective
import Mathlib.Analysis.Complex.Polynomial.Basic
import Mathlib.GroupTheory.SpecificGroups.Cyclic

/-! A genuine projective representation of a finite cyclic group lifts to GL.
The projective representation is an actual homomorphism to Mathlib's PGL,
and equality after projection is the conclusion, not a hypothesis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicLinearization
open scoped MatrixGroups

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- Every nonzero complex scalar has a nonzero root of any positive order. -/
theorem unit_root (a : ℂˣ) {m : ℕ} (hm : 0 < m) :
    ∃ u : ℂˣ, u ^ m = a := by
  obtain ⟨z, hz⟩ := IsAlgClosed.exists_pow_nat_eq (a : ℂ) hm
  have hne : z ≠ 0 := by
    intro h
    rw [h, zero_pow (Nat.ne_of_gt hm)] at hz
    exact a.ne_zero hz.symm
  refine ⟨Units.mk0 z hne, ?_⟩
  apply Units.ext
  exact hz

/-- A GL lift of a finite-order projective element can be rescaled to have
that finite order relation itself. -/
theorem rescale_generator (T : GL ι ℂ) {m : ℕ} (hm : 0 < m)
    (hT : Matrix.ProjGenLinGroup.mk T ^ m = 1) :
    ∃ S : GL ι ℂ, S ^ m = 1 ∧
      Matrix.ProjGenLinGroup.mk S = Matrix.ProjGenLinGroup.mk T := by
  have hc : T ^ m ∈ Subgroup.center (GL ι ℂ) := by
    apply Matrix.ProjGenLinGroup.mk_eq_one.mp
    simpa only [map_pow] using hT
  rw [Matrix.GeneralLinearGroup.center_eq_range_scalar] at hc
  obtain ⟨a, ha⟩ := hc
  obtain ⟨u, hu⟩ := unit_root a⁻¹ hm
  refine ⟨Matrix.GeneralLinearGroup.scalar ι u * T, ?_, ?_⟩
  · have hcomm : Commute (Matrix.GeneralLinearGroup.scalar ι u) T :=
      Matrix.GeneralLinearGroup.scalar_commute u T
    rw [hcomm.mul_pow, ← map_pow, hu, ← ha, ← map_mul]
    simp
  · simp

variable {G : Type*} [Group G]

/-- A projective cyclic action lifts, using any explicitly supplied generator
of finite positive order. -/
theorem lift_of_generator (π : G →* PGL(ι, ℂ)) (g : G)
    (hg : ∀ x, x ∈ Subgroup.zpowers g) (hm : 0 < orderOf g) :
    ∃ ρ : G →* GL ι ℂ, Matrix.ProjGenLinGroup.mk.comp ρ = π := by
  obtain ⟨T, hT⟩ := Matrix.ProjGenLinGroup.mk_surjective (π g)
  have hp : Matrix.ProjGenLinGroup.mk T ^ orderOf g = 1 := by
    rw [hT, ← map_pow, pow_orderOf_eq_one, map_one]
  obtain ⟨S, hS, hproj⟩ := rescale_generator T hm hp
  let ρ : G →* GL ι ℂ := monoidHomOfForallMemZpowers hg
    (orderOf_dvd_of_pow_eq_one hS)
  refine ⟨ρ, (MonoidHom.eq_iff_eq_on_generator hg _ _).mpr ?_⟩
  change Matrix.ProjGenLinGroup.mk (ρ g) = π g
  rw [monoidHomOfForallMemZpowers_apply_gen, hproj, hT]

/-- Paper XI Lemma 11.4: every projective representation of a finite cyclic
group over the complex numbers is the projectivization of an honest action. -/
theorem finite_cyclic_linearization [Finite G] [IsCyclic G]
    (π : G →* PGL(ι, ℂ)) :
    ∃ ρ : G →* GL ι ℂ, Matrix.ProjGenLinGroup.mk.comp ρ = π := by
  obtain ⟨g, hg⟩ := IsCyclic.exists_generator (α := G)
  exact lift_of_generator π g hg (orderOf_pos g)

/-- Pointwise projective equality gives actual invertible scalar changes of
any chosen lifts of the input projective action. -/
theorem finite_cyclic_scalar_equivalence [Finite G] [IsCyclic G]
    (π : G →* PGL(ι, ℂ)) (T : G → GL ι ℂ)
    (hT : ∀ g, Matrix.ProjGenLinGroup.mk (T g) = π g) :
    ∃ ρ : G →* GL ι ℂ, ∀ g, ∃ u : ℂˣ,
      T g * Matrix.GeneralLinearGroup.scalar ι u = ρ g := by
  obtain ⟨ρ, hρ⟩ := finite_cyclic_linearization π
  refine ⟨ρ, fun g => Matrix.ProjGenLinGroup.mk_eq_mk_iff.mp ?_⟩
  rw [hT g]
  exact (DFunLike.congr_fun hρ g).symm

end PaperXI.CyclicLinearization
