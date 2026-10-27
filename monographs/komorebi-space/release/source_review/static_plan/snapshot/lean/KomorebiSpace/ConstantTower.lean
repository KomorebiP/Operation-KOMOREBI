import KomorebiSpace.BanachTowers

set_option autoImplicit false

/-!
# A non-vacuous canonical model

For a tower with identity bonding maps, exact transports are precisely constant
operator families. Every bounded candidate has a unique exact repair preserving
its level-zero operator. No residual-proportional error estimate is asserted.
-/
universe u v
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace BanachTower
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (E F : Type v) [NormedAddCommGroup E] [NormedSpace 𝕜 E] [CompleteSpace E]
variable [NormedAddCommGroup F] [NormedSpace 𝕜 F] [CompleteSpace F]

def constant : BanachTower.{u,v} 𝕜 where
  Obj _ := E
  down _ := ContinuousLinearMap.id 𝕜 E
  bound := 1
  down_bound _ := ContinuousLinearMap.norm_id_le

variable {E F}

def constantCandidate (T : E →L[𝕜] F) :
    Candidates (constant (𝕜 := 𝕜) E) (constant (𝕜 := 𝕜) F) :=
  ⟨fun _ => T, memℓp_infty ⟨‖T‖, by rintro _ ⟨n, rfl⟩; exact le_rfl⟩⟩

@[simp] theorem constantCandidate_apply (T : E →L[𝕜] F) (n : ℕ) :
    constantCandidate T n = T := rfl

theorem constantCandidate_exact (T : E →L[𝕜] F) :
    Exact (constant E) (constant F) (constantCandidate T) := by
  intro n
  ext x
  rfl

/-- A characterization of all exact maps, not merely a chosen example. -/
theorem constant_exact_iff
    (f : Candidates (constant (𝕜 := 𝕜) E) (constant (𝕜 := 𝕜) F)) :
    Exact (constant E) (constant F) f ↔ ∀ n, f n = f 0 := by
  constructor
  · intro hf n
    induction n with
    | zero => rfl
    | succ n ih =>
      have hn : f (n+1) = f n := by
        ext x
        exact congrArg (fun T : E →L[𝕜] F => T x) (hf n)
      exact hn.trans ih
  · intro hf n
    ext x
    change f (n+1) x = f n x
    rw [hf (n+1), hf n]
    rfl

/-- Uniqueness follows from the actual identity-tower structure. -/
theorem constant_unique_repair
    (f : Candidates (constant (𝕜 := 𝕜) E) (constant (𝕜 := 𝕜) F)) :
    ∃! g : Candidates (constant (𝕜 := 𝕜) E) (constant (𝕜 := 𝕜) F),
      Exact (constant E) (constant F) g ∧ g 0 = f 0 := by
  refine ⟨constantCandidate (f 0), ⟨constantCandidate_exact _, rfl⟩, ?_⟩
  intro g hg
  apply lp.ext
  funext n
  exact ((constant_exact_iff g).mp hg.1 n).trans hg.2

/-- The inverse limit of an identity tower is actually its underlying Banach space. -/
def constantPointEquiv : (constant (𝕜 := 𝕜) E).Point ≃ E where
  toFun x := x.val 0
  invFun x := ⟨fun _ => x, fun _ => rfl⟩
  left_inv x := by
    apply Subtype.ext
    funext n
    change x.val 0 = x.val n
    induction n with
    | zero => rfl
    | succ n ih =>
      have hn : x.val (n+1) = x.val n := x.property n
      exact ih.trans hn.symm
  right_inv _ := rfl

/-- After these equivalences, realization recovers the supplied operator exactly. -/
theorem constant_realization (T : E →L[𝕜] F) (x : E) :
    constantPointEquiv
      (onLimit (constant E) (constant F) (constantCandidate T)
        (constantCandidate_exact T) (constantPointEquiv.symm x)) = T x := rfl

end BanachTower
end KomorebiSpace
end
