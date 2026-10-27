# Arithmetic Becomes Interference

## One exact bridge between number theory, signals, and quantum states

A set of four integers can be represented as a pattern of waves. Those waves add to an integer-valued signal. A Fourier transform recovers the original four integers as the signal's exact spectral support. After normalization, the same calculation describes a quantum state and the probabilities of its measurement.

This is not a visual analogy. Each passage below is an explicit map, with its assumptions and normalization stated. The ingredients are classical. Their role here is to make the transport language of Komorebi tangible. The link to the manuscript is Proposition 21.11 of *Stratified Universality for Resolved Representations*, which constructs rational cyclic projectors from Ramanujan sums. [K1]

### Step 1. Start with an arithmetic selection

Work modulo $12$. Two integers are coprime when their greatest common divisor is $1$. The coprime residues are

$$
U_{12}=\{a\in\{0,\ldots,11\}:\gcd(a,12)=1\}=\{1,5,7,11\}.
$$

Put $\zeta=e^{2\pi i/12}$. The phase $\zeta^a$ returns to $1$ after exactly $12/\gcd(a,12)$ powers: the first return is the least positive $t$ for which $12$ divides $at$. Thus the four selected residues label precisely the primitive twelfth roots of unity. An arithmetic condition has selected waves with exact period $12$.

### Step 2. Add the selected waves

For each integer sample index $n$, define the Ramanujan sum

$$
c_{12}(n)=\zeta^n+\zeta^{5n}+\zeta^{7n}+\zeta^{11n}.
$$

This is the standard sum of powers of primitive roots of unity. [M1] Pairing conjugate terms gives a real expression,

$$
c_{12}(n)=2\cos(\pi n/6)+2\cos(5\pi n/6).
$$

Over one period the samples are exactly

$$
\bigl(c_{12}(0),\ldots,c_{12}(11)\bigr)=(4,0,2,0,-2,0,-4,0,-2,0,2,0).
$$

At $n=0$, all four phases agree and the sum is $4$. At $n=1$, they cancel. At $n=6$, all four equal $-1$, giving $-4$. The negative samples are essential: they record destructive and constructive interference, not a plotting convention.

PAGEBREAK

### Step 3. Prove that the samples are integers

Cancellation explains the picture, but it does not by itself establish integrality for every modulus. For any positive integer $q$, let $U_q$ be its coprime residue set. The Möbius function $\mu(d)$ is $0$ if a prime square divides $d$, and otherwise $(-1)^r$ when $d$ is a product of $r$ distinct primes. In particular $\mu(1)=1$.

The coprimality indicator has the identity

$$
\mathbf 1_{\gcd(a,q)=1}=\sum_{d\mid\gcd(a,q)}\mu(d).
$$

Indeed, if the greatest common divisor has $r>0$ distinct prime factors, the sum is $(1-1)^r=0$. If it is $1$, the sum is $1$. Substitute this identity into the phase sum and write $a=db$:

$$
c_q(n)=\sum_{d\mid q}\mu(d)\sum_{b=0}^{q/d-1}e^{2\pi i bn/(q/d)}
       =\sum_{\substack{d\mid q\\(q/d)\mid n}}\mu(d)\frac qd.
$$

The inner sum is a geometric series. It equals $q/d$ when all its phases agree, and zero otherwise. Relabeling $e=q/d$ yields the classical divisor formula [M1],

$$
\boxed{c_q(n)=\sum_{e\mid\gcd(q,n)}e\,\mu(q/e)\in\mathbb Z.}
$$

For example, $c_{12}(2)=\mu(12)+2\mu(6)=2$, while $c_{12}(4)=\mu(12)+2\mu(6)+4\mu(3)=-2$. Every displayed sample can therefore be checked using integers alone.

### Step 4. Prove what the Fourier transform sees

Fix the classical discrete Fourier transform convention

$$
\widehat{x}(k)=\sum_{n=0}^{q-1}x(n)e^{-2\pi i kn/q}.
$$

Substituting the definition of $c_q$ and interchanging two finite sums gives

$$
\widehat{c_q}(k)=\sum_{a\in U_q}\sum_{n=0}^{q-1}e^{2\pi i(a-k)n/q}
               =q\,\mathbf 1_{\gcd(k,q)=1}.
$$

