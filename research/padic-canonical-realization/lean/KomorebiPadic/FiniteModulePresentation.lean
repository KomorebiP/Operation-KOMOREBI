import Mathlib.GroupTheory.FiniteAbelian.Basic
import Mathlib.Algebra.Module.ZMod
import KomorebiPadic.CyclicIdealCoordinates

/-! # Prime-power cyclic presentations of finite modules
The existence proof uses the classical finite abelian group structure theorem.
The multiset of exponents will be proved intrinsic separately. This existence
choice does not claim to select canonical generators or transition matrices.
-/
namespace KomorebiPadic
namespace FiniteModulePresentation
noncomputable section

variable {p r : ℕ} {V : Type*} [AddCommGroup V] [Module (ZMod (p^r)) V]

/-- Every module over ZMod(p^r) is annihilated by p^r as an additive group. -/
theorem precision_nsmul_zero (x : V) : (p^r) • x = 0 := by
  rw [← Nat.cast_smul_eq_nsmul (R := ZMod (p^r)), ZMod.natCast_self, zero_smul]

/-- A finite module splits into nontrivial cyclic p-power groups of exponent at most r. -/
theorem exists_cyclic [Finite V] (hp : p.Prime) :
    ∃ (I : Type) (_ : Fintype I) (e : I → ℕ),
      (∀ i, 0 < e i ∧ e i ≤ r) ∧ Nonempty (V ≃+ ((i : I) → ZMod (p^(e i)))) := by
  classical
  obtain ⟨I, inst, n, hn, ⟨f⟩⟩ := AddCommGroup.equiv_directSum_zmod_of_finite' V
  let g : V ≃+ ((i : I) → ZMod (n i)) := f.trans (DirectSum.addEquivProd _)
  have hdvd : ∀ i, n i ∣ p^r := by
    intro i
    have hh := congrArg g (precision_nsmul_zero (p := p) (r := r)
      (g.symm (Pi.single i (1 : ZMod (n i)))))
    have hcoord := congrFun (show (p^r) • Pi.single i (1 : ZMod (n i)) = 0 by
      simpa only [map_nsmul, map_zero, AddEquiv.apply_symm_apply] using hh) i
    have hz : (p^r : ZMod (n i)) = 0 := by simpa [nsmul_eq_mul] using hcoord
    exact (ZMod.natCast_eq_zero_iff (p^r) (n i)).mp (by simpa only [Nat.cast_pow] using hz)
  choose e he using fun i => (Nat.dvd_prime_pow hp).mp (hdvd i)
  refine ⟨I, inst, e, ?_, ⟨g.trans (AddEquiv.piCongrRight fun i =>
    (ZMod.ringEquivCongr (he i).2).toAddEquiv)⟩⟩
  intro i
  refine ⟨?_, (he i).1⟩
  by_contra hz
  have he0 : e i = 0 := by omega
  have hni := hn i
  rw [(he i).2, he0, pow_zero] at hni
  omega

/-- A presentation carries actual coordinates and an equivalence, not just a cardinality. -/
structure Presentation (p r : ℕ) (V : Type*) [AddCommGroup V] where
  Index : Type
  indexFintype : Fintype Index
  exponent : Index → ℕ
  positive : ∀ i, 0 < exponent i
  bounded : ∀ i, exponent i ≤ r
  equiv : V ≃+ ((i : Index) → ZMod (p^(exponent i)))

attribute [instance] Presentation.indexFintype

theorem nonempty_presentation [Finite V] (hp : p.Prime) : Nonempty (Presentation p r V) := by
  obtain ⟨I, inst, e, he, ⟨f⟩⟩ := exists_cyclic (p := p) (r := r) (V := V) hp
  exact ⟨⟨I, inst, e, fun i => (he i).1, fun i => (he i).2, f⟩⟩

/-- Noncomputable choice of a presentation; only the signature, not this choice, is intrinsic. -/
def choosePresentation [Finite V] (hp : p.Prime) : Presentation p r V :=
  Classical.choice (nonempty_presentation (p := p) (r := r) (V := V) hp)

abbrev Coordinates (P : Presentation p r V) := (i : P.Index) → ZMod (p^(P.exponent i))

/-- The transported action equals scalar reduction separately in each cyclic factor. -/
theorem equiv_scalar (P : Presentation p r V) (a : ZMod (p^r)) (x : V) (i : P.Index) :
    P.equiv (a • x) i =
      ZMod.castHom (pow_dvd_pow p (P.bounded i)) (ZMod (p^(P.exponent i))) a * P.equiv x i := by
  rw [← ZMod.intCast_zmod_cast a, Int.cast_smul_eq_zsmul, map_zsmul]
  simp only [Pi.smul_apply, map_intCast, zsmul_eq_mul]

omit [Module (ZMod (p^r)) V] in
/-- Exact cardinality, not a bound or a statement of observability. -/
theorem card (hp : 0 < p) (P : Presentation p r V) :
    Nat.card V = p^(∑ i, P.exponent i) := by
  rw [Nat.card_congr P.equiv.toEquiv]
  exact CoordinateIdeal.cyclicState_card hp P.exponent

end
end FiniteModulePresentation
end KomorebiPadic
