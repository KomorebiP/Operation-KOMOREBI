module
public import MatrixCertificates

@[expose] public section

namespace Komorebi.Representation.Matrix
open Lean.Grind
universe u
variable {R : Type u} [Semiring R] {d t : Nat}

/- Actual image factors: scalar multiples, not unweighted free coordinates. -/
def PrincipalCoordinates (weights : Vec R t) (y : Vec R t) : Prop :=
  ∀ i, ∃ a : R, weights i * a = y i

def diagonal (ht : t ≤ d) (weights : Vec R t) : Mat R t d :=
  fun i j => if (Fin.castLE ht i) = j then weights i else 0

theorem diagonal_mv (ht : t ≤ d) (weights : Vec R t) (x : Vec R d) (i : Fin t) :
    mv (diagonal ht weights) x i = weights i * x (Fin.castLE ht i) := by
  have hh : (fun j => (if Fin.castLE ht i = j then weights i else (0 : R)) * x j) =
      (fun j => if Fin.castLE ht i = j then weights i * x j else 0) := by
    funext j; split <;> simp only [Semiring.zero_mul]
  change fsum d (fun j => (if Fin.castLE ht i = j then weights i else (0 : R)) * x j) = _
  rw [hh]
  exact fsum_indicator d (fun j => weights i * x j) (Fin.castLE ht i)

structure SmithData (R : Type u) (d t : Nat) where
  width : t ≤ d
  weights : Vec R t
  change : Mat R d d
  inverse : Mat R d d

def SmithValid (P : Mat R t d) (s : SmithData R d t) : Prop :=
  (∀ i j, mm s.change s.inverse i j = eye d i j) ∧
  (∀ i j, mm s.inverse s.change i j = eye d i j) ∧
  (∀ i j, mm P s.change i j = diagonal s.width s.weights i j)

instance decidableSmithValid [DecidableEq R] (P : Mat R t d) (s : SmithData R d t) :
    Decidable (SmithValid P s) := by
  unfold SmithValid
  infer_instance

theorem smith_image_iff (P : Mat R t d) (s : SmithData R d t) (hs : SmithValid P s)
    (y : Vec R t) :
    (∃ x : Vec R d, mv P x = y) ↔ PrincipalCoordinates s.weights y := by
  have hid : mm s.change s.inverse = eye d :=
    funext (fun i => funext (hs.1 i))
  have hdiag : mm P s.change = diagonal s.width s.weights :=
    funext (fun i => funext (hs.2.2 i))
  constructor
  · intro ⟨x, hx⟩ i
    let z := mv s.inverse x
    have hback : mv s.change z = x := by
      change mv s.change (mv s.inverse x) = x
      rw [← mv_mm, hid, mv_eye]
    refine ⟨z (Fin.castLE s.width i), ?_⟩
    rw [← diagonal_mv s.width s.weights z i, ← hdiag, mv_mm, hback, hx]
  · intro hy
    let a : Vec R t := fun i => Classical.choose (hy i)
    let z : Vec R d := fun j => if h : j.val < t then a ⟨j.val, h⟩ else 0
    refine ⟨mv s.change z, ?_⟩
    rw [← mv_mm, hdiag]
    funext i
    rw [diagonal_mv]
    have hz : z (Fin.castLE s.width i) = a i := by
      simp only [z, Fin.val_castLE, i.isLt, dite_true]
    rw [hz]
    exact Classical.choose_spec (hy i)

def imageToPrincipal {k o l : Nat} (c : CertificateData R d t k o l)
    (s : SmithData R d t) (hs : SmithValid c.encoding s) (x : EncodedImage c) :
    { y : Vec R t // PrincipalCoordinates s.weights y } :=
  ⟨x.val, (smith_image_iff c.encoding s hs x.val).mp x.property⟩

def principalToImage {k o l : Nat} (c : CertificateData R d t k o l)
    (s : SmithData R d t) (hs : SmithValid c.encoding s)
    (x : { y : Vec R t // PrincipalCoordinates s.weights y }) : EncodedImage c :=
  ⟨x.val, (smith_image_iff c.encoding s hs x.val).mpr x.property⟩

theorem smith_image_roundtrip {k o l : Nat} (c : CertificateData R d t k o l)
    (s : SmithData R d t) (hs : SmithValid c.encoding s) (x : EncodedImage c) :
    principalToImage c s hs (imageToPrincipal c s hs x) = x := by
  apply Subtype.ext; rfl

theorem smith_principal_roundtrip {k o l : Nat} (c : CertificateData R d t k o l)
    (s : SmithData R d t) (hs : SmithValid c.encoding s)
    (x : { y : Vec R t // PrincipalCoordinates s.weights y }) :
    imageToPrincipal c s hs (principalToImage c s hs x) = x := by
  apply Subtype.ext; rfl

def checkSmith {m : Nat} [NeZero m] (P : Mat (Fin m) t d)
    (s : SmithData (Fin m) d t) : Bool := decide (SmithValid P s)

theorem checked_smith_image {m : Nat} [NeZero m] (P : Mat (Fin m) t d)
    (s : SmithData (Fin m) d t) (h : checkSmith P s = true) (y : Vec (Fin m) t) :
    (∃ x, mv P x = y) ↔ PrincipalCoordinates s.weights y :=
  smith_image_iff P s (of_decide_eq_true h) y

end Komorebi.Representation.Matrix