The last equality is character orthogonality: the inner sum is $q$ if $a=k$ modulo $q$, and $0$ otherwise. Thus $\widehat{c_{12}}$ equals $12$ exactly at $1,5,7,11$. The arithmetic selection has not been guessed from a numerical spectrum. It has been recovered by an exact identity.

PAGEBREAK

### Step 5. Turn the arithmetic signal into an exact filter

A signal is now any vector $x\in\mathbb C^{12}$, with indices interpreted modulo $12$. Define circular convolution and the operator $P$ by

$$
(Px)(n)=\frac1{12}\sum_{m=0}^{11}c_{12}(n-m)x(m),
\qquad P_{nm}=\frac{c_{12}(n-m)}{12}.
$$

Every matrix entry is rational. Step 4 and the convolution theorem show that

$$
\widehat{Px}(k)=\mathbf 1_{k\in U_{12}}\,\widehat{x}(k).
$$

So $P$ retains precisely the four selected Fourier modes and removes the others. This is a genuine signal-processing construction, not just a relabeling of a sequence. Ramanujan subspaces, projection methods, and filter banks have an established signal-processing literature. [M2]

For a matrix formulation, define the positive-sign unitary Fourier matrix

$$
F_{na}=\frac1{\sqrt{12}}e^{2\pi i na/12},
\qquad D=\operatorname{diag}(\mathbf 1_{a\in U_{12}}).
$$

Orthogonality gives $F^\dagger F=I$. Direct multiplication gives the exact transport identity

$$
\boxed{P=FDF^\dagger,\qquad P^2=P,\qquad P^\dagger=P.}
$$

Here $\dagger$ denotes conjugate transpose. In frequency coordinates, $P$ is simply a diagonal selector. In sample coordinates, it is a rational convolution matrix. Its rank is $4$, because $D$ has four ones on its diagonal. Its trace gives the same answer: $12c_{12}(0)/12=4$.

**A filter with something to remove.** Consider the integer-valued test signal

$$
x(n)=c_{12}(n)+3\cos(\pi n/2)+2.
$$

The cosine occupies modes $3$ and $9$, and the constant occupies mode $0$. None is coprime to $12$. Therefore

$$
Px=c_{12},\qquad (I-P)x=3\cos(\pi n/2)+2.
$$

The two components are orthogonal. Over twelve samples their squared norms are $48$ and $102$, and the input energy is $150=48+102$. These values are reproduced exactly by the supplied verifier. The retained component, discarded component, reconstruction, and invariant energy balance are all explicit.

PAGEBREAK

### Step 6. Make the quantum connection literal

A collection of complex phases is not, by itself, a quantum experiment. To make the connection precise we need a normalized state, a unitary operation, and a measurement rule. A finite quantum state is a unit vector whose squared amplitude magnitudes sum to $1$. [M4]

In a twelve-dimensional Hilbert space with orthonormal basis $\left\lvert 0\right\rangle,\ldots,\left\lvert 11\right\rangle$, prepare the uniform coprime state

$$
\left\lvert u\right\rangle=\frac{\left\lvert 1\right\rangle+\left\lvert 5\right\rangle+\left\lvert 7\right\rangle+\left\lvert 11\right\rangle}{2}.
$$

Its norm is $1$, because it has four amplitudes of magnitude $1/2$. Apply the unitary Fourier transform defined in Step 5,

$$
F\left\lvert a\right\rangle=\frac1{\sqrt{12}}\sum_{n=0}^{11}e^{2\pi i an/12}\left\lvert n\right\rangle.
$$

This uses the positive-sign convention of the quantum Fourier transform, generalized here to dimension $12$. [M3] Linearity now gives

$$
\boxed{\left\lvert \psi\right\rangle=F\left\lvert u\right\rangle=\frac1{\sqrt{48}}\sum_{n=0}^{11}c_{12}(n)\left\lvert n\right\rangle.}
$$

The arithmetic signal has become the amplitude vector of a quantum state. Its normalization is visible directly: $4^2+2^2+(-2)^2+(-4)^2+(-2)^2+2^2=48$. Applying $F^\dagger$ recovers $\left\lvert u\right\rangle$ exactly.

