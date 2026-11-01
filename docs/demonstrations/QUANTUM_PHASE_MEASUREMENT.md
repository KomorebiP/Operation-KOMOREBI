# Quantum phase, measurement, and information loss

**An extended hand-worked example · Komorebi P.**

Start with a two-component state whose amplitudes are known exactly. Change its
relative phase, measure it in three different settings, and reconstruct its
density matrix. Then remove the coherence and identify precisely which
questions can still be answered. A two-qubit record and a refinement of its
measurement packets show where the lost information went.

[Run the phase comparison](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-phase) ·
[Run partial dephasing and tomography](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-dephasing) ·
[Read the exact Python program](../../examples/quantum_phase_measurement.py) ·
[Download source and results](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/quantum-phase-measurement/source-and-results.zip)

This is a standard finite quantum-mechanics calculation presented through
the collection's packet and recovery language. All displayed probabilities
are exact ensemble probabilities. Repeated experimental measurements would
estimate them; a single measurement does not reveal a density matrix.

## 1. Declare the state and the coordinates

Use the orthonormal basis \(\{|0\rangle,|1\rangle\}\) of \(\mathbb C^2\).
For a phase \(z\in\mathbb C\) with \(|z|=1\), let

\[
|\psi_z\rangle=\frac35|0\rangle+\frac45z|1\rangle,
\qquad
\rho_z=|\psi_z\rangle\langle\psi_z|
=\begin{pmatrix}
9/25&(12/25)\overline z\\
(12/25)z&16/25
\end{pmatrix}.
\]

The norm is \(9/25+16/25=1\). Consequently
\(\rho_z^*=\rho_z\), \(\operatorname{tr}\rho_z=1\), and
\(\rho_z^2=\rho_z\). Positivity follows directly from
\(v^*\rho_zv=|\langle\psi_z,v\rangle|^2\ge0\).
The purity \(\operatorname{tr}(\rho_z^2)\) is one.

The two coordinate projectors are
\(P_0=\operatorname{diag}(1,0)\) and
\(P_1=\operatorname{diag}(0,1)\). Their four density-matrix blocks are

\[
P_0\rho_zP_0=\frac9{25}|0\rangle\langle0|,
\quad P_1\rho_zP_1=\frac{16}{25}|1\rangle\langle1|,
\quad P_0\rho_zP_1=\frac{12}{25}\overline z|0\rangle\langle1|,
\quad P_1\rho_zP_0=(P_0\rho_zP_1)^*.
\]

The diagonal blocks contain the populations. The off-diagonal blocks contain
the coherence between the two declared packets. Adding all four blocks
reconstructs the state exactly. A global phase multiplying both amplitudes
cancels in \(\rho_z\); the relative phase \(z\) remains.

## 2. Change the measurement setting

Write a general qubit density matrix as
\(\rho=\begin{pmatrix}p&c\\\overline c&1-p\end{pmatrix}\).
The Pauli observables and their plus-outcome projectors are

\[
X=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad
Y=\begin{pmatrix}0&-i\\i&0\end{pmatrix},\quad
Z=\begin{pmatrix}1&0\\0&-1\end{pmatrix},
\qquad E_{A,+}=\frac{I+A}{2}.
\]

For each setting \(A\in\{X,Y,Z\}\), the minus effect is
\(I-E_{A,+}\). The Born rule gives

\[
\boxed{p_{X,+}=\frac12+\operatorname{Re}c,\quad
p_{Y,+}=\frac12-\operatorname{Im}c,\quad p_{Z,+}=p.}
\]

For our state, \(c=(12/25)\overline z\), so

\[
p_{X,+}=\frac12+\frac{12}{25}\operatorname{Re}z,
\qquad p_{Y,+}=\frac12+\frac{12}{25}\operatorname{Im}z,
\qquad p_{Z,+}=\frac9{25}.
\]

The sign in the Y formula matters: the upper-right entry is the conjugate
of the lower-left entry. With the displayed convention, a positive imaginary
part of \(z\) increases the Y-plus probability.

