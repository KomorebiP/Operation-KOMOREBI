module
public import Mathlib.Geometry.Manifold.Algebra.Structures
public import Mathlib.Geometry.Manifold.VectorBundle.Basic
public import Mathlib.Analysis.Calculus.ContDiff.Operations
public import Mathlib.Analysis.Normed.Ring.Units
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, item 6.4.
Construct the range-bundle atlas from a smooth idempotent, not as a hypothesis.
The fibers are the actual fixed subspaces, with their subspace topologies.
-/
@[expose] public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
open scoped Manifold ContDiff Topology
open Set Filter
noncomputable section
namespace KomorebiPaperVII.RangeBundle

variable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- The actual fiber, written as the fixed subspace of an idempotent. -/
def fiber (p : F →L[ℝ] F) : Submodule ℝ F where
  carrier := {v | p v = v}
  zero_mem' := map_zero p
  add_mem' := by intro u v hu hv; simp_all
  smul_mem' := by intro c v hv; simp_all

@[simp] theorem mem_fiber (p : F →L[ℝ] F) (v : F) : v ∈ fiber p ↔ p v = v := Iff.rfl

/-- Projection from the ambient space to the actual fiber. -/
def project (p : F →L[ℝ] F) (hp : p*p=p) : F →L[ℝ] fiber p :=
  p.codRestrict (fiber p) (fun v => congrArg (fun q : F →L[ℝ] F => q v) hp)

@[simp] theorem project_coe (p : F →L[ℝ] F) (hp : p*p=p) (v : F) :
    (project p hp v : F) = p v := rfl

@[simp] theorem project_fiber (p : F →L[ℝ] F) (hp : p*p=p) (v : fiber p) :
    project p hp (v : F) = v := Subtype.ext v.property

/-- Canonical intertwiner between two nearby idempotents. -/
def transport (p q : F →L[ℝ] F) : F →L[ℝ] F := p*q+(1-p)*(1-q)

theorem transport_self (p : F →L[ℝ] F) (hp : p*p=p) : transport p p=1 := by
  unfold transport
  noncomm_ring [hp]

theorem transport_intertwines (p q : F →L[ℝ] F) (hp : p*p=p) (hq : q*q=q) :
    p*transport p q=transport p q*q := by
  unfold transport
  have ha : p*(p*q)=p*q := by rw [← mul_assoc,hp]
  have hb : p*(q*q)=p*q := by rw [hq]
  noncomm_ring [hp,hq,ha,hb]

theorem transport_inverse_intertwines (p q : F →L[ℝ] F) (hp : p*p=p) (hq : q*q=q)
    (h : IsUnit (transport p q)) : q*Ring.inverse (transport p q)=Ring.inverse (transport p q)*p := by
  calc
    q*Ring.inverse (transport p q) =
      Ring.inverse (transport p q)*(transport p q*q)*Ring.inverse (transport p q) := by
        simp only [← mul_assoc, Ring.inverse_mul_cancel _ h, one_mul]
    _ = Ring.inverse (transport p q)*(p*transport p q)*Ring.inverse (transport p q) := by
      rw [transport_intertwines p q hp hq]
    _ = Ring.inverse (transport p q)*p := by
      simp only [mul_assoc, Ring.mul_inverse_cancel _ h, mul_one]

variable {M : Type*} [TopologicalSpace M]

/-- Each base point determines an open local trivialization domain. -/
def domain (P : M → F →L[ℝ] F) (a : M) : Set M :=
  {x | IsUnit (transport (P x) (P a))}

theorem mem_domain (P : M → F →L[ℝ] F) (hP : ∀ x, P x*P x=P x) (a : M) :
    a ∈ domain P a := by simp [domain, transport_self _ (hP a)]

theorem isOpen_domain [CompleteSpace F] (P : M → F →L[ℝ] F) (hP : Continuous P) (a : M) :
    IsOpen (domain P a) :=
  Units.isOpen.preimage ((hP.mul continuous_const).add
    ((continuous_const.sub hP).mul continuous_const))

/-- Fiber coordinates. The extra fixed projection makes this a total CLM. -/
def toCoord (P : M → F →L[ℝ] F) (hP : ∀ x, P x*P x=P x) (a x : M) :
    F →L[ℝ] fiber (P a) :=
  (project (P a) (hP a)).comp (Ring.inverse (transport (P x) (P a)))

/-- Reconstruction from the coordinate fiber into the ambient space. -/
def fromCoord (P : M → F →L[ℝ] F) (a x : M) : fiber (P a) →L[ℝ] F :=
  (transport (P x) (P a)).comp (fiber (P a)).subtypeL

theorem fromCoord_range (P : M → F →L[ℝ] F) (hP : ∀ x, P x*P x=P x)
    (a x : M) (v : fiber (P a)) : P x (fromCoord P a x v)=fromCoord P a x v := by
  have ht := congrArg (fun q : F →L[ℝ] F => q (v : F))
    (transport_intertwines (P x) (P a) (hP x) (hP a))
  have hv : P a (v : F)=(v : F) := v.property
  simpa [fromCoord, hv] using ht

