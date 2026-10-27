import Std
namespace H12.GerbeDescent

/- Exact integer exterior-cohomology certificate. The geometric Hodge/gerbe
interpretation is proved in PROOF.md, not encoded as a project axiom. -/
structure Form where
  c0 : Int
  c1 : Int
  c2 : Int
  c3 : Int
  c4 : Int
  c5 : Int
  c6 : Int
  c7 : Int
  c8 : Int
  c9 : Int
  c10 : Int
  c11 : Int
  c12 : Int
  c13 : Int
  c14 : Int
  c15 : Int
  c16 : Int
  c17 : Int
  c18 : Int
  c19 : Int
  deriving DecidableEq, Repr

def zero : Form := ⟨0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0⟩

def pull (v : Form) : Form :=
  ⟨(1) * v.c19,
   (16) * v.c13 + (4) * v.c14 + (8) * v.c15 + (4) * v.c16 + (1) * v.c17 + (2) * v.c18,
   (-4) * v.c7 + (-1) * v.c8 + (-2) * v.c9 + (-8) * v.c13 + (-2) * v.c14 + (-4) * v.c15,
   (-60) * v.c13 + (-15) * v.c14 + (-30) * v.c15 + (-16) * v.c16 + (-4) * v.c17 + (-8) * v.c18 + (-1) * v.c19,
   (-4) * v.c15 + (-1) * v.c18,
   (1) * v.c9 + (2) * v.c15 + (1) * v.c19,
   (15) * v.c15 + (4) * v.c18,
   (-16) * v.c2 + (-4) * v.c3 + (-4) * v.c5 + (-1) * v.c6 + (-8) * v.c11 + (-2) * v.c12 + (16) * v.c13 + (4) * v.c14 + (8) * v.c15 + (4) * v.c16 + (1) * v.c17 + (2) * v.c18,
   (4) * v.c11 + (1) * v.c12 + (-4) * v.c15 + (-1) * v.c18,
   (-60) * v.c2 + (-15) * v.c3 + (-16) * v.c5 + (-4) * v.c6 + (1) * v.c9 + (-32) * v.c11 + (-8) * v.c12 + (60) * v.c13 + (15) * v.c14 + (32) * v.c15 + (16) * v.c16 + (4) * v.c17 + (8) * v.c18 + (1) * v.c19,
   (60) * v.c13 + (16) * v.c14 + (32) * v.c15 + (15) * v.c16 + (4) * v.c17 + (8) * v.c18 + (-1) * v.c19,
   (-15) * v.c7 + (-4) * v.c8 + (-8) * v.c9 + (-30) * v.c13 + (-8) * v.c14 + (-16) * v.c15,
   (-225) * v.c13 + (-60) * v.c14 + (-120) * v.c15 + (-60) * v.c16 + (-16) * v.c17 + (-32) * v.c18,
   (4) * v.c1 + (8) * v.c2 + (1) * v.c4 + (2) * v.c5 + (-4) * v.c7 + (-1) * v.c8 + (-2) * v.c9 + (2) * v.c10 + (4) * v.c11 + (-8) * v.c13 + (-2) * v.c14 + (-4) * v.c15,
   (-1) * v.c10 + (-2) * v.c11 + (1) * v.c14 + (2) * v.c15 + (-1) * v.c16 + (-1) * v.c19,
   (15) * v.c1 + (30) * v.c2 + (4) * v.c4 + (8) * v.c5 + (-15) * v.c7 + (-4) * v.c8 + (-8) * v.c9 + (8) * v.c10 + (16) * v.c11 + (-30) * v.c13 + (-8) * v.c14 + (-16) * v.c15,
   (60) * v.c2 + (16) * v.c3 + (15) * v.c5 + (4) * v.c6 + (1) * v.c9 + (30) * v.c11 + (8) * v.c12 + (-60) * v.c13 + (-16) * v.c14 + (-30) * v.c15 + (-15) * v.c16 + (-4) * v.c17 + (-8) * v.c18 + (1) * v.c19,
   (-15) * v.c11 + (-4) * v.c12 + (15) * v.c15 + (4) * v.c18,
   (225) * v.c2 + (60) * v.c3 + (60) * v.c5 + (16) * v.c6 + (120) * v.c11 + (32) * v.c12 + (-225) * v.c13 + (-60) * v.c14 + (-120) * v.c15 + (-60) * v.c16 + (-16) * v.c17 + (-32) * v.c18,
   (-1) * v.c0 + (-1) * v.c3 + (1) * v.c5 + (-1) * v.c9 + (-1) * v.c10 + (1) * v.c14 + (-1) * v.c16 + (-1) * v.c19⟩

