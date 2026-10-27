import PaperXI.LocalFactorIdentification

/-! The one-candidate local-factor comparison used in the manuscript.
The candidate and its admissibility are supplied. Matching factors are required
only for this candidate. No atom-realization existence field is consumed.
The separating factor system remains an explicit classical input. -/
set_option autoImplicit false
noncomputable section

namespace PaperXI.SingleCandidateComparison
open LocalFactorIdentification

variable {Atom Test Value : Type*} {s : Setoid Atom}

/-- Equality of the declared factor profile identifies this supplied candidate
with the reference in the declared isomorphism quotient. -/
theorem source (S : FactorSystem s Test Value)
    (candidate reference : Atom)
    (hcandidate : S.admissible candidate) (hreference : S.admissible reference)
    (expected : Test → Value)
    (h5 : S.profile candidate = expected)
    (href : S.profile reference = expected) :
    Quotient.mk s candidate = Quotient.mk s reference := by
  apply (class_eq_iff S hcandidate hreference).mpr
  exact h5.trans href.symm

end PaperXI.SingleCandidateComparison
