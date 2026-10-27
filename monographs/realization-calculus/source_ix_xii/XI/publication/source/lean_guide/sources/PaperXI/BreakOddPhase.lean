import PaperXI.BreakMoving

/-! Source 15.3 in odd characteristic, using the moving phase of Definition
12.7. Fixed vectors do not enter a determinant on the full singular space. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BreakOddPhase
open FixedMoving
open scoped BigOperators Classical

variable {p : ℕ} [Fact p.Prime]
variable {ι : Type*} [Fintype ι] {V : ι → Type*}
variable [∀ i, AddCommGroup (V i)] [∀ i, Module (ZMod p) (V i)]
variable [∀ i, FiniteDimensional (ZMod p) (V i)]
variable {X : Type*} [AddCommGroup X] [Module (ZMod p) X]

omit [Fintype ι] [∀ i, FiniteDimensional (ZMod p) (V i)] in
/-- Fixed-point-freeness of the actual total moving action descends to every
actual summand moving action through the constructed moving decomposition. -/
theorem component_fixedPointFree
    (G : X ≃ₗ[ZMod p] X) (g : ∀ i, V i ≃ₗ[ZMod p] V i)
    (e : X ≃ₗ[ZMod p] (∀ i, V i))
    (he : ∀ x, e (G x) = LinearEquiv.piCongrRight g (e x))
    (hf : OddPhase.FixedPointFree (movingAction G)) (i : ι) :
    OddPhase.FixedPointFree (movingAction (g i)) := by
  have hp := (OddPhase.fixedPointFree_conjugacy (movingAction G)
    (LinearEquiv.piCongrRight (fun j => movingAction (g j)))
    (BreakMoving.equiv G g e he) (BreakMoving.equiv_intertwines G g e he)).mp hf
  intro x hx
  have hsingle : LinearEquiv.piCongrRight (fun j => movingAction (g j)) (Pi.single i x) =
      Pi.single i x := by
    funext j
    by_cases hji : j = i
    · subst j
      simpa using hx
    · simp [Pi.single_eq_of_ne hji]
  have hz := congrFun (hp (Pi.single i x) hsingle) i
  simpa using hz

/-- Finite multiplicativity after constructing the actual moving equivalence.
The hypotheses on the summand moving forms are derived in `source` below. -/
theorem product_of_moving_forms (hp : p ≠ 2)
    (G : X ≃ₗ[ZMod p] X) (g : ∀ i, V i ≃ₗ[ZMod p] V i)
    (e : X ≃ₗ[ZMod p] (∀ i, V i))
    (he : ∀ x, e (G x) = LinearEquiv.piCongrRight g (e x))
    (b : ∀ i, LinearMap.BilinForm (ZMod p) (V i))
    (ha : ∀ i, (b i).IsAlt) (hn : ∀ i, (movingForm (g i) (b i)).Nondegenerate) :
    MovingPhase.phase G = ∏ i, MovingPhase.phase (g i) := by
  change OddPhase.phase (movingAction G) = ∏ i, OddPhase.phase (movingAction (g i))
  rw [OddPhase.conjugacy (movingAction G)
    (OddPhaseSum.action (fun i => movingAction (g i)))
    (BreakMoving.equiv G g e he) (BreakMoving.equiv_intertwines G g e he)]
  exact OddPhaseSum.phase_product_symplectic hp (fun i => movingForm (g i) (b i))
    (fun i => movingForm_alt (g i) (b i) (ha i)) hn (fun i => movingAction (g i))

/-- The source moving hypothesis supplies nondegenerate moving restrictions
and hence the product law. No extra condition on the order of g is required. -/
theorem product (hp : p ≠ 2)
    (G : X ≃ₗ[ZMod p] X) (g : ∀ i, V i ≃ₗ[ZMod p] V i)
    (e : X ≃ₗ[ZMod p] (∀ i, V i))
    (he : ∀ x, e (G x) = LinearEquiv.piCongrRight g (e x))
    (b : ∀ i, LinearMap.BilinForm (ZMod p) (V i))
    (ha : ∀ i, (b i).IsAlt) (hn : ∀ i, (b i).Nondegenerate)
    (hb : ∀ i x y, b i (g i x) (g i y) = b i x y)
    (hf : OddPhase.FixedPointFree (movingAction G)) :
    MovingPhase.phase G = ∏ i, MovingPhase.phase (g i) :=
  product_of_moving_forms hp G g e he b ha (fun i =>
    BreakMoving.movingForm_nondegenerate (g i)
      (component_fixedPointFree G g e he hf i) (b i) (ha i) (hn i) (hb i))

omit [Fintype ι] in
/-- Each determinant in the actual moving product is nonzero. This conclusion
includes a zero moving space, whose endomorphism determinant is one. -/
theorem determinants_ne_zero
    (G : X ≃ₗ[ZMod p] X) (g : ∀ i, V i ≃ₗ[ZMod p] V i)
    (e : X ≃ₗ[ZMod p] (∀ i, V i))
    (he : ∀ x, e (G x) = LinearEquiv.piCongrRight g (e x))
    (hf : OddPhase.FixedPointFree (movingAction G)) (i : ι) :
    (OddPhase.difference (movingAction (g i))).det ≠ 0 :=
  (OddPhase.fixedPointFree_iff_det_ne_zero (movingAction (g i))).mp
    (component_fixedPointFree G g e he hf i)

omit [Fintype ι] [∀ i, FiniteDimensional (ZMod p) (V i)] in
/-- The finite product law is valid when the family is empty. -/
theorem empty [IsEmpty ι] (G : X ≃ₗ[ZMod p] X)
    (e : X ≃ₗ[ZMod p] (∀ i, V i)) : MovingPhase.phase G = 1 := by
  have : Subsingleton X := e.injective.subsingleton
  exact OddPhase.phase_zero_space (movingAction G)

