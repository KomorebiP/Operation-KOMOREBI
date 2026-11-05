import KomorebiPaperIIIJetNorm

noncomputable section
open Komorebi.PaperIII.PacketCoordinates Komorebi.PaperIII.JetNorm

namespace Komorebi.PaperIII.JetNormControls

def zeroOneSystem : System ℝ ℝ Bool where
  projector b := if b then LinearMap.id else 0
  complete := by simp
  idempotent := by intro b; cases b <;> simp
  orthogonal := by intro b c h; cases b <;> cases c <;> simp_all

theorem zeroOne_continuous : ∀ b, Continuous (zeroOneSystem.projector b) := by
  intro b
  cases b
  · exact continuous_const
  · exact continuous_id

def nullaryB : ContinuousMultilinearMap ℝ (fun (_ : Fin 0) => ℝ) ℝ :=
  ContinuousMultilinearMap.constOfIsEmpty ℝ _ 1

def nullaryJet := continuousPacketJet zeroOneSystem zeroOneSystem zeroOne_continuous
  nullaryB true (fun k : Fin 0 => k.elim0)

theorem nullary_value :
    (nullaryJet (fun k : Fin 0 => k.elim0) : ℝ) = 1 := by
  rfl

theorem nullary_nonzero : nullaryJet ≠ 0 := by
  intro h
  have hv := congrArg (fun B => (B (fun k : Fin 0 => k.elim0) : ℝ)) h
  rw [nullary_value] at hv
  norm_num at hv

def unaryB : ContinuousMultilinearMap ℝ (fun (_ : Fin 1) => ℝ) ℝ :=
  ContinuousMultilinearMap.ofSubsingleton ℝ ℝ ℝ (0 : Fin 1)
    (ContinuousLinearMap.id ℝ ℝ)

theorem zero_input : continuousPacketJet zeroOneSystem zeroOneSystem
    zeroOne_continuous unaryB true (fun _ => false) = 0 := by
  apply continuousPacketJet_eq_zero_of_input_zero zeroOneSystem zeroOneSystem
    zeroOne_continuous unaryB true (fun _ => false) (0 : Fin 1)
  rfl

theorem zero_output : continuousPacketJet zeroOneSystem zeroOneSystem
    zeroOne_continuous unaryB false (fun _ => true) = 0 := by
  apply continuousPacketJet_eq_zero_of_output_zero
  rfl

theorem orthogonal_output_bound :
    ‖continuousPacketJet zeroOneSystem zeroOneSystem
      zeroOne_continuous unaryB true (fun _ => true)‖ ≤ ‖unaryB‖ := by
  apply continuousPacketJet_norm_le_orthogonal zeroOneSystem zeroOneSystem
    zeroOne_continuous unaryB true (fun _ => true) (⊤ : Submodule ℝ ℝ)
  rw [Submodule.starProjection_top]
  rfl

def obliqueTrue : (ℝ × ℝ) →L[ℝ] (ℝ × ℝ) :=
  ((ContinuousLinearMap.fst ℝ ℝ ℝ) + 2 • ContinuousLinearMap.snd ℝ ℝ ℝ).prod 0

def obliqueFalse : (ℝ × ℝ) →L[ℝ] (ℝ × ℝ) :=
  ((-2 : ℝ) • ContinuousLinearMap.snd ℝ ℝ ℝ).prod (ContinuousLinearMap.snd ℝ ℝ ℝ)

def obliqueSystem : System ℝ (ℝ × ℝ) Bool where
  projector b := if b then obliqueTrue.toLinearMap else obliqueFalse.toLinearMap
  complete := by ext <;> simp [obliqueTrue, obliqueFalse]
  idempotent := by intro b; cases b <;> ext <;> simp [obliqueTrue, obliqueFalse]
  orthogonal := by
    intro b c h
    cases b <;> cases c <;> simp_all [obliqueTrue, obliqueFalse] <;> ext <;> simp

theorem oblique_continuous : ∀ b, Continuous (obliqueSystem.projector b) := by
  intro b
  cases b
  · exact obliqueFalse.continuous
  · exact obliqueTrue.continuous

theorem oblique_norm_ge_three :
    3 ≤ ‖obliqueSystem.continuousProjector oblique_continuous true‖ := by
  have h := (obliqueSystem.continuousProjector oblique_continuous true).le_opNorm
    ((1 : ℝ), (1 : ℝ))
  norm_num [System.continuousProjector_apply, obliqueSystem, obliqueTrue,
    Prod.norm_def] at h
  exact h

theorem oblique_not_contractive :
    ¬ ‖obliqueSystem.continuousProjector oblique_continuous true‖ ≤ 1 := by
  have h := oblique_norm_ge_three
  linarith

end Komorebi.PaperIII.JetNormControls
