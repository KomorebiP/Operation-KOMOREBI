import PaperIRelease.PacketTopologyGeneral
set_option autoImplicit false
universe u v w
open Komorebi.Foundation
example {𝕜 : Type u} {X : Type v} {ι : Type w}
    [NormedField 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X] [Fintype ι]
    (P : LinearProjectorFamily 𝕜 X ι) (hP : ∀ i, Continuous (P.proj i)) (i : ι) :
    IsBoundedLinearMap 𝕜 (P.proj i) := by
  exact (ContinuousLinearMap.mk (P.proj i) (hP i)).isBoundedLinearMap
