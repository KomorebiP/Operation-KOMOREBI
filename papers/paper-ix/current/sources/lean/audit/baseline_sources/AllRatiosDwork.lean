module
public import RatioRiccati
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.AllRatiosDwork
open PowerSeries EulerSeriesInverse RatioRiccati HurwitzDworkClosure
open SingularRatioAmice RatioSeriesSupport
variable (p : ℕ) [Fact p.Prime]

/-- Flatness of the actual normalized source, in its previously established standard window. -/
theorem source_window_flat (m j : ℕ) (hm : m∣p-1) (hmpos : 0<m) (hj : j<p) :
    Flat p (SeriesDifferenceBridge.rationalMap p
      (expand (m*p) (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne'
        (Congruential.sectionKernel (m*p) j))) := by
  have H := (flat_encode_iff p _).mpr (StandardWindowDwork.kernel_flat p m j hm hj)
  rw [StandardWindowDwork.kernel_encoding p m j hmpos hj] at H
  exact H

/-- The standard-window inverse theorem supplies the actual packet series, not an arbitrary reciprocal. -/
theorem packet_window_flat (m j : ℕ) (hm : m∣p-1) (hmpos : 0<m) (hj : j<p) :
    Flat p (SeriesDifferenceBridge.rationalMap p
      (expand (m*p) (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne'
        (Congruential.packetSeries (m*p) j))) := by
  have H := (flat_encode_iff p _).mpr (StandardWindowDwork.standard_window_flat p m j hm hmpos hj)
  rw [StandardWindowDwork.packet_encoding p m j hmpos hj] at H
  exact H

/-- All ratios wholly inside the standard window are flat by the proved product and inverse laws. -/
theorem ratio_window_flat (m c : ℕ) (hm : m∣p-1) (hmpos : 0<m) (hc : c+1<p) :
    Flat p (ratio p (m*p) (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne' c) := by
  rw [ratio, SeriesDifferenceBridge.rationalMap, ratioSeries, expanded_inverse, map_mul, map_mul]
  apply flat_mul p
  · apply flat_mul p
    · simp only [PowerSeries.map_C]
      apply flat_constant p
      simpa using (natCast_mem (PadicInt.subring p) (c+1))
    · exact source_window_flat p m c hm hmpos (by omega)
  · exact packet_window_flat p m (c+1) hm hmpos hc

/-- Every permitted ratio is now flat: singular indices use the weighted theorem, others use
    the actual Riccati propagation. There is no assumed all-ratio certificate. -/
theorem all_ratios_flat (m : ℕ) (hm : m∣p-1) (hmpos : 0<m)
    (c : ℕ) (hc : c+1<m*p) :
    Flat p (ratio p (m*p) (Nat.mul_pos hmpos (Fact.out : p.Prime).pos).ne' c) := by
  induction c with
  | zero => exact ratio_window_flat p m 0 hm hmpos (Fact.out : p.Prime).one_lt
  | succ c ih =>
    by_cases hn : p∣c+2
    · obtain ⟨a,he⟩ := hn
      have hp := (Fact.out : p.Prime).pos
      have ha : 0<a := by nlinarith
      have ham : a<m := by nlinarith
      have hmul : a*p=c+2 := by nlinarith
      have hidx : a*p-1=c+1 := by omega
      have H := WeightedDworkTransfer.singular_ratio_flat p m a hm ha ham
      simpa only [hidx, Flat, ratio, SeriesDifferenceBridge.rationalMap] using H
    · exact next_ratio_flat p (m*p) _ (dvd_mul_left p m) c hc hn (ih (by omega))

end KomorebiPaperIX.AllRatiosDwork
