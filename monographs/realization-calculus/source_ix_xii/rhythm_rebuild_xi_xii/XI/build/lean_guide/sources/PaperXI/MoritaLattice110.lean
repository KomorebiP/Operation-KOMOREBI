import Mathlib.Data.Matrix.Basis
import Mathlib.Algebra.Ring.AddAut
import Mathlib.GroupTheory.QuotientGroup.Basic

/-! The common-corner and diagonal-transport part of the maximal-order
Morita calculation. The coefficient ring acts through an arbitrary ring
homomorphism into a possibly noncommutative endomorphism ring. In particular,
no false centrality assumption on O_E inside End_F(E) is imposed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaLattice110

open Matrix

variable {R D m : Type*} [Ring R] [Ring D] [Fintype m] [DecidableEq m]

/-- Stability under the actual mapped coefficient matrices on both sides. -/
def IsMatrixBimodule (φ : R →+* D) (L : AddSubgroup (Matrix m m D)) : Prop :=
  (∀ b : Matrix m m R, ∀ x ∈ L, b.map φ * x ∈ L) ∧
  (∀ b : Matrix m m R, ∀ x ∈ L, x * b.map φ ∈ L)

/-- The literal insertion into a chosen diagonal corner. -/
def cornerEmbedding (p : m) : D →+ Matrix m m D where
  toFun x := single p p x
  map_zero' := single_zero p p
  map_add' := single_add p p

/-- The actual corner subgroup, not an independently supplied module. -/
def corner (L : AddSubgroup (Matrix m m D)) (p : m) : AddSubgroup D :=
  L.comap (cornerEmbedding p)

omit [Fintype m] in
@[simp] theorem mem_corner (L : AddSubgroup (Matrix m m D)) (p : m) (x : D) :
    x ∈ corner L p ↔ single p p x ∈ L := Iff.rfl

/-- Multiplying by matrix units extracts an entry into the chosen corner. -/
theorem entry_mem_corner (φ : R →+* D) (L : AddSubgroup (Matrix m m D))
    (hL : IsMatrixBimodule φ L) (p : m) {x : Matrix m m D} (hx : x ∈ L)
    (i j : m) : x i j ∈ corner L p := by
  have hleft := hL.1 (single p i 1) x hx
  have hright := hL.2 (single j p 1) _ hleft
  simpa [mem_corner, single_mul_mul_single] using hright

/-- An allowed corner entry can be inserted at every matrix position. -/
theorem single_mem_of_corner (φ : R →+* D) (L : AddSubgroup (Matrix m m D))
    (hL : IsMatrixBimodule φ L) (p i j : m) {x : D}
    (hx : x ∈ corner L p) : single i j x ∈ L := by
  have hleft := hL.1 (single i p 1) (single p p x) hx
  have hright := hL.2 (single p j 1) _ hleft
  simpa [single_mul_mul_single] using hright

/-- Matrix-unit Morita reduction, as equality of the actual additive subgroups. -/
theorem eq_matrix_corner (φ : R →+* D) (L : AddSubgroup (Matrix m m D))
    (hL : IsMatrixBimodule φ L) (p : m) : L = (corner L p).matrix := by
  ext x
  constructor
  · intro hx i j
    exact entry_mem_corner φ L hL p hx i j
  · intro hx
    rw [matrix_eq_sum_single x]
    apply L.sum_mem
    intro i _
    apply L.sum_mem
    intro j _
    exact single_mem_of_corner φ L hL p i j (hx i j)

/-- The corner inherits genuine left and right coefficient-ring stability. -/
theorem corner_bimodule (φ : R →+* D) (L : AddSubgroup (Matrix m m D))
    (hL : IsMatrixBimodule φ L) (p : m) (a : R) {x : D}
    (hx : x ∈ corner L p) :
    φ a * x ∈ corner L p ∧ x * φ a ∈ corner L p := by
  constructor
  · have h := hL.1 (single p p a) (single p p x) hx
    simpa [mem_corner] using h
  · have h := hL.2 (single p p a) (single p p x) hx
    simpa [mem_corner] using h

