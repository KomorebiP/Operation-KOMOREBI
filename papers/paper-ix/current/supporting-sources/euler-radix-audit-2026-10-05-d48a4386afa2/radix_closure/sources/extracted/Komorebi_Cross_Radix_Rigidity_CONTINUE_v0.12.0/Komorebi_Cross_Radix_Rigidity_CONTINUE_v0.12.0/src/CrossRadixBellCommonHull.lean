import CrossRadixRankNullity
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

noncomputable section
open Polynomial
namespace KomorebiCrossRadix

/-- Evaluate a bounded quasi-polynomial residue profile on the natural numbers. -/
def quasiPolynomialEval (T d : ℕ) : DegreeBoundedProfile T d →ₗ[ℂ] (ℕ → ℂ) where
  toFun P n := (P (n : ZMod T)).1.eval (n : ℂ)
  map_add' P Q := by
    funext n
    simp
  map_smul' c P := by
    funext n
    simp

@[simp] theorem quasiPolynomialEval_apply (T d : ℕ)
    (P : DegreeBoundedProfile T d) (n : ℕ) :
    quasiPolynomialEval T d P n = (P (n : ZMod T)).1.eval (n : ℂ) := rfl

/-- The exact downstream normal-form interface used after Bell's generalized Cobham theorem.
This is deliberately not a formalization of Bell's theorem.  It records only an eventual
bounded-degree quasi-polynomial conclusion.  The external passage from Bell's printed
root-of-unity rationality conclusion to this normal form remains outside Lean in this release. -/
structure BellDownstreamInterface (a : ℕ → ℂ) where
  N : ℕ
  T : ℕ
  d : ℕ
  hTpos : 0 < T
  profile : DegreeBoundedProfile T d
  agrees : ∀ n, N ≤ n → a n = quasiPolynomialEval T d profile n

/-- Canonical bounded quasi-polynomial profile after the affine section `n ↦ m*n+r`. -/
def quasiPolynomialSectionProfile
    (T d m r : ℕ) (hm : 0 < m) (P : DegreeBoundedProfile T d) :
    DegreeBoundedProfile T d :=
  fun k => boundedAffinePolynomialEquiv d (m : ℂ) (r : ℂ)
    (natCast_complex_ne_zero_of_pos hm)
    (P ((m : ZMod T) * k + (r : ZMod T)))

/-- Quasi-polynomial evaluation is exactly closed under every positive affine section. -/
theorem quasiPolynomialEval_coeffSection
    (T d m r : ℕ) (hm : 0 < m) (P : DegreeBoundedProfile T d) :
    coeffSection m r (quasiPolynomialEval T d P) =
      quasiPolynomialEval T d (quasiPolynomialSectionProfile T d m r hm P) := by
  funext n
  simp only [coeffSection, quasiPolynomialEval_apply, quasiPolynomialSectionProfile,
    boundedAffinePolynomialEquiv_apply, Polynomial.eval_comp, Polynomial.eval_add,
    Polynomial.eval_mul, Polynomial.eval_C, Polynomial.eval_X]
  congr 2
  · push_cast
    ring
  · apply congrArg
    push_cast
    ring

/-- Agreement from a fixed threshold. -/
def AgreesFromQP (N : ℕ) (f g : ℕ → ℂ) : Prop :=
  ∀ n, N ≤ n → f n = g n

/-- Positive affine sectioning preserves the same eventual-agreement threshold. -/
theorem agreesFromQP_coeffSection
    (N m r : ℕ) (f g : ℕ → ℂ) (hm : 0 < m)
    (hfg : AgreesFromQP N f g) :
    AgreesFromQP N (coeffSection m r f) (coeffSection m r g) := by
  intro n hn
  apply hfg
  have hm1 : 1 ≤ m := hm
  have hnm : n ≤ m * n := by
    simpa using Nat.mul_le_mul_right n hm1
  exact hn.trans (hnm.trans (Nat.le_add_right (m * n) r))

/-- An eventual bounded quasi-polynomial stays in the same `(N,T,d)` profile after every
positive affine section. -/
theorem eventualQuasiPolynomial_section_closed
    (a : ℕ → ℂ) (N T d m r : ℕ) (hm : 0 < m)
    (P : DegreeBoundedProfile T d)
    (ha : AgreesFromQP N a (quasiPolynomialEval T d P)) :
    AgreesFromQP N (coeffSection m r a)
      (quasiPolynomialEval T d (quasiPolynomialSectionProfile T d m r hm P)) := by
  intro n hn
  calc
    coeffSection m r a n = coeffSection m r (quasiPolynomialEval T d P) n :=
      agreesFromQP_coeffSection N m r a (quasiPolynomialEval T d P) hm ha n hn
    _ = quasiPolynomialEval T d (quasiPolynomialSectionProfile T d m r hm P) n :=
      congrFun (quasiPolynomialEval_coeffSection T d m r hm P) n

