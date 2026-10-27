module
public import Mathlib.Data.Finsupp.Basic
public section
namespace H12
noncomputable def charge (a : ℤ →₀ ℤ) : ℤ := a.sum (fun _ z => z)
noncomputable def shift (a : ℤ →₀ ℤ) : ℤ →₀ ℤ := a.mapDomain (fun n => n+1)
noncomputable def boundary (a : ℤ →₀ ℤ) : ℤ →₀ ℤ := shift a - a
theorem charge_sub (a b : ℤ →₀ ℤ) : charge (a-b)=charge a-charge b := by
 exact Finsupp.sum_sub_index (fun _ _ _ => rfl)
theorem charge_add (a b : ℤ →₀ ℤ) : charge (a+b)=charge a+charge b := by
 exact Finsupp.sum_add_index' (fun _ => rfl) (fun _ _ _ => rfl)
theorem charge_single (n k : ℤ) : charge (Finsupp.single n k)=k := by
 exact Finsupp.sum_single_index rfl
theorem charge_shift (a : ℤ →₀ ℤ) : charge (shift a)=charge a := by
 exact Finsupp.sum_mapDomain_index (fun _ => rfl) (fun _ _ _ => rfl)
theorem charge_boundary (a : ℤ →₀ ℤ) : charge (boundary a)=0 := by
 rw [boundary, charge_sub, charge_shift, sub_self]
theorem nonzero_charge_not_boundary (d : ℤ →₀ ℤ) (hd : charge d≠0) :
     ¬ ∃ a, boundary a=d := by
 rintro ⟨a,ha⟩
 apply hd
 rw [←ha, charge_boundary]
theorem kernel_profile_not_boundary (k : ℤ) (hk : k≠0) :
     ¬ ∃ a, boundary a=Finsupp.single 0 (4*k) := by
 apply nonzero_charge_not_boundary
 rw [charge_single]
 omega
theorem normed_profile_not_boundary (k : ℤ) (hk : k≠0) :
     ¬ ∃ a, boundary a=Finsupp.single 0 (-8*k)+Finsupp.single (-1) (-16*k) := by
 apply nonzero_charge_not_boundary
 rw [charge_add,charge_single,charge_single]
 omega
end H12

namespace H12
/-- Pushing a divisor to any invariant label set kills translation boundaries. -/
theorem invariant_projection_kills_boundary {A B : Type*}
    (step : A → A) (label : A → B) (h : ∀ a, label (step a)=label a)
    (d : A →₀ ℤ) :
    (d.mapDomain step - d).mapDomain label=0 := by
  rw [Finsupp.mapDomain_sub, ← Finsupp.mapDomain_comp]
  have hc : label ∘ step=label := funext h
  rw [hc,sub_self]

abbrev OrbitPoint := Bool × ℤ
noncomputable def orbitShift (d : OrbitPoint →₀ ℤ) : OrbitPoint →₀ ℤ :=
  d.mapDomain (fun p => (p.1,p.2+1))
noncomputable def twoProfile (a b : ℤ) : OrbitPoint →₀ ℤ :=
  Finsupp.single (false,0) (4*a+4*b) + Finsupp.single (true,0) (-4*b)

theorem two_profile_exact (a b : ℤ)
    (d : OrbitPoint →₀ ℤ) (h : orbitShift d-d=twoProfile a b) : a=0 ∧ b=0 := by
  have hp := invariant_projection_kills_boundary (fun p : OrbitPoint => (p.1,p.2+1))
    Prod.fst (fun _ => rfl) d
  change (orbitShift d-d).mapDomain Prod.fst=0 at hp
  rw [h] at hp
  have h0 := congrArg (fun f : Bool →₀ ℤ => f false) hp
  have h1 := congrArg (fun f : Bool →₀ ℤ => f true) hp
  simp only [twoProfile,Finsupp.mapDomain_add,Finsupp.mapDomain_single,
    Finsupp.add_apply,Finsupp.single_apply,Finsupp.zero_apply] at h0 h1
  simp at h0 h1
  omega

theorem two_profile_not_boundary (a b : ℤ) (h : a≠0 ∨ b≠0) :
    ¬ ∃ d, orbitShift d-d=twoProfile a b := by
  rintro ⟨d,hd⟩
  obtain ⟨ha,hb⟩ := two_profile_exact a b d hd
  rcases h with h|h
  · exact h ha
  · exact h hb
end H12
