module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case012
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 6 6 := ![![![184, 123, 124, 190, 155, 27], ![111, 172, 118, 22, 5, 225], ![211, 96, 121, 72, 191, 42], ![227, 174, 126, 126, 229, 215], ![22, 143, 124, 135, 45, 174], ![205, 149, 202, 67, 239, 140]], ![![176, 8, 65, 21, 105, 238], ![18, 175, 199, 155, 46, 78], ![201, 131, 46, 190, 141, 105], ![184, 198, 157, 93, 52, 129], ![164, 49, 20, 134, 71, 205], ![175, 56, 166, 209, 87, 11]]]
def O : Mat R 1 6 := ![![13, 209, 121, 160, 68, 232]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 3 5 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case012
