module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case059
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 3 3 := ![![![18, 14, 51], ![35, 91, 21], ![104, 16, 39]], ![![35, 111, 1], ![82, 58, 68], ![22, 85, 107]], ![![86, 36, 8], ![94, 45, 23], ![55, 13, 20]]]
def O : Mat R 1 3 := ![![83, 54, 59]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 3 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case059
