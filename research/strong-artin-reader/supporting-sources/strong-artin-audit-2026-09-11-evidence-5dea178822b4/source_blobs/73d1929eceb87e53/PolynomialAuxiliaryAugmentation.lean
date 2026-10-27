import SurjectiveResidueHomPolynomialHensel
import AuxiliaryColumnCompletion

/-!
# Canonical polynomial augmentation by auxiliary Jacobian columns

A finite family of auxiliary columns can be inserted as honest linear variables
in a coordinate polynomial system.  The Jacobian of the augmented system is
then the original Jacobian together with exactly those columns.
-/

namespace Komorebi.StrongArtin.PolynomialAuxiliaryAugmentation

open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.AuxiliaryColumnCompletion

noncomputable section

variable {R k ι κ α : Type*} [CommRing R]

/-- Rename the variables of a polynomial expression. -/
def renameExpr (f : ι → α) : Expr ι R → Expr α R
  | .const c => .const c
  | .var i => .var (f i)
  | .add e₁ e₂ => .add (renameExpr f e₁) (renameExpr f e₂)
  | .neg e => .neg (renameExpr f e)
  | .mul e₁ e₂ => .mul (renameExpr f e₁) (renameExpr f e₂)

@[simp] theorem eval_renameExpr (f : ι → α) (e : Expr ι R)
    (x : α → R) :
    Expr.eval (renameExpr f e) x = Expr.eval e (fun i => x (f i)) := by
  induction e with
  | const c => rfl
  | var i => rfl
  | add e₁ e₂ ih₁ ih₂ => simp [renameExpr, ih₁, ih₂]
  | neg e ih => simp [renameExpr, ih]
  | mul e₁ e₂ ih₁ ih₂ => simp [renameExpr, ih₁, ih₂]

@[simp] theorem deriv_renameExpr (f : ι → α) (e : Expr ι R)
    (x delta : α → R) :
    Expr.deriv (renameExpr f e) x delta =
      Expr.deriv e (fun i => x (f i)) (fun i => delta (f i)) := by
  induction e with
  | const c => rfl
  | var i => rfl
  | add e₁ e₂ ih₁ ih₂ => simp [renameExpr, ih₁, ih₂]
  | neg e ih => simp [renameExpr, ih]
  | mul e₁ e₂ ih₁ ih₂ => simp [renameExpr, ih₁, ih₂]

@[simp] theorem deriv_zero_direction (e : Expr ι R) (x : ι → R) :
    Expr.deriv e x 0 = 0 := by
  induction e with
  | const c => rfl
  | var i => rfl
  | add e₁ e₂ ih₁ ih₂ => simp [ih₁, ih₂]
  | neg e ih => simp [ih]
  | mul e₁ e₂ ih₁ ih₂ => simp [ih₁, ih₂]

/-- Ordered finite sum in the expression syntax.  The syntax itself need not be
quotiented by associativity or commutativity. -/
def listSumExpr {β : Type*} : List β → (β → Expr α R) → Expr α R
  | [], _ => .const 0
  | b :: l, f => .add (f b) (listSumExpr l f)

@[simp] theorem eval_listSumExpr {β : Type*} (l : List β)
    (f : β → Expr α R) (x : α → R) :
    Expr.eval (listSumExpr l f) x =
      (l.map (fun b => Expr.eval (f b) x)).sum := by
  induction l with
  | nil => rfl
  | cons b l ih => simp [listSumExpr, ih]

@[simp] theorem deriv_listSumExpr {β : Type*} (l : List β)
    (f : β → Expr α R) (x delta : α → R) :
    Expr.deriv (listSumExpr l f) x delta =
      (l.map (fun b => Expr.deriv (f b) x delta)).sum := by
  induction l with
  | nil => rfl
  | cons b l ih => simp [listSumExpr, ih]

/-- Sum over a finite type using its canonical `univ.toList` enumeration. -/
def fintypeSumExpr {β : Type*} [Fintype β] [DecidableEq β]
    (f : β → Expr α R) : Expr α R :=
  listSumExpr Finset.univ.toList f

@[simp] theorem eval_fintypeSumExpr {β : Type*} [Fintype β] [DecidableEq β]
    (f : β → Expr α R) (x : α → R) :
    Expr.eval (fintypeSumExpr f) x = ∑ b : β, Expr.eval (f b) x := by
  simp [fintypeSumExpr]

@[simp] theorem deriv_fintypeSumExpr {β : Type*} [Fintype β] [DecidableEq β]
    (f : β → Expr α R) (x delta : α → R) :
    Expr.deriv (fintypeSumExpr f) x delta =
      ∑ b : β, Expr.deriv (f b) x delta := by
  simp [fintypeSumExpr]

/-- Embed an original point and set every auxiliary coordinate to zero. -/
def zeroAuxPoint [Zero R] (x : ι → R) : Sum ι α → R :=
  Sum.elim x (fun _ => 0)

