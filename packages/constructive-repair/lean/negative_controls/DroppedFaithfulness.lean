import KomorebiRepair
open KomorebiRepair KomorebiRepair.Examples
-- Expected rejection: the target's correction is not a source correction.
theorem bad_transport : Correctable fineD (0, 1) := by
  exact coarse_information_loss.2