theorem toCoord_fromCoord (P : M → F →L[ℝ] F) (hP : ∀ x, P x*P x=P x)
    (a x : M) (hx : x ∈ domain P a) (v : fiber (P a)) :
    toCoord P hP a x (fromCoord P a x v)=v := by
  apply Subtype.ext
  change P a ((Ring.inverse (transport (P x) (P a)) * transport (P x) (P a)) (v : F)) = v
  rw [Ring.inverse_mul_cancel _ hx]
  exact v.property

theorem fromCoord_toCoord (P : M → F →L[ℝ] F) (hP : ∀ x, P x*P x=P x)
    (a x : M) (hx : x ∈ domain P a) (v : F) (hv : P x v=v) :
    fromCoord P a x (toCoord P hP a x v)=v := by
  have ht := congrArg (fun q : F →L[ℝ] F => q v)
    (transport_inverse_intertwines (P x) (P a) (hP x) (hP a) hx)
  change transport (P x) (P a) (P a (Ring.inverse (transport (P x) (P a)) v))=v
  rw [show P a (Ring.inverse (transport (P x) (P a)) v)=
    Ring.inverse (transport (P x) (P a)) v from by simpa [hv] using ht]
  change (transport (P x) (P a)*Ring.inverse (transport (P x) (P a))) v=v
  rw [Ring.mul_inverse_cancel _ hx]
  rfl

/-- The transition is an actual map between the two fixed coordinate fibers. -/
def transition (P : M → F →L[ℝ] F) (hP : ∀ x, P x*P x=P x) (a b x : M) :
    fiber (P a) →L[ℝ] fiber (P b) := (toCoord P hP b x).comp (fromCoord P a x)

theorem transition_self (P : M → F →L[ℝ] F) (hP : ∀ x, P x*P x=P x)
    (a x : M) (hx : x ∈ domain P a) : transition P hP a a x=1 := by
  apply ContinuousLinearMap.ext
  intro v
  exact toCoord_fromCoord P hP a x hx v

theorem transition_cocycle (P : M → F →L[ℝ] F) (hP : ∀ x, P x*P x=P x)
    (a b c x : M) (hb : x ∈ domain P b) :
    (transition P hP b c x).comp (transition P hP a b x)=transition P hP a c x := by
  apply ContinuousLinearMap.ext
  intro v
  change toCoord P hP c x (fromCoord P b x (toCoord P hP b x (fromCoord P a x v))) = _
  rw [fromCoord_toCoord P hP b x hb _ (fromCoord_range P hP a x v)]
  rfl

variable {E H : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [TopologicalSpace H]
  {I : ModelWithCorners ℝ E H} [ChartedSpace H M] [CompleteSpace F]

theorem smooth_transport (P : M → F →L[ℝ] F)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) (a : M) :
    ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ (fun x => transport (P x) (P a)) :=
  (hP.clm_comp contMDiff_const).add ((contMDiff_const.sub hP).clm_comp contMDiff_const)

theorem smooth_inverse_transport (P : M → F →L[ℝ] F)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) (a : M) :
    ContMDiffOn I 𝓘(ℝ, F →L[ℝ] F) ∞
      (fun x => Ring.inverse (transport (P x) (P a))) (domain P a) := by
  intro x hx
  have hi : ContDiffAt ℝ ∞ Ring.inverse (transport (P x) (P a)) := by
    simpa only [IsUnit.unit_spec] using (contDiffAt_ringInverse ℝ hx.unit (n := ∞))
  exact hi.comp_contMDiffWithinAt (f := fun y : M => transport (P y) (P a))
    ((smooth_transport P hP a x).contMDiffWithinAt)

theorem smooth_toCoord (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) (a : M) :
    ContMDiffOn I 𝓘(ℝ, F →L[ℝ] fiber (P a)) ∞ (toCoord P hPP a) (domain P a) :=
  contMDiffOn_const.clm_comp (smooth_inverse_transport P hP a)

theorem smooth_fromCoord (P : M → F →L[ℝ] F)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) (a : M) :
    ContMDiff I 𝓘(ℝ, fiber (P a) →L[ℝ] F) ∞ (fromCoord P a) :=
  (smooth_transport P hP a).clm_comp contMDiff_const

theorem smooth_transition (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) (a b : M) :
    ContMDiffOn I 𝓘(ℝ, fiber (P a) →L[ℝ] fiber (P b)) ∞
      (transition P hPP a b) (domain P a ∩ domain P b) :=
  ((smooth_toCoord P hPP hP b).mono inter_subset_right).clm_comp
    (smooth_fromCoord P hP a).contMDiffOn


