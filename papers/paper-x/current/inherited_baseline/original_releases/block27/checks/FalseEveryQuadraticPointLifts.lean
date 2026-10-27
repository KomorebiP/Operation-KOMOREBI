import PaperX.QuadraticGaloisPackets
open PaperX.QuadraticGalois PaperX.QuadraticGaloisPackets
example : ∃ χ : Packet (ZMod 16),
    mapPacket PaperX.QuadraticPacketBoundary.reduceSixteen χ = threePacket := by
  rw [iff_false_intro threePacket_no_lift]
