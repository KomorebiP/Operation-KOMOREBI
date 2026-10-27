import KomorebiPadic.PresentationExamples
open KomorebiPadic KomorebiPadic.FiniteModulePresentation
noncomputable section
variable {p r : ℕ} {V W A : Type*} [AddCommGroup V] [AddCommGroup W]

example [Module (ZMod (p^r)) V] [Finite V] (hp : p.Prime) :
    Nonempty (Presentation p r V) := nonempty_presentation hp

example [Module (ZMod (p^r)) V] [Module (ZMod (p^r)) W]
    (hp : 1 < p) (P : Presentation p r V) (Q : Presentation p r W) :
    Nonempty (V ≃ₗ[ZMod (p^r)] W) ↔ signature P = signature Q :=
  signature_classifies_linear hp P Q

example (hp : 1 < p) (P Q : Presentation p r V) :
    sortedSignature P = sortedSignature Q := sortedSignature_unique hp P Q

example (hp : 1 < p) (P : Presentation p r V) (k : ℕ) (hk : 0 < k) :
    intrinsicMultiplicity p k V = (Finset.univ.filter (fun i : P.Index => P.exponent i = k)).card := by
  classical
  exact multiplicity_eq_count hp P k hk

example (P : Presentation p r V) (a : P.Index → ℤ) :
    (∑ i, a i • generator P i) = 0 ↔ ∀ i, (p^(P.exponent i) : ℤ) ∣ a i :=
  generator_relations P a

example [Module (ZMod (p^r)) V] (hp : 0 < p) (P : Presentation p r V)
    (T : V →ₗ[ZMod (p^r)] V) (i j : P.Index) :
    p^(P.exponent j-P.exponent i) ∣ (entry P T j i).val :=
  entry_divisibility hp P T j i

example [Module (ZMod (p^r)) V] (P : Presentation p r V)
    (M : LinearReachability.System (ZMod (p^r)) V A) (ds : List A) (x : Coordinates P) :
    P.equiv.symm (FiniteModulePresentation.run P M ds x) =
      LinearReachability.run M ds (P.equiv.symm x) := run_decode P M ds x

example (p r : ℕ) (A B : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    PresentedCanonicalMaskCertificate p r A B hp hr hB :=
  presentedCanonicalMaskCertificate p r A B hp hr hB hAB

example (p r : ℕ) (A B : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    presentedMaskOutput p r A B hp hr hB
      (presentedMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (presentedMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) :=
  presentedMask_output_canonical_coefficient p r A B hp hr hB hAB n
end
