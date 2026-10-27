/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Algebra.Polynomial.Basic
import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Data.Finset.NatAntidiagonal
import Mathlib.Data.Fintype.Card
import Mathlib.Data.List.OfFn
import Mathlib.Data.Matrix.Basic
import Mathlib.LinearAlgebra.Matrix.Adjugate
import Mathlib.RingTheory.PowerSeries.Basic
import Mathlib.RingTheory.PowerSeries.Inverse

/-!
# Finite weighted transfer walks and certificate-checked zeta series

This file formalizes the finite combinatorial part of the transfer-zeta
construction.  A finite edge type represents a directed multigraph: distinct
edges may have the same source and target, so parallel edges are counted with
their full multiplicity.  Every edge has strictly positive natural weight.

The coefficient algorithm is genuinely finite.  At weight `n` it enumerates
tuples of at most `n` edges, filters by endpoints and exact total weight, and
counts the survivors.  Positivity proves that this bound loses no walk.

The finite transfer matrix also gives a certificate-free rational series.
Writing `T = I - A`, Lean constructs `Q = det T` and `H = adjugate T`, proves
`T H = Q I`, proves `Q(0) = 1`, and therefore constructs the inverse of `Q` in
the formal power-series ring.  The older coefficient-level certificate API is
retained below for compatibility with the enumerated `pathZeta` series.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.TransferZeta

open scoped BigOperators

universe u v

/--
A finite directed multigraph with positive integral edge weights.

Parallel edges are represented by distinct elements of `E`; consequently all
enumerations below retain their multiplicities without a separate multiplicity
field.
-/
structure PositiveWeightedMultigraph (V : Type u) (E : Type v) where
  source : E → V
  target : E → V
  weight : E → ℕ
  weight_pos : ∀ e, 0 < weight e

namespace PositiveWeightedMultigraph

variable {V : Type u} {E : Type v}

/-- The recursive endpoint condition for an ordered list of edges. -/
def IsWalk (G : PositiveWeightedMultigraph V E) (s t : V) : List E → Prop
  | [] => s = t
  | e :: es => G.source e = s ∧ G.IsWalk (G.target e) t es