section ScalarTransport
variable {D : Type*} [Ring D]

/-- Conjugation by a genuine unit of the noncommutative coefficient ring. -/
def unitConjugation (u : Dˣ) : D ≃+ D where
  toFun x := (u : D) * x * ((u⁻¹ : Dˣ) : D)
  invFun x := ((u⁻¹ : Dˣ) : D) * x * (u : D)
  left_inv x := by simp [mul_assoc]
  right_inv x := by simp [mul_assoc]
  map_add' x y := by simp [mul_add, add_mul]

@[simp] theorem unitConjugation_apply (u : Dˣ) (x : D) :
    unitConjugation u x = (u : D) * x * ((u⁻¹ : Dˣ) : D) := rfl

/-- The units that normalize the literal additive subgroup. -/
def normalizingUnits (Λ : AddSubgroup D) : Subgroup Dˣ where
  carrier := {u | ∀ x : D, unitConjugation u x ∈ Λ ↔ x ∈ Λ}
  one_mem' := by intro x; simp [unitConjugation]
  mul_mem' {u v} hu hv := by
    intro x
    have he : unitConjugation u (unitConjugation v x) =
        unitConjugation (u * v) x := by simp [unitConjugation, mul_assoc]
    rw [← he, hu, hv]
  inv_mem' {u} hu := by
    intro x
    have h := hu (unitConjugation u⁻¹ x)
    simpa [unitConjugation, mul_assoc] using h.symm

@[simp] theorem mem_normalizingUnits (Λ : AddSubgroup D) (u : Dˣ) :
    u ∈ normalizingUnits Λ ↔ ∀ x, unitConjugation u x ∈ Λ ↔ x ∈ Λ := Iff.rfl

/-- Radical commutation implies normalization; no centrality is assumed. -/
theorem normalizes_of_left_right_map_eq (Λ : AddSubgroup D) (u : Dˣ)
    (hcomm : Λ.map (AddMonoidHom.mulLeft (u : D)) =
      Λ.map (AddMonoidHom.mulRight (u : D))) :
    u ∈ normalizingUnits Λ := by
  intro x
  constructor
  · intro hx
    have hmem : (u : D) * x ∈ Λ.map (AddMonoidHom.mulRight (u : D)) := by
      refine ⟨unitConjugation u x, hx, ?_⟩
      simp [unitConjugation, mul_assoc]
    rw [← hcomm] at hmem
    obtain ⟨z, hz, he⟩ := hmem
    have hzx : z = x := by
      have h := congrArg (fun t : D => ((u⁻¹ : Dˣ) : D) * t) he
      simpa [mul_assoc] using h
    exact hzx ▸ hz
  · intro hx
    have hmem : (u : D) * x ∈ Λ.map (AddMonoidHom.mulLeft (u : D)) :=
      ⟨x, hx, rfl⟩
    rw [hcomm] at hmem
    obtain ⟨z, hz, he⟩ := hmem
    have hzx : z = unitConjugation u x := by
      have h := congrArg (fun t : D => t * ((u⁻¹ : Dˣ) : D)) he
      simpa [unitConjugation, mul_assoc] using h
    exact hzx ▸ hz

/-- All positive and negative powers normalize, derived from one commutation. -/
theorem zpow_normalizes (Λ : AddSubgroup D) (u : Dˣ)
    (hu : u ∈ normalizingUnits Λ) (a : ℤ) :
    u ^ a ∈ normalizingUnits Λ := (normalizingUnits Λ).zpow_mem hu a

