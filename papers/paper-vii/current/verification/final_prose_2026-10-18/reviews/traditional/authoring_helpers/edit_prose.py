from pathlib import Path
import hashlib
import json
import difflib
import re

ROOT = Path("/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Final_2026-10-18")
BASE = Path("/workspace/scratch/be33f0b6c391/output/Komorebi_Paper_VII_Complete_Proofread_2026-10-18")
OUT = Path("/workspace/scratch/be33f0b6c391/tmp/p7_final_traditional_prose")
OUT.mkdir(parents=True, exist_ok=True)
edits = []

def add(file, category, before, after):
    edits.append({"file": file, "category": category, "before": before, "after": after})

C = "editable/traditional/parts/01_finite_core.tex"
S = "editable/traditional/parts/02_strengthened.tex"
E = "editable/traditional/monograph_examples.tex"

add(C, "natural prose", r"Unless a zero-dimensional boundary case is stated explicitly, quantum state spaces are nonzero finite-dimensional complex Hilbert spaces.",
    r"Unless the zero space is explicitly included as a boundary case, quantum state spaces are nonzero complex Hilbert spaces of finite dimension.")
add(C, "unnecessary compound", r"All operator norms in the analytic estimates are induced by the Hilbert-space norm, not the entrywise maximum norm or the Frobenius norm.",
    r"All operator norms in the analytic estimates are induced by the norm on the Hilbert space. The estimates do not use the entrywise maximum norm or the Frobenius norm.")
add(C, "full caption prose", r"The quantum realization of the common seed-calculus operator chain. The same finite packet language is used for states, gates, Hamiltonians, channels, geometric projectors, and effective dynamics.",
    r"The diagram shows the quantum realization of the common sequence of operators in the seed calculus. The same finite packet language describes states, gates, Hamiltonians, channels, geometric projectors, and effective dynamics.")
add(C, "semicolon", r"An empty block family represents the zero space and has seed rank zero; an empty maximum below is assigned the value zero.",
    r"An empty block family represents the zero space and has seed rank zero. The maximum over an empty block family is also assigned the value zero.")
add(C, "unnecessary compound", r"Under the coefficient-matrix identification, $(A\otimes I_m)\psi$ corresponds to $AC$.",
    r"Under the identification by coefficient matrices, $(A\otimes I_m)\psi$ corresponds to $AC$.")
add(C, "semicolon", r"The reduced positive operator on $B$ is $\rho_B=\Tr_A(\ket\psi\bra\psi)$; normalization of $\psi$ is immaterial to its support.",
    r"The reduced positive operator on $B$ is $\rho_B=\Tr_A(\ket\psi\bra\psi)$. Normalization of $\psi$ does not affect its support.")
add(C, "full explanation", r"This is an algebraic span statement for arbitrary local operators. It is not a claim that a normalized unitary gate orbit contains every vector, nor a deterministic protocol for preparing arbitrary remote states. Entanglement controls the multiplicity support appearing in that algebraic span.",
    r"The conclusion concerns the algebraic span obtained from arbitrary local operators. A normalized unitary gate orbit need not contain every vector, and the span statement does not supply a deterministic protocol for preparing arbitrary remote states. Entanglement controls the multiplicity support appearing in that algebraic span.")
add(C, "historical numerical scope", r"The implementation generated all eight computational basis states from $\ket{000}$ using the three local $X$ address operators. The measured orbit rank was $8/8$.",
    r"The original numerical implementation generated all eight computational basis states from $\ket{000}$ using the three local $X$ address operators. It reported an orbit rank of $8/8$.")
add(C, "natural proof prose", r"one obtains $P_jP_k=\delta_{jk}P_j$. Summing over $j$ cancels every term indexed by $r\ne0$ and retains the $r=0$ term, proving completeness.",
    r"we obtain $P_jP_k=\delta_{jk}P_j$. Summing over $j$ cancels every term indexed by $r\ne0$ and retains the $r=0$ term, which proves completeness.")
add(C, "natural proof prose", r"The stated coarse families partition their address set by total residue.",
    r"Grouping the fine addresses by their total residue partitions the full address set.")
add(C, "unnecessary compound", r"For three qubits, the local computational projectors were grouped by Hamming-weight parity.",
    r"For three qubits, the local computational projectors were grouped by the parity of their Hamming weight.")
add(C, "semicolon", r"For the empty circuit $m=0$, set $U=I$; its boundary block is $P_\beta P_\alpha=\delta_{\beta\alpha}P_\alpha$.",
    r"For the empty circuit $m=0$, set $U=I$. Its boundary block is $P_\beta P_\alpha=\delta_{\beta\alpha}P_\alpha$.")
add(C, "full proof sentence", r"The second identity is analogous.",
    r"For the second identity, sum over the source packets and use unitarity in the reverse order.")
add(C, "unnecessary compounds", r"The Bell-state residual and the complete parity-path reconstruction residual were both $0$ in the numerical implementation.",
    r"The original numerical implementation reported residuals of $0$ for both the Bell state and its complete reconstruction from parity paths.")
