# Continue with Block74

Use Komorebi_Beal_Block73_Nontriangular_Deformation_Tame_Obstruction_v7.3.0.zip as
sole execution checkpoint. Read README, contracts, report, proof boundary, theorem
index, gap ledger, all work73/notes, source records, failures and verification.
Keep bytecode disabled. Run:

    python -B verify.py --report ../Block73_Replay.json

--replay-predecessor adds only the immediate Block72 default run, not the full
history. Preserve the original Block72 archive bytes and all controls.

New boundary: rho=(I+7X)rho0 with X=[[p,q],[beta,-p]] is the ACTUAL n1 global
nontriangular deformation; rho0 is only an auxiliary triangular Kummer reference.
The full adjoint equations must be retained. Fixed7 requires
nu7(X)=v7(C)*v/(2epsilon), not a free upper Kummer alpha2.

rho+7xi E12 has identical mod49 traces, determinant and endpoint residuals for
any k(chi) cocycle xi. But a local mod343 lift requires [A,M]=hM, where
F=I+7A, T=I+7M mod49 and h=(Q-1)/7 mod7. At actual beta support M21!=0.
An unramified upper xi with xi(F)!=0 cannot retain the same inertia and lift.
At883 all eight patterns ramify; phi,3,sqrt5 are seventh powers,7 is not.
Thus the [7] direction is detected there. The complete fixed-trace/fixed-inertia
fibre has invariant nu7, but its actual global value is NOT computed or proved0.

NEXT TARGET: compute or constrain the actual global adjoint deformation X with
its local inertia frames and fixed-seven valuation, or obtain a genuine obstruction
to solving its p,q equations with those local conditions. The current eight tuples
do not supply all these data. Do not mistake an auxiliary rho0 with beta0 for a
point in the same fibre or apply the fibre theorem to a finite trace list alone.

ALL EIGHT patterns remain unresolved. The2744 local matrix packets are not global
Frey curves. Local Frey positive families, E(C)/H(C)/beta support distinctions,
and arbitrary-depth/support boundaries remain. No point counts, Lean proof, or
independent mathematical reviewer in Block73. General signature and Beal unresolved.
