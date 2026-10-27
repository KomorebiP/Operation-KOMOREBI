import Komorebi.CachedPacketTrajectory

set_option autoImplicit false
namespace Komorebi.CachedPosterior
open Matrix
variable {ι κ α : Type*}
variable [Fintype ι] [Fintype κ] [DecidableEq α]

/-- Stop using the exact cached score; rounded certification is deferred until the returned state. -/
def search (K : Kernel κ) (seed : α) (scan : List α) (ε : ℚ) : ℕ → State ι κ α → Option (State ι κ α)
  | 0,c => if score K c ≤ ε^2/4 then some c else none
  | n+1,c => if score K c ≤ ε^2/4 then some c else search K seed scan ε n (advance K seed scan c)

theorem search_score (K : Kernel κ) (seed : α) (scan : List α) (ε : ℚ)
    (n : ℕ) (c out : State ι κ α) (hr : search K seed scan ε n c = some out) :
    score K out ≤ ε^2/4 := by
  induction n generalizing c with
  | zero =>
    unfold search at hr
    split at hr
    next h => cases Option.some.inj hr; exact h
    next => contradiction
  | succ n ih =>
    unfold search at hr
    split at hr
    next h => cases Option.some.inj hr; exact h
    next => exact ih _ hr

theorem search_origin (K : Kernel κ) (seed : α) (scan : List α) (ε : ℚ)
    (n : ℕ) (c out : State ι κ α) (hr : search K seed scan ε n c = some out) :
    ∃ k ≤ n, out = trajectory K seed scan c k := by
  induction n generalizing c with
  | zero =>
    unfold search at hr
    split at hr
    · exact ⟨0,le_rfl,(Option.some.inj hr).symm⟩
    · contradiction
  | succ n ih =>
    unfold search at hr
    split at hr
    · exact ⟨0,Nat.zero_le _,(Option.some.inj hr).symm⟩
    · obtain ⟨k,hk,he⟩ := ih _ hr
      exact ⟨k+1,Nat.succ_le_succ hk,by simpa only [trajectory_shift] using he⟩

theorem search_complete (K : Kernel κ) (seed : α) (scan : List α) (ε : ℚ)
    (n : ℕ) (c : State ι κ α) (hp : score K (trajectory K seed scan c n) ≤ ε^2/4) :
    ∃ out, search K seed scan ε n c = some out := by
  induction n generalizing c with
  | zero => exact ⟨c,by rw [search,ite_eq_left hp]⟩
  | succ n ih =>
    by_cases hs : score K c ≤ ε^2/4
    · exact ⟨c,by rw [search,ite_eq_left hs]⟩
    · have hp' : score K (trajectory K seed scan (advance K seed scan c) n) ≤ ε^2/4 := by
        simpa only [trajectory_shift] using hp
      obtain ⟨out,hr⟩ := ih _ hp'
      exact ⟨out,by rw [search,ite_eq_right hs]; exact hr⟩

end Komorebi.CachedPosterior
