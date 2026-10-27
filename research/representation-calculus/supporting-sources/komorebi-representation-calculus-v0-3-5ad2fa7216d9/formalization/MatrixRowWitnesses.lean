import MatrixCertificates

namespace Komorebi.Representation.Matrix
open Lean.Grind
universe u
variable {R : Type u} [Semiring R] {d t k o l : Nat}

/- Row proof traces share earlier calculations. Their checker enumerates coordinate
   indices only; it never enumerates all states or recomputes long dense words. -/
theorem observed_row_base (A : Fin k → Mat R d d) (O : Mat R o d)
    (j : Fin o) (row : Vec R d) (h : ∀ i, row i = O j i) (x : Vec R d) :
    dot row x = behavior (linearSystem A O) x [] j := by
  rw [show row = O j from funext h]
  rfl

theorem observed_row_prepend (A : Fin k → Mat R d d) (O : Mat R o d)
    (a : Fin k) (w : List (Fin k)) (j : Fin o)
    (parent row : Vec R d) (hp : ∀ x, dot parent x = behavior (linearSystem A O) x w j)
    (h : ∀ i, row i = rm parent (A a) i) (x : Vec R d) :
    dot row x = behavior (linearSystem A O) x (a :: w) j := by
  rw [show row = rm parent (A a) from funext h, dot_rm, hp]
  rfl

theorem valid_from_rows (c : CertificateData R d t k o l) (rows : Mat R l d)
    (hrows : ∀ i x, dot (rows i) x =
      behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2)
    (hstep : ∀ a i j, mm c.encoding (c.actions a) i j = mm (c.transitions a) c.encoding i j)
    (hobs : ∀ j i, c.observations j i = mm c.decoder c.encoding j i)
    (hcomb : ∀ i j, c.encoding i j = mm c.combinations rows i j) : Valid c := by
  have hr : rows = testRows c := by
    funext i
    apply covector_ext
    intro x
    rw [hrows]
    exact (wordRow_behavior c.actions c.observations (c.tests i).1 (c.tests i).2 x).symm
  exact ⟨hstep, hobs, by rw [← hr]; exact hcomb⟩


theorem witnessed_growth_excludes_merge (c : CertificateData R d t k o l)
    (rows deltas : Mat R l d)
    (hrows : ∀ i x, dot (rows i) x =
      behavior (sourceSystem c) x (c.tests i).1 (c.tests i).2)
    (hgrowth : ∀ i, (∀ j, j.val < i.val → dot (rows j) (deltas i) = 0) ∧
      dot (rows i) (deltas i) ≠ 0) (i : Fin l) :
    (∀ j, j.val < i.val → dot (rows j) (deltas i) = dot (rows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem c) (deltas i) (fun _ => 0) := by
  constructor
  · intro j hj
    rw [dot_zero]
    exact (hgrowth i).1 j hj
  · intro hobs
    apply (hgrowth i).2
    rw [hrows, hobs (c.tests i).1 (c.tests i).2, ← hrows, dot_zero]

end Komorebi.Representation.Matrix
