from pathlib import Path
r=Path('/workspace/scratch/196a43c5b4f3')
s=r/'release_staging/PRSC_IX_Complete_Polynomial_Lifting'
p=s/'REMAINING_CHECKLIST.md'
t=p.read_text().replace(' — completed in this block.',' — completed in the preceding isometry block.')
start=t.index('## Clear routes still awaiting formalization')
end=t.index('## Research questions still open')
new=r'''- [x] **Actual polynomial Taylor formula — completed in this block.** For every finite-variable integer polynomial and integer step \(a\),
  \[
  a^2\mid P(x+at)-P(x)-a\sum_i\partial_iP(x)t_i.
  \]
  At depth \(L\ge1\), the remainder vanishes modulo \(q^{L+1}\) when \(a=q^L\).

- [x] **Fixed-presentation finite polynomial obstruction — completed in this block.** For every \(q>0\), \(L\ge1\), finite system \(F\), and lower root \(x\), put \(r_x=F(x)/q^L\) and \(J_x=\rho_q\circ DF(x)\). Then
  \[
  \mathcal O_x=(\mathbb Z/q\mathbb Z)^e/\operatorname{im}J_x,
  \qquad [\rho_q(r_x)]=0
  \iff \exists y\equiv x\pmod{q^L}:F(y)\equiv0\pmod{q^{L+1}}.
  \]
  The quotient is finite. The theorem derives the residual from the actual congruence and permits composite moduli and modulus one. No surjectivity premise is imposed on the Jacobian.

- [x] **Polynomial representative independence — completed in this block.** Changing \(x\) by \(q^Ls\) leaves the reduced Jacobian unchanged and changes the residual digit by \(J_xs\). The same quotient therefore carries the same obstruction class. This is independence of integer representatives within a fixed presentation.

- [x] **Actual shared polynomial corrections — completed in this block.** For two systems with the same variables, define \(\mathcal C_x=\mathbb Z^d/(\ker J_x+\ker K_x)\). Given separately valid corrections \(u,v\), a single next lift of both systems exists exactly when \([u]=[v]\) in this finite quotient. Each label is independent of the selected valid correction. An unconditional version includes individual solvability in the criterion.

## Clear routes still awaiting formalization

| Status | Target | Exact work left |
|---|---|---|
| [ ] Proved in existing prose; counts not yet Lean-checked | **Polynomial correction torsor and prime-field counts.** | Work with correction digits in \(\mathbb F_p^d\). If a lift exists, identify the lift fiber with a torsor for the kernel of the induced Jacobian \(\overline A_x\); prove its size \(p^{d-\operatorname{rank}\overline A_x}\), and cokernel size \(p^{e-\operatorname{rank}\overline A_x}\). Integer correcting vectors themselves form an infinite set when \(d>0\). |
| [ ] Beyond the completed one-step theorem | **Compatibility through a specified polynomial tower.** | Define level objects and transition maps. Use the checked stability of the reduced Jacobians, then prove transport of the actual residual labels and the conditions needed for a compatible infinite lift. A one-step lift does not ensure continuation. |
| [ ] Recovery/formalization task | **Remaining historical edge identities and carry forms.** | Inventory the exact older odd-prime formulas and binary digit-sum form of the checked binomial weights. Recovered partial source windows and the available reconstructed Annals text are included with their provenance. |

The continuous isometry, polynomial Taylor bridge, fixed-presentation obstruction, and one-step shared-polynomial application are now formalized. The prime-field torsor/count formulas remain distinct formalization tasks; the full earlier prose theorem has not been marked uniformly Lean-checked.

'''
t=t[:start]+new+t[end:]
a=t.index('## Suggested next block');b=t.index('## Evidence locations')
t=t[:a]+r'''## Suggested next block

Formalize the **finite correction-digit torsor and prime-field lift counts**. The actual polynomial-to-Jacobian bridge is now complete, so the remaining proof is finite linear algebra followed by identifying correction digits with distinct representatives modulo \(p^{L+1}\). Then specify the intended tower and its transition maps before attempting infinite compatibility or native descent.

'''+t[b:]
t=t.replace('- Latest isometry block:', '- Latest polynomial block: `polynomial_lifting/POLYNOMIAL_LIFTING.md`, `polynomial_lifting/formalization/`, `polynomial_lifting/verification/polynomial_verification.json`, and `polynomial_lifting/INDEPENDENT_PROOF_AUDIT.md`.\n- Previous isometry block:')
p.write_text(t)
# Clarify notation in the new supplement before copying it.
p=r/'polynomial_lifting/POLYNOMIAL_LIFTING.md';t=p.read_text()
t=t.replace(r'F(y)\equiv G(y)\equiv0\pmod{q^{L+1}}.',r'F(y)\equiv0\pmod{q^{L+1}},\quad G(y)\equiv0\pmod{q^{L+1}}.')
t=t.replace('The last display means that both systems vanish in their respective dimensions. ', '')
t=t.replace(r'the prime-field counts \(p^{d-\operatorname{rank}J_x}\) and \(p^{e-\operatorname{rank}J_x}\)',r'the prime-field counts \(p^{d-\operatorname{rank}\overline A_x}\) and \(p^{e-\operatorname{rank}\overline A_x}\), where \(\overline A_x:\mathbb F_p^d\to\mathbb F_p^e\) is the induced Jacobian')
p.write_text(t)
