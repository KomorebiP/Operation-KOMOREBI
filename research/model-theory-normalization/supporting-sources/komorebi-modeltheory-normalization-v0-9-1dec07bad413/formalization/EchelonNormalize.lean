module
public import EchelonInsert

@[expose] public section
namespace Komorebi.Echelon

@[simp] theorem tailV_sub {n : Nat} (x y : Fin (n+1) → ℤ) :
    tailV (x-y)=tailV x-tailV y := rfl

/-- Diagonal pivot in each coordinate. -/
def pivots : {n : Nat} → Basis n → (Fin n → ℤ)
  | 0, .nil => fun i => Fin.elim0 i
  | _+1, .cons q _ _ B => Fin.cons q (pivots B)

/-- The rectangular half-open fundamental domain for a triangular basis. -/
def InBox : {n : Nat} → Basis n → (Fin n → ℤ) → Prop
  | 0, .nil, _ => True
  | _+1, .cons q _ _ B, x => 0 ≤ x 0 ∧ x 0 < q ∧ InBox B (tailV x)

/-- Euclidean reduction, whether or not the input belongs to the lattice. -/
def residue : {n : Nat} → Basis n → (Fin n → ℤ) → (Fin n → ℤ)
  | 0, .nil, _ => 0
  | _+1, .cons q _ b B, x =>
    Fin.cons (x 0 % q) (residue B (tailV x - (x 0 / q) • b))

theorem residue_inBox {n : Nat} (B : Basis n) (x : Fin n → ℤ) :
    InBox B (residue B x) := by
  induction B with
  | nil => trivial
  | cons q hq b B ih =>
    exact ⟨Int.emod_nonneg _ (ne_of_gt hq), Int.emod_lt_of_pos _ hq, ih _⟩

/-- Reduction changes a vector only by a genuine integer lattice vector. -/
theorem residue_coset {n : Nat} (B : Basis n) (x : Fin n → ℤ) :
    Represents B (x - residue B x) := by
  induction B with
  | nil => exact ⟨0, Subsingleton.elim _ _⟩
  | cons q hq b B ih =>
    apply (represents_cons_iff q hq b B _).mpr
    refine ⟨x 0 / q, ?_, ?_⟩
    · change x 0 - x 0 % q = x 0 / q * q
      have h := Int.emod_add_ediv_mul (x 0) q
      omega
    · have h := ih (tailV x - (x 0 / q) • b)
      convert h using 1
      ext j
      simp only [tailV, Pi.sub_apply, Pi.smul_apply, smul_eq_mul,
        residue, Fin.cons_succ]
      ring

/-- Two representatives of a lattice coset cannot both occupy different points of the box. -/
theorem inBox_unique {n : Nat} (B : Basis n) (x y : Fin n → ℤ)
    (hx : InBox B x) (hy : InBox B y) (hxy : Represents B (x-y)) : x=y := by
  induction B with
  | nil => exact Subsingleton.elim _ _
  | cons q hq b B ih =>
    obtain ⟨a, ha, ht⟩ := (represents_cons_iff q hq b B _).mp hxy
    change x 0-y 0=a*q at ha
    have h0 : a=0 := by
      rcases lt_trichotomy a 0 with hn | hz | hp
      · have hn' : a ≤ -1 := by omega
        have hpq : 0 ≤ (-1-a)*q := mul_nonneg (by omega) (le_of_lt hq)
        have hx0 := hx.1; have hy0 := hy.2.1
        nlinarith
      · exact hz
      · have hp' : 1 ≤ a := by omega
        have hpq : 0 ≤ (a-1)*q := mul_nonneg (by omega) (le_of_lt hq)
        have hx0 := hx.2.1; have hy0 := hy.1
        nlinarith
    have head : x 0=y 0 := by rw [h0] at ha; linarith
    have tail : tailV x=tailV y := by
      apply ih _ _ hx.2.2 hy.2.2
      simpa only [h0, zero_smul, sub_zero, tailV_sub] using ht
    ext i; exact Fin.cases head (fun j => congrFun tail j) i

theorem residue_of_inBox {n : Nat} (B : Basis n) (x : Fin n → ℤ)
    (hx : InBox B x) : residue B x=x := by
  exact (inBox_unique B x (residue B x) hx (residue_inBox B x) (residue_coset B x)).symm

