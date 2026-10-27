import ProofPath.Transport
import ProofPath.Recovery

namespace ProofPath
namespace ExtensionExamples

def conjunction : Field (Fin 3) Unit where
  leaf := ∅
  premises _ := {0, 1}
  conclusion _ := 2
  certified _ := True

theorem forbidden_two_derived : (2 : Fin 3) ∈ conjunction.closure {0, 1} := by
  apply Field.Derives.step () trivial
  intro v hv
  exact conjunction.closure_contains_seed {0, 1} hv

theorem conjunction_obstructed :
    ¬ ∃ x, conjunction.Extends {0, 1} {2} x := by
  apply (conjunction.infeasible_iff_forbidden_derivation _ _).mpr
  exact ⟨2, by simp, forbidden_two_derived⟩

theorem partial_a_false_c_feasible :
    ∃ x, conjunction.Extends {0} {2} x := by
  refine ⟨fun v => v = 0, ⟨?_, ?_⟩, ?_, ?_⟩
  · intro v hv
    exact False.elim hv
  · intro _ _ hp
    have h : (1 : Fin 3) = 0 := hp 1 (by simp [conjunction])
    exact False.elim ((by decide : (1 : Fin 3) ≠ 0) h)
  · intro v hv
    exact Set.mem_singleton_iff.mp hv
  · intro v hv
    have h : v = 2 := Set.mem_singleton_iff.mp hv
    rw [h]
    decide

def source : Field Bool Empty where
  leaf := ∅
  premises := Empty.elim
  conclusion := Empty.elim
  certified := Empty.elim

def target : Field Unit Empty where
  leaf := ∅
  premises := Empty.elim
  conclusion := Empty.elim
  certified := Empty.elim

def collapse : RuleTransport source target where
  node _ := ()
  rule := Empty.elim
  leaves := by intro _ h; exact False.elim h
  certified := by intro j; exact Empty.elim j
  premises := by intro j; exact Empty.elim j
  conclusion := by intro j; exact Empty.elim j

theorem source_feasible : ∃ x, source.Extends {false} {true} x := by
  refine ⟨fun b => b = false, ⟨?_, ?_⟩, ?_, ?_⟩
  · intro v h; exact False.elim h
  · intro j; exact Empty.elim j
  · intro v hv; exact Set.mem_singleton_iff.mp hv
  · intro v hv
    have h : v = true := Set.mem_singleton_iff.mp hv
    rw [h]
    decide

theorem collapsed_target_infeasible :
    ¬ ∃ x, target.Extends (collapse.node '' {false}) (collapse.node '' {true}) x := by
  rintro ⟨x, hx⟩
  exact hx.2.2 () ⟨true, by simp, rfl⟩ (hx.2.1 () ⟨false, by simp, rfl⟩)

end ExtensionExamples
end ProofPath
