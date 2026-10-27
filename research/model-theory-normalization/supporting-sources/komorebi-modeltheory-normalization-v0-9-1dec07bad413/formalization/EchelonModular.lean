module
public import EchelonInsert
public import Mathlib.Data.ZMod.Basic
public import Mathlib.LinearAlgebra.Finsupp.LinearCombination

@[expose] public section
namespace Komorebi.Echelon
open scoped BigOperators

def diagonal (m : ℤ) (hm : 0<m) : (n : Nat) → Basis n
  | 0 => .nil
  | n+1 => .cons m hm 0 (diagonal m hm n)

theorem synth_diagonal (m : ℤ) (hm : 0<m) (n : Nat) (c : Fin n → ℤ) :
    synth (diagonal m hm n) c = m • c := by
  induction n with
  | zero => exact Subsingleton.elim _ _
  | succ n ih =>
      ext i; refine Fin.cases ?_ (fun j => ?_) i
      · simp [diagonal,synth,mul_comm]
      · simp [diagonal,synth,ih,tailV]

def extend {n : Nat} (B : Basis n) : List (Fin n → ℤ) → Basis n
  | [] => B
  | v::vs => extend (insert B v) vs

def rowSpan (R : Type) {M : Type} [Semiring R] [AddCommMonoid M] [Module R M]
    (L : List M) : Submodule R M := Submodule.span R {v | v ∈ L}

theorem rowSpan_cons (R : Type) {M : Type} [Semiring R] [AddCommMonoid M] [Module R M]
    (v : M) (L : List M) :
    rowSpan R (v::L) = Submodule.span R {v} ⊔ rowSpan R L := by
  have hs : {x | x ∈ v::L} = Insert.insert v {x | x∈L} := by ext x; simp
  simp only [rowSpan,hs,Submodule.span_insert]

theorem lattice_extend {n : Nat} (B : Basis n) (L : List (Fin n → ℤ)) :
    lattice (extend B L) = lattice B ⊔ rowSpan ℤ L := by
  induction L generalizing B with
  | nil => simp [extend,rowSpan]
  | cons v L ih => rw [extend,ih,lattice_insert,rowSpan_cons,sup_assoc]

def reduce (m : Nat) {n : Nat} (x : Fin n → ℤ) : Fin n → ZMod m := fun i => x i

def lift (m : Nat) {n : Nat} (x : Fin n → ZMod m) : Fin n → ℤ := fun i => (x i).val

@[simp] theorem reduce_lift (m : Nat) [NeZero m] {n : Nat} (x : Fin n → ZMod m) :
    reduce m (lift m x) = x := by ext i; simp [reduce,lift]

@[simp] theorem reduce_zero (m : Nat) {n : Nat} : reduce m (0 : Fin n → ℤ) = 0 := by
  ext i; simp [reduce]

@[simp] theorem reduce_add (m : Nat) {n : Nat} (x y : Fin n → ℤ) :
    reduce m (x+y) = reduce m x+reduce m y := by ext i; simp [reduce]

@[simp] theorem reduce_sub (m : Nat) {n : Nat} (x y : Fin n → ℤ) :
    reduce m (x-y) = reduce m x-reduce m y := by ext i; simp [reduce]

@[simp] theorem reduce_smul (m : Nat) {n : Nat} (a : ℤ) (x : Fin n → ℤ) :
    reduce m (a • x) = (a : ZMod m) • reduce m x := by ext i; simp [reduce]

theorem diagonal_kernel (m : Nat) [NeZero m] {n : Nat} (x : Fin n → ℤ) :
    Represents (diagonal (m:ℤ) (by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne m)) n) x
      ↔ reduce m x=0 := by
  simp only [Represents,synth_diagonal]
  constructor
  · rintro ⟨c,rfl⟩; ext i; simp [reduce]
  · intro h
    have hd : ∀i,(m:ℤ) ∣ x i := by
      intro i
      exact (ZMod.intCast_zmod_eq_zero_iff_dvd (x i) m).mp (congrFun h i)
    refine ⟨fun i => x i / (m:ℤ),?_⟩
    ext i
    change (m:ℤ)*(x i/(m:ℤ))=x i
    rw [mul_comm]
    exact Int.ediv_mul_cancel (hd i)

/-- Integer preimage lattice for the exact residue-row module. -/
def build (m : Nat) [NeZero m] {n : Nat} (rows : List (Fin n → ZMod m)) : Basis n :=
  extend (diagonal (m:ℤ) (by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne m)) n)
    (rows.map (lift m))

