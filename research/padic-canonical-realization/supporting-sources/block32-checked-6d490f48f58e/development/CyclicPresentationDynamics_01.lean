import KomorebiPadic.InvariantFactorSignature
import KomorebiPadic.LinearReachability

/-! # Finite relations and operator transport in cyclic module coordinates
Coordinates have different moduli. Entries are homomorphism coefficients subject
to annihilator constraints; they are not an unconstrained matrix over a field.
-/
namespace KomorebiPadic
namespace FiniteModulePresentation
noncomputable section

variable {p r : ℕ} {V A : Type*} [AddCommGroup V] [Module (ZMod (p^r)) V]

/-- One generator for each nontrivial cyclic factor. -/
def generator (P : Presentation p r V) (i : P.Index) : V :=
  P.equiv.symm (Pi.single i 1)

omit [Module (ZMod (p^r)) V] in
/-- The integer relation lattice is exactly the componentwise p-power relations. -/
theorem generator_relations (P : Presentation p r V) (a : P.Index → ℤ) :
    (∑ i, a i • generator P i) = 0 ↔ ∀ i, (p^(P.exponent i) : ℤ) ∣ a i := by
  classical
  rw [← P.equiv.injective.eq_iff]
  simp only [map_sum, map_zsmul, generator, AddEquiv.apply_symm_apply, map_zero]
  rw [funext_iff]
  simp [Finset.sum_apply, Pi.smul_apply, Pi.single_apply, zsmul_eq_mul,
    ZMod.intCast_zmod_eq_zero_iff_dvd]

omit [Module (ZMod (p^r)) V] in
/-- Every element has an exact cyclic-coordinate generator expansion. -/
theorem generator_expansion (P : Presentation p r V) (x : V) :
    (∑ i, (P.equiv x i).val • generator P i) = x := by
  classical
  apply P.equiv.injective
  simp only [map_sum, map_nsmul, generator, AddEquiv.apply_symm_apply]
  funext j
  simp [Finset.sum_apply, Pi.smul_apply, Pi.single_apply, nsmul_eq_mul]

/-- Transport of one R-linear map through an actual chosen cyclic presentation. -/
def transport (P : Presentation p r V) (T : V →ₗ[ZMod (p^r)] V) :
    Coordinates P →+ Coordinates P :=
  P.equiv.toAddMonoidHom.comp (T.toAddMonoidHom.comp P.equiv.symm.toAddMonoidHom)

@[simp] theorem transport_decode (P : Presentation p r V) (T : V →ₗ[ZMod (p^r)] V)
    (x : Coordinates P) : P.equiv.symm (transport P T x) = T (P.equiv.symm x) :=
  P.equiv.symm_apply_apply _

@[simp] theorem transport_encode (P : Presentation p r V) (T : V →ₗ[ZMod (p^r)] V) (x : V) :
    transport P T (P.equiv x) = P.equiv (T x) := by
  simp only [transport, AddMonoidHom.comp_apply, AddEquiv.toAddMonoidHom_eq_coe,
    AddEquiv.coe_addMonoidHom, AddEquiv.symm_apply_apply, LinearMap.coe_toAddMonoidHom]

def initial (P : Presentation p r V) (M : LinearReachability.System (ZMod (p^r)) V A) :
    Coordinates P := P.equiv M.initial

def run (P : Presentation p r V) (M : LinearReachability.System (ZMod (p^r)) V A) :
    List A → Coordinates P → Coordinates P
  | [], x => x
  | d::ds, x => run P M ds (transport P (M.transition d) x)

theorem run_decode (P : Presentation p r V) (M : LinearReachability.System (ZMod (p^r)) V A)
    (ds : List A) (x : Coordinates P) :
    P.equiv.symm (run P M ds x) = LinearReachability.run M ds (P.equiv.symm x) := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih =>
    simp only [run, LinearReachability.run]
    rw [ih, transport_decode]

theorem run_initial (P : Presentation p r V) (M : LinearReachability.System (ZMod (p^r)) V A)
    (ds : List A) :
    P.equiv.symm (run P M ds (initial P M)) = LinearReachability.run M ds M.initial := by
  rw [run_decode]
  exact congrArg (LinearReachability.run M ds) (P.equiv.symm_apply_apply _)

