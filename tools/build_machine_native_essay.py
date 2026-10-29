#!/usr/bin/env python3
"""Build the revised Machine-Native Mathematics reading edition from Markdown.

The Markdown manuscript is authoritative for this editorial edition. This
converter supports only the small set of constructs used in that manuscript.
It does not execute manuscript content or enable TeX shell commands.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / 'docs/essays/MACHINE_NATIVE_MATHEMATICS.md'
PROJECT = ROOT / 'publication/machine-native-mathematics'
PUBLIC_PDF = ROOT / 'website/assets/publications/machine-native-mathematics.pdf'
SITE = 'https://komorebip.github.io/Operation-KOMOREBI/'
INLINE = re.compile(r'\\\((.*?)\\\)|`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*|\[([^\]]+)\]\(([^)]+)\)')

PREAMBLE = r'''\documentclass[11pt,oneside,openany]{book}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amsthm,mathtools}
\usepackage{newpxtext,newpxmath,mathrsfs}
\usepackage[paperwidth=7.5in,paperheight=10in,inner=0.80in,outer=0.80in,top=0.82in,bottom=0.78in,headheight=14pt,headsep=0.22in,footskip=0.35in]{geometry}
\usepackage{microtype,xcolor,titlesec,fancyhdr,enumitem,needspace,etoolbox}
\usepackage{xurl,hyperref,bookmark}
\definecolor{Ink}{HTML}{172A3A}
\definecolor{Accent}{HTML}{286E75}
\definecolor{Quiet}{HTML}{52656D}
\definecolor{CoverLight}{HTML}{CDDEE2}
\hypersetup{colorlinks=true,linkcolor=Accent,urlcolor=Accent,
pdftitle={The Possibility for a Machine-Native Mathematics},
pdfauthor={Komorebi P.},pdfsubject={Representation, abstraction, and mathematical reasoning},
bookmarksnumbered=true,pdfdisplaydoctitle=true}
\urlstyle{same}
\setlength{\parindent}{1.05em}
\setlength{\parskip}{3pt plus 0.8pt}
\linespread{1.045}
\setlength{\emergencystretch}{2em}
\raggedbottom
\setcounter{tocdepth}{1}
\setcounter{secnumdepth}{1}
\makeatletter
\patchcmd{\l@chapter}{\vskip1.0em}{\vskip0.3em}{}{\PackageError{essay}{Could not set contents spacing}{}}
\makeatother
\titleformat{\chapter}[display]{\normalfont\color{Ink}}{\sffamily\small\color{Accent}\MakeUppercase{\chaptertitlename}\ \thechapter}{9pt}{\fontsize{25}{29}\selectfont\raggedright\hyphenpenalty=10000\exhyphenpenalty=10000}
\titlespacing*{\chapter}{0pt}{4pt}{20pt}
\titleformat{\section}{\large\bfseries\color{Ink}}{\thesection}{0.7em}{}
\titlespacing*{\section}{0pt}{16pt}{7pt}
\setlist{itemsep=3pt,topsep=6pt,parsep=0pt,leftmargin=1.6em}
\appto\normalsize{\setlength{\abovedisplayskip}{8pt plus 2pt minus 2pt}\setlength{\belowdisplayskip}{8pt plus 2pt minus 2pt}}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\sffamily\fontsize{8}{10}\selectfont\color{Quiet}\nouppercase{\leftmark}}
\fancyhead[R]{\sffamily\fontsize{8}{10}\selectfont\color{Quiet}KOMOREBI P.}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\chaptermark}[1]{\markboth{\thechapter\quad #1}{}}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0pt}}
\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}
\thispagestyle{empty}
\pagecolor{Ink}\color{CoverLight}
\noindent{\sffamily\small MATHEMATICS AND ARTIFICIAL INTELLIGENCE}\par
\vspace{0.24in}
\noindent{\color{Accent}\rule{\textwidth}{1.5pt}}\par
\vspace{0.65in}
\noindent{\color{white}\fontsize{35}{41}\selectfont
The Possibility for a\\Machine-Native\\Mathematics\par}
\vspace{0.42in}
\noindent{\fontsize{16}{22}\selectfont\raggedright\hyphenpenalty=10000\exhyphenpenalty=10000
How mathematical reasoning may change when its representations and primitive operations can change with it.\par}
\vfill
\noindent{\color{white}\Large Komorebi P.}\par
\vspace{0.18in}
\noindent{\sffamily\small Revised reading edition\par 29 October 2026}
\end{titlepage}
\nopagecolor\color{Ink}
\frontmatter
\hypersetup{pageanchor=true}
'''


def escape(text):
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                    '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
                    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(replacements.get(char, char) for char in text)


def public_url(target):
    if urlsplit(target).scheme:
        return target
    path, _, fragment = target.partition('#')
    resolved = posixpath.normpath(posixpath.join('docs/essays', path))
    if resolved.startswith('docs/') and resolved.endswith('.md'):
        result = SITE + 'collection/' + resolved[5:-3] + '.html'
    elif resolved.startswith('website/assets/'):
        result = SITE + resolved[len('website/'):]
    else:
        result = 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/' + resolved
    return result + ('#' + fragment if fragment else '')


def inline(text):
    result = []
    offset = 0
    for match in INLINE.finditer(text):
        result.append(escape(text[offset:match.start()]))
        math, code, bold, italic, label, target = match.groups()
        if math is not None:
            result.append(r'\(' + math + r'\)')
        elif code is not None:
            result.append(r'{\ttfamily\small\nolinkurl{' + code + '}}')
        elif bold is not None:
            result.append(r'\textbf{' + inline(bold) + '}')
        elif italic is not None:
            result.append(r'\emph{' + inline(italic) + '}')
        elif target.startswith('#'):
            result.append(r'\hyperlink{' + target[1:] + '}{' + inline(label) + '}')
        else:
            url = public_url(target).replace('%', r'\%').replace('#', r'\#').replace('&', r'\&')
            result.append(r'\href{' + url + '}{' + inline(label) + '}')
        offset = match.end()
    result.append(escape(text[offset:]))
    return ''.join(result)


def latex(source):
    output = [PREAMBLE]
    paragraph = []
    display = None
    list_kind = None
    mainmatter = False

    def flush():
        if paragraph:
            output.append(inline(' '.join(paragraph)) + '\n\n')
            paragraph.clear()

    def close_list():
        nonlocal list_kind
        if list_kind:
            output.append('\\end{' + list_kind + '}\n\n')
            list_kind = None

    for line in source.splitlines():
        stripped = line.strip()
        if display is not None:
            display.append(line)
            if stripped == r'\]':
                output.append('\n'.join(display) + '\n\n')
                display = None
            continue
        if stripped == r'\[':
            flush()
            close_list()
            display = [line]
            continue
        if not stripped:
            flush()
            continue
        if stripped.startswith('# ') or stripped == '**Komorebi P.**' or stripped.startswith('Revised reading edition') or stripped.startswith('[Download the monograph PDF]'):
            continue
        anchor = re.fullmatch(r'<a id="([A-Za-z0-9_-]+)"></a>', stripped)
        if anchor:
            flush()
            close_list()
            output.append(r'\hypertarget{' + anchor[1] + '}{}\n')
            continue
        heading = re.fullmatch(r'(#{2,4})\s+(.+)', stripped)
        if heading:
            flush()
            close_list()
            depth, title = len(heading[1]), heading[2]
            if depth == 2 and title == 'Introduction' and not mainmatter:
                output.append(r'\begingroup\small\setlength{\parskip}{0pt}\tableofcontents\endgroup\clearpage\mainmatter' + '\n')
                mainmatter = True
            if depth == 2 and not mainmatter and title == 'About this edition':
                output.append(r'\section*{' + inline(title) + r'}\addcontentsline{toc}{section}{' + inline(title) + '}\n')
            elif depth == 2 and not mainmatter:
                output.append(r'\chapter*{' + inline(title) + r'}\markboth{' + inline(title) + r'}{}\addcontentsline{toc}{chapter}{' + inline(title) + '}\n')
            elif depth == 2:
                if title == 'References':
                    output.append('\\backmatter\n')
                output.append(r'\chapter{' + inline(title) + '}\n')
            else:
                command = 'section' if depth == 3 else 'subsection'
                output.append('\\' + command + '{' + inline(title) + '}\n')
            continue
        item = re.fullmatch(r'(?:\d+\.|-)\s+(.+)', stripped)
        if item:
            flush()
            kind = 'enumerate' if stripped[0].isdigit() else 'itemize'
            if list_kind != kind:
                close_list()
                output.append('\\begin{' + kind + '}\n')
                list_kind = kind
            output.append(r'\item ' + inline(item[1]) + '\n')
            continue
        close_list()
        paragraph.append(stripped)
    flush()
    close_list()
    if display is not None:
        raise ValueError('Unclosed display math')
    output.append('\\end{document}\n')
    result = ''.join(output)
    for pattern in (r'\\\[(.*?)\\\]', r'\\\((.*?)\\\)'):
        original = re.findall(pattern, source, re.S)
        generated = re.findall(pattern, result, re.S)
        if original != generated:
            raise ValueError('Mathematical expressions changed during conversion')
    return result


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tectonic', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    PROJECT.mkdir(parents=True, exist_ok=True)
    tex = PROJECT / 'main.tex'
    tex.write_text(latex(MANUSCRIPT.read_text(encoding='utf-8')), encoding='utf-8', newline='\n')
    if not args.tectonic:
        print(json.dumps({'source': str(tex), 'manuscript_sha256': sha256(MANUSCRIPT)}))
        return
    if not args.output:
        parser.error('--output is required with --tectonic')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(args.tectonic.resolve()), '-X', 'compile', '--untrusted', '--keep-logs',
                    '--outdir', str(output), str(tex.resolve())], check=True)
    pdf = output / 'main.pdf'
    PUBLIC_PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf, PUBLIC_PDF)
    from pypdf import PdfReader
    record = {
        'edition': 'Revised reading edition, 29 October 2026',
        'manuscript': MANUSCRIPT.relative_to(ROOT).as_posix(),
        'manuscript_sha256': sha256(MANUSCRIPT),
        'latex': tex.relative_to(ROOT).as_posix(),
        'latex_sha256': sha256(tex),
        'pdf': PUBLIC_PDF.relative_to(ROOT).as_posix(),
        'pdf_sha256': sha256(PUBLIC_PDF),
        'pages': len(PdfReader(PUBLIC_PDF).pages),
        'display_math_expressions': len(re.findall(r'\\\[(.*?)\\\]', MANUSCRIPT.read_text(encoding='utf-8'), re.S)),
        'inline_math_expressions': len(re.findall(r'\\\((.*?)\\\)', MANUSCRIPT.read_text(encoding='utf-8'), re.S)),
        'compiler': subprocess.check_output([str(args.tectonic.resolve()), '--version'], text=True).strip(),
        'original_pdf_sha256': 'dfe58e51a85e008bc7f23885da8453b08201753d6d3dc4bcdb05d339d10a5920',
        'scope': 'Editorial revision, explicit local mathematical assumptions, and monograph typesetting. No new Lean execution or collection-wide mathematical audit.'
    }
    (PROJECT / 'build-record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
