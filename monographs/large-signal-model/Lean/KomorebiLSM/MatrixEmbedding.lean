import KomorebiLSM.BaseNormTopology
import KomorebiLSM.ObservationTree
import KomorebiLSM.ConditionalStochasticCompletion
import Mathlib.Analysis.Matrix.Order
import KomorebiLSM.MatrixOrderUnit

/-! Exact finite-dimensional matrix-embedding certificates. -/
set_option autoImplicit false
namespace Komorebi.LSM.MatrixEmbedding
open scoped BigOperators

/-- A symmetric injective matrix realization with an actual positive-definite witness. -/
structure Embedding (E D : Type*) [AddCommGroup E] [Module ℝ E] [Fintype D] where
  J : E →ₗ[ℝ] Matrix D D ℝ
  symmetric : ∀ z, (J z).IsHermitian
  injective : Function.Injective J
  interior : E
  interior_posDef : (J interior).PosDef

namespace Embedding
variable {E D : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
  [Fintype D] (M : Embedding E D)

/-- Trace is the mass functional certified by the embedding. -/
def mass : E →ₗ[ℝ] ℝ := (Matrix.traceLinearMap D ℝ ℝ).comp M.J

/-- The embedded positive-semidefinite cone. -/
def cone : Set E := {z | (M.J z).PosSemidef}

@[simp] theorem mass_apply (z : E) : M.mass z = Matrix.trace (M.J z) := rfl
@[simp] theorem mem_cone (z : E) : z ∈ M.cone ↔ (M.J z).PosSemidef := Iff.rfl

theorem cone_zero : (0 : E) ∈ M.cone := by simp [cone, Matrix.PosSemidef.zero]

theorem cone_add {x y : E} (hx : x ∈ M.cone) (hy : y ∈ M.cone) :
    x + y ∈ M.cone := by
  simpa only [cone, Set.mem_ofPred_eq, map_add] using hx.add hy

theorem cone_smul {a : ℝ} (ha : 0 ≤ a) {x : E} (hx : x ∈ M.cone) :
    a • x ∈ M.cone := by
  simpa only [cone, Set.mem_ofPred_eq, map_smul] using hx.smul ha

theorem cone_closed [FiniteDimensional ℝ E] : IsClosed M.cone :=
  Matrix.posSemidef_is_closed.preimage M.J.continuous_of_finiteDimensional

theorem cone_mass_nonneg {x : E} (hx : x ∈ M.cone) : 0 ≤ M.mass x := by
  classical
  exact Finset.sum_nonneg fun i _ => hx.diag_nonneg

theorem cone_mass_pos {x : E} (hx : x ∈ M.cone) (hne : x ≠ 0) : 0 < M.mass x := by
  have hzero : M.mass x ≠ 0 := by
    intro h
    have hj : M.J x = M.J 0 := by simpa using hx.trace_eq_zero_iff.mp h
    exact hne (M.injective hj)
  exact lt_of_le_of_ne (M.cone_mass_nonneg hx) (Ne.symm hzero)

theorem cone_pointed {x : E} (hx : x ∈ M.cone) (hnx : -x ∈ M.cone) : x = 0 := by
  by_contra hn
  have hp := M.cone_mass_pos hx hn
  have hnp := M.cone_mass_nonneg hnx
  rw [map_neg] at hnp
  linarith

/-- A definite point dominates every symmetric embedded direction. -/
theorem exists_positive_decomposition (x : E) :
    ∃ u ∈ M.cone, ∃ v ∈ M.cone, x = u - v := by
  classical
  obtain ⟨a, ha, hp, _⟩ := MatrixOrderUnit.exists_nonnegative_bound
    (M.J M.interior) (M.J x) M.interior_posDef (M.symmetric x)
  refine ⟨a • M.interior + x, ?_, a • M.interior, ?_, ?_⟩
  · simpa only [mem_cone, map_add, map_smul] using hp
  · exact M.cone_smul ha M.interior_posDef.posSemidef
  · simp

theorem cone_spans : Submodule.span ℝ M.cone = ⊤ := by
  apply top_unique
  intro x _
  obtain ⟨u, hu, v, hv, rfl⟩ := M.exists_positive_decomposition x
  exact Submodule.sub_mem _ (Submodule.subset_span hu) (Submodule.subset_span hv)

/-- All cone axioms follow from injectivity and the actual definite witness. -/
noncomputable def coneInstance [FiniteDimensional ℝ E] : BaseNorm.ProbabilityCone E where
  carrier := M.cone
  zero_mem := M.cone_zero
  add_mem := M.cone_add
  smul_mem := M.cone_smul
  spans := M.cone_spans
  mass := M.mass
  mass_pos := M.cone_mass_pos
  closed := M.cone_closed

@[simp] theorem coneInstance_mem [FiniteDimensional ℝ E] (z : E) :
    z ∈ M.coneInstance.carrier ↔ (M.J z).PosSemidef := Iff.rfl

@[simp] theorem coneInstance_mass [FiniteDimensional ℝ E] : M.coneInstance.mass = M.mass := rfl

/-- The normalized trace-one base is compact in the original coordinates. -/
theorem base_compact [FiniteDimensional ℝ E] :
    IsCompact {z | z ∈ M.cone ∧ M.mass z = 1} := M.coneInstance.base_compact

/-- A finite weighted congruence, including the empty sum. -/
def weightedCongruence {I : Type*} [Fintype I] (w : I → ℝ)
    (K : I → Matrix D D ℝ) (X : Matrix D D ℝ) : Matrix D D ℝ :=
  ∑ i, w i • (K i * X * (K i).transpose)

theorem weightedCongruence_posSemidef {I : Type*} [Fintype I]
    (w : I → ℝ) (hw : ∀ i, 0 ≤ w i) (K : I → Matrix D D ℝ)
    {X : Matrix D D ℝ} (hX : X.PosSemidef) :
    (weightedCongruence w K X).PosSemidef := by
  classical
  apply Matrix.posSemidef_sum
  intro i _
  apply Matrix.PosSemidef.smul _ (hw i)
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    hX.mul_mul_conjTranspose_same (K i)

/-- Branch data expose actual nonnegative weights and matrices, rather than assuming positivity. -/
structure CongruenceCertificate {S : Type*} (B : S → E →ₗ[ℝ] E) where
  terms : S → ℕ
  weight : (s : S) → Fin (terms s) → ℝ
  weight_nonneg : ∀ s i, 0 ≤ weight s i
  factor : (s : S) → Fin (terms s) → Matrix D D ℝ
  identity : ∀ s z, M.J (B s z) = weightedCongruence (weight s) (factor s) (M.J z)

variable {S : Type*} {B : S → E →ₗ[ℝ] E}

theorem CongruenceCertificate.preserves_cone
    (cert : M.CongruenceCertificate B) (s : S) {z : E} (hz : z ∈ M.cone) :
    B s z ∈ M.cone := by
  change (M.J (B s z)).PosSemidef
  rw [cert.identity]
  exact weightedCongruence_posSemidef _ (cert.weight_nonneg s) _ hz

theorem CongruenceCertificate.word_cone (cert : M.CongruenceCertificate B)
    (word : List S) {z : E} (hz : z ∈ M.cone) :
    FiniteInstruments.wordAction B word z ∈ M.cone := by
  induction word generalizing z with
  | nil => exact hz
  | cons s word ih => exact ih (CongruenceCertificate.preserves_cone M cert s hz)

theorem CongruenceCertificate.word_mass_nonneg (cert : M.CongruenceCertificate B)
    (word : List S) {z : E} (hz : z ∈ M.cone) :
    0 ≤ M.mass (FiniteInstruments.wordAction B word z) :=
  M.cone_mass_nonneg (CongruenceCertificate.word_cone M cert word hz)

section Probability
variable {A O : Type*} [Fintype O] {B : A × O → E →ₗ[ℝ] E}

theorem CongruenceCertificate.causal (cert : M.CongruenceCertificate B)
    (mass_conservation : ∀ a z, ∑ o, M.mass (B (a,o) z) = M.mass z)
    (z : E) (hz : z ∈ M.cone) (hm : M.mass z = 1) :
    Behavior.CausalLaw (fun word => M.mass (FiniteInstruments.wordAction B word z)) := by
  refine ⟨hm, ?_, ?_⟩
  · intro word
    exact CongruenceCertificate.word_mass_nonneg M cert word hz
  · intro history a
    simpa only [FiniteInstruments.wordAction_append, FiniteInstruments.wordAction_cons,
      FiniteInstruments.wordAction_nil, LinearMap.id_comp, LinearMap.comp_apply]
      using mass_conservation a (FiniteInstruments.wordAction B history z)

theorem CongruenceCertificate.word_probability (cert : M.CongruenceCertificate B)
    (mass_conservation : ∀ a z, ∑ o, M.mass (B (a,o) z) = M.mass z)
    (z : E) (hz : z ∈ M.cone) (hm : M.mass z = 1) (word : List (A × O)) :
    0 ≤ M.mass (FiniteInstruments.wordAction B word z) ∧
      M.mass (FiniteInstruments.wordAction B word z) ≤ 1 :=
  (CongruenceCertificate.causal M cert mass_conservation z hz hm).word_bounds word

/-- Exact mass conservation supplies a complete instrument for each intervention. -/
theorem CongruenceCertificate.instrument [FiniteDimensional ℝ E]
    (cert : M.CongruenceCertificate B)
    (mass_conservation : ∀ a z, ∑ o, M.mass (B (a,o) z) = M.mass z) (a : A) :
    M.coneInstance.Instrument (fun o => B (a,o)) := by
  refine ⟨?_, mass_conservation a⟩
  intro o x hx
  exact CongruenceCertificate.preserves_cone M cert (a,o) hx

/-- Every finite observation tree under a history-dependent intervention is normalized. -/
theorem CongruenceCertificate.observation_tree_prior [FiniteDimensional ℝ E]
    (cert : M.CongruenceCertificate B)
    (mass_conservation : ∀ a z, ∑ o, M.mass (B (a,o) z) = M.mass z)
    (policy : List O → A) (n : ℕ) (z : E) (hz : z ∈ M.cone) (hm : M.mass z = 1) :
    FiniteBayes.IsPrior (ObservationTree.recordLaw M.coneInstance
      (fun h o => B (policy h,o)) n [] z) := by
  exact ObservationTree.record_prior M.coneInstance _
    (fun h => CongruenceCertificate.instrument M cert mass_conservation (policy h))
    n [] z ⟨hz, hm⟩

end Probability

section Atlas
variable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- Change of coordinates transports the embedding and its definite interior witness together. -/
def transport (T : E ≃ₗ[ℝ] F) : Embedding F D where
  J := M.J.comp T.symm.toLinearMap
  symmetric z := M.symmetric (T.symm z)
  injective := M.injective.comp T.symm.injective
  interior := T M.interior
  interior_posDef := by simpa using M.interior_posDef

@[simp] theorem transport_apply (T : E ≃ₗ[ℝ] F) (z : E) :
    (M.transport T).J (T z) = M.J z := by simp [transport]

@[simp] theorem transport_mass (T : E ≃ₗ[ℝ] F) (z : E) :
    (M.transport T).mass (T z) = M.mass z := by simp [mass]

theorem transport_cone (T : E ≃ₗ[ℝ] F) : (M.transport T).cone = T '' M.cone := by
  ext z
  constructor
  · intro hz
    exact ⟨T.symm z, hz, T.apply_symm_apply z⟩
  · rintro ⟨x, hx, rfl⟩
    simpa only [mem_cone, transport_apply] using hx

/-- The same weighted factors certify every conjugated branch in the new atlas. -/
def CongruenceCertificate.transport (cert : M.CongruenceCertificate B)
    (T : E ≃ₗ[ℝ] F) : (M.transport T).CongruenceCertificate
      (ConditionalStochasticCompletion.atlasOperator T B) where
  terms := cert.terms
  weight := cert.weight
  weight_nonneg := cert.weight_nonneg
  factor := cert.factor
  identity s z := by
    change M.J (T.symm (T (B s (T.symm z)))) = _
    simpa only [LinearEquiv.symm_apply_apply, Embedding.transport, LinearMap.comp_apply,
      LinearEquiv.coe_coe] using cert.identity s (T.symm z)

theorem transport_word_trace (T : E ≃ₗ[ℝ] F) (word : List S) (z : E) :
    (M.transport T).mass
      (FiniteInstruments.wordAction (ConditionalStochasticCompletion.atlasOperator T B)
        word (T z)) = M.mass (FiniteInstruments.wordAction B word z) := by
  rw [ConditionalStochasticCompletion.atlas_word, M.transport_mass]

end Atlas
end Embedding
end Komorebi.LSM.MatrixEmbedding