def normal (A B : Int) : Form :=
  ⟨(1) * A + (0) * B, (0) * A + (0) * B, (0) * A + (0) * B, (0) * A + (1) * B, (0) * A + (0) * B, (0) * A + (-1) * B, (0) * A + (0) * B, (0) * A + (0) * B, (0) * A + (0) * B, (-1) * A + (-1) * B, (0) * A + (1) * B, (0) * A + (0) * B, (0) * A + (0) * B, (0) * A + (0) * B, (1) * A + (1) * B, (0) * A + (0) * B, (-1) * A + (-1) * B, (0) * A + (0) * B, (0) * A + (0) * B, (1) * A + (0) * B⟩

def hodgeReal (v : Form) : Int := (1) * v.c0 + (1) * v.c3 + (-1) * v.c5 + (1) * v.c10 + (-1) * v.c19
def hodgeImag (v : Form) : Int := (1) * v.c3 + (-1) * v.c5 + (1) * v.c9 + (1) * v.c10 + (-1) * v.c14 + (1) * v.c16

theorem normal_fixed (A B : Int) : pull (normal A B) = normal A B := by
  simp [pull, normal, Form.mk.injEq]
  omega

theorem certificate_1 (v : Form) :
    270 * (v.c1 - ((0)*v.c0 + (0)*v.c3)) = (-240) * ((pull v).c1 - v.c1) + (-60) * ((pull v).c2 - v.c2) + (12) * ((pull v).c4 - v.c4) + (2) * ((pull v).c6 - v.c6) + (30) * ((pull v).c7 - v.c7) + (24) * ((pull v).c9 - v.c9) + (45) * ((pull v).c10 - v.c10) + (12) * ((pull v).c11 - v.c11) + (-4) * ((pull v).c12 - v.c12) + (-60) * ((pull v).c13 - v.c13) + (-21) * ((pull v).c14 - v.c14) + (18) * ((pull v).c15 - v.c15) + (2) * ((pull v).c17 - v.c17) + (8) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_2 (v : Form) :
    270 * (v.c2 - ((0)*v.c0 + (0)*v.c3)) = (15) * ((pull v).c1 - v.c1) + (-210) * ((pull v).c2 - v.c2) + (12) * ((pull v).c5 - v.c5) + (1) * ((pull v).c6 - v.c6) + (15) * ((pull v).c7 - v.c7) + (-6) * ((pull v).c8 - v.c8) + (-12) * ((pull v).c9 - v.c9) + (12) * ((pull v).c10 - v.c10) + (54) * ((pull v).c11 - v.c11) + (4) * ((pull v).c12 - v.c12) + (60) * ((pull v).c13 - v.c13) + (-12) * ((pull v).c14 - v.c14) + (-15) * ((pull v).c15 - v.c15) + (-2) * ((pull v).c17 - v.c17) + (-2) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_4 (v : Form) :
    90 * (v.c4 - ((0)*v.c0 + (0)*v.c3)) = (30) * ((pull v).c1 - v.c1) + (-90) * ((pull v).c2 - v.c2) + (-60) * ((pull v).c3 - v.c3) + (-92) * ((pull v).c4 - v.c4) + (-32) * ((pull v).c5 - v.c5) + (-13) * ((pull v).c6 - v.c6) + (45) * ((pull v).c7 - v.c7) + (16) * ((pull v).c8 - v.c8) + (-32) * ((pull v).c9 - v.c9) + (-32) * ((pull v).c10 - v.c10) + (19) * ((pull v).c11 - v.c11) + (10) * ((pull v).c12 - v.c12) + (150) * ((pull v).c13 - v.c13) + (28) * ((pull v).c14 - v.c14) + (-38) * ((pull v).c15 - v.c15) + (-5) * ((pull v).c17 - v.c17) + (-6) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_5 (v : Form) :
    90 * (v.c5 - ((0)*v.c0 + (-1)*v.c3)) = (60) * ((pull v).c1 - v.c1) + (225) * ((pull v).c2 - v.c2) + (-90) * ((pull v).c3 - v.c3) + (8) * ((pull v).c4 - v.c4) + (-46) * ((pull v).c5 - v.c5) + (23) * ((pull v).c8 - v.c8) + (-28) * ((pull v).c9 - v.c9) + (-76) * ((pull v).c10 - v.c10) + (-64) * ((pull v).c11 - v.c11) + (7) * ((pull v).c12 - v.c12) + (120) * ((pull v).c13 - v.c13) + (92) * ((pull v).c14 - v.c14) + (-28) * ((pull v).c15 - v.c15) + (4) * ((pull v).c17 - v.c17) + (-7) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_6 (v : Form) :
    18 * (v.c6 - ((0)*v.c0 + (0)*v.c3)) = (-30) * ((pull v).c1 - v.c1) + (60) * ((pull v).c2 - v.c2) + (45) * ((pull v).c3 - v.c3) + (24) * ((pull v).c5 - v.c5) + (-8) * ((pull v).c6 - v.c6) + (-30) * ((pull v).c7 - v.c7) + (-12) * ((pull v).c8 - v.c8) + (21) * ((pull v).c9 - v.c9) + (24) * ((pull v).c10 - v.c10) + (-12) * ((pull v).c11 - v.c11) + (-8) * ((pull v).c12 - v.c12) + (-120) * ((pull v).c13 - v.c13) + (-24) * ((pull v).c14 - v.c14) + (30) * ((pull v).c15 - v.c15) + (4) * ((pull v).c17 - v.c17) + (4) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_7 (v : Form) :
    270 * (v.c7 - ((0)*v.c0 + (0)*v.c3)) = (-30) * ((pull v).c1 - v.c1) + (60) * ((pull v).c2 - v.c2) + (45) * ((pull v).c3 - v.c3) + (-24) * ((pull v).c5 - v.c5) + (-2) * ((pull v).c6 - v.c6) + (-210) * ((pull v).c7 - v.c7) + (12) * ((pull v).c8 - v.c8) + (69) * ((pull v).c9 - v.c9) + (21) * ((pull v).c10 - v.c10) + (-18) * ((pull v).c11 - v.c11) + (-8) * ((pull v).c12 - v.c12) + (-120) * ((pull v).c13 - v.c13) + (-21) * ((pull v).c14 - v.c14) + (30) * ((pull v).c15 - v.c15) + (4) * ((pull v).c17 - v.c17) + (4) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_8 (v : Form) :
    90 * (v.c8 - ((0)*v.c0 + (0)*v.c3)) = (-45) * ((pull v).c1 - v.c1) + (-150) * ((pull v).c2 - v.c2) + (-16) * ((pull v).c4 - v.c4) + (-28) * ((pull v).c5 - v.c5) + (5) * ((pull v).c6 - v.c6) + (75) * ((pull v).c7 - v.c7) + (-76) * ((pull v).c8 - v.c8) + (-4) * ((pull v).c9 - v.c9) + (32) * ((pull v).c10 - v.c10) + (38) * ((pull v).c11 - v.c11) + (6) * ((pull v).c12 - v.c12) + (60) * ((pull v).c13 - v.c13) + (-64) * ((pull v).c14 - v.c14) + (-19) * ((pull v).c15 - v.c15) + (-18) * ((pull v).c17 - v.c17) + (4) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_9 (v : Form) :
    90 * (v.c9 - ((-1)*v.c0 + (-1)*v.c3)) = (-90) * ((pull v).c0 - v.c0) + (105) * ((pull v).c2 - v.c2) + (-120) * ((pull v).c3 - v.c3) + (-8) * ((pull v).c4 - v.c4) + (28) * ((pull v).c5 - v.c5) + (-4) * ((pull v).c6 - v.c6) + (60) * ((pull v).c7 - v.c7) + (31) * ((pull v).c8 - v.c8) + (-74) * ((pull v).c9 - v.c9) + (-92) * ((pull v).c10 - v.c10) + (-32) * ((pull v).c11 - v.c11) + (7) * ((pull v).c12 - v.c12) + (120) * ((pull v).c13 - v.c13) + (76) * ((pull v).c14 - v.c14) + (-32) * ((pull v).c15 - v.c15) + (4) * ((pull v).c17 - v.c17) + (-15) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_10 (v : Form) :
    90 * (v.c10 - ((0)*v.c0 + (1)*v.c3)) = (60) * ((pull v).c1 - v.c1) + (90) * ((pull v).c3 - v.c3) + (23) * ((pull v).c4 - v.c4) + (14) * ((pull v).c5 - v.c5) + (-7) * ((pull v).c8 - v.c8) + (32) * ((pull v).c9 - v.c9) + (-16) * ((pull v).c10 - v.c10) + (-4) * ((pull v).c11 - v.c11) + (-23) * ((pull v).c12 - v.c12) + (-105) * ((pull v).c13 - v.c13) + (-28) * ((pull v).c14 - v.c14) + (32) * ((pull v).c15 - v.c15) + (4) * ((pull v).c17 - v.c17) + (8) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_11 (v : Form) :
    90 * (v.c11 - ((0)*v.c0 + (0)*v.c3)) = (60) * ((pull v).c2 - v.c2) + (15) * ((pull v).c3 - v.c3) + (4) * ((pull v).c4 - v.c4) + (16) * ((pull v).c5 - v.c5) + (2) * ((pull v).c6 - v.c6) + (-30) * ((pull v).c7 - v.c7) + (-8) * ((pull v).c8 - v.c8) + (7) * ((pull v).c9 - v.c9) + (31) * ((pull v).c10 - v.c10) + (-14) * ((pull v).c11 - v.c11) + (4) * ((pull v).c12 - v.c12) + (-60) * ((pull v).c13 - v.c13) + (-23) * ((pull v).c14 - v.c14) + (16) * ((pull v).c15 - v.c15) + (-2) * ((pull v).c17 - v.c17) := by
  cases v
  simp only [pull]
  omega