add(C, "unnecessary compound", r"The parity-resolved Hamiltonian is exactly block diagonal after the even and odd basis vectors are grouped.",
    r"The Hamiltonian becomes exactly block diagonal when the even and odd basis vectors are grouped.")
add(C, "natural proof prose", r"Differentiation of the actual exponential gives",
    r"Differentiating the exponential gives")
add(C, "full caption prose", r"A parity-breaking perturbation creates nonzero transfer between the packets, while the measured leakage remains below the commutator bound.",
    r"A perturbation that breaks parity creates nonzero transfer between the packets. The measured leakage remains below the commutator bound.")
add(C, "unnecessary compounds", r"For the parity-preserving Hamiltonian, the off-packet block norm and maximum measured leakage were both $0$. After adding a parity-breaking $X\otimes I$ perturbation, the maximum leakage was approximately $0.79196$, and the maximum violation of the proved bound was $0$.",
    r"For the Hamiltonian that preserves parity, the norm of the block between distinct packets and the maximum measured leakage were both $0$. Adding an $X\otimes I$ perturbation broke parity and produced a maximum leakage of approximately $0.79196$. The maximum violation of the proved bound remained $0$.")
add(C, "unnecessary compound", r"The moving-frame equation closes to numerical precision only when the connection term is retained.",
    r"The equation in the moving frame holds to numerical precision only when the connection term is retained.")
add(C, "historical numerical scope", r"The complete moving-frame equation had residual $1.0645\times10^{-10}$, while omitting the connection produced residual $0.7000$.",
    r"The reported residual for the complete equation in the moving frame was $1.0645\times10^{-10}$. Omitting the connection increased the residual to $0.7000$.")
add(C, "natural explanation", r"The connection is the infinitesimal transport operator of the moving packet frame. It is determined by the packet family itself, without choosing a basis inside any packet.",
    r"The connection generates infinitesimal transport of the moving packet frame. The packet family determines it directly, so its construction does not require a basis inside any packet.")
add(C, "unnecessary compounds", r"No global frame, globally constant rank or commuting-vector-field assumption is imposed. The geometric formalization concerns real smooth structures, not complex-analytic manifolds or boundary extensions.",
    r"No global frame or globally constant rank is required, and the vector fields need not commute. The geometric formalization concerns real smooth structures. It does not cover complex analytic manifolds or extensions to a boundary.")
add(C, "natural proof prose", r"This expression is alternating, bilinear in the tangent vectors and range-preserving. The ordinary chain rule and the Lie-bracket transformation law identify the local calculations on chart overlaps, yielding the global formula.",
    r"This expression is alternating and bilinear in the tangent vectors, and it preserves the range. The ordinary chain rule and the transformation law for the Lie bracket make the local calculations agree on chart overlaps, which gives the global formula.")
add(C, "formal scope prose", r"This explicit worked calculation is not a separate entry in the 19-item Lean register.",
    r"This explicit calculation is not a separate entry among the 19 items in the Lean register.")
add(C, "full caption prose", r"Finite-difference evaluation of the Bloch projector curvature against the exact density $\frac12\sin\theta$.",
    r"The curvature of the Bloch projector, evaluated by finite differences, is compared with the exact density $\frac12\sin\theta$.")
add(C, "unnecessary compound", r"The maximum Bloch-curvature residual was $2.0803\times10^{-11}$.",
    r"The maximum residual for the Bloch curvature was $2.0803\times10^{-11}$.")
add(C, "natural explanation", r"This theorem says exactly what coherence a declared measurement can and cannot see. Coherence between different packets is invisible to every packet-diagonal observable, while coherence inside a packet remains available.",
    r"The theorem identifies which coherences a declared measurement can detect. Observables that are diagonal in the packet decomposition cannot detect coherence between distinct packets. Coherence within a packet remains available to such observables.")
add(C, "complete subsection introduction", "\\subsection{Kraus transfer}\n\n",
    "\\subsection{Kraus transfer}\n\nA quantum channel can transfer both populations and coherences between packet addresses. A Kraus representation describes this transfer by summing the contributions of its individual branches. The normalization of those branches ensures that the total trace is preserved.\n\n")
add(C, "unnecessary compounds", r"For $\gamma=0.23$, the Kraus completeness and output-trace residuals were $0$. The computed output from $\ket1\bra1$ was $\diag(0.23,0.77)$. Packet dephasing changed no computational-basis measurement probability in the Bell-state test.",
    r"For $\gamma=0.23$, the residuals for Kraus completeness and the output trace were $0$. The computed output from $\ket1\bra1$ was $\diag(0.23,0.77)$. In the Bell state test, packet dephasing left every measurement probability in the computational basis unchanged.")
add(C, "unnecessary compounds", r"are the code-level obstruction packets: if they retain logical-state information beyond one scalar multiple of $P$, the environment can distinguish logical states and exact correction is impossible.",
    r"are the obstruction packets on the code. If they retain information about the logical state beyond one scalar multiple of $P$, the environment can distinguish logical states and exact correction is impossible.")
add(C, "natural explanation", r"For precision, a complete recovery is a Kraus map",
    r"We call a recovery complete when it is a Kraus map")
