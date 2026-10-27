module
public import KomorebiPhysics.ClosedCellDomains

/-!
Infinite coarse currents with real domain obligations and actual HasSum proofs.
The iterated sums are justified by symmetry and coarse-domain preservation.
Joint double-array summability is a separate, explicitly stated hypothesis.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace DomainAtlas
open Filter
open scoped BigOperators Topology
variable {H I J : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable [CompleteSpace H] {T : H →ₗ.[ℂ] H} (P : DomainAtlas T I)
variable (f : I → J)
variable (hp : ∀ (a : J) (x : T.domain), P.atlas.cell (f ⁻¹' {a}) x ∈ T.domain)
include hp

/-- For a single receiving fine packet, symmetry moves T onto that packet.
Only the source-cell state sum is then needed. -/
theorem cell_amplitude_row_hasSum (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (i : I) (b : J) :
    HasSum (fun j : f ⁻¹' {b} => P.amplitude x i j)
      (inner ℂ (P.atlas.proj i x) (T ((P.coarsenOfPreserves f hp).project b x))) := by
  have h := (P.atlas.cell_sum (f ⁻¹' {b}) (x : H)).mapL (innerSL ℂ (T (P.project i x)))
  have he : ∀ j : f ⁻¹' {b}, P.amplitude x i j =
      inner ℂ (T (P.project i x)) (P.atlas.proj j x) := by
    intro j
    exact (hT (P.project i x) (P.project j x)).symm
  have hh := h.congr_fun he
  have hv := hT (P.project i x) ((P.coarsenOfPreserves f hp).project b x)
  change inner ℂ (T (P.project i x)) (P.atlas.cell (f ⁻¹' {b}) x) = _ at hv
  exact hv ▸ hh

theorem cell_current_row_hasSum (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (i : I) (b : J) :
    HasSum (fun j : f ⁻¹' {b} => P.current x i j)
      (2 * (inner ℂ (P.atlas.proj i x) (T ((P.coarsenOfPreserves f hp).project b x))).im) :=
  ((P.cell_amplitude_row_hasSum f hp hT x i b).mapL Complex.imCLM).mul_left 2

theorem coarse_amplitude_iterated_hasSum (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J) :
    HasSum (fun i : f ⁻¹' {a} => ∑' j : f ⁻¹' {b}, P.amplitude x i j)
      ((P.coarsenOfPreserves f hp).amplitude x a b) := by
  have h := (P.atlas.cell_sum (f ⁻¹' {a}) (x : H)).mapL
    (innerSLFlip ℂ (T ((P.coarsenOfPreserves f hp).project b x)))
  exact h.congr_fun (fun i => (P.cell_amplitude_row_hasSum f hp hT x i b).tsum_eq)

/-- Equation (6.47), with actual inner and outer summability proved. This is
not a declaration that the entire double array is absolutely summable. -/
theorem coarse_current_iterated_hasSum (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J) :
    HasSum (fun i : f ⁻¹' {a} => ∑' j : f ⁻¹' {b}, P.current x i j)
      ((P.coarsenOfPreserves f hp).current x a b) := by
  have h := (((P.atlas.cell_sum (f ⁻¹' {a}) (x : H)).mapL
    (innerSLFlip ℂ (T ((P.coarsenOfPreserves f hp).project b x)))).mapL Complex.imCLM).mul_left 2
  exact h.congr_fun (fun i => (P.cell_current_row_hasSum f hp hT x i b).tsum_eq)

theorem coarse_amplitude_iterated (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J) :
    (P.coarsenOfPreserves f hp).amplitude x a b =
      ∑' i : f ⁻¹' {a}, ∑' j : f ⁻¹' {b}, P.amplitude x i j :=
  (P.coarse_amplitude_iterated_hasSum f hp hT x a b).tsum_eq.symm

theorem coarse_current_iterated (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J) :
    (P.coarsenOfPreserves f hp).current x a b =
      ∑' i : f ⁻¹' {a}, ∑' j : f ⁻¹' {b}, P.current x i j :=
  (P.coarse_current_iterated_hasSum f hp hT x a b).tsum_eq.symm

theorem coarse_current_outer_abs_summable (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J) :
    Summable (fun i : f ⁻¹' {a} => |∑' j : f ⁻¹' {b}, P.current x i j|) :=
  (P.coarse_current_iterated_hasSum f hp hT x a b).summable.abs

/-- The other iteration order has its own proof. This does not use a false
Fubini theorem based only on rowwise summability. -/
theorem coarse_current_reverse_hasSum (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J) :
    HasSum (fun j : f ⁻¹' {b} => ∑' i : f ⁻¹' {a}, P.current x i j)
      ((P.coarsenOfPreserves f hp).current x a b) := by
  have h := (P.coarse_current_iterated_hasSum f hp hT x b a).neg
  have he : ∀ j : f ⁻¹' {b}, (∑' i : f ⁻¹' {a}, P.current x i j) =
      -(∑' i : f ⁻¹' {a}, P.current x j i) := by
    intro j
    rw [← tsum_neg]
    exact tsum_congr (fun i => P.current_antisymm hT x i j)
  have hh := h.congr_fun he
  rw [← (P.coarsenOfPreserves f hp).current_antisymm hT x a b] at hh
  exact hh

theorem coarse_current_order_independent (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J) :
    (∑' i : f ⁻¹' {a}, ∑' j : f ⁻¹' {b}, P.current x i j) =
      ∑' j : f ⁻¹' {b}, ∑' i : f ⁻¹' {a}, P.current x i j := by
  rw [(P.coarse_current_iterated_hasSum f hp hT x a b).tsum_eq,
    (P.coarse_current_reverse_hasSum f hp hT x a b).tsum_eq]

/-- Flattening to a jointly indexed sum explicitly requires joint summability. -/
theorem coarse_current_product (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J)
    (hs : Summable (fun ij : (f ⁻¹' {a}) × (f ⁻¹' {b}) => P.current x ij.1 ij.2)) :
    HasSum (fun ij : (f ⁻¹' {a}) × (f ⁻¹' {b}) => P.current x ij.1 ij.2)
      ((P.coarsenOfPreserves f hp).current x a b) := by
  have h := hs.hasSum
  have hv := hs.tsum_prod
  rw [hv, ← P.coarse_current_iterated f hp hT x a b] at h
  exact h

theorem coarse_amplitude_product (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a b : J)
    (hs : Summable (fun ij : (f ⁻¹' {a}) × (f ⁻¹' {b}) => P.amplitude x ij.1 ij.2)) :
    HasSum (fun ij : (f ⁻¹' {a}) × (f ⁻¹' {b}) => P.amplitude x ij.1 ij.2)
      ((P.coarsenOfPreserves f hp).amplitude x a b) := by
  have h := hs.hasSum
  rw [hs.tsum_prod, ← P.coarse_amplitude_iterated f hp hT x a b] at h
  exact h

/-- An infinite receiving cell has an actual energy derivative because its
constructed coarse projection is bounded and domain-compatible. No infinite
sum of derivatives is assumed or interchanged. -/
theorem infinite_cell_hasDerivAt (hT : GraphDomain.IsSymmetric T)
    {ψ : ℝ → T.domain} {t : ℝ}
    (hψ : HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) (a : J) :
    HasDerivAt (fun s => ∑' i : f ⁻¹' {a}, P.atlas.energy (ψ s : H) i)
      (∑' b, (P.coarsenOfPreserves f hp).current (ψ t) a b) t := by
  have h := (P.coarsenOfPreserves f hp).hasDerivAt_energy_tsum hT hψ a
  have he : (fun s => ∑' i : f ⁻¹' {a}, P.atlas.energy (ψ s : H) i) =
      (fun s => (P.coarsenOfPreserves f hp).atlas.energy (ψ s : H) a) := by
    funext s
    exact (P.atlas.coarsenInfinite_energy f (ψ s : H) a).symm
  rw [he]
  exact h

/-- Even internal infinite cells cancel as iterated, certified sums. -/
theorem infinite_cell_internal_zero (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (a : J) :
    (∑' i : f ⁻¹' {a}, ∑' j : f ⁻¹' {a}, P.current x i j) = 0 := by
  rw [← P.coarse_current_iterated f hp hT x a a]
  exact (P.coarsenOfPreserves f hp).current_self hT x a

end DomainAtlas
end KomorebiPhysics
