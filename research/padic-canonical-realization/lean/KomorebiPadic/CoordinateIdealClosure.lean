import KomorebiPadic.PrimePowerIdeals
import KomorebiPadic.CoordinateSupport

/-! # Least invariant products of p-power coordinate ideals
The order is expressed in capacities: larger capacity means a larger ideal.
-/
namespace KomorebiPadic
namespace CoordinateIdeal
open PrimePowerIdeal
variable {p r : ℕ} {I A : Type*} [Fintype I] [DecidableEq I] [Fintype A]

abbrev System := CoordinateSupport.System (ZMod (p^r)) I A

def InBox (w : I → ℕ) (x : I → ZMod (p^r)) : Prop := ∀ i, x i ∈ capacityIdeal p r (w i)

def Closed (M : System (p := p) (r := r) (I := I) (A := A)) (w : I → ℕ) : Prop :=
  (∀ i, capacity p r (M.initial i) ≤ w i) ∧
    ∀ d i j, transfer p r (M.transition d (Pi.single i 1) j) (w i) ≤ w j

noncomputable def propagation (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A)) :
    DegreePropagationSystem (Fintype.card I) (Fintype.card (A × I)) r where
  target _ b := Fintype.equivFin I ((Fintype.equivFin (A × I)).symm b).2
  seed i := capacity p r (M.initial ((Fintype.equivFin I).symm i))
  seed_bound _ := capacity_le p r _
  transfer i b := transfer p r (M.transition ((Fintype.equivFin (A × I)).symm b).1
    (Pi.single ((Fintype.equivFin I).symm i) 1) ((Fintype.equivFin (A × I)).symm b).2)
  transfer_mono _ _ := transfer_mono hp _
  transfer_bound _ _ := transfer_le p r _ r

noncomputable def finiteProfile (w : I → ℕ) : Fin (Fintype.card I) → ℕ :=
  fun i => w ((Fintype.equivFin I).symm i)
noncomputable def iterate (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A))
    (n : ℕ) (i : I) : ℕ := degreeProfileIterate (propagation hp M) n (Fintype.equivFin I i)
noncomputable def least (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A)) : I → ℕ :=
  iterate hp M (Fintype.card I * r)

theorem closed_iff_propagation (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (w : I → ℕ) :
    Closed M w ↔ DegreeProfileClosed (propagation hp M) (finiteProfile w) := by
  constructor
  · rintro ⟨hs, ht⟩
    constructor
    · intro i; exact hs _
    · intro i b
      simpa [propagation, finiteProfile] using
        ht ((Fintype.equivFin (A × I)).symm b).1 ((Fintype.equivFin I).symm i)
          ((Fintype.equivFin (A × I)).symm b).2
  · rintro ⟨hs, ht⟩
    constructor
    · intro i
      simpa [propagation, finiteProfile] using hs (Fintype.equivFin I i)
    · intro d i j
      simpa [propagation, finiteProfile] using
        ht (Fintype.equivFin I i) (Fintype.equivFin (A × I) (d,j))

theorem least_closed (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A)) :
    Closed M (least hp M) := by
  apply (closed_iff_propagation hp M _).mpr
  have he : finiteProfile (least hp M) = leastDegreeProfile (propagation hp M) := by
    funext i
    simp [finiteProfile, least, iterate, leastDegreeProfile]
  rw [he]
  exact leastDegreeProfile_closed _

theorem least_le (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A))
    (w : I → ℕ) (hw : Closed M w) : least hp M ≤ w := by
  intro i
  have h := leastDegreeProfile_le (propagation hp M) (finiteProfile w)
    ((closed_iff_propagation hp M w).mp hw) (Fintype.equivFin I i)
  simpa [least, iterate, finiteProfile, leastDegreeProfile] using h

theorem least_bound (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A))
    (i : I) : least hp M i ≤ r := leastDegreeProfile_bound _ _