add(C, "unnecessary compounds", r"The zero-code and empty-error-family cases are included. An empty family is not a trace-preserving channel on a nonzero ambient space.",
    r"The zero code and an empty error family are included. An empty family cannot define a channel that preserves trace on a nonzero ambient space.")
add(C, "unnecessary compound", r"The one-dimensional case is immediate, and the zero-code case is vacuous.",
    r"The one-dimensional case is immediate, and the claim is vacuous for the zero code.")
add(C, "unnecessary compound", r"Every recovery branch of a coherent combination is therefore scalar on the code, while its unused-space branch vanishes.",
    r"Every recovery branch of a coherent combination is therefore scalar on the code, while the branch for the unused space vanishes.")
add(C, "unnecessary compounds", r"The Knill--Laflamme residual and syndrome-completeness residual were both $0$. A mixed single-bit-flip channel applied to a nontrivial logical superposition was reversed with density-matrix residual $1.0385\times10^{-16}$.",
    r"The residuals for the Knill--Laflamme condition and completeness of the syndrome packets were both $0$. A mixed channel of single bit flip errors, applied to a nontrivial logical superposition, was reversed with a residual of $1.0385\times10^{-16}$ in the density matrix.")
add(C, "unnecessary compounds", r"The block matrix $z-H$ has lower-right block $z-H_{QQ}$.",
    r"The block in the lower right corner of $z-H$ is $z-H_{QQ}$.")
add(C, "unnecessary compounds", r"The assumed invertibility of the lower-right block and of the full matrix implies invertibility of this Schur complement. The upper-left block of the full inverse is its inverse, which is exactly the displayed operator.",
    r"The assumed invertibility of this block and of the full matrix implies that the Schur complement is invertible. The block in the upper left corner of the full inverse is the inverse of that Schur complement, which is exactly the displayed operator.")
add(C, "unnecessary compound", r"Bare truncation drops $\Sigma_P(z)$ and is therefore exact only when the cross-packet coupling vanishes or the self-energy cancels for another stated reason.",
    r"Bare truncation drops $\Sigma_P(z)$ and is therefore exact only when the coupling between packets vanishes or the self-energy cancels for another stated reason.")
add(C, "historical numerical scope", r"For a random six-dimensional Hermitian test, the exact Feshbach residual was $3.2291\times10^{-17}$. The corresponding bare-truncation residual was $1.3091\times10^{-2}$.",
    r"In the reported test with a random Hermitian matrix of dimension six, the exact Feshbach residual was $3.2291\times10^{-17}$. The corresponding residual for bare truncation was $1.3091\times10^{-2}$.")
add(C, "unnecessary compounds", r"Thus the eliminated degrees of freedom are retained as a frequency-dependent self-energy or an exact memory term. For forward evolution the integral is causal. A time-dependent Hamiltonian requires its two-time propagator instead of the stationary exponential used here. This Volterra derivation is not a separate entry in the finite Lean register.",
    r"The influence of the eliminated degrees of freedom is therefore retained in a self-energy that depends on frequency, or equivalently in an exact memory term. For forward evolution the integral is causal. When the Hamiltonian depends on time, the corresponding propagator between two times replaces the stationary exponential used here. This Volterra derivation is not a separate entry in the finite Lean register.")
add(C, "full explanatory prose", r"The entries are an observable algebra, Hilbert space, geometric or Dirac-type operator, packet projectors, fine embedding, coarse reconstruction, physical constraint projector, and transfer operator.",
    r"In order, the entries specify the observable algebra, Hilbert space, geometric or Dirac-type operator, packet projectors, embedding into the fine space, reconstruction onto the coarse space, physical constraint projector, and transfer operator.")
add(C, "natural explanation", r"A left inverse $C_\ell E_\ell=I$ does not by itself assert $C_\ell=E_\ell^*$ or an isometric embedding.",
    r"The left inverse relation $C_\ell E_\ell=I$ alone does not imply $C_\ell=E_\ell^*$ or make the embedding isometric.")
add(C, "full caption prose and semicolon", r"A conjectural nested packet tower for quantum geometry. The diagram is an organizational model; it is not a numerical reconstruction of physical spacetime.",
    r"The diagram organizes a conjectural nested packet tower for quantum geometry. It does not provide a numerical reconstruction of physical spacetime.")
add(C, "full caption prose and semicolon", r"The finite Euclidean volume-transfer kernel. Positivity and semigroup composition are exact finite statements; its gravitational interpretation remains provisional.",
    r"The figure shows the finite Euclidean kernel for volume transfer. Positivity and semigroup composition hold exactly in the finite model. Its gravitational interpretation remains provisional.")
add(C, "semicolon and unnecessary compounds", r"It tends to zero as $\tau\downarrow0$ and, under the stated zero-mode assumption, as $\tau\to\infty$. If a general positive operator has no zero mode, its large-time behavior is instead asymptotic to $2\tau\lambda_{\min}$; the zero-mode conclusion must not be applied to it. A geometric dimension can only be inferred from a stable intermediate window and a controlled refinement limit.",
    r"It tends to zero as $\tau\downarrow0$ and, under the stated assumption of a zero mode, as $\tau\to\infty$. If a general positive operator has no zero mode, its behavior at large times is instead asymptotic to $2\tau\lambda_{\min}$. The conclusion for operators with a zero mode therefore does not apply to that case. Inferring a geometric dimension requires a stable intermediate window and a controlled refinement limit.")
