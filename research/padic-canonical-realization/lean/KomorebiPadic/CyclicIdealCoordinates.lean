import KomorebiPadic.CoordinateIdealClosure
import Mathlib.Tactic.Ring

/-! # Exact cyclic normalization
Decode divides a divisible canonical integer representative, never a nonunit
inside the residue ring. The result is an additive equivalence with scalar law.
-/
namespace KomorebiPadic
namespace PrimePowerIdeal
variable {p r c : ℕ}

theorem modulus_factor (hc : c ≤ r) : p^(r-c)*p^c = p^r := by
  rw [← pow_add, Nat.sub_add_cancel hc]

noncomputable def cyclicEncode (_hp : 0 < p) (_hc : c ≤ r) (y : ZMod (p^c)) :
    capacityIdeal p r c :=
  ⟨(p : ZMod (p^r))^(r-c) * (y.val : ZMod (p^r)),
    Ideal.mem_span_singleton.mpr ⟨(y.val : ZMod (p^r)), rfl⟩⟩

theorem cyclicEncode_val (hp : 0 < p) (hc : c ≤ r) (y : ZMod (p^c)) :
    (cyclicEncode hp hc y).val.val = p^(r-c)*y.val := by
  let : NeZero (p^c) := ⟨ne_of_gt (pow_pos hp _)⟩
  have hl : p^(r-c)*y.val < p^r := by
    rw [← modulus_factor hc]
    exact Nat.mul_lt_mul_of_pos_left (ZMod.val_lt y) (pow_pos hp _)
  change ((p : ZMod (p^r))^(r-c) * (y.val : ZMod (p^r))).val = _
  rw [← Nat.cast_pow, ← Nat.cast_mul]
  exact ZMod.val_natCast_of_lt hl

noncomputable def cyclicDecode (x : capacityIdeal p r c) : ZMod (p^c) :=
  (x.val.val / p^(r-c) : ℕ)

theorem cyclicDecode_val (hp : 0 < p) (hc : c ≤ r) (x : capacityIdeal p r c) :
    (cyclicDecode x).val = x.val.val / p^(r-c) := by
  let : NeZero (p^r) := ⟨ne_of_gt (pow_pos hp _)⟩
  apply ZMod.val_natCast_of_lt
  apply (Nat.div_lt_iff_lt_mul (pow_pos hp _)).mpr
  rw [Nat.mul_comm, modulus_factor hc]
  exact ZMod.val_lt x.val

@[simp] theorem cyclicDecode_encode (hp : 0 < p) (hc : c ≤ r) (y : ZMod (p^c)) :
    cyclicDecode (cyclicEncode hp hc y) = y := by
  let : NeZero (p^c) := ⟨ne_of_gt (pow_pos hp _)⟩
  unfold cyclicDecode
  rw [cyclicEncode_val hp hc, Nat.mul_div_right _ (pow_pos hp _)]
  exact ZMod.natCast_zmod_val y

@[simp] theorem cyclicEncode_decode (hp : 0 < p) (hc : c ≤ r) (x : capacityIdeal p r c) :
    cyclicEncode hp hc (cyclicDecode x) = x := by
  let : NeZero (p^r) := ⟨ne_of_gt (pow_pos hp _)⟩
  apply Subtype.ext
  apply ZMod.val_injective (p^r)
  rw [cyclicEncode_val hp hc, cyclicDecode_val hp hc]
  exact Nat.mul_div_cancel' ((mem_powerIdeal_iff hp (Nat.sub_le _ _) x.val).mp x.property)

theorem scaled_mod (_hp : 0 < p) (hc : c ≤ r) (n : ℕ) :
    (p : ZMod (p^r))^(r-c) * (n % p^c : ℕ) = (p : ZMod (p^r))^(r-c) * (n : ℕ) := by
  have hz : (p : ZMod (p^r))^(r-c) * (p^c : ℕ) = 0 := by
    rw [Nat.cast_pow, ← pow_add, Nat.sub_add_cancel hc, ← Nat.cast_pow, ZMod.natCast_self]
  have he : ((n % p^c : ℕ) : ZMod (p^r)) + (p^c : ℕ)*(n / p^c : ℕ) = (n : ℕ) := by
    simpa only [Nat.cast_add, Nat.cast_mul] using
      congrArg (fun k : ℕ => (k : ZMod (p^r))) (Nat.mod_add_div n (p^c))
  conv_rhs => rw [← he]
  rw [mul_add, ← mul_assoc, hz, zero_mul, add_zero]

