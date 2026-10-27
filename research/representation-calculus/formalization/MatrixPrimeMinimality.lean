module
public import FinRingCompatibility

@[expose] public section

set_option backward.isDefEq.respectTransparency false

namespace Komorebi.Representation.Matrix

/-- The general torsion-safe lower bound. Only the initial encoding must be linear;
the competitor's deterministic dynamics and outputs may be nonlinear. -/
theorem prime_certificate_linear_lower {p r d t k o l n : Nat}
    (hp : p.Prime) (hr : 0 < r)
    (c : CertificateData (ZMod (p^r)) d t k o l) (hc : Valid c)
    (s : SmithData (ZMod (p^r)) d t) (hs : SmithValid c.encoding s)
    (hw : ∀ i, s.weights i ≠ 0)
    (U : System (Fin n → ZMod (p^r)) (Fin k) (Fin o) (ZMod (p^r)))
    (e : (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin n → ZMod (p^r)))
    (he : ∀ x w j, behavior (sourceSystem c) x w j = behavior U (e x) w j) :
    t ≤ n := by
  have hker := fun x y h => sufficient_encoding_kernel c hc U e he (x:=x) (y:=y) h
  obtain ⟨q,hq,hgen⟩ := KomorebiPadic.zmod_submodule_generators (p^r) n e.range
  have hmap := hgen.map (encodingToPrincipal c s hs e hker)
    (encodingToPrincipal_surjective c s hs e hker)
  have ht := KomorebiPadic.primePrincipalFamily_generator_lower p hp r hr
    s.weights hw q hmap
  simpa using ht.trans hq

/-- Sharp budget characterization under an all-source-state, all-future-word contract. -/
theorem prime_certificate_minimum_iff {p r d t k o l : Nat}
    (hp : p.Prime) (hr : 0 < r)
    (c : CertificateData (ZMod (p^r)) d t k o l) (hc : Valid c)
    (s : SmithData (ZMod (p^r)) d t) (hs : SmithValid c.encoding s)
    (hw : ∀ i, s.weights i ≠ 0) (budget : Nat) :
    (∃ n ≤ budget,
      ∃ (U : System (Fin n → ZMod (p^r)) (Fin k) (Fin o) (ZMod (p^r)))
        (e : (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin n → ZMod (p^r))),
      ∀ x w j, behavior (sourceSystem c) x w j = behavior U (e x) w j) ↔
      t ≤ budget := by
  constructor
  · rintro ⟨n,hn,U,e,he⟩
    exact (prime_certificate_linear_lower hp hr c hc s hs hw U e he).trans hn
  · intro ht
    exact ⟨t,ht,targetSystem c,matrixLinear c.encoding,matrix_all_words c hc⟩

/-- A modulus equality is used once, without re-elaborating every concrete matrix over p^r. -/
theorem residue_certificate_minimum_iff {m p r d t k o l : Nat}
    (hp : p.Prime) (hr : 0 < r) (hm : m = p^r)
    (c : CertificateData (ZMod m) d t k o l) (hc : Valid c)
    (s : SmithData (ZMod m) d t) (hs : SmithValid c.encoding s)
    (hw : ∀ i, s.weights i ≠ 0) (budget : Nat) :
    (∃ n ≤ budget,
      ∃ (U : System (Fin n → ZMod m) (Fin k) (Fin o) (ZMod m))
        (e : (Fin d → ZMod m) →ₗ[ZMod m] (Fin n → ZMod m)),
      ∀ x w j, behavior (sourceSystem c) x w j = behavior U (e x) w j) ↔
      t ≤ budget := by
  subst m
  exact prime_certificate_minimum_iff hp hr c hc s hs hw budget

open Fin.CommRing in
theorem fin_certificate_minimum_iff {m p r d t k o l : Nat} [NeZero m]
    (hp : p.Prime) (hr : 0 < r) (hm : m = p^r)
    (c : CertificateData (Fin m) d t k o l) (hc : Valid c)
    (s : SmithData (Fin m) d t) (hs : SmithValid c.encoding s)
    (hw : ∀ i, s.weights i ≠ 0) (budget : Nat) :
    (∃ n ≤ budget,
      ∃ (U : System (Fin n → Fin m) (Fin k) (Fin o) (Fin m))
        (e : (Fin d → Fin m) →ₗ[Fin m] (Fin n → Fin m)),
      ∀ x w j, behavior (sourceSystem c) x w j = behavior U (e x) w j) ↔
      t ≤ budget := by
  cases m with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ m =>
    have heq : (Lean.Grind.Fin.instCommRingFinOfNeZeroNat (m+1)).toCommSemiring.toSemiring =
        (@CommRing.toGrindCommRing (ZMod (m+1)) (ZMod.commRing (m+1))).toCommSemiring.toSemiring :=
      fin_grindSemiring_eq (m+1)
    rw [heq] at hc hs ⊢
    exact residue_certificate_minimum_iff hp hr hm c hc s hs hw budget

theorem smith_valid_of_check {m d t : Nat} [NeZero m]
    (P : Mat (Fin m) t d) (s : SmithData (Fin m) d t)
    (h : checkSmith P s = true) : SmithValid P s := of_decide_eq_true h

end Komorebi.Representation.Matrix
