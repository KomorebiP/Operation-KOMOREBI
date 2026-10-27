# Proof ledger — v0.36

Evidence: new statements are Lean-checked as written; detailed fresh replay is
recorded in RESULT.json. Every theorem retains its exact quantified hypotheses.
The ordinary Koenig compactness theorem is imported from pinned Mathlib.

## Closed mechanisms

1. Finite reduction-stable nonempty levels yield a compatible branch without
   surjectivity of transition maps on the solution sets.
2. A fixed prefix survives every level iff a full compatible branch passes
   through it; persistent prefixes have persistent children.
3. A failed prefix has a finite obstruction; finitely many prefixes give a
   finite eventual survivor horizon. The latter is non-effective.
4. Arbitrary-level genuine matrix-unit reductions agree with the old positive
   coefficient tower. Coherent tuples assemble into actual PadicInt matrix units.
5. A p-adic root above a fixed prefix exists iff every deeper level admits one.
   Arbitrarily deep solvability suffices; absence has a first obstructed level.
6. A finite local-conjugacy family has one shared p-adic Frobenius and compatible
   conjugators iff every deeper level admits the simultaneous tuple. The
   conjugators are identity modulo p, not functions of a local group variable.
7. Controls: two distinct 2-adic roots 1,-1 of X^2=1 in the same residue fibre;
   9 is a root modulo 16 but has no successor modulo 32 and no 2-adic continuation;
   all four roots mod16 and the two prefixes reached from mod32 are classified.

## Declaration inventory


### FiniteBranchCompactness

- `structure Komorebi.StrongArtin.ResonantBranch.FiniteTower`
- `def Komorebi.StrongArtin.ResonantBranch.DownwardClosed`
- `theorem Komorebi.StrongArtin.ResonantBranch.exists_compatible_branch`
- `theorem Komorebi.StrongArtin.ResonantBranch.compatible_branch_iff`
- `theorem Komorebi.StrongArtin.ResonantBranch.no_branch_iff_finite_obstruction`

### PersistentFinitePrefix

- `def Komorebi.StrongArtin.ResonantBranch.AbovePrefix`
- `theorem Komorebi.StrongArtin.ResonantBranch.abovePrefix_downward`
- `def Komorebi.StrongArtin.ResonantBranch.Persistent`
- `theorem Komorebi.StrongArtin.ResonantBranch.persistent_supplies_all_levels`
- `theorem Komorebi.StrongArtin.ResonantBranch.persistent_iff_branch`
- `theorem Komorebi.StrongArtin.ResonantBranch.persistent_has_persistent_child`
- `theorem Komorebi.StrongArtin.ResonantBranch.not_persistent_iff_finite_obstruction`
- `theorem Komorebi.StrongArtin.ResonantBranch.finite_survivor_horizon`

### PadicFiniteBranch

- `def Komorebi.StrongArtin.FrobeniusTower.coefficientProject`
- `def Komorebi.StrongArtin.FrobeniusTower.project`
- `theorem Komorebi.StrongArtin.FrobeniusTower.project_refl`
- `theorem Komorebi.StrongArtin.FrobeniusTower.project_trans`
- `theorem Komorebi.StrongArtin.FrobeniusTower.project_succ`
- `theorem Komorebi.StrongArtin.FrobeniusTower.project_padicReduction`
- `def Komorebi.StrongArtin.FrobeniusTower.finiteTupleTower`
- `theorem Komorebi.StrongArtin.FrobeniusTower.padic_tuple_exists_iff_every_level`
- `theorem Komorebi.StrongArtin.FrobeniusTower.no_padic_tuple_iff_empty_level`

### ResonantPadicRoots

- `def Komorebi.StrongArtin.FrobeniusTower.matrixUnitTower`
- `def Komorebi.StrongArtin.FrobeniusTower.RootNode`
- `theorem Komorebi.StrongArtin.FrobeniusTower.rootNode_downward`
- `theorem Komorebi.StrongArtin.FrobeniusTower.padic_root_iff_all_deeper_roots`
- `theorem Komorebi.StrongArtin.FrobeniusTower.no_padic_root_iff_finite_prefix_obstruction`
- `theorem Komorebi.StrongArtin.FrobeniusTower.padic_root_finite_survivor_horizon`
- `theorem Komorebi.StrongArtin.FrobeniusTower.surviving_root_has_surviving_child`
- `theorem Komorebi.StrongArtin.FrobeniusTower.padic_root_iff_arbitrarily_deep_roots`
- `theorem Komorebi.StrongArtin.FrobeniusTower.first_obstructed_level`

### SimultaneousGaugeBranch

- `def Komorebi.StrongArtin.FrobeniusTower.LocalGaugeNode`
- `theorem Komorebi.StrongArtin.FrobeniusTower.localGaugeNode_downward`
- `def Komorebi.StrongArtin.FrobeniusTower.PadicGaugeMatch`
- `theorem Komorebi.StrongArtin.FrobeniusTower.padic_local_gauge_iff_every_level`
- `theorem Komorebi.StrongArtin.FrobeniusTower.padic_local_gauge_iff_all_deeper_levels`
- `theorem Komorebi.StrongArtin.FrobeniusTower.no_padic_local_gauge_iff_finite_obstruction`

### ResonantBranchControls

- `theorem Komorebi.StrongArtin.FrobeniusTower.BranchControls.two_distinct_two_adic_square_roots`
- `def Komorebi.StrongArtin.FrobeniusTower.BranchControls.red32to16`
- `theorem Komorebi.StrongArtin.FrobeniusTower.BranchControls.square_root_prefix_mod16`
- `theorem Komorebi.StrongArtin.FrobeniusTower.BranchControls.square_root_prefix_dies_mod32`
- `theorem Komorebi.StrongArtin.FrobeniusTower.BranchControls.no_two_adic_root_above_nine`
- `theorem Komorebi.StrongArtin.FrobeniusTower.BranchControls.roots_mod16_and_extendable_prefixes`
