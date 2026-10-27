module
public import DensePadicIsometry

@[expose] public section

#print axioms KomorebiPaperIX.DensePadicIsometry.onNaturalRange
#print axioms KomorebiPaperIX.DensePadicIsometry.onNaturalRange_nat
#print axioms KomorebiPaperIX.DensePadicIsometry.onNaturalRange_isometry
#print axioms KomorebiPaperIX.DensePadicIsometry.extension
#print axioms KomorebiPaperIX.DensePadicIsometry.extension_continuous
#print axioms KomorebiPaperIX.DensePadicIsometry.extension_nat
#print axioms KomorebiPaperIX.DensePadicIsometry.extension_isometry
#print axioms KomorebiPaperIX.DensePadicIsometry.extension_unique
#print axioms KomorebiPaperIX.DensePadicIsometry.extension_surjective
#print axioms KomorebiPaperIX.DensePadicIsometry.extensionEquiv
#print axioms KomorebiPaperIX.DensePadicIsometry.extensionEquiv_apply
#print axioms KomorebiPaperIX.DensePadicIsometry.extensionEquiv_nat
#print axioms KomorebiPaperIX.DensePadicIsometry.extensionEquiv_unique_continuous
#print axioms KomorebiPaperIX.DensePadicIsometry.extensionEquiv_unique
#print axioms KomorebiPaperIX.DensePadicIsometry.existsUnique_extensionEquiv

example (p : ℕ) [Fact p.Prime] (f : ℕ → ℤ_[p])
    (hdist : ∀ m n : ℕ, dist (f m) (f n) = dist (m : ℤ_[p]) (n : ℤ_[p])) :
    ∃! e : ℤ_[p] ≃ᵢ ℤ_[p], ∀ n : ℕ, e (n : ℤ_[p]) = f n :=
  KomorebiPaperIX.DensePadicIsometry.existsUnique_extensionEquiv p f hdist
