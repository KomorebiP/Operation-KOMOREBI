import KomorebiVerification.PaperII.SmithDyadic
import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.RingTheory.Ideal.Norm.AbsNorm

/-! Actual DVR quotient fibres, derived from ideal powers and their cardinalities. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.SmithDVR
open IsLocalRing
universe u
variable {O : Type u} [CommRing O] [IsDomain O] [IsDiscreteValuationRing O]

def powerIdeal (pi : O) (L : Nat) : Ideal O := Ideal.span {pi ^ L}
abbrev QuotientAt (pi : O) (L : Nat) := O ⧸ powerIdeal pi L

theorem powerIdeal_eq (pi : O) (hpi : Irreducible pi) (L : Nat) :
    powerIdeal pi L = maximalIdeal O ^ L := by
  rw [hpi.maximalIdeal_eq, Ideal.span_singleton_pow]
  rfl

/-- Cardinality follows from the ideal-power theorem, not a supplied coordinate certificate. -/
theorem quotientAt_card (pi : O) (hpi : Irreducible pi) (L : Nat) :
    Nat.card (QuotientAt pi L) = Nat.card (ResidueField O) ^ L := by
  have hp : maximalIdeal O ≠ ⊥ := by
    rw [hpi.maximalIdeal_eq]
    exact fun h => hpi.ne_zero (Ideal.span_singleton_eq_bot.mp h)
  change Nat.card (O ⧸ powerIdeal pi L) = _
  rw [powerIdeal_eq pi hpi]
  exact cardQuot_pow_of_prime hp

instance quotientAtFinite [Finite (ResidueField O)]
    (pi : O) (hpi : Irreducible pi) (L : Nat) : Finite (QuotientAt pi L) := by
  apply Nat.finite_of_card_ne_zero
  rw [quotientAt_card pi hpi]
  exact pow_ne_zero _ (Nat.ne_of_gt Nat.card_pos)

/-- Multiplication by the uniformizer power on the actual residue quotient. -/
def multiplyPower (pi : O) (s L : Nat) : QuotientAt pi L →ₗ[O] QuotientAt pi L where
  toFun x := pi ^ s • x
  map_add' x y := smul_add _ _ _
  map_smul' c x := by
    simp only [smul_smul, RingHom.id_apply]
    rw [mul_comm]

@[simp] theorem multiplyPower_mk (pi : O) (s L : Nat) (x : O) :
    multiplyPower pi s L ((powerIdeal pi L).mkQ x) =
      (powerIdeal pi L).mkQ (pi ^ s * x) := rfl

def baseMultiply (pi : O) (s L : Nat) : O →ₗ[O] QuotientAt pi L :=
  (multiplyPower pi s L).comp (powerIdeal pi L).mkQ

theorem baseMultiply_ker (pi : O) (hpi : pi ≠ 0) (s L : Nat) (hs : s ≤ L) :
    (baseMultiply pi s L).ker = powerIdeal pi (L - s) := by
  ext x
  change (powerIdeal pi L).mkQ (pi ^ s * x) = 0 ↔ x ∈ powerIdeal pi (L - s)
  rw [Submodule.Quotient.mk_eq_zero]
  change pi ^ s * x ∈ Ideal.span {pi ^ L} ↔ x ∈ Ideal.span {pi ^ (L - s)}
  rw [Ideal.mem_span_singleton, Ideal.mem_span_singleton]
  rw [show pi ^ L = pi ^ s * pi ^ (L - s) by rw [← pow_add, Nat.add_sub_of_le hs]]
  exact mul_dvd_mul_iff_left (pow_ne_zero _ hpi)

theorem baseMultiply_range (pi : O) (s L : Nat) :
    (baseMultiply pi s L).range = (multiplyPower pi s L).range := by
  rw [baseMultiply, LinearMap.range_comp, Submodule.range_mkQ, Submodule.map_top]

theorem multiplyPower_range_card (pi : O) (hpi : Irreducible pi)
    (s L : Nat) (hs : s ≤ L) :
    Nat.card (multiplyPower pi s L).range = Nat.card (ResidueField O) ^ (L - s) := by
  rw [← baseMultiply_range]
  rw [← Nat.card_congr (baseMultiply pi s L).quotKerEquivRange.toEquiv]
  rw [baseMultiply_ker pi hpi.ne_zero s L hs]
  exact quotientAt_card pi hpi (L - s)

