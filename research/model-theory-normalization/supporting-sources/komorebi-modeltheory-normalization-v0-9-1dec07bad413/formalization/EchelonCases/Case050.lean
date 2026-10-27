module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case050
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 2 2 := ![![![805, 472], ![3032, 359]], ![![2615, 469], ![2949, 110]], ![![1617, 1101], ![2979, 2199]]]
def O : Mat R 2 2 := ![![2612, 2325], ![435, 42]]
def result : List (Test 3 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 5 5 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case050
