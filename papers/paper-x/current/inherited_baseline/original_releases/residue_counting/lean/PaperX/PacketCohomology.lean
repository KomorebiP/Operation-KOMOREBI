import PaperX.Cohomology

/-!
Paper X 4.2: a finite family of commuting chain projectors yields an actual
linear equivalence between cohomology and the direct sum of packet cohomologies.
The packet terms are ranges of the stated projectors; their boundaries are
computed from their own incoming differentials. No dimension equality is assumed.
-/
set_option autoImplicit false
namespace PaperX.PacketCohomology

open PaperX.Cohomology
open scoped BigOperators DirectSum

universe u v w
variable {R : Type u} [CommRing R]

/-- Restrict a commuting linear map to the actual image submodules. -/
def rangeMap {V W : Type v} [AddCommGroup V] [AddCommGroup W]
    [Module R V] [Module R W]
    (f : V →ₗ[R] W) (p : V →ₗ[R] V) (q : W →ₗ[R] W)
    (h : f.comp p = q.comp f) : LinearMap.range p →ₗ[R] LinearMap.range q :=
  (f.comp (LinearMap.range p).subtype).codRestrict (LinearMap.range q) (by
    rintro ⟨x, y, hy⟩
    exact ⟨f y, by
      change q (f y) = f x
      rw [← hy]
      exact (LinearMap.congr_fun h y).symm⟩)

@[simp] theorem rangeMap_val {V W : Type v} [AddCommGroup V] [AddCommGroup W]
    [Module R V] [Module R W]
    (f : V →ₗ[R] W) (p : V →ₗ[R] V) (q : W →ₗ[R] W)
    (h : f.comp p = q.comp f) (x : LinearMap.range p) :
    (rangeMap f p q h x).val = f x.val := rfl

variable {C D : Triple.{u,v} R}

/-- The genuine packet subcomplex: range(P) in each of three consecutive degrees. -/
def packet (p : ChainMap C C) : Triple.{u,v} R where
  X₀ := LinearMap.range p.left
  X₁ := LinearMap.range p.middle
  X₂ := LinearMap.range p.right
  d₀ := rangeMap C.d₀ p.left p.middle p.comm₀
  d₁ := rangeMap C.d₁ p.middle p.right p.comm₁
  square := by
    ext x
    exact LinearMap.congr_fun C.square x.val

def inclusion (p : ChainMap C C) : ChainMap (packet p) C where
  left := (LinearMap.range p.left).subtype
  middle := (LinearMap.range p.middle).subtype
  right := (LinearMap.range p.right).subtype
  comm₀ := by ext x; rfl
  comm₁ := by ext x; rfl

def projection (p : ChainMap C C) : ChainMap C (packet p) where
  left := p.left.rangeRestrict
  middle := p.middle.rangeRestrict
  right := p.right.rangeRestrict
  comm₀ := by
    ext x
    apply Subtype.ext
    exact LinearMap.congr_fun p.comm₀ x
  comm₁ := by
    ext x
    apply Subtype.ext
    exact LinearMap.congr_fun p.comm₁ x

/-- Inclusion of a packet cocycle really is a total cocycle. -/
theorem packet_cycle_is_cycle (p : ChainMap C C) (x : Cycles (packet p)) :
    C.d₁ x.val.val = 0 := by
  exact congrArg Subtype.val x.property

/-- The incoming packet boundary is obtained from an incoming element in range(P). -/
theorem packet_boundary_is_boundary (p : ChainMap C C) (x : (packet p).X₀) :
    C.d₀ x.val = ((packet p).d₀ x).val := rfl

/-- A retraction on the quotient, proved using actual packet representatives. -/
theorem h_retract (p : ChainMap C C) (hp : p.middle.comp p.middle = p.middle)
    (z : H (packet p)) : hmap (projection p) (hmap (inclusion p) z) = z := by
  obtain ⟨x, rfl⟩ := classOf_surjective (packet p) z
  rw [hmap_classOf, hmap_classOf]
  congr 1
  apply Subtype.ext
  apply Subtype.ext
  change p.middle x.val.val = x.val.val
  obtain ⟨y, hy⟩ := x.val.property
  rw [← hy]
  exact LinearMap.congr_fun hp y

/-- Orthogonal packets vanish under the other packet's quotient projection. -/
theorem h_cross_zero (p q : ChainMap C C)
    (hpq : p.middle.comp q.middle = 0) (z : H (packet q)) :
    hmap (projection p) (hmap (inclusion q) z) = 0 := by
  obtain ⟨x, rfl⟩ := classOf_surjective (packet q) z
  rw [hmap_classOf, hmap_classOf]
  have hx : cyclesMap (projection p) (cyclesMap (inclusion q) x) = 0 := by
    apply Subtype.ext
    apply Subtype.ext
    change p.middle x.val.val = 0
    obtain ⟨y, hy⟩ := x.val.property
    rw [← hy]
    exact LinearMap.congr_fun hpq y
  rw [hx, map_zero]

