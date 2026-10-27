import KomorebiPaperV.Packets

/-!
Author: Komorebi P.
Checked source; see the bundled build and axiom audit.
Literal signed integer polyphase coordinates, with N strictly positive.
No summability or Hilbert-space statement is hidden in these pointwise identities.
-/

open scoped BigOperators
namespace KomorebiPaperV.IntegerPolyphase

variable {V : Type*}

def phase (N : ℕ) (hN : 0 < N) (n : ℤ) : Fin N :=
  ⟨(n % (N : ℤ)).toNat, by
    have hn : (N : ℤ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hN)
    have hlo := Int.emod_nonneg n hn
    have hhi := Int.emod_lt_of_pos n (show (0 : ℤ) < N by exact_mod_cast hN)
    omega⟩

def quotient (N : ℕ) (n : ℤ) : ℤ := n / (N : ℤ)

def address (N : ℕ) (r : Fin N) (q : ℤ) : ℤ := (N : ℤ) * q + (r.val : ℤ)

theorem phase_val (N : ℕ) (hN : 0 < N) (n : ℤ) :
    ((phase N hN n).val : ℤ) = n % (N : ℤ) := by
  apply Int.toNat_of_nonneg
  exact Int.emod_nonneg n (by exact_mod_cast (Nat.ne_of_gt hN))

theorem address_phase_quotient (N : ℕ) (hN : 0 < N) (n : ℤ) :
    address N (phase N hN n) (quotient N n) = n := by
  dsimp [address, quotient]
  rw [phase_val]
  exact Int.mul_ediv_add_emod n (N : ℤ)

theorem address_divmod (N : ℕ) (hN : 0 < N) (r : Fin N) (q : ℤ) :
    address N r q / (N : ℤ) = q ∧
      address N r q % (N : ℤ) = (r.val : ℤ) := by
  apply (Int.ediv_emod_unique (show (0 : ℤ) < N by exact_mod_cast hN)).mpr
  refine ⟨?_, ?_, ?_⟩
  · dsimp [address]
    ring
  · exact_mod_cast (Nat.zero_le r.val)
  · exact_mod_cast r.isLt

theorem phase_address (N : ℕ) (hN : 0 < N) (r : Fin N) (q : ℤ) :
    phase N hN (address N r q) = r := by
  apply Fin.ext
  change (address N r q % (N : ℤ)).toNat = r.val
  rw [(address_divmod N hN r q).2]
  simp

theorem quotient_address (N : ℕ) (hN : 0 < N) (r : Fin N) (q : ℤ) :
    quotient N (address N r q) = q :=
  (address_divmod N hN r q).1

def addressEquiv (N : ℕ) (hN : 0 < N) : ℤ ≃ Fin N × ℤ where
  toFun n := (phase N hN n, quotient N n)
  invFun p := address N p.1 p.2
  left_inv := address_phase_quotient N hN
  right_inv p := by
    apply Prod.ext
    · exact phase_address N hN p.1 p.2
    · exact quotient_address N hN p.1 p.2

def analysis (N : ℕ) (x : ℤ → V) : Fin N → ℤ → V :=
  fun r q => x (address N r q)

def synthesis (N : ℕ) (hN : 0 < N) (c : Fin N → ℤ → V) : ℤ → V :=
  fun n => c (phase N hN n) (quotient N n)

theorem synthesis_analysis (N : ℕ) (hN : 0 < N) (x : ℤ → V) :
    synthesis N hN (analysis N x) = x := by
  funext n
  exact congrArg x (address_phase_quotient N hN n)

theorem analysis_synthesis (N : ℕ) (hN : 0 < N) (c : Fin N → ℤ → V) :
    analysis N (synthesis N hN c) = c := by
  funext r q
  simp only [analysis, synthesis, phase_address N hN, quotient_address N hN]

/-- Delay in ORIGINAL sample addresses, allowing negative delays (advances). -/
def delay (d : ℤ) (x : ℤ → V) : ℤ → V := fun n => x (n - d)

/-- A channel delay d is an original-sample delay N*d. -/
theorem channel_delay (N : ℕ) (d : ℤ) (x : ℤ → V) (r : Fin N) (q : ℤ) :
    analysis N (delay ((N : ℤ) * d) x) r q = analysis N x r (q - d) := by
  dsimp [analysis, delay, address]
  congr 1
  ring

/-- General sample delay: the input phase is (r-d) mod N and the carry is signed. -/
theorem sample_delay (N : ℕ) (hN : 0 < N) (d : ℤ) (x : ℤ → V)
    (r : Fin N) (q : ℤ) :
    analysis N (delay d x) r q =
      analysis N x (phase N hN ((r.val : ℤ) - d))
        (q + quotient N ((r.val : ℤ) - d)) := by
  dsimp [analysis, delay]
  congr 1
  have h := address_phase_quotient N hN ((r.val : ℤ) - d)
  dsimp [address] at h ⊢
  linear_combination -h

/-- Reduction modulo a divisor commutes with reduction modulo the finer modulus. -/
theorem emod_coarsen (N M : ℕ) (hNM : N ∣ M) (n : ℤ) :
    (n % (M : ℤ)) % (N : ℤ) = n % (N : ℤ) := by
  exact Int.emod_emod_of_dvd n (by exact_mod_cast hNM)

/-- Literal integer-residue refinement, before the bounded-operator bridge. -/
theorem residue_refinement [AddCommMonoid V] (N M : ℕ) (hN : 0 < N)
    (hM : 0 < M) (hNM : N ∣ M) (r : Fin N) (x : ℤ → V) (n : ℤ) :
    KomorebiPaperV.packet (phase N hN) r x n =
      ∑ s : Fin M, if phase N hN (s.val : ℤ) = r
        then KomorebiPaperV.packet (phase M hM) s x n else 0 := by
  have hcoarse : (phase N hN ∘ fun j : ℤ => ((phase M hM j).val : ℤ)) =
      phase N hN := by
    funext j
    apply Fin.ext
    change (((phase M hM j).val : ℤ) % (N : ℤ)).toNat = (j % (N : ℤ)).toNat
    rw [phase_val, emod_coarsen N M hNM]
  have h := KomorebiPaperV.packet_refinement (phase M hM)
    (fun s : Fin M => phase N hN (s.val : ℤ)) r x n
  have hc : (fun j : ℤ => phase N hN ((phase M hM j).val : ℤ)) = phase N hN := hcoarse
  simpa only [Function.comp_def, hc] using h

end KomorebiPaperV.IntegerPolyphase
