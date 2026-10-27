import Mathlib.Data.Set.Function

namespace ProofPath

/-- Task sufficiency is factorization, not the length of an encoding. -/
def Sufficient {A B C : Type*} (encode : A → B) (task : A → C) : Prop :=
  ∃ decode : B → C, ∀ a, decode (encode a) = task a

theorem collision_obstructs_sufficiency {A B C : Type*}
    (encode : A → B) (task : A → C) {a b : A}
    (hc : encode a = encode b) (ht : task a ≠ task b) :
    ¬ Sufficient encode task := by
  rintro ⟨decode, hd⟩
  exact ht ((hd a).symm.trans ((congrArg decode hc).trans (hd b)))

/-- Losslessness means injectivity. It does not require identical bytes. -/
theorem all_predicates_sufficient_iff_injective {A B : Type*} (encode : A → B) :
    (∀ task : A → Prop, Sufficient encode task) ↔ Function.Injective encode := by
  constructor
  · intro h a b he
    obtain ⟨d, hd⟩ := h (fun x => x = a)
    have hba : (b = a) = (a = a) := (hd b).symm.trans ((congrArg d he.symm).trans (hd a))
    exact (Eq.mp hba.symm rfl).symm
  · intro hi task
    refine ⟨fun b => ∃ a, encode a = b ∧ task a, ?_⟩
    intro a
    apply propext
    constructor
    · rintro ⟨a', he, ht⟩
      exact hi he ▸ ht
    · exact fun ht => ⟨a, rfl, ht⟩

end ProofPath
