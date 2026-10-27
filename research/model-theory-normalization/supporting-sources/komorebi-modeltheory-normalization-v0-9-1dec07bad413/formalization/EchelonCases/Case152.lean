module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case152
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 3 3 := ![![![451, 436, 276], ![479, 93, 432], ![589, 339, 233]], ![![484, 347, 456], ![427, 476, 265], ![207, 564, 148]], ![![456, 254, 330], ![443, 360, 400], ![63, 151, 0]]]
def O : Mat R 2 3 := ![![37, 453, 286], ![34, 229, 482]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 5 4 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case152