add(C, "unnecessary compound", r"The all-real inequalities $|\sin x|\le|x|$ and $|x-\sin x|\le |x|^3/6$ give",
    r"The inequalities $|\sin x|\le|x|$ and $|x-\sin x|\le |x|^3/6$, which hold for every real argument, give")
add(C, "semicolon and natural prose", r"The estimate holds for every frequency, but its second-order convergence interpretation keeps $k$ fixed while $h\to0$; it is not a uniform small relative error across all grid modes.",
    r"The estimate holds for every frequency. Its interpretation as convergence of second order keeps $k$ fixed while $h\to0$, so it does not assert a uniformly small relative error across all grid modes.")
add(C, "historical numerical scope", r"The observed convergence order was $1.99936$. The maximum error-minus-bound value was negative, so no tested mode violated the theorem.",
    r"The reported convergence order was $1.99936$. For every tested mode, the error was below the bound, so none of those tests violated the theorem.")
add(C, "complete subsection introduction", "\\subsection{One- and two-dimensional plateaus}\n\n",
    "\\subsection{One- and two-dimensional plateaus}\n\nAt intermediate diffusion times, a finite cycle and a finite torus can exhibit plateaus near the dimensions of their underlying geometries. The following figure and numerical certificate show the reported behavior for these two examples. The plateaus occur between the small and large time regimes in which the spectral dimension returns to zero.\n\n")
add(C, "full caption prose", r"Intermediate spectral-dimension windows for a finite cycle and a finite two-dimensional torus. The ultraviolet and infrared departures are finite-size effects, not additional dimensions.",
    r"The curves show intermediate windows of spectral dimension for a finite cycle and a finite two-dimensional torus. Departures in the ultraviolet and infrared reflect the finite size of the models rather than additional dimensions.")
add(C, "semicolon and unnecessary compound", r"These tests recover the expected dimensions of the chosen finite geometries; they do not select a physical quantum-spacetime theory.",
    r"These tests recover the expected dimensions of the chosen finite geometries. They do not select a physical theory of quantum spacetime.")
add(C, "semicolon and unnecessary compound", r"The operator condition is the substantive research target in this edition; the earlier compression-only wording was too weak. A choice of model, dynamics and refinement maps is still needed before this program becomes a fully specified physical existence problem.",
    r"The substantive research target is the operator condition. The earlier condition stated only in terms of compression was too weak. A choice of model, dynamics, and refinement maps is still needed before this program becomes a fully specified physical existence problem.")
add(C, "unnecessary compound", r"Together with consistent Hilbert-space identifications and a proved resolvent convergence criterion, they yield a nontrivial strong-resolvent continuum limit.",
    r"Together with consistent identifications of the Hilbert spaces and a proved resolvent convergence criterion, they yield a nontrivial continuum limit in the strong resolvent sense.")
add(C, "semicolon and unnecessary compounds", r"None of these physical conclusions is established by the exact finite identities. No formal logical-independence theorem is claimed. Exact packet reconstruction is a kinematic and computational advantage; it does not determine the physical action, prove continuum existence, or guarantee the general-relativistic limit.",
    r"The exact finite identities establish none of these physical conclusions, and no formal theorem of logical independence is claimed. Exact packet reconstruction provides a kinematic and computational advantage. It does not determine the physical action, prove existence of the continuum theory, or guarantee the limit of general relativity.")
add(C, "historical evidence scope and semicolons", r"The original manuscript reports CPU experiments and a 22-test suite; it makes no GPU claim. The values below reproduce the original historical report. They are numerical observations and are not counted among the 323 declarations in the selected finite formal checkpoint. The recovered numerical source and raw records accompany the source corpus; the present reading copy distinguishes those observations from mathematical proof. A displayed floating-point residual of zero denotes the reported computation, not an independent proof of exact arithmetic equality.",
    r"The original manuscript reports CPU experiments and a suite of 22 tests. It makes no claim about GPU computation. The values below reproduce that historical report and have not been recomputed for this prose revision. These numerical observations are separate from the 323 declarations in the selected finite formal checkpoint of 6 September 2026. The recovered numerical source and raw records accompany the source corpus. A displayed floating-point residual of zero records the reported computation and does not independently prove equality in exact arithmetic.")
add(C, "connected conclusion prose", r"The quantum realization of the seed calculus can now be stated precisely. A primitive state is addressed by a declared operator grammar; symmetry projectors split the state and every operator into exact packets; circuit products become sums over packet paths; Hamiltonian symmetry and its controlled breaking are visible as diagonal blocks and leakage; moving packets carry a canonical connection and curvature; channels, measurements, and error-correction conditions admit exact packet formulations; and eliminated sectors return through self-energy and memory rather than disappearing.",
    "The quantum realization of the seed calculus begins with a primitive state and a declared operator grammar. Symmetry projectors resolve the state and every operator into exact packets. In these coordinates, circuit products become sums over packet paths, and Hamiltonian symmetry appears as a diagonal block structure. When that symmetry is broken, the resulting transfer is measured by the leakage estimates.\n\nMoving packets carry a canonical connection and curvature. Channels and measurements act on the corresponding operator packets, while the conditions for error correction become statements about compression to the code. Exact elimination retains the influence of hidden sectors through self-energy and memory.")
