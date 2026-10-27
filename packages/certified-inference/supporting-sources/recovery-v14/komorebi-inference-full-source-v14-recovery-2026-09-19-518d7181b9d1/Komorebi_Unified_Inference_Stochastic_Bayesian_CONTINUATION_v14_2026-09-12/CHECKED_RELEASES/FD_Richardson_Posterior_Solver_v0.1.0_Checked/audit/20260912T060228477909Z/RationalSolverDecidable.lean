import Komorebi.RationalCertificateChecker

set_option autoImplicit false
namespace Komorebi.ExactPosterior
variable {ι κ α β : Type*} [Fintype ι] [Fintype κ] [Fintype α] [Fintype β]

/-- Executable equality for finite candidate records, used by concrete kernel reductions. -/
instance candidateDecidableEq : DecidableEq (RationalCandidate ι κ α β) := by
  intro c d
  cases c with
  | mk g u v =>
    cases d with
    | mk g' u' v' =>
      exact decidable_of_iff (g=g' ∧ u=u' ∧ v=v') RationalCandidate.mk.injEq.symm
end Komorebi.ExactPosterior
