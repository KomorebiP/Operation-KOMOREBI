"""Render the archived 115 exact theorem types into a source-bound appendix."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source/komorebi-circuit-obstructions-v1.2.0'
CATALOG = SOURCE / 'reference/lean-block02/declaration_catalog.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    catalog = json.loads(CATALOG.read_text())
    entries = catalog['theorems']
    assert len(entries) == 115 and len({e['name'] for e in entries}) == 115
    modules = {}
    for e in entries:
        file = SOURCE / 'formalization/lean' / e['file']
        assert sha(file) == e['source_sha256'], e['file']
        assert e['name'].split('.')[-1] in file.read_text().splitlines()[e['line']-1]
        modules.setdefault(e['module'], []).append(e)
    output = [r'\clearpage\section*{Complete declaration register}',
              r'\addcontentsline{toc}{section}{Complete declaration register}',
              'The following 115 types are transcribed from the archived Block 02 '
              'declaration catalog. Unicode logical operators are rendered as mathematical '
              'glyphs; the complete original UTF-8 statements are also supplied. '
              'Source files and line locators match the preserved source hashes. '
              'These are archived elaborated types, not a new compilation result.',
              r'\begingroup',
              r'\lstset{basicstyle=\ttfamily\scriptsize,breakatwhitespace=false,',
              r'literate={¬}{{\ensuremath{\neg}}}1 {×}{{\ensuremath{\times}}}1',
              r'{→}{{\ensuremath{\to}}}1 {↔}{{\ensuremath{\leftrightarrow}}}1',
              r'{∀}{{\ensuremath{\forall}}}1 {∃}{{\ensuremath{\exists}}}1',
              r'{∈}{{\ensuremath{\in}}}1 {∧}{{\ensuremath{\land}}}1',
              r'{≠}{{\ensuremath{\ne}}}1 {≤}{{\ensuremath{\le}}}1}',
              '']
    for module, theorems in modules.items():
        short = module.split('.')[-1]
        output.append(r'\subsection*{' + short + ': ' + str(len(theorems)) + ' declarations}')
        for e in theorems:
            output.extend([
                r'\par\medskip\noindent\begin{minipage}{\textwidth}',
                r'{\small\bfseries ' + e['id'] + r'\enspace\texttt{' + e['name'].split('.')[-1].replace('_',r'\_') + r'}\par}',
                r'{\footnotesize\raggedright\textbf{Source.}\enspace\code{' + e['file'] + '}:' + str(e['line']) + r'\par',
                r'\textbf{Block.}\enspace ' + ('02' if e['new_in_block02'] else '01') +
                r'\quad\textbf{Axioms.}\enspace ' + (', '.join(e['axioms']) or 'none') + r'\par}\nopagebreak',
                r'\begin{lstlisting}',
                e['statement_utf8'],
                r'\end{lstlisting}', r'\end{minipage}\par', ''])
    output.append(r'\endgroup')
    (ROOT/'manuscripts/lean_register.tex').write_text('\n'.join(output)+'\n')
    (ROOT/'manuscripts/lean_statements_utf8.txt').write_text(
        '\n\n'.join(e['id']+'\n'+e['statement_utf8'] for e in entries)+'\n')
    report = {'schema':'komorebi.circuit.lean-register.v1','status':'PASS',
              'catalog_sha256':sha(CATALOG),'declarations':len(entries),
              'modules':{m:len(es) for m,es in modules.items()},
              'source_hashes_and_line_locators_match':True,
              'register_tex_sha256':sha(ROOT/'manuscripts/lean_register.tex'),
              'utf8_statements_sha256':sha(ROOT/'manuscripts/lean_statements_utf8.txt'),
              'fresh_compilation':False,
              'meaning':'Exact archived type transcription and source binding, not new elaboration'}
    (ROOT/'reviews/lean_register_generation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
