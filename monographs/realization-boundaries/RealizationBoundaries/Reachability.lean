import Mathlib.Algebra.Group.Subgroup.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Set.Countable
import Mathlib.Data.Set.Finite.Basic
import Mathlib.SetTheory.Cardinal.Basic
import Mathlib.Topology.Algebra.Group.ClosedSubgroup

/-!
# Finite descriptions and graph reachability

The finite-code result permits arbitrary single-valued semantics. The graph
result uses the actual dependent direct sum of abelian packets, transfer blocks
of primitive endomorphisms, and finite operator words.
-/
set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace RealizationBoundaries
universe u v w

/-- A grammar has finite strings, an arbitrary validity predicate, and a single
semantic value per valid string. No computability hypothesis is imposed. -/
structure FiniteDescriptionGrammar (Alphabet : Type u) (Target : Type v) where
  valid : Set (List Alphabet)
  realize : valid → Target

def FiniteDescriptionGrammar.outputs {Alphabet : Type u} {Target : Type v}
    (g : FiniteDescriptionGrammar Alphabet Target) : Set Target := Set.range g.realize

/-- Monograph 1.5: single-valued finite-string semantics has countable image. -/
theorem finite_description_outputs_countable {Alphabet : Type u} {Target : Type v}
    [Countable Alphabet] (g : FiniteDescriptionGrammar Alphabet Target) :
    g.outputs.Countable := Set.countable_range g.realize

/-- The same theorem as a cardinal bound on the actual realized-value subtype. -/
theorem finite_description_cardinal_bound {Alphabet : Type u} {Target : Type v}
    [Countable Alphabet] (g : FiniteDescriptionGrammar Alphabet Target) :
    Cardinal.mk g.outputs ≤ Cardinal.aleph0 := by
  exact Cardinal.le_aleph0_iff_set_countable.mpr (finite_description_outputs_countable g)

section Packets
variable {I : Type u} (M : I → Type v) [∀ i, AddCommGroup (M i)]

/-- The genuine dependent direct sum, represented by finite-support vectors. -/
def packetSum : AddSubgroup (∀ i, M i) where
  carrier := {x | {i | x i ≠ 0}.Finite}
  zero_mem' := by simp
  add_mem' := by
    intro x y hx hy
    apply (hx.union hy).subset
    intro i hi
    by_contra hn
    have hxy : x i = 0 ∧ y i = 0 := by simpa using hn
    exact hi (by simp [hxy.1, hxy.2])
  neg_mem' := by intro x hx; simpa using hx

def packetSupport (x : packetSum M) : Set I := {i | x.val i ≠ 0}

def packetProjection (i : I) : packetSum M →+ M i where
  toFun x := x.val i
  map_zero' := rfl
  map_add' _ _ := rfl

/-- The actual packet injection, interpreted as a finite-support vector. -/
def packetSingle (i : I) (a : M i) : packetSum M := by
  classical
  refine ⟨Pi.single i a, (Set.finite_singleton i).subset ?_⟩
  intro j hj
  by_contra h
  have hji : j ≠ i := by simpa only [Set.mem_singleton_iff] using h
  exact hj (Pi.single_eq_of_ne hji a)

@[simp] theorem packetSingle_same (i : I) (a : M i) :
    (packetSingle M i a).val i = a := by
  classical
  simp [packetSingle]

@[simp] theorem packetSingle_other (i j : I) (a : M i) (h : j ≠ i) :
    (packetSingle M i a).val j = 0 := by
  classical
  exact Pi.single_eq_of_ne h a

/-- Finite decomposition is derived from finite support, rather than assumed as
an extra transfer hypothesis. -/
theorem packet_decomposition (x : packetSum M) :
    x = ∑ i ∈ x.property.toFinset, packetSingle M i (x.val i) := by
  classical
  apply Subtype.ext
  funext j
  change packetProjection M j x =
    packetProjection M j (∑ i ∈ x.property.toFinset, packetSingle M i (x.val i))
  rw [map_sum]
  by_cases hj : j ∈ x.property.toFinset
  · rw [Finset.sum_eq_single j]
    · exact (packetSingle_same M j (x.val j)).symm
    · intro i _ hij
      exact packetSingle_other M i j (x.val i) (Ne.symm hij)
    · exact fun hn => False.elim (hn hj)
  · have hxj : x.val j = 0 := by
      by_contra hn
      exact hj ((Set.Finite.mem_toFinset x.property).mpr hn)
    change x.val j = _
    rw [hxj]
    symm
    apply Finset.sum_eq_zero
    intro i hi
    exact packetSingle_other M i j (x.val i) (by intro h; exact hj (h ▸ hi))