/-- Replace a leading row tail by a congruent tail without changing its integer lattice. -/
theorem lattice_shift_tail {n : Nat} (q : ℤ) (hq : 0<q)
    (b c : Fin n → ℤ) (B : Basis n) (hbc : Represents B (b-c)) :
    lattice (.cons q hq b B)=lattice (.cons q hq c B) := by
  ext x
  change Represents (.cons q hq b B) x ↔ Represents (.cons q hq c B) x
  rw [represents_cons_iff, represents_cons_iff]
  constructor
  · rintro ⟨a,ha,ht⟩
    refine ⟨a,ha,?_⟩
    have hm := (lattice B).add_mem ht ((lattice B).smul_mem a hbc)
    change Represents B (tailV x-a • b+a • (b-c)) at hm
    convert hm using 1
    ext j
    simp only [Pi.sub_apply, Pi.add_apply, Pi.smul_apply, smul_eq_mul]
    ring
  · rintro ⟨a,ha,ht⟩
    refine ⟨a,ha,?_⟩
    have hm := (lattice B).sub_mem ht ((lattice B).smul_mem a hbc)
    change Represents B (tailV x-a • c-a • (b-c)) at hm
    convert hm using 1
    ext j
    simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
    ring

theorem lattice_cons_congr {n : Nat} (q : ℤ) (hq : 0<q)
    (b : Fin n → ℤ) (B C : Basis n) (hBC : lattice B=lattice C) :
    lattice (.cons q hq b B)=lattice (.cons q hq b C) := by
  ext x
  change Represents (.cons q hq b B) x ↔ Represents (.cons q hq b C) x
  rw [represents_cons_iff, represents_cons_iff]
  have he : ∀ y, Represents B y ↔ Represents C y := fun y => by
    change y ∈ lattice B ↔ y ∈ lattice C
    rw [hBC]
  simp only [he]

/-- Normalize lower rows first, then reduce the upper tail modulo their actual lattice. -/
def normalize : {n : Nat} → Basis n → Basis n
  | 0, .nil => .nil
  | _+1, .cons q hq b B =>
    let C := normalize B
    .cons q hq (residue C b) C

/-- Exact integer-lattice preservation, with no saturation. -/
theorem lattice_normalize {n : Nat} (B : Basis n) :
    lattice (normalize B)=lattice B := by
  induction B with
  | nil => rfl
  | cons q hq b B ih =>
    change lattice (.cons q hq (residue (normalize B) b) (normalize B)) = _
    exact (lattice_shift_tail q hq b _ (normalize B) (residue_coset _ _)).symm.trans
      (lattice_cons_congr q hq b (normalize B) B ih)

theorem represents_normalize {n : Nat} (B : Basis n) (x : Fin n → ℤ) :
    Represents (normalize B) x ↔ Represents B x := by
  change x ∈ lattice (normalize B) ↔ x ∈ lattice B
  rw [lattice_normalize]

def Reduced : {n : Nat} → Basis n → Prop
  | 0, .nil => True
  | _+1, .cons _ _ b B => InBox B b ∧ Reduced B

theorem normalize_reduced {n : Nat} (B : Basis n) : Reduced (normalize B) := by
  induction B with
  | nil => trivial
  | cons q hq b B ih => exact ⟨residue_inBox _ _, ih⟩

theorem normalize_of_reduced {n : Nat} (B : Basis n) (h : Reduced B) : normalize B=B := by
  induction B with
  | nil => rfl
  | cons q hq b B ih =>
    change Basis.cons q hq (residue (normalize B) b) (normalize B)=Basis.cons q hq b B
    rw [ih h.2, residue_of_inBox B b h.1]

theorem normalize_idempotent {n : Nat} (B : Basis n) :
    normalize (normalize B)=normalize B := normalize_of_reduced _ (normalize_reduced B)

theorem pivots_normalize {n : Nat} (B : Basis n) : pivots (normalize B)=pivots B := by
  induction B with
  | nil => rfl
  | cons q hq b B ih => simp only [normalize, pivots, ih]

end Komorebi.Echelon