add(C, "natural conclusion prose", r"What it does not yet provide is the physical continuum theorem. The next decisive results would be anomaly-free refinement, uniform effective-operator control, Lorentzian reconstruction, the Einstein infrared limit, and a positive massless spin-two sector. Those requirements are explicit enough to be tested and too substantial to be replaced by finite numerical resemblance.",
    r"A physical continuum theorem remains open. The next required results are anomaly-free refinement, uniform control of effective operators, Lorentzian reconstruction, the Einstein infrared limit, and a positive massless spin-two sector. Each requires its own hypotheses and proof. Agreement in a finite numerical model cannot replace those arguments.")

add(S, "natural prose", r"Finite dimensional quantum information and operator theory supply the standard background",
    r"Quantum information and operator theory in finite dimensions provide the standard background")
add(S, "full explanation", r"A leakage estimate shows that the relevant off packet coupling is not \(QHP\) alone. It is",
    r"The leakage estimate must account for the motion of the packet itself. The physical coupling \(QHP\) is therefore replaced by")
add(S, "natural prose", r"Density matrices require two packet labels.",
    r"Density matrices require separate packet labels for their output and input coordinates.")
add(S, "natural prose", r"The class of \(PAP\) modulo scalar multiples of \(P\) is the obstruction to making \(A\) invisible inside the code.",
    r"The class of \(PAP\) modulo scalar multiples of \(P\) measures the obstruction to making \(A\) undetectable within the code.")
add(S, "full explanation", r"The geometric part has two finite components. A positive transfer matrix gives a reflection positive Hankel kernel and reconstructs a nonnegative Hamiltonian through its logarithm. A finite Laplacian gives a heat trace and a scale dependent spectral dimension. The article proves fixed time convergence from periodic lattices to the continuum torus. Poisson summation then gives the continuum small time dimension.",
    r"The geometric part develops two finite constructions. A positive transfer matrix gives a reflection positive Hankel kernel, and its logarithm reconstructs a nonnegative Hamiltonian. A finite Laplacian gives a heat trace from which the spectral dimension is defined at each diffusion scale. The article proves convergence from periodic lattices to the continuum torus at every fixed positive diffusion time. Poisson summation then determines the continuum dimension as diffusion time tends to zero.")
add(S, "full explanation", r"The last part gives two bounded continuum tower theorems. Exact compatible finite Hamiltonians define a bounded self adjoint operator on the Hilbert direct limit. A norm summable sequence in a common Hilbert space converges to a bounded self adjoint limit, and its unitary and Euclidean evolutions converge uniformly on bounded time intervals. Reflection positivity and fixed algebraic closure pass to limits under the stated convergence assumptions.",
    r"The last part gives two theorems for towers of bounded Hamiltonians. Exactly compatible finite Hamiltonians with a uniform norm bound define a bounded self adjoint operator on the Hilbert direct limit. When successive bounded self adjoint Hamiltonians on a common Hilbert space have norm summable differences, they converge to a bounded self adjoint limit. Their unitary evolutions, and their Euclidean evolutions under the stated positivity assumption, converge uniformly on bounded time intervals. Reflection positivity and closure with fixed structure coefficients pass to the limit under the stated convergence assumptions.")
add(S, "full proof sentence", r"The Schmidt rank is the rank of the coefficient matrix in any product basis. Apply \cref{strong:thm:orbit_dimension}.",
    r"The Schmidt rank is the rank of the coefficient matrix in any product basis. Substituting that rank into \cref{strong:thm:orbit_dimension} gives the stated orbit dimension.")
add(S, "full proof sentence", r"Conjugation by \(S\) is a star automorphism. Apply it to \(AB\) and \(A^*\).",
    r"Conjugation by \(S\) is a star automorphism. Applying it to \(AB\) adds the two charges, while applying it to \(A^*\) changes the sign of the charge.")
add(S, "natural caption", r"A charge one operator moves each cyclic packet to the next packet and has no other transfer blocks.",
    r"An operator of charge one moves each cyclic packet to the next packet and has no other transfer blocks.")
add(S, "full proof sentence", r"The second identity follows in the same way.",
    r"Summing instead over the source packets and using unitarity in the reverse order gives the second identity.")
add(S, "full proof prose", r"Expand the squared norm and group conjugate cross terms. The norm bound is the triangle inequality. Orthogonality removes every cross term.",
    r"Expanding the squared norm and grouping conjugate cross terms gives the interference formula. The triangle inequality gives the norm bound. When the path outputs are orthogonal, every cross term vanishes and only the individual path probabilities remain.")
add(S, "scientific gate name", r"Starting from \(\ket{00}\), apply a Hadamard gate to the first qubit and then a controlled not gate.",
    r"Starting from \(\ket{00}\), apply a Hadamard gate to the first qubit and then a controlled NOT gate.")
