import ProofPath.TraceWire

/-! Generated concrete records. Acceptance is kernel-normalized with decide;
not inferred from Python's PASS flag. JSON text and address books remain in
examples/trace_exchange for independent input correspondence checks. -/
namespace ProofPath.Trace.Fixtures
open Wire

def andPositiveProblem : Problem := ⟨8, [0], [⟨[7], 1⟩, ⟨[4], 2⟩, ⟨[0], 3⟩, ⟨[3], 4⟩, ⟨[0, 3], 6⟩, ⟨[6], 7⟩], [], []⟩
def andPositiveCertificate : Certificate := ⟨true, [0, 1, 2, 3, 4, 6, 7], [2, 3, 4, 5, 0, 1], none⟩
theorem andPositive_accepted : accept andPositiveProblem andPositiveCertificate = true := by decide
theorem andPositive_checked : CertifiedAnswer andPositiveProblem andPositiveCertificate :=
  acceptance_sound _ _ andPositive_accepted

def andNegativeProblem : Problem := ⟨8, [0], [⟨[7], 1⟩, ⟨[4], 2⟩, ⟨[0], 3⟩, ⟨[3], 4⟩, ⟨[0, 3], 6⟩, ⟨[6], 7⟩], [], [1]⟩
def andNegativeCertificate : Certificate := ⟨false, [0, 1, 2, 3, 4, 6, 7], [2, 3, 4, 5, 0, 1], some ⟨1, [2, 4, 5, 0]⟩⟩
theorem andNegative_accepted : accept andNegativeProblem andNegativeCertificate = true := by decide
theorem andNegative_checked : CertifiedAnswer andNegativeProblem andNegativeCertificate :=
  acceptance_sound _ _ andNegative_accepted

def alternativePositiveProblem : Problem := ⟨4, [0], [⟨[2], 1⟩, ⟨[3], 1⟩, ⟨[0], 2⟩, ⟨[0], 3⟩], [], []⟩
def alternativePositiveCertificate : Certificate := ⟨true, [0, 1, 2, 3], [2, 3, 0], none⟩
theorem alternativePositive_accepted : accept alternativePositiveProblem alternativePositiveCertificate = true := by decide
theorem alternativePositive_checked : CertifiedAnswer alternativePositiveProblem alternativePositiveCertificate :=
  acceptance_sound _ _ alternativePositive_accepted

def alternativeNegativeProblem : Problem := ⟨4, [0], [⟨[2], 1⟩, ⟨[3], 1⟩, ⟨[0], 2⟩, ⟨[0], 3⟩], [], [1]⟩
def alternativeNegativeCertificate : Certificate := ⟨false, [0, 1, 2, 3], [2, 3, 0], some ⟨1, [2, 0]⟩⟩
theorem alternativeNegative_accepted : accept alternativeNegativeProblem alternativeNegativeCertificate = true := by decide
theorem alternativeNegative_checked : CertifiedAnswer alternativeNegativeProblem alternativeNegativeCertificate :=
  acceptance_sound _ _ alternativeNegative_accepted

def seededCycleProblem : Problem := ⟨2, [], [⟨[0], 1⟩, ⟨[1], 0⟩], [0], [1]⟩
def seededCycleCertificate : Certificate := ⟨false, [0, 1], [0], some ⟨1, [0]⟩⟩
theorem seededCycle_accepted : accept seededCycleProblem seededCycleCertificate = true := by decide
theorem seededCycle_checked : CertifiedAnswer seededCycleProblem seededCycleCertificate :=
  acceptance_sound _ _ seededCycle_accepted

def emptyProblemProblem : Problem := ⟨0, [], [], [], []⟩
def emptyProblemCertificate : Certificate := ⟨true, [], [], none⟩
theorem emptyProblem_accepted : accept emptyProblemProblem emptyProblemCertificate = true := by decide
theorem emptyProblem_checked : CertifiedAnswer emptyProblemProblem emptyProblemCertificate :=
  acceptance_sound _ _ emptyProblem_accepted

end ProofPath.Trace.Fixtures