theorem certificate_12 (v : Form) :
    18 * (v.c12 - ((0)*v.c0 + (0)*v.c3)) = (-15) * ((pull v).c1 - v.c1) + (-60) * ((pull v).c2 - v.c2) + (-6) * ((pull v).c4 - v.c4) + (-12) * ((pull v).c5 - v.c5) + (2) * ((pull v).c6 - v.c6) + (30) * ((pull v).c7 - v.c7) + (6) * ((pull v).c8 - v.c8) + (-12) * ((pull v).c10 - v.c10) + (15) * ((pull v).c11 - v.c11) + (-4) * ((pull v).c12 - v.c12) + (30) * ((pull v).c13 - v.c13) + (-9) * ((pull v).c15 - v.c15) + (-1) * ((pull v).c17 - v.c17) + (2) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_13 (v : Form) :
    270 * (v.c13 - ((0)*v.c0 + (0)*v.c3)) = (-15) * ((pull v).c1 - v.c1) + (-60) * ((pull v).c2 - v.c2) + (6) * ((pull v).c4 - v.c4) + (12) * ((pull v).c5 - v.c5) + (2) * ((pull v).c6 - v.c6) + (30) * ((pull v).c7 - v.c7) + (-6) * ((pull v).c8 - v.c8) + (12) * ((pull v).c10 - v.c10) + (15) * ((pull v).c11 - v.c11) + (2) * ((pull v).c12 - v.c12) + (-150) * ((pull v).c13 - v.c13) + (39) * ((pull v).c15 - v.c15) + (-1) * ((pull v).c17 - v.c17) + (2) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_14 (v : Form) :
    45 * (v.c14 - ((1)*v.c0 + (1)*v.c3)) = (45) * ((pull v).c0 - v.c0) + (-60) * ((pull v).c2 - v.c2) + (30) * ((pull v).c3 - v.c3) + (-4) * ((pull v).c4 - v.c4) + (-16) * ((pull v).c5 - v.c5) + (-2) * ((pull v).c6 - v.c6) + (30) * ((pull v).c7 - v.c7) + (8) * ((pull v).c8 - v.c8) + (-7) * ((pull v).c9 - v.c9) + (14) * ((pull v).c10 - v.c10) + (14) * ((pull v).c11 - v.c11) + (-4) * ((pull v).c12 - v.c12) + (60) * ((pull v).c13 - v.c13) + (-22) * ((pull v).c14 - v.c14) + (-16) * ((pull v).c15 - v.c15) + (2) * ((pull v).c17 - v.c17) := by
  cases v
  simp only [pull]
  omega

