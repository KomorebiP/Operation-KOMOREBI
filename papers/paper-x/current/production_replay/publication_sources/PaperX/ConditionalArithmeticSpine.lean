import PaperX.DeterminantSpine
import PaperX.InverseLimitLocalConditions

/-! The universal conditional implication of source Claim 8.2.

The selected weight and packet relations are parameters, just as the source
quantifies over a chosen spine and assumes inverse-limit closure. They are not
definitions of Hodge--Tate or Weil--Deligne attachment. Instantiating such a
relation and proving its closure is an application premise, not a conclusion.
Determinants are coefficient-specific: no common E-valued character on G is
required. The shared polynomial data still live over E.
-/
set_option autoImplicit false
namespace PaperX.ConditionalArithmeticSpine
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.RepresentationTopology PaperX.ClassCompletion PaperX.ClassInvariants
open PaperX.ClassCommonSpine PaperX.InverseLimitLocalConditions
open PaperX.DeterminantSpine

variable {Λ G ι V E : Type} [Group G] [Fintype ι] [DecidableEq ι] [Field E]
variable (K : Λ → Type) [∀ l, Field (K l)]

/-- A precise interface for the source's chosen data. The relations retain their
supplied meaning; this structure neither constructs them nor declares them true.
Inactive places can be represented by implications inside the packet relation.
The determinant family may vary with the coefficient place. -/
structure Spine where
  sample : V → G
  good : Λ → V → Prop
  good_cofinite : ∀ l, {v | ¬ good l v}.Finite
  polynomial : V → Polynomial E
  determinant : (l : Λ) → G → K l
  Weight : Type
  weights : Weight
  hasWeights : (l : Λ) → Weight → MatrixRep (K l) G ι → Prop
  PacketIndex : Type
  Packet : PacketIndex → Type
  packets : (j : PacketIndex) → Packet j
  hasPacket : (l : Λ) → (j : PacketIndex) → Packet j → MatrixRep (K l) G ι → Prop

variable {K}

/-- Exactly the selected full local conditions, with the common labels visible. -/
def LocalRealizes (S : Spine (G := G) (ι := ι) (V := V) (E := E) K)
    (l : Λ) (ρ : MatrixRep (K l) G ι) : Prop :=
  S.hasWeights l S.weights ρ ∧ ∀ j, S.hasPacket l j (S.packets j) ρ

/-- Realization of every item of the chosen spine. Continuity is a separate
conclusion of completion. This definition imposes no extra WD convention beyond
the supplied packet relation, and no semisimplicity beyond the selected data. -/
def RealizesSpine (S : Spine (G := G) (ι := ι) (V := V) (E := E) K)
    (emb : (l : Λ) → E →+* K l) (ρ : (l : Λ) → MatrixRep (K l) G ι) : Prop :=
  (∀ l v, S.good l v → (ρ l (S.sample v)).charpoly =
    (S.polynomial v).map (emb l)) ∧
  (∀ l g, (ρ l g).det = S.determinant l g) ∧
  ∀ l, LocalRealizes S l (ρ l)

/-- The good-place metadata in the chosen spine gives an actual almost-everywhere
common polynomial statement at every coefficient place. -/
theorem realizes_almost_everywhere
    (S : Spine (G := G) (ι := ι) (V := V) (E := E) K)
    (emb : (l : Λ) → E →+* K l) (ρ : (l : Λ) → MatrixRep (K l) G ι)
    (h : RealizesSpine S emb ρ) (l : Λ) :
    ∀ᶠ v in Filter.cofinite,
      (ρ l (S.sample v)).charpoly = (S.polynomial v).map (emb l) := by
  have hg : ∀ᶠ v in Filter.cofinite, S.good l v :=
    Filter.mem_cofinite.mpr (S.good_cofinite l)
  exact hg.mono (fun v hv => h.1 l v hv)

/-- An integral realization supplies the actual branch promised in the source,
including its allowed objects and exact successive reductions. -/
def reductionBranch {R : Type} [CommRing R] (I : Ideal R)
    (C : ClassConditions (G := G) (ι := ι) I) (ρ : MatrixRep R G ι)
    (hρ : ∀ k, C.allowed k (classOf (reduce I ρ k))) :
    PaperX.Compactness.Branch (PaperX.RepresentationForests.tower I (framed I C)) where
  value k := ⟨reduce I ρ k, hρ k⟩
  compatible k := Subtype.ext (transition_reduce I ρ (Nat.le_succ k))

