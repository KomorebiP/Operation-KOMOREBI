import PaperXI.CentralProduct

/-! Actual maps and isomorphisms of the central quotients induced by compatible factor maps. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralProduct

variable {S Z : Type*} [Fintype S] [CommGroup Z]
variable {H A H' A' : S → Type*}
variable [∀ s, _root_.Group (H s)] [∀ s, CommGroup (A s)]
variable [∀ s, _root_.Group (H' s)] [∀ s, CommGroup (A' s)]
variable (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
variable (E : ∀ s, CentralExtension.Datum Z (H' s) (A' s))

def ambientMap (f : ∀ s, H s →* H' s) :
    Ambient (Z := Z) (H := H) →* Ambient (Z := Z) (H := H') where
  toFun x := (x.1, fun s => f s (x.2 s))
  map_one' := by ext <;> simp
  map_mul' x y := by ext <;> simp

def map (f : ∀ s, H s →* H' s)
    (hf : ∀ s z, f s ((D s).i z) = (E s).i z) : Group D →* Group E :=
  descend D ((mk E).comp (ambientMap f)) (by
    intro z
    change mk E ((∏ s, z s)⁻¹, fun s => f s ((D s).i (z s))) = 1
    simp_rw [hf]
    exact mk_balanced E z)

@[simp] theorem map_mk (f : ∀ s, H s →* H' s)
    (hf : ∀ s z, f s ((D s).i z) = (E s).i z)
    (x : Ambient (Z := Z) (H := H)) :
    map D E f hf (mk D x) = mk E (x.1, fun s => f s (x.2 s)) := rfl

@[simp] theorem map_center (f : ∀ s, H s →* H' s)
    (hf : ∀ s z, f s ((D s).i z) = (E s).i z) (z : Z) :
    map D E f hf (center D z) = center E z := by
  simp [center_apply]
  rfl

def congr (f : ∀ s, H s ≃* H' s)
    (hf : ∀ s z, f s ((D s).i z) = (E s).i z) : Group D ≃* Group E where
  toFun := map D E (fun s => (f s).toMonoidHom) hf
  invFun := map E D (fun s => (f s).symm.toMonoidHom) (by
    intro s z
    apply (f s).injective
    simpa using (hf s z).symm)
  left_inv x := by
    obtain ⟨x, rfl⟩ := mk_surjective D x
    simp
  right_inv x := by
    obtain ⟨x, rfl⟩ := mk_surjective E x
    simp
  map_mul' x y := (map D E (fun s => (f s).toMonoidHom) hf).map_mul x y

@[simp] theorem congr_mk (f : ∀ s, H s ≃* H' s)
    (hf : ∀ s z, f s ((D s).i z) = (E s).i z)
    (x : Ambient (Z := Z) (H := H)) :
    congr D E f hf (mk D x) = mk E (x.1, fun s => f s (x.2 s)) := rfl

@[simp] theorem congr_center (f : ∀ s, H s ≃* H' s)
    (hf : ∀ s z, f s ((D s).i z) = (E s).i z) (z : Z) :
    congr D E f hf (center D z) = center E z := map_center D E _ hf z

end PaperXI.CentralProduct