| Relative phase \(z\) | X-plus | Y-plus | Z-plus |
|---|---:|---:|---:|
| \(1\) | \(49/50\) | \(1/2\) | \(9/25\) |
| \(i\) | \(1/2\) | \(49/50\) | \(9/25\) |
| \(-1\) | \(1/50\) | \(1/2\) | \(9/25\) |
| \(-i\) | \(1/2\) | \(1/50\) | \(9/25\) |
| \((3+4i)/5\) | \(197/250\) | \(221/250\) | \(9/25\) |

![For five phases, Z-plus stays at 9/25 while X-plus and Y-plus vary as listed in the preceding exact table.](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/quantum-phase-measurement/measurement-comparison.svg)

*Figure 1. One state family measured in three settings. The Python program
generates this diagram and its exact CSV. Bar widths use rounded drawing
coordinates; their fraction labels and the table give the exact values.*

The Hadamard matrix
\(H=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}\)
turns an X measurement into a coordinate measurement because
\(H^*ZH=X\). Thus the coordinate probabilities of \(H|\psi_z\rangle\)
are \((p_{X,+},1-p_{X,+})\). The factors of \(\sqrt2\) cancel when
computing \(H\rho H^*\), allowing exact arithmetic in \(\mathbb Q(i)\)
for all five phases above.

## 3. Forget a coordinate measurement outcome

A selective coordinate measurement returns outcome \(j\) with probability
\(p_j\). Conditional on an outcome of nonzero probability, the state is
\(P_j\rho P_j/p_j\). For this family these conditional states are
\(P_0\) and \(P_1\).

If the outcome is discarded, the channel is

\[
\mathcal D(\rho)=P_0\rho P_0+P_1\rho P_1,
\qquad
\mathcal D(\rho_z)=\begin{pmatrix}9/25&0\\0&16/25\end{pmatrix}.
\]

The Kraus completeness relation is \(P_0^*P_0+P_1^*P_1=I\).
The channel preserves trace and positivity, and
\(\mathcal D^2=\mathcal D\). It deletes the two cross-packet blocks.
Its output purity is

\[
\boxed{\operatorname{tr}(\mathcal D(\rho_z)^2)
=\left(\frac9{25}\right)^2+\left(\frac{16}{25}\right)^2
=\frac{337}{625}.}
\]

For every coordinate-diagonal effect
\(E=\operatorname{diag}(e_0,e_1)\), with \(0\le e_j\le1\),

\[
\operatorname{tr}(E\rho_z)
=e_0\frac9{25}+e_1\frac{16}{25}
=\operatorname{tr}(E\mathcal D(\rho_z)).
\]

That measurement cannot detect the discarded coherence. An X or Y
measurement can: after dephasing, both plus probabilities become \(1/2\).

This gives an exact recovery obstruction. The states \(\rho_1\) and
\(\rho_i\) have the same dephased output, but their X-plus probabilities
are \(49/50\) and \(1/2\). A function of that output alone cannot return
both answers. Z probabilities remain recoverable from it.

## 4. Retain a controlled amount of coherence

Let \(0\le t\le1\) and define

\[
\mathcal D_t=t\,\operatorname{id}+(1-t)\mathcal D,
\qquad
\mathcal D_t(\rho)=\begin{pmatrix}p&tc\\t\overline c&1-p\end{pmatrix}.
\]

Here \(t\) is the **retained coherence**, rather than the probability of
performing a measurement. An independent implementation is the random
phase-flip channel

\[
\mathcal D_t(\rho)=\frac{1+t}{2}\rho+
\frac{1-t}{2}Z\rho Z.
\]

The weights are nonnegative and sum to one; the corresponding Kraus
operators are \(\sqrt{(1+t)/2}\,I\) and
\(\sqrt{(1-t)/2}\,Z\). Multiplication of the two off-diagonal entries
verifies the formula directly. In particular,
\(\mathcal D_s\mathcal D_t=\mathcal D_{st}\).

For the family \(\rho_z\), direct matrix multiplication gives

\[
\boxed{\operatorname{tr}(\mathcal D_t(\rho_z)^2)
=\frac{337+288t^2}{625}.}
\]

