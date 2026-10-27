import KomorebiPadic.CoordinateIdealClosure
import KomorebiPadic.SupportMaskAutomaton

namespace KomorebiPadic
open Polynomial

noncomputable def leastMaskIdealCapacity (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :=
  CoordinateIdeal.least hp.pos (maskSupportSystem p r A B hp)

abbrev IdealMaskState (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) : Type :=
  CoordinateIdeal.State (p := p) (r := r) (leastMaskIdealCapacity p r A B hp)

noncomputable def idealMaskInitial (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) : IdealMaskState p r A B hp :=
  CoordinateIdeal.initial hp.pos (maskSupportSystem p r A B hp)

noncomputable def idealMaskTransition (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (d : Fin p) :=
  CoordinateIdeal.transition hp.pos (maskSupportSystem p r A B hp) d

noncomputable def idealMaskIterate (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : IdealMaskState p r A B hp) : IdealMaskState p r A B hp :=
  CoordinateIdeal.run hp.pos (maskSupportSystem p r A B hp) ds x

noncomputable def idealMaskEmbedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (x : IdealMaskState p r A B hp) : SupportMaskState p r A B hp :=
  CoordinateIdeal.supportEmbedding hp.pos (maskSupportSystem p r A B hp) x

theorem leastMaskIdealCapacity_closed (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    CoordinateIdeal.Closed (maskSupportSystem p r A B hp) (leastMaskIdealCapacity p r A B hp) :=
  CoordinateIdeal.least_closed _ _

theorem leastMaskIdealCapacity_le (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (w : ProfilePosition (leastMaskDegreeProfile p r A B hp) → ℕ)
    (hw : CoordinateIdeal.Closed (maskSupportSystem p r A B hp) w) :
    leastMaskIdealCapacity p r A B hp ≤ w := CoordinateIdeal.least_le _ _ _ hw

theorem leastMaskIdealCapacity_bound (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (i : ProfilePosition (leastMaskDegreeProfile p r A B hp)) :
    leastMaskIdealCapacity p r A B hp i ≤ r := CoordinateIdeal.least_bound _ _ _

theorem idealMaskEmbedding_injective (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    Function.Injective (idealMaskEmbedding p r A B hp) := CoordinateIdeal.supportEmbedding_injective _ _

@[simp] theorem idealMask_initial_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) :
    idealMaskEmbedding p r A B hp (idealMaskInitial p r A B hp) = supportMaskInitial p r A B hp := rfl

theorem idealMask_transition_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (d : Fin p) (x : IdealMaskState p r A B hp) :
    idealMaskEmbedding p r A B hp (idealMaskTransition p r A B hp d x) =
      supportMaskTransition p r A B hp d (idealMaskEmbedding p r A B hp x) :=
  CoordinateIdeal.supportEmbedding_transition _ _ _ _

theorem idealMask_iterate_embedding (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (ds : List (Fin p)) (x : IdealMaskState p r A B hp) :
    idealMaskEmbedding p r A B hp (idealMaskIterate p r A B hp ds x) =
      supportMaskIterate p r A B hp ds (idealMaskEmbedding p r A B hp x) :=
  CoordinateIdeal.supportEmbedding_run _ _ _ _

noncomputable def idealMaskOutput (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (x : IdealMaskState p r A B hp) : ZMod (p^r) :=
  supportMaskOutput p r A B hp hr hB (idealMaskEmbedding p r A B hp x)

theorem idealMask_output_eq_support (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (ds : List (Fin p)) :
    idealMaskOutput p r A B hp hr hB (idealMaskIterate p r A B hp ds (idealMaskInitial p r A B hp)) =
      supportMaskOutput p r A B hp hr hB (supportMaskIterate p r A B hp ds (supportMaskInitial p r A B hp)) := by
  unfold idealMaskOutput
  rw [idealMask_iterate_embedding, idealMask_initial_embedding]

theorem idealMask_output_canonical_word (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (ds : List (Fin p)) :
    idealMaskOutput p r A B hp hr hB (idealMaskIterate p r A B hp ds (idealMaskInitial p r A B hp)) =
      PowerSeries.coeff (cartierWordValue p (ds.map Fin.val)) (canonicalMaskSeries p r A B hp hr hB) := by
  rw [idealMask_output_eq_support]
  exact supportMask_output_canonical_word p r A B hp hr hB hAB ds

theorem idealMask_output_canonical_coefficient (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    idealMaskOutput p r A B hp hr hB
      (idealMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (idealMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) := by
  rw [idealMask_output_eq_support]
  exact supportMask_output_canonical_coefficient p r A B hp hr hB hAB n

structure IdealCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) where
  predecessor : SupportCanonicalMaskCertificate p r A B hp hr hB
  closed : CoordinateIdeal.Closed (maskSupportSystem p r A B hp) (leastMaskIdealCapacity p r A B hp)
  least : ∀ w, CoordinateIdeal.Closed (maskSupportSystem p r A B hp) w → leastMaskIdealCapacity p r A B hp ≤ w
  bounded : ∀ i, leastMaskIdealCapacity p r A B hp i ≤ r
  output : ∀ n, idealMaskOutput p r A B hp hr hB
    (idealMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (idealMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB)

noncomputable def idealCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    IdealCanonicalMaskCertificate p r A B hp hr hB where
  predecessor := supportCanonicalMaskCertificate p r A B hp hr hB hAB
  closed := leastMaskIdealCapacity_closed p r A B hp
  least := leastMaskIdealCapacity_le p r A B hp
  bounded := leastMaskIdealCapacity_bound p r A B hp
  output := idealMask_output_canonical_coefficient p r A B hp hr hB hAB

end KomorebiPadic