/-- Output transport needs no field structure or inverse of a nonunit. -/
def output (P : Presentation p r V) (f : V → ZMod (p^r)) (x : Coordinates P) : ZMod (p^r) :=
  f (P.equiv.symm x)

theorem output_run (P : Presentation p r V) (M : LinearReachability.System (ZMod (p^r)) V A)
    (f : V → ZMod (p^r)) (ds : List A) :
    output P f (run P M ds (initial P M)) = f (LinearReachability.run M ds M.initial) := by
  unfold output
  rw [run_initial]

/-- Chosen presentations differ by an exact coordinate equivalence. -/
def changeCoordinates (P Q : Presentation p r V) : Coordinates P ≃+ Coordinates Q :=
  P.equiv.symm.trans Q.equiv

theorem changeCoordinates_transition (P Q : Presentation p r V)
    (T : V →ₗ[ZMod (p^r)] V) (x : Coordinates P) :
    changeCoordinates P Q (transport P T x) = transport Q T (changeCoordinates P Q x) := by
  change Q.equiv (P.equiv.symm (transport P T x)) =
    Q.equiv (T (Q.equiv.symm (Q.equiv (P.equiv.symm x))))
  rw [transport_decode, AddEquiv.symm_apply_apply]

theorem changeCoordinates_run (P Q : Presentation p r V)
    (M : LinearReachability.System (ZMod (p^r)) V A) (ds : List A) (x : Coordinates P) :
    changeCoordinates P Q (run P M ds x) = run Q M ds (changeCoordinates P Q x) := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih =>
    simp only [run]
    rw [ih, changeCoordinates_transition]

/-- Destination row, source column; entries are residues at the destination modulus. -/
def entry (P : Presentation p r V) (T : V →ₗ[ZMod (p^r)] V)
    (j i : P.Index) : ZMod (p^(P.exponent j)) := transport P T (Pi.single i 1) j

omit [Module (ZMod (p^r)) V] in
theorem coordinate_expansion (P : Presentation p r V) (x : Coordinates P) :
    (∑ i, (x i).val • Pi.single i 1) = x := by
  classical
  funext j
  simp [Finset.sum_apply, Pi.smul_apply, Pi.single_apply, nsmul_eq_mul]

/-- Exact mixed-modulus matrix action; source representatives act by repeated addition. -/
theorem transition_entry_formula (P : Presentation p r V) (T : V →ₗ[ZMod (p^r)] V)
    (x : Coordinates P) (j : P.Index) :
    transport P T x j = ∑ i, (x i).val • entry P T j i := by
  conv_lhs => rw [← coordinate_expansion P x]
  simp only [map_sum, map_nsmul, Finset.sum_apply, Pi.smul_apply, entry]

/-- Each entry must annihilate the source cyclic modulus. -/
theorem entry_source_relation (P : Presentation p r V) (T : V →ₗ[ZMod (p^r)] V) (j i : P.Index) :
    (p^(P.exponent i)) • entry P T j i = 0 := by
  classical
  have hg : (p^(P.exponent i)) • (Pi.single i 1 : Coordinates P) = 0 := by
    funext l
    by_cases hl : l = i
    · subst l
      simp [Pi.smul_apply, nsmul_eq_mul]
    · simp [Pi.smul_apply, Pi.single_apply, hl, Ne.symm hl]
  have he := congrArg (fun x => transport P T x j) hg
  simpa only [map_nsmul, map_zero, Pi.smul_apply, entry] using he

/-- An entry from exponent e_i to exponent e_j has forced p-divisibility. -/
theorem entry_divisibility (hp : 0 < p) (P : Presentation p r V)
    (T : V →ₗ[ZMod (p^r)] V) (j i : P.Index) :
    p^(P.exponent j - P.exponent i) ∣ (entry P T j i).val := by
  have hm := (cyclic_torsion_iff hp (P.exponent j) (P.exponent i) (entry P T j i)).mp
    (entry_source_relation P T j i)
  have hd := (PrimePowerIdeal.mem_powerIdeal_iff hp (Nat.sub_le _ _) (entry P T j i)).mp hm
  have he : P.exponent j - min (P.exponent i) (P.exponent j) = P.exponent j - P.exponent i := by omega
  simpa only [he] using hd

end
end FiniteModulePresentation
end KomorebiPadic