theorem cyclicEncode_add (hp : 0 < p) (hc : c ≤ r) (x y : ZMod (p^c)) :
    cyclicEncode hp hc (x+y) = cyclicEncode hp hc x + cyclicEncode hp hc y := by
  let : NeZero (p^c) := ⟨ne_of_gt (pow_pos hp _)⟩
  apply Subtype.ext
  change (p : ZMod (p^r))^(r-c)*((x+y).val : ℕ) =
    (p : ZMod (p^r))^(r-c)*(x.val : ℕ) + (p : ZMod (p^r))^(r-c)*(y.val : ℕ)
  rw [ZMod.val_add, scaled_mod hp hc, Nat.cast_add, mul_add]

noncomputable def cyclicIdealEquiv (hp : 0 < p) (hc : c ≤ r) :
    ZMod (p^c) ≃+ capacityIdeal p r c where
  toFun := cyclicEncode hp hc
  invFun := cyclicDecode
  left_inv := cyclicDecode_encode hp hc
  right_inv := cyclicEncode_decode hp hc
  map_add' := cyclicEncode_add hp hc

theorem cyclicEncode_scalar (hp : 0 < p) (hc : c ≤ r)
    (a : ZMod (p^r)) (y : ZMod (p^c)) :
    cyclicEncode hp hc (ZMod.castHom (pow_dvd_pow p hc) (ZMod (p^c)) a * y) =
      a • cyclicEncode hp hc y := by
  let : NeZero (p^r) := ⟨ne_of_gt (pow_pos hp _)⟩
  let : NeZero (p^c) := ⟨ne_of_gt (pow_pos hp _)⟩
  have he : ZMod.castHom (pow_dvd_pow p hc) (ZMod (p^c)) a = (a.val : ZMod (p^c)) := by
    conv_lhs => rw [← ZMod.natCast_zmod_val a]
    simp
  calc
    cyclicEncode hp hc (ZMod.castHom (pow_dvd_pow p hc) (ZMod (p^c)) a*y) =
        cyclicEncode hp hc (a.val • y) := by rw [he, nsmul_eq_mul]
    _ = a.val • cyclicEncode hp hc y := map_nsmul (cyclicIdealEquiv hp hc) a.val y
    _ = a • cyclicEncode hp hc y := by
      apply Subtype.ext
      simp [nsmul_eq_mul]

theorem capacityIdeal_card (hp : 0 < p) (hc : c ≤ r) :
    Nat.card (capacityIdeal p r c) = p^c := by
  rw [← Nat.card_congr (cyclicIdealEquiv hp hc).toEquiv, Nat.card_zmod]

end PrimePowerIdeal
namespace CoordinateIdeal
open PrimePowerIdeal
variable {p r : ℕ} {I A : Type*} [Fintype I] [DecidableEq I] [Fintype A]

abbrev CyclicState (p : ℕ) (w : I → ℕ) := (i : I) → ZMod (p^(w i))

noncomputable def cyclicBoxEquiv (hp : 0 < p) (w : I → ℕ) (hw : ∀ i, w i ≤ r) :
    CyclicState p w ≃+ State (p := p) (r := r) w where
  toFun y := ⟨fun i => (cyclicIdealEquiv hp (hw i) (y i)).val,
    fun i => (cyclicIdealEquiv hp (hw i) (y i)).property⟩
  invFun x i := (cyclicIdealEquiv hp (hw i)).symm ⟨x.val i, x.property i⟩
  left_inv y := by
    funext i
    exact (cyclicIdealEquiv hp (hw i)).left_inv (y i)
  right_inv x := by
    apply Subtype.ext
    funext i
    exact congrArg Subtype.val ((cyclicIdealEquiv hp (hw i)).apply_symm_apply ⟨x.val i, x.property i⟩)
  map_add' x y := by
    apply Subtype.ext
    funext i
    exact congrArg Subtype.val ((cyclicIdealEquiv hp (hw i)).map_add (x i) (y i))