add(S, "complete statement prose", "\\item \\([H,P_a]=0\\) for every \\(a\\)\n\\item \\(P_bHP_a=0\\) whenever \\(a\\neq b\\)\n\\item every packet \\(P_a\\Hcal\\) is invariant under \\(\\e^{-\\ii tH}\\) for every real \\(t\\)",
    "\\item The Hamiltonian commutes with each projector: \\([H,P_a]=0\\) for every \\(a\\).\n\\item Transfer blocks between distinct packets vanish: \\(P_bHP_a=0\\) whenever \\(a\\neq b\\).\n\\item Every packet \\(P_a\\Hcal\\) is invariant under \\(\\e^{-\\ii tH}\\) for every real \\(t\\).")
add(S, "full proof sentence", r"Apply \cref{strong:thm:fixed_leakage} and square the result.",
    r"Apply \cref{strong:thm:fixed_leakage} to the unit vector, then square the resulting nonnegative bound.")
add(S, "natural explanation", r"The geometric term is therefore part of the exact coupling test. A Hamiltonian may be packet diagonal at every fixed time and still fail to transport the moving packet because the packet itself rotates.",
    r"The exact coupling test therefore includes the geometric term. Even if the Hamiltonian is diagonal in the packet decomposition at every fixed time, its evolution can fail to follow a packet whose range rotates.")
add(S, "unnecessary compound", r"The absolute-value notation for the partition denotes its mesh, the largest subinterval length.",
    r"Here the size of the partition is measured by its mesh, which is the length of its largest subinterval.")
add(S, "natural proof prose", r"This is a first order one step approximation to \(\dot W=KW\).",
    r"This gives a first order approximation to \(\dot W=KW\) over a single time step.")
add(S, "natural scientific prose", r"The matrix valued one form",
    r"The one form with matrix values")
add(S, "full proof sentence", r"Integration gives one.",
    r"Integrating the displayed curvature over the sphere and applying the stated normalization gives one.")
add(S, "full proof sentence", r"The Pythagorean identity follows.",
    r"Since the packets are orthogonal and sum to the original operator, their squared norms add to its squared norm.")
add(S, "natural proof prose", r"Its range consists exactly of the diagonal operator packets, which is the commutant of the projector family.",
    r"Its range is the sum of the diagonal operator packets. This is exactly the commutant of the projector family.")
add(S, "full explanation", r"The theorem does not say that every diagonal quantum master equation closes to a classical Markov chain on packet populations. Scalar population closure needs additional isotropy inside each packet.",
    r"Preservation of coherence order does not by itself give a closed classical Markov chain for the packet populations. Such scalar population equations require additional isotropy within each packet.")
add(S, "semicolon", r"The zero code has only the zero supported operator and no normalized code state; that branch is treated in the mathematical completion in Part III.",
    r"The zero code has only the zero supported operator and no normalized code state. Part III treats that branch in the mathematical completion.")
add(S, "full explanation", r"The next result gives the packet construction behind the criterion.",
    r"The next result turns the scalar compression identities into a family of orthogonal syndrome packets. Those packets provide the coordinates used by the recovery map.")
add(S, "natural definition prose", r"For a finite error family define, with the maximum of the empty family set to zero,",
    r"For a finite error family, define the following defect. When the family is empty, assign the maximum the value zero.")
add(S, "full proof sentence", r"Invert the factors and read the upper left block.",
    r"Invert the factors. The retained resolvent is the block in the upper left corner of the resulting inverse.")
add(S, "natural proof prose", r"Divide by \(2\ii\) and sandwich the result between \(B\) and \(B^*\).",
    r"Divide by \(2\ii\), then multiply the result on the left by \(B\) and on the right by \(B^*\).")
add(S, "full proof prose", r"The first two estimates follow. The last is the mean value estimate along the real interval.",
    r"Taking operator norms gives the first two estimates. Applying the derivative bound along the real interval gives the final mean value estimate.")
add(S, "natural proof prose", r"and sandwich by \(B\) and \(B^*\).",
    r"and multiply on the left by \(B\) and on the right by \(B^*\).")
add(S, "full proof sentence", r"Insert the spectral decomposition into the exponential.",
    r"Inserting the spectral decomposition into the exponential gives the stated sum. The spectral projectors are positive semidefinite, so multiplication by the coupling and its adjoint preserves positivity of each coefficient.")
add(S, "full caption prose", r"A finite hidden spectrum produces an oscillatory memory kernel rather than an instantaneous retained Hamiltonian.",
    r"A finite hidden spectrum produces an oscillatory memory kernel. The retained dynamics therefore depend on the history of the retained state.")
add(S, "full proof sentence", r"Apply \cref{strong:prop:self_energy_bounds,strong:thm:self_energy_stability} uniformly.",
    r"The common gap and coupling bounds allow \cref{strong:prop:self_energy_bounds,strong:thm:self_energy_stability} to be applied uniformly across the family.")
