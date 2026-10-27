import KomorebiRepair
open KomorebiRepair KomorebiRepair.Examples
-- Expected rejection: the actual executable singleton-menu check is false.
theorem bad_menu : repairMenuCheck finiteD finiteE finiteR {0} = true := by
  decide +kernel