For a matrix \(A\), define
\(\|A\|_{\mathrm{HS}}^2=\operatorname{tr}(A^*A)\). The lost part is
entirely off diagonal, giving

\[
\|\rho_z-\mathcal D_t(\rho_z)\|_{\mathrm{HS}}^2
=\frac{288}{625}(1-t)^2.
\]

For \(z=1\), selected exact checkpoints are:

| Retained coherence \(t\) | X-plus | Y-plus | Purity |
|---:|---:|---:|---:|
| \(0\) | \(1/2\) | \(1/2\) | \(337/625\) |
| \(1/2\) | \(37/50\) | \(1/2\) | \(409/625\) |
| \(1\) | \(49/50\) | \(1/2\) | \(1\) |

The [browser experiment](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-dephasing)
plots nine rational values of \(t\) and exports their exact fractions.

## 5. Recover the density matrix from three settings

Solving the probability equations in section 2 gives

\[
\boxed{\rho=
\begin{pmatrix}
p_{Z,+}&p_{X,+}-\frac12+i(\frac12-p_{Y,+})\\
p_{X,+}-\frac12-i(\frac12-p_{Y,+})&1-p_{Z,+}
\end{pmatrix}.}
\]

For \(z=(3+4i)/5\), the measured triple
\((197/250,221/250,9/25)\) reconstructs

\[
\rho=\begin{pmatrix}
9/25&(36-48i)/125\\
(36+48i)/125&16/25
\end{pmatrix}.
\]

These are three alternative measurement settings on identically prepared
copies. They are not three simultaneous outcomes on one qubit. Arbitrary
noisy triples also need not produce a positive matrix; the exact data here
come from the stated density matrices.

If a known \(t>0\) was applied first, ideal tomography reconstructs
\(\mathcal D_t(\rho)\), and division of its off-diagonal entries by \(t\)
recovers the original entries algebraically. Measurement error in those
entries is amplified by \(1/t\). At \(t=0\), division is impossible and
the two-state obstruction in section 3 applies.

This algebraic inverse on the channel's image is not a physical recovery
channel on arbitrary input states. For example, at \(t=1/2\), doubling the
coherence of \(|+\rangle\langle+|\) would give

\[
A=\begin{pmatrix}1/2&1\\1&1/2\end{pmatrix},
\qquad (1,-1)A(1,-1)^{\mathsf T}=-1<0.
\]

The output would fail positivity. This particular pure input is outside
the image of \(\mathcal D_{1/2}\) on density matrices.

## 6. Operation order changes the answer

Use \(z=1\). Changing basis before dephasing gives

\[
\mathcal D(H\rho_1H^*)=
\begin{pmatrix}49/50&0\\0&1/50\end{pmatrix}.
\]

Dephasing before changing basis gives

\[
H\mathcal D(\rho_1)H^*=
\begin{pmatrix}1/2&-7/50\\-7/50&1/2\end{pmatrix}.
\]

A final coordinate measurement has outcome-0 probability \(49/50\) in
the first experiment and \(1/2\) in the second. The difference is
\(12/25\). Changing the measurement setting after the phase was removed
cannot recover the original interference.

## 7. A coherent record can be uncomputed

Introduce a second qubit, initially \(|0\rangle\), and use system-first
address order \(00,01,10,11\). A controlled-NOT from the system to the
record sends

\[
|\psi_z\rangle|0\rangle\longmapsto
|\Omega_z\rangle=\frac35|00\rangle+\frac45z|11\rangle.
\]

The joint state remains pure and retains cross entries between addresses
\(00\) and \(11\). Its reduced system state is
\(\operatorname{tr}_{\mathrm{record}}|\Omega_z\rangle\langle\Omega_z|
=\mathcal D(\rho_z)\). Partial trace ignores the record; it does not erase
the joint coherence. If both qubits remain coherently accessible, applying
the same controlled-NOT again returns
\(|\psi_z\rangle|0\rangle\).

If the record has instead been measured in its coordinate basis and only
the classical outcome is retained, the joint density matrix is

\[
\frac9{25}|00\rangle\langle00|
+\frac{16}{25}|11\rangle\langle11|.
\]

