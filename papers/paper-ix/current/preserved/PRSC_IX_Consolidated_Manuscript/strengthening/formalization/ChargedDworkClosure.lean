module
public import CubicDworkClosure
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.ChargedDworkClosure
open DworkAlgebra
variable {K A : Type*} [Field K] [CommRing A] [Algebra K A]

/-- A charged fourth derivative defect; multiplication adds its integer charge. -/
def B (D : Derivation K A A) (c : ℤ) : A →ₗ[K] A :=
  (2:K)⁻¹ • (deriv D 4 - (c:K) • LinearMap.id)

theorem B_deriv (D : Derivation K A A) (c : ℤ) (n : ℕ) (f : A) :
    B D c (deriv D n f) = deriv D n (B D c f) := by
  simp only [B, LinearMap.smul_apply, LinearMap.sub_apply, LinearMap.id_apply,
    map_smul, map_sub, CubicDworkClosure.deriv_add]
  rw [Nat.add_comm 4 n]

theorem iterate_B_deriv (D : Derivation K A A) (c : ℤ) (s n : ℕ) (f : A) :
    (B D c ^ s) (deriv D n f) = deriv D n ((B D c ^ s) f) := by
  induction s with
  | zero => rfl
  | succ s ih => simp only [pow_succ', Module.End.mul_apply, ih, B_deriv]

theorem B_mul [CharZero K] (D : Derivation K A A) (c d : ℤ) (f g : A) :
    B D (c+d) (f*g) = B D c f*g + f*B D d g + middle D 2 4 f g := by
  have h := prime_power_leibniz D 2 2 Nat.prime_two f g
  norm_num only at h
  simp only [B, LinearMap.smul_apply, LinearMap.sub_apply, LinearMap.id_apply]
  rw [h]
  simp only [Int.cast_add, Algebra.smul_def, map_add]
  have hc := congrArg (algebraMap K A) (inv_mul_cancel₀ (by norm_num : (2:K)≠0))
  simp only [map_mul, map_ofNat, map_one] at hc
  linear_combination middle D 2 4 f g * hc

@[simp] theorem B_zero_one (D : Derivation K A A) : B D 0 1 = 0 := by
  simp [B, CubicDworkClosure.deriv_one_eq_zero D 4 (by decide)]

def bounded (D : Derivation K A A) (c : ℤ) (I : Subring A) (n : ℕ) (f : A) : Prop :=
  ∀ s ≤ n, (B D c ^ s) f ∈ I

def flat (D : Derivation K A A) (c : ℤ) (I : Subring A) (f : A) : Prop :=
  ∀ s, (B D c ^ s) f ∈ I

@[simp] theorem bounded_zero (D : Derivation K A A) (c : ℤ) (I : Subring A) (f : A) :
    bounded D c I 0 f ↔ f∈I := by simp [bounded]

theorem bounded_mono (D : Derivation K A A) (c : ℤ) (I : Subring A) {n m : ℕ}
    (h : m≤n) {f : A} (hf : bounded D c I n f) : bounded D c I m f :=
  fun s hs => hf s (hs.trans h)

theorem bounded_succ (D : Derivation K A A) (c : ℤ) (I : Subring A) (n : ℕ) (f : A) :
    bounded D c I (n+1) f ↔ f∈I ∧ bounded D c I n (B D c f) := by
  constructor
  · intro hf
    refine ⟨by simpa using hf 0 (by omega), ?_⟩
    intro s hs
    have h := hf (s+1) (by omega)
    simpa only [pow_succ, Module.End.mul_apply] using h
  · rintro ⟨hf,hb⟩ s hs
    cases s with
    | zero => simpa using hf
    | succ s => simpa only [pow_succ, Module.End.mul_apply] using hb s (by omega)

theorem bounded_add (D : Derivation K A A) (c : ℤ) (I : Subring A) (n : ℕ)
    {f g : A} (hf : bounded D c I n f) (hg : bounded D c I n g) :
    bounded D c I n (f+g) := by
  intro s hs
  rw [map_add]
  exact I.add_mem (hf s hs) (hg s hs)

theorem bounded_neg (D : Derivation K A A) (c : ℤ) (I : Subring A) (n : ℕ)
    {f : A} (hf : bounded D c I n f) : bounded D c I n (-f) := by
  intro s hs
  rw [map_neg]
  exact I.neg_mem (hf s hs)

theorem bounded_sub (D : Derivation K A A) (c : ℤ) (I : Subring A) (n : ℕ)
    {f g : A} (hf : bounded D c I n f) (hg : bounded D c I n g) :
    bounded D c I n (f-g) := by
  intro s hs
  rw [map_sub]
  exact I.sub_mem (hf s hs) (hg s hs)

theorem bounded_nat_mul (D : Derivation K A A) (c : ℤ) (I : Subring A) (n a : ℕ)
    {f : A} (hf : bounded D c I n f) : bounded D c I n ((a:A)*f) := by
  intro s hs
  rw [← nsmul_eq_mul, map_nsmul]
  exact I.nsmul_mem (hf s hs) a

theorem bounded_sum (D : Derivation K A A) (c : ℤ) (I : Subring A) (n : ℕ)
    {ι : Type*} (S : Finset ι) (f : ι → A) (hf : ∀ i∈S, bounded D c I n (f i)) :
    bounded D c I n (∑ i∈S, f i) := by
  intro s hs
  rw [map_sum]
  exact I.sum_mem (fun i hi => hf i hi s hs)

theorem bounded_deriv (D : Derivation K A A) (c : ℤ) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (n a : ℕ) {f : A} (hf : bounded D c I n f) :
    bounded D c I n (deriv D a f) := by
  intro s hs
  rw [iterate_B_deriv]
  induction a with
  | zero => exact hf s hs
  | succ a ih => rw [deriv_succ]; exact hD _ ih

theorem bounded_middle (D : Derivation K A A) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (n : ℕ)
    (hmul : ∀ c d f g, bounded D c I n f → bounded D d I n g → bounded D (c+d) I n (f*g))
    (c d : ℤ) {f g : A} (hf : bounded D c I n f) (hg : bounded D d I n g) :
    bounded D (c+d) I n (middle D 2 4 f g) := by
  unfold middle
  apply bounded_sum
  intro k _
  rw [mul_assoc]
  apply bounded_nat_mul
  exact hmul _ _ _ _ (bounded_deriv D c I hD n _ hf) (bounded_deriv D d I hD n _ hg)

variable [CharZero K]

/-- The all-order product theorem tracks additive charges. -/
theorem bounded_mul (D : Derivation K A A) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (n : ℕ) (c d : ℤ) (f g : A)
    (hf : bounded D c I n f) (hg : bounded D d I n g) : bounded D (c+d) I n (f*g) := by
  induction n generalizing c d f g with
  | zero => simpa using I.mul_mem ((bounded_zero D c I f).mp hf) ((bounded_zero D d I g).mp hg)
  | succ n ih =>
    have hfl := bounded_mono D c I (Nat.le_succ n) hf
    have hgl := bounded_mono D d I (Nat.le_succ n) hg
    rw [bounded_succ] at hf hg ⊢
    refine ⟨I.mul_mem hf.1 hg.1, ?_⟩
    rw [B_mul]
    exact bounded_add D (c+d) I n
      (bounded_add D (c+d) I n (ih _ _ _ _ hf.2 hgl) (ih _ _ _ _ hfl hg.2))
      (bounded_middle D I hD n ih c d hfl hgl)

theorem inverse_defect (D : Derivation K A A) (c : ℤ) (f g : A) (hfg : f*g=1) :
    B D (-c) g = -(g*g*B D c f) - g*middle D 2 4 f g := by
  have h := B_mul D c (-c) f g
  rw [add_neg_cancel, hfg, B_zero_one] at h
  linear_combination -g*h - (B D (-c) g)*hfg

/-- Inverting an actual integral reciprocal negates the charge. -/
theorem bounded_inverse (D : Derivation K A A) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (n : ℕ) (c : ℤ) (f g : A) (hfg : f*g=1)
    (hf : bounded D c I n f) (hg : g∈I) : bounded D (-c) I n g := by
  induction n with
  | zero => simpa using hg
  | succ n ih =>
    have hfl := bounded_mono D c I (Nat.le_succ n) hf
    have hgl := ih hfl
    have hbf := (bounded_succ D c I n f).mp hf |>.2
    rw [bounded_succ]
    refine ⟨hg, ?_⟩
    rw [inverse_defect D c f g hfg]
    have hm := bounded_mul D I hD n
    apply bounded_sub
    · apply bounded_neg
      have H := hm _ _ _ _ (hm _ _ _ _ hgl hgl) hbf
      convert H using 1
      omega
    · have H := hm _ _ _ _ hgl (bounded_middle D I hD n hm c (-c) hfl hgl)
      simpa only [add_neg_cancel, add_zero] using H

theorem B_charge_shift (D : Derivation K A A) (c : ℤ) (f : A) :
    B D (c+2) f = B D c f - f := by
  simp only [B, LinearMap.smul_apply, LinearMap.sub_apply, LinearMap.id_apply]
  simp only [Int.cast_add, Int.cast_ofNat, Algebra.smul_def, map_add, map_ofNat]
  have hc := congrArg (algebraMap K A) (inv_mul_cancel₀ (by norm_num : (2:K)≠0))
  simp only [map_mul, map_ofNat, map_one] at hc
  linear_combination -f*hc

theorem bounded_charge_shift (D : Derivation K A A) (c : ℤ) (I : Subring A)
    (n : ℕ) (f : A) (hf : bounded D c I n f) : bounded D (c+2) I n f := by
  induction n generalizing f with
  | zero => simpa using hf
  | succ n ih =>
    have hfl := bounded_mono D c I (Nat.le_succ n) hf
    rw [bounded_succ] at hf ⊢
    refine ⟨hf.1, ?_⟩
    rw [B_charge_shift]
    exact bounded_sub D (c+2) I n (ih _ hf.2) (ih _ hfl)

theorem flat_inverse (D : Derivation K A A) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (c : ℤ) (f g : A) (hfg : f*g=1)
    (hf : flat D c I f) (hg : g∈I) : flat D (-c) I g := by
  intro s
  exact bounded_inverse D I hD s c f g hfg (fun k _ => hf k) hg s le_rfl

theorem flat_charge_shift (D : Derivation K A A) (c : ℤ) (I : Subring A)
    (f : A) (hf : flat D c I f) : flat D (c+2) I f := by
  intro s
  exact bounded_charge_shift D c I s f (fun k _ => hf k) s le_rfl

end KomorebiPaperIX.ChargedDworkClosure
