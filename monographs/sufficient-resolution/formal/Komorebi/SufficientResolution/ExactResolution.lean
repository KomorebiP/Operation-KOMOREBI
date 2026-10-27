import Mathlib.Algebra.Module.LinearMap.End

/-!
# Exact analysis/synthesis and realizable transport kernels

The ambient coordinate space may be redundant.  No orthogonality, finite
 dimension, topology, positivity, or arithmetic existence is assumed.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution

universe uR uX uY uZ uV uW uU

variable (R : Type uR) [Semiring R]
variable (X : Type uX) [AddCommMonoid X] [Module R X]
variable (V : Type uV) [AddCommMonoid V] [Module R V]

/-- A split analysis/synthesis pair.  Only synthesis after analysis is identity. -/
structure Resolution where
  analysis : X →ₗ[R] V
  synthesis : V →ₗ[R] X
  synthesis_analysis : synthesis.comp analysis = LinearMap.id

namespace Resolution

variable {R X V}
variable {Y : Type uY} [AddCommMonoid Y] [Module R Y]
variable {Z : Type uZ} [AddCommMonoid Z] [Module R Z]
variable {W : Type uW} [AddCommMonoid W] [Module R W]
variable {U : Type uU} [AddCommMonoid U] [Module R U]

variable (r : Resolution R X V) (s : Resolution R Y W)

@[simp] theorem synthesis_analysis_apply (x : X) :
    r.synthesis (r.analysis x) = x :=
  LinearMap.congr_fun r.synthesis_analysis x

/-- Idempotent selecting coordinate vectors which describe global objects. -/
def projector : V →ₗ[R] V := r.analysis.comp r.synthesis

@[simp] theorem projector_apply (v : V) :
    r.projector v = r.analysis (r.synthesis v) := rfl

@[simp] theorem projector_idempotent :
    r.projector.comp r.projector = r.projector := by
  ext v
  simp

@[simp] theorem projector_analysis (x : X) :
    r.projector (r.analysis x) = r.analysis x := by
  simp

 theorem analysis_injective : Function.Injective r.analysis := by
  intro x y h
  have := congrArg r.synthesis h
  simpa using this

 theorem fixed_iff_realizable (v : V) :
    r.projector v = v ↔ ∃ x : X, r.analysis x = v := by
  constructor
  · intro h
    exact ⟨r.synthesis v, h⟩
  · rintro ⟨x, rfl⟩
    simp

/-- Resolve a global linear transformation into a coordinate transport kernel. -/
def encode (T : X →ₗ[R] Y) : V →ₗ[R] W :=
  s.analysis.comp (T.comp r.synthesis)

/-- Synthesize a global transformation from proposed coordinate transport. -/
def decode (K : V →ₗ[R] W) : X →ₗ[R] Y :=
  s.synthesis.comp (K.comp r.analysis)

/-- A coordinate kernel acts only between realizable coordinate sectors. -/
def Compatible (K : V →ₗ[R] W) : Prop :=
  s.projector.comp (K.comp r.projector) = K

@[simp] theorem decode_encode (T : X →ₗ[R] Y) :
    r.decode s (r.encode s T) = T := by
  ext x
  simp [decode, encode]

 theorem encode_decode (K : V →ₗ[R] W) :
    r.encode s (r.decode s K) = s.projector.comp (K.comp r.projector) := by
  ext v
  rfl

 theorem encode_compatible (T : X →ₗ[R] Y) :
    r.Compatible s (r.encode s T) := by
  ext v
  simp [encode]

 theorem encode_injective : Function.Injective (r.encode s) := by
  intro T S h
  have := congrArg (r.decode s) h
  simpa using this

 theorem compatible_iff_existsUnique (K : V →ₗ[R] W) :
    r.Compatible s K ↔ ∃! T : X →ₗ[R] Y, r.encode s T = K := by
  constructor
  · intro h
    refine ⟨r.decode s K, ?_, ?_⟩
    · exact (r.encode_decode s K).trans h
    · intro T hT
      rw [← hT, decode_encode]
  · rintro ⟨T, hT, _⟩
    rw [← hT]
    exact r.encode_compatible s T

/-- Exact, mutually inverse correspondence with the compatible-kernel subtype. -/
def kernelEquiv : (X →ₗ[R] Y) ≃ {K : V →ₗ[R] W // r.Compatible s K} where
  toFun T := ⟨r.encode s T, r.encode_compatible s T⟩
  invFun K := r.decode s K.1
  left_inv T := r.decode_encode s T
  right_inv K := by
    apply Subtype.ext
    exact (r.encode_decode s K.1).trans K.2

 theorem encode_comp (t : Resolution R Z U) (S : Y →ₗ[R] Z) (T : X →ₗ[R] Y) :
    r.encode t (S.comp T) = (s.encode t S).comp (r.encode s T) := by
  ext v
  simp [encode]

 theorem encode_id : r.encode r LinearMap.id = r.projector := by
  ext v
  rfl

 theorem encode_add (T S : X →ₗ[R] Y) :
    r.encode s (T + S) = r.encode s T + r.encode s S := by
  ext v
  simp [encode]

 theorem encode_zero : r.encode s 0 = 0 := by
  ext v
  simp [encode]

end Resolution
end Komorebi.SufficientResolution
