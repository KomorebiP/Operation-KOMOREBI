module
public import MatrixCore
public import FiniteCertificates

@[expose] public section

namespace Komorebi.Representation.Matrix
open Lean.Grind
universe u

/- A finite certificate describes matrices, not a table of all possible states. -/
structure CertificateData (R : Type u) (d t k o l : Nat) where
  actions : Fin k → Mat R d d
  observations : Mat R o d
  encoding : Mat R t d
  transitions : Fin k → Mat R t t
  decoder : Mat R o t
  tests : Fin l → List (Fin k) × Fin o
  combinations : Mat R t l

variable {R : Type u} [Semiring R] {d t k o l : Nat}

def testRows (c : CertificateData R d t k o l) : Mat R l d :=
  fun a => wordRow c.actions c.observations (c.tests a).1 (c.tests a).2

def sourceSystem (c : CertificateData R d t k o l) :=
  linearSystem c.actions c.observations

def targetSystem (c : CertificateData R d t k o l) :=
  linearSystem c.transitions c.decoder

def Valid (c : CertificateData R d t k o l) : Prop :=
  (∀ a i j, mm c.encoding (c.actions a) i j = mm (c.transitions a) c.encoding i j) ∧
  (∀ j i, c.observations j i = mm c.decoder c.encoding j i) ∧
  (∀ i j, c.encoding i j = mm c.combinations (testRows c) i j)

instance decidableValid [DecidableEq R] (c : CertificateData R d t k o l) : Decidable (Valid c) := by
  unfold Valid
  infer_instance

def matrixTransport (c : CertificateData R d t k o l) (h : Valid c) :
    Transport (sourceSystem c) (targetSystem c) where
  encode := mv c.encoding
  step_ok := by
    intro a x
    change mv c.encoding (mv (c.actions a) x) = mv (c.transitions a) (mv c.encoding x)
    rw [← mv_mm, ← mv_mm]
    have heq : mm c.encoding (c.actions a) = mm (c.transitions a) c.encoding :=
      funext (fun i => funext (h.1 a i))
    rw [heq]
  observe_ok := by
    intro j x
    have heq : c.observations j = rm (c.decoder j) c.encoding :=
      funext (h.2.1 j)
    change dot (c.observations j) x = dot (c.decoder j) (mv c.encoding x)
    rw [heq, dot_rm]

theorem matrix_all_words (c : CertificateData R d t k o l) (h : Valid c)
    (x : Vec R d) (w : List (Fin k)) (j : Fin o) :
    behavior (sourceSystem c) x w j =
    behavior (targetSystem c) (mv c.encoding x) w j :=
  transport_behavior (matrixTransport c h) w j x

theorem matrix_behavior_exact (c : CertificateData R d t k o l) (h : Valid c)
    (x y : Vec R d) :
    ObsEq (sourceSystem c) x y ↔ mv c.encoding x = mv c.encoding y := by
  constructor
  · intro hb
    have ht : mv (testRows c) x = mv (testRows c) y := by
      funext a
      change dot (wordRow c.actions c.observations (c.tests a).1 (c.tests a).2) x =
        dot (wordRow c.actions c.observations (c.tests a).1 (c.tests a).2) y
      rw [wordRow_behavior, wordRow_behavior]
      exact hb (c.tests a).1 (c.tests a).2
    have hp : c.encoding = mm c.combinations (testRows c) :=
      funext (fun i => funext (h.2.2 i))
    rw [hp, mv_mm, mv_mm, ht]
  · exact transport_kernel_sound (matrixTransport c h)

abbrev EncodedImage (c : CertificateData R d t k o l) :=
  { y : Vec R t // ∃ x : Vec R d, mv c.encoding x = y }

def imageSystem (c : CertificateData R d t k o l) (h : Valid c) :
    System (EncodedImage c) (Fin k) (Fin o) R where
  step := fun a y => ⟨mv (c.transitions a) y.val, by
    obtain ⟨x, hx⟩ := y.property
    exact ⟨mv (c.actions a) x, ((matrixTransport c h).step_ok a x).trans
      (congrArg (mv (c.transitions a)) hx)⟩⟩
  observe := fun j y => dot (c.decoder j) y.val

def imageTransport (c : CertificateData R d t k o l) (h : Valid c) :
    Transport (sourceSystem c) (imageSystem c h) where
  encode := fun x => ⟨mv c.encoding x, ⟨x, rfl⟩⟩
  step_ok := by
    intro a x; apply Subtype.ext; exact (matrixTransport c h).step_ok a x
  observe_ok := (matrixTransport c h).observe_ok

theorem image_surjective (c : CertificateData R d t k o l) (h : Valid c) :
    ∀ y, ∃ x, (imageTransport c h).encode x = y := by
  intro y
  obtain ⟨x, hx⟩ := y.property
  exact ⟨x, Subtype.ext hx⟩

theorem image_encoding_exact (c : CertificateData R d t k o l) (h : Valid c)
    (x y : Vec R d) :
    ObsEq (sourceSystem c) x y ↔ (imageTransport c h).encode x = (imageTransport c h).encode y := by
  rw [matrix_behavior_exact c h]
  exact ⟨fun hxy => Subtype.ext hxy, fun hxy => congrArg Subtype.val hxy⟩

theorem image_separated (c : CertificateData R d t k o l) (h : Valid c) :
    ∀ y z : EncodedImage c, y ≠ z →
      ∃ w j, behavior (imageSystem c h) y w j ≠ behavior (imageSystem c h) z w j := by
  intro y z hne
  obtain ⟨x, rfl⟩ := image_surjective c h y
  obtain ⟨v, rfl⟩ := image_surjective c h z
  apply Classical.byContradiction
  intro hnone
  apply hne
  apply (image_encoding_exact c h x v).mp
  intro w j
  rw [transport_behavior (imageTransport c h), transport_behavior (imageTransport c h)]
  apply Classical.byContradiction
  intro hj
  exact hnone ⟨w, j, hj⟩

theorem image_minimal_semantic_encoding (c : CertificateData R d t k o l) (h : Valid c)
    {Z : Type u} (U : System Z (Fin k) (Fin o) R) (encode : Vec R d → Z)
    (hc : ∀ x w j, behavior (sourceSystem c) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage c → Z, ∀ y z, f y = f z → y = z := by
  exact ⟨semanticEmbedding (imageTransport c h) (image_surjective c h) encode,
    minimal_word_encoding_injective (imageTransport c h) (image_surjective c h)
      (image_separated c h) encode hc⟩

/- Concrete certificates are checked only over matrix/test indices, never over R^d. -/
def checkCertificate {m : Nat} [NeZero m]
    (c : CertificateData (Fin m) d t k o l) : Bool := decide (Valid c)

theorem checked_matrix_all_words {m : Nat} [NeZero m]
    (c : CertificateData (Fin m) d t k o l) (h : checkCertificate c = true)
    (x : Vec (Fin m) d) (w : List (Fin k)) (j : Fin o) :
    behavior (sourceSystem c) x w j = behavior (targetSystem c) (mv c.encoding x) w j :=
  matrix_all_words c (of_decide_eq_true h) x w j

theorem checked_matrix_exact {m : Nat} [NeZero m]
    (c : CertificateData (Fin m) d t k o l) (h : checkCertificate c = true)
    (x y : Vec (Fin m) d) :
    ObsEq (sourceSystem c) x y ↔ mv c.encoding x = mv c.encoding y :=
  matrix_behavior_exact c (of_decide_eq_true h) x y

end Komorebi.Representation.Matrix
