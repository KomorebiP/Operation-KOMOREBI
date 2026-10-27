module
public import Mathlib.Data.Int.GCD
public import Mathlib.Data.Fin.VecNotation
public import Mathlib.LinearAlgebra.Span.Basic
public import Mathlib.Tactic

@[expose] public section
namespace Komorebi.Echelon

def tailV {n : Nat} (x : Fin (n+1) → ℤ) : Fin n → ℤ := fun i => x i.succ
@[simp] theorem tailV_zero {n : Nat} : tailV (0 : Fin (n+1) → ℤ) = 0 := rfl
@[simp] theorem tailV_add {n : Nat} (x y : Fin (n+1) → ℤ) :
    tailV (x+y) = tailV x + tailV y := rfl
@[simp] theorem tailV_smul {n : Nat} (a : ℤ) (x : Fin (n+1) → ℤ) :
    tailV (a • x) = a • tailV x := rfl
@[simp] theorem tailV_cons {n : Nat} (a : ℤ) (x : Fin n → ℤ) :
    tailV (Fin.cons a x) = x := rfl

/-- A full-rank triangular integer basis. Positivity belongs to the data contract. -/
inductive Basis : Nat → Type where
  | nil : Basis 0
  | cons {n : Nat} (pivot : ℤ) (positive : 0 < pivot)
      (tail : Fin n → ℤ) (rest : Basis n) : Basis (n+1)

def synth : {n : Nat} → Basis n → (Fin n → ℤ) → (Fin n → ℤ)
  | 0, .nil, _ => 0
  | _+1, .cons q _ b B, c => Fin.cons (c 0*q) (c 0 • b + synth B (tailV c))

def Represents {n : Nat} (B : Basis n) (x : Fin n → ℤ) : Prop :=
  ∃ c, synth B c = x

theorem synth_zero {n : Nat} (B : Basis n) : synth B 0 = 0 := by
  induction B with
  | nil => rfl
  | cons q hq b B ih =>
    ext i; refine Fin.cases ?_ (fun j => ?_) i
    · simp [synth]
    · simp [synth, ih]

theorem synth_add {n : Nat} (B : Basis n) (c e : Fin n → ℤ) :
    synth B (c+e) = synth B c + synth B e := by
  induction B with
  | nil => simp [synth]
  | cons q hq b B ih =>
    ext i; refine Fin.cases ?_ (fun j => ?_) i
    · simp [synth, add_mul]
    · simp only [synth, Fin.cons_succ, tailV_add, ih, Pi.add_apply, Pi.smul_apply, smul_eq_mul]; ring

theorem synth_smul {n : Nat} (B : Basis n) (a : ℤ) (c : Fin n → ℤ) :
    synth B (a • c) = a • synth B c := by
  induction B with
  | nil => simp [synth]
  | cons q hq b B ih =>
    ext i; refine Fin.cases ?_ (fun j => ?_) i
    · simp [synth, mul_assoc]
    · simp only [synth, Fin.cons_succ, tailV_smul, ih, Pi.smul_apply, Pi.add_apply, smul_eq_mul]; ring

def lattice {n : Nat} (B : Basis n) : Submodule ℤ (Fin n → ℤ) where
  carrier := Represents B
  zero_mem' := ⟨0, synth_zero B⟩
  add_mem' := by
    rintro x y ⟨c,rfl⟩ ⟨e,rfl⟩
    exact ⟨c+e, synth_add B c e⟩
  smul_mem' := by
    rintro a x ⟨c,rfl⟩
    exact ⟨a • c, synth_smul B a c⟩

theorem represents_cons_iff {n : Nat} (q : ℤ) (hq : 0<q)
    (b : Fin n → ℤ) (B : Basis n) (x : Fin (n+1) → ℤ) :
    Represents (.cons q hq b B) x ↔
    ∃ a : ℤ, x 0 = a*q ∧ Represents B (tailV x - a • b) := by
  constructor
  · rintro ⟨c,hc⟩
    refine ⟨c 0, ?_, tailV c, ?_⟩
    · exact (congrFun hc 0).symm
    · ext j
      have hj := congrFun hc j.succ
      simp only [synth, Fin.cons_succ, Pi.add_apply, Pi.smul_apply, smul_eq_mul] at hj
      simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul, tailV]
      linarith
  · rintro ⟨a,ha,c,hc⟩
    refine ⟨Fin.cons a c, ?_⟩
    ext i; refine Fin.cases ?_ (fun j => ?_) i
    · simpa [synth] using ha.symm
    · have hj := congrFun hc j
      simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul, tailV] at hj
      change a*b j + synth B c j = x j.succ
      rw [hj]; ring