/-- Actual global range space, with the topology induced from `M × F`. -/
abbrev Total (P : M → F →L[ℝ] F) := {z : M × F // P z.1 z.2=z.2}

/-- Restriction of the actual total space to a trivialization domain. -/
abbrev LocalTotal (P : M → F →L[ℝ] F) (a : M) :=
  {z : Total P // z.val.1 ∈ domain P a}

/-- The explicitly constructed fiberwise linear local product homeomorphism. -/
def localProduct (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) (a : M) :
    LocalTotal P a ≃ₜ (domain P a × fiber (P a)) where
  toFun z := (⟨z.val.val.1,z.property⟩,toCoord P hPP a z.val.val.1 z.val.val.2)
  invFun y := ⟨⟨(y.1.val,fromCoord P a y.1.val y.2),
    fromCoord_range P hPP a y.1.val y.2⟩,y.1.property⟩
  left_inv := by
    intro z
    apply Subtype.ext
    apply Subtype.ext
    apply Prod.ext
    · rfl
    · exact fromCoord_toCoord P hPP a _ z.property _ z.val.property
  right_inv := by
    intro y
    apply Prod.ext
    · rfl
    · exact toCoord_fromCoord P hPP a _ y.1.property y.2
  continuous_toFun := by
    have hx : Continuous (fun z : LocalTotal P a => z.val.val.1) := by fun_prop
    have hv : Continuous (fun z : LocalTotal P a => z.val.val.2) := by fun_prop
    have hc : Continuous (fun z : LocalTotal P a => toCoord P hPP a z.val.val.1) :=
      (smooth_toCoord P hPP hP a).continuousOn.comp_continuous hx (fun z => z.property)
    exact (hx.subtype_mk _).prodMk (hc.clm_apply hv)
  continuous_invFun := by
    have hx : Continuous (fun y : domain P a × fiber (P a) => y.1.val) := by fun_prop
    have hv : Continuous (fun y : domain P a × fiber (P a) => y.2) := by fun_prop
    have hc : Continuous (fun y : domain P a × fiber (P a) => fromCoord P a y.1.val) :=
      (smooth_fromCoord P hP a).continuous.comp hx
    exact ((hx.prodMk (hc.clm_apply hv)).subtype_mk _).subtype_mk _

/-- The local homeomorphism does not change the base point. -/
theorem localProduct_base (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) (a : M) (z : LocalTotal P a) :
    (localProduct P hPP hP a z).1.val=z.val.val.1 := rfl

/-- Reconstruction of local coordinates is exactly the transition map. -/
theorem localProduct_transition (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (a b x : M) (v : fiber (P a)) :
    toCoord P hPP b x (fromCoord P a x v)=transition P hPP a b x v := rfl

/-- A local fiber equivalence, derived from the same transport. -/
def fiberEquiv (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (a x : M) (hx : x ∈ domain P a) : fiber (P a) ≃L[ℝ] fiber (P x) where
  toFun v := ⟨fromCoord P a x v, fromCoord_range P hPP a x v⟩
  invFun v := toCoord P hPP a x v
  left_inv := toCoord_fromCoord P hPP a x hx
  right_inv := fun v => Subtype.ext (fromCoord_toCoord P hPP a x hx v v.property)
  map_add' := by intros; apply Subtype.ext; exact map_add _ _ _
  map_smul' := by intros; apply Subtype.ext; exact map_smul _ _ _
  continuous_toFun := (fromCoord P a x).continuous.subtype_mk _
  continuous_invFun := (toCoord P hPP a x).continuous.comp continuous_subtype_val

/-- Local constancy of rank is a consequence, not an additional hypothesis. -/
theorem fiber_rank_locally_constant (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) (a : M) :
    ∀ᶠ x in 𝓝 a, Module.finrank ℝ (fiber (P x))=Module.finrank ℝ (fiber (P a)) := by
  filter_upwards [(isOpen_domain P hP.continuous a).mem_nhds (mem_domain P hPP a)] with x hx
  exact (fiberEquiv P hPP a x hx).toLinearEquiv.finrank_eq.symm

/-- All local data come from `P`. This bundles the actual construction and its smooth cocycle. -/
theorem smooth_range_bundle_atlas (P : M → F →L[ℝ] F) (hPP : ∀ x, P x*P x=P x)
    (hP : ContMDiff I 𝓘(ℝ, F →L[ℝ] F) ∞ P) :
    (∀ a, IsOpen (domain P a) ∧ a ∈ domain P a) ∧
    (∀ a, Nonempty (LocalTotal P a ≃ₜ (domain P a × fiber (P a)))) ∧
    (∀ a b, ContMDiffOn I 𝓘(ℝ, fiber (P a) →L[ℝ] fiber (P b)) ∞
      (transition P hPP a b) (domain P a ∩ domain P b)) ∧
    (∀ a x, x ∈ domain P a → transition P hPP a a x=1) ∧
    (∀ a b c x, x ∈ domain P a ∩ domain P b ∩ domain P c →
      (transition P hPP b c x).comp (transition P hPP a b x)=transition P hPP a c x) := by
  exact ⟨fun a => ⟨isOpen_domain P hP.continuous a,mem_domain P hPP a⟩,
    fun a => ⟨localProduct P hPP hP a⟩,smooth_transition P hPP hP,
    transition_self P hPP,fun a b c x hx => transition_cocycle P hPP a b c x hx.1.2⟩

end KomorebiPaperVII.RangeBundle