/-- The right scalar can be transferred to the left in a membership test. -/
theorem two_sided_mem_iff_left (Λ : AddSubgroup D) (u : Dˣ)
    (hu : u ∈ normalizingUnits Λ) (a b : ℤ) (x : D) :
    ((u ^ a : Dˣ) : D) * x * ((u ^ b : Dˣ) : D) ∈ Λ ↔
      ((u ^ (a + b) : Dˣ) : D) * x ∈ Λ := by
  have h := zpow_normalizes Λ u hu b
  have he : unitConjugation (u ^ b)
      (((u ^ a : Dˣ) : D) * x * ((u ^ b : Dˣ) : D)) =
      ((u ^ (a + b) : Dˣ) : D) * x := by
    simp only [unitConjugation_apply]
    calc
      _ = (((u ^ b : Dˣ) : D) * ((u ^ a : Dˣ) : D)) * x *
          (((u ^ b : Dˣ) : D) * (((u ^ b)⁻¹ : Dˣ) : D)) := by simp [mul_assoc]
      _ = ((u ^ (a + b) : Dˣ) : D) * x := by
        rw [Units.mul_inv, mul_one, ← Units.val_mul, ← zpow_add, add_comm b a]
  exact (h _).symm.trans (by rw [he])

/-- The actual left power translate of the corner subgroup. -/
def leftPower (Λ : AddSubgroup D) (u : Dˣ) (a : ℤ) : AddSubgroup D :=
  Λ.map (AddMonoidHom.mulLeft ((u ^ a : Dˣ) : D))

theorem mem_leftPower (Λ : AddSubgroup D) (u : Dˣ) (a : ℤ) (x : D) :
    x ∈ leftPower Λ u a ↔ ((u ^ (-a) : Dˣ) : D) * x ∈ Λ := by
  constructor
  · rintro ⟨z, hz, rfl⟩
    simpa [leftPower, ← mul_assoc, ← Units.val_mul, ← zpow_add] using hz
  · intro hx
    refine ⟨((u ^ (-a) : Dˣ) : D) * x, hx, ?_⟩
    simp [← mul_assoc, ← Units.val_mul]

end ScalarTransport

section DiagonalTransport
variable {D m : Type*} [Ring D] [Fintype m] [DecidableEq m]

/-- A diagonal matrix unit, including its explicit inverse. -/
def diagonalUnit (d : m → Dˣ) : (Matrix m m D)ˣ where
  val := diagonal (fun i => (d i : D))
  inv := diagonal (fun i => (((d i)⁻¹ : Dˣ) : D))
  val_inv := by
    rw [diagonal_mul_diagonal]
    ext i j
    by_cases h : i = j
    · subst j; simp [diagonal]
    · simp [diagonal, h]
  inv_val := by
    rw [diagonal_mul_diagonal]
    ext i j
    by_cases h : i = j
    · subst j; simp [diagonal]
    · simp [diagonal, h]

/-- Conjugation really acts separately on the actual matrix entries. -/
theorem diagonal_conjugation_apply (d : m → Dˣ) (x : Matrix m m D) (i j : m) :
    unitConjugation (diagonalUnit d) x i j =
      (d i : D) * x i j * (((d j)⁻¹ : Dˣ) : D) := by
  simp [unitConjugation, diagonalUnit, diagonal_mul, mul_diagonal]

/-- A scalar diagonal preserves the chosen corner insertion. -/
theorem scalar_conjugation_single (u : Dˣ) (p : m) (x : D) :
    unitConjugation (diagonalUnit (fun _ : m => u)) (single p p x) =
      single p p (unitConjugation u x) := by
  ext i j
  rw [diagonal_conjugation_apply]
  by_cases h : p = i ∧ p = j <;> simp [single, h, unitConjugation]

/-- Radical commutation on the actual matrix subgroup descends to its corner. -/
theorem corner_normalizes_of_scalar_commutation
    (L : AddSubgroup (Matrix m m D)) (u : Dˣ) (p : m)
    (hcomm : L.map (AddMonoidHom.mulLeft
        (diagonalUnit (fun _ : m => u) : Matrix m m D)) =
      L.map (AddMonoidHom.mulRight
        (diagonalUnit (fun _ : m => u) : Matrix m m D))) :
    u ∈ normalizingUnits (corner L p) := by
  have hnorm := normalizes_of_left_right_map_eq L
    (diagonalUnit (fun _ : m => u)) hcomm
  intro x
  simpa only [mem_corner, scalar_conjugation_single] using hnorm (single p p x)