Applying controlled-NOT now produces
\(\mathcal D(\rho_z)\otimes|0\rangle\langle0|\). The classical label
tells us which branch occurred, but contains no relative phase. Restoring
that phase would require coherent access to all relevant degrees of
freedom carrying the record. Uncomputation of the two qubits alone no
longer supplies it.

## 8. Refine the packets and see which coherence disappears

For a separate two-qubit example, use
\(|\Phi^+\rangle=(|00\rangle+|11\rangle)/\sqrt2\). Its density matrix
has four entries equal to \(1/2\), at \((00,00),(00,11),(11,00),(11,11)\).

The parity packets are

\[
P_{\mathrm{even}}=|00\rangle\langle00|+|11\rangle\langle11|,
\qquad
P_{\mathrm{odd}}=|01\rangle\langle01|+|10\rangle\langle10|.
\]

The state lies entirely in the even packet. Forgetting a parity-measurement
outcome therefore leaves it unchanged, with purity one. Its coherence
between \(00\) and \(11\) is **within** that packet.

Refine the measurement into four singleton-address projectors and forget
their outcomes. Now the same coherence is between distinct packets and is
deleted. The result is

\[
\frac12|00\rangle\langle00|+\frac12|11\rangle\langle11|,
\qquad \text{purity }\frac12.
\]

Declaring finer coordinates while retaining all matrix blocks is reversible.
Performing the finer measurement and discarding its outcome is a different
operation. This example makes the distinction explicit.

## Reproduce the calculation

Download the [standalone program](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/quantum-phase-measurement/quantum_phase_measurement.py)
and run it with Python 3.10 or later. It uses only the standard library.

```text
python -B quantum_phase_measurement.py
python -B quantum_phase_measurement.py --output quantum-results
```

<!-- expected-output -->
```text
Coordinate probabilities: 9/25, 16/25
X-plus, phase 1: 49/50; phase i: 1/2
Y-plus, phase 1: 1/2; phase i: 49/50
Purity: original 1; dephased 337/625; half coherence 409/625
Order witness, outcome 0: 49/50 versus 1/2
Coherent record: reversible; classical record: phase lost
Bell purity: parity packets 1; individual addresses 1/2
PASS: 1284 exact cases
```

The suite covers 182 pure states formed from rational circle parameters,
910 partial-channel cases, 182 coherent/classical record comparisons, and
10 fixed controls. It uses direct matrix products and independent
random-unitary channel formulas. These finite checks accompany the hand
derivations; they are not a proof about all quantum systems or a replay of
the collection's Lean evidence.

[Measurement settings CSV](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/quantum-phase-measurement/measurement-settings.csv) ·
[Partial dephasing CSV](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/quantum-phase-measurement/partial-dephasing.csv) ·
[Exact results JSON](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/quantum-phase-measurement/results.json) ·
[Revision and SHA-256 source record](https://KomorebiP.github.io/Operation-KOMOREBI/downloads/quantum-phase-measurement/source-record.json)

## Papers, written proofs, and scope

The starting state is the one in [hand-worked example 17](../examples/17_QUANTUM_MEASUREMENT.md).
[Paper VII's measurement and channel section](../../papers/paper-vii/current/editable/traditional/parts/01_finite_core.tex#L670)
states the block-diagonal measurement-invariance result and defines Kraus
transfer. The diagonal-effect calculation in section 3 is its explicit
two-dimensional instance. The same source distinguishes cross-packet
coherence from coherence inside a packet, as used in section 8.

[Paper VII: reading, written proofs, Lean coverage, code, and evidence](../works/paper-vii.md) ·
[Quantum and Circuits book and its recorded coverage](../works/monographs-quantum-and-circuits.md) ·
[Recovery from a summary](RECOVERY.md) · [Physics collection](../PHYSICS_COLLECTION.md#quantum-phase) ·
[All demonstrations](../DEMONSTRATIONS.md)

This walkthrough establishes only the displayed finite matrix identities
and their stated elementary generalizations. It makes no new theorem,
physical realization, continuum-limit, or formal-verification claim.
