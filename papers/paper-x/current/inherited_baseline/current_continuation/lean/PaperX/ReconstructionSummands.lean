import PaperX.MonodromyReconstruction
import PaperX.WeilMorphisms

/-! Reconstruction commutes with actual finite-copy actions and split maps. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ReconstructionSummands
open PaperX.WeilData PaperX.WeilCopies PaperX.WeilMorphisms
open PaperX.MonodromyReconstruction PaperX.CarrierSummands
variable {K G : Type*} [Field K] [CharZero K] [Group G] {ν : G →* Kˣ}
variable {V W : Type*} [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

theorem reconstruct_intertwines {D : Datum ν V} {E : Datum ν W}
    (f : Hom D E) (t : TwistedCocycle ν) (g : G) (x : V) :
    f.map (reconstruct D t g x) = reconstruct E t g (f.map x) := by
  have hc := PaperX.NilpotentExponential.expN_intertwines D.nilpotent E.nilpotent f.map
    (LinearMap.ext fun x => (f.monodromy_eq x).symm) (t.value g)
  change f.map (unipotent D (t.value g) (D.r g x)) = _
  exact (LinearMap.congr_fun hc (D.r g x)).symm.trans
    (congrArg (unipotent E (t.value g)) (f.group_eq g x))

def twistHom {D : Datum ν V} {E : Datum ν W} (f : Hom D E) (t : TwistedCocycle ν) :
    Hom (twist D t) (twist E t) where
  map := f.map
  group_eq := reconstruct_intertwines f t
  monodromy_eq := f.monodromy_eq

variable {I : Type*} [Fintype I] {X : I → Type*}
variable [∀ i, AddCommGroup (X i)] [∀ i, Module K (X i)]

omit [CharZero K] in
def component (m : I → ℕ) (i : I) (k : Fin (m i)) : Copies X m →ₗ[K] X i where
  toFun x := x i k
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem unipotent_copies (D : ∀ i, Datum ν (X i)) (m : I → ℕ) (a : K)
    (x : Copies X m) (i : I) (k : Fin (m i)) :
    unipotent (copiesDatum D m) a x i k = unipotent (D i) a (x i k) := by
  have h := PaperX.NilpotentExponential.expN_intertwines
    (copiesDatum D m).nilpotent (D i).nilpotent (component m i k) (by rfl) a
  exact (LinearMap.congr_fun h x).symm

theorem reconstruct_copies (D : ∀ i, Datum ν (X i)) (m : I → ℕ)
    (t : TwistedCocycle ν) :
    reconstruct (copiesDatum D m) t = copiesRep (fun i => reconstruct (D i) t) m := by
  ext g x i k
  exact unipotent_copies D m (t.value g) _ i k

theorem twist_copies (D : ∀ i, Datum ν (X i)) (m : I → ℕ)
    (t : TwistedCocycle ν) :
    twist (copiesDatum D m) t = copiesDatum (fun i => twist (D i) t) m :=
  datum_ext (reconstruct_copies D m t) rfl

theorem reconstructed_inclusion (D : ∀ i, Datum ν (X i)) (t : TwistedCocycle ν)
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (g : G) (x : Copies X m) :
    inclusion (R := K) h (reconstruct (copiesDatum D m) t g x) =
      reconstruct (copiesDatum D c) t g (inclusion (R := K) h x) :=
  reconstruct_intertwines (inclusionHom D h) t g x

theorem reconstructed_retraction (D : ∀ i, Datum ν (X i)) (t : TwistedCocycle ν)
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (g : G) (x : Copies X c) :
    retraction (R := K) h (reconstruct (copiesDatum D c) t g x) =
      reconstruct (copiesDatum D m) t g (retraction (R := K) h x) :=
  reconstruct_intertwines (retractionHom D h) t g x

theorem reconstructed_projector (D : ∀ i, Datum ν (X i)) (t : TwistedCocycle ν)
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (g : G) :
    (projector (R := K) (V := X) h).comp (reconstruct (copiesDatum D c) t g) =
      (reconstruct (copiesDatum D c) t g).comp (projector h) := by
  rw [reconstruct_copies]
  exact projector_equivariant (fun i => reconstruct (D i) t) h g

end PaperX.ReconstructionSummands
