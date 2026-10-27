import AVOC.RecursiveSynthesis

namespace Komorebi.AVOC.SemanticSynthesis

open Synthesis

/-- Instrument the exact number of indexed representatives inspected. -/
def insertMeasured (p : Entry) : List Entry → List Entry × Nat
  | [] => ([p], 0)
  | q :: qs =>
    if p.bits = q.bits then (pick p q :: qs, 1)
    else let r := insertMeasured p qs; (q :: r.1, r.2 + 1)

theorem insertMeasured_refines (p : Entry) (xs : List Entry) :
    (insertMeasured p xs).1 = insert p xs := by
  induction xs with
  | nil => rfl
  | cons q qs ih =>
    by_cases h : p.bits = q.bits <;> simp [insertMeasured, insert, h, ih]

theorem insertMeasured_probes (p : Entry) (xs : List Entry) :
    (insertMeasured p xs).2 ≤ xs.length := by
  induction xs with
  | nil => simp [insertMeasured]
  | cons q qs ih =>
    by_cases h : p.bits = q.bits <;> simp [insertMeasured, h] <;> omega

def collectMeasured : List Program → List Entry → Nat → List Entry × Nat
  | [], acc, probes => (acc, probes)
  | p :: ps, acc, probes =>
    let r := insertMeasured (pack p) acc
    collectMeasured ps r.1 (probes + r.2)

theorem collectMeasured_refines (ps : List Program) (acc : List Entry) (n : Nat) :
    (collectMeasured ps acc n).1 = collect ps acc := by
  induction ps generalizing acc n with
  | nil => rfl
  | cons p ps ih => simp only [collectMeasured, collect, ih, insertMeasured_refines]

theorem collectMeasured_probes (ps : List Program) (acc : List Entry) (n : Nat)
    (h : Unique acc) : (collectMeasured ps acc n).2 ≤ n + 256 * ps.length := by
  induction ps generalizing acc n with
  | nil => simp [collectMeasured]
  | cons p ps ih =>
    have hs : Unique (insertMeasured (pack p) acc).1 := by
      rw [insertMeasured_refines]
      exact insert_unique _ _ h
    have hi := ih (insertMeasured (pack p) acc).1 (n + (insertMeasured (pack p) acc).2) hs
    have hp := insertMeasured_probes (pack p) acc
    have hl := unique_entries_at_most_256 acc h
    simp only [collectMeasured, List.length_cons]
    omega

structure Work where
  emitted : Nat
  nodeMass : Nat
  probes : Nat
  deriving Repr, DecidableEq

def Work.add (a b : Work) : Work :=
  ⟨a.emitted+b.emitted, a.nodeMass+b.nodeMass, a.probes+b.probes⟩

/-- Declared structural tariff: emitted entries; eight eager semantic traversals plus
two size traversals (cached size and statistics); eight signature bits plus one size comparison per probe.
Allocation, list copying, recursion, serialization and wall time are NOT all priced. -/
def Work.charge (w : Work) : Nat := w.emitted + 10*w.nodeMass + 9*w.probes

theorem work_charge_add (a b : Work) : (a.add b).charge = a.charge+b.charge := by
  simp only [Work.add, Work.charge]
  omega

structure Indexed where
  entries : List Entry
  work : Work

def indexed (ps : List Program) : Indexed :=
  let result := collectMeasured ps [] 0
  ⟨result.1, ⟨ps.length, (ps.map nodes).sum, result.2⟩⟩

theorem indexed_refines (ps : List Program) : (indexed ps).entries = compact ps :=
  collectMeasured_refines ps [] 0

theorem indexed_unique (ps : List Program) : Unique (indexed ps).entries := by
  rw [indexed_refines]
  exact compact_unique ps

theorem indexed_coverage (ps : List Program) : Covers ps (codes (indexed ps).entries) := by
  rw [indexed_refines]
  exact compact_covers_all ps

theorem indexed_probe_bound (ps : List Program) : (indexed ps).work.probes ≤ 256*ps.length := by
  simpa [indexed] using collectMeasured_probes ps [] 0 (by simp [Unique])