theorem reduce_span (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) (x : Fin n → ℤ)
    (hx : x ∈ rowSpan ℤ (rows.map (lift m))) : reduce m x ∈ rowSpan (ZMod m) rows := by
  induction hx using Submodule.span_induction with
  | mem v hv =>
      obtain ⟨u,hu,rfl⟩ := List.mem_map.mp hv
      rw [reduce_lift]
      exact Submodule.subset_span hu
  | zero => simp
  | add x y _ _ ihx ihy => simpa using (rowSpan (ZMod m) rows).add_mem ihx ihy
  | smul a x _ ih =>
      rw [reduce_smul]
      exact (rowSpan (ZMod m) rows).smul_mem (a : ZMod m) ih

theorem lift_span (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) (y : Fin n → ZMod m)
    (hy : y ∈ rowSpan (ZMod m) rows) :
    ∃ x ∈ rowSpan ℤ (rows.map (lift m)), reduce m x=y := by
  induction hy using Submodule.span_induction with
  | mem v hv =>
      exact ⟨lift m v,Submodule.subset_span (List.mem_map.mpr ⟨v,hv,rfl⟩),reduce_lift m v⟩
  | zero => exact ⟨0,(rowSpan ℤ _).zero_mem,reduce_zero m⟩
  | add x y _ _ ihx ihy =>
      obtain ⟨u,hu,he⟩ := ihx
      obtain ⟨v,hv,hf⟩ := ihy
      exact ⟨u+v,(rowSpan ℤ _).add_mem hu hv,by simp [he,hf]⟩
  | smul a x _ ih =>
      obtain ⟨u,hu,he⟩ := ih
      refine ⟨(a.val:ℤ) • u,(rowSpan ℤ _).smul_mem (a.val:ℤ) hu,?_⟩
      rw [reduce_smul,he]
      simp

/-- No saturation is introduced: membership is in the original residue module. -/
theorem build_correct (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) (x : Fin n → ℤ) :
    Represents (build m rows) x ↔ reduce m x ∈ rowSpan (ZMod m) rows := by
  change x ∈ lattice (build m rows) ↔ _
  rw [build,lattice_extend,Submodule.mem_sup]
  constructor
  · rintro ⟨a,ha,b,hb,rfl⟩
    have hz := (diagonal_kernel m a).mp ha
    simpa [hz] using reduce_span m rows b hb
  · intro hx
    obtain ⟨b,hb,he⟩ := lift_span m rows (reduce m x) hx
    refine ⟨x-b, (diagonal_kernel m (x-b)).mpr ?_, b,hb,?_⟩
    · simp [he]
    · abel

/-- Insertions preserve the exact preimage contract for any residue submodule. -/
theorem insert_preimage (m : Nat) [NeZero m] {n : Nat}
    (B : Basis n) (S : Submodule (ZMod m) (Fin n → ZMod m))
    (hB : ∀x, Represents B x ↔ reduce m x ∈ S)
    (v : Fin n → ZMod m) (x : Fin n → ℤ) :
    Represents (insert B (lift m v)) x ↔
      reduce m x ∈ S ⊔ Submodule.span (ZMod m) {v} := by
  rw [insert_correct,Submodule.mem_sup]
  constructor
  · rintro ⟨c,hc⟩
    have hm := (hB _).mp hc
    rw [reduce_sub,reduce_smul,reduce_lift] at hm
    exact ⟨reduce m x-(c:ZMod m) • v,hm,(c:ZMod m) • v,
      Submodule.mem_span_singleton.mpr ⟨(c:ZMod m),rfl⟩,by abel⟩
  · rintro ⟨a,ha,b,hb,he⟩
    obtain ⟨c,rfl⟩ := Submodule.mem_span_singleton.mp hb
    refine ⟨(c.val:ℤ),(hB _).mpr ?_⟩
    rw [reduce_sub,reduce_smul,reduce_lift]
    have hcast : ((c.val:ℤ) : ZMod m)=c := by simp
    rw [hcast,← he]
    simpa using ha

/-- Exact, non-enumerative residue membership. -/
def member (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) (v : Fin n → ZMod m) : Bool :=
  (coordinates (build m rows) (lift m v)).isSome

theorem member_correct (m : Nat) [NeZero m] {n : Nat}
    (rows : List (Fin n → ZMod m)) (v : Fin n → ZMod m) :
    member m rows v=true ↔ v ∈ rowSpan (ZMod m) rows := by
  simp only [member,Option.isSome_iff_exists,coordinates_correct,build_correct,reduce_lift]

end Komorebi.Echelon