/-- A finite directed path from the initial set. The reflexive constructor
includes the empty operator word. -/
inductive GraphReach (E : I → I → Prop) (F : Set I) : I → Prop
  | start {i : I} : i ∈ F → GraphReach E F i
  | step {i j : I} : GraphReach E F i → E i j → GraphReach E F j

/-- The inductive reachability predicate is exactly finite-path reachability
in the usual reflexive transitive closure of the directed graph. -/
theorem graphReach_iff_finite_path (E : I → I → Prop) (F : Set I) (j : I) :
    GraphReach E F j ↔ ∃ i ∈ F, Relation.ReflTransGen E i j := by
  constructor
  · intro h
    induction h with
    | start hi => exact ⟨_, hi, Relation.ReflTransGen.refl⟩
    | step _ hij ih =>
      obtain ⟨i, hi, hpath⟩ := ih
      exact ⟨i, hi, hpath.tail hij⟩
  · rintro ⟨i, hi, hpath⟩
    induction hpath with
    | refl => exact GraphReach.start hi
    | tail _ hij ih => exact GraphReach.step ih hij

/-- Vectors supported on a prescribed packet set form an actual subgroup. -/
def supportedPackets (R : Set I) : AddSubgroup (packetSum M) where
  carrier := {x | ∀ i, i ∉ R → x.val i = 0}
  zero_mem' := by intro i _; rfl
  add_mem' := by intro x y hx hy i hi; change x.val i + y.val i = 0; rw [hx i hi, hy i hi, add_zero]
  neg_mem' := by intro x hx i hi; change -x.val i = 0; rw [hx i hi, neg_zero]

/-- The transfer block from packet `i` to packet `j`, applied to one vector. -/
def packetTransfer (T : AddMonoid.End (packetSum M)) (i j : I) (a : M i) : M j :=
  (T (packetSingle M i a)).val j

/-- Vanishing transfer blocks give the one-step support implication. -/
theorem packet_operator_support (E : I → I → Prop) (R : Set I)
    (hR : ∀ i j, i ∈ R → E i j → j ∈ R)
    (T : AddMonoid.End (packetSum M))
    (hT : ∀ i j, ¬ E i j → ∀ a : M i, packetTransfer M T i j a = 0)
    (x : packetSum M) (hx : x ∈ supportedPackets M R) :
    T x ∈ supportedPackets M R := by
  classical
  intro j hj
  have he := congrArg (fun y : packetSum M => (T y).val j) (packet_decomposition M x)
  change (T x).val j = 0
  rw [he]
  change packetProjection M j (T (∑ i ∈ x.property.toFinset, packetSingle M i (x.val i))) = 0
  rw [map_sum, map_sum]
  apply Finset.sum_eq_zero
  intro i hi
  have hxi : x.val i ≠ 0 := (Set.Finite.mem_toFinset x.property).mp hi
  have hiR : i ∈ R := by by_contra hn; exact hxi (hx i hn)
  exact hT i j (fun hij => hj (hR i j hiR hij)) (x.val i)

end Packets

section OperatorWords
variable {G : Type w} [AddCommGroup G]

/-- Only the declared primitive operators may appear in a word. -/
def operatorWord (O : Set (AddMonoid.End G)) : List O → AddMonoid.End G
  | [] => AddMonoidHom.id G
  | f :: word => f.val.comp (operatorWord O word)

def primitiveOperatorOrbit (O : Set (AddMonoid.End G)) (S : Set G) : Set G :=
  {x | ∃ word : List O, ∃ s ∈ S, operatorWord O word s = x}

def primitiveOperatorHull (O : Set (AddMonoid.End G)) (S : Set G) : AddSubgroup G :=
  AddSubgroup.closure (primitiveOperatorOrbit O S)

/-- An invariant subgroup containing the seeds contains every finite word and
then its algebraic operator hull. -/
theorem primitiveOperatorHull_le (O : Set (AddMonoid.End G)) (S : Set G)
    (H : AddSubgroup G) (hS : S ⊆ H)
    (hH : ∀ T ∈ O, ∀ x ∈ H, T x ∈ H) : primitiveOperatorHull O S ≤ H := by
  apply (AddSubgroup.closure_le _).mpr
  rintro x ⟨word, s, hs, rfl⟩
  induction word with
  | nil => exact hS hs
  | cons T word ih => exact hH T.val T.property _ ih

