import KomorebiVerification.PaperII.ReleaseFiltered
import Mathlib.Data.Fintype.Card

/-! # Packet-supported word and path expansions

Words here use written multiplication order. `IsPath s t word` reads that
word from right to left, so it describes the directed path from `s` to `t`
whose chronological edge list is `word.reverse`. This is precisely the
reversal convention stated in the manuscript.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.ReleaseFilteredPaths

open scoped BigOperators
open Komorebi.PaperII.WeightedTransfer
open Komorebi.PaperII.ReleaseFiltered

universe u v w

/-- Finite packet idempotents and supported normalized transfer edges. -/
structure PacketTransfer (R : Type u) [Ring R] (V : Type v) (E : Type w)
    [Fintype V] [DecidableEq V] where
  packet : V → R
  packet_mul : ∀ i j, packet i * packet j = if i = j then packet i else 0
  packet_sum : ∑ i, packet i = 1
  source : E → V
  target : E → V
  edge : E → R
  left_support : ∀ e, packet (target e) * edge e = edge e
  right_support : ∀ e, edge e * packet (source e) = edge e

namespace PacketTransfer

variable {R : Type u} [Ring R] {V : Type v} {E : Type w}
  [Fintype V] [DecidableEq V] (G : PacketTransfer R V E)

/-- Endpoint compatibility in written multiplication order. -/
def IsPath (G : PacketTransfer R V E) (s t : V) : List E → Prop
  | [] => s = t
  | e :: es => G.target e = t ∧ G.IsPath s (G.source e) es

instance instDecidableIsPath (s t : V) (es : List E) : Decidable (G.IsPath s t es) := by
  induction es generalizing t with
  | nil => change Decidable (s = t); infer_instance
  | cons e es ih =>
      change Decidable (G.target e = t ∧ G.IsPath s (G.source e) es)
      exact instDecidableAnd

theorem packet_mul_edge (t : V) (e : E) :
    G.packet t * G.edge e = if G.target e = t then G.edge e else 0 := by
  rw [← G.left_support e, ← mul_assoc, G.packet_mul]
  by_cases h : G.target e = t
  · subst t
    simp only [↓reduceIte, G.left_support]
  · have ht : t ≠ G.target e := Ne.symm h
    simp only [ht, h, ↓reduceIte, zero_mul]

/-- Every incompatible word vanishes in the sandwiched block, while a compatible
word retains the chronological path product (and the source projection). -/
theorem block_word_eq (s t : V) (word : List E) :
    G.packet t * wordProduct G.edge word * G.packet s =
      if G.IsPath s t word then wordProduct G.edge word * G.packet s else 0 := by
  induction word generalizing t with
  | nil =>
      simp only [wordProduct_nil, mul_one, one_mul, IsPath, G.packet_mul]
      by_cases h : s = t
      · subst t; simp
      · simp [h, Ne.symm h]
  | cons e es ih =>
      rw [wordProduct_cons, ← mul_assoc (G.packet t), G.packet_mul_edge]
      by_cases ht : G.target e = t
      · simp only [ht, ↓reduceIte]
        have hid : G.edge e * wordProduct G.edge es * G.packet s =
            G.edge e * (G.packet (G.source e) * wordProduct G.edge es * G.packet s) := by
          simp only [← mul_assoc, G.right_support]
        rw [hid, ih]
        by_cases hp : G.IsPath s (G.source e) es
        · simp only [hp, ↓reduceIte, IsPath, ht, and_self]
        · simp only [hp, ↓reduceIte, IsPath, ht, and_false, mul_zero]
      · simp only [ht, ↓reduceIte, zero_mul, IsPath, false_and]

/-- The signed finite path sum at a fixed weight and length cutoff. -/
def pathInverse [Fintype E] (weight : E → ℕ) (s t : V) (L N : ℕ) : R :=
  ∑ n ∈ Finset.range N, (-1 : R) ^ n *
    ∑ word : Fin n → E with
      wordWeight weight (List.ofFn word) < L ∧ G.IsPath s t (List.ofFn word),
      wordProduct G.edge (List.ofFn word) * G.packet s