/-- Coordinates for the finite transient prefix. -/
abbrev PrefixData (N : ℕ) := Fin N → ℂ

/-- Extend `N` prefix coordinates by zero. -/
def prefixSynthesize (N : ℕ) : PrefixData N →ₗ[ℂ] (ℕ → ℂ) where
  toFun c n := if h : n < N then c ⟨n, h⟩ else 0
  map_add' c e := by
    funext n
    by_cases h : n < N <;> simp [h]
  map_smul' x c := by
    funext n
    by_cases h : n < N <;> simp [h]

/-- One fixed finite coordinate space containing a transient prefix and a bounded
quasi-polynomial tail profile. -/
abbrev CommonHullCoordinates (N T d : ℕ) :=
  PrefixData N × DegreeBoundedProfile T d

/-- Synthesis from the common finite coordinate space to a sequence. -/
def commonHullSynthesize (N T d : ℕ) :
    CommonHullCoordinates N T d →ₗ[ℂ] (ℕ → ℂ) where
  toFun c n := prefixSynthesize N c.1 n + quasiPolynomialEval T d c.2 n
  map_add' c e := by
    funext n
    simp only [Prod.fst_add, Prod.snd_add, map_add, Pi.add_apply]
    ring
  map_smul' x c := by
    funext n
    change prefixSynthesize N (x • c.1) n + quasiPolynomialEval T d (x • c.2) n =
      x • (prefixSynthesize N c.1 n + quasiPolynomialEval T d c.2 n)
    rw [map_smul, map_smul]
    simp only [Pi.smul_apply, smul_eq_mul]
    ring

/-- The single linear common hull used for all positive radices. -/
def CommonHull (N T d : ℕ) : Submodule ℂ (ℕ → ℂ) :=
  LinearMap.range (commonHullSynthesize N T d)

/-- The correction coordinates required to replace a quasi-polynomial tail by an arbitrary
sequence on its first `N` entries. -/
def prefixCorrection (N T d : ℕ) (f : ℕ → ℂ) (P : DegreeBoundedProfile T d) : PrefixData N :=
  fun i => f i - quasiPolynomialEval T d P i

/-- Any sequence agreeing with a bounded quasi-polynomial after `N` belongs to the common hull. -/
theorem mem_commonHull_of_agreesFromQP
    (f : ℕ → ℂ) (N T d : ℕ) (P : DegreeBoundedProfile T d)
    (h : AgreesFromQP N f (quasiPolynomialEval T d P)) :
    f ∈ CommonHull N T d := by
  refine ⟨(prefixCorrection N T d f P, P), ?_⟩
  funext n
  by_cases hn : n < N
  · simp [commonHullSynthesize, prefixSynthesize, prefixCorrection, hn]
  · have hN : N ≤ n := Nat.le_of_not_gt hn
    have heq := h n hN
    simp [commonHullSynthesize, prefixSynthesize, hn, heq]

/-- Every element of the common hull has an eventual quasi-polynomial tail with the same
`(N,T,d)` bounds. -/
theorem exists_profile_agreesFromQP_of_mem_commonHull
    (N T d : ℕ) {f : ℕ → ℂ} (hf : f ∈ CommonHull N T d) :
    ∃ P : DegreeBoundedProfile T d, AgreesFromQP N f (quasiPolynomialEval T d P) := by
  rcases hf with ⟨c, hc⟩
  rcases c with ⟨pref, P⟩
  refine ⟨P, ?_⟩
  intro n hn
  have hnot : ¬ n < N := Nat.not_lt_of_ge hn
  calc
    f n = commonHullSynthesize N T d (pref, P) n := by rw [hc]
    _ = quasiPolynomialEval T d P n := by
      simp [commonHullSynthesize, prefixSynthesize, hnot]