/-- Membership in the actual conjugate image is tested by inverse conjugation. -/
theorem mem_conjugate (L : AddSubgroup D) (u : Dˣ) (x : D) :
    x ∈ L.map (unitConjugation u).toAddMonoidHom ↔
      unitConjugation u⁻¹ x ∈ L := by
  constructor
  · rintro ⟨z, hz, rfl⟩
    simpa [unitConjugation, mul_assoc] using hz
  · intro hx
    refine ⟨unitConjugation u⁻¹ x, hx, ?_⟩
    simp [unitConjugation, mul_assoc]

/-- A family of actual allowed-entry additive subgroups. -/
def entrywise (S : m → m → AddSubgroup D) : AddSubgroup (Matrix m m D) where
  carrier := {x | ∀ i j, x i j ∈ S i j}
  zero_mem' i j := (S i j).zero_mem
  add_mem' hx hy i j := (S i j).add_mem (hx i j) (hy i j)
  neg_mem' hx i j := (S i j).neg_mem (hx i j)

omit [Fintype m] [DecidableEq m] in
@[simp] theorem mem_entrywise (S : m → m → AddSubgroup D) (x : Matrix m m D) :
    x ∈ entrywise S ↔ ∀ i j, x i j ∈ S i j := Iff.rfl

/-- Diagonal conjugation of the genuine Morita lattice is the family of left
power translates, with the correct signed Cartan differences. -/
theorem conjugate_eq_entrywise_leftPower
    (φ : R →+* D) (L : AddSubgroup (Matrix m m D))
    (hL : IsMatrixBimodule φ L) (p : m) (u : Dˣ)
    (hu : u ∈ normalizingUnits (corner L p)) (a : m → ℤ) :
    L.map (unitConjugation (diagonalUnit (fun i => u ^ a i))).toAddMonoidHom =
      entrywise (fun i j => leftPower (corner L p) u (a i - a j)) := by
  ext x
  rw [mem_conjugate]
  conv_lhs => rw [eq_matrix_corner φ L hL p]
  change (∀ i j, unitConjugation (diagonalUnit (fun i => u ^ a i))⁻¹ x i j ∈
      corner L p) ↔ ∀ i j, x i j ∈ leftPower (corner L p) u (a i - a j)
  have hdiag : (diagonalUnit (fun i => u ^ a i))⁻¹ =
      diagonalUnit (fun i => (u ^ a i)⁻¹) := by
    apply Units.ext
    rfl
  simp only [hdiag, diagonal_conjugation_apply, inv_inv]
  constructor <;> intro hx i j
  · rw [mem_leftPower]
    have h := (two_sided_mem_iff_left (corner L p) u hu (-a i) (a j) (x i j)).mp
      (by simpa only [zpow_neg] using hx i j)
    have he : -(a i - a j) = -a i + a j := by omega
    rw [he]
    exact h
  · have h := (mem_leftPower (corner L p) u (a i - a j) (x i j)).mp (hx i j)
    have h' : ((u ^ (-a i + a j) : Dˣ) : D) * x i j ∈ corner L p := by
      have he : -(a i - a j) = -a i + a j := by omega
      rw [he] at h
      exact h
    simpa only [zpow_neg] using
      (two_sided_mem_iff_left (corner L p) u hu (-a i) (a j) (x i j)).mpr h'

/-- The actual conjugate intersection is the entrywise corner intersection. -/
theorem intersection_eq_entrywise
    (φ : R →+* D) (L : AddSubgroup (Matrix m m D))
    (hL : IsMatrixBimodule φ L) (p : m) (u : Dˣ)
    (hu : u ∈ normalizingUnits (corner L p)) (a : m → ℤ) :
    L ⊓ L.map (unitConjugation (diagonalUnit (fun i => u ^ a i))).toAddMonoidHom =
      entrywise (fun i j => corner L p ⊓ leftPower (corner L p) u (a i - a j)) := by
  rw [conjugate_eq_entrywise_leftPower φ L hL p u hu a]
  nth_rw 1 [eq_matrix_corner φ L hL p]
  ext x
  change ((∀ i j, x i j ∈ corner L p) ∧
    (∀ i j, x i j ∈ leftPower (corner L p) u (a i - a j))) ↔
      ∀ i j, x i j ∈ corner L p ∧ x i j ∈ leftPower (corner L p) u (a i - a j)
  exact ⟨fun h i j => ⟨h.1 i j, h.2 i j⟩,
    fun h => ⟨fun i j => (h i j).1, fun i j => (h i j).2⟩⟩

