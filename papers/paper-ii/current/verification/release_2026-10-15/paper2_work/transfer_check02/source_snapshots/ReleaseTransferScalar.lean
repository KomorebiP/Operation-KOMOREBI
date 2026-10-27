import KomorebiVerification.PaperII.TransferZeta

/-!
Scalar-weighted semantic walks. The finite walk type is the original unrestricted
list model with its proved finite enumeration. Products below retain every edge
occurrence, including parallel edges and repeated visits.
-/
set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseTransferScalar
open TransferZeta TransferZeta.PositiveWeightedMultigraph
universe u v w
variable {V : Type u} {E : Type v} {R : Type w}
variable [Fintype E] [DecidableEq V] [CommRing R]
variable (G : PositiveWeightedMultigraph V E) (m : E → R)

def walkMultiplicity (es : List E) : R := (es.map m).prod

omit [Fintype E] in
@[simp] theorem walkMultiplicity_nil : walkMultiplicity m [] = 1 := rfl
omit [Fintype E] in
@[simp] theorem walkMultiplicity_cons (e : E) (es : List E) :
    walkMultiplicity m (e :: es) = m e * walkMultiplicity m es := rfl

noncomputable def coefficient (s t : V) (n : ℕ) : R :=
  ∑ x : G.ExactWalk s t n, walkMultiplicity m x.val

theorem coefficient_firstEdge (s t : V) (n : ℕ) :
    coefficient G m s t n = (if s = t ∧ n = 0 then 1 else 0) +
      ∑ e : E, if G.source e = s ∧ G.weight e ≤ n then
        m e * coefficient G m (G.target e) t (n - G.weight e) else 0 := by
  classical
  let f : EmptyExactWalk s t n ⊕ G.FirstEdgeExactWalk s t n → R :=
    Sum.elim (fun _ ↦ 1) (fun x ↦ m x.val.1 * walkMultiplicity m x.val.2)
  have hfirst : coefficient G m s t n = ∑ x, f x := by
    apply Fintype.sum_equiv (G.exactWalkFirstEdgeEquiv s t n)
    intro x
    rcases x with ⟨es, hx⟩
    cases es <;> rfl
  rw [hfirst, Fintype.sum_sum_type]
  have hempty : (∑ _x : EmptyExactWalk s t n, (1 : R)) =
      if s = t ∧ n = 0 then 1 else 0 := by
    by_cases h : s = t ∧ n = 0 <;> simp [EmptyExactWalk, h]
  change (∑ _x : EmptyExactWalk s t n, (1 : R)) +
    (∑ x : G.FirstEdgeExactWalk s t n, m x.val.1 * walkMultiplicity m x.val.2) = _
  rw [hempty]
  congr 1
  calc
    _ = ∑ x : G.FirstEdgeTail s t n,
          m x.1 * walkMultiplicity m x.2.val.val := by
      apply Fintype.sum_equiv (G.firstEdgeTailEquiv s t n)
      intro x
      rcases x with ⟨⟨e, es⟩, hs, hw, hn⟩
      rfl
    _ = _ := by
      rw [Fintype.sum_sigma]
      apply Finset.sum_congr rfl
      intro e _
      by_cases h : G.source e = s ∧ G.weight e ≤ n
      · rw [if_pos h, coefficient, Finset.mul_sum]
        apply Fintype.sum_equiv (Equiv.subtypeUnivEquiv fun _ ↦ h)
        intro x
        rfl
      · rw [if_neg h]
        apply Finset.sum_eq_zero
        intro x _
        exact False.elim (h x.property)

noncomputable def series (s t : V) : PowerSeries R :=
  PowerSeries.mk (coefficient G m s t)

@[simp] theorem coeff_series (s t : V) (n : ℕ) :
    PowerSeries.coeff n (series G m s t) = coefficient G m s t n := by
  simp [series]

noncomputable def adjacency : Matrix V V (Polynomial R) :=
  fun i j ↦ ∑ e : E, if G.source e = i ∧ G.target e = j then
    Polynomial.monomial (G.weight e) (m e) else 0

theorem adjacency_coeff_zero (i j : V) : (adjacency G m i j).coeff 0 = 0 := by
  classical
  rw [adjacency, ← Polynomial.lcoeff_apply, map_sum]
  simp only [Polynomial.lcoeff_apply]
  apply Finset.sum_eq_zero
  intro e _
  by_cases h : G.source e = i ∧ G.target e = j
  · simp [h, Polynomial.coeff_monomial, Nat.ne_of_gt (G.weight_pos e)]
  · simp [h]

end Komorebi.PaperII.ReleaseTransferScalar
