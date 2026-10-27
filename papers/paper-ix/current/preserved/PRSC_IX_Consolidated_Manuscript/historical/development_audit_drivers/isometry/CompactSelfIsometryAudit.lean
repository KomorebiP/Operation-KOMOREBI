module

public import CompactSelfIsometry

@[expose] public section

#print axioms KomorebiPaperIX.CompactSelfIsometry.iterate_isometry
#print axioms KomorebiPaperIX.CompactSelfIsometry.denseRange
#print axioms KomorebiPaperIX.CompactSelfIsometry.surjective

example {X : Type*} [MetricSpace X] [CompactSpace X] (f : X → X)
    (hf : Isometry f) : ∀ y, ∃ x, f x = y :=
  KomorebiPaperIX.CompactSelfIsometry.surjective hf
