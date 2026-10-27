import AVOC.StochasticQuotient

namespace Komorebi.AVOC

/-- A completely uninformative Bool experiment cannot Blackwell-refine the
perfect Bool observation. This certifies that the Blackwell order can be
strict. -/
theorem noInformation_not_refines_perfectBool :
    ¬ BlackwellRefines (uninformativeChannel Bool) (identityChannel Bool) := by
  intro h
  rcases h with ⟨K, hK⟩
  have hf := congrArg (fun E : RationalChannel Bool Bool => E.prob false false) hK
  have ht := congrArg (fun E : RationalChannel Bool Bool => E.prob true false) hK
  simp [composeChannel, uninformativeChannel, identityChannel] at hf ht
  linarith

/-- Perfect Bool observation does refine the uninformative Bool experiment. -/
theorem perfectBool_refines_noInformation :
    BlackwellRefines (identityChannel Bool) (uninformativeChannel Bool) := by
  exact blackwellRefines_uninformative (identityChannel Bool)

/-- Therefore Blackwell refinement is not symmetric. -/
theorem blackwellRefinement_not_symmetric_example :
    BlackwellRefines (identityChannel Bool) (uninformativeChannel Bool) ∧
      ¬ BlackwellRefines (uninformativeChannel Bool) (identityChannel Bool) := by
  exact ⟨perfectBool_refines_noInformation, noInformation_not_refines_perfectBool⟩

end Komorebi.AVOC