theorem iterate_stabilizes (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A)) :
    iterate hp M (Fintype.card I*r+1) = least hp M := by
  funext i
  exact congrFun (degreeProfileIterate_stabilizes (propagation hp M)) (Fintype.equivFin I i)

theorem least_unique (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A))
    (w : I → ℕ) (hw : Closed M w) (hl : ∀ v, Closed M v → w ≤ v) : w = least hp M :=
  le_antisymm (hl _ (least_closed hp M)) (least_le hp M w hw)

omit [Fintype I] [Fintype A] in
theorem initial_inBox (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A))
    {w : I → ℕ} (hc : Closed M w) : InBox (p := p) (r := r) w M.initial :=
  fun i => (capacity_le_iff hp _).mp (hc.1 i)

omit [Fintype A] in
theorem transition_inBox (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A))
    {w : I → ℕ} (hc : Closed M w) (d : A) {x : I → ZMod (p^r)} (hx : InBox w x) :
    InBox w (M.transition d x) := by
  intro j
  rw [CoordinateSupport.transition_eq_sum]
  apply Ideal.sum_mem
  intro i _
  exact (transfer_spec hp _).mp (hc.2 d i j) (x i) (hx i)

omit [Fintype A] in
/-- Generator tests are equivalent to full ideal-product invariance. -/
theorem closed_iff_invariant (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (w : I → ℕ) :
    Closed M w ↔ InBox w M.initial ∧ ∀ d x, InBox w x → InBox w (M.transition d x) := by
  classical
  constructor
  · intro hc
    exact ⟨initial_inBox hp M hc, fun d _ hx => transition_inBox hp M hc d hx⟩
  · rintro ⟨hi, ht⟩
    constructor
    · intro i
      exact (capacity_le_iff hp _).mpr (hi i)
    · intro d i j
      apply (capacity_le_iff hp _).mpr
      have hx : InBox (p := p) (r := r) w
          ((p : ZMod (p^r))^(r-w i) • Pi.single i (1 : ZMod (p^r))) := by
        intro k
        by_cases hk : k = i
        · subst k
          simp [capacityIdeal, powerIdeal]
        · simp [Ne.symm hk]
      have h := ht d _ hx j
      simpa only [map_smul, Pi.smul_apply, smul_eq_mul] using h

omit [Fintype I] [DecidableEq I] in
theorem inBox_mono {v w : I → ℕ} (hvw : v ≤ w) {x : I → ZMod (p^r)}
    (hx : InBox v x) : InBox w x := fun i => capacityIdeal_mono p r (hvw i) (hx i)

theorem least_minimal_invariant (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (w : I → ℕ)
    (hi : InBox w M.initial) (ht : ∀ d x, InBox w x → InBox w (M.transition d x)) :
    ∀ x : I → ZMod (p^r), InBox (least hp M) x → InBox w x := by
  intro x hx
  exact inBox_mono (least_le hp M w ((closed_iff_invariant hp M w).mpr ⟨hi,ht⟩)) hx

def boxModule (w : I → ℕ) : Submodule (ZMod (p^r)) (I → ZMod (p^r)) where
  carrier := {x | InBox w x}
  zero_mem' := fun i => (capacityIdeal p r (w i)).zero_mem
  add_mem' hx hy := fun i => (capacityIdeal p r (w i)).add_mem (hx i) (hy i)
  smul_mem' a _x hx := fun i => (capacityIdeal p r (w i)).mul_mem_left a (hx i)

abbrev State (w : I → ℕ) := boxModule (p := p) (r := r) w

noncomputable def initial (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) : State (p := p) (r := r) (least hp M) :=
  ⟨M.initial, initial_inBox hp M (least_closed hp M)⟩

noncomputable def transition (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (d : A) :
    State (p := p) (r := r) (least hp M) →ₗ[ZMod (p^r)] State (p := p) (r := r) (least hp M) where
  toFun x := ⟨M.transition d x.val, transition_inBox hp M (least_closed hp M) d x.property⟩
  map_add' x y := by apply Subtype.ext; exact (M.transition d).map_add _ _
  map_smul' a x := by apply Subtype.ext; exact (M.transition d).map_smul _ _

noncomputable def run (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A)) :
    List A → State (p := p) (r := r) (least hp M) → State (p := p) (r := r) (least hp M)
  | [], x => x
  | d :: ds, x => run hp M ds (transition hp M d x)

theorem run_embedding (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A))
    (ds : List A) (x : State (p := p) (r := r) (least hp M)) :
    (run hp M ds x).val = CoordinateSupport.run M ds x.val := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (transition hp M d x)

noncomputable def supportCapacity (s : Finset I) : I → ℕ := fun i => if i ∈ s then r else 0

omit [Fintype I] in
theorem inBox_supportCapacity (s : Finset I) (x : I → ZMod (p^r)) :
    InBox (supportCapacity (r := r) s) x ↔ CoordinateSupport.Supported s x := by
  classical
  constructor
  · intro h i hi
    have hh := h i
    simpa [supportCapacity, hi] using hh
  · intro h i
    by_cases hi : i ∈ s
    · simp [supportCapacity, hi]
    · simpa [supportCapacity, hi] using h i hi

theorem least_supported (hp : 0 < p) (M : System (p := p) (r := r) (I := I) (A := A))
    (x : State (p := p) (r := r) (least hp M)) :
    CoordinateSupport.Supported (CoordinateSupport.least M) x.val := by
  have hs := (CoordinateSupport.closed_iff_invariant M (CoordinateSupport.least M)).mp
    (CoordinateSupport.least_closed M)
  have hh : Closed M (supportCapacity (r := r) (CoordinateSupport.least M)) := by
    apply (closed_iff_invariant hp M _).mpr
    exact ⟨(inBox_supportCapacity _ _).mpr hs.1,
      fun d x hx => (inBox_supportCapacity _ _).mpr (hs.2 d x ((inBox_supportCapacity _ _).mp hx))⟩
  exact (inBox_supportCapacity _ _).mp (inBox_mono (least_le hp M _ hh) x.property)

noncomputable def supportEmbedding (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (x : State (p := p) (r := r) (least hp M)) :
    CoordinateSupport.State (R := ZMod (p^r)) (CoordinateSupport.least M) :=
  CoordinateSupport.restrict _ x.val

theorem supportEmbedding_injective (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) : Function.Injective (supportEmbedding hp M) := by
  intro x y h
  apply Subtype.ext
  have hh := congrArg (CoordinateSupport.embed (CoordinateSupport.least M)) h
  simpa only [supportEmbedding, CoordinateSupport.embed_restrict _ _ (least_supported hp M _)] using hh

theorem supportEmbedding_transition (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (d : A)
    (x : State (p := p) (r := r) (least hp M)) :
    supportEmbedding hp M (transition hp M d x) =
      CoordinateSupport.transition M (CoordinateSupport.least M) d (supportEmbedding hp M x) := by
  unfold supportEmbedding CoordinateSupport.transition
  rw [CoordinateSupport.embed_restrict _ _ (least_supported hp M x)]
  rfl

@[simp] theorem supportEmbedding_initial (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) :
    supportEmbedding hp M (initial hp M) =
      CoordinateSupport.restrict (CoordinateSupport.least M) M.initial := rfl

theorem supportEmbedding_run (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (ds : List A)
    (x : State (p := p) (r := r) (least hp M)) :
    supportEmbedding hp M (run hp M ds x) =
      CoordinateSupport.runRestricted M (CoordinateSupport.least M) ds (supportEmbedding hp M x) := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih =>
    simp only [run, CoordinateSupport.runRestricted]
    rw [ih, supportEmbedding_transition]

end CoordinateIdeal
end KomorebiPadic