theorem multiplyPower_zero (pi : O) (s L : Nat) (hs : L ≤ s) :
    multiplyPower pi s L = 0 := by
  apply LinearMap.ext
  intro x
  obtain ⟨a, rfl⟩ := (powerIdeal pi L).mkQ_surjective x
  rw [multiplyPower_mk, LinearMap.zero_apply, Submodule.Quotient.mk_eq_zero]
  apply Ideal.mem_span_singleton.mpr
  exact dvd_mul_of_dvd_left (pow_dvd_pow pi hs) a

/-- The true scalar kernel has the expected finite residue-field cardinality. -/
theorem multiplyPower_ker_card [Finite (ResidueField O)]
    (pi : O) (hpi : Irreducible pi) (s L : Nat) :
    Nat.card (multiplyPower pi s L).ker = Nat.card (ResidueField O) ^ min s L := by
  rcases le_total s L with hs | hs
  · rw [min_eq_left hs]
    have hcard := Submodule.card_eq_card_quotient_mul_card (multiplyPower pi s L).ker
    rw [Nat.card_congr (multiplyPower pi s L).quotKerEquivRange.toEquiv,
      quotientAt_card pi hpi, multiplyPower_range_card pi hpi s L hs] at hcard
    apply Nat.eq_of_mul_eq_mul_right (pow_pos (Nat.card_pos (α := ResidueField O)) (L - s))
    rw [← hcard, ← pow_add, Nat.add_sub_of_le hs]
  · rw [min_eq_right hs, multiplyPower_zero pi s L hs, LinearMap.ker_zero]
    rw [Nat.card_congr (Submodule.topEquiv : (⊤ : Submodule O (QuotientAt pi L)) ≃ₗ[O]
      QuotientAt pi L).toEquiv]
    exact quotientAt_card pi hpi L

abbrev ScalarFiber (pi : O) (s L : Nat) (b : O) :=
  {x : QuotientAt pi L // multiplyPower pi s L x = (powerIdeal pi L).mkQ b}

/-- Exact scalar solvability, with divisibility of the actual integral target. -/
theorem scalarFiber_nonempty_iff (pi : O) (s L : Nat) (b : O) :
    Nonempty (ScalarFiber pi s L b) ↔ pi ^ min s L ∣ b := by
  constructor
  · rintro ⟨⟨x, hx⟩⟩
    obtain ⟨a, rfl⟩ := (powerIdeal pi L).mkQ_surjective x
    rw [multiplyPower_mk] at hx
    have hd : pi ^ L ∣ pi ^ s * a - b :=
      Ideal.mem_span_singleton.mp ((Submodule.Quotient.eq _).mp hx)
    have hsa : pi ^ min s L ∣ pi ^ s * a :=
      dvd_mul_of_dvd_left (pow_dvd_pow pi (min_le_left s L)) a
    have hdiff : pi ^ min s L ∣ pi ^ s * a - b :=
      dvd_trans (pow_dvd_pow pi (min_le_right s L)) hd
    exact (dvd_sub_iff_right hsa).mp hdiff
  · intro hb
    rcases le_total s L with hs | hs
    · rw [min_eq_left hs] at hb
      obtain ⟨a, ha⟩ := hb
      exact ⟨⟨(powerIdeal pi L).mkQ a, by rw [multiplyPower_mk, ← ha]⟩⟩
    · rw [min_eq_right hs] at hb
      have hb0 : (powerIdeal pi L).mkQ b = 0 :=
        (Submodule.Quotient.mk_eq_zero _).mpr (Ideal.mem_span_singleton.mpr hb)
      exact ⟨⟨0, by simp [hb0]⟩⟩

/-- Inhabited actual scalar fibres have the kernel cardinality. -/
theorem scalarFiber_card [Finite (ResidueField O)]
    (pi : O) (hpi : Irreducible pi) (s L : Nat) (b : O)
    (hb : pi ^ min s L ∣ b) :
    Nat.card (ScalarFiber pi s L b) = Nat.card (ResidueField O) ^ min s L := by
  obtain ⟨⟨x, hx⟩⟩ := (scalarFiber_nonempty_iff pi s L b).mpr hb
  let f := (multiplyPower pi s L).toAddMonoidHom
  have he : ScalarFiber pi s L b ≃ f.ker := by
    simpa only [ScalarFiber, ← hx] using f.fiberEquivKer x
  rw [Nat.card_congr he]
  exact multiplyPower_ker_card pi hpi s L

end Komorebi.PaperII.SmithDVR
#print axioms Komorebi.PaperII.SmithDVR.quotientAt_card
#print axioms Komorebi.PaperII.SmithDVR.scalarFiber_nonempty_iff
#print axioms Komorebi.PaperII.SmithDVR.scalarFiber_card