add(S, "natural explanation", r"This result identifies the finite hypotheses needed for cutoff independent Feshbach control. It does not prove that a chosen geometric refinement tower satisfies them.",
    r"This result identifies hypotheses that make Feshbach control uniform in the cutoff. Whether a chosen geometric refinement tower satisfies those hypotheses remains a separate question.")
add(S, "natural spectral prose", r"The global spectral dimension is the heat weight average",
    r"The global spectral dimension is the average of the packet dimensions weighted by their heat traces:")
add(S, "natural proof prose", r"Both dominators are summable on \(\ZZ^d\).",
    r"Both dominating sequences are summable on \(\ZZ^d\).")
add(S, "full proof sentence", r"Insert this in the logarithmic derivative.",
    r"Substituting this estimate into the logarithmic derivative gives the stated small time expansion.")
add(S, "natural explanation", r"This is why the quotient in \cref{strong:def:closure_obstruction} is needed. Compression to physical states tests action on the common kernel, not closure of the operator algebra.",
    r"The quotient in \cref{strong:def:closure_obstruction} is needed because closure concerns the operator algebra. Compression to physical states tests only the action on the common kernel, where the constraints already vanish.")
add(S, "full proof sentence", r"Their norms give the bound.",
    r"The triangle inequality and the stated bounds on the constraints and defects give the claimed estimate.")
add(S, "natural proof prose", r"Compatibility makes this well defined. The uniform norm bound makes it bounded on the dense union, so it extends uniquely.",
    r"Compatibility makes the definition independent of the chosen level. The uniform norm bound makes the operator bounded on the dense union, so it extends uniquely to the completion.")
add(S, "natural explanation", r"The next theorem uses a common Hilbert space. It is appropriate for bounded effective Hamiltonians, not for an unbounded field Hamiltonian.",
    r"The next theorem places all approximating Hamiltonians on a common Hilbert space. It applies to bounded effective Hamiltonians. An unbounded field Hamiltonian requires a different convergence argument.")
add(S, "natural proof prose", r"Both unitary factors have norm one. The Euclidean estimate is identical because the nonnegative semigroups are contractions.",
    r"Both unitary factors have norm one, which gives the first estimate. The same argument gives the Euclidean estimate because the semigroups generated by nonnegative Hamiltonians are contractions.")
add(S, "unnecessary compound", r"then the spectral dimensions defined by the heat-moment ratio converge at that time.",
    r"then the spectral dimensions defined by the heat moment ratio converge at that time.")
add(S, "natural explanation", r"Its construction generally requires strong resolvent convergence, convergence of closed quadratic forms, or another domain sensitive method",
    r"Its construction generally requires strong resolvent convergence, convergence of closed quadratic forms, or another method that controls operator domains")
add(S, "natural explanation", r"The finite theorems establish exact identities and bounded limit criteria. They do not collapse the steps between a finite transfer model and a continuum theory. This section records the separate mathematical tasks.",
    r"The finite theorems establish exact identities and criteria for bounded limits. Passing from a finite transfer model to a continuum theory still requires several separate arguments. This section states those remaining mathematical tasks.")
add(S, "natural criterion prose", r"A quantum geometric tower meets an Einstein infrared criterion only if a controlled long wavelength effective action exists and has an expansion whose leading geometric terms take the form",
    r"A quantum geometric tower meets an Einstein infrared criterion only if an effective action is controlled at long wavelengths and has an expansion whose leading geometric terms take the form")
add(S, "connected conclusion prose", r"The bounded tower theorems show how exact compatibility and norm summability produce limiting quantum evolutions. They also show the boundary of the argument. Unbounded field Hamiltonians, continuum gauge constraints, reflection positive field measures, the Einstein infrared action, and a massless spin two sector require additional theorems. The finite packet calculus organizes those questions but does not settle them.",
    r"The theorems for bounded towers show how exact compatibility and summable differences in operator norm produce limiting quantum evolutions. Their hypotheses also mark the scope of the argument. Unbounded field Hamiltonians, continuum gauge constraints, reflection positive field measures, the Einstein infrared action, and a massless spin two sector each require additional theorems. The finite packet calculus gives a common framework in which those questions can be stated and studied, while leaving their physical resolution open.")

add(E, "unnecessary compounds and fuller prose", r"For $M_2(\mathbb C)\otimes I_3$, a coefficient matrix with rank one generates a two-dimensional orbit. A rank-two matrix generates a four-dimensional orbit. Neither single seed spans the six-dimensional space, because a $2\times3$ matrix cannot have rank three. Two seeds can cover the three multiplicity coordinates together. This is the finite seed-rank formula with $d=2$ and $m=3$.",
    r"For $M_2(\mathbb C)\otimes I_3$, a coefficient matrix with rank one generates an orbit of dimension two. A matrix of rank two generates an orbit of dimension four. Neither single seed spans the full space of dimension six, because a $2\times3$ matrix cannot have rank three. Two seeds can nevertheless cover all three multiplicity coordinates together. The example illustrates the finite seed rank formula with $d=2$ and $m=3$.")
