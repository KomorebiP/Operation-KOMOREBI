# Source concordance callout layout fix

Status: **implemented; isolated mechanism check passed; final-page acceptance pending.**

Only `source/preamble.tex` was changed for this fix. No theorem, proof text, caption, figure, or accepted formal evidence was edited. The coordinator owns the full monograph rebuild and final rendered-page review.

## Defect and implemented change

Several source concordance callouts had appeared at the top of a new page after their associated proof/example ended on the preceding page, including the reported KS07, KS15, KS35, KS36, KS65, KS70, and KS72 cases. Raising the theorem/proof end penalty alone did not remove every intervening breakpoint.

The source macro now starts its paragraph before emitting the anchor, label, and color nodes:

```tex
\newcommand{\source}[1]{\par\nopagebreak[4]\noindent\phantomsection\label{src:#1}{\footnotesize\sffamily\color{KomorebiMuted}Source concordance: \hyperlink{claim:#1}{#1}.}\par\smallskip}
```

The ineffective begin-hook arrangement was removed and replaced by an assignment at the environment ending, immediately before the environment's `endtrivlist` machinery:

```tex
\newcommand{\KomorebiKeepSourceEnding}[1]{%
  \AtEndEnvironment{#1}{\@endparpenalty\@M}}
\forcsvlist{\KomorebiKeepSourceEnding}{proof,theorem,proposition,lemma,corollary,definition,example,remark}
```

This suppresses the breakpoint after the final environment line and prevents a second breakpoint between vertical anchor/color nodes and the callout text. Interior proof paragraphs and lines are not boxed or given an unbreakable-proof policy. The ending penalty also keeps an environment's final line with the following paragraph when that paragraph is ordinary prose rather than a source callout.

## Isolated TeX evidence

The check loaded the real publication preamble in a tiny separate document, placed one proof and its source callout in a `vbox`, and inspected TeX's node list using `showbox`. It did not build the full monograph or overwrite its output. The fixture was:

```tex
\documentclass[11pt]{article}
\input{preamble}
\begin{document}
\showboxbreadth=100 \showboxdepth=8
\setbox0=\vbox{\hsize=400pt\begin{proof}Final proof line.\end{proof}\source{KS35}}
\showbox0
\end{document}
```

Before the fix, the node dump showed both intended penalties of 10000, but also a **vertical color-stack node immediately before paragraph glue**:

```text
.\hbox(...)                         [final proof line]
.\penalty 10000
.\glue 9.0 plus 7.0 minus 1.0
.\penalty 10000
.\pdfdest name{section*.1} xyz
.\penalty 10000
.\write1{...src:KS35...}
.\write1{...src:KS35@cref...}
.\pdfcolorstack 0 push {...}
.\glue(\parskip) 4.57288
.\glue(\parskip) 0.0
.\glue(\baselineskip) 5.03966
.\hbox(...)                         [source callout]
```

Thus the existing end penalty was present; it was insufficient because the later vertical whatsit preceded a new legal glue breakpoint. After inserting `noindent` before the anchor/color, the relevant vertical list was:

```text
.\hbox(...)                         [final proof line]
.\penalty 10000
.\glue 9.0 plus 7.0 minus 1.0
.\penalty 10000
.\glue(\parskip) 4.57288
.\glue(\parskip) 0.0
.\glue(\baselineskip) 5.03966
.\hbox(...)                         [source callout; anchor and color inside]
```

The anchor was confirmed at the nested `..\pdfdest` level inside the callout paragraph; the source text remained the same 9-point sans-serif font. No permitted breakpoint remains between the final proof line and its one-line callout in this fixture. The deliberate `showbox` diagnostic reports `! OK.`; it is a node inspection, not a normal PDF compilation acceptance run.

The fixture logs are in `tmp/source_callout_fixture/before.log` and `after.log`. Their relevant evidence is retained above, since scratch diagnostic paths are not release reproduction instructions.

## Snapshot and remaining acceptance

- Preamble SHA-256: `ae4e6ae0760d9c84e62ea3edaf7f7e255ba56c5e80bfefec55a06c552b5b4c5e`
- Before node-dump log SHA-256: `0069e0cae45d242fd7d0af37db1f00a68eb348915077bf9783a01292766c4352`
- After node-dump log SHA-256: `a1ab47167dd4c903e7bb55cb61e2e68dd261befb7233ca12bcc4c42d6519b46b`

The final monograph has not been visually accepted by this mechanism check. The coordinator's new full build must be inspected for the affected callouts and any pagination changes. No claim is made here that all seven previously affected source IDs are already on accepted final pages.
