import ContinuousLocalGluingCokernel

/-! The local degree-zero terms absent from the strict v0.28 quotient.
All cochains retain their genuine continuity proofs; the source is not discretized. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

def localGaugeCoboundary (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    (I → D.Kernel) →ₗ[ℤ] D.localOneCocycles L loc where
  toFun x := ⟨⟨fun i h => D.action (loc i h) (x i)-x i,fun i =>
    ((D.continuous_kernel_action hr).comp ((hloc i).prodMk continuous_const)).sub
      continuous_const⟩,by
    intro i g h
    change D.action (loc i g) (D.action (loc i h) (x i)-x i) -
      (D.action (loc i (g*h)) (x i)-x i)+(D.action (loc i g) (x i)-x i)=0
    rw [map_sub,map_mul,map_mul]
    change D.action (loc i g) (D.action (loc i h) (x i))-D.action (loc i g) (x i)-
      (D.action (loc i g) (D.action (loc i h) (x i))-x i)+
      (D.action (loc i g) (x i)-x i)=0
    abel⟩
  map_add' x y := by
    apply Subtype.ext
    apply Subtype.ext
    funext i h
    change D.action (loc i h) (x i+y i)-(x i+y i)=_
    rw [map_add]
    change _=(D.action (loc i h) (x i)-x i)+(D.action (loc i h) (y i)-y i)
    abel
  map_smul' r x := by
    apply Subtype.ext
    apply Subtype.ext
    funext i h
    change D.action (loc i h) (r • x i)-r • x i=r • (D.action (loc i h) (x i)-x i)
    rw [map_smul,smul_sub]

omit [IsTopologicalGroup G] in
@[simp] theorem localGaugeCoboundary_apply (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (x : I → D.Kernel) (i : I) (h : L i) :
    (D.localGaugeCoboundary L hr loc hloc x).1.1 i h=D.action (loc i h) (x i)-x i := rfl

def globalGaugeCoboundary (hr : Continuous D.lift) :
    D.Kernel →ₗ[ℤ] D.globalOneCocycles hr where
  toFun x := ⟨⟨fun g => D.action g x-x,
    ((D.continuous_kernel_action hr).comp (continuous_id.prodMk continuous_const)).sub
      continuous_const⟩,by
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    change D.action g (D.action h x-x)-(D.action (g*h) x-x)+(D.action g x-x)=0
    rw [map_sub,map_mul]
    change D.action g (D.action h x)-D.action g x-
      (D.action g (D.action h x)-x)+(D.action g x-x)=0
    abel⟩
  map_add' x y := by
    apply Subtype.ext
    apply Subtype.ext
    funext g
    change D.action g (x+y)-(x+y)=(D.action g x-x)+(D.action g y-y)
    rw [map_add]
    abel
  map_smul' r x := by
    apply Subtype.ext
    apply Subtype.ext
    funext g
    change D.action g (r • x)-r • x=r • (D.action g x-x)
    rw [map_smul,smul_sub]

@[simp] theorem restrict_globalGaugeCoboundary (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) (x : D.Kernel) :
    D.restrictOneCocycles L hr loc hloc (D.globalGaugeCoboundary hr x)=
      D.localGaugeCoboundary L hr loc hloc (fun _ => x) := by
  rfl

/-- Degree-one continuous cohomology in the explicit inhomogeneous convention. -/
abbrev GaugeGlobalH1 (hr : Continuous D.lift) :=
  D.globalOneCocycles hr ⧸ LinearMap.range (D.globalGaugeCoboundary hr)

/-- Family of local degree-one classes, with independent local zero-cochains. -/
abbrev GaugeLocalH1 (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :=
  D.localOneCocycles L loc ⧸ LinearMap.range (D.localGaugeCoboundary L hr loc hloc)

noncomputable def gaugeRestrictionH1 (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.GaugeGlobalH1 hr →ₗ[ℤ] D.GaugeLocalH1 L hr loc hloc :=
  (LinearMap.range (D.globalGaugeCoboundary hr)).liftQ
    (((LinearMap.range (D.localGaugeCoboundary L hr loc hloc)).mkQ).comp
      (D.restrictOneCocycles L hr loc hloc)) (by
    rintro z ⟨x,rfl⟩
    change Submodule.Quotient.mk _=0
    rw [Submodule.Quotient.mk_eq_zero]
    exact ⟨fun _ => x,rfl⟩)

@[simp] theorem gaugeRestrictionH1_mk (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.globalOneCocycles hr) :
    D.gaugeRestrictionH1 L hr loc hloc (Submodule.Quotient.mk z)=
      Submodule.Quotient.mk (D.restrictOneCocycles L hr loc hloc z) := rfl

end Komorebi.StrongArtin.SquareZeroH2.Datum