theorem sum_nodes_le (ps : List Program) (m : Nat) (h : ∀ p ∈ ps, nodes p ≤ m) :
    (ps.map nodes).sum ≤ ps.length*m := by
  induction ps with
  | nil => simp
  | cons p ps ih =>
    have hp := h p (by simp)
    have ht := ih (fun q hq => h q (List.mem_cons_of_mem p hq))
    simp only [List.map_cons, List.sum_cons, List.length_cons, Nat.add_mul]
    omega

/-- Reserve conservatively BEFORE constructing and indexing a grammar layer. -/
def reserve (count maxNodes : Nat) : Nat := count + 10*(count*maxNodes) + 9*(256*count)

theorem indexed_charge_bound (ps : List Program) (m : Nat) (h : ∀ p ∈ ps, nodes p ≤ m) :
    (indexed ps).work.charge ≤ reserve ps.length m := by
  have hn := sum_nodes_le ps m h
  have hp := indexed_probe_bound ps
  change ps.length + 10*(ps.map nodes).sum + 9*(indexed ps).work.probes ≤ _
  unfold reserve
  omega

structure Stage where
  depth : Nat
  kept : Nat
  work : Work
  deriving Repr, DecidableEq

structure Build where
  entries : List Entry
  work : Work
  stages : List Stage

def learnedBuild : Nat → Build
  | 0 => let r := indexed atoms; ⟨r.entries, r.work, [⟨0,r.entries.length,r.work⟩]⟩
  | d+1 =>
    let previous := learnedBuild d
    let r := indexed (expand (codes previous.entries))
    ⟨r.entries, previous.work.add r.work,
      previous.stages ++ [⟨d+1,r.entries.length,r.work⟩]⟩

theorem learnedBuild_refines (d : Nat) : (learnedBuild d).entries = representatives d := by
  induction d with
  | zero => exact indexed_refines atoms
  | succ d ih => simp only [learnedBuild, representatives, ih, indexed_refines]

theorem learnedBuild_capacity (d : Nat) : (learnedBuild d).entries.length ≤ 256 := by
  rw [learnedBuild_refines]
  cases d <;> exact compact_at_most_256 _

theorem learnedBuild_optimum (r : Program) (d : Nat) :
    nodes (select r r (codes (learnedBuild d).entries)) = nodes (select r r (programs d)) := by
  rw [learnedBuild_refines]
  exact same_optimum_as_frozen r d

/-- Frozen ablation: use the same signature checker/index, but generate the next
layer from EVERY previous raw expression, not the retained representatives. -/
structure FrozenBuild extends Build where
  raw : List Program

def frozenBuild : Nat → FrozenBuild
  | 0 => let r := indexed atoms; ⟨⟨r.entries,r.work,[⟨0,r.entries.length,r.work⟩]⟩,atoms⟩
  | d+1 =>
    let previous := frozenBuild d
    let raw := expand previous.raw
    let r := indexed raw
    ⟨⟨r.entries,previous.work.add r.work,
      previous.stages ++ [⟨d+1,r.entries.length,r.work⟩]⟩,raw⟩

theorem frozenBuild_raw (d : Nat) : (frozenBuild d).raw = programs d := by
  induction d with
  | zero => rfl
  | succ d ih => simp only [frozenBuild, programs, ih]

theorem frozenBuild_indexed (d : Nat) : (frozenBuild d).entries = compact (programs d) := by
  cases d with
  | zero => exact indexed_refines _
  | succ d => simp only [frozenBuild, frozenBuild_raw, indexed_refines, programs]

theorem equal_executed_optima (r : Program) (d : Nat) :
    nodes (select r r (codes (learnedBuild d).entries)) =
    nodes (select r r (codes (frozenBuild d).entries)) := by
  rw [learnedBuild_optimum, frozenBuild_indexed, compact_preserves_query_optimum]

end Komorebi.AVOC.SemanticSynthesis
