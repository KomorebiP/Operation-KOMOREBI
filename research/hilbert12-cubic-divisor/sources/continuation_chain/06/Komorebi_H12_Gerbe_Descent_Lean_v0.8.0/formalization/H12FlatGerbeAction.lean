import Std
namespace H12FlatGerbeAction

structure V where
  c0 : Int
  c1 : Int
  c2 : Int
  c3 : Int
  c4 : Int
  c5 : Int
  deriving DecidableEq, Repr
structure TwoForm where
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
  deriving DecidableEq, Repr
def flat (v : V) : V := ⟨-8*v.c3 + 4*v.c4 + -15*v.c5, -v.c3, -2*v.c3 + v.c4 + -4*v.c5, 8*v.c0 + -4*v.c1 + 15*v.c2 + -8*v.c3 + 4*v.c4 + -15*v.c5, v.c0 + -v.c3, 2*v.c0 + -v.c1 + 4*v.c2 + -2*v.c3 + v.c4 + -4*v.c5⟩
def opposite (v : V) : V := ⟨-v.c1 + v.c4, 4*v.c0 + -2*v.c1 + -15*v.c2 + -4*v.c3 + 2*v.c4 + 15*v.c5, v.c0 + -4*v.c2 + -v.c3 + 4*v.c5, -v.c1, 4*v.c0 + -2*v.c1 + -15*v.c2, v.c0 + -4*v.c2⟩
def original (v : V) : V := ⟨v.c1, -4*v.c0 + 2*v.c1 + 15*v.c2, -v.c0 + 4*v.c2, v.c4, -4*v.c3 + 2*v.c4 + 15*v.c5, -v.c3 + 4*v.c5⟩
def rotate (v : V) : V := ⟨-v.c3, -v.c4, -v.c5, v.c0 + -v.c3, v.c1 + -v.c4, v.c2 + -v.c5⟩
def sub (v w : V) : V := ⟨v.c0-w.c0, v.c1-w.c1, v.c2-w.c2, v.c3-w.c3, v.c4-w.c4, v.c5-w.c5⟩
def zero : V := ⟨0,0,0,0,0,0⟩
def project (v : TwoForm) : V := ⟨-v.c5 + v.c14, v.c1 + -v.c13, -v.c0 + v.c12, -v.c5 + -v.c8 + v.c10, v.c1 + v.c4 + -v.c9, -v.c0 + -v.c3 + v.c6⟩
def pull (v : TwoForm) : TwoForm := ⟨4*v.c12 + v.c13 + 2*v.c14, -v.c14, 16*v.c7 + 4*v.c8 + 4*v.c10 + v.c11, -4*v.c3 + -v.c4 + -8*v.c7 + -2*v.c8 + -4*v.c12 + -v.c13 + -2*v.c14, -60*v.c7 + -15*v.c8 + -16*v.c10 + -4*v.c11 + v.c14, 15*v.c12 + 4*v.c13 + 8*v.c14, -4*v.c6 + -8*v.c7 + -v.c9 + -2*v.c10 + 4*v.c12 + v.c13 + 2*v.c14, v.c2 + 2*v.c3 + 2*v.c6 + 4*v.c7, 15*v.c6 + 30*v.c7 + 4*v.c9 + 8*v.c10 + -15*v.c12 + -4*v.c13 + -8*v.c14, -60*v.c7 + -16*v.c8 + -15*v.c10 + -4*v.c11 + -v.c14, 15*v.c3 + 4*v.c4 + 30*v.c7 + 8*v.c8 + 15*v.c12 + 4*v.c13 + 8*v.c14, 225*v.c7 + 60*v.c8 + 60*v.c10 + 16*v.c11, 4*v.c0 + v.c1 + 4*v.c3 + v.c4 + 2*v.c5 + -4*v.c6 + 2*v.c8 + -v.c9 + -2*v.c10 + 4*v.c12 + v.c13 + 2*v.c14, -v.c5 + -v.c8 + v.c10 + -v.c14, 15*v.c0 + 4*v.c1 + 15*v.c3 + 4*v.c4 + 8*v.c5 + -15*v.c6 + 8*v.c8 + -4*v.c9 + -8*v.c10 + 15*v.c12 + 4*v.c13 + 8*v.c14⟩
def lift (v : V) : TwoForm := ⟨-v.c2, v.c1, 0, v.c2 + -v.c5, -v.c1 + v.c4, -v.c0, 0, 0, v.c0 + -v.c3, 0, 0, 0, 0, 0, 0⟩

theorem projection_intertwines (v : TwoForm) : project (pull v) = flat (project v) := by
  cases v
  simp only [project, pull, flat, V.mk.injEq]
  omega

theorem projection_surjective_witness (v : V) : project (lift v) = v := by
  cases v
  simp only [project, lift, V.mk.injEq]
  omega