@[simp] theorem reductionBranch_value {R : Type} [CommRing R] (I : Ideal R)
    (C : ClassConditions (G := G) (ι := ι) I) (ρ : MatrixRep R G ι)
    (hρ : ∀ k, C.allowed k (classOf (reduce I ρ k))) (k : ℕ) :
    ((reductionBranch I C ρ hρ).value k).val = reduce I ρ k := rfl

variable [TopologicalSpace G] [∀ l, TopologicalSpace (K l)]

/-- All four source ingredients are used: a specified spine and its reductions,
finite nonempty admissible levels, total compatible reduction maps (in C), and
inverse-limit closure of the selected full local conditions. Finite branching
requires no additional assumption because every level is finite.

The complete coefficient rings and continuity of finite admissible objects are
the ambient representation setting. No coefficient-prime carrier, finite-level
liftability, arithmetic local closure, or coherent framing is concluded for free.
-/
theorem adelic_finite_depth_completion
    (O : Λ → Type) [∀ l, CommRing (O l)]
    (I : (l : Λ) → Ideal (O l)) [∀ l, IsAdicComplete (I l) (O l)]
    (hI : ∀ l, (I l).FG) [∀ l, Finite (O l ⧸ I l)]
    (C : (l : Λ) → ClassConditions (G := G) (ι := ι) (I l))
    (finite : ∀ l k, 0 < k → Finite {c // (C l).allowed k c})
    (occupied : ∀ l k, 0 < k → ∃ c, (C l).allowed k c)
    (continuous : ∀ l k c, (C l).allowed k c →
      ∃ ρ, classOf ρ = c ∧ FiniteRepContinuous ρ)
    (inc : (l : Λ) → O l →+* K l)
    (hinc : ∀ l, @Continuous (O l) (K l) (I l).adicTopology inferInstance (inc l))
    (emb : (l : Λ) → E →+* K l)
    (S : Spine (G := G) (ι := ι) (V := V) (E := E) K)
    (closed : ∀ l, InverseLimitClosed (I l) (C l)
      (fun ρ => LocalRealizes S l (changeCoefficients (inc l) ρ)))
    (localP : (l : Λ) → V → Polynomial (O l))
    (poly_integral : ∀ l v, S.good l v →
      (localP l v).map (inc l) = (S.polynomial v).map (emb l))
    (poly_spec : ∀ l k c, (C l).allowed k c → ∀ v, S.good l v →
      classCharpoly c (S.sample v) = (localP l v).map (Ideal.Quotient.mk ((I l)^k)))
    (localDet : (l : Λ) → G → O l)
    (det_integral : ∀ l g, inc l (localDet l g) = S.determinant l g)
    (det_spec : ∀ l k c, (C l).allowed k c → ∀ g,
      classDet c g = Ideal.Quotient.mk ((I l)^k) (localDet l g)) :
    ∃ ρ : (l : Λ) → MatrixRep (O l) G ι,
      (∀ l k, (C l).allowed k (classOf (reduce (I l) (ρ l) k))) ∧
      (∀ l, Continuous (changeCoefficients (inc l) (ρ l))) ∧
      RealizesSpine S emb (fun l => changeCoefficients (inc l) (ρ l)) := by
  obtain ⟨ρ, hρ, hl, hp⟩ := unframed_common_spine_completion O K I hI C
    finite occupied continuous inc hinc emb (LocalRealizes S)
    (fun l => (inverseLimitClosed_iff_realizations (I l) (C l) _).mp (closed l))
    S.sample S.good S.polynomial localP poly_integral poly_spec
  refine ⟨ρ, hρ, fun l => (hl l).1, hp, ?_, fun l => (hl l).2⟩
  intro l g
  rw [determinant_changeCoefficients,
    class_realization_has_determinant (I l) (C l) (ρ l) (hρ l) (localDet l)
      (det_spec l) g, det_integral]

end PaperX.ConditionalArithmeticSpine
