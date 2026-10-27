import PaperXI.SchrodingerFourier
import PaperXI.SchrodingerSeparation
import Mathlib.RepresentationTheory.Irreducible

/-! Irreducibility of the finite Schrödinger action from its actual translation
and dual-character multiplication operators. The proof uses coordinate
projections and spans all functions, including the zero-dimensional case. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SchrodingerIrreducible

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X] [Fintype X]

/-- Every subspace invariant under translations and all nontrivial scalar
character modulations is either zero or the full function space. -/
theorem invariant_eq_bot_or_top (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
    (S : Submodule ℂ (X → ℂ))
    (htranslation : ∀ x f, f ∈ S → (fun u => f (u + x)) ∈ S)
    (hmodulation : ∀ (ξ : Module.Dual K X) f, f ∈ S →
      (fun u => ψ (ξ u) * f u) ∈ S) : S = ⊥ ∨ S = ⊤ := by
  classical
  by_cases hbot : S = ⊥
  · exact Or.inl hbot
  right
  obtain ⟨f, hf, hfne⟩ := S.ne_bot_iff.mp hbot
  have hex : ∃ u : X, f u ≠ 0 := by
    by_contra h
    push Not at h
    exact hfne (funext h)
  obtain ⟨u, hu⟩ := hex
  have hsep : ∀ u v : X, u ≠ v →
      ∃ ξ : Module.Dual K X, ψ (ξ u) ≠ ψ (ξ v) :=
    fun _ _ huv => SchrodingerSeparation.exists_dual_character_ne hψ huv
  have hunit : (fun x => if x = u then (1 : ℂ) else 0) ∈ S :=
    SchrodingerFourier.coordinate_unit_mem (fun (ξ : Module.Dual K X) x => ψ (ξ x)) hsep S
      hmodulation u f hf hu
  have hall : ∀ v : X, (fun x => if x = v then (1 : ℂ) else 0) ∈ S := by
    intro v
    have h := htranslation (u - v) _ hunit
    convert h using 1
    funext x
    have heq : x + (u - v) = u ↔ x = v := by
      constructor
      · intro he
        calc
          x = (x + (u - v)) - u + v := by abel
          _ = v := by rw [he]; abel
      · rintro rfl
        abel
    simp only [heq]
  apply top_unique
  intro g _
  rw [pi_eq_sum_univ g]
  apply S.sum_mem
  intro v _
  apply S.smul_mem
  simpa only [eq_comm] using hall v

/-- Any actual representation containing every translation and dual modulation
is irreducible in Mathlib's subrepresentation sense. -/
theorem irreducible_of_actions {G : Type*} [Monoid G]
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (ρ : Representation ℂ G (X → ℂ))
    (htranslation : ∀ x : X, ∃ g : G, ∀ (f : X → ℂ) (u : X),
      ρ g f u = f (u + x))
    (hmodulation : ∀ ξ : Module.Dual K X, ∃ g : G, ∀ (f : X → ℂ) (u : X),
      ρ g f u = ψ (ξ u) * f u) : Representation.IsIrreducible ρ := by
  change IsSimpleOrder (Subrepresentation ρ)
  refine { exists_pair_ne := ?_, eq_bot_or_eq_top := ?_ }
  · refine ⟨⊥, ⊤, fun h => ?_⟩
    exact bot_ne_top (congrArg Subrepresentation.toSubmodule h)
  · intro S
    have ht : ∀ x f, f ∈ S.toSubmodule → (fun u => f (u + x)) ∈ S.toSubmodule := by
      intro x f hf
      obtain ⟨g, hg⟩ := htranslation x
      have h := S.apply_mem_toSubmodule g hf
      convert h using 1
      exact (funext (hg f)).symm
    have hm : ∀ (ξ : Module.Dual K X) f, f ∈ S.toSubmodule →
        (fun u => ψ (ξ u) * f u) ∈ S.toSubmodule := by
      intro ξ f hf
      obtain ⟨g, hg⟩ := hmodulation ξ
      have h := S.apply_mem_toSubmodule g hf
      convert h using 1
      exact (funext (hg f)).symm
    rcases invariant_eq_bot_or_top ψ hψ S.toSubmodule ht hm with h | h
    · exact Or.inl (Subrepresentation.toSubmodule_injective h)
    · exact Or.inr (Subrepresentation.toSubmodule_injective h)
end PaperXI.SchrodingerIrreducible