/-- The fixed common hull is invariant under every positive affine section.  Thus the positive
section monoid acts internally on one finite-dimensional ambient space. -/
theorem commonHull_closed_under_positive_section
    (N T d m r : ℕ) (hm : 0 < m) {f : ℕ → ℂ}
    (hf : f ∈ CommonHull N T d) :
    coeffSection m r f ∈ CommonHull N T d := by
  obtain ⟨P, hP⟩ := exists_profile_agreesFromQP_of_mem_commonHull N T d hf
  apply mem_commonHull_of_agreesFromQP
    (coeffSection m r f) N T d (quasiPolynomialSectionProfile T d m r hm P)
  exact eventualQuasiPolynomial_section_closed f N T d m r hm P hP

/-- Exact finite dimension of the common coordinate source. -/
theorem commonHullCoordinates_finrank (N T d : ℕ) [NeZero T] :
    Module.finrank ℂ (CommonHullCoordinates N T d) = N + T * (d + 1) := by
  rw [Module.finrank_prod]
  rw [Module.finrank_fin_fun]
  rw [degreeBoundedProfile_finrank]

/-- The synthesized common hull has dimension at most `N + T(d+1)`. -/
theorem commonHull_finrank_le (N T d : ℕ) [NeZero T] :
    Module.finrank ℂ (CommonHull N T d) ≤ N + T * (d + 1) := by
  calc
    Module.finrank ℂ (CommonHull N T d) ≤
        Module.finrank ℂ (CommonHullCoordinates N T d) :=
      LinearMap.finrank_range_le (commonHullSynthesize N T d)
    _ = N + T * (d + 1) := commonHullCoordinates_finrank N T d

/-- The Bell downstream interface places every positive affine section in the same common
hull.  This is stronger than restricting to powers of a fixed radix. -/
theorem bellDownstream_uniform_all_positive_affine_commonHull
    (a : ℕ → ℂ) (B : BellDownstreamInterface a) :
    ∀ m r : ℕ, 0 < m → coeffSection m r a ∈ CommonHull B.N B.T B.d := by
  intro m r hm
  apply mem_commonHull_of_agreesFromQP
    (coeffSection m r a) B.N B.T B.d
      (quasiPolynomialSectionProfile B.T B.d m r hm B.profile)
  exact eventualQuasiPolynomial_section_closed a B.N B.T B.d m r hm B.profile B.agrees

/-- **Uniform all-positive-radix common-hull theorem.**  Once the explicit downstream Bell
interface is supplied, every depth and address of every positive radix belongs to one and the
same finite-dimensional linear hull.  Neither the hull nor its dimension bound depends on the
radix, depth, or address. -/
theorem bellDownstream_uniform_all_positive_radix_commonHull
    (a : ℕ → ℂ) (B : BellDownstreamInterface a) :
    ∀ b e s : ℕ, 0 < b →
      coeffSection (b ^ e) s a ∈ CommonHull B.N B.T B.d := by
  intro b e s hb
  exact bellDownstream_uniform_all_positive_affine_commonHull a B (b ^ e) s (Nat.pow_pos hb)

/-- Quantitative form: the same common hull controlling all positive radices has the uniform
coarse dimension bound `N + T(d+1)`. -/
theorem bellDownstream_uniform_commonHull_with_dimension
    (a : ℕ → ℂ) (B : BellDownstreamInterface a) :
    ∃ H : Submodule ℂ (ℕ → ℂ),
      Module.finrank ℂ H ≤ B.N + B.T * (B.d + 1) ∧
      ∀ b e s : ℕ, 0 < b → coeffSection (b ^ e) s a ∈ H := by
  let hne : NeZero B.T := ⟨Nat.ne_of_gt B.hTpos⟩
  refine ⟨CommonHull B.N B.T B.d, @commonHull_finrank_le B.N B.T B.d hne, ?_⟩
  exact bellDownstream_uniform_all_positive_radix_commonHull a B

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.quasiPolynomialEval_coeffSection
#print axioms KomorebiCrossRadix.eventualQuasiPolynomial_section_closed
#print axioms KomorebiCrossRadix.mem_commonHull_of_agreesFromQP
#print axioms KomorebiCrossRadix.exists_profile_agreesFromQP_of_mem_commonHull
#print axioms KomorebiCrossRadix.commonHull_closed_under_positive_section
#print axioms KomorebiCrossRadix.commonHull_finrank_le
#print axioms KomorebiCrossRadix.bellDownstream_uniform_all_positive_affine_commonHull
#print axioms KomorebiCrossRadix.bellDownstream_uniform_all_positive_radix_commonHull
#print axioms KomorebiCrossRadix.bellDownstream_uniform_commonHull_with_dimension