![Figure 1. One state in two bases. Circles are the signed amplitudes of the Ramanujan signal state. Squares are the amplitudes after the inverse quantum Fourier transform. The shared horizontal labels refer to different bases before and after the transform. Heights are amplitudes, not measurement probabilities. Every plotted value follows from the identities above.](arithmetic_interference.png){width=6.3in}

PAGEBREAK

### Step 7. Distinguish interference from measurement

The Born rule assigns probability $\left\lvert\alpha_n\right\rvert^2$ to outcome $n$ for a normalized state with amplitudes $\alpha_n$. [M4] Before applying $F^\dagger$, the probabilities are therefore $c_{12}(n)^2/48$. After applying it, each of the four coprime labels has probability $1/4$.

| Label | $c_{12}(n)$ | Before inverse QFT | After inverse QFT |
|:---:|---:|:---:|:---:|
| 0 | 4 | $1/3$ | $0$ |
| 1 | 0 | $0$ | $1/4$ |
| 2 | 2 | $1/12$ | $0$ |
| 3 | 0 | $0$ | $0$ |
| 4 | $-2$ | $1/12$ | $0$ |
| 5 | 0 | $0$ | $1/4$ |
| 6 | $-4$ | $1/3$ | $0$ |
| 7 | 0 | $0$ | $1/4$ |
| 8 | $-2$ | $1/12$ | $0$ |
| 9 | 0 | $0$ | $0$ |
| 10 | 2 | $1/12$ | $0$ |
| 11 | 0 | $0$ | $1/4$ |

The two probability columns refer to alternative measurement procedures on fresh preparations. Measuring first would generally destroy the coherent state needed for the second procedure. One run returns one label, not the entire Fourier spectrum.

**Why the negative amplitudes matter.** Define a different normalized state by replacing every amplitude of $\left\lvert \psi\right\rangle$ with its absolute value:

$$
\left\lvert \chi\right\rangle=\frac1{\sqrt{48}}\sum_{n=0}^{11}\left\lvert c_{12}(n)\right\rvert\,\left\lvert n\right\rangle.
$$

The states $\left\lvert \chi\right\rangle$ and $\left\lvert \psi\right\rangle$ have identical probabilities in the original sample basis. Nevertheless, their Fourier-basis measurements disagree completely on the arithmetic selection. Since $c_{12}(n+6)=-c_{12}(n)$, the absolute-value signal has period $6$. Pairing its samples $n$ and $n+6$ in the inverse transform produces the factor $1+(-1)^k$, which vanishes for every odd $k$.

All four coprime labels are odd. Consequently,

$$
\Pr_{F^\dagger\psi}(k\in U_{12})=1,
\qquad \Pr_{F^\dagger\chi}(k\in U_{12})=0.
$$

Identical initial histograms do not imply identical coherent states. Relative phase carries information that becomes observable after a change of basis. This is the substantive quantum content missing from a picture of roots of unity alone.

PAGEBREAK

### Step 8. Identify the Komorebi structure precisely

The common structure is now an operator, not a loose resemblance:

$$
\text{arithmetic selection }D
\quad\longleftrightarrow\quad
\text{signal projector }P=FDF^\dagger
\quad\longleftrightarrow\quad
\text{quantum spectral measurement}.
$$

For quantum states, the pair $\{P,I-P\}$ defines a projective measurement. On input $\left\lvert x\right\rangle$, the selected outcome occurs with probability $\left\lVert P\left\lvert x\right\rangle\right\rVert^2$. When this probability is nonzero, the corresponding state is $P\left\lvert x\right\rangle/\left\lVert P\left\lvert x\right\rangle\right\rVert$. Unlike $F$, the projector is not a reversible unitary operation: a rank-four selector cannot preserve every vector in a twelve-dimensional space.

The arithmetic rationality is also structural. In the group algebra of $C_N=\langle g\rangle$, with $g^N=1$, the split Fourier idempotents are

$$
e_j=\frac1N\sum_{\ell=0}^{N-1}\zeta_N^{-j\ell}g^\ell.
$$

Changing the chosen primitive root by a Galois automorphism sends $e_j$ to $e_{aj}$ for a unit $a$ modulo $N$. Summing over a complete orbit produces a rational operator. Proposition 21.11 of the Komorebi manuscript states this as [K1]

$$
E_d=\sum_{N/\gcd(N,j)=d}e_j
   =\frac1N\sum_{\ell=0}^{N-1}c_d(\ell)g^\ell,
