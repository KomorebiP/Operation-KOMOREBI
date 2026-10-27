import PaperX.WeilCopies

/-! Maps commute with every group element and with monodromy. Restrictions
therefore respect the actual inertia-fixed kernel, including split summands. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.WeilMorphisms
open PaperX.WeilData PaperX.WeilCopies PaperX.CarrierSummands
variable {K G : Type*} [Field K] [Group G] {ν : G →* Kˣ}
variable {U V W : Type*} [AddCommGroup U] [Module K U]
variable [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

structure Hom (D : Datum ν V) (E : Datum ν W) where
  map : V →ₗ[K] W
  group_eq : ∀ g x, map (D.r g x) = E.r g (map x)
  monodromy_eq : ∀ x, map (D.N x) = E.N (map x)

def fixedMap {D : Datum ν V} {E : Datum ν W} (f : Hom D E) (H : Subgroup G) :
    fixedKernel D H →ₗ[K] fixedKernel E H where
  toFun x := ⟨f.map x.val, ⟨by
    change E.N (f.map x.val) = 0
    rw [← f.monodromy_eq, show D.N x.val = 0 from x.property.1, map_zero], by
    intro h
    change E.r h (f.map x.val) = f.map x.val
    rw [← f.group_eq]
    exact congrArg f.map (x.property.2 h)⟩⟩
  map_add' x y := by apply Subtype.ext; exact f.map.map_add _ _
  map_smul' a x := by apply Subtype.ext; exact f.map.map_smul _ _

theorem fixedMap_equivariant {D : Datum ν V} {E : Datum ν W}
    (f : Hom D E) (H : Subgroup G) [H.Normal] (g : G) (x : fixedKernel D H) :
    fixedMap f H (fixedRep D H g x) = fixedRep E H g (fixedMap f H x) := by
  apply Subtype.ext
  exact f.group_eq g x.val

/-- An actual group-and-monodromy equivalence restricts to an equivalence of local spaces. -/
def fixedEquiv {D : Datum ν V} {E : Datum ν W} (e : V ≃ₗ[K] W)
    (he : ∀ g x, e (D.r g x) = E.r g (e x))
    (hN : ∀ x, e (D.N x) = E.N (e x)) (H : Subgroup G) :
    fixedKernel D H ≃ₗ[K] fixedKernel E H where
  toFun := fixedMap ⟨e.toLinearMap, he, hN⟩ H
  invFun := fixedMap ⟨e.symm.toLinearMap,
    fun g y => by apply e.injective; simp [he],
    fun y => by apply e.injective; simp [hN]⟩ H
  left_inv x := by apply Subtype.ext; exact e.symm_apply_apply x.val
  right_inv x := by apply Subtype.ext; exact e.apply_symm_apply x.val
  map_add' x y := (fixedMap ⟨e.toLinearMap, he, hN⟩ H).map_add x y
  map_smul' a x := (fixedMap ⟨e.toLinearMap, he, hN⟩ H).map_smul a x

theorem localCharpoly_equiv [FiniteDimensional K V] [FiniteDimensional K W]
    {D : Datum ν V} {E : Datum ν W} (e : V ≃ₗ[K] W)
    (he : ∀ g x, e (D.r g x) = E.r g (e x))
    (hN : ∀ x, e (D.N x) = E.N (e x)) (H : Subgroup G) [H.Normal] (φ : G) :
    localCharpoly D H φ = localCharpoly E H φ := by
  have hc : (fixedEquiv e he hN H).conj (fixedRep D H φ) = fixedRep E H φ := by
    ext x
    change e (D.r φ (e.symm x.val)) = E.r φ x.val
    rw [he, e.apply_symm_apply]
  unfold localCharpoly
  rw [← LinearEquiv.charpoly_conj (fixedEquiv e he hN H), hc]

variable {I : Type*} [Fintype I] {X : I → Type*}
variable [∀ i, AddCommGroup (X i)] [∀ i, Module K (X i)]

def inclusionHom (D : ∀ i, Datum ν (X i)) {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    Hom (copiesDatum D m) (copiesDatum D c) where
  map := inclusion h
  group_eq := inclusion_equivariant (fun i => (D i).r) h
  monodromy_eq := PaperX.MonodromyData.inclusion_intertwines_N (fun i => (D i).N) h

def retractionHom (D : ∀ i, Datum ν (X i)) {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    Hom (copiesDatum D c) (copiesDatum D m) where
  map := retraction h
  group_eq := retraction_equivariant (fun i => (D i).r) h
  monodromy_eq := PaperX.MonodromyData.retraction_intertwines_N (fun i => (D i).N) h

theorem fixed_split (D : ∀ i, Datum ν (X i)) (H : Subgroup G)
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (x : fixedKernel (copiesDatum D m) H) :
    fixedMap (retractionHom D h) H (fixedMap (inclusionHom D h) H x) = x := by
  apply Subtype.ext
  exact retraction_inclusion h x.val

end PaperX.WeilMorphisms
