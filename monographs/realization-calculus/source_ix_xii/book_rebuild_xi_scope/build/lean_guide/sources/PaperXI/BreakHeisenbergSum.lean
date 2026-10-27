import PaperXI.AbstractHeisenberg
import PaperXI.CentralProduct
import Mathlib.Algebra.BigOperators.GroupWithZero.Finset
import Mathlib.Tactic

/-! Actual half-form Heisenberg groups of a finite orthogonal sum are the
balanced central product of the summand groups. The retained center handles
an empty family. The group isomorphism is constructed, not assumed. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace PaperXI.BreakHeisenbergSum
open AbstractHeisenberg

variable {S K : Type*} [Fintype S] [Field K]
variable {V : S → Type*} [∀ s, AddCommGroup (V s)] [∀ s, Module K (V s)]

/-- The actual bilinear form on the dependent finite product. -/
def form (b : ∀ s, LinearMap.BilinForm K (V s)) : LinearMap.BilinForm K (∀ s, V s) where
  toFun v := {
    toFun := fun w => ∑ s, b s (v s) (w s)
    map_add' := by intros; simp [map_add, Finset.sum_add_distrib]
    map_smul' := by intros; simp [Finset.mul_sum] }
  map_add' := by intros; ext; simp [map_add, Finset.sum_add_distrib]
  map_smul' := by intros; ext; simp [Finset.mul_sum]

@[simp] theorem form_apply (b : ∀ s, LinearMap.BilinForm K (V s)) (v w : ∀ s, V s) :
    form b v w = ∑ s, b s (v s) (w s) := rfl

theorem form_isAlt (b : ∀ s, LinearMap.BilinForm K (V s)) (hb : ∀ s, (b s).IsAlt) :
    (form b).IsAlt := by
  intro v
  simp [form_apply, fun s => hb s (v s)]

/-- The actual ambient product maps to the half-form group by summing central coordinates. -/
def fromProduct (b : ∀ s, LinearMap.BilinForm K (V s)) :
    CentralProduct.Ambient (Z := Multiplicative K) (H := fun s => Element (b s)) →*
      Element (form b) where
  toFun x := ⟨fun s => (x.2 s).vector, x.1.toAdd + ∑ s, (x.2 s).central⟩
  map_one' := by ext <;> simp
  map_mul' x y := by
    ext
    · rfl
    · simp only [mul_central, form_apply, Prod.fst_mul, Prod.snd_mul,
        toAdd_mul, Pi.mul_apply]
      simp only [Finset.sum_add_distrib, Finset.mul_sum]
      ring

@[simp] theorem fromProduct_vector (b : ∀ s, LinearMap.BilinForm K (V s))
    (x : CentralProduct.Ambient (Z := Multiplicative K) (H := fun s => Element (b s))) (s : S) :
    (fromProduct b x).vector s = (x.2 s).vector := rfl

@[simp] theorem fromProduct_central (b : ∀ s, LinearMap.BilinForm K (V s))
    (x : CentralProduct.Ambient (Z := Multiplicative K) (H := fun s => Element (b s))) :
    (fromProduct b x).central = x.1.toAdd + ∑ s, (x.2 s).central := rfl

/-- A total group element has the literal coordinate-wise preimage with central sum correction. -/
theorem fromProduct_surjective (b : ∀ s, LinearMap.BilinForm K (V s)) :
    Function.Surjective (fromProduct b) := by
  intro h
  refine ⟨(Multiplicative.ofAdd h.central, fun s => ⟨h.vector s, 0⟩), ?_⟩
  ext <;> simp

/-- The actual balancing relation is killed by the orthogonal-sum map. -/
theorem fromProduct_balanced (b : ∀ s, LinearMap.BilinForm K (V s)) (w : S → Multiplicative K) :
    fromProduct b (CentralProduct.balanced (fun s => datum (b s)) w) = 1 := by
  ext
  · rfl
  · simp [fromProduct, CentralProduct.balanced]

/-- The induced map from the actual central quotient. -/
def sumMap (b : ∀ s, LinearMap.BilinForm K (V s)) :
    CentralProduct.Group (fun s => datum (b s)) →* Element (form b) :=
  CentralProduct.descend _ (fromProduct b) (fromProduct_balanced b)

@[simp] theorem sumMap_mk (b : ∀ s, LinearMap.BilinForm K (V s))
    (x : CentralProduct.Ambient (Z := Multiplicative K) (H := fun s => Element (b s))) :
    sumMap b (CentralProduct.mk _ x) = fromProduct b x := rfl

@[simp] theorem sumMap_center (b : ∀ s, LinearMap.BilinForm K (V s)) (z : Multiplicative K) :
    sumMap b (CentralProduct.center _ z) = (datum (form b)).i z := by
  ext <;> simp [CentralProduct.center_apply]

theorem sumMap_surjective (b : ∀ s, LinearMap.BilinForm K (V s)) :
    Function.Surjective (sumMap b) := by
  intro h
  obtain ⟨x, rfl⟩ := fromProduct_surjective b h
  exact ⟨CentralProduct.mk _ x, rfl⟩

/-- Vanishing of the actual image forces the representative to be a balanced central tuple. -/
theorem sumMap_injective (b : ∀ s, LinearMap.BilinForm K (V s)) :
    Function.Injective (sumMap b) := by
  apply (MonoidHom.ker_eq_bot_iff _).mp
  apply le_antisymm
  · intro x hx
    change x = 1
    obtain ⟨⟨z, h⟩, rfl⟩ := CentralProduct.mk_surjective (fun s => datum (b s)) x
    have hv : ∀ s, (h s).vector = 0 := by
      intro s
      exact congrArg (fun x : Element (form b) => x.vector s) hx
    have hz : z.toAdd + ∑ s, (h s).central = 0 :=
      congrArg (fun x : Element (form b) => x.central) hx
    have hh : h = fun s => (datum (b s)).i (Multiplicative.ofAdd (h s).central) := by
      funext s
      ext
      · exact hv s
      · rfl
    rw [hh, CentralProduct.mk_centers]
    have hw : z * ∏ s, Multiplicative.ofAdd (h s).central = 1 := by
      apply Multiplicative.toAdd.injective
      simpa using hz
    rw [hw, map_one]
  · exact bot_le

/-- The central product is the actual Heisenberg group of the orthogonal finite product. -/
def sumEquiv (b : ∀ s, LinearMap.BilinForm K (V s)) :
    CentralProduct.Group (fun s => datum (b s)) ≃* Element (form b) :=
  MulEquiv.ofBijective (sumMap b) ⟨sumMap_injective b, sumMap_surjective b⟩

@[simp] theorem sumEquiv_mk (b : ∀ s, LinearMap.BilinForm K (V s))
    (x : CentralProduct.Ambient (Z := Multiplicative K) (H := fun s => Element (b s))) :
    sumEquiv b (CentralProduct.mk _ x) = fromProduct b x := rfl

@[simp] theorem sumEquiv_center (b : ∀ s, LinearMap.BilinForm K (V s)) (z : Multiplicative K) :
    sumEquiv b (CentralProduct.center _ z) = (datum (form b)).i z := sumMap_center b z

variable {T : Type*} [AddCommGroup T] [Module K T]

/-- Transfer through the actual supplied form-preserving break decomposition. -/
def decompositionEquiv (b : ∀ s, LinearMap.BilinForm K (V s))
    (c : LinearMap.BilinForm K T) (e : (∀ s, V s) ≃ₗ[K] T)
    (he : ∀ v w, c (e v) (e w) = form b v w) :
    CentralProduct.Group (fun s => datum (b s)) ≃* Element c :=
  (sumEquiv b).trans (AbstractHeisenberg.lift (form b) c e he)

@[simp] theorem decompositionEquiv_center (b : ∀ s, LinearMap.BilinForm K (V s))
    (c : LinearMap.BilinForm K T) (e : (∀ s, V s) ≃ₗ[K] T)
    (he : ∀ v w, c (e v) (e w) = form b v w) (z : Multiplicative K) :
    decompositionEquiv b c e he (CentralProduct.center _ z) = (datum c).i z := by
  exact (congrArg (AbstractHeisenberg.lift (form b) c e he) (sumEquiv_center b z)).trans
    (AbstractHeisenberg.lift_inclusion (form b) c e he z)

end PaperXI.BreakHeisenbergSum