\qquad d\mid N.
$$

Our $P$ is the $N=d=12$ specialization in the cyclic shift representation. The sum is rational even though its separate phase components need not be. For all divisors $d$ of $12$, the analogous operators satisfy

$$
P_dP_e=\delta_{de}P_d,
\qquad \sum_{d\mid12}P_d=I.
$$

Thus the six order classes $1,2,3,4,6,12$ give a complete, exact decomposition of every twelve-sample signal. The twelve-order component has rank $\varphi(12)=4$. These are character-order projectors, not coefficient-residue selectors on formal power series. The manuscript explicitly preserves that distinction in Boundary 21.12. [K1]

For the essay, this is the point of the example: coprimality, a rational filter, and a quantum measurement can be different realizations of the same selector. The bridges specify what is preserved, what is reversible, and what is discarded. No unspecified arrow between two lists of coefficients is needed.

PAGEBREAK

## Evidence, boundaries, and research questions

### What was checked for this edition

The accompanying Python verifier passes **3,003 exact assertions**. It checks the twelve phase sums and Fourier coefficients in the exact ring $\mathbb Z[z]/(z^4-z^2+1)$, rather than rounding floating-point exponentials. It checks every entry of $P^2=P$ and $P^T=P$, the integer test-signal decomposition, the six divisor projectors and their completeness, and the phase-sensitivity example.

It also runs finite arithmetic regressions for moduli $2$ through $64$. Separately, numerical checks test Fourier unitarity, state preparation, inversion, and projector transport. Their largest reported matrix or state residual is below $2\times10^{-15}$, against a declared tolerance of $10^{-12}$. The exact checks and numerical checks are recorded separately in `verification.json`.

The finite tests are implementation evidence. The general identities are justified by the algebraic derivations above. **No new Lean compilation or quantum-hardware experiment was performed for this edition.** The retrieved manuscript establishes source lineage, not a fresh compiler certificate or an independent novelty assessment.

### What this example does not establish

The construction uses a twelve-dimensional system. It is not the ordinary four-qubit, sixteen-point QFT. One mathematical embedding into four qubits is the unitary $F_{12}\oplus I_4$, but this edition supplies neither its gate synthesis nor a resource bound. Preparing the coprime state, implementing the transform, preserving coherence, and collecting statistics all have costs. No quantum speedup, factoring algorithm, or new fundamental law of physics follows from the example.

Nor are Ramanujan sums or Fourier projection new discoveries of Komorebi. They are classical ingredients with established arithmetic and signal-processing antecedents. The example substantiates a realization of the framework's transport vocabulary. It does not, by itself, establish the framework's novelty or universality.

### What the example suggests asking next

A useful next mathematical question is which selectors remain exactly representable over a chosen coefficient field when individual phase components do not. A signal-processing question is how the projector behaves under incomplete sampling or a change of window. A quantum-information question is whether particular arithmetic selectors admit efficient state preparation and measurement. Each question has a separate correctness condition and a separate cost model. Their shared operator language makes comparisons possible without making their difficulties identical.

### Sources for the worked example

**[M1]** NIST Digital Library of Mathematical Functions, §27.10, especially equations 27.10.2–27.10.5. Finite Fourier series, Ramanujan sums, and the Möbius divisor formula. https://dlmf.nist.gov/27.10

**[M2]** Caltech, *The Ramanujan Periodicity Project*. Primary project description of Ramanujan subspaces, projection techniques, and filter banks. https://systems.caltech.edu/dsp/students/srikanth/Ramanujan/

**[M3]** IBM Quantum Documentation, *QFT*. Definition and positive-sign phase convention for the qubit Fourier transform. The twelve-dimensional extension used here is defined explicitly in Step 6. https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QFT

**[M4]** IBM Quantum Learning, *Quantum information*, sections on state vectors, standard-basis measurement, and unitary operations. https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/quantum-information

**[K1]** Komorebi P., *Stratified Universality for Resolved Representations*, v1.16.0, Block 16, Proposition 21.11 and Boundary 21.12, printed p. 189. Library source: `Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.pdf`; associated text: `block16_section.tex`. Internal manuscript, inspected for this edition. Its validation section distinguishes regression checks from proof and acknowledges classical antecedents.