theorem certificate_15 (v : Form) :
    90 * (v.c15 - ((0)*v.c0 + (0)*v.c3)) = (30) * ((pull v).c1 - v.c1) + (60) * ((pull v).c2 - v.c2) + (15) * ((pull v).c3 - v.c3) + (8) * ((pull v).c4 - v.c4) + (8) * ((pull v).c5 - v.c5) + (2) * ((pull v).c6 - v.c6) + (-30) * ((pull v).c7 - v.c7) + (-4) * ((pull v).c8 - v.c8) + (23) * ((pull v).c9 - v.c9) + (8) * ((pull v).c10 - v.c10) + (-16) * ((pull v).c11 - v.c11) + (8) * ((pull v).c14 - v.c14) + (2) * ((pull v).c15 - v.c15) + (4) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_16 (v : Form) :
    6 * (v.c16 - ((-1)*v.c0 + (-1)*v.c3)) = (-6) * ((pull v).c0 - v.c0) + (-6) * ((pull v).c3 - v.c3) + (-1) * ((pull v).c4 - v.c4) + (-2) * ((pull v).c5 - v.c5) + (1) * ((pull v).c8 - v.c8) + (-2) * ((pull v).c10 - v.c10) + (1) * ((pull v).c12 - v.c12) + (15) * ((pull v).c13 - v.c13) + (-4) * ((pull v).c15 - v.c15) := by
  cases v
  simp only [pull]
  omega

