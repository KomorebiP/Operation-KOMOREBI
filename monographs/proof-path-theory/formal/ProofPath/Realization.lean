import ProofPath.Field
import ProofPath.Views

namespace ProofPath

structure PatchInclusion (ι : Type*) where
  small : Set ι
  large : Set ι
  le : small ⊆ large

namespace Field
variable {ι J : Type*} (F : Field ι J)

def patchDiagram : ViewDiagram (Set ι) (PatchInclusion ι) where
  fiber U := F.Local U
  source e := e.small
  target e := e.large
  restriction e := F.restrict e.le

def modelSection (x : ι → Prop) (hx : F.Model x) : (U : Set ι) → F.Local U :=
  F.localize x hx

theorem modelSection_coherent (x : ι → Prop) (hx : F.Model x) :
    F.patchDiagram.Coherent (F.modelSection x hx) := by
  intro e
  apply Local.ext
  intro v
  exact ⟨fun h => ⟨h.1, h.2.2⟩, fun h => ⟨h.1, e.le h.1, h.2⟩⟩

theorem section_at_full_model (s : (U : Set ι) → F.Local U) :
    F.Model (s Set.univ).val := by
  constructor
  · intro v hv
    exact (s Set.univ).leaves v hv (Set.mem_univ v)
  · intro j hj hp
    exact (s Set.univ).rules j hj (Set.subset_univ _) hp

/-- The full-patch equivalence identifies the ambient construction. It is not
    an existence theorem for prescribed proper-patch data. -/
def modelEquivSections : {x : ι → Prop // F.Model x} ≃
    {s : (U : Set ι) → F.Local U // F.patchDiagram.Coherent s} where
  toFun x := ⟨F.modelSection x.val x.property, F.modelSection_coherent x.val x.property⟩
  invFun s := ⟨(s.val Set.univ).val, F.section_at_full_model s.val⟩
  left_inv x := by
    apply Subtype.ext
    funext v
    exact propext (and_iff_right (Set.mem_univ v))
  right_inv s := by
    apply Subtype.ext
    funext U
    have hc := s.property (PatchInclusion.mk U Set.univ (Set.subset_univ U))
    change F.restrict (Set.subset_univ U) (s.val Set.univ) = s.val U at hc
    apply Local.ext
    intro v
    have he := congrArg (fun t : F.Local U => t.val v) hc
    exact Iff.of_eq he

end Field
end ProofPath