add(E, "full caption prose", r"Exact coefficient matrices for $d=2$, $m=3$. The combined row support of two seeds has rank three. The bar heights are algebraic orbit dimensions, not unitary preparation probabilities.",
    r"The figure displays exact coefficient matrices for $d=2$, $m=3$. The combined row support of two seeds has rank three. The bar heights record algebraic orbit dimensions and should not be read as probabilities of unitary state preparation.")
add(E, "full explanation", r"The difference comes from a path through the discarded coordinate.",
    r"The difference records the contribution of a path through the eliminated coordinate. Direct compression omits that contribution, while block inversion retains it.")
add(E, "full caption prose", r"A rational two-coordinate block-inverse model. Both the eliminated block and full operator are invertible. The plotted values are exact fractions. This example distinguishes direct compression from resolvent elimination.",
    r"This rational model uses two coordinates to illustrate block inversion. Both the eliminated block and the full operator are invertible, and the plotted values are exact fractions. The example shows why direct compression and resolvent elimination give different results.")
add(E, "full explanation", r"The same relative weights produce different output traces.",
    r"The two families have the same relative weights, but their total normalization differs. That difference changes the output trace even though the supported state has the same direction.")
add(E, "full caption prose", r"Exact weights for one supported code state. The normalized map preserves trace one. The unnormalized positive map has output trace four. The illustration records this finite scaling distinction and does not assert a general recovery construction.",
    r"The figure shows exact weights for one supported code state. The normalized map preserves trace one, while the unnormalized positive map has output trace four. The illustration records this finite scaling distinction and does not assert a general recovery construction.")

math_pattern = re.compile(r"\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$.*?(?<!\\)\$", re.S)
def sha(data): return hashlib.sha256(data).hexdigest()
def math_spans(text): return math_pattern.findall(text)
def structural(text):
    return re.findall(r"\\(?:begin|end)\{[^}]+\}|\\(?:label|(?:C|c)?ref|eqref|cite|citep|citet)\{[^}]+\}", text)

files = []
patches = []
for file in (C, S, E):
    old_bytes = (BASE / file).read_bytes()
    original = old_bytes.decode("utf-8")
    current = (ROOT / file).read_text()
    if current != original:
        raise RuntimeError(f"Owned source is not pristine: {file}")
    chosen = [item for item in edits if item["file"] == file]
    new = current
    for ordinal, item in enumerate(chosen, 1):
        before = item["before"]
        if new.count(before) != 1:
            raise RuntimeError(f"Replacement must match exactly once: {file}: {ordinal}: {before!r}")
        item["ordinal_in_file"] = ordinal
        item["line_before"] = original[:original.index(before)].count("\n") + 1
        new = new.replace(before, item["after"], 1)
    if math_spans(original) != math_spans(new):
        a = math_spans(original)
        b = math_spans(new)
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                raise RuntimeError(f"Math span changed: {file}, index {i}: {x!r} -> {y!r}")
        raise RuntimeError(f"Math span count changed: {file}")
    if structural(original) != structural(new):
        raise RuntimeError(f"Structural command sequence changed: {file}")
    (ROOT / file).write_text(new)
    files.append({
        "file": file,
        "sha256_before": sha(old_bytes),
        "sha256_after": sha(new.encode()),
        "lines_before": len(original.splitlines()),
        "lines_after": len(new.splitlines()),
        "replacement_count": len(chosen),
        "math_span_count": len(math_spans(original)),
        "math_spans_byte_identical": True,
        "structural_commands_identical": True,
        "coverage": "Entire original source read sequentially, including surrounding displays and every proof. Every replacement reread in context before application. Final source reread pending.",
        "prose_semicolons_before": len(re.sub(math_pattern, "", original).split(";")) - 1,
        "prose_semicolons_after": len(re.sub(math_pattern, "", new).split(";")) - 1,
    })
    patches.append("".join(difflib.unified_diff(
        original.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"previous/{file}", tofile=f"final/{file}")))

report = {
    "status": "SOURCE_EDITS_APPLIED_FINAL_REREAD_PENDING",
    "date": "2026-10-18",
    "role": "Traditional core and examples prose editor",
    "scope": "Complete source reading and conservative sentence-level prose editing in the three owned files.",
    "user_preference": "Natural full scientific prose; avoid unnecessary hyphens, dashes, and semicolons.",
    "mathematical_token_changes": [],
    "fresh_lean_execution": False,
    "fresh_numerical_experiments": False,
    "preserved": "All extracted inline and display mathematical spans, labels, cross-reference and citation commands, and environment sequence are byte-identical. Proof prose may change, but proof steps and hypotheses are retained.",
    "known_pagination_support": [
        "Added a complete introduction after the Part I Kraus transfer heading.",
        "Added a complete introduction after the Part I one- and two-dimensional plateaus heading.",
        "Parent owns floats, spacing and final PDF pagination."
    ],
    "files": files,
    "replacement_count": len(edits),
    "replacements": edits,
    "unresolved_issues": [],
    "pdf_review": "Not yet run. Parent rebuilds PDFs and will provide final candidates.",
}
(OUT / "PROSE_REVIEW.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
(OUT / "PROSE_EDITS.patch").write_text("".join(patches))
print(json.dumps({"status": report["status"], "replacement_count": len(edits), "files": files}, indent=2))