theorem certificate_17 (v : Form) :
    18 * (v.c17 - ((0)*v.c0 + (0)*v.c3)) = (30) * ((pull v).c1 - v.c1) + (120) * ((pull v).c2 - v.c2) + (12) * ((pull v).c4 - v.c4) + (24) * ((pull v).c5 - v.c5) + (-4) * ((pull v).c6 - v.c6) + (-60) * ((pull v).c7 - v.c7) + (-12) * ((pull v).c8 - v.c8) + (-21) * ((pull v).c10 - v.c10) + (-30) * ((pull v).c11 - v.c11) + (-4) * ((pull v).c12 - v.c12) + (-60) * ((pull v).c13 - v.c13) + (45) * ((pull v).c14 - v.c14) + (18) * ((pull v).c15 - v.c15) + (-4) * ((pull v).c17 - v.c17) + (-4) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_18 (v : Form) :
    18 * (v.c18 - ((0)*v.c0 + (0)*v.c3)) = (-30) * ((pull v).c1 - v.c1) + (-30) * ((pull v).c2 - v.c2) + (-6) * ((pull v).c4 - v.c4) + (1) * ((pull v).c6 - v.c6) + (15) * ((pull v).c7 - v.c7) + (-12) * ((pull v).c9 - v.c9) + (9) * ((pull v).c11 - v.c11) + (-2) * ((pull v).c12 - v.c12) + (-30) * ((pull v).c13 - v.c13) + (-12) * ((pull v).c14 - v.c14) + (6) * ((pull v).c15 - v.c15) + (1) * ((pull v).c17 - v.c17) + (-2) * ((pull v).c18 - v.c18) := by
  cases v
  simp only [pull]
  omega

theorem certificate_19 (v : Form) :
    1 * (v.c19 - ((1)*v.c0 + (0)*v.c3)) = (1) * ((pull v).c0 - v.c0) := by
  cases v
  simp only [pull]
  omega

