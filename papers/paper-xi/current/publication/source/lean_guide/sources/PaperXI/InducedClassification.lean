import PaperXI.InducedDual
import PaperXI.CyclicInducedWrap

/-! Classification uses the full subgroup characters, including return values.
No assertion identifies an abstract degree subgroup with a local Weil group. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InducedClassification
open PaperXI.CyclicInduced PaperXI.InducedDual
open scoped Classical
variable {G Q : Type*} [Group G] [Group Q] [Fintype Q]
variable (d : G →* Q) (r : Q → G) (hr : ∀ q, d (r q) = q⁻¹)

omit [Fintype Q] in
include hr in
theorem index_transitive (j k : Q) : ∃ g : G, indexAction d g j = k := by
  refine ⟨(r (k * j⁻¹))⁻¹, ?_⟩
  change d ((r (k * j⁻¹))⁻¹) * j = k
  simp [hr, mul_assoc]

omit [Fintype Q] in
theorem index_stabilizer (j : Q) (g : G) : g ∈ d.ker ↔ indexAction d g j = j := by
  change d g = 1 ↔ d g * j = j
  constructor
  · intro h; simp [h]
  · intro h; exact mul_right_cancel (h.trans (one_mul j).symm)

/-- Changing the distinguished coset line gives actual induction of its conjugate character. -/
def conjugateEquiv (ψ : d.ker →* ℂˣ) (j : Q) :
    Representation.Equiv (induced d (conjugateCharacter d r ψ j)) (induced d ψ) :=
  MonomialInduction.transitiveEquivalenceOfSubgroupAction
    (induced d ψ) (basis d r hr ψ) (indexAction d) (weight d r hr ψ)
    (fun g k => basis_action d r hr ψ g k) j
    (index_transitive d r hr j) d.ker (conjugateCharacter d r ψ j)
    (index_stabilizer d j) (fun h => basis_action_kernel d r hr ψ h j)

/-- Coefficients of a subgroup action are its actual diagonal characters. -/
theorem coefficient_action (ψ : d.ker →* ℂˣ) (h : d.ker) (j : Q) (v : IndSpace d ψ) :
    (basis d r hr ψ).repr (induced d ψ h v) j =
      (conjugateCharacter d r ψ j h : ℂ) * (basis d r hr ψ).repr v j := by
  have he : ((basis d r hr ψ).coord j).comp (induced d ψ h) =
      (conjugateCharacter d r ψ j h : ℂ) • (basis d r hr ψ).coord j := by
    apply (basis d r hr ψ).ext
    intro k
    change (basis d r hr ψ).repr (induced d ψ h (basis d r hr ψ k)) j =
      (conjugateCharacter d r ψ j h : ℂ) * (basis d r hr ψ).repr (basis d r hr ψ k) j
    rw [basis_action_kernel]
    by_cases hk : k = j
    · subst k
      simp
    · simp [hk]
  exact LinearMap.congr_fun he v

include hr in
/-- A nonzero coefficient of the image of the original character line detects a conjugate. -/
theorem character_of_equiv (hr1 : r 1 = 1) (χ ψ : d.ker →* ℂˣ)
    (e : Representation.Equiv (induced d χ) (induced d ψ)) :
    ∃ j : Q, χ = conjugateCharacter d r ψ j := by
  have hv : e (basis d r hr χ 1) ≠ 0 := by
    intro h
    exact (basis d r hr χ).ne_zero 1 (e.injective (h.trans e.map_zero.symm))
  obtain ⟨j, hj⟩ : ∃ j : Q, (basis d r hr ψ).repr (e (basis d r hr χ 1)) j ≠ 0 := by
    by_contra hn
    simp only [not_exists, not_not] at hn
    apply hv
    apply (basis d r hr ψ).repr.injective
    ext j
    simpa using hn j
  refine ⟨j, ?_⟩
  apply MonoidHom.ext
  intro h
  apply Units.ext
  have he := LinearMap.congr_fun (e.isIntertwining' (h : G)) (basis d r hr χ 1)
  change e (induced d χ h (basis d r hr χ 1)) =
    induced d ψ h (e (basis d r hr χ 1)) at he
  rw [basis_action_origin d r hr χ hr1, map_smul] at he
  have hc := congrArg (fun v => (basis d r hr ψ).repr v j) he
  rw [coefficient_action d r hr ψ] at hc
  simp only [map_smul, Finsupp.smul_apply, smul_eq_mul] at hc
  exact mul_right_cancel₀ hj hc

include hr in
/-- Equality of induction classes is exactly conjugacy of full inducing characters. -/
theorem equiv_iff (hr1 : r 1 = 1) (χ ψ : d.ker →* ℂˣ) :
    Nonempty (Representation.Equiv (induced d χ) (induced d ψ)) ↔
      ∃ j : Q, χ = conjugateCharacter d r ψ j := by
  constructor
  · rintro ⟨e⟩; exact character_of_equiv d r hr hr1 χ ψ e
  · rintro ⟨j, rfl⟩; exact ⟨conjugateEquiv d r hr ψ j⟩

include hr in
/-- Dual induction together with classification gives the full self-duality criterion. -/
theorem selfDual_iff (hr1 : r 1 = 1) (χ : d.ker →* ℂˣ) :
    Nonempty (Representation.Equiv (induced d χ).dual (induced d χ)) ↔
      ∃ j : Q, χ⁻¹ = conjugateCharacter d r χ j := by
  constructor
  · rintro ⟨e⟩
    exact (equiv_iff d r hr hr1 (χ⁻¹) χ).mp
      ⟨(inverseCharacterEquiv d r hr χ).trans e⟩
  · intro h
    obtain ⟨e⟩ := (equiv_iff d r hr hr1 (χ⁻¹) χ).mpr h
    exact ⟨(inverseCharacterEquiv d r hr χ).symm.trans e⟩

section Degree
variable (δ : G →* Multiplicative ℤ) (φ : G)
variable (hφ : δ φ = Multiplicative.ofAdd (1 : ℤ)) (n : ℕ) [NeZero n]
variable (ξ : TameDegree.degreeSubgroup δ n →* ℂˣ)

/-- Source-facing dual equivalence on the degree-subgroup induction. -/
def degreeDualEquiv : Representation.Equiv
    (degreeInduced δ n ξ).dual (degreeInduced δ n (ξ⁻¹)) :=
  (inverseCharacterEquiv (TameDegree.degreeMod δ n) (cyclicRep φ)
    (cyclicRep_degree _ φ (by
      change Multiplicative.ofAdd (((δ φ).toAdd : ℤ) : ZMod n) = _
      rw [hφ]
      simp)) ξ).symm

include hφ in
/-- Full character equality, not equality merely on inertia, detects self-duality. -/
theorem degreeSelfDual_iff :
    Nonempty (Representation.Equiv (degreeInduced δ n ξ).dual (degreeInduced δ n ξ)) ↔
      ∃ j : ZMod n, ξ⁻¹ = degreeCharacter δ φ n ξ j := by
  have hh := selfDual_iff (TameDegree.degreeMod δ n) (cyclicRep φ)
    (cyclicRep_degree _ φ (by
      change Multiplicative.ofAdd (((δ φ).toAdd : ℤ) : ZMod n) = _
      rw [hφ]
      simp)) (cyclicRep_one φ) ξ
  constructor
  · intro h
    obtain ⟨j, hj⟩ := hh.mp h
    exact ⟨j.toAdd, hj⟩
  · rintro ⟨j, hj⟩
    exact hh.mpr ⟨Multiplicative.ofAdd j, hj⟩

end Degree
end PaperXI.InducedClassification
