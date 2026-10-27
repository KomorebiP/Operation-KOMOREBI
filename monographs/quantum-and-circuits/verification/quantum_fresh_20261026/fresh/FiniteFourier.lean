import QuantumArithmeticBridge

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000

namespace Komorebi.QuantumArithmetic

abbrev Index := Fin 12
abbrev KVector := Index → Cyclo12
abbrev KMatrix := Index → Index → Cyclo12

def kSum (f : Index → Cyclo12) : Cyclo12 := cSum (List.ofFn f)

def kIdentity : KMatrix := fun i j => if i = j then cOne else cZero

def kAdjoint (A : KMatrix) : KMatrix := fun i j => cConj (A j i)

def kMatMul (A B : KMatrix) : KMatrix := fun i j =>
  kSum (fun k => cMul (A i k) (B k j))

def kMatVec (A : KMatrix) (v : KVector) : KVector := fun i =>
  kSum (fun j => cMul (A i j) (v j))

/-- sqrt(3)/6 = 1/sqrt(12). Its interpretation is proved separately. -/
def fourierScale : Cyclo12 := ⟨0, (1/6 : ℚ), 0, 0⟩

/-- sqrt(3)/12 = 1/sqrt(48). -/
def stateScale : Cyclo12 := ⟨0, (1/12 : ℚ), 0, 0⟩

def rootPower (n : Nat) : Cyclo12 := cPow zeta12 (n % 12)

def exactFourier : KMatrix := fun i j =>
  cMul fourierScale (rootPower (i.val * j.val))

def exactSelector : KMatrix := fun i j =>
  if i = j ∧ Nat.gcd i.val 12 = 1 then cOne else cZero

def exactProjector : KMatrix := fun i j =>
  cRat ((ramanujan12.getD ((i.val + 12 - j.val) % 12) 0) / 12)

def exactUnitState : KVector := fun i =>
  if Nat.gcd i.val 12 = 1 then cRat (1/2) else cZero

def exactPsi : KVector := fun i =>
  cMul stateScale (cRat (ramanujan12.getD i.val 0))

def exactChi : KVector := fun i =>
  cMul stateScale (cRat (absRamanujan12.getD i.val 0))

def kNormSq (z : Cyclo12) : Cyclo12 := cMul (cConj z) z

def kMass (v : KVector) : Cyclo12 := kSum (fun i => kNormSq (v i))

def kCoprimeMass (v : KVector) : Cyclo12 :=
  kSum (fun i => if Nat.gcd i.val 12 = 1 then kNormSq (v i) else cZero)

/-- The stored arithmetic selector is exactly the coprimality predicate. -/
theorem coprime_residues_exact :
    (List.range 12).filter (fun a => Nat.gcd a 12 == 1) = unitResidues12 := by
  decide +kernel

theorem root_exact_order :
    ∀ n : Fin 12, 0 < n.val → cPow zeta12 n.val ≠ cOne := by
  decide +kernel

theorem normalized_fourier_left :
    ∀ i j, kMatMul (kAdjoint exactFourier) exactFourier i j = kIdentity i j := by
  decide +kernel

theorem normalized_fourier_right :
    ∀ i j, kMatMul exactFourier (kAdjoint exactFourier) i j = kIdentity i j := by
  decide +kernel

def selectedKernel : KMatrix := fun i j =>
  kSum (fun k => if Nat.gcd k.val 12 = 1 then
    cMul (exactFourier i k) (cConj (exactFourier j k)) else cZero)

theorem exact_projector_transport :
    ∀ i j, selectedKernel i j = exactProjector i j := by
  decide +kernel

theorem exact_projector_matches_rational_table :
    ∀ i j, exactProjector i j = cRat ((projector12.getD i.val []).getD j.val 0) := by
  decide +kernel

theorem exact_state_preparation :
    ∀ i, kMatVec exactFourier exactUnitState i = exactPsi i := by
  decide +kernel

theorem exact_state_recovery :
    ∀ i, kMatVec (kAdjoint exactFourier) exactPsi i = exactUnitState i := by
  decide +kernel

theorem exact_unit_normalized : kMass exactUnitState = cOne := by
  decide +kernel

theorem exact_psi_normalized : kMass exactPsi = cOne := by
  decide +kernel

theorem exact_chi_normalized : kMass exactChi = cOne := by
  decide +kernel

theorem exact_same_initial_probabilities :
    ∀ i, kNormSq (exactPsi i) = kNormSq (exactChi i) := by
  decide +kernel

theorem exact_orthogonal_states :
    kSum (fun i => cMul (cConj (exactPsi i)) (exactChi i)) = cZero := by
  decide +kernel

theorem exact_coprime_mass_psi :
    kCoprimeMass (kMatVec (kAdjoint exactFourier) exactPsi) = cOne := by
  decide +kernel

theorem exact_coprime_mass_chi :
    kCoprimeMass (kMatVec (kAdjoint exactFourier) exactChi) = cZero := by
  decide +kernel

theorem exact_projector_fixes_psi :
    ∀ i, kMatVec exactProjector exactPsi i = exactPsi i := by
  decide +kernel

theorem exact_projector_kills_chi :
    ∀ i, kMatVec exactProjector exactChi i = cZero := by
  decide +kernel

end Komorebi.QuantumArithmetic