theorem fixed_normal_form (v : Form) (h : pull v = v) :
    v = normal v.c0 v.c3 := by
  have h1 := certificate_1 v
  rw [h] at h1
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h1
  have h2 := certificate_2 v
  rw [h] at h2
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h2
  have h4 := certificate_4 v
  rw [h] at h4
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h4
  have h5 := certificate_5 v
  rw [h] at h5
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h5
  have h6 := certificate_6 v
  rw [h] at h6
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h6
  have h7 := certificate_7 v
  rw [h] at h7
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h7
  have h8 := certificate_8 v
  rw [h] at h8
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h8
  have h9 := certificate_9 v
  rw [h] at h9
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h9
  have h10 := certificate_10 v
  rw [h] at h10
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h10
  have h11 := certificate_11 v
  rw [h] at h11
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h11
  have h12 := certificate_12 v
  rw [h] at h12
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h12
  have h13 := certificate_13 v
  rw [h] at h13
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h13
  have h14 := certificate_14 v
  rw [h] at h14
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h14
  have h15 := certificate_15 v
  rw [h] at h15
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h15
  have h16 := certificate_16 v
  rw [h] at h16
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h16
  have h17 := certificate_17 v
  rw [h] at h17
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h17
  have h18 := certificate_18 v
  rw [h] at h18
  simp only [Int.sub_self, Int.mul_zero, Int.add_zero] at h18
  have h19 := certificate_19 v
  rw [h] at h19
  simp only [Int.sub_self, Int.mul_zero] at h19
  cases v
  simp only [normal, Form.mk.injEq] at *
  omega

theorem hodge_normal (A B : Int) :
    hodgeReal (normal A B) = 3*B ∧ hodgeImag (normal A B) = -3*A := by
  simp [hodgeReal, hodgeImag, normal]
  omega

theorem invariant_hodge_zero (v : Form) (h : pull v = v)
    (hr : hodgeReal v = 0) (hi : hodgeImag v = 0) : v = zero := by
  have hn := fixed_normal_form v h
  have hp := hodge_normal v.c0 v.c3
  rw [← hn] at hp
  have h0 : v.c0 = 0 := by omega
  have h3 : v.c3 = 0 := by omega
  rw [h0,h3] at hn
  simpa [normal, zero] using hn

theorem normal_parameters (A B : Int) :
    (normal A B).c0 = A ∧ (normal A B).c3 = B := by simp [normal]

theorem normal_injective (A B C D : Int) (h : normal A B = normal C D) : A=C ∧ B=D := by
  have h0 := congrArg Form.c0 h
  have h3 := congrArg Form.c3 h
  simpa [normal] using And.intro h0 h3

def conjugateParameters (p : Int × Int) : Int × Int := (p.1, -p.1-p.2)
theorem conjugate_parameters_involution (p : Int × Int) :
    conjugateParameters (conjugateParameters p) = p := by
  rcases p with ⟨a,b⟩
  change (a, -a-(-a-b)) = (a,b)
  apply Prod.ext
  · rfl
  · change -a-(-a-b)=b
    omega

theorem conjugation_fixed_even_restriction (a b : Int)
    (h : conjugateParameters (a,b) = (a,b)) : ∃ k : Int, a=2*k := by
  refine ⟨-b, ?_⟩
  simp only [conjugateParameters, Prod.mk.injEq] at h
  omega

theorem no_conjugate_normalized_volume (b : Int) :
    conjugateParameters (1,b) ≠ (1,b) := by
  intro h; simp only [conjugateParameters, Prod.mk.injEq] at h; omega

