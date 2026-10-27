import KomorebiLSM.InstrumentContraction
import KomorebiLSM.FiniteTV

/-! P43: actual finite records and their unnormalized state trees.
Every horizon is proved by induction, without a branch-likelihood lower bound. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservationTree
open scoped BigOperators
open BaseNorm FiniteBayes

universe u
/-- Chronological fixed-length records. -/
def Record (O : Type u) : ℕ → Type u
  | 0 => PUnit.{u+1}
  | n+1 => O × Record O n

instance recordFintype {O : Type*} [Fintype O] : (n : ℕ) → Fintype (Record O n)
  | 0 => inferInstanceAs (Fintype PUnit)
  | n+1 => by
    letI : Fintype (Record O n) := recordFintype n
    exact inferInstanceAs (Fintype (O × Record O n))

theorem sum_record_zero {O : Type*} [Fintype O] (f : Record O 0 → ℝ) :
    (∑ w, f w)=f PUnit.unit := by
  let : Unique (Record O 0) := inferInstanceAs (Unique PUnit)
  exact Fintype.sum_unique f

theorem sum_record_succ {O : Type*} [Fintype O] (n : ℕ) (f : Record O (n+1) → ℝ) :
    (∑ w, f w)=∑ o, ∑ v : Record O n, f (o,v) := by
  change (∑ w : O × Record O n, f w)=_
  exact Fintype.sum_prod_type f

theorem record_pair_eq_iff {O : Type*} {n : ℕ} (a b : O) (v w : Record O n) :
    (show Record O (n+1) from (a,v))=(b,w) ↔ a=b ∧ v=w := by
  constructor
  · intro h; exact ⟨congrArg Prod.fst h,congrArg Prod.snd h⟩
  · rintro ⟨rfl,rfl⟩; rfl

def recordList {O : Type*} : {n : ℕ} → Record O n → List O
  | 0, _ => []
  | _+1, w => w.1 :: recordList w.2

theorem recordList_length {O : Type*} (n : ℕ) (w : Record O n) : (recordList w).length=n := by
  induction n with
  | zero => rfl
  | succ n ih => exact congrArg Nat.succ (ih w.2)

def recordMap {O J : Type*} (f : O → J) : {n : ℕ} → Record O n → Record J n
  | 0, _ => PUnit.unit
  | _+1, w => (f w.1,recordMap f w.2)

