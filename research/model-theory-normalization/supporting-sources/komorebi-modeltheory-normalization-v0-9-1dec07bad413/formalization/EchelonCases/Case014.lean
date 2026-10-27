module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case014
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 2 → Mat R 6 6 := ![![![3, 2, 14, 14, 5, 17], ![16, 12, 4, 7, 21, 19], ![1, 15, 21, 16, 23, 1], ![16, 12, 13, 15, 14, 13], ![15, 7, 19, 0, 5, 3], ![18, 19, 22, 0, 4, 23]], ![![7, 15, 9, 10, 10, 4], ![9, 18, 8, 7, 23, 17], ![10, 19, 14, 3, 7, 9], ![14, 22, 24, 1, 8, 12], ![22, 13, 13, 0, 0, 3], ![2, 1, 20, 23, 16, 11]]]
def O : Mat R 1 6 := ![![8, 10, 12, 24, 16, 6]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 5 2 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case014