def realMatrix : List (List Int) := [[0, 0, 0, 0, -1, 0], [0, 0, 0, 4, -2, -15], [0, 0, 0, 1, 0, -4], [0, 1, 0, 0, -1, 0], [-4, 2, 15, 4, -2, -15], [-1, 0, 4, 1, 0, -4]]
def triples : List (List Nat) := [[0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 1, 5], [0, 2, 3], [0, 2, 4], [0, 2, 5], [0, 3, 4], [0, 3, 5], [0, 4, 5], [1, 2, 3], [1, 2, 4], [1, 2, 5], [1, 3, 4], [1, 3, 5], [1, 4, 5], [2, 3, 4], [2, 3, 5], [2, 4, 5], [3, 4, 5]]
def exteriorTable : List (List Int) := [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 4, 8, 4, 1, 2, 0], [0, 0, 0, 0, 0, 0, 0, -4, -1, -2, 0, 0, 0, -8, -2, -4, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -60, -15, -30, -16, -4, -8, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 0, 0, -1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 0, 0, 4, 0], [0, 0, -16, -4, 0, -4, -1, 0, 0, 0, 0, -8, -2, 16, 4, 8, 4, 1, 2, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0, 0, -4, 0, 0, -1, 0], [0, 0, -60, -15, 0, -16, -4, 0, 0, 1, 0, -32, -8, 60, 15, 32, 16, 4, 8, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60, 16, 32, 15, 4, 8, -1], [0, 0, 0, 0, 0, 0, 0, -15, -4, -8, 0, 0, 0, -30, -8, -16, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -225, -60, -120, -60, -16, -32, 0], [0, 4, 8, 0, 1, 2, 0, -4, -1, -2, 2, 4, 0, -8, -2, -4, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2, 0, 0, 1, 2, -1, 0, 0, -1], [0, 15, 30, 0, 4, 8, 0, -15, -4, -8, 8, 16, 0, -30, -8, -16, 0, 0, 0, 0], [0, 0, 60, 16, 0, 15, 4, 0, 0, 1, 0, 30, 8, -60, -16, -30, -15, -4, -8, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -15, -4, 0, 0, 15, 0, 0, 4, 0], [0, 0, 225, 60, 0, 60, 16, 0, 0, 0, 0, 120, 32, -225, -60, -120, -60, -16, -32, 0], [-1, 0, 0, -1, 0, 1, 0, 0, 0, -1, -1, 0, 0, 0, 1, 0, -1, 0, 0, -1]]
def entry (i j : Nat) : Int := (realMatrix.getD i []).getD j 0
def tri (i j : Nat) : Nat := (triples.getD i []).getD j 0
def minor (i j : Nat) : Int :=
  let a := tri j 0; let b := tri j 1; let c := tri j 2
  let d := tri i 0; let e := tri i 1; let f := tri i 2
  entry a d * (entry b e * entry c f - entry b f * entry c e)
  - entry a e * (entry b d * entry c f - entry b f * entry c d)
  + entry a f * (entry b d * entry c e - entry b e * entry c d)
set_option maxRecDepth 10000 in
set_option maxHeartbeats 4000000 in
theorem all_exterior_minors : ∀ i j : Fin 20,
    (exteriorTable.getD i.val []).getD j.val 0 = minor i.val j.val := by decide

def coordinates (v : Form) : List Int := [v.c0, v.c1, v.c2, v.c3, v.c4, v.c5, v.c6, v.c7, v.c8, v.c9, v.c10, v.c11, v.c12, v.c13, v.c14, v.c15, v.c16, v.c17, v.c18, v.c19]
def basis (j : Nat) : Form := ⟨if j=0 then 1 else 0, if j=1 then 1 else 0, if j=2 then 1 else 0, if j=3 then 1 else 0, if j=4 then 1 else 0, if j=5 then 1 else 0, if j=6 then 1 else 0, if j=7 then 1 else 0, if j=8 then 1 else 0, if j=9 then 1 else 0, if j=10 then 1 else 0, if j=11 then 1 else 0, if j=12 then 1 else 0, if j=13 then 1 else 0, if j=14 then 1 else 0, if j=15 then 1 else 0, if j=16 then 1 else 0, if j=17 then 1 else 0, if j=18 then 1 else 0, if j=19 then 1 else 0⟩
set_option maxRecDepth 10000 in
set_option maxHeartbeats 4000000 in
theorem pull_table_consistency : ∀ i j : Fin 20,
    ((coordinates (pull (basis j.val))).getD i.val 0)
    = (exteriorTable.getD i.val []).getD j.val 0 := by decide

end H12.GerbeDescent