/-- Add one honest linear variable for each selected auxiliary column. -/
def augmentedSystem [Fintype α] [DecidableEq α]
    (system : System ι κ R) (column : α → (κ → R)) :
    System (Sum ι α) κ R :=
  fun j => .add
    (renameExpr Sum.inl (system j))
    (fintypeSumExpr fun a =>
      .mul (.const (column a j)) (.var (.inr a)))

@[simp] theorem eval_augmentedSystem [Fintype α] [DecidableEq α]
    (system : System ι κ R) (column : α → (κ → R))
    (x : Sum ι α → R) (j : κ) :
    evalSystem (augmentedSystem system column) x j =
      evalSystem system (fun i => x (.inl i)) j +
        ∑ a : α, column a j * x (.inr a) := by
  simp [augmentedSystem, evalSystem]

@[simp] theorem eval_augmentedSystem_zeroAuxPoint
    [Fintype α] [DecidableEq α]
    (system : System ι κ R) (column : α → (κ → R)) (x : ι → R) :
    evalSystem (augmentedSystem system column) (zeroAuxPoint x) =
      evalSystem system x := by
  funext j
  rw [eval_augmentedSystem]
  simp [zeroAuxPoint]

@[simp] theorem deriv_augmentedSystem [Fintype α] [DecidableEq α]
    (system : System ι κ R) (column : α → (κ → R))
    (x delta : Sum ι α → R) (j : κ) :
    Expr.deriv ((augmentedSystem system column) j) x delta =
      Expr.deriv (system j) (fun i => x (.inl i))
        (fun i => delta (.inl i)) +
        ∑ a : α, column a j * delta (.inr a) := by
  simp [augmentedSystem]

/-- The standard-coordinate matrix obtained by adjoining the auxiliary columns. -/
def augmentedMatrix (J : Matrix κ ι k) (column : α → (κ → k)) :
    Matrix κ (Sum ι α) k :=
  fun j s => Sum.elim (fun i => J j i) (fun a => column a j) s

@[simp] theorem augmentedMatrix_inl
    (J : Matrix κ ι k) (column : α → (κ → k)) (j : κ) (i : ι) :
    augmentedMatrix J column j (.inl i) = J j i := rfl

@[simp] theorem augmentedMatrix_inr
    (J : Matrix κ ι k) (column : α → (κ → k)) (j : κ) (a : α) :
    augmentedMatrix J column j (.inr a) = column a j := rfl

/-- The Jacobian of the explicit augmented polynomial system is exactly the
original Jacobian with the selected columns adjoined. -/
theorem jacobianMatrix_augmentedSystem
    [Fintype ι] [DecidableEq ι]
    [Fintype κ] [DecidableEq κ]
    [Fintype α] [DecidableEq α]
    (system : System ι κ R) (column : α → (κ → R)) (x : ι → R) :
    jacobianMatrix (augmentedSystem system column) (zeroAuxPoint x) =
      augmentedMatrix (jacobianMatrix system x) column := by
  ext j s
  cases s with
  | inl i =>
      have hdir :
          (fun i' : ι => Pi.single (M := fun _ : Sum ι α => R) (Sum.inl i) (1 : R) (Sum.inl i')) =
            Pi.single i 1 := by
        funext i'
        simp [Pi.single_apply]
      simp only [jacobianMatrix_apply, deriv_augmentedSystem, zeroAuxPoint,
        Sum.elim_inl]
      rw [hdir]
      have hsum : (∑ a : α, column a j *
          Pi.single (M := fun _ : Sum ι α => R) (Sum.inl i) (1 : R) (Sum.inr a)) = 0 := by
        apply Finset.sum_eq_zero
        intro a ha
        simp
      rw [hsum, add_zero]
      simp [augmentedMatrix, jacobianMatrix_apply]
  | inr a =>
      simp only [jacobianMatrix_apply, deriv_augmentedSystem, zeroAuxPoint,
        Sum.elim_inl]
      have hzero : Expr.deriv (system j) x
          (fun i : ι => Pi.single (M := fun _ : Sum ι α => R) (Sum.inr a) (1 : R) (Sum.inl i)) = 0 := by
        have hfun :
            (fun i : ι => Pi.single (M := fun _ : Sum ι α => R) (Sum.inr a) (1 : R) (Sum.inl i)) = 0 := by
          funext i
          simp
        rw [hfun]
        exact deriv_zero_direction (system j) x
      rw [hzero, zero_add]
      classical
      rw [Finset.sum_eq_single a]
      · simp [augmentedMatrix]
      · intro b hb hba
        simp [hba]
      · simp

end

end Komorebi.StrongArtin.PolynomialAuxiliaryAugmentation

#print axioms Komorebi.StrongArtin.PolynomialAuxiliaryAugmentation.jacobianMatrix_augmentedSystem