noncomputable def dropZeroCyclicEquiv (w : I → ℕ) :
    CyclicState p w ≃+ ((i : {i : I // 0 < w i}) → ZMod (p^(w i.val))) := by
  classical
  refine
    { toFun := fun x i => x i.val
      invFun := fun y i => if hi : 0 < w i then y ⟨i,hi⟩ else 0
      left_inv := ?_
      right_inv := ?_
      map_add' := fun _ _ => rfl }
  · intro x
    funext i
    by_cases hi : 0 < w i
    · simp [hi]
    · have hz : w i = 0 := Nat.eq_zero_of_not_pos hi
      have : Subsingleton (ZMod (p^(w i))) := by simp only [hz, pow_zero]; infer_instance
      exact Subsingleton.elim _ _
  · intro y
    funext i
    simp [i.property]

noncomputable def cyclicInitial (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) : CyclicState p (least hp M) :=
  (cyclicBoxEquiv hp (least hp M) (least_bound hp M)).symm (initial hp M)

noncomputable def cyclicTransition (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (d : A) :
    CyclicState p (least hp M) →+ CyclicState p (least hp M) :=
  let e := cyclicBoxEquiv hp (least hp M) (least_bound hp M)
  e.symm.toAddMonoidHom.comp ((transition hp M d).toAddMonoidHom.comp e.toAddMonoidHom)

noncomputable def cyclicRun (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) :
    List A → CyclicState p (least hp M) → CyclicState p (least hp M)
  | [], x => x
  | d::ds, x => cyclicRun hp M ds (cyclicTransition hp M d x)

theorem cyclicTransition_embedding (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (d : A)
    (x : CyclicState p (least hp M)) :
    cyclicBoxEquiv hp (least hp M) (least_bound hp M) (cyclicTransition hp M d x) =
      transition hp M d (cyclicBoxEquiv hp (least hp M) (least_bound hp M) x) := by
  exact (cyclicBoxEquiv hp (least hp M) (least_bound hp M)).apply_symm_apply _

theorem cyclicRun_embedding (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (ds : List A)
    (x : CyclicState p (least hp M)) :
    cyclicBoxEquiv hp (least hp M) (least_bound hp M) (cyclicRun hp M ds x) =
      run hp M ds (cyclicBoxEquiv hp (least hp M) (least_bound hp M) x) := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih =>
    simp only [cyclicRun, run]
    rw [ih, cyclicTransition_embedding]

theorem cyclicTransition_coordinate (hp : 0 < p)
    (M : System (p := p) (r := r) (I := I) (A := A)) (d : A)
    (x : CyclicState p (least hp M)) (j : I) :
    cyclicTransition hp M d x j =
      (((∑ i : I, ((p : ZMod (p^r))^(r-least hp M i) * ((x i).val : ℕ)) *
        M.transition d (Pi.single i 1) j).val / p^(r-least hp M j) : ℕ) :
        ZMod (p^(least hp M j))) := by
  change (((M.transition d (fun i => (p : ZMod (p^r))^(r-least hp M i) *
    ((x i).val : ℕ)) j).val / p^(r-least hp M j) : ℕ) : ZMod (p^(least hp M j))) = _
  rw [CoordinateSupport.transition_eq_sum]

omit [DecidableEq I] [Fintype A] in
theorem cyclicState_card (hp : 0 < p) (w : I → ℕ) :
    Nat.card (CyclicState p w) = p^(∑ i, w i) := by
  classical
  let : ∀ i : I, Fintype (ZMod (p^(w i))) := fun i => by
    let : NeZero (p^(w i)) := ⟨ne_of_gt (pow_pos hp _)⟩
    infer_instance
  rw [Nat.card_eq_fintype_card]
  simp [CyclicState, Fintype.card_pi, ZMod.card, Finset.prod_pow_eq_pow_sum]

omit [DecidableEq I] in
theorem boxState_card (hp : 0 < p) (w : I → ℕ) (hw : ∀ i, w i ≤ r) :
    Nat.card (State (p := p) (r := r) w) = p^(∑ i, w i) := by
  rw [← Nat.card_congr (cyclicBoxEquiv hp w hw).toEquiv, cyclicState_card hp w]

end CoordinateIdeal
end KomorebiPadic
