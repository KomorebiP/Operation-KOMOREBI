module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case184
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 5 5 := ![![![190, 61, 168, 113, 0], ![16, 1, 13, 131, 109], ![15, 17, 145, 1, 57], ![66, 46, 167, 80, 219], ![82, 90, 236, 120, 79]], ![![182, 240, 208, 122, 72], ![17, 129, 228, 181, 105], ![40, 131, 146, 133, 106], ![164, 47, 217, 2, 17], ![151, 162, 56, 95, 197]]]
def O : Mat R 2 5 := ![![171, 200, 177, 159, 118], ![199, 74, 135, 218, 222]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 3 5 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case184
