import KomorebiLSM.TensorBernsteinCertificate

/-! Complete dyadic subdivision attains every prescribed positive cell size. -/
set_option autoImplicit false
namespace Komorebi.LSM.TensorBernsteinCertificate
noncomputable section

/-- One dyadic bisection, with both branches represented explicitly. -/
def Rectangle.half (R : Rectangle) (axis : Fin 2) (upper : Bool) : Rectangle :=
  if upper then R.upper axis else R.lower axis

theorem Rectangle.half_domain_subset (R : Rectangle) (axis : Fin 2) (upper : Bool) :
    (R.half axis upper).domain⊆R.domain := by
  intro x hx i
  cases upper
  · have h := hx i
    constructor
    · exact h.1
    · by_cases he : i=axis
      · subst i
        simp [Rectangle.half,Rectangle.lower] at h
        have hp : (R.lo axis : ℝ)<R.hi axis := by exact_mod_cast R.proper axis
        linarith
      · simpa [Rectangle.half,Rectangle.lower,he] using h.2
  · have h := hx i
    constructor
    · by_cases he : i=axis
      · subst i
        simp [Rectangle.half,Rectangle.upper] at h
        have hp : (R.lo axis : ℝ)<R.hi axis := by exact_mod_cast R.proper axis
        linarith
      · simpa [Rectangle.half,Rectangle.upper,he] using h.1
    · exact h.2

def Rectangle.quarter (R : Rectangle) (upperX upperY : Bool) : Rectangle :=
  (R.half 0 upperX).half 1 upperY

theorem Rectangle.quarter_domain_subset (R : Rectangle) (upperX upperY : Bool) :
    (R.quarter upperX upperY).domain⊆R.domain :=
  (Rectangle.half_domain_subset _ _ _).trans (Rectangle.half_domain_subset _ _ _)

theorem Rectangle.quarter_width (R : Rectangle) (upperX upperY : Bool) (i : Fin 2) :
    (R.quarter upperX upperY).width i=R.width i/2 := by
  fin_cases i <;> cases upperX <;> cases upperY <;>
    simp [Rectangle.quarter,Rectangle.half,Rectangle.lower,Rectangle.upper,Rectangle.width] <;> ring

/-- A complete four-child round is a complete binary split at each of its two axes. -/
def SubdivisionWitness.of_quarters {p : Polynomial₂} {R : Rectangle}
    (w : ∀ upperX upperY,SubdivisionWitness p (R.quarter upperX upperY)) : SubdivisionWitness p R :=
  .split 0 (.split 1 (w false false) (w false true))
    (.split 1 (w true false) (w true true))

/-- At depth `N` each coordinate has been halved `N` times. -/
theorem witness_of_scale {p : Polynomial₂} {root : Rectangle} {delta epsilon : ℝ}
    (hepsilon : epsilon<delta)
    (hcert : ∀ R : Rectangle,R.domain⊆root.domain →
      (∀ i,(R.width i : ℝ)<delta) → Nonempty (LocalCertificate p R))
    (N : ℕ) (R : Rectangle) (hsub : R.domain⊆root.domain)
    (hwidth : ∀ i,(R.width i : ℝ)≤(2 : ℝ)^N*epsilon) :
    Nonempty (SubdivisionWitness p R) := by
  induction N generalizing R with
  | zero =>
    have hw0 (i : Fin 2) : (R.width i : ℝ)≤epsilon := by simpa using hwidth i
    exact ⟨.leaf (hcert R hsub (fun i => (hw0 i).trans_lt hepsilon)).some⟩
  | succ N ih =>
    have hw (upperX upperY : Bool) (i : Fin 2) :
        ((R.quarter upperX upperY).width i : ℝ)≤(2 : ℝ)^N*epsilon := by
      rw [Rectangle.quarter_width]
      push_cast
      have hi := hwidth i
      rw [pow_succ] at hi
      linarith
    have hh (upperX upperY : Bool) : Nonempty (SubdivisionWitness p (R.quarter upperX upperY)) :=
      ih _ ((R.quarter_domain_subset upperX upperY).trans hsub) (hw upperX upperY)
    exact ⟨.of_quarters (fun upperX upperY => (hh upperX upperY).some)⟩