/-- Deterministic triangular solve. None certifies nonmembership; it is not a resource exit. -/
def coordinates : {n : Nat} → Basis n → (Fin n → ℤ) → Option (Fin n → ℤ)
  | 0, .nil, _ => some (fun i => Fin.elim0 i)
  | _+1, .cons q _ b B, x =>
    if x 0 % q = 0 then
      (coordinates B (tailV x - (x 0 / q) • b)).map (Fin.cons (x 0 / q))
    else none

theorem coordinates_correct {n : Nat} (B : Basis n) (x : Fin n → ℤ) :
    (∃ c, coordinates B x = some c) ↔ Represents B x := by
  induction B with
  | nil =>
    simp only [coordinates, Option.some.injEq, exists_eq', Represents, synth]
    exact ⟨fun _ => ⟨0, Subsingleton.elim _ _⟩, fun _ => trivial⟩
  | cons q hq b B ih =>
    rw [represents_cons_iff]
    simp only [coordinates]
    split
    · rename_i hd
      have hdiv : x 0 / q * q = x 0 := Int.ediv_mul_cancel (Int.dvd_of_emod_eq_zero hd)
      constructor
      · rintro ⟨c,hc⟩
        obtain ⟨z,hz,_⟩ := Option.map_eq_some_iff.mp hc
        exact ⟨x 0 / q,hdiv.symm,(ih _).mp ⟨z,hz⟩⟩
      · rintro ⟨a,ha,ht⟩
        have he : x 0 / q = a := by rw [ha, Int.mul_ediv_cancel _ (ne_of_gt hq)]
        obtain ⟨z,hz⟩ := (ih _).mpr (by simpa [he] using ht)
        exact ⟨Fin.cons (x 0 / q) z, by simp [he, hz]⟩
    · rename_i hd
      constructor
      · rintro ⟨c,hc⟩; cases hc
      · rintro ⟨a,ha,_⟩
        exact False.elim (hd (by simp [ha]))

/-- The stored full-rank triangular rows are genuinely independent over the integers. -/
theorem synth_injective {n : Nat} (B : Basis n) : Function.Injective (synth B) := by
  induction B with
  | nil => intro c e _; exact Subsingleton.elim _ _
  | cons q hq b B ih =>
      intro c e h
      have hh : c 0*q=e 0*q := congrFun h 0
      have h0 : c 0=e 0 := mul_right_cancel₀ (ne_of_gt hq) hh
      have ht : tailV c=tailV e := by
        apply ih
        ext j
        have hj := congrFun h j.succ
        change c 0*b j+synth B (tailV c) j=e 0*b j+synth B (tailV e) j at hj
        rw [h0] at hj
        exact add_left_cancel hj
      ext i; refine Fin.cases h0 (fun j => congrFun ht j) i

/-- Returned coefficients reconstruct the input, not merely some member of the lattice. -/
theorem coordinates_solution {n : Nat} (B : Basis n) (x c : Fin n → ℤ)
    (h : coordinates B x=some c) : synth B c=x := by
  induction B with
  | nil => exact Subsingleton.elim _ _
  | cons q hq b B ih =>
      simp only [coordinates] at h
      split at h
      · rename_i hd
        obtain ⟨z,hz,hc⟩ := Option.map_eq_some_iff.mp h
        subst c
        have hs := ih _ _ hz
        ext i; refine Fin.cases ?_ (fun j => ?_) i
        · change x 0/q*q=x 0
          exact Int.ediv_mul_cancel (Int.dvd_of_emod_eq_zero hd)
        · change x 0/q*b j+synth B z j=x j.succ
          have hj := congrFun hs j
          change synth B z j=x j.succ-(x 0/q)*b j at hj
          rw [hj]; ring
      · cases h

end Komorebi.Echelon
