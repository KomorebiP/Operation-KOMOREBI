module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case077
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 4 4 := ![![![299, 527, 250, 441], ![451, 406, 318, 302], ![234, 59, 177, 312], ![469, 250, 252, 243]], ![![395, 164, 160, 582], ![136, 189, 328, 150], ![406, 53, 261, 547], ![64, 432, 561, 139]], ![![531, 303, 385, 393], ![417, 43, 51, 304], ![74, 386, 27, 527], ![43, 437, 313, 578]]]
def O : Mat R 1 4 := ![![375, 0, 250, 250]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem computed : fastPrimeDiscover 5 4 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case077