end DiagonalTransport

section PowerIntersection
variable {D : Type*} [Ring D]

/-- Integral scalar stability is iterated, rather than supplied for each power. -/
theorem pow_mul_mem (Λ : AddSubgroup D) (u : Dˣ)
    (hstable : ∀ x ∈ Λ, (u : D) * x ∈ Λ) (n : ℕ) {x : D} (hx : x ∈ Λ) :
    ((u ^ n : Dˣ) : D) * x ∈ Λ := by
  induction n with
  | zero => simpa using hx
  | succ n ih => simpa [pow_succ', mul_assoc] using hstable _ ih

theorem leftPower_zero (Λ : AddSubgroup D) (u : Dˣ) : leftPower Λ u 0 = Λ := by
  ext x
  rw [mem_leftPower]
  simp

/-- The actual nested intersection is the nonnegative scalar-power translate. -/
theorem inf_leftPower_eq_toNat (Λ : AddSubgroup D) (u : Dˣ)
    (hstable : ∀ x ∈ Λ, (u : D) * x ∈ Λ) (a : ℤ) :
    Λ ⊓ leftPower Λ u a = leftPower Λ u (a.toNat : ℤ) := by
  cases a with
  | ofNat n =>
    have hle : leftPower Λ u (n : ℤ) ≤ Λ := by
      rintro x ⟨z, hz, rfl⟩
      change ((u ^ (n : ℤ) : Dˣ) : D) * z ∈ Λ
      simpa only [zpow_natCast] using pow_mul_mem Λ u hstable n hz
    simpa using inf_eq_right.mpr hle
  | negSucc n =>
    have hle : Λ ≤ leftPower Λ u (Int.negSucc n) := by
      intro x hx
      rw [mem_leftPower]
      simpa only [Int.neg_negSucc, zpow_natCast] using pow_mul_mem Λ u hstable (n + 1) hx
    simpa only [Int.toNat_negSucc, Nat.cast_zero, leftPower_zero] using inf_eq_left.mpr hle

end PowerIntersection

/-- Left integral scalar stability for the actual corner follows from the
coefficient bimodule; the uniformizer unit is tied to its coefficient value. -/
theorem corner_scalar_stable (φ : R →+* D) (L : AddSubgroup (Matrix m m D))
    (hL : IsMatrixBimodule φ L) (p : m) (π : R) (u : Dˣ)
    (hπ : (u : D) = φ π) : ∀ x ∈ corner L p, (u : D) * x ∈ corner L p := by
  intro x hx
  rw [hπ]
  exact (corner_bimodule φ L hL p π hx).1

/-- The final entrywise intersection reduction, with each negative Cartan
difference contributing zero. Its remaining numerical leaf is a genuine DVR
quotient of the actual corner module. -/
theorem intersection_eq_nonnegative_entrywise
    (φ : R →+* D) (L : AddSubgroup (Matrix m m D))
    (hL : IsMatrixBimodule φ L) (p : m) (π : R) (u : Dˣ)
    (hπ : (u : D) = φ π)
    (hu : u ∈ normalizingUnits (corner L p)) (a : m → ℤ) :
    L ⊓ L.map (unitConjugation (diagonalUnit (fun i => u ^ a i))).toAddMonoidHom =
      entrywise (fun i j => leftPower (corner L p) u ((a i - a j).toNat : ℤ)) := by
  rw [intersection_eq_entrywise φ L hL p u hu a]
  congr 1
  funext i j
  exact inf_leftPower_eq_toNat (corner L p) u
    (corner_scalar_stable φ L hL p π u hπ) (a i - a j)

end PaperXI.MoritaLattice110