end OperatorWords

section Reachability
variable {I : Type u} (M : I → Type v) [∀ i, AddCommGroup (M i)]

/-- The initial packet set is exactly the union of the supports of the seeds. -/
def seedPackets (S : Set (packetSum M)) : Set I := ⋃ s ∈ S, packetSupport M s

/-- Monograph 1.8, for the actual direct sum, actual primitive transfer blocks,
and the hull of all finite primitive-operator words. -/
theorem operator_hull_reachable (E : I → I → Prop)
    (O : Set (AddMonoid.End (packetSum M))) (S : Set (packetSum M))
    (hO : ∀ T ∈ O, ∀ i j, ¬ E i j → ∀ a : M i, packetTransfer M T i j a = 0) :
    primitiveOperatorHull O S ≤ supportedPackets M {j | GraphReach E (seedPackets M S) j} := by
  apply primitiveOperatorHull_le
  · intro s hs j hj
    by_contra hn
    exact hj (GraphReach.start (Set.mem_iUnion.mpr ⟨s, Set.mem_iUnion.mpr ⟨hs, hn⟩⟩))
  · intro T hT x hx
    exact packet_operator_support M E _ (fun _ _ hi hij => GraphReach.step hi hij)
      T (hO T hT) x hx

/-- An omitted nonzero packet is an explicit certificate of non-generation. -/
theorem unreachable_packet_obstructs (E : I → I → Prop)
    (O : Set (AddMonoid.End (packetSum M))) (S : Set (packetSum M))
    (hO : ∀ T ∈ O, ∀ i j, ¬ E i j → ∀ a : M i, packetTransfer M T i j a = 0)
    (j : I) (hj : ¬ GraphReach E (seedPackets M S) j) [Nontrivial (M j)] :
    (∀ x ∈ primitiveOperatorHull O S, x.val j = 0) ∧ primitiveOperatorHull O S ≠ ⊤ := by
  have hz : ∀ x ∈ primitiveOperatorHull O S, x.val j = 0 :=
    fun x hx => operator_hull_reachable M E O S hO hx j hj
  refine ⟨hz, ?_⟩
  intro heq
  obtain ⟨a, ha⟩ := exists_ne (0 : M j)
  have hsingle := hz (packetSingle M j a) (heq ▸ AddSubgroup.mem_top _)
  exact ha ((packetSingle_same M j a).symm.trans hsingle)

/-- If the omitted coordinate projection is continuous into a Hausdorff
packet, its closed kernel also contains the topological operator hull. -/
theorem unreachable_packet_obstructs_topological (E : I → I → Prop)
    (O : Set (AddMonoid.End (packetSum M))) (S : Set (packetSum M))
    (hO : ∀ T ∈ O, ∀ i j, ¬ E i j → ∀ a : M i, packetTransfer M T i j a = 0)
    (j : I) (hj : ¬ GraphReach E (seedPackets M S) j)
    [Nontrivial (M j)] [TopologicalSpace (packetSum M)]
    [IsTopologicalAddGroup (packetSum M)] [TopologicalSpace (M j)] [T2Space (M j)]
    (hcontinuous : Continuous (packetProjection M j)) :
    (∀ x ∈ (primitiveOperatorHull O S).topologicalClosure, x.val j = 0) ∧
      (primitiveOperatorHull O S).topologicalClosure ≠ ⊤ := by
  have hle : primitiveOperatorHull O S ≤ (packetProjection M j).ker := by
    intro x hx
    exact (unreachable_packet_obstructs M E O S hO j hj).1 x hx
  have hclosed : IsClosed ((packetProjection M j).ker : Set (packetSum M)) :=
    isClosed_eq hcontinuous continuous_const
  have hclosure : (primitiveOperatorHull O S).topologicalClosure ≤
      (packetProjection M j).ker := closure_minimal hle hclosed
  have hz : ∀ x ∈ (primitiveOperatorHull O S).topologicalClosure, x.val j = 0 := hclosure
  refine ⟨hz, ?_⟩
  intro heq
  obtain ⟨a, ha⟩ := exists_ne (0 : M j)
  have hsingle := hz (packetSingle M j a) (heq ▸ AddSubgroup.mem_top _)
  exact ha ((packetSingle_same M j a).symm.trans hsingle)

end Reachability
end RealizationBoundaries
