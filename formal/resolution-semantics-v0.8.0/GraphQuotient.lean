import GraphEdgeSpace

/-! The actual additive quotient of edge fields by the derivative image. -/

namespace KRS.Graph

variable {n : Nat}

def cutSetoid (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : Setoid (EdgeBits G) where
  r := fun r s => bitXor r s ∈ cutFields G
  iseqv := {
    refl := by
      intro r
      rw [bit_xor_self]
      exact (cut_fields_complete G _).mpr ⟨fun _ => false, derivative_zero G⟩
    symm := by
      intro r s h
      simpa only [bit_xor_comm] using h
    trans := by
      intro r s t hrs hst
      obtain ⟨a, ha⟩ := (cut_fields_complete G _).mp hrs
      obtain ⟨b, hb⟩ := (cut_fields_complete G _).mp hst
      apply (cut_fields_complete G _).mpr
      refine ⟨bitXor a b, ?_⟩
      rw [derivative_xor, ha, hb]
      funext i
      simp only [bitXor]
      cases r i <;> cases s i <;> cases t i <;> rfl }

abbrev EdgeQuotient (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] := Quotient (cutSetoid G)

def edgeClass (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (r : EdgeBits G) :
    EdgeQuotient G := Quotient.mk (cutSetoid G) r

instance edgeQuotientDecidableEq (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    DecidableEq (EdgeQuotient G) :=
  let cuts := cutFields G
  @Quotient.decidableEq _ (cutSetoid G) (fun r s =>
    inferInstanceAs (Decidable (bitXor r s ∈ cuts)))

theorem edge_class_eq_iff (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (r s : EdgeBits G) :
    edgeClass G r = edgeClass G s ↔ bitXor r s ∈ cutFields G :=
  ⟨fun h => @Quotient.exact _ (cutSetoid G) r s h,
   fun h => @Quotient.sound _ (cutSetoid G) r s h⟩

def quotientClasses (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : List (EdgeQuotient G) :=
  distinctValues ((assignments (edgeCount G)).map (edgeClass G))

theorem quotient_classes_nodup (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    (quotientClasses G).Nodup := distinct_values_nodup _

theorem quotient_classes_complete (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (q : EdgeQuotient G) : q ∈ quotientClasses G := by
  obtain ⟨r, rfl⟩ := Quotient.exists_rep q
  apply (distinct_values_complete _ _).mpr
  exact List.mem_map.mpr ⟨r, assignments_complete _ r, rfl⟩

theorem bit_xor_injective {k : Nat} (r : Fin k → Bool) : Function.Injective (bitXor r) := by
  intro a b h
  have hh := congrArg (bitXor r) h
  simpa only [bit_xor_cancel] using hh

theorem quotient_fiber_count (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (q : EdgeQuotient G) :
    ((assignments (edgeCount G)).filter (fun r => edgeClass G r == q)).length =
      (cutFields G).length := by
  obtain ⟨r, rfl⟩ := Quotient.exists_rep q
  change ((assignments (edgeCount G)).filter (fun s => edgeClass G s == edgeClass G r)).length = _
  rw [← List.length_map (f := bitXor r) (as := cutFields G)]
  apply same_members_length
  · exact List.Pairwise.filter _ (assignments_nodup _)
  · exact nodup_map_injective _ (bit_xor_injective r) _ (cut_fields_nodup G)
  · intro s
    simp only [List.mem_filter, assignments_complete, true_and, beq_iff_eq,
      edge_class_eq_iff, List.mem_map]
    constructor
    · intro hs
      refine ⟨bitXor r s, ?_, bit_xor_cancel r s⟩
      simpa only [bit_xor_comm] using hs
    · rintro ⟨a, ha, rfl⟩
      have heq : bitXor (bitXor r a) r = a := by
        rw [bit_xor_comm (bitXor r a) r, bit_xor_cancel]
      simpa only [heq] using ha

theorem quotient_partition (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    2 ^ edgeCount G = (quotientClasses G).length * (cutFields G).length := by
  rw [← assignments_length]
  apply constant_fiber_count _ _ (edgeClass G) (quotient_classes_nodup G)
  · intro r _
    exact quotient_classes_complete G (edgeClass G r)
  · intro q _
    exact quotient_fiber_count G q

theorem quotient_xor_respects (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r r' s s' : EdgeBits G) (hr : (cutSetoid G).r r r')
    (hs : (cutSetoid G).r s s') :
    (cutSetoid G).r (bitXor r s) (bitXor r' s') := by
  obtain ⟨a, ha⟩ := (cut_fields_complete G _).mp hr
  obtain ⟨b, hb⟩ := (cut_fields_complete G _).mp hs
  apply (cut_fields_complete G _).mpr
  refine ⟨bitXor a b, ?_⟩
  rw [derivative_xor, ha, hb]
  funext i
  simp only [bitXor]
  cases r i <;> cases r' i <;> cases s i <;> cases s' i <;> rfl

def quotientXor (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (q p : EdgeQuotient G) : EdgeQuotient G :=
  Quotient.liftOn₂ q p (fun r s => edgeClass G (bitXor r s))
    (fun r s r' s' hr hs => Quotient.sound (quotient_xor_respects G r r' s s' hr hs))

theorem quotient_xor_self (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (q : EdgeQuotient G) : quotientXor G q q = edgeClass G (fun _ => false) := by
  refine Quotient.inductionOn q ?_
  intro r
  change edgeClass G (bitXor r r) = _
  rw [bit_xor_self]

theorem quotient_xor_zero (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (q : EdgeQuotient G) : quotientXor G q (edgeClass G (fun _ => false)) = q := by
  refine Quotient.inductionOn q ?_
  intro r
  change edgeClass G (bitXor r (fun _ => false)) = _
  rw [bit_xor_zero]
  rfl

theorem quotient_xor_comm (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (q p : EdgeQuotient G) : quotientXor G q p = quotientXor G p q := by
  refine Quotient.inductionOn₂ q p ?_
  intro r s
  change edgeClass G (bitXor r s) = edgeClass G (bitXor s r)
  rw [bit_xor_comm]

theorem quotient_xor_assoc (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (q p t : EdgeQuotient G) :
    quotientXor G (quotientXor G q p) t = quotientXor G q (quotientXor G p t) := by
  refine Quotient.inductionOn q ?_
  intro r
  refine Quotient.inductionOn₂ p t ?_
  intro s u
  change edgeClass G (bitXor (bitXor r s) u) = edgeClass G (bitXor r (bitXor s u))
  rw [bit_xor_assoc]

end KRS.Graph
