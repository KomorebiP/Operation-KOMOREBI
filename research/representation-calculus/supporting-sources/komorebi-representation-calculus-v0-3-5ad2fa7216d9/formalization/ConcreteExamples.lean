import InvariantCertificates

namespace Komorebi.Representation.Fixtures
open Komorebi.Representation
set_option maxRecDepth 10000
set_option maxHeartbeats 2000000

def reduceFin (n : Nat) (h : 0 < n) (v : Nat) : Fin n := ⟨v % n, Nat.mod_lt _ h⟩

def shift64 (x : Fin 64) : Fin 64 :=
  reduceFin 64 (by decide)
    ((x.val % 4 + x.val / 4 % 4) % 4 + 4 * (x.val / 4 % 4) + 16 * (x.val / 16))

def swap64 (x : Fin 64) : Fin 64 :=
  reduceFin 64 (by decide) (x.val / 16 + 4 * (x.val / 4 % 4) + 16 * (x.val % 4))

def shift16 (x : Fin 16) : Fin 16 :=
  reduceFin 16 (by decide) ((x.val % 4 + x.val / 4) % 4 + 4 * (x.val / 4))

def oldSystem : System (Fin 64) (Fin 1) (Fin 1) (Fin 4) where
  step := fun _ => shift64
  observe := fun _ x => reduceFin 4 (by decide) x.val

def compressedOld : System (Fin 16) (Fin 1) (Fin 1) (Fin 4) where
  step := fun _ => shift16
  observe := fun _ x => reduceFin 4 (by decide) x.val

def oldEncode (x : Fin 64) : Fin 16 := reduceFin 16 (by decide) x.val

theorem old_local_check : checkLocal oldSystem compressedOld oldEncode = true := by decide

def oldTransport : Transport oldSystem compressedOld :=
  checkedTransport oldSystem compressedOld oldEncode old_local_check

theorem old_all_words (x : Fin 64) (w : List (Fin 1)) (j : Fin 1) :
    behavior oldSystem x w j = behavior compressedOld (oldEncode x) w j :=
  transport_behavior oldTransport w j x

def oldWitness (x y : Fin 16) : List (Fin 1) :=
  if x.val % 4 = y.val % 4 then [0] else []

theorem old_witness_check : ∀ x y : Fin 16, x ≠ y →
    behavior compressedOld x (oldWitness x y) 0 ≠
    behavior compressedOld y (oldWitness x y) 0 := by decide

theorem old_separation (x y : Fin 16) (h : x ≠ y) :
    ∃ w j, behavior compressedOld x w j ≠ behavior compressedOld y w j :=
  ⟨oldWitness x y,0,old_witness_check x y h⟩

theorem old_exact_quotient (x y : Fin 64) :
    ObsEq oldSystem x y ↔ oldEncode x = oldEncode y :=
  separated_encoding_exact oldTransport old_separation x y

def enlargedSystem : System (Fin 64) (Fin 2) (Fin 1) (Fin 4) where
  step := fun a => if a.val = 0 then shift64 else swap64
  observe := fun _ x => reduceFin 4 (by decide) x.val

def enlargedWitness (x y : Fin 64) : List (Fin 2) :=
  if x.val % 4 ≠ y.val % 4 then []
  else if x.val / 4 % 4 ≠ y.val / 4 % 4 then [0] else [1]

theorem enlarged_witness_check : ∀ x y : Fin 64, x ≠ y →
    behavior enlargedSystem x (enlargedWitness x y) 0 ≠
    behavior enlargedSystem y (enlargedWitness x y) 0 := by decide

theorem enlarged_exact (x y : Fin 64) : ObsEq enlargedSystem x y ↔ x = y := by
  constructor
  · intro h
    apply Classical.byContradiction
    intro hn
    exact enlarged_witness_check x y hn (h (enlargedWitness x y) 0)
  · intro h; rw [h]; exact obsEq_refl _ _

-- No possible target transition tables can repair this stale encoder.
theorem old_encoder_impossible_after_profile_change
    (T : System (Fin 16) (Fin 2) (Fin 1) (Fin 4))
    (q : Transport enlargedSystem T) (hq : q.encode = oldEncode) : False := by
  have same : q.encode 0 = q.encode 16 := by rw [hq]; rfl
  have h := transport_kernel_sound q same [1] 0
  have hne : behavior enlargedSystem (0 : Fin 64) [1] 0 ≠
      behavior enlargedSystem (16 : Fin 64) [1] 0 := by decide
  exact hne h

-- At precision four, observe 2x and discard exactly parity-equivalent inputs.
def torsionSource : System (Fin 4) (Fin 1) (Fin 1) (Fin 4) where
  step := fun _ x => x
  observe := fun _ x => reduceFin 4 (by decide) (2*x.val)

def torsionTarget : System (Fin 2) (Fin 1) (Fin 1) (Fin 4) where
  step := fun _ x => x
  observe := fun _ x => reduceFin 4 (by decide) (2*x.val)

def torsionEncode (x : Fin 4) : Fin 2 := reduceFin 2 (by decide) x.val

theorem torsion_local_check : checkLocal torsionSource torsionTarget torsionEncode = true := by decide

def torsionTransport : Transport torsionSource torsionTarget :=
  checkedTransport torsionSource torsionTarget torsionEncode torsion_local_check

theorem torsion_exact (x y : Fin 4) : ObsEq torsionSource x y ↔ torsionEncode x = torsionEncode y := by
  apply separated_encoding_exact torsionTransport
  intro a b h
  refine ⟨[],0,?_⟩
  have hh : ∀ a b : Fin 2, a ≠ b →
      behavior torsionTarget a [] 0 ≠ behavior torsionTarget b [] 0 := by decide
  exact hh a b h

-- Reducing the original observation to modulus two makes it identically zero.
def lowerSource : System (Fin 2) (Fin 1) (Fin 1) (Fin 2) where
  step := fun _ x => x
  observe := fun _ _ => 0

theorem lower_all_equivalent (x y : Fin 2) : ObsEq lowerSource x y := by
  intro w j
  rfl

end Komorebi.Representation.Fixtures
