import PaperXII.S3Standard
import PaperXII.S3Spectrum
import PaperXII.S3Adjoint
import PaperXII.S3Detection
import PaperXII.FiniteGroupCohomology
import Mathlib.FieldTheory.IsAlgClosed.AlgebraicClosure

/-!
# The finite adequacy certificate in original Claim 4.2

The four adequacy clauses use actual group cohomology and every irreducible
subrepresentation of the actual trace-zero conjugation representation. The
ambient faithful, absolutely irreducible, split standard representation and
the two literal constituent witnesses are recorded in the final certificate.
No adequacy theorem is taken as an input.
-/

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
namespace PaperXII.FiniteAdequacy

open S3Standard S3Adjoint S3Detection FiniteGroupCohomology

/-- The trace criterion is quantified over every actual irreducible adjoint submodule. -/
def TraceDetection : Prop :=
  ∀ (N : Subrepresentation adjoint), Representation.IsIrreducible (k := K) (G := Group) (V := N.toSubmodule) N.toRepresentation →
    ∃ (g : Group) (α β : K) (P : S3Adjoint.Mat) (w : Adj),
      CanonicalProjector (matrixRep K g) α β P ∧ w ∈ N ∧
        Matrix.trace (P * (w : S3Adjoint.Mat)) ≠ 0

/-- The four clauses of adequacy, for the standard S3 representation over F7. -/
structure Adequate : Prop where
  h0_adjoint : Subsingleton (groupCohomology (Rep.of adjoint) 0)
  h1_trivial : Subsingleton (groupCohomology (Rep.trivial K Group K) 1)
  h1_adjoint : Subsingleton (groupCohomology (Rep.of adjoint) 1)
  detection : TraceDetection

/-- An irreducible subrepresentation has a nonzero underlying subspace. -/
theorem irreducible_subrepresentation_ne_bot (N : Subrepresentation adjoint)
    (hN : Representation.IsIrreducible (k := K) (G := Group) (V := N.toSubmodule) N.toRepresentation) : N ≠ ⊥ := by
  intro h
  have := hN
  have heq : (⊥ : Subrepresentation N.toRepresentation) = ⊤ := by
    apply Subrepresentation.toSubmodule_injective
    apply le_antisymm le_top
    intro v _
    have hv : (v : Adj) = 0 := by
      change (v : Adj) ∈ (⊥ : Subrepresentation adjoint).toSubmodule
      simpa only [h] using v.property
    have hz : v = 0 := Subtype.ext hv
    rw [hz]
    exact Submodule.zero_mem _
  exact bot_ne_top heq

/-- Separation of all matrices gives the required detection on every irreducible submodule. -/
theorem trace_detection : TraceDetection := by
  intro N hN
  have hn : N.toSubmodule ≠ ⊥ := fun h =>
    irreducible_subrepresentation_ne_bot N hN (Subrepresentation.toSubmodule_injective h)
  obtain ⟨w, hw, hw0⟩ := Submodule.exists_mem_ne_zero_of_ne_bot hn
  have hm : (w : S3Adjoint.Mat) ≠ 0 := fun h => hw0 (Subtype.ext h)
  obtain ⟨g, α, β, P, hp, ht⟩ := detects_every_nonzero (w : S3Adjoint.Mat) hm
  exact ⟨g, α, β, P, w, hp, hw, ht⟩

/-- The concrete four-clause adequacy assertion. -/
theorem adequate : Adequate where
  h0_adjoint := h0_subsingleton_of_fixed_eq_zero (Rep.of adjoint) fixed_eq_zero
  h1_trivial := s3_h1_subsingleton (Rep.trivial K Group K)
  h1_adjoint := s3_h1_subsingleton (Rep.of adjoint)
  detection := trace_detection

/-- Coefficient extension is the same matrix representation over the extension field. -/
theorem extension_matrix {L : Type*} [Field L] [Algebra K L] (g : Group) :
    (matrixRep K g).map (algebraMap K L) = matrixRep L g :=
  matrixRep_map K (algebraMap K L) g

/-- Irreducibility persists over the algebraic closure of the original coefficient field. -/
theorem absolutely_irreducible :
    Representation.IsIrreducible (rep (AlgebraicClosure K)) := irreducible_char_seven

/-- Complete ambient hypotheses and the precise additional assertions printed in Claim 4.2. -/
structure StandardCertificate : Prop where
  faithful : Function.Injective (rep K)
  absolutely_irreducible : Representation.IsIrreducible (rep (AlgebraicClosure K))
  split : ∀ g : Group, (matrixRep K g).charpoly.Splits
  adequate : Adequate
  decomposition : Nonempty ((signRep.prod (rep K)).Equiv adjoint)
  sign_member : (⟨W 2 3 4, trace_W 2 3 4⟩ : Adj) ∈ signSummand
  sign_projector : CanonicalProjector (matrixRep K cycle) 2 4 Pt2
  sign_trace : Matrix.trace (Pt2 * W 2 3 4) = 3 ∧ (3 : K) ≠ 0
  standard_member : (⟨W 6 4 3, trace_W 6 4 3⟩ : Adj) ∈ standardSummand
  standard_projector : CanonicalProjector (matrixRep K transposition) 1 (-1) Ps1
  standard_trace : Matrix.trace (Ps1 * W 6 4 3) = 6 ∧ (6 : K) ≠ 0

/-- Original Claim 4.2, with no additional mathematical hypotheses. -/
theorem standard_S3_F7 : StandardCertificate where
  faithful := rep_faithful K
  absolutely_irreducible := absolutely_irreducible
  split := S3Spectrum.all_charpolys_split
  adequate := adequate
  decomposition := ⟨decompositionEquiv⟩
  sign_member := W_sign_mem
  sign_projector := pt2_canonical
  sign_trace := ⟨trace_sign_witness, by decide⟩
  standard_member := W_standard_mem
  standard_projector := ps1_canonical
  standard_trace := ⟨trace_standard_witness, by decide⟩

end PaperXII.FiniteAdequacy
