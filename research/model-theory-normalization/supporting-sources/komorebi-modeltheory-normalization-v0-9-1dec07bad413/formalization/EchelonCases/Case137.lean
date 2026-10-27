module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case137
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 2 2 := ![![![160, 259], ![36, 470]], ![![112, 271], ![302, 184]], ![![600, 11], ![332, 216]]]
def O : Mat R 1 2 := ![![323, 376]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 4 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case137