variable {E O : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [Fintype O] (C : ProbabilityCone E)

/-- The next map is selected using the complete chronological prefix. -/
def recordState (B : List O → O → E →ₗ[ℝ] E) :
    (n : ℕ) → List O → E → Record O n → E
  | 0, _, x, _ => x
  | n+1, h, x, w => recordState B n (h ++ [w.1]) (B h w.1 x) w.2

noncomputable def recordLaw (B : List O → O → E →ₗ[ℝ] E) (n : ℕ) (h : List O) (x : E) :
    Record O n → ℝ := fun w => C.mass (recordState B n h x w)

theorem recordState_mem (B : List O → O → E →ₗ[ℝ] E)
    (hB : ∀ h, C.Instrument (B h)) (n : ℕ) (h : List O) (x : E) (hx : x ∈ C.carrier)
    (w : Record O n) : recordState B n h x w ∈ C.carrier := by
  induction n generalizing h x with
  | zero => exact hx
  | succ n ih => exact ih _ _ ((hB h).1 w.1 x hx) w.2

theorem record_mass (B : List O → O → E →ₗ[ℝ] E)
    (hB : ∀ h, C.Instrument (B h)) (n : ℕ) (h : List O) (x : E) :
    ∑ w, recordLaw C B n h x w=C.mass x := by
  induction n generalizing h x with
  | zero =>
    change (∑ _ : PUnit, C.mass x)=C.mass x
    simp
  | succ n ih =>
    change (∑ w : O × Record O n, recordLaw C B n (h++[w.1]) (B h w.1 x) w.2)=C.mass x
    rw [Fintype.sum_prod_type]
    simp_rw [ih]
    exact (hB h).2 x

theorem record_prior (B : List O → O → E →ₗ[ℝ] E)
    (hB : ∀ h, C.Instrument (B h)) (n : ℕ) (h : List O) (x : E) (hx : x ∈ C.base) :
    IsPrior (recordLaw C B n h x) :=
  ⟨fun w => C.mass_nonneg (recordState_mem C B hB n h x hx.1 w),
    (record_mass C B hB n h x).trans hx.2⟩

noncomputable def tailBudget (ε : ℕ → ℝ) (t n : ℕ) : ℝ := ∑ k ∈ Finset.range n, ε (t+k)

theorem tailBudget_succ (ε : ℕ → ℝ) (t n : ℕ) :
    tailBudget ε t (n+1)=ε t+tailBudget ε (t+1) n := by
  unfold tailBudget
  rw [Finset.sum_range_succ']
  simp only [Nat.add_zero]
  rw [add_comm]
  congr 1
  apply Finset.sum_congr rfl
  intro k _
  congr 1
  omega

/-- The central positive-mass-weighted tree induction. -/
theorem record_state_error (B D : List O → O → E →ₗ[ℝ] E)
    (hB : ∀ h, C.Instrument (B h)) (hD : ∀ h, C.Instrument (D h))
    (ε : ℕ → ℝ) (hε : ∀ h z, z ∈ C.base → C.discrepancy (B h) (D h) z ≤ ε h.length)
    (n : ℕ) (h : List O) (x y : E) (hy : y ∈ C.carrier) :
    (∑ w, C.value (recordState B n h x w-recordState D n h y w)) ≤
      C.value (x-y)+C.mass y*tailBudget ε h.length n := by
  induction n generalizing h x y with
  | zero =>
    change (∑ _ : PUnit, C.value (x-y)) ≤ _
    simp [tailBudget]
  | succ n ih =>
    change (∑ w : O × Record O n, C.value
      (recordState B n (h++[w.1]) (B h w.1 x) w.2-
       recordState D n (h++[w.1]) (D h w.1 y) w.2)) ≤ _
    rw [Fintype.sum_prod_type]
    calc
      _ ≤ ∑ o, (C.value (B h o x-D h o y)+
          C.mass (D h o y)*tailBudget ε (h.length+1) n) := by
        apply Finset.sum_le_sum
        intro o _
        simpa only [List.length_append,List.length_singleton] using
          ih (h++[o]) (B h o x) (D h o y) ((hD h).1 o y hy)
      _ = (∑ o, C.value (B h o x-D h o y))+C.mass y*tailBudget ε (h.length+1) n := by
        rw [Finset.sum_add_distrib,← Finset.sum_mul,(hD h).2]
      _ ≤ C.value (x-y)+ε h.length*C.mass y+C.mass y*tailBudget ε (h.length+1) n :=
        add_le_add (C.instrument_pair_step (B h) (D h) (hB h) (ε h.length) (hε h) x hy) le_rfl
      _ = C.value (x-y)+C.mass y*tailBudget ε h.length (n+1) := by
        rw [tailBudget_succ]
        ring

/-- Total variation is bounded by the summed unnormalized state differences. -/
theorem record_l1_le_state_error (B D : List O → O → E →ₗ[ℝ] E)
    (n : ℕ) (h : List O) (x y : E) :
    FiniteTV.l1 (recordLaw C B n h x-recordLaw C D n h y) ≤
      ∑ w, C.value (recordState B n h x w-recordState D n h y w) := by
  unfold FiniteTV.l1
  apply Finset.sum_le_sum
  intro w _
  simpa only [recordLaw,Pi.sub_apply,map_sub] using C.abs_mass_le (recordState B n h x w-recordState D n h y w)

/-- P43 for arbitrary history-dependent finite branch families. -/
theorem observation_tree_tv_bound (B D : List O → O → E →ₗ[ℝ] E)
    (hB : ∀ h, C.Instrument (B h)) (hD : ∀ h, C.Instrument (D h))
    (ε : ℕ → ℝ) (hε : ∀ h z, z ∈ C.base → C.discrepancy (B h) (D h) z ≤ ε h.length)
    (n : ℕ) (x y : E) (hx : x ∈ C.base) (hy : y ∈ C.base) :
    FiniteTV.distance (recordLaw C B n [] x) (recordLaw C D n [] y) ≤
      min 1 (C.value (x-y)/2+(∑ t ∈ Finset.range n, ε t)/2) := by
  apply le_min
  · exact FiniteTV.distance_le_one _ _ (record_prior C B hB n [] x hx) (record_prior C D hD n [] y hy)
  · have hb := (record_l1_le_state_error C B D n [] x y).trans
      (record_state_error C B D hB hD ε hε n [] x y hy.1)
    simp only [hy.2,one_mul,List.length_nil,tailBudget,Nat.zero_add] at hb
    unfold FiniteTV.distance
    linarith

end Komorebi.LSM.ObservationTree
