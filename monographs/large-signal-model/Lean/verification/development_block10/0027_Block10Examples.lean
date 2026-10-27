import KomorebiLSM.RationalCertificateSoundness

/-! Exact examples and failures for P45. -/
set_option autoImplicit false
namespace Komorebi.LSM.Block10Examples
open scoped BigOperators
open RationalSearch

def oneCertificate : Candidate 1 1 := ⟨1,1,(fun _ => 1),(fun _ => 1),1⟩
def zeroBranchCertificate : Candidate 1 2 :=
  ⟨1,1,(fun t => if t = 0 then 1 else 0),(fun _ => 1),1⟩
def signedCertificate : Candidate 1 1 := ⟨1,1,(fun _ => -1),(fun _ => 1),1⟩
def singularCertificate : Candidate 2 1 := ⟨1,(fun _ _ => 1),(fun _ => 1),(fun _ => 1),0⟩

theorem one_certificate_valid : Valid (fun _ => 1) (fun _ => 1) (fun _ => 1) oneCertificate := by
  unfold oneCertificate Valid synthesis lifts initial rightInverse
  dsimp only
  norm_num [Matrix.mul_apply,Matrix.mulVec,dotProduct,Matrix.one_apply,
    funext_iff,Fin.forall_fin_one,Fin.forall_fin_two]

theorem zero_branch_certificate_valid : Valid (fun _ => 1) (fun _ => 1)
    (fun t => if t = 0 then 1 else 0) zeroBranchCertificate := by
  unfold zeroBranchCertificate Valid synthesis lifts initial rightInverse
  dsimp only
  norm_num [Matrix.mul_apply,Matrix.mulVec,dotProduct,Matrix.one_apply,
    funext_iff,Fin.forall_fin_one,Fin.forall_fin_two]

theorem signed_lift_rejected : ¬ Valid (fun _ => 1) (fun _ => 1) (fun _ => -1) signedCertificate := by
  unfold signedCertificate Valid synthesis lifts initial rightInverse
  dsimp only
  norm_num [Matrix.mul_apply,Matrix.mulVec,dotProduct,Matrix.one_apply,
    funext_iff,Fin.forall_fin_one,Fin.forall_fin_two]

theorem singular_generators_rejected : ¬ Valid (fun i => if i = 0 then 1 else 0)
    (fun _ => 1) (fun _ => 1) singularCertificate := by
  unfold singularCertificate Valid synthesis lifts initial rightInverse
  dsimp only
  norm_num [Matrix.mul_apply,Matrix.mulVec,dotProduct,Matrix.one_apply,
    funext_iff,Fin.forall_fin_one,Fin.forall_fin_two]

theorem exact_checker_finds_encoded : checkCode (fun _ => 1) (fun _ => 1) (fun _ => 1)
    (Encodable.encode oneCertificate) = some oneCertificate :=
  checkCode_encode _ _ _ _ one_certificate_valid

theorem bounded_failure_not_impossibility :
    search (fun _ => 1) (fun _ => 1) (fun _ => 1) 0 = (none : Option (Candidate 1 1)) ∧
    ∃ c : Candidate 1 1, Valid (fun _ => 1) (fun _ => 1) (fun _ => 1) c :=
  ⟨rfl,oneCertificate,one_certificate_valid⟩

theorem rational_boundary_solution :
    ∃ q : Fin 2 → ℚ, (∀ j, 0 ≤ q j) ∧ q 0 = 0 ∧ q 1 = 1 := by
  refine ⟨![0,1],?_,rfl,rfl⟩
  intro j
  fin_cases j <;> norm_num

/-- Exact mass alone does not establish branch positivity. -/
theorem mass_without_positivity :
    (2 : ℚ) + (-1) = 1 ∧ ¬ 0 ≤ (-1 : ℚ) := by norm_num

end Komorebi.LSM.Block10Examples