/-- No coverage oracle is supplied: a finite complete dyadic tree reaches any uniform cell size. -/
theorem witness_of_uniform_small {p : Polynomial₂} (delta : ℝ) (hdelta : 0<delta)
    (hcert : ∀ R : Rectangle,R.domain⊆square.domain →
      (∀ i,(R.width i : ℝ)<delta) → Nonempty (LocalCertificate p R)) :
    Nonempty (SubdivisionWitness p square) := by
  let epsilon : ℝ := delta/2
  have he0 : 0<epsilon := by dsimp [epsilon]; positivity
  have hed : epsilon<delta := by dsimp [epsilon]; linarith
  obtain ⟨N,hN⟩ := exists_nat_gt (2/epsilon)
  have hn : (N : ℝ)<(2 : ℝ)^N := by exact_mod_cast N.lt_two_pow_self
  have hw : (2 : ℝ)≤(2 : ℝ)^N*epsilon := by
    have hg : 2<(N : ℝ)*epsilon := (div_lt_iff₀ he0).mp hN
    nlinarith
  apply witness_of_scale hed hcert N square (Set.Subset.refl _)
  intro i
  have hs : (square.width i : ℝ)=2 := by norm_num [Rectangle.width,square]
  rw [hs]
  exact hw

/-- A literal complete grid: each round bisects both axes in all four children. -/
def UniformCertificate (p : Polynomial₂) (R : Rectangle) : ℕ → Type
  | 0 => LocalCertificate p R
  | N+1 => ∀ upperX upperY,UniformCertificate p (R.quarter upperX upperY) N

def UniformCertificate.toSubdivision {p : Polynomial₂} {R : Rectangle} :
    {N : ℕ} → UniformCertificate p R N → SubdivisionWitness p R
  | 0,c => .leaf c
  | _+1,c => .of_quarters (fun a b => (c a b).toSubdivision)

theorem UniformCertificate.sound {p : Polynomial₂} {R : Rectangle} {N : ℕ}
    (cert : UniformCertificate p R N) {x : Fin 2 → ℝ} (hx : x∈R.domain) : 0≤value p x :=
  cert.toSubdivision.sound hx

theorem uniform_of_scale {p : Polynomial₂} {root : Rectangle} {delta epsilon : ℝ}
    (hepsilon : epsilon<delta)
    (hcert : ∀ R : Rectangle,R.domain⊆root.domain →
      (∀ i,(R.width i : ℝ)<delta) → Nonempty (LocalCertificate p R))
    (N : ℕ) (R : Rectangle) (hsub : R.domain⊆root.domain)
    (hwidth : ∀ i,(R.width i : ℝ)≤(2 : ℝ)^N*epsilon) :
    Nonempty (UniformCertificate p R N) := by
  induction N generalizing R with
  | zero =>
    have hw0 (i : Fin 2) : (R.width i : ℝ)≤epsilon := by simpa using hwidth i
    exact hcert R hsub (fun i => (hw0 i).trans_lt hepsilon)
  | succ N ih =>
    have hw (upperX upperY : Bool) (i : Fin 2) :
        ((R.quarter upperX upperY).width i : ℝ)≤(2 : ℝ)^N*epsilon := by
      rw [Rectangle.quarter_width]
      push_cast
      have hi := hwidth i
      rw [pow_succ] at hi
      linarith
    exact ⟨fun a b => (ih _ ((R.quarter_domain_subset a b).trans hsub) (hw a b)).some⟩

/-- Every sufficiently fine full dyadic subdivision succeeds once a uniform small-cell bound holds. -/
theorem eventually_uniform_dyadic {p : Polynomial₂} (delta : ℝ) (hdelta : 0<delta)
    (hcert : ∀ R : Rectangle,R.domain⊆square.domain →
      (∀ i,(R.width i : ℝ)<delta) → Nonempty (LocalCertificate p R)) :
    ∃ N : ℕ,∀ M : ℕ,N≤M → Nonempty (UniformCertificate p square M) := by
  let epsilon : ℝ := delta/2
  have he0 : 0<epsilon := by dsimp [epsilon]; positivity
  have hed : epsilon<delta := by dsimp [epsilon]; linarith
  obtain ⟨N,hN⟩ := exists_nat_gt (2/epsilon)
  have hn : (N : ℝ)<(2 : ℝ)^N := by exact_mod_cast N.lt_two_pow_self
  have hw : (2 : ℝ)≤(2 : ℝ)^N*epsilon := by
    have hg : 2<(N : ℝ)*epsilon := (div_lt_iff₀ he0).mp hN
    nlinarith
  refine ⟨N,fun M hNM => ?_⟩
  apply uniform_of_scale hed hcert M square (Set.Subset.refl _)
  intro i
  have hp : (2 : ℝ)^N≤(2 : ℝ)^M := pow_le_pow_right₀ (by norm_num) hNM
  have hm := hw.trans (mul_le_mul_of_nonneg_right hp he0.le)
  have hs : (square.width i : ℝ)=2 := by norm_num [Rectangle.width,square]
  rw [hs]
  exact hm

end
end Komorebi.LSM.TensorBernsteinCertificate