/-- Endpoint validity is decidable on every finite edge tuple. -/
instance instDecidableIsWalk [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (es : List E) :
    Decidable (G.IsWalk s t es) := by
  induction es generalizing s with
  | nil =>
      change Decidable (s = t)
      infer_instance
  | cons e es ih =>
      change Decidable (G.source e = s ∧ G.IsWalk (G.target e) t es)
      exact instDecidableAnd

/-- Total weight of an ordered edge list. -/
def pathWeight (G : PositiveWeightedMultigraph V E) (es : List E) : ℕ :=
  (es.map G.weight).sum

@[simp] theorem pathWeight_nil (G : PositiveWeightedMultigraph V E) :
    G.pathWeight [] = 0 :=
  rfl

@[simp] theorem pathWeight_cons (G : PositiveWeightedMultigraph V E)
    (e : E) (es : List E) :
    G.pathWeight (e :: es) = G.weight e + G.pathWeight es :=
  rfl

/-- Positive edge weights bound the number of edges by cumulative weight. -/
theorem length_le_pathWeight (G : PositiveWeightedMultigraph V E) (es : List E) :
    es.length ≤ G.pathWeight es := by
  induction es with
  | nil => simp
  | cons e es ih =>
      calc
        (e :: es).length = 1 + es.length := by simp [Nat.add_comm]
        _ ≤ G.weight e + G.pathWeight es :=
          Nat.add_le_add (G.weight_pos e) ih
        _ = G.pathWeight (e :: es) := by simp

/-- A tuple carrying its length, with no a priori length bound. -/
abbrev EdgeTuple (E : Type v) := Σ r : ℕ, Fin r → E

/-- A tuple whose length is at most `n`. -/
abbrev BoundedEdgeTuple (E : Type v) (n : ℕ) :=
  Σ r : Fin (n + 1), Fin r.val → E

/-- Convert a bounded tuple to its ordered edge list. -/
def tupleEdges {n : ℕ} (x : BoundedEdgeTuple E n) : List E :=
  List.ofFn x.2

/--
The exact finite enumeration used for the coefficient of weight `n`.
-/
def walkTuplesAtWeight [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :
    Finset (BoundedEdgeTuple E n) :=
  Finset.univ.filter fun x ↦
    G.IsWalk s t (tupleEdges x) ∧ G.pathWeight (tupleEdges x) = n

/-- Membership in the finite enumerator has exactly the advertised meaning. -/
theorem mem_walkTuplesAtWeight_iff [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ)
    (x : BoundedEdgeTuple E n) :
    x ∈ G.walkTuplesAtWeight s t n ↔
      G.IsWalk s t (tupleEdges x) ∧ G.pathWeight (tupleEdges x) = n := by
  simp [walkTuplesAtWeight]

/-- The finite type whose elements are precisely the exact-weight walk tuples. -/
abbrev ExactWalkTuple [Fintype E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :=
  {x : BoundedEdgeTuple E n //
    G.IsWalk s t (tupleEdges x) ∧ G.pathWeight (tupleEdges x) = n}

/--
Independent semantic presentation: an exact walk is simply a finite edge list
with the required endpoints and total weight.  It carries no enumeration bound
in its definition.
-/
abbrev ExactWalk (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :=
  {es : List E // G.IsWalk s t es ∧ G.pathWeight es = n}

/-- Executable coefficient algorithm: enumerate, filter, and count. -/
def coefficientAlgorithm [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) : ℕ :=
  (G.walkTuplesAtWeight s t n).card

/-- The enumerator's cardinality is the cardinality of the exact semantic type. -/
theorem coefficientAlgorithm_correct [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :
    G.coefficientAlgorithm s t n = Fintype.card (G.ExactWalkTuple s t n) := by
  rw [coefficientAlgorithm, walkTuplesAtWeight, Fintype.card_subtype]

/--
Exact capture theorem for unrestricted finite tuples.  The forward direction
says every enumerated tuple is a walk of weight `n`; the reverse direction is
where positivity supplies the finite length bound.
-/
theorem tuple_captured_iff [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ)
    (x : EdgeTuple E) :
    (∃ y : BoundedEdgeTuple E n,
        y ∈ G.walkTuplesAtWeight s t n ∧ tupleEdges y = List.ofFn x.2) ↔
      G.IsWalk s t (List.ofFn x.2) ∧ G.pathWeight (List.ofFn x.2) = n := by
  constructor
  · rintro ⟨y, hy, hedge⟩
    have hp := (G.mem_walkTuplesAtWeight_iff s t n y).mp hy
    simpa [hedge] using hp
  · intro hx
    have hlength : x.1 ≤ n := by
      calc
        x.1 = (List.ofFn x.2).length := by simp
        _ ≤ G.pathWeight (List.ofFn x.2) := G.length_le_pathWeight _
        _ = n := hx.2
    let y : BoundedEdgeTuple E n :=
      ⟨⟨x.1, Nat.lt_succ_iff.mpr hlength⟩, x.2⟩
    refine ⟨y, ?_, rfl⟩
    exact (G.mem_walkTuplesAtWeight_iff s t n y).mpr (by simpa [y, tupleEdges] using hx)

/-- Forget the bounded-tuple representation and recover its semantic edge list. -/
def exactWalkTupleToList [Fintype E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ)
    (x : G.ExactWalkTuple s t n) : G.ExactWalk s t n :=
  ⟨tupleEdges x.1, x.2⟩

/--
Positive weights turn a semantic exact walk back into a bounded tuple.  This is
the constructive content behind finiteness of the unrestricted list model.
-/
def exactWalkListToTuple [Fintype E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ)
    (x : G.ExactWalk s t n) : G.ExactWalkTuple s t n := by
  have hlength : x.1.length ≤ n := by
    calc
      x.1.length ≤ G.pathWeight x.1 := G.length_le_pathWeight x.1
      _ = n := x.2.2
  let y : BoundedEdgeTuple E n :=
    ⟨⟨x.1.length, Nat.lt_succ_iff.mpr hlength⟩, x.1.get⟩
  refine ⟨y, ?_⟩
  simpa [y, tupleEdges, List.ofFn_get] using x.2

/-- Semantic lists survive the encode/decode round trip. -/
theorem exactWalkTupleToList_listToTuple [Fintype E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ)
    (x : G.ExactWalk s t n) :
    G.exactWalkTupleToList s t n (G.exactWalkListToTuple s t n x) = x := by
  apply Subtype.ext
  simp [exactWalkTupleToList, exactWalkListToTuple, tupleEdges, List.ofFn_get]

/-- Exact list-walks and exact bounded tuples are equivalent. -/
noncomputable def exactWalkEquiv [Fintype E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :
    G.ExactWalk s t n ≃ G.ExactWalkTuple s t n :=
  (Equiv.ofBijective (G.exactWalkTupleToList s t n) ⟨by
    intro x y hxy
    apply Subtype.ext
    rcases x with ⟨⟨⟨r, hr⟩, f⟩, hx⟩
    rcases y with ⟨⟨⟨q, hq⟩, g⟩, hy⟩
    have hlists : List.ofFn f = List.ofFn g := congrArg Subtype.val hxy
    have htuples : (⟨r, f⟩ : EdgeTuple E) = ⟨q, g⟩ :=
      List.equivSigmaTuple.symm.injective hlists
    cases htuples
    rfl, by
    intro x
    exact ⟨G.exactWalkListToTuple s t n x,
      G.exactWalkTupleToList_listToTuple s t n x⟩⟩).symm

/-- Positivity and the tuple equivalence make the unrestricted list model finite. -/
noncomputable instance instFintypeExactWalk [Fintype E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :
    Fintype (G.ExactWalk s t n) :=
  Fintype.ofEquiv (G.ExactWalkTuple s t n) (G.exactWalkEquiv s t n).symm

/-- The executable coefficient is the cardinality of the semantic list-walk type. -/
theorem coefficientAlgorithm_eq_card_exactWalk [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :
    G.coefficientAlgorithm s t n = Fintype.card (G.ExactWalk s t n) := by
  rw [G.coefficientAlgorithm_correct s t n]
  exact Fintype.card_congr (G.exactWalkEquiv s t n).symm

/-- Data of the unique possible empty exact walk. -/
abbrev EmptyExactWalk (s t : V) (n : ℕ) :=
  {_u : Unit // s = t ∧ n = 0}

/--
Data obtained by removing the first edge of a nonempty exact walk.  The tail is
again an unrestricted list; the endpoint and weight equations are explicit.
-/
abbrev FirstEdgeExactWalk (G : PositiveWeightedMultigraph V E)
    (s t : V) (n : ℕ) :=
  {p : E × List E //
    G.source p.1 = s ∧ G.IsWalk (G.target p.1) t p.2 ∧
      G.weight p.1 + G.pathWeight p.2 = n}

/--
Exact first-edge decomposition of semantic walks.  This is the combinatorial
source of the transfer recurrence: every walk is either the empty diagonal
walk, or a first edge followed by an exact tail, with no overlap.
-/
def exactWalkFirstEdgeEquiv (G : PositiveWeightedMultigraph V E)
    (s t : V) (n : ℕ) :
    G.ExactWalk s t n ≃ EmptyExactWalk s t n ⊕ G.FirstEdgeExactWalk s t n where
  toFun x := by
    rcases x with ⟨es, hes⟩
    cases es with
    | nil =>
        exact Sum.inl ⟨(), hes.1, hes.2.symm⟩
    | cons e es =>
        exact Sum.inr ⟨(e, es), hes.1.1, hes.1.2, hes.2⟩
  invFun x := by
    rcases x with h | h
    · exact ⟨[], ⟨h.2.1, h.2.2.symm⟩⟩
    · exact ⟨h.1.1 :: h.1.2, ⟨⟨h.2.1, h.2.2.1⟩, h.2.2.2⟩⟩
  left_inv x := by
    rcases x with ⟨es, hes⟩
    cases es <;> rfl
  right_inv x := by
    rcases x with h | h <;> rfl

/-- First-edge data reindexed by the remaining weight. -/
abbrev FirstEdgeTail (G : PositiveWeightedMultigraph V E)
    (s t : V) (n : ℕ) :=
  Σ e : E, {_x : G.ExactWalk (G.target e) t (n - G.weight e) //
    G.source e = s ∧ G.weight e ≤ n}

/-- Reindex first-edge data by the exact remaining weight `n - weight e`. -/
def firstEdgeTailEquiv (G : PositiveWeightedMultigraph V E)
    (s t : V) (n : ℕ) :
    G.FirstEdgeExactWalk s t n ≃ G.FirstEdgeTail s t n where
  toFun x := by
    rcases x with ⟨⟨e, es⟩, hsource, hwalk, hweight⟩
    have hle : G.weight e ≤ n := by
      exact Nat.le.intro hweight
    have hremaining : G.pathWeight es = n - G.weight e :=
      Nat.eq_sub_of_add_eq (by simpa [Nat.add_comm] using hweight)
    exact ⟨e, ⟨⟨es, hwalk, hremaining⟩, hsource, hle⟩⟩
  invFun x := by
    rcases x with ⟨e, ⟨⟨es, hwalk, hremaining⟩, hsource, hle⟩⟩
    exact ⟨(e, es), hsource, hwalk, by
      rw [hremaining]
      exact Nat.add_sub_of_le hle⟩
  left_inv x := by
    rcases x with ⟨⟨e, es⟩, hsource, hwalk, hweight⟩
    apply Subtype.ext
    rfl
  right_inv x := by
    rcases x with ⟨e, ⟨⟨es, hwalk, hweight⟩, hsource, hle⟩⟩
    apply Sigma.ext rfl
    apply heq_of_eq
    apply Subtype.ext
    apply Subtype.ext
    rfl

/-- First-edge data is finite because the edge set and every exact tail are finite. -/
noncomputable instance instFintypeFirstEdgeExactWalk
    [Fintype E] [DecidableEq V] (G : PositiveWeightedMultigraph V E)
    (s t : V) (n : ℕ) : Fintype (G.FirstEdgeExactWalk s t n) :=
  Fintype.ofEquiv (G.FirstEdgeTail s t n) (G.firstEdgeTailEquiv s t n).symm

/-- Cardinality of the possible empty-walk contribution. -/
theorem card_emptyExactWalk [DecidableEq V] (s t : V) (n : ℕ) :
    Fintype.card (EmptyExactWalk s t n) =
      if s = t ∧ n = 0 then 1 else 0 := by
  by_cases h : s = t ∧ n = 0 <;> simp [EmptyExactWalk, h]

/-- Cardinality of first-edge data as a finite sum over edges. -/
theorem card_firstEdgeExactWalk [Fintype E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :
    Fintype.card (G.FirstEdgeExactWalk s t n) =
      ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
        Fintype.card (G.ExactWalk (G.target e) t (n - G.weight e)) else 0 := by
  rw [Fintype.card_congr (G.firstEdgeTailEquiv s t n), Fintype.card_sigma]
  apply Finset.sum_congr rfl
  intro e _
  by_cases h : G.source e = s ∧ G.weight e ≤ n <;> simp [h]

/--
First-edge recurrence for the executable coefficients.  Unlike the old
rationality certificate, this is derived from the walk semantics and finite
edge data rather than assumed coefficientwise.
-/
theorem coefficientAlgorithm_firstEdge [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :
    G.coefficientAlgorithm s t n =
      (if s = t ∧ n = 0 then 1 else 0) +
        ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
          G.coefficientAlgorithm (G.target e) t (n - G.weight e) else 0 := by
  rw [G.coefficientAlgorithm_eq_card_exactWalk s t n,
    Fintype.card_congr (G.exactWalkFirstEdgeEquiv s t n), Fintype.card_sum,
    card_emptyExactWalk, G.card_firstEdgeExactWalk]
  congr 1
  apply Finset.sum_congr rfl
  intro e _
  by_cases h : G.source e = s ∧ G.weight e ≤ n
  · simp only [h]
    exact (G.coefficientAlgorithm_eq_card_exactWalk
      (G.target e) t (n - G.weight e)).symm
  · simp [h]

/-- Number of edges from `i` to `j` having exact weight `n`. -/
def edgeCoefficient [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (i j : V) (n : ℕ) : ℕ :=
  (Finset.univ.filter fun e ↦
    G.source e = i ∧ G.target e = j ∧ G.weight e = n).card

/-- Polynomial weighted adjacency matrix. -/
noncomputable def weightedAdjacency [Fintype E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) : Matrix V V (Polynomial ℤ) :=
  fun i j ↦ ∑ e : E,
    if G.source e = i ∧ G.target e = j then
      Polynomial.monomial (G.weight e) 1
    else 0

/--
Coefficient correctness for the polynomial adjacency matrix.  Because edges
are elements of a multigraph edge type, the cardinality counts parallel edges.
-/
theorem weightedAdjacency_coeff [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (i j : V) (n : ℕ) :
    (G.weightedAdjacency i j).coeff n = (G.edgeCoefficient i j n : ℤ) := by
  classical
  rw [weightedAdjacency, ← Polynomial.lcoeff_apply]
  rw [map_sum]
  simp only [Polynomial.lcoeff_apply]
  calc
    (∑ e : E, (if G.source e = i ∧ G.target e = j then
        Polynomial.monomial (G.weight e) 1 else 0 : Polynomial ℤ).coeff n) =
        ∑ e : E, if G.source e = i ∧ G.target e = j ∧ G.weight e = n
          then (1 : ℤ) else 0 := by
      apply Fintype.sum_congr
      intro e
      by_cases he : G.source e = i ∧ G.target e = j
      · simp [he, Polynomial.coeff_monomial]
      · have hfull : ¬(G.source e = i ∧ G.target e = j ∧ G.weight e = n) :=
          fun h ↦ he ⟨h.1, h.2.1⟩
        simp [he, hfull]
    _ = (G.edgeCoefficient i j n : ℤ) := by
      simp [edgeCoefficient]

/-- Positive weights make every adjacency entry have zero constant term. -/
theorem weightedAdjacency_coeff_zero [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (i j : V) :
    (G.weightedAdjacency i j).coeff 0 = 0 := by
  rw [G.weightedAdjacency_coeff i j 0]
  simp only [edgeCoefficient, Int.ofNat_eq_zero, Finset.card_eq_zero,
    Finset.filter_eq_empty_iff]
  intro e _ hs
  rcases hs with ⟨_, _, hw⟩
  exact (Nat.ne_of_gt (G.weight_pos e)) hw

/-- Formal `pathZeta` series whose coefficients are the certified unrestricted walk counts. -/
def pathZeta [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) : PowerSeries ℤ :=
  PowerSeries.mk fun n ↦ (G.coefficientAlgorithm s t n : ℤ)

/-- Coefficients of the formal zeta series are exactly the finite algorithm. -/
@[simp] theorem coeff_pathZeta [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) (n : ℕ) :
    PowerSeries.coeff n (G.pathZeta s t) = (G.coefficientAlgorithm s t n : ℤ) := by
  simp [pathZeta]

section FiniteTransferRationality

variable [Fintype E] [DecidableEq E] [Fintype V] [DecidableEq V]
  (G : PositiveWeightedMultigraph V E)

/-- Polynomial weighted adjacency included entrywise into `ℤ⟦X⟧`. -/
noncomputable def weightedAdjacencySeries : Matrix V V (PowerSeries ℤ) :=
  Polynomial.coeToPowerSeries.ringHom.mapMatrix G.weightedAdjacency

/-- The independently enumerated walk series assembled into a matrix. -/
def enumeratedPathZetaMatrix : Matrix V V (PowerSeries ℤ) :=
  fun s t ↦ G.pathZeta s t

/-- Multiplication by adjacency is an explicit finite sum over first edges. -/
theorem weightedAdjacencySeries_mul_enumeratedPathZetaMatrix_apply
    (s t : V) :
    (G.weightedAdjacencySeries * G.enumeratedPathZetaMatrix) s t =
      ∑ e : E, if G.source e = s then
        PowerSeries.X ^ G.weight e * G.pathZeta (G.target e) t else 0 := by
  classical
  have hadjacency (i k : V) :
      G.weightedAdjacencySeries i k =
        ∑ e : E, if G.source e = i ∧ G.target e = k then
          (PowerSeries.X : PowerSeries ℤ) ^ G.weight e else 0 := by
    rw [weightedAdjacencySeries, RingHom.mapMatrix_apply, Matrix.map_apply,
      weightedAdjacency, map_sum]
    apply Finset.sum_congr rfl
    intro e _
    by_cases h : G.source e = i ∧ G.target e = k <;>
      simp [h, ← PowerSeries.X_pow_eq]
  rw [Matrix.mul_apply]
  simp_rw [hadjacency, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro e _
  by_cases hs : G.source e = s
  · simp [hs, enumeratedPathZetaMatrix]
  · simp [hs]

/--
Coefficient of `A(X) Z(X)` as the finite first-edge tail sum.  The proof
expands the finite edge adjacency definition and uses monomial coefficient
extraction; it assumes no rationality identity.
-/
theorem coeff_weightedAdjacencySeries_mul_enumeratedPathZetaMatrix
    (s t : V) (n : ℕ) :
    PowerSeries.coeff n
        ((G.weightedAdjacencySeries * G.enumeratedPathZetaMatrix) s t) =
      ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
        (G.coefficientAlgorithm (G.target e) t (n - G.weight e) : ℤ) else 0 := by
  classical
  rw [G.weightedAdjacencySeries_mul_enumeratedPathZetaMatrix_apply s t, map_sum]
  apply Finset.sum_congr rfl
  intro e _
  by_cases hs : G.source e = s
  · simp [hs, PowerSeries.coeff_X_pow_mul']
  · simp [hs]

/--
Series form of the semantic first-edge recurrence:
`Z_enum = I + A(X) Z_enum`.
-/
theorem enumeratedPathZetaMatrix_eq_one_add_adjacency_mul :
    G.enumeratedPathZetaMatrix =
      1 + G.weightedAdjacencySeries * G.enumeratedPathZetaMatrix := by
  ext s t n
  change PowerSeries.coeff n (G.pathZeta s t) =
    PowerSeries.coeff n
      ((1 : Matrix V V (PowerSeries ℤ)) s t +
        (G.weightedAdjacencySeries * G.enumeratedPathZetaMatrix) s t)
  rw [G.coeff_pathZeta, map_add,
    G.coeff_weightedAdjacencySeries_mul_enumeratedPathZetaMatrix s t n]
  have hrec := congrArg Int.ofNat (G.coefficientAlgorithm_firstEdge s t n)
  by_cases hst : s = t
  · subst t
    by_cases hn : n = 0 <;>
      simpa [Matrix.one_apply, PowerSeries.coeff_one, hn] using hrec
  · simpa [Matrix.one_apply, PowerSeries.coeff_one, hst] using hrec

/-- The polynomial transfer matrix `I - A(X)` attached to the finite graph. -/
noncomputable def transferMatrix : Matrix V V (Polynomial ℤ) :=
  1 - G.weightedAdjacency

/-- The canonical denominator obtained from the finite transfer matrix. -/
noncomputable def transferDenominator : Polynomial ℤ :=
  Matrix.det G.transferMatrix

/-- The canonical numerator matrix obtained by taking the adjugate. -/
noncomputable def transferNumeratorMatrix : Matrix V V (Polynomial ℤ) :=
  Matrix.adjugate G.transferMatrix

/-- Entrywise canonical numerator for a source and target. -/
noncomputable def transferNumerator (s t : V) : Polynomial ℤ :=
  G.transferNumeratorMatrix s t

omit [DecidableEq E] in
/--
The adjugate identity is a finite, automatically generated rationality
certificate.  It has no coefficientwise walk-series hypothesis.
-/
theorem transferMatrix_mul_numerator :
    G.transferMatrix * G.transferNumeratorMatrix =
      G.transferDenominator • (1 : Matrix V V (Polynomial ℤ)) := by
  exact Matrix.mul_adjugate G.transferMatrix

omit [DecidableEq E] in
/-- The companion adjugate identity, with the factors reversed. -/
theorem transferNumerator_mul_transferMatrix :
    G.transferNumeratorMatrix * G.transferMatrix =
      G.transferDenominator • (1 : Matrix V V (Polynomial ℤ)) := by
  exact Matrix.adjugate_mul G.transferMatrix

/-- Evaluation at zero sends the weighted adjacency matrix to zero. -/
theorem constantCoeff_weightedAdjacency :
    Polynomial.constantCoeff.mapMatrix G.weightedAdjacency = 0 := by
  ext i j
  simp [RingHom.mapMatrix_apply, Matrix.map_apply,
    Polynomial.constantCoeff_apply, G.weightedAdjacency_coeff_zero]

/-- Consequently, evaluation at zero sends the transfer matrix to `I`. -/
theorem constantCoeff_transferMatrix :
    Polynomial.constantCoeff.mapMatrix G.transferMatrix =
      (1 : Matrix V V ℤ) := by
  ext i j
  by_cases hij : i = j <;>
    simp [transferMatrix, RingHom.mapMatrix_apply, Matrix.map_apply,
    Polynomial.constantCoeff_apply, G.weightedAdjacency_coeff_zero,
    Matrix.one_apply, hij]

/-- The determinant denominator is canonically normalized by `Q(0) = 1`. -/
theorem transferDenominator_coeff_zero :
    G.transferDenominator.coeff 0 = 1 := by
  change Polynomial.constantCoeff G.transferDenominator = 1
  rw [transferDenominator, RingHom.map_det, G.constantCoeff_transferMatrix,
    Matrix.det_one]

/-- In particular, the automatically generated polynomial denominator is nonzero. -/
theorem transferDenominator_ne_zero : G.transferDenominator ≠ 0 := by
  intro hzero
  have h : (0 : ℤ) = 1 := by
    simpa [hzero] using G.transferDenominator_coeff_zero
  exact Int.zero_ne_one h

/-- The canonical denominator becomes a unit in the formal power-series ring. -/
theorem transferDenominator_isUnit :
    IsUnit (G.transferDenominator : PowerSeries ℤ) := by
  rw [PowerSeries.isUnit_iff_constantCoeff, Polynomial.constantCoeff_coe,
    G.transferDenominator_coeff_zero]
  exact isUnit_one

/-- Explicit inverse of the normalized determinant in `ℤ〖X〗`. -/
noncomputable def transferDenominatorInverse : PowerSeries ℤ :=
  PowerSeries.invOfUnit (G.transferDenominator : PowerSeries ℤ) (1 : ℤˣ)

/-- The constructed series is a right inverse of the determinant denominator. -/
theorem transferDenominator_mul_inverse :
    (G.transferDenominator : PowerSeries ℤ) *
        G.transferDenominatorInverse = 1 := by
  apply PowerSeries.mul_invOfUnit
  simpa [Polynomial.constantCoeff_coe] using G.transferDenominator_coeff_zero

/-- The constructed series is also a left inverse. -/
theorem transferDenominator_inverse_mul :
    G.transferDenominatorInverse *
        (G.transferDenominator : PowerSeries ℤ) = 1 := by
  apply PowerSeries.invOfUnit_mul
  simpa [Polynomial.constantCoeff_coe] using G.transferDenominator_coeff_zero

/--
The canonical rational transfer series for an entry: `Q⁻¹ Hₛₜ`.  Both
`Q` and `H` are computed from the finite polynomial adjacency matrix.
-/
noncomputable def matrixPathZeta (s t : V) : PowerSeries ℤ :=
  G.transferDenominatorInverse * (G.transferNumerator s t : PowerSeries ℤ)

/-- Transfer matrix after entrywise inclusion into formal power series. -/
noncomputable def transferSeriesMatrix : Matrix V V (PowerSeries ℤ) :=
  Polynomial.coeToPowerSeries.ringHom.mapMatrix G.transferMatrix

omit [DecidableEq E] in
/-- The series transfer matrix is literally `I - A(X)`. -/
theorem transferSeriesMatrix_eq_one_sub_adjacency :
    G.transferSeriesMatrix = 1 - G.weightedAdjacencySeries := by
  rw [transferSeriesMatrix, transferMatrix, weightedAdjacencySeries, map_sub, map_one]

/-- The enumerated walk series solves `(I - A(X)) Z_enum = I`. -/
theorem transferSeriesMatrix_mul_enumeratedPathZetaMatrix :
    G.transferSeriesMatrix * G.enumeratedPathZetaMatrix = 1 := by
  rw [G.transferSeriesMatrix_eq_one_sub_adjacency, sub_mul, one_mul]
  exact sub_eq_iff_eq_add.mpr G.enumeratedPathZetaMatrix_eq_one_add_adjacency_mul

/-- All canonical rational entries assembled into one matrix. -/
noncomputable def matrixPathZetaMatrix : Matrix V V (PowerSeries ℤ) :=
  fun s t ↦ G.matrixPathZeta s t

omit [DecidableEq E] in
/-- The polynomial adjugate identity survives entrywise inclusion into `ℤ⟦X⟧`. -/
theorem transferSeriesMatrix_mul_adjugate :
    G.transferSeriesMatrix *
        Polynomial.coeToPowerSeries.ringHom.mapMatrix G.transferNumeratorMatrix =
      (G.transferDenominator : PowerSeries ℤ) •
        (1 : Matrix V V (PowerSeries ℤ)) := by
  calc
    _ = Polynomial.coeToPowerSeries.ringHom.mapMatrix
        (G.transferDenominator • (1 : Matrix V V (Polynomial ℤ))) := by
      simpa [transferSeriesMatrix] using congrArg
        (Polynomial.coeToPowerSeries.ringHom.mapMatrix)
        G.transferMatrix_mul_numerator
    _ = _ := by
      ext i j
      by_cases hij : i = j <;>
        simp [RingHom.mapMatrix_apply, Matrix.map_apply, hij]

omit [DecidableEq E] in
/-- The reversed adjugate identity after inclusion into `ℤ⟦X⟧`. -/
theorem adjugate_mul_transferSeriesMatrix :
    Polynomial.coeToPowerSeries.ringHom.mapMatrix G.transferNumeratorMatrix *
        G.transferSeriesMatrix =
      (G.transferDenominator : PowerSeries ℤ) •
        (1 : Matrix V V (PowerSeries ℤ)) := by
  calc
    _ = Polynomial.coeToPowerSeries.ringHom.mapMatrix
        (G.transferDenominator • (1 : Matrix V V (Polynomial ℤ))) := by
      simpa [transferSeriesMatrix] using congrArg
        (Polynomial.coeToPowerSeries.ringHom.mapMatrix)
        G.transferNumerator_mul_transferMatrix
    _ = _ := by
      ext i j
      by_cases hij : i = j <;>
        simp [RingHom.mapMatrix_apply, Matrix.map_apply, hij]

omit [DecidableEq E] in
/-- The canonical rational matrix is the scaled adjugate. -/
theorem matrixPathZetaMatrix_eq_scaled_adjugate :
    G.matrixPathZetaMatrix =
      G.transferDenominatorInverse •
        Polynomial.coeToPowerSeries.ringHom.mapMatrix G.transferNumeratorMatrix := by
  ext s t
  rfl

/--
The automatic series solves the finite first-step transfer equation
`(I - A(X)) Z(X) = I`.  This is the matrix form of the first-edge recurrence.
-/
theorem transferSeriesMatrix_mul_matrixPathZetaMatrix :
    G.transferSeriesMatrix * G.matrixPathZetaMatrix = 1 := by
  rw [G.matrixPathZetaMatrix_eq_scaled_adjugate, Matrix.mul_smul,
    G.transferSeriesMatrix_mul_adjugate]
  ext i j
  by_cases hij : i = j <;>
    simp [Matrix.one_apply, hij, G.transferDenominator_inverse_mul]

/-- The canonical rational matrix is also a left inverse of the transfer matrix. -/
theorem matrixPathZetaMatrix_mul_transferSeriesMatrix :
    G.matrixPathZetaMatrix * G.transferSeriesMatrix = 1 := by
  rw [G.matrixPathZetaMatrix_eq_scaled_adjugate, Matrix.smul_mul,
    G.adjugate_mul_transferSeriesMatrix]
  ext i j
  by_cases hij : i = j <;>
    simp [Matrix.one_apply, hij, G.transferDenominator_inverse_mul]

/--
Uniqueness of the transfer inverse identifies the independently enumerated
walk series with the determinant/adjugate construction.
-/
theorem enumeratedPathZetaMatrix_eq_matrixPathZetaMatrix :
    G.enumeratedPathZetaMatrix = G.matrixPathZetaMatrix := by
  calc
    G.enumeratedPathZetaMatrix = 1 * G.enumeratedPathZetaMatrix :=
      (Matrix.one_mul _).symm
    _ = (G.matrixPathZetaMatrix * G.transferSeriesMatrix) *
        G.enumeratedPathZetaMatrix := by
      rw [G.matrixPathZetaMatrix_mul_transferSeriesMatrix]
    _ = G.matrixPathZetaMatrix *
        (G.transferSeriesMatrix * G.enumeratedPathZetaMatrix) :=
      Matrix.mul_assoc _ _ _
    _ = G.matrixPathZetaMatrix * 1 := by
      rw [G.transferSeriesMatrix_mul_enumeratedPathZetaMatrix]
    _ = G.matrixPathZetaMatrix := Matrix.mul_one _

/-- Every enumerated `pathZeta` entry is the canonical finite-matrix entry. -/
theorem pathZeta_eq_matrixPathZeta (s t : V) :
    G.pathZeta s t = G.matrixPathZeta s t := by
  exact congrFun (congrFun G.enumeratedPathZetaMatrix_eq_matrixPathZetaMatrix s) t

/-- Explicit formula `Zₛₜ = det(I-A)⁻¹ adj(I-A)ₛₜ` in `ℤ⟦X⟧`. -/
theorem pathZeta_eq_inverse_mul_transferNumerator (s t : V) :
    G.pathZeta s t = G.transferDenominatorInverse *
      (G.transferNumerator s t : PowerSeries ℤ) := by
  rw [G.pathZeta_eq_matrixPathZeta s t]
  rfl

/-- Automatic rationality, now derived from finite graph data alone. -/
theorem transferDenominator_mul_matrixPathZeta (s t : V) :
    (G.transferDenominator : PowerSeries ℤ) * G.matrixPathZeta s t =
      (G.transferNumerator s t : PowerSeries ℤ) := by
  rw [matrixPathZeta, ← mul_assoc, G.transferDenominator_mul_inverse, one_mul]

/-- Canonical determinant/adjugate identity for the enumerated walk series `pathZeta`. -/
theorem transferDenominator_mul_pathZeta (s t : V) :
    (G.transferDenominator : PowerSeries ℤ) * G.pathZeta s t =
      (G.transferNumerator s t : PowerSeries ℤ) := by
  rw [G.pathZeta_eq_matrixPathZeta s t]
  exact G.transferDenominator_mul_matrixPathZeta s t

/--
The automatically generated determinant gives an eventual constant-coefficient
recurrence for the enumerated walk counts.
-/
theorem finite_graph_constant_coefficient_recurrence (s t : V)
    {n : ℕ} (hn : (G.transferNumerator s t).natDegree < n) :
    ∑ p ∈ Finset.HasAntidiagonal.antidiagonal n,
        G.transferDenominator.coeff p.1 *
          (G.coefficientAlgorithm s t p.2 : ℤ) = 0 := by
  have hcoeff := congrArg (PowerSeries.coeff n)
    (G.transferDenominator_mul_pathZeta s t)
  rw [PowerSeries.coeff_mul] at hcoeff
  simpa [Polynomial.coeff_eq_zero_of_natDegree_lt hn] using hcoeff

/--
Packaged certificate-free rationality theorem for the canonical matrix entry.
Unlike `certificate_explicit_rationality`, its only input is the finite graph.
-/
theorem finite_graph_matrix_rationality (s t : V) :
    ∃ P Q : Polynomial ℤ,
      Q.coeff 0 = 1 ∧ Q ≠ 0 ∧
        (Q : PowerSeries ℤ) * G.matrixPathZeta s t = (P : PowerSeries ℤ) := by
  exact ⟨G.transferNumerator s t, G.transferDenominator,
    G.transferDenominator_coeff_zero, G.transferDenominator_ne_zero,
    G.transferDenominator_mul_matrixPathZeta s t⟩

/--
Automatic rationality of the original enumerated `pathZeta`.  The numerator
and denominator are computed from the finite graph as an adjugate entry and
the determinant of `I - A(X)`; no coefficientwise rationality premise occurs.
-/
theorem finite_graph_pathZeta_rationality (s t : V) :
    ∃ P Q : Polynomial ℤ,
      Q.coeff 0 = 1 ∧ Q ≠ 0 ∧
        (Q : PowerSeries ℤ) * G.pathZeta s t = (P : PowerSeries ℤ) := by
  refine ⟨G.transferNumerator s t, G.transferDenominator,
    G.transferDenominator_coeff_zero, G.transferDenominator_ne_zero, ?_⟩
  exact G.transferDenominator_mul_pathZeta s t

/--
Direct traceability wrapper for the composite finite-graph transfer-zeta
theorem in Paper II: the finite coefficient algorithm counts semantic walks,
the coefficients satisfy the first-edge recurrence, and the canonical
determinant/adjugate data give the normalized rational identity.
-/
theorem finite_graph_transferZeta_trace (s t : V) :
    (∀ n : ℕ,
      G.coefficientAlgorithm s t n = Fintype.card (G.ExactWalk s t n)) ∧
    (∀ n : ℕ,
      G.coefficientAlgorithm s t n =
        (if s = t ∧ n = 0 then 1 else 0) +
          ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
            G.coefficientAlgorithm (G.target e) t (n - G.weight e) else 0) ∧
    G.transferDenominator.coeff 0 = 1 ∧
    G.transferDenominator ≠ 0 ∧
    (G.transferDenominator : PowerSeries ℤ) * G.pathZeta s t =
      (G.transferNumerator s t : PowerSeries ℤ) := by
  exact ⟨G.coefficientAlgorithm_eq_card_exactWalk s t,
    G.coefficientAlgorithm_firstEdge s t,
    G.transferDenominator_coeff_zero,
    G.transferDenominator_ne_zero,
    G.transferDenominator_mul_pathZeta s t⟩

omit [Fintype V] in
/--
Direct traceability wrapper for the path-zeta algorithm row.  For each target
weight it records both semantic correctness of the returned cardinality and
the first-edge recurrence used by the subsequent matrix construction.
-/
theorem pathZetaAlgorithm_trace (s t : V) (n : ℕ) :
    G.coefficientAlgorithm s t n = Fintype.card (G.ExactWalk s t n) ∧
    G.coefficientAlgorithm s t n =
      (if s = t ∧ n = 0 then 1 else 0) +
        ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
          G.coefficientAlgorithm (G.target e) t (n - G.weight e) else 0 := by
  exact ⟨G.coefficientAlgorithm_eq_card_exactWalk s t n,
    G.coefficientAlgorithm_firstEdge s t n⟩

end FiniteTransferRationality

/--
An explicit rationality certificate.  Its final field is a coefficient-level
identity, so checking the certificate never invokes a symbolic matrix inverse.
-/
structure RationalCertificate [Fintype E] [DecidableEq E] [DecidableEq V]
    (G : PositiveWeightedMultigraph V E) (s t : V) where
  numerator : Polynomial ℤ
  denominator : Polynomial ℤ
  denominator_constant : denominator.coeff 0 = 1
  coefficient_identity : ∀ n : ℕ,
    ∑ p ∈ Finset.HasAntidiagonal.antidiagonal n,
        denominator.coeff p.1 * (G.coefficientAlgorithm s t p.2 : ℤ) =
      numerator.coeff n

namespace RationalCertificate

variable [Fintype E] [DecidableEq E] [DecidableEq V]
  {G : PositiveWeightedMultigraph V E} {s t : V}

/-- Normalization at zero forces the certified denominator to be nonzero. -/
theorem denominator_ne_zero (c : RationalCertificate G s t) :
    c.denominator ≠ 0 := by
  intro hzero
  have h : (0 : ℤ) = 1 := by
    simpa [hzero] using c.denominator_constant
  exact Int.zero_ne_one h

/-- The coefficient certificate checks the formal identity `Q Z = P`. -/
theorem mul_pathZeta_eq (c : RationalCertificate G s t) :
    (c.denominator : PowerSeries ℤ) * G.pathZeta s t =
      (c.numerator : PowerSeries ℤ) := by
  ext n
  rw [PowerSeries.coeff_mul]
  simpa using c.coefficient_identity n

/--
Certificate-explicit rationality: a supplied certificate yields normalized,
nonzero `Q` and the exact formal identity `Q Z = P`.
-/
theorem certificate_explicit_rationality (c : RationalCertificate G s t) :
    ∃ P Q : Polynomial ℤ,
      Q.coeff 0 = 1 ∧ Q ≠ 0 ∧
        (Q : PowerSeries ℤ) * G.pathZeta s t = (P : PowerSeries ℤ) := by
  exact ⟨c.numerator, c.denominator, c.denominator_constant,
    c.denominator_ne_zero, c.mul_pathZeta_eq⟩

/--
After the numerator's finite initial range, the walk counts obey the constant-
coefficient recurrence encoded by the certified denominator.
-/
theorem constant_coefficient_recurrence (c : RationalCertificate G s t)
    {n : ℕ} (hn : c.numerator.natDegree < n) :
    ∑ p ∈ Finset.HasAntidiagonal.antidiagonal n,
        c.denominator.coeff p.1 * (G.coefficientAlgorithm s t p.2 : ℤ) = 0 := by
  rw [c.coefficient_identity n]
  exact Polynomial.coeff_eq_zero_of_natDegree_lt hn

end RationalCertificate

end PositiveWeightedMultigraph

end Komorebi.PaperII.TransferZeta
