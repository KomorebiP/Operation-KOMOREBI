module

public import CubicDworkAlgebra

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.CubicDworkClosure

open DworkAlgebra

variable {K A : Type*} [Field K] [CommRing A] [Algebra K A] [CharZero K]

theorem deriv_add (D : Derivation K A A) (n m : ℕ) (f : A) :
    deriv D n (deriv D m f) = deriv D (n+m) f := by
  simp [deriv, pow_add, Module.End.mul_apply]

theorem B_deriv (D : Derivation K A A) (p n : ℕ) (f : A) :
    CubicDworkAlgebra.B D p (deriv D n f) = deriv D n (CubicDworkAlgebra.B D p f) := by
  simp only [CubicDworkAlgebra.B, LinearMap.smul_apply, LinearMap.sub_apply, map_smul, map_sub, deriv_add]
  rw [Nat.add_comm (p^3) n, Nat.add_comm (p^2) n]

theorem iterate_B_deriv (D : Derivation K A A) (p s n : ℕ) (f : A) :
    (CubicDworkAlgebra.B D p ^ s) (deriv D n f) = deriv D n ((CubicDworkAlgebra.B D p ^ s) f) := by
  induction s with
  | zero => rfl
  | succ s ih =>
    simp only [pow_succ', Module.End.mul_apply, ih, B_deriv]

theorem deriv_one_eq_zero (D : Derivation K A A) (n : ℕ) (hn : 0<n) :
    deriv D n (1:A) = 0 := by
  obtain ⟨n, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hn)
  rw [deriv_succ_right, Derivation.map_one_eq_zero, map_zero]

@[simp] theorem B_one (D : Derivation K A A) (p : ℕ) (hp : 0<p) : CubicDworkAlgebra.B D p 1 = 0 := by
  simp [CubicDworkAlgebra.B, deriv_one_eq_zero D (p^2) (pow_pos hp 2), deriv_one_eq_zero D (p^3) (pow_pos hp 3)]

/-- Integrality of all normalized defects through a specified finite order. -/
def bounded (D : Derivation K A A) (p : ℕ) (I : Subring A) (n : ℕ) (f : A) : Prop :=
  ∀ s ≤ n, (CubicDworkAlgebra.B D p ^ s) f ∈ I

/-- The full all-iterate condition, with no product or inverse closure built into its definition. -/
def flat (D : Derivation K A A) (p : ℕ) (I : Subring A) (f : A) : Prop :=
  ∀ s, (CubicDworkAlgebra.B D p ^ s) f ∈ I

@[simp] theorem bounded_zero (D : Derivation K A A) (p : ℕ) (I : Subring A) (f : A) :
    bounded D p I 0 f ↔ f∈I := by
  simp [bounded]

theorem bounded_mono (D : Derivation K A A) (p : ℕ) (I : Subring A) {n m : ℕ}
    (h : m≤n) {f : A} (hf : bounded D p I n f) : bounded D p I m f :=
  fun s hs => hf s (hs.trans h)

theorem bounded_succ (D : Derivation K A A) (p : ℕ) (I : Subring A) (n : ℕ) (f : A) :
    bounded D p I (n+1) f ↔ f∈I ∧ bounded D p I n (CubicDworkAlgebra.B D p f) := by
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

theorem bounded_add (D : Derivation K A A) (p : ℕ) (I : Subring A) (n : ℕ)
    {f g : A} (hf : bounded D p I n f) (hg : bounded D p I n g) :
    bounded D p I n (f+g) := by
  intro s hs
  rw [map_add]
  exact I.add_mem (hf s hs) (hg s hs)

theorem bounded_neg (D : Derivation K A A) (p : ℕ) (I : Subring A) (n : ℕ)
    {f : A} (hf : bounded D p I n f) : bounded D p I n (-f) := by
  intro s hs
  rw [map_neg]
  exact I.neg_mem (hf s hs)

theorem bounded_sub (D : Derivation K A A) (p : ℕ) (I : Subring A) (n : ℕ)
    {f g : A} (hf : bounded D p I n f) (hg : bounded D p I n g) :
    bounded D p I n (f-g) := by
  intro s hs
  rw [map_sub]
  exact I.sub_mem (hf s hs) (hg s hs)

theorem bounded_nat_mul (D : Derivation K A A) (p : ℕ) (I : Subring A) (n a : ℕ)
    {f : A} (hf : bounded D p I n f) : bounded D p I n ((a:A)*f) := by
  intro s hs
  rw [← nsmul_eq_mul, map_nsmul]
  exact I.nsmul_mem (hf s hs) a

theorem bounded_sum (D : Derivation K A A) (p : ℕ) (I : Subring A) (n : ℕ)
    {ι : Type*} (S : Finset ι) (f : ι → A) (hf : ∀ i∈S, bounded D p I n (f i)) :
    bounded D p I n (∑ i∈S, f i) := by
  intro s hs
  rw [map_sum]
  exact I.sum_mem (fun i hi => hf i hi s hs)

