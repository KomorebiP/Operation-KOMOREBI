import KomorebiLSM.DataSelectedGeometry

/-! Both initial states have mass one and both operators preserve mass. Covering
the truth and checking only a convenient fitted candidate still does not verify
the selected cone for the truth; the same entire set must be quantified. -/
open Komorebi.LSM DataSelectedGeometry

def candidate : Model Unit (ℝ × ℝ) := ⟨(1,0),fun _ => LinearMap.id⟩
def truth : Model Unit (ℝ × ℝ) := ⟨(1,2),fun _ => LinearMap.id⟩
def domain (_ : Unit) : Set (ℝ × ℝ) := LorentzCylinder.cone
def uncertainty : Set (Model Unit (ℝ × ℝ)) := {M | M=candidate ∨ M=truth}

example : candidate.initial.1=1 ∧ truth.initial.1=1 := ⟨rfl,rfl⟩
example : truth∈uncertainty := Or.inr rfl
example : DomainValid domain () candidate := by
  constructor
  · norm_num [domain,candidate,LorentzCylinder.cone,OrientedEllipsoid.lorentz]
  · intro s z hz
    exact hz

example : DomainValid domain () truth := by
  change (‖(2 : ℝ)‖≤1) ∧ _
  norm_num