/-- Filtering the explicit finite inverse by endpoints is exactly taking its
packet block; the assertion is algebraic and needs no completeness. -/
theorem block_pruned_eq_pathInverse [Fintype E]
    (weight : E → ℕ) (s t : V) (L N : ℕ) :
    G.packet t * prunedWordInverse weight G.edge L N * G.packet s =
      G.pathInverse weight s t L N := by
  classical
  simp only [prunedWordInverse, pathInverse, Finset.mul_sum, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro n _
  have hcentral : G.packet t * (-1 : R) ^ n = (-1 : R) ^ n * G.packet t := by
    exact (Commute.neg_one_right (G.packet t)).pow_right n
  rw [← mul_assoc, hcentral, mul_assoc, mul_assoc]
  simp only [retainedFixedWordSum, Finset.sum_filter, Finset.mul_sum, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro word _
  by_cases hw : wordWeight weight (List.ofFn word) < L
  · simp only [hw, ↓reduceIte, true_and]
    simpa only [mul_assoc, mul_ite, mul_zero] using
      congrArg (fun x : R ↦ (-1 : R) ^ n * x)
        (G.block_word_eq s t (List.ofFn word))
  · simp only [hw, ↓reduceIte, false_and, mul_zero, zero_mul]

/-- Completed packet block formula: at every depth it is exactly the finite
sum over compatible retained paths modulo that depth. -/
theorem complete_block_path_formula [Fintype E]
    (F : IdealFiltration R) (hF : F.Complete)
    (weight : E → ℕ) (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, F.Mem (weight e) (G.edge e)) :
    ∃ S : R, TwoSidedInverse (1 + ∑ e : E, G.edge e) S ∧
      ∀ s t L, F.Mem L
        (G.packet t * S * G.packet s - G.pathInverse weight s t L L) := by
  obtain ⟨S, hS, hcong⟩ := F.exists_weighted_inverse hF weight G.edge hpositive hedge
  refine ⟨S, hS, ?_⟩
  intro s t L
  have h := F.right_mem (F.left_mem (G.packet t) (hcong L)) (G.packet s)
  simpa only [mul_sub, sub_mul, G.block_pruned_eq_pathInverse] using h

/-- If every valid path has weight at least `d`, every retained block candidate
has that same lower filtration bound. -/
theorem pathInverse_mem [Fintype E]
    (F : IdealFiltration R) (weight : E → ℕ)
    (hedge : ∀ e, F.Mem (weight e) (G.edge e)) (s t : V) (d L N : ℕ)
    (hmin : ∀ word : List E, G.IsPath s t word → d ≤ wordWeight weight word) :
    F.Mem d (G.pathInverse weight s t L N) := by
  classical
  unfold pathInverse
  apply F.sum_mem
  intro n _
  apply F.left_mem
  apply F.sum_mem
  intro word hw
  have hpath := (Finset.mem_filter.mp hw).2.2
  apply F.right_mem
  exact F.antitone (hmin _ hpath)
    (F.toMultiplicativeFiltration.wordProduct_mem weight G.edge hedge _)

/-- The minimum-path filtration bound follows by reducing the completed
formula at that depth. -/
theorem minimum_path_weight [Fintype E]
    (F : IdealFiltration R) (weight : E → ℕ)
    (hedge : ∀ e, F.Mem (weight e) (G.edge e)) (S : R)
    (hcong : ∀ s t L, F.Mem L
      (G.packet t * S * G.packet s - G.pathInverse weight s t L L))
    (s t : V) (d : ℕ)
    (hmin : ∀ word : List E, G.IsPath s t word → d ≤ wordWeight weight word) :
    F.Mem d (G.packet t * S * G.packet s) := by
  have h := F.add_mem (hcong s t d) (G.pathInverse_mem F weight hedge s t d d d hmin)
  simpa only [sub_add_cancel] using h

/-- No directed path means the completed block is zero. -/
theorem no_path_block_zero [Fintype E]
    (F : IdealFiltration R) (hF : F.Complete) (weight : E → ℕ)
    (hedge : ∀ e, F.Mem (weight e) (G.edge e)) (S : R)
    (hcong : ∀ s t L, F.Mem L
      (G.packet t * S * G.packet s - G.pathInverse weight s t L L))
    (s t : V) (hno : ∀ word : List E, ¬ G.IsPath s t word) :
    G.packet t * S * G.packet s = 0 := by
  apply F.separated hF
  intro d
  exact G.minimum_path_weight F weight hedge S hcong s t d
    (by intro word hp; exact False.elim (hno word hp))



/-- The vertices encountered from target back to source in written order. -/
def vertices (G : PacketTransfer R V E) (t : V) : List E → List V
  | [] => [t]
  | e :: es => t :: G.vertices (G.source e) es

@[simp] theorem vertices_length (t : V) (word : List E) :
    (G.vertices t word).length = word.length + 1 := by
  induction word generalizing t with
  | nil => rfl
  | cons e es ih => simp only [vertices, List.length_cons, ih]

/-- A visited vertex splits a path into two valid subpaths. -/
theorem path_cut_of_vertex_mem (s t v : V) (word : List E)
    (hp : G.IsPath s t word) (hv : v ∈ G.vertices t word) :
    ∃ front back : List E, word = front ++ back ∧
      G.IsPath v t front ∧ G.IsPath s v back := by
  induction word generalizing t with
  | nil =>
      have hvt : v = t := by simpa only [vertices, List.mem_singleton] using hv
      subst v
      exact ⟨[], [], rfl, rfl, hp⟩
  | cons e es ih =>
      rcases hp with ⟨ht, htail⟩
      rcases List.mem_cons.mp hv with hvt | hv
      · subst v
        exact ⟨[], e :: es, rfl, rfl, ⟨ht, htail⟩⟩
      · obtain ⟨front, back, heq, hfront, hback⟩ := ih (G.source e) htail hv
        refine ⟨e :: front, back, ?_, ⟨ht, hfront⟩, hback⟩
        simp only [List.cons_append, heq]

/-- Acyclicity excludes every nonempty closed directed path. -/
def Acyclic : Prop := ∀ v (word : List E), word ≠ [] → ¬ G.IsPath v v word

/-- An acyclic path cannot repeat a vertex. -/
theorem vertices_nodup (hacyc : G.Acyclic) (s t : V) (word : List E)
    (hp : G.IsPath s t word) : (G.vertices t word).Nodup := by
  induction word generalizing t with
  | nil => simp [vertices]
  | cons e es ih =>
      rcases hp with ⟨ht, htail⟩
      apply List.nodup_cons.mpr
      constructor
      · intro hv
        obtain ⟨front, back, _, hfront, _⟩ :=
          G.path_cut_of_vertex_mem s (G.source e) t es htail hv
        exact hacyc t (e :: front) (by simp) ⟨ht, hfront⟩
      · exact ih (G.source e) htail

/-- The number of edges of a path in a finite acyclic graph is strictly less
than the number of vertices. -/
theorem path_length_lt_card (hacyc : G.Acyclic) (s t : V) (word : List E)
    (hp : G.IsPath s t word) : word.length < Fintype.card V := by
  have h := (G.vertices_nodup hacyc s t word hp).length_le_card
  rw [G.vertices_length] at h
  exact Nat.lt_of_succ_le h

/-- If every packet block is zero, the operator itself is zero. -/
theorem eq_zero_of_blocks (x : R) (h : ∀ s t, G.packet t * x * G.packet s = 0) : x = 0 := by
  have hl (t : V) : G.packet t * x = 0 := by
    calc
      G.packet t * x = (G.packet t * x) * (∑ s, G.packet s) := by rw [G.packet_sum, mul_one]
      _ = ∑ s, G.packet t * x * G.packet s := Finset.mul_sum _ _ _
      _ = 0 := by simp only [h, Finset.sum_const_zero]
  calc
    x = (∑ t, G.packet t) * x := by rw [G.packet_sum, one_mul]
    _ = ∑ t, G.packet t * x := Finset.sum_mul _ _ _
    _ = 0 := by simp only [hl, Finset.sum_const_zero]

/-- Acyclic supported transfer is nilpotent over any ring. Neither positive
weights nor a complete filtration is required for this conclusion. -/
theorem acyclic_nilpotent [Fintype E] (hacyc : G.Acyclic) :
    (∑ e : E, G.edge e) ^ Fintype.card V = 0 := by
  apply G.eq_zero_of_blocks
  intro s t
  rw [← sum_fixedWordProduct_eq_pow]
  simp only [Finset.mul_sum, Finset.sum_mul]
  apply Finset.sum_eq_zero
  intro word _
  rw [G.block_word_eq]
  have hno : ¬ G.IsPath s t (List.ofFn word) := by
    intro hp
    have h := G.path_length_lt_card hacyc s t (List.ofFn word) hp
    simp only [List.length_ofFn, lt_self_iff_false] at h
  simp only [hno, ↓reduceIte]

/-- The inverse in an acyclic graph is a finite sum in the original ring. -/
theorem acyclic_finite_inverse [Fintype E] (hacyc : G.Acyclic) :
    TwoSidedInverse (1 + ∑ e : E, G.edge e)
      (finiteGeometricInverse (∑ e : E, G.edge e) (Fintype.card V)) :=
  finiteGeometricInverse_spec_of_pow_eq_zero _ _ (G.acyclic_nilpotent hacyc)

/-- Packet diagonality expressed by commutation with every packet. -/
def IsDiagonal (D : R) : Prop := ∀ i, G.packet i * D = D * G.packet i

/-- An inverse of a packet-diagonal unit is packet diagonal. -/
theorem inverse_diagonal (D Dinv : R) (hD : TwoSidedInverse D Dinv)
    (hdiag : G.IsDiagonal D) : G.IsDiagonal Dinv := by
  intro i
  calc
    G.packet i * Dinv = (Dinv * D) * (G.packet i * Dinv) := by rw [hD.left_inv, one_mul]
    _ = Dinv * (D * G.packet i) * Dinv := by simp only [mul_assoc]
    _ = Dinv * (G.packet i * D) * Dinv := by rw [← hdiag i]
    _ = Dinv * G.packet i := by simp only [mul_assoc, hD.right_inv, mul_one]

/-- Normalizing a supported transfer by a packet-diagonal inverse preserves
its two endpoints. -/
def normalized (Dinv : R) (hdiag : G.IsDiagonal Dinv) : PacketTransfer R V E where
  packet := G.packet
  packet_mul := G.packet_mul
  packet_sum := G.packet_sum
  source := G.source
  target := G.target
  edge := fun e ↦ Dinv * G.edge e
  left_support e := by
    rw [← mul_assoc, hdiag, mul_assoc, G.left_support]
  right_support e := by
    rw [mul_assoc, G.right_support]

/-- The packet-diagonal formula in the manuscript implies commutation. -/
theorem diagonal_of_block_sum (D : R)
    (hD : D = ∑ i, G.packet i * D * G.packet i) : G.IsDiagonal D := by
  intro j
  have hl : G.packet j * D = G.packet j * D * G.packet j := by
    conv_lhs => rw [hD]
    rw [Finset.mul_sum]
    simp only [← mul_assoc, G.packet_mul]
    simp
  have hr : D * G.packet j = G.packet j * D * G.packet j := by
    conv_lhs => rw [hD]
    rw [Finset.sum_mul]
    simp only [mul_assoc, G.packet_mul]
    simp
  exact hl.trans hr.symm

/-- The full diagonal-plus-transfer packet path formula at every precision.
The candidate includes the source corner of `Dinv` at its right endpoint. -/
theorem complete_diagonal_block_path_formula [Fintype E]
    (F : IdealFiltration R) (hF : F.Complete)
    (D Dinv : R) (hD : TwoSidedInverse D Dinv) (hdiag : G.IsDiagonal D)
    (weight : E → ℕ) (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, F.Mem (weight e) (G.edge e)) :
    let Gnorm := G.normalized Dinv (G.inverse_diagonal D Dinv hD hdiag)
    ∃ Tinv : R, TwoSidedInverse (D + ∑ e : E, G.edge e) Tinv ∧
      ∀ s t L, F.Mem L (G.packet t * Tinv * G.packet s -
        Gnorm.pathInverse weight s t L L * Dinv) := by
  dsimp only
  let Gnorm := G.normalized Dinv (G.inverse_diagonal D Dinv hD hdiag)
  have hnorm : ∀ e, F.Mem (weight e) (Gnorm.edge e) :=
    fun e ↦ F.left_mem Dinv (hedge e)
  obtain ⟨S, hS, hcong⟩ := Gnorm.complete_block_path_formula F hF weight hpositive hnorm
  have hsum : Dinv * (∑ e : E, G.edge e) = ∑ e : E, Gnorm.edge e := by
    simp only [Gnorm, normalized, Finset.mul_sum]
  have hSn : TwoSidedInverse (1 + Dinv * ∑ e : E, G.edge e) S := by
    simpa only [hsum] using hS
  refine ⟨S * Dinv, IdealFiltration.diagonal_inverse D Dinv _ S hD hSn, ?_⟩
  intro s t L
  have h := F.right_mem (hcong s t L) Dinv
  have hd : Dinv * G.packet s = G.packet s * Dinv :=
    (G.inverse_diagonal D Dinv hD hdiag s).symm
  have he : G.packet t * (S * Dinv) * G.packet s =
      (G.packet t * S * G.packet s) * Dinv := by
    simp only [mul_assoc, hd]
  rw [he]
  simpa only [sub_mul, Gnorm, normalized] using h

end PacketTransfer
end Komorebi.PaperII.ReleaseFilteredPaths
