module
public import CostedPrimitives
public import EchelonTemporaryBounds

@[expose] public section
namespace Komorebi.Costed
open Komorebi.Echelon Komorebi.Echelon.Cost

/-- Remainder, comparison, exact quotient, and two tail operations per entry.
Returned coefficients are part of the value, not a precomputed certificate. -/
def coordinatesEval : {n : Nat} → Basis n → (Fin n → ℤ) → Eval (Option (Fin n → ℤ))
  | 0,.nil,_ => (some (fun i => Fin.elim0 i),0)
  | n+1,.cons q _ b B,v =>
    if v 0 % q=0 then
      let c := v 0/q
      let t := coordinatesEval B (tailV v-c • b)
      (t.1.map (Fin.cons c),t.2+2*n+3)
    else (none,2)

@[simp] theorem coordinatesEval_value {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    (coordinatesEval B v).1=coordinates B v := by
  induction B generalizing v with
  | nil => rfl
  | cons q hq b B ih =>
    simp only [coordinatesEval,coordinates]
    split
    · rw [ih]
    · rfl

theorem coordinatesEval_units_le {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    (coordinatesEval B v).2≤n*n+2*n := by
  induction B generalizing v with
  | nil => simp [coordinatesEval]
  | @cons n q hq b B ih =>
    simp only [coordinatesEval]
    split
    · have hh := ih (tailV v-(v 0/q) • b)
      dsimp only at ⊢
      nlinarith
    · dsimp only; nlinarith

/-- Euclidean division and remainder plus multiply/subtract for each tail entry. -/
def residueEval : {n : Nat} → Basis n → (Fin n → ℤ) → Eval (Fin n → ℤ)
  | 0,.nil,_ => (0,0)
  | n+1,.cons q _ b B,v =>
    let c := v 0/q
    let t := residueEval B (tailV v-c • b)
    (Fin.cons (v 0%q) t.1,t.2+2*n+2)

@[simp] theorem residueEval_value {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    (residueEval B v).1=residue B v := by
  induction B generalizing v with
  | nil => rfl
  | cons q hq b B ih => simp only [residueEval,residue,ih]

@[simp] theorem residueEval_units {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    (residueEval B v).2=n*(n+1) := by
  induction B generalizing v with
  | nil => rfl
  | @cons n q hq b B ih => simp only [residueEval,ih]; ring

/-- Bottom-up normalization, charged through the actual residue evaluator. -/
def normalizeEval : {n : Nat} → Basis n → Eval (Basis n)
  | 0,.nil => (.nil,0)
  | _+1,.cons q hq b B =>
    let t := normalizeEval B
    let z := residueEval t.1 b
    (.cons q hq z.1 t.1,t.2+z.2)

@[simp] theorem normalizeEval_value {n : Nat} (B : Basis n) :
    (normalizeEval B).1=normalize B := by
  induction B with
  | nil => rfl
  | cons q hq b B ih => simp only [normalizeEval,normalize,residueEval_value,ih]

def normalizationUnits : Nat → Nat
  | 0 => 0
  | n+1 => normalizationUnits n+n*(n+1)

@[simp] theorem normalizeEval_units {n : Nat} (B : Basis n) :
    (normalizeEval B).2=normalizationUnits n := by
  induction B with
  | nil => rfl
  | cons q hq b B ih => simp only [normalizeEval,residueEval_units,ih,normalizationUnits]

theorem normalizationUnits_cubic (n : Nat) :
    3*normalizationUnits n+n=n*n*n := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [normalizationUnits]; nlinarith

theorem normalizationUnits_le (n : Nat) : normalizationUnits n≤n*n*n := by
  have hh := normalizationUnits_cubic n; omega

/-- Executable insertion: BOTH gcd and Bezout recursions are metered.
The five extra scalar units are two abs operations, two quotients and one negation;
signedEuclidEval separately accounts for its own abs/sign operations. -/
def insertEval : {n : Nat} → Basis n → (Fin n → ℤ) → Eval (Basis n)
  | 0,.nil,_ => (.nil,0)
  | n+1,.cons q hq b B,v =>
    let gd := gcdEval q.natAbs (v 0).natAbs
    let g : ℤ := gd.1
    let z := signedEuclidEval q (v 0)
    let row := z.1.1 • b+z.1.2 • tailV v
    let rem := (-(v 0/g)) • b+(q/g) • tailV v
    let t := insertEval B rem
    (.cons g (by simpa only [g,gcdEval_value,←Int.gcd_def] using
      (bounded_update_data q (v 0) hq).1) row t.1,
      gd.2+z.2+5+6*n+t.2)

@[simp] theorem insertEval_value {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    (insertEval B v).1=boundedInsert B v := by
  induction B generalizing v with
  | nil => rfl
  | cons q hq b B ih =>
    simp only [insertEval,boundedInsert,gcdEval_value,signedEuclidEval_value,ih,Int.gcd_def]

/-- The sum of actual Euclidean recursion lengths along this insertion. -/
def insertionEuclidSum : {n : Nat} → Basis n → (Fin n → ℤ) → Nat
  | 0,.nil,_ => 0
  | _+1,.cons q _ b B,v =>
    euclidSteps q.natAbs (v 0).natAbs+
    insertionEuclidSum B
      ((-(v 0/(Int.gcd q (v 0):ℤ))) • b+(q/(Int.gcd q (v 0):ℤ)) • tailV v)

@[simp] theorem insertEval_units {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    (insertEval B v).2=3*n*n+8*n+7*insertionEuclidSum B v := by
  induction B generalizing v with
  | nil => rfl
  | @cons n q hq b B ih =>
    simp only [insertEval,gcdEval_units,signedEuclidEval_units,gcdEval_value,
      ih,insertionEuclidSum,Int.gcd_def]
    ring

/-- The existing arithmetic peak bounds every candidate argument to Euclid. -/
theorem insertionEuclidSum_le {n : Nat} (B : Basis n) (v : Fin n → ℤ) (bits : Nat)
    (hp : insertionPeak B v<(2:ℤ)^bits) :
    insertionEuclidSum B v≤2*bits*n := by
  induction B generalizing v with
  | nil => simp [insertionEuclidSum]
  | @cons n q hq b B ih =>
    simp only [insertionPeak,max_lt_iff] at hp
    rcases hp with ⟨hv,_,_,_,_,_,_,_,_,_,_,_,_,_,ht⟩
    have ha : (v 0).natAbs<2^bits := by
      have hh : |v 0|<(2:ℤ)^bits := lt_of_le_of_lt (coord_le_peak v 0) hv
      rw [←Int.natCast_natAbs] at hh
      exact_mod_cast hh
    have he := euclidSteps_binary_bound bits q.natAbs (v 0).natAbs ha
    have hi := ih _ ht
    simp only [insertionEuclidSum]
    nlinarith

theorem insertEval_units_le {n : Nat} (B : Basis n) (v : Fin n → ℤ) (bits : Nat)
    (hp : insertionPeak B v<(2:ℤ)^bits) :
    (insertEval B v).2≤3*n*n+8*n+14*bits*n := by
  rw [insertEval_units]
  have hh := insertionEuclidSum_le B v bits hp
  omega

/-- Normalized insertion shares the computed raw result with its normalizer. -/
def updateEval {n : Nat} (B : Basis n) (v : Fin n → ℤ) : Eval (Basis n) :=
  let t := insertEval B v
  let z := normalizeEval t.1
  (z.1,t.2+z.2)

@[simp] theorem updateEval_value {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    (updateEval B v).1=boundedNormalizedInsert B v := by
  simp only [updateEval,normalizeEval_value,insertEval_value,boundedNormalizedInsert]

@[simp] theorem updateEval_units {n : Nat} (B : Basis n) (v : Fin n → ℤ) :
    (updateEval B v).2=3*n*n+8*n+7*insertionEuclidSum B v+normalizationUnits n := by
  simp only [updateEval,normalizeEval_units,insertEval_units]

theorem updateEval_units_le {n : Nat} (B : Basis n) (v : Fin n → ℤ) (bits : Nat)
    (hp : insertionPeak B v<(2:ℤ)^bits) :
    (updateEval B v).2≤3*n*n+8*n+14*bits*n+n*n*n := by
  simp only [updateEval,normalizeEval_units]
  have hi := insertEval_units_le B v bits hp
  have hn := normalizationUnits_le n
  omega

end Komorebi.Costed
