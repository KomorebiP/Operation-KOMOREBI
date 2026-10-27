import Mathlib.Data.Nat.Prime.Basic
import KomorebiPaperV.Packets

/-!
Author: Komorebi P.
Literal residue-mask factorization using the Chinese remainder equivalence.
-/

namespace KomorebiPaperV.CRT

variable {V : Type*} [Zero V]

theorem residue_pair_iff (M N : ℕ) (h : M.Coprime N) (r : ZMod (M * N)) (i : ℤ) :
    (i : ZMod (M * N)) = r ↔
      (i : ZMod M) = (ZMod.chineseRemainder h r).1 ∧
      (i : ZMod N) = (ZMod.chineseRemainder h r).2 := by
  rw [← (ZMod.chineseRemainder h).injective.eq_iff, Prod.ext_iff]
  simp only [map_intCast, Prod.fst_intCast, Prod.snd_intCast]

theorem residue_mask_factorization (M N : ℕ) (h : M.Coprime N)
    (r : ZMod (M * N)) (x : ℤ → V) :
    KomorebiPaperV.packet (fun i : ℤ => (i : ZMod (M * N))) r x =
      KomorebiPaperV.packet (fun i : ℤ => (i : ZMod M))
        (ZMod.chineseRemainder h r).1
        (KomorebiPaperV.packet (fun i : ℤ => (i : ZMod N))
          (ZMod.chineseRemainder h r).2 x) := by
  funext i
  simp only [KomorebiPaperV.packet, residue_pair_iff M N h]
  split_ifs <;> simp_all

theorem dyadic_odd_coprime (a d : ℕ) (hd : Odd d) : (2 ^ a).Coprime d := by
  exact (Nat.coprime_two_left.mpr hd).pow_left a

theorem dyadic_odd_packet_factorization (a d : ℕ) (hd : Odd d)
    (r : ZMod (2 ^ a * d)) (x : ℤ → V) :
    KomorebiPaperV.packet (fun i : ℤ => (i : ZMod (2 ^ a * d))) r x =
      KomorebiPaperV.packet (fun i : ℤ => (i : ZMod (2 ^ a)))
        (ZMod.chineseRemainder (dyadic_odd_coprime a d hd) r).1
        (KomorebiPaperV.packet (fun i : ℤ => (i : ZMod d))
          (ZMod.chineseRemainder (dyadic_odd_coprime a d hd) r).2 x) :=
  residue_mask_factorization _ _ (dyadic_odd_coprime a d hd) r x

end KomorebiPaperV.CRT
