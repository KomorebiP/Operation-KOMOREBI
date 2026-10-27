import DiscoveryExamples
open Komorebi.Discovery Komorebi.Discovery.Examples
example : finitePrimeDiscover 2 2 3 (fun a => rowRight (shearA a)) shearO = some [] := by decide +kernel
