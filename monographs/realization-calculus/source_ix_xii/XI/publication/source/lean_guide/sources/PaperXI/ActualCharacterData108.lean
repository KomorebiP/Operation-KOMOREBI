import PaperXI.ActualHeisenbergCandidate107
import PaperXI.CharacterSupport108

/-! Character occurrence on the actual prescribed kappa carrier, with its
normality and invariance derived from the literal character normalizer. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualCharacterData108
open Matrix ValuativeRel Representation
open ActualCharacterType61 ActualCuspidalCandidate105
open ActualELatticeTopology60 LatticeCongruenceTopology60
variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)
  (hDc : D ≤ matrixCongruence F E m n e)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
include hDc in
theorem domain_le_compact : D ≤ compact F E m n e D θ :=
  domain_le_compactGroup F E m n e D θ
    (hDc.trans (matrixCongruence_le_chainGroup F E m n e))

def intoCompact : D →* compact F E m n e D θ :=
  Subgroup.inclusion (domain_le_compact F E m n e D θ hDc)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
theorem intoCompact_mem_first (d : D) :
    intoCompact F E m n e D θ hDc d ∈ firstSubgroup F E m n e D θ := hDc d.property

variable {W : Type*} [AddCommGroup W] [Module ℂ W]
  (κ : Representation ℂ (compact F E m n e D θ) W)

/-- Literal character occurrence on the existing carrier. -/
def Contains : Prop :=
  ∃ v : W, v ≠ 0 ∧ ∀ d : D, κ (intoCompact F E m n e D θ hDc d) v = (θ d : ℂ) • v

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m] [Nonempty n] in
theorem scalar_restriction [IsIrreducible (κ.comp (firstSubgroup F E m n e D θ).subtype)]
    (hc : Contains F E m n e D θ hDc κ) (d : D) :
    κ (intoCompact F E m n e D θ hDc d) = (θ d : ℂ) • LinearMap.id := by
  let : IsIrreducible κ := CharacterAttachment108.irreducible_of_restriction
    (firstSubgroup F E m n e D θ) κ
  exact CharacterAttachment108.scalar_of_contains D (compact F E m n e D θ)
    (domain_le_compact F E m n e D θ hDc) θ (fun _ h => h.1) κ hc d

end PaperXI.ActualCharacterData108
