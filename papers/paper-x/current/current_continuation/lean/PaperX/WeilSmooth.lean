import PaperX.WeilCopies
import PaperX.CarrierCompatibility

/-! The finite-image and open-kernel inertia conditions are predicates on the
actual representation, and their preservation under finite sums is proved. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.WeilSmooth
open PaperX.WeilData PaperX.WeilCopies PaperX.CarrierSummands PaperX.CarrierPolynomials
variable {K G I : Type*} [Field K] [Group G] [Fintype I]
variable {W : I → Type*} [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]

omit [Fintype I] in
theorem copies_eq_one_iff (ρ : ∀ i, Representation K G (W i)) (m : I → ℕ) (g : G) :
    copiesRep ρ m g = 1 ↔ ∀ i, 0 < m i → ρ i g = 1 := by
  classical
  constructor
  · intro h i hi
    apply LinearMap.ext
    intro x
    have hh := congrFun (congrFun (LinearMap.congr_fun h
      (Pi.single i (fun _ : Fin (m i) => x))) i) (⟨0, hi⟩ : Fin (m i))
    simpa using hh
  · intro h
    apply LinearMap.ext
    intro x
    funext i k
    have hi := h i (lt_of_le_of_lt (Nat.zero_le k.val) k.isLt)
    simp [hi]

theorem copies_inertia_finite (ρ : ∀ i, Representation K G (W i)) (m : I → ℕ)
    (H : Subgroup G) (h : ∀ i, Set.Finite (Set.range (fun g : H => ρ i g))) :
    Set.Finite (Set.range (fun g : H => copiesRep ρ m g)) := by
  classical
  have : ∀ i, Finite (Set.range (fun g : H => ρ i g)) := fun i => (h i).to_subtype
  have ht := Set.finite_range (fun z : ∀ i, Set.range (fun g : H => ρ i g) =>
    piEnd (fun i => piEnd (fun _ : Fin (m i) => (z i).val)))
  apply ht.subset
  rintro _ ⟨g, rfl⟩
  refine ⟨fun i => ⟨ρ i g, ⟨g, rfl⟩⟩, ?_⟩
  ext x i k
  rfl

theorem copies_inertia_open [TopologicalSpace G]
    (ρ : ∀ i, Representation K G (W i)) (m : I → ℕ) (H : Subgroup G)
    (h : ∀ i, IsOpen {g : H | ρ i g = 1}) :
    IsOpen {g : H | copiesRep ρ m g = 1} := by
  have he : {g : H | copiesRep ρ m g = 1} =
      ⋂ i, {g : H | 0 < m i → ρ i g = 1} := by
    ext g
    simp [copies_eq_one_iff]
  rw [he]
  apply isOpen_iInter_of_finite
  intro i
  by_cases hi : 0 < m i
  · simpa [hi] using h i
  · simp [hi]

structure InertialDatum {ν : G →* Kˣ} (H : Subgroup G) [TopologicalSpace G]
    (V : Type*) [AddCommGroup V] [Module K V] extends Datum ν V where
  inertia_finite : Set.Finite (Set.range (fun g : H => toDatum.r g))
  inertia_open : IsOpen {g : H | toDatum.r g = 1}

def copiesInertialDatum {ν : G →* Kˣ} [TopologicalSpace G] (H : Subgroup G)
    (D : ∀ i, InertialDatum (ν := ν) H (W i)) (m : I → ℕ) :
    InertialDatum (ν := ν) H (Copies W m) where
  toDatum := copiesDatum (fun i => (D i).toDatum) m
  inertia_finite := copies_inertia_finite _ m H (fun i => (D i).inertia_finite)
  inertia_open := copies_inertia_open _ m H (fun i => (D i).inertia_open)

end PaperX.WeilSmooth
