import PaperXI.FiniteTensor

/-! Actual finite tensor maps of the supplied break intertwiners. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BreakTensorMap

variable {ι K : Type*} [Field K] {H V W : ι → Type*}
variable [∀ i, Monoid (H i)]
variable [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]
variable [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]

/-- The tensor bridge is an actual invertible map of multiple tensor products. -/
def tensor (U : ∀ i, V i ≃ₗ[K] W i) :
    PiTensorProduct K V ≃ₗ[K] PiTensorProduct K W := PiTensorProduct.congr U

@[simp] theorem tensor_tprod (U : ∀ i, V i ≃ₗ[K] W i) (v : ∀ i, V i) :
    tensor U (PiTensorProduct.tprod K v) =
      PiTensorProduct.tprod K (fun i => U i (v i)) :=
  PiTensorProduct.congr_tprod U v

@[simp] theorem tensor_symm_tprod (U : ∀ i, V i ≃ₗ[K] W i) (w : ∀ i, W i) :
    (tensor U).symm (PiTensorProduct.tprod K w) =
      PiTensorProduct.tprod K (fun i => (U i).symm (w i)) :=
  PiTensorProduct.congr_symm_tprod U w

theorem tensor_symm (U : ∀ i, V i ≃ₗ[K] W i) :
    (tensor U).symm = tensor (fun i => (U i).symm) := by
  apply LinearEquiv.toLinearMap_injective
  apply PiTensorProduct.ext
  ext v
  simp

/-- Actual factor covariance extends by the tensor universal property. -/
theorem intertwines (ρ : ∀ i, Representation K (H i) (V i))
    (σ : ∀ i, Representation K (H i) (W i)) (U : ∀ i, V i ≃ₗ[K] W i)
    (hU : ∀ i h x, U i (ρ i h x) = σ i h (U i x))
    (h : ∀ i, H i) (x : PiTensorProduct K V) :
    tensor U (FiniteTensor.representation ρ h x) =
      FiniteTensor.representation σ h (tensor U x) := by
  have he : (tensor U).toLinearMap.comp (FiniteTensor.representation ρ h) =
      (FiniteTensor.representation σ h).comp (tensor U).toLinearMap := by
    apply PiTensorProduct.ext
    ext v
    simp [hU]
  exact DFunLike.congr_fun he x

/-- Covariance passes through any actual surjective quotient map. -/
theorem descends {P Q X Y : Type*} [Monoid P] [Monoid Q]
    [AddCommGroup X] [Module K X] [AddCommGroup Y] [Module K Y]
    (q : P →* Q) (hq : Function.Surjective q)
    (ρ : Representation K Q X) (σ : Representation K Q Y) (U : X ≃ₗ[K] Y)
    (hU : ∀ p x, U (ρ (q p) x) = σ (q p) (U x)) :
    ∀ g x, U (ρ g x) = σ g (U x) := by
  intro g x
  obtain ⟨p, rfl⟩ := hq g
  exact hU p x

variable {C : Type*} [Monoid C]

/-- The common stabilizer acts on every break at once. -/
def stabilizer (R : ∀ i, Representation K C (V i)) :
    Representation K C (PiTensorProduct K V) :=
  (FiniteTensor.representation R).comp (MonoidHom.pi (fun _ => MonoidHom.id C))

@[simp] theorem stabilizer_tprod (R : ∀ i, Representation K C (V i))
    (g : C) (v : ∀ i, V i) :
    stabilizer R g (PiTensorProduct.tprod K v) =
      PiTensorProduct.tprod K (fun i => R i g (v i)) := by
  exact FiniteTensor.representation_tprod R (fun _ => g) v

/-- Factor discrepancies multiply to the actual total discrepancy. -/
def productCharacter [Fintype ι] (δ : ι → C →* Kˣ) : C →* Kˣ where
  toFun g := ∏ i, δ i g
  map_one' := by simp
  map_mul' g h := by simp [Finset.prod_mul_distrib]

@[simp] theorem productCharacter_apply [Fintype ι] (δ : ι → C →* Kˣ) (g : C) :
    productCharacter δ g = ∏ i, δ i g := rfl

/-- The total discrepancy permits nontrivial break characters to cancel. -/
theorem scalar_intertwines [Fintype ι]
    (R : ∀ i, Representation K C (V i)) (T : ∀ i, Representation K C (W i))
    (U : ∀ i, V i ≃ₗ[K] W i) (δ : ι → C →* Kˣ)
    (hδ : ∀ i g x, U i (R i g x) = (δ i g : K) • T i g (U i x))
    (g : C) (x : PiTensorProduct K V) :
    tensor U (stabilizer R g x) =
      (productCharacter δ g : K) • stabilizer T g (tensor U x) := by
  have he : (tensor U).toLinearMap.comp (stabilizer R g) =
      (productCharacter δ g : K) • ((stabilizer T g).comp (tensor U).toLinearMap) := by
    apply PiTensorProduct.ext
    ext v
    simp only [LinearMap.compMultilinearMap_apply, LinearMap.comp_apply,
      LinearEquiv.coe_coe, stabilizer_tprod, tensor_tprod, LinearMap.smul_apply, hδ]
    simpa [productCharacter_apply] using
      (PiTensorProduct.tprod K (s := W)).map_smul_univ (fun i => (δ i g : K))
        (fun i => T i g (U i (v i)))
  exact DFunLike.congr_fun he x

end PaperXI.BreakTensorMap
