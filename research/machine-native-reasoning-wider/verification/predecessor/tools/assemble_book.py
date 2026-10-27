from pathlib import Path
r=Path(__file__).resolve().parents[1]
text=(r/'sources/core/src/core.tex').read_text()
preamble=text.split('\\begin{document}',1)[0]
preamble=preamble.replace('\\definecolor{Ink}{HTML}{203B36}', '\\definecolor{Ink}{HTML}{153B42}\n\\definecolor{Accent}{HTML}{B27B47}')
preamble=preamble.replace('Machine-Native Reasoning: Reviewed Mathematical Core','Machine-Native Reasoning: Representation, Inference, Discovery, and Self-Correction')
preamble=preamble.replace('Evidence, methods, and accountable revision','Representation, inference, discovery and self-correction')
preamble=preamble.replace('\\fancyhead[R]{\\small Reviewed core 0.2}','\\fancyhead[R]{\\small\\scshape Realization Calculus}')
preamble=preamble.replace('\\setcounter{tocdepth}{0}','\\setcounter{tocdepth}{1}')
preamble=preamble.replace('\\newtheorem{theorem}{Theorem}[chapter]', '\\newtheorem{theorem}{Theorem}[chapter]\n\\newtheorem{lemma}[theorem]{Lemma}')
# Preserve original theorem environment names to avoid touching the verified manuscript.
body=r'''\begin{document}
\frontmatter
\hypersetup{pageanchor=false}
\begin{titlepage}
\thispagestyle{empty}
{\small\scshape REALIZATION CALCULUS\hfill MATHEMATICAL REASONING}\par
\vspace{1.1in}
{\color{Ink}\fontsize{34}{39}\selectfont\bfseries Machine-Native\\[3mm]Reasoning\par}
\vspace{0.30in}
{\fontsize{19}{25}\selectfont Representation, Inference,\\ Discovery, and Self-Correction\par}
\vspace{0.38in}{\color{Accent}\rule{1.9in}{2pt}}\par
\vspace{0.45in}{\Large Komorebi P.\par}
\vfill
{\large A mathematical theory of evidence-bearing computational realizations}\par
\vspace{0.22in}
This working edition contains the complete reviewed reasoning core, a formal realization prologue, an integrated legal-and-stochastic quotient argument, and a developed safe-ending proof. The wider monograph remains in preparation.\par
\vspace{0.65in}
{\color{Ink}\rule{\linewidth}{0.7pt}}\par
{\small Mathematical edition and reproducibility companion \hfill Working manuscript}
\end{titlepage}
\hypersetup{pageanchor=true}

\chapter*{Preface}\addcontentsline{toc}{chapter}{Preface}
A useful representation is not merely a shorter description of a state. It is a declaration about what can be read, predicted, corrected, transferred, and executed without needing the information that has been discarded. In this sense the mathematics of machine reasoning is a mathematics of preserved obligations. Different uses demand different kinds of preservation. A valid probabilistic prediction does not establish permission to act. A valid proof does not certify a sensor's interpretation. A record of a method does not ensure that another program can execute it.

The point of this book is to examine these interfaces as explicit mathematical objects. The first nine chapters preserve a continuously written, internally reviewed sequence of finite results. They move from evidence to reusable state, from state to operator transport, from correction memory to Bayesian updating, and from resource-bounded inquiry to certificate-preserving revision and collective operation. A new realization prologue places that sequence within Komorebi Space, the ambient theory of coherent views, gluing, and obstruction. New chapters then test whether the probabilistic and legal-operation contracts can be composed and expand the proof of safe continuation with an available ending strategy.

This edition should not be confused with the much larger archival collection of source manuscripts. The archive preserves specialized theories, historical evidence and experimental branches in their own scopes. The present text is selected and integrated. A statement appears as a proved theorem only with its hypotheses and proof. Computational examples use exact finite models. The existence of an abstract factorization is never treated as evidence that a learned model found it.

The reviewed mathematical core has twenty-seven written result/proof pairs. Its archived Lean correspondence covers twenty-three selected source results within recorded scopes. Four selected targets remain outside that formalization. The new interface theorem and the expanded ending proof are new prose developments in this working edition. They have exact finite reference checks where stated, but have not received new Lean kernel certification or external review. This is important mathematical metadata rather than a limitation to hide.

This book belongs to the Realization Calculus series. It does not assert a universal representation theorem for general intelligence, an unrestricted autonomous agent, or a physically verified learned semantics. It offers a bounded language in which such questions can be phrased more precisely. The mathematical claims and the assurance records remain separate, so readers can examine one without confusing it for the other.

\chapter*{How to read this edition}\addcontentsline{toc}{chapter}{How to read this edition}
The Realization Setting introduces the ambient mathematical language. Part I then gives nine chapters of a complete finite reasoning chain, including proofs and counterexamples. Part II adds a joint legal-and-stochastic quotient criterion, a full game-theoretic analysis of safe continuation with authorized ending, and the main unsolved composition and acquisition questions. The theorem and source maps appear at the back. The accompanying computational files are part of the reproducible edition, not substitute proofs for the general statements.

\tableofcontents
\input{realization_prologue.tex}
\mainmatter
\part{The Reviewed Mathematical Chain}
\input{core_chapters.tex}
\part{Composition, Control, and Boundaries}
\input{composition_chapter.tex}
\input{ending_chapter.tex}
\input{frontier_chapter.tex}
\backmatter
\chapter{A Glossary of the Reasoning Calculus}
\begin{description}[style=nextline]
\item[Realization] A compatible family of typed views meeting declared restriction constraints, or a concrete mathematical model satisfying a specified system contract.
\item[Representation] A map or retained record together with the questions and operations it is required to preserve.
\item[Evidence] Information accessible through declared observation or intervention protocols, not an assumed hidden truth label.
\item[Predictive closure] Existence of an update on retained state that commutes with the protected dynamics.
\item[Packet] A typed resolved component or projection. It is not automatically a probability distribution.
\item[Residual] A discrepancy relative to a specified representation or operation contract; its interpretation depends on the chosen norm or invariant.
\item[Correction signature] A retained equivalence class preserving the outcomes of all allowed future evidence filters on the target.
\item[Instrument] A joint next-state and report probability law, including the evidence scale needed for normalization.
\item[Legal-operation quotient] An abstraction preserving labels, action availability and successor semantics on all enabled actions.
\item[Certificate] Typed evidence for a named mathematical or operational claim relative to its explicit assumptions.
\item[Proof field] The larger network of typed claims and justifications within which a certified proof is located.
\item[Ending attractor] States from which a sure ending is possible under all admitted successor choices.
\item[Running kernel] The greatest region invariant under some running strategy that preserves immediate membership in the ending attractor.
\item[Assurance boundary] The precise source, computation, proof environment, or external premise supported by a verification record.
\end{description}
\input{original_backmatter.tex}
\end{document}
'''
# Original \backmatter and \end{document} are removed; the map and reading-sources chapters are retained.
src=text.split('\\backmatter',1)[1].rsplit('\\end{document}',1)[0]
(r/'original_backmatter.tex').write_text(src)
(r/'book.tex').write_text(preamble+body)
print('Wrote book.tex, verbatim core chapters and original source map')