omit [Fintype ι] [∀ i, FiniteDimensional (ZMod p) (V i)] in
/-- A summand with zero moving space contributes exactly one. -/
theorem zero_moving_factor (i : ι) (g : V i ≃ₗ[ZMod p] V i)
    [Subsingleton (moving g)] : MovingPhase.phase g = 1 :=
  OddPhase.phase_zero_space (movingAction g)

section Internal
variable [FiniteDimensional (ZMod p) X]

/-- The actual internal decomposition is equivariant in the inverse direction. -/
theorem internal_intertwines (G : X ≃ₗ[ZMod p] X)
    (S : ι → Submodule (ZMod p) X) (hS : DirectSum.IsInternal S)
    (hs : ∀ i, ∀ x ∈ S i, G x ∈ S i) (x : X) :
    (OrthogonalPhase.decomposition S hS).symm (G x) =
      LinearEquiv.piCongrRight (OrthogonalPhase.restricted G S hs)
        ((OrthogonalPhase.decomposition S hS).symm x) := by
  apply (OrthogonalPhase.decomposition S hS).injective
  rw [LinearEquiv.apply_symm_apply, OrthogonalPhase.intertwines,
    LinearEquiv.apply_symm_apply]

omit [FiniteDimensional (ZMod p) X] in
/-- Orthogonality proves the actual internal decomposition's form identity. -/
theorem internal_form (b : LinearMap.BilinForm (ZMod p) X)
    (S : ι → Submodule (ZMod p) X) (hS : DirectSum.IsInternal S)
    (ho : ∀ i j, i ≠ j → ∀ x ∈ S i, ∀ y ∈ S j, b x y = 0)
    (x y : ∀ i, S i) :
    b (OrthogonalPhase.decomposition S hS x) (OrthogonalPhase.decomposition S hS y) =
      ∑ i, b.restrict (S i) (x i) (y i) := by
  simp only [OrthogonalPhase.decomposition_sum, map_sum, LinearMap.sum_apply]
  apply Finset.sum_congr rfl
  intro i _
  exact Finset.sum_eq_single i (fun j _ hji => ho j i hji _ (x j).property
    _ (y i).property) (fun hi => (hi (Finset.mem_univ i)).elim)

/-- The constructed total moving equivalence preserves the actual orthogonal
sum of the moving forms; neither forms nor action covariance are abstract placeholders. -/
theorem internal_moving_form (G : X ≃ₗ[ZMod p] X)
    (b : LinearMap.BilinForm (ZMod p) X)
    (S : ι → Submodule (ZMod p) X) (hS : DirectSum.IsInternal S)
    (ho : ∀ i j, i ≠ j → ∀ x ∈ S i, ∀ y ∈ S j, b x y = 0)
    (hs : ∀ i, ∀ x ∈ S i, G x ∈ S i) (x y : moving G) :
    movingForm G b x y = ∑ i,
      movingForm (OrthogonalPhase.restricted G S hs i) (b.restrict (S i))
        (BreakMoving.equiv G (OrthogonalPhase.restricted G S hs)
          (OrthogonalPhase.decomposition S hS).symm (internal_intertwines G S hS hs) x i)
        (BreakMoving.equiv G (OrthogonalPhase.restricted G S hs)
          (OrthogonalPhase.decomposition S hS).symm (internal_intertwines G S hS hs) y i) := by
  apply BreakMoving.equiv_preserves G (OrthogonalPhase.restricted G S hs)
    (OrthogonalPhase.decomposition S hS).symm (internal_intertwines G S hS hs) b
    (fun i => b.restrict (S i))
  intro u v
  simpa only [LinearEquiv.apply_symm_apply] using internal_form b S hS ho
    ((OrthogonalPhase.decomposition S hS).symm u) ((OrthogonalPhase.decomposition S hS).symm v)

/-- Source 15.3, odd branch: the actual finite internal orthogonal decomposition,
its restricted actions, and fixed-point-freeness on the total moving image imply
the Definition 12.7 moving-phase product. Empty families and zero summands are allowed. -/
theorem source (hp : p ≠ 2) (b : LinearMap.BilinForm (ZMod p) X)
    (ha : b.IsAlt) (hn : b.Nondegenerate) (G : X ≃ₗ[ZMod p] X)
    (hb : ∀ x y, b (G x) (G y) = b x y)
    (S : ι → Submodule (ZMod p) X) (hS : DirectSum.IsInternal S)
    (ho : ∀ i j, i ≠ j → ∀ x ∈ S i, ∀ y ∈ S j, b x y = 0)
    (hs : ∀ i, ∀ x ∈ S i, G x ∈ S i)
    (hf : OddPhase.FixedPointFree (movingAction G)) :
    MovingPhase.phase G = ∏ i, MovingPhase.phase (OrthogonalPhase.restricted G S hs i) := by
  exact product hp G (OrthogonalPhase.restricted G S hs)
    (OrthogonalPhase.decomposition S hS).symm (internal_intertwines G S hS hs)
    (fun i => b.restrict (S i))
    (fun i => OrthogonalSummands.restricted_isAlt b ha (S i))
    (fun i => OrthogonalSummands.restricted_form_nondegenerate b hn S
      hS.submodule_iSup_eq_top ho i)
    (fun i => OrthogonalSummands.restrictionEquiv_form b G hb (S i) (hs i)) hf

end Internal
end PaperXI.BreakOddPhase
