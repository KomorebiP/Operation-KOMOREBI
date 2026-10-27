import PaperXI.AtomicReconstruction

/-! Naturality and the exact information-preservation boundary for Theorem 2.5.
Twist laws are attached to the primitive decomposition and ordered quotient
relations. Equivariance of the final candidate is then a theorem, not an input. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.AtomicNaturality
open PaperXI.AtomicMultiset PaperXI.AtomicReconstruction

variable {P A B T : Type*} {sP : Setoid P}

/-- The initial assignment can be stated on representatives. Isomorphism
compatibility suffices to descend it before performing any block reconstruction. -/
theorem reconstruction_from_representatives {A₀ B₀ : Type*}
    (sA : Setoid A₀) (sB : Setoid B₀) (f : A₀ → B₀)
    (hf : ∀ a a', sA.r a a' → sB.r (f a) (f a'))
    (D : Decomposition sP (Quotient sA)) (L : OrderedQuotient (Quotient sB) T) :
    ∃! F : Quotient sP → T, Reconstructs (descend f hf) D L F :=
  formal_atomic_reconstruction (descend f hf) D L

theorem blocks_twist (D : Decomposition sP A) (tP : P → P) (tA : A → A)
    (hP : ∀ p q, sP.r p q → sP.r (tP p) (tP q))
    (hD : ∀ p xs, D.displays p xs → D.displays (tP p) (xs.map (blockMap tA)))
    (p : Quotient sP) :
    blocks D (Quotient.map tP hP p) = extend tA (blocks D p) := by
  refine Quotient.inductionOn p ?_
  intro p
  obtain ⟨xs, hxs⟩ := D.exists_display p
  change blocks D (Quotient.mk sP (tP p)) = extend tA (blocks D (Quotient.mk sP p))
  rw [blocks_of_display D (tP p) _ (hD p xs hxs), blocks_of_display D p xs hxs]
  rfl

/-- Twisting a valid ordered quotient yields the quotient of the twisted factors.
The sorting itself is not assumed to commute: ties may choose different displays. -/
theorem realize_twist (L : OrderedQuotient B T) (tB : B → B) (tT : T → T)
    (horder : ∀ a b, L.precedes a b → L.precedes (blockMap tB a) (blockMap tB b))
    (hquot : ∀ xs t, xs.Pairwise L.precedes → L.quotient xs t →
      L.quotient (xs.map (blockMap tB)) (tT t))
    (s : Multiset (Block B)) : realize L (extend tB s) = tT (realize L s) := by
  have hs : ((ordered L s).map (blockMap tB)).Pairwise L.precedes := by
    rw [List.pairwise_map]
    exact (ordered_pairwise L s).imp (fun h => horder _ _ h)
  have hm : (((ordered L s).map (blockMap tB)) : Multiset (Block B)) = extend tB s := by
    rw [← Multiset.map_coe, ordered_multiset]
    rfl
  exact realize_eq L (extend tB s) _ hs hm _
    (hquot _ _ (ordered_pairwise L s)
      (realize_spec L s _ (ordered_pairwise L s) (ordered_multiset L s)))

/-- The final reconstruction commutes with unramified-type twists when the
atomic assignment and the two classical interfaces have the declared twist laws. -/
theorem candidate_twist (f : A → B) (D : Decomposition sP A)
    (L : OrderedQuotient B T) (tP : P → P) (tA : A → A) (tB : B → B) (tT : T → T)
    (hP : ∀ p q, sP.r p q → sP.r (tP p) (tP q))
    (hD : ∀ p xs, D.displays p xs → D.displays (tP p) (xs.map (blockMap tA)))
    (hf : ∀ a, f (tA a) = tB (f a))
    (horder : ∀ a b, L.precedes a b → L.precedes (blockMap tB a) (blockMap tB b))
    (hquot : ∀ xs t, xs.Pairwise L.precedes → L.quotient xs t →
      L.quotient (xs.map (blockMap tB)) (tT t)) (p : Quotient sP) :
    candidate f D L (Quotient.map tP hP p) = tT (candidate f D L p) := by
  change realize L (extend f (blocks D (Quotient.map tP hP p))) = _
  rw [blocks_twist D tP tA hP hD, extend_natural f tA tB hf]
  exact realize_twist L tB tT horder hquot _

/-- Injectivity of the formal block assembly is exactly injectivity on atoms. -/
theorem extend_injective_iff (f : A → B) :
    Function.Injective (extend f) ↔ Function.Injective f := by
  constructor
  · intro h a b hab
    let x : Block A := ⟨a, 1, by omega⟩
    let y : Block A := ⟨b, 1, by omega⟩
    have hm : extend f ({x} : Multiset (Block A)) = extend f {y} := by
      simp only [extend_singleton]
      congr 1
      exact Block.ext hab rfl
    have he : x = y := by simpa only [Multiset.singleton_inj] using h hm
    exact congrArg Block.atom he
  · exact extend_injective f

/-- Full output injectivity needs both source classification and target
classification, in addition to atomic injectivity. None follows from uniqueness
of the reconstruction map alone. -/
theorem candidate_injective (f : A → B) (D : Decomposition sP A)
    (L : OrderedQuotient B T) (hf : Function.Injective f)
    (hD : Function.Injective (blocks D)) (hL : Function.Injective (realize L)) :
    Function.Injective (candidate f D L) := by
  exact hL.comp ((extend_injective f hf).comp hD)

/-- Different display choices satisfying a common intrinsic-decomposition
contract produce identical candidates. -/
theorem decomposition_independence (f : A → B) (D E : Decomposition sP A)
    (L : OrderedQuotient B T)
    (hDE : ∀ p xs ys, D.displays p xs → E.displays p ys → xs.Perm ys) :
    candidate f D L = candidate f E L := by
  funext p
  refine Quotient.inductionOn p ?_
  intro p
  obtain ⟨xs, hx⟩ := D.exists_display p
  obtain ⟨ys, hy⟩ := E.exists_display p
  change realize L (extend f (blocks D (Quotient.mk sP p))) =
    realize L (extend f (blocks E (Quotient.mk sP p)))
  rw [blocks_of_display D p xs hx, blocks_of_display E p ys hy,
      Multiset.coe_eq_coe.mpr (hDE p xs ys hx hy)]

end PaperXI.AtomicNaturality