/-- Only the middle-degree orthogonality and completeness are needed for H in
that degree; a full chain-projector resolution in the manuscript implies them. -/
structure Resolution (C : Triple.{u,v} R) (ι : Type w) [Fintype ι] where
  projectors : ι → ChainMap C C
  idempotent : ∀ i, (projectors i).middle.comp (projectors i).middle = (projectors i).middle
  orthogonal : ∀ i j, i ≠ j → (projectors i).middle.comp (projectors j).middle = 0
  complete : ∑ i, (projectors i).middle = LinearMap.id

variable {ι : Type w} [Fintype ι]

theorem h_reconstruct (P : Resolution C ι) (z : H C) :
    ∑ i, hmap (inclusion (P.projectors i)) (hmap (projection (P.projectors i)) z) = z := by
  obtain ⟨x, rfl⟩ := classOf_surjective C z
  simp only [hmap_classOf]
  rw [← map_sum]
  congr 1
  apply Subtype.ext
  simp only [Submodule.coe_sum]
  change (∑ i, (P.projectors i).middle x.val) = x.val
  simpa only [LinearMap.sum_apply, LinearMap.id_apply] using
    LinearMap.congr_fun P.complete x.val

/-- The main splitting as a linear equivalence with the finite product. -/
noncomputable def cohomologyPiEquiv (P : Resolution C ι) :
    H C ≃ₗ[R] (∀ i, H (packet (P.projectors i))) := by
  classical
  refine
    { LinearMap.pi (fun i => hmap (projection (P.projectors i))) with
      invFun := fun z => ∑ i, hmap (inclusion (P.projectors i)) (z i)
      left_inv := fun z => h_reconstruct P z
      right_inv := ?_ }
  intro z
  funext i
  change hmap (projection (P.projectors i)) (∑ j, hmap (inclusion (P.projectors j)) (z j)) = z i
  rw [map_sum, Finset.sum_eq_single i]
  · exact h_retract _ (P.idempotent i) (z i)
  · intro j _ hj
    exact h_cross_zero _ _ (P.orthogonal i j (Ne.symm hj)) (z j)
  · intro hi
    exact (hi (Finset.mem_univ i)).elim

/-- Paper X 4.2 in literal direct-sum notation. Valid over every commutative ring. -/
noncomputable def cohomologyPacketEquiv (P : Resolution C ι) :
    H C ≃ₗ[R] ⨁ i, H (packet (P.projectors i)) :=
  (cohomologyPiEquiv P).trans
    (DirectSum.linearEquivFunOnFintype R ι (fun i => H (packet (P.projectors i)))).symm

/-- The forward map is exactly projection of a cocycle's class. -/
theorem decompose_class (P : Resolution C ι) (x : Cycles C) (i : ι) :
    cohomologyPiEquiv P (classOf C x) i =
      classOf (packet (P.projectors i)) (cyclesMap (projection (P.projectors i)) x) := rfl

/-- Its inverse is precisely the finite sum of included packet classes. -/
theorem recompose_classes (P : Resolution C ι) (z : ∀ i, H (packet (P.projectors i))) :
    (cohomologyPiEquiv P).symm z =
      ∑ i, hmap (inclusion (P.projectors i)) (z i) := rfl

/-- Being a total boundary is equivalent to every projected cocycle being a
boundary inside its own packet, not merely vanishing in the ambient module. -/
theorem boundary_iff_packet_boundaries (P : Resolution C ι) (x : Cycles C) :
    classOf C x = 0 ↔
      ∀ i, ∃ y : (packet (P.projectors i)).X₀,
        (packet (P.projectors i)).d₀ y = (projection (P.projectors i)).middle x.val := by
  constructor
  · intro hx i
    have h := congrArg (fun z => cohomologyPiEquiv P z i) hx
    simpa only [decompose_class, map_zero, Pi.zero_apply, classOf_eq_zero_iff,
      cyclesMap_val] using h
  · intro hx
    apply (cohomologyPiEquiv P).injective
    ext i
    rw [map_zero, Pi.zero_apply, decompose_class, classOf_eq_zero_iff]
    exact hx i


/-- Splitting detects vanishing but cannot force it: total cohomology vanishes
if and only if every packet cohomology vanishes. -/
theorem vanishing_iff (P : Resolution C ι) :
    Subsingleton (H C) ↔ ∀ i, Subsingleton (H (packet (P.projectors i))) := by
  constructor
  · intro h i
    let _ := h
    constructor
    intro x y
    calc
      x = hmap (projection (P.projectors i)) (hmap (inclusion (P.projectors i)) x) :=
        (h_retract _ (P.idempotent i) x).symm
      _ = hmap (projection (P.projectors i)) (hmap (inclusion (P.projectors i)) y) :=
        congrArg (hmap (projection (P.projectors i))) (Subsingleton.elim _ _)
      _ = y := h_retract _ (P.idempotent i) y
  · intro h
    constructor
    intro x y
    apply (cohomologyPiEquiv P).injective
    funext i
    exact (h i).elim _ _

end PaperX.PacketCohomology