theorem bounded_deriv (D : Derivation K A A) (p : ℕ) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (n a : ℕ) {f : A} (hf : bounded D p I n f) :
    bounded D p I n (deriv D a f) := by
  intro s hs
  rw [iterate_B_deriv]
  induction a with
  | zero => exact hf s hs
  | succ a ih => rw [deriv_succ]; exact hD _ ih

theorem bounded_middle (D : Derivation K A A) (p : ℕ) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (n q : ℕ)
    (hmul : ∀ f g, bounded D p I n f → bounded D p I n g → bounded D p I n (f*g))
    {f g : A} (hf : bounded D p I n f) (hg : bounded D p I n g) :
    bounded D p I n (middle D p q f g) := by
  unfold middle
  apply bounded_sum
  intro k _
  rw [mul_assoc]
  apply bounded_nat_mul
  exact hmul _ _ (bounded_deriv D p I hD n _ hf) (bounded_deriv D p I hD n _ hg)


/-- Multiplicative closure is proved by induction in the defect order. -/
theorem bounded_mul (D : Derivation K A A) (p : ℕ) (hp : p.Prime) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (n : ℕ) (f g : A)
    (hf : bounded D p I n f) (hg : bounded D p I n g) : bounded D p I n (f*g) := by
  induction n generalizing f g with
  | zero => simpa using I.mul_mem (bounded_zero D p I f |>.mp hf) (bounded_zero D p I g |>.mp hg)
  | succ n ih =>
    have hfl := bounded_mono D p I (Nat.le_succ n) hf
    have hgl := bounded_mono D p I (Nat.le_succ n) hg
    rw [bounded_succ] at hf hg ⊢
    refine ⟨I.mul_mem hf.1 hg.1, ?_⟩
    rw [CubicDworkAlgebra.B_mul D p hp]
    apply bounded_sub
    · apply bounded_add
      · exact bounded_add D p I n (ih _ _ hf.2 hgl) (ih _ _ hfl hg.2)
      · exact bounded_middle D p I hD n _ ih hfl hgl
    · exact bounded_middle D p I hD n _ ih hfl hgl

/-- The inverse defect identity is derived from the actual equation f*g=1. -/
theorem inverse_defect (D : Derivation K A A) (p : ℕ) (hp : p.Prime)
    (f g : A) (hfg : f*g=1) :
    CubicDworkAlgebra.B D p g = -(g*g*CubicDworkAlgebra.B D p f) - g*middle D p (p^3) f g + g*middle D p (p^2) f g := by
  have h := CubicDworkAlgebra.B_mul D p hp f g
  rw [hfg, B_one D p hp.pos] at h
  linear_combination -g*h - (CubicDworkAlgebra.B D p g)*hfg

/-- All inverse defects are integral, not merely the first defect. -/
theorem bounded_inverse (D : Derivation K A A) (p : ℕ) (hp : p.Prime) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (n : ℕ) (f g : A) (hfg : f*g=1)
    (hf : bounded D p I n f) (hg : g∈I) : bounded D p I n g := by
  induction n with
  | zero => simpa using hg
  | succ n ih =>
    have hfl := bounded_mono D p I (Nat.le_succ n) hf
    have hgl := ih hfl
    have hbf := (bounded_succ D p I n f).mp hf |>.2
    rw [bounded_succ]
    refine ⟨hg, ?_⟩
    rw [inverse_defect D p hp f g hfg]
    have hm := bounded_mul D p hp I hD n
    apply bounded_add
    · apply bounded_sub
      · exact bounded_neg D p I n (hm _ _ (hm _ _ hgl hgl) hbf)
      · exact hm _ _ hgl (bounded_middle D p I hD n _ hm hfl hgl)
    · exact hm _ _ hgl (bounded_middle D p I hD n _ hm hfl hgl)

/-- Unbounded-order product closure; no closure premise is assumed. -/
theorem flat_mul (D : Derivation K A A) (p : ℕ) (hp : p.Prime) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) {f g : A} (hf : flat D p I f) (hg : flat D p I g) :
    flat D p I (f*g) := by
  intro s
  exact bounded_mul D p hp I hD s f g (fun k _ => hf k) (fun k _ => hg k) s le_rfl

/-- Unbounded-order reciprocal closure for an actual integral inverse. -/
theorem flat_inverse (D : Derivation K A A) (p : ℕ) (hp : p.Prime) (I : Subring A)
    (hD : ∀ f∈I, D f∈I) (f g : A) (hfg : f*g=1)
    (hf : flat D p I f) (hg : g∈I) : flat D p I g := by
  intro s
  exact bounded_inverse D p hp I hD s f g hfg (fun k _ => hf k) hg s le_rfl

end KomorebiPaperIX.CubicDworkClosure
