module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case062
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 3 3 := ![![![160, 517, 144], ![590, 142, 456], ![497, 266, 206]], ![![136, 113, 520], ![493, 130, 537], ![535, 151, 204]], ![![282, 292, 605], ![375, 467, 617], ![485, 126, 288]]]
def O : Mat R 2 3 := ![![89, 88, 344], ![264, 398, 38]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 5 4 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case062
