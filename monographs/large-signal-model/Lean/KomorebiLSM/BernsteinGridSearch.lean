import KomorebiLSM.DyadicBernsteinCertificate
import Mathlib.Logic.Encodable.Pi

set_option autoImplicit false
namespace Komorebi.LSM.BernsteinGridSearch
open TensorBernsteinCertificate
noncomputable section

/-- Proof-free finite rational leaf data; dimensions and every coefficient are enumerated. -/
abbrev LeafData := Σ m : ℕ, Σ n : ℕ, Fin (m+1) → Fin (n+1) → ℚ

def leafValid (p : Polynomial₂) (R : Rectangle) (d : LeafData) : Prop :=
  (∀ i j,0≤d.2.2 i j) ∧ R.localPolynomial p=tensorPolynomial d.2.2

instance decidableLeafValid (p : Polynomial₂) (R : Rectangle) (d : LeafData) :
    Decidable (leafValid p R d) := by unfold leafValid; infer_instance

def leafCertificate (p : Polynomial₂) (R : Rectangle) (d : LeafData) (h : leafValid p R d) :
    LocalCertificate p R where
  degreeX := d.1
  degreeY := d.2.1
  coefficient := d.2.2
  nonneg := h.1
  identity := h.2

def leafData {p : Polynomial₂} {R : Rectangle} (c : LocalCertificate p R) : LeafData :=
  ⟨c.degreeX,c.degreeY,c.coefficient⟩

theorem leafData_valid {p : Polynomial₂} {R : Rectangle} (c : LocalCertificate p R) :
    leafValid p R (leafData c) := ⟨c.nonneg,c.identity⟩

/-- Every round has all four children; no arbitrary rectangle list is accepted. -/
def GridData : ℕ → Type
  | 0 => LeafData
  | N+1 => Bool → Bool → GridData N

instance encodableGridData (N : ℕ) : Encodable (GridData N) := by
  induction N with
  | zero => change Encodable LeafData; infer_instance
  | succ N ih => change Encodable (Bool → Bool → GridData N); infer_instance

def gridValid (p : Polynomial₂) (R : Rectangle) : (N : ℕ) → GridData N → Prop
  | 0,d => leafValid p R d
  | N+1,d => ∀ a b,gridValid p (R.quarter a b) N (d a b)

instance decidableGridValid (p : Polynomial₂) (R : Rectangle) (N : ℕ) (d : GridData N) :
    Decidable (gridValid p R N d) := by
  induction N generalizing R with
  | zero => exact decidableLeafValid p R d
  | succ N ih =>
    change Decidable (∀ a b,gridValid p (R.quarter a b) N (d a b))
    letI (a b : Bool) : Decidable (gridValid p (R.quarter a b) N (d a b)) := ih _ _
    infer_instance

def toUniform (p : Polynomial₂) (R : Rectangle) :
    {N : ℕ} → (d : GridData N) → gridValid p R N d → UniformCertificate p R N
  | 0,d,h => leafCertificate p R d h
  | _+1,d,h => fun a b => toUniform p (R.quarter a b) (d a b) (h a b)

def ofUniform {p : Polynomial₂} {R : Rectangle} :
    {N : ℕ} → UniformCertificate p R N → GridData N
  | 0,c => leafData c
  | _+1,c => fun a b => ofUniform (c a b)

theorem ofUniform_valid {p : Polynomial₂} {R : Rectangle} {N : ℕ}
    (c : UniformCertificate p R N) : gridValid p R N (ofUniform c) := by
  induction N generalizing R with
  | zero => exact leafData_valid c
  | succ N ih => exact fun a b => ih (c a b)

theorem ofUniform_toUniform (p : Polynomial₂) (R : Rectangle) {N : ℕ}
    (d : GridData N) (h : gridValid p R N d) : ofUniform (toUniform p R d h)=d := by
  induction N generalizing R with
  | zero => rfl
  | succ N ih =>
    funext a b
    exact ih (R.quarter a b) (d a b) (h a b)

/-- Acceptance is equivalent to a certificate with exactly the enumerated finite data. -/
theorem gridValid_iff (p : Polynomial₂) (R : Rectangle) (N : ℕ) (d : GridData N) :
    gridValid p R N d ↔ ∃ c : UniformCertificate p R N, ofUniform c=d := by
  constructor
  · intro h
    exact ⟨toUniform p R d h,ofUniform_toUniform p R d h⟩
  · rintro ⟨c,hc⟩
    rw [← hc]
    exact ofUniform_valid c

section Enumeration
variable {α : Type*} [Encodable α] (valid : α → Prop) [DecidablePred valid]

/-- One actual decoded finite description is tested at each dovetailed stage. -/
def step (k : ℕ) : Option α :=
  match (Encodable.decode k : Option α) with
  | none => none
  | some a => if valid a then some a else none

theorem step_sound {k : ℕ} {a : α} (h : step valid k=some a) : valid a := by
  unfold step at h
  cases hd : (Encodable.decode k : Option α) with
  | none => simp [hd] at h
  | some b =>
    rw [hd] at h
    by_cases hb : valid b
    · simp [hb] at h
      subst a
      exact hb
    · simp [hb] at h

theorem step_complete (a : α) (ha : valid a) :
    step valid (Encodable.encode a)=some a := by simp [step,ha]

/-- The bounded search retains the first accepted description. -/
def search : ℕ → Option α
  | 0 => step valid 0
  | k+1 => match search k with
    | none => step valid (k+1)
    | some a => some a

theorem search_sound {k : ℕ} {a : α} (h : search valid k=some a) : valid a := by
  induction k with
  | zero => exact step_sound valid h
  | succ k ih =>
    cases hk : search valid k with
    | none => exact step_sound valid (by simpa [search,hk] using h)
    | some b =>
      have he : b=a := by simpa [search,hk] using h
      subst a
      exact ih hk

theorem search_add {k : ℕ} {a : α} (h : search valid k=some a) (j : ℕ) :
    search valid (k+j)=some a := by
  induction j with
  | zero => simpa using h
  | succ j ih => simp [search,ih]

theorem search_eventually (hexists : ∃ a,valid a) :
    ∃ k a,valid a ∧ ∀ m,k≤m → search valid m=some a := by
  obtain ⟨a,ha⟩ := hexists
  have hk := step_complete valid a ha
  have hfound (k : ℕ) : (∃ a,step valid k=some a) → ∃ a,search valid k=some a := by
    cases k with
    | zero => exact fun h => h
    | succ k =>
      intro h
      cases hs : search valid k with
      | none => simpa [search,hs] using h
      | some b => exact ⟨b,by simp [search,hs]⟩
  obtain ⟨b,hb⟩ := hfound (Encodable.encode a) ⟨a,hk⟩
  refine ⟨Encodable.encode a,b,search_sound valid hb,?_⟩
  intro m hm
  have h := search_add valid hb (m-Encodable.encode a)
  simpa only [Nat.add_sub_of_le hm] using h
end Enumeration

end
end Komorebi.LSM.BernsteinGridSearch