theorem opposite_inverse_flat (v : V) : opposite (flat v) = v := by
  cases v
  simp only [opposite, flat, V.mk.injEq]
  omega

theorem flat_inverse_opposite (v : V) : flat (opposite v) = v := by
  cases v
  simp only [opposite, flat, V.mk.injEq]
  omega

theorem fixed_kernel_relation (v : V) : original (sub (flat v) v) = rotate (sub v (opposite v)) := by
  cases v
  simp only [original, sub, flat, rotate, opposite, V.mk.injEq]
  omega

theorem fixed_groups_agree (v : V) : flat v = v ↔ opposite v = v := by
  constructor
  · intro h
    have h1 := congrArg opposite h
    rw [opposite_inverse_flat] at h1
    exact h1.symm
  · intro h
    have h1 := congrArg flat h
    rw [flat_inverse_opposite] at h1
    exact h1.symm
def parameter (a b : Int) : V := ⟨4*a+b, a-5*b, a, -a+5*b, 5*a-4*b, b⟩

theorem opposite_parameter (a b : Int) :
    sub (opposite (parameter a b)) (parameter a b) =
      ⟨0*a + 0*b, 12*a + 6*b, 0*a + 0*b, 0*a + 0*b, -6*a + 18*b, 0*a + 0*b⟩ := by
  simp only [sub, opposite, parameter, V.mk.injEq]
  omega
def realMatrix : List (List Int) := [[0, 0, 0, 0, -1, 0], [0, 0, 0, 4, -2, -15], [0, 0, 0, 1, 0, -4], [0, 1, 0, 0, -1, 0], [-4, 2, 15, 4, -2, -15], [-1, 0, 4, 1, 0, -4]]
def pairs : List (List Nat) := [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [1, 2], [1, 3], [1, 4], [1, 5], [2, 3], [2, 4], [2, 5], [3, 4], [3, 5], [4, 5]]
def table : List (List Int) := [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 2], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], [0, 0, 0, 0, 0, 0, 0, 16, 4, 0, 4, 1, 0, 0, 0], [0, 0, 0, -4, -1, 0, 0, -8, -2, 0, 0, 0, -4, -1, -2], [0, 0, 0, 0, 0, 0, 0, -60, -15, 0, -16, -4, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 4, 8], [0, 0, 0, 0, 0, 0, -4, -8, 0, -1, -2, 0, 4, 1, 2], [0, 0, 1, 2, 0, 0, 2, 4, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 15, 30, 0, 4, 8, 0, -15, -4, -8], [0, 0, 0, 0, 0, 0, 0, -60, -16, 0, -15, -4, 0, 0, -1], [0, 0, 0, 15, 4, 0, 0, 30, 8, 0, 0, 0, 15, 4, 8], [0, 0, 0, 0, 0, 0, 0, 225, 60, 0, 60, 16, 0, 0, 0], [4, 1, 0, 4, 1, 2, -4, 0, 2, -1, -2, 0, 4, 1, 2], [0, 0, 0, 0, 0, -1, 0, 0, -1, 0, 1, 0, 0, 0, -1], [15, 4, 0, 15, 4, 8, -15, 0, 8, -4, -8, 0, 15, 4, 8]]
def entry (i j : Nat) : Int := (realMatrix.getD i []).getD j 0
def pair (i j : Nat) : Nat := (pairs.getD i []).getD j 0
def minor (i j : Nat) : Int :=
  entry (pair j 0) (pair i 0) * entry (pair j 1) (pair i 1)
  - entry (pair j 0) (pair i 1) * entry (pair j 1) (pair i 0)
set_option maxRecDepth 10000 in
set_option maxHeartbeats 2000000 in
theorem all_two_minors : ∀ i j : Fin 15,
    (table.getD i.val []).getD j.val 0 = minor i.val j.val := by decide
def coordinates (v : TwoForm) : List Int := [v.c0, v.c1, v.c2, v.c3, v.c4, v.c5, v.c6, v.c7, v.c8, v.c9, v.c10, v.c11, v.c12, v.c13, v.c14]
def basis (j : Nat) : TwoForm := ⟨if j=0 then 1 else 0, if j=1 then 1 else 0, if j=2 then 1 else 0, if j=3 then 1 else 0, if j=4 then 1 else 0, if j=5 then 1 else 0, if j=6 then 1 else 0, if j=7 then 1 else 0, if j=8 then 1 else 0, if j=9 then 1 else 0, if j=10 then 1 else 0, if j=11 then 1 else 0, if j=12 then 1 else 0, if j=13 then 1 else 0, if j=14 then 1 else 0⟩
set_option maxRecDepth 10000 in
set_option maxHeartbeats 2000000 in
theorem pull_matches_table : ∀ i j : Fin 15,
    (coordinates (pull (basis j.val))).getD i.val 0 =
    (table.getD i.val []).getD j.val 0 := by decide
end H12FlatGerbeAction
