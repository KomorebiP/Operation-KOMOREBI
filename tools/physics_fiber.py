"""Retained book structure and macro dependencies for the covariant fiber reader."""
import re

BASE = 'monographs/physics/source/backreaction/'
MAIN = BASE+'Projector_Refinement_Physics_Covariant_Backreaction_Bridge.tex'
VALUES = BASE+'generated_values.tex'


def source_blocks(load, treatment):
    """Interleave the book's opening, authored inputs, and closing scope note."""
    raw = load(MAIN)
    lines = raw.splitlines()
    begin = lines.index(r'\begin{document}')+2
    end = lines.index(r'\end{document}')
    inputs = [(i+1, re.fullmatch(r'\\input\{(source/[^{}]+)\}', line))
              for i, line in enumerate(lines)]
    inputs = [(line, match[1]) for line, match in inputs if match]
    if [name for _, name in inputs] != treatment['inputs']:
        raise ValueError('Review Physics fiber body input order')
    blocks = [(MAIN, begin, inputs[0][0]-1)]
    for line, name in inputs:
        source = BASE+name+'.tex'
        body = load(source)
        if r'\input' in body:
            raise ValueError('Review Physics fiber nested input')
        blocks.append((source, 1, len(body.splitlines())))
    blocks.append((MAIN, inputs[-1][0]+1, end))
    # Only the printed input commands and appendix switch may fall between
    # selected main-file passages. Any additional prose must be selected.
    skipped = '\n'.join(lines[inputs[0][0]-1:inputs[-1][0]])
    skipped = re.sub(r'\\input\{source/[^{}]+\}|\\appendix\b', '', skipped)
    if skipped.strip() or lines[inputs[-1][0]-2] != r'\appendix':
        raise ValueError('Review Physics fiber main-file passage coverage')
    return blocks


def normalize(text):
    """Map book heading levels and styled boxes without moving source lines."""
    from physics_reading import mask
    text = re.sub(r'\\mainmatter\b', lambda m: mask(m[0]), text)
    text = text.replace(r'\begin{enumerate}[leftmargin=2.2em]', r'\begin{enumerate}')
    text = re.sub(r'\\(chapter|section|subsection)(\*)?\{',
        lambda m: '\\'+{'chapter':'section','section':'subsection','subsection':'subsubsection'}[m[1]]+(m[2] or '')+'{', text)
    for source, target in [('negativebox','warningbox'),('statusbox','readerroadmap'),('resultbox','keyidea')]:
        text = re.sub(r'\\begin\{'+source+r'\}\[([^\]]+)\]',
            lambda m: r'\begin{'+target+'}[title={'+m[1]+'}]', text)
        text = text.replace(r'\end{'+source+'}', r'\end{'+target+'}')
    return text


def macros(load):
    from readable_chapters import manuscript_macros, group
    text = load(MAIN)+'\n'+load(VALUES)
    result = manuscript_macros(text, [])
    match = re.search(r'\\newcommand\{\\PB\}\[2\]', text)
    if not match:
        raise ValueError('Missing Physics fiber Poisson-bracket macro')
    body, _ = group(text, match.end())
    result['PB'] = dict(arguments=2, body=body)
    return result


def display_equation_numbers(selected, prefix):
    """Bind every numbered book display, including displays without labels."""
    from readable_chapters import MATH_PATTERN, split_cells
    pattern = (r'\\begin\{(?P<environment>equation|align)\}(?P<body>.*?)'
               r'\\end\{(?P=environment)\}|'+MATH_PATTERN.pattern)
    result, counter = {}, 0
    for ordinal, match in enumerate(re.finditer(pattern, selected, re.S)):
        if not match['environment']:
            continue
        rows = [match['body']] if match['environment']=='equation' else [row for row in split_cells(match['body'],r'\\') if row.strip()]
        numbers = []
        for row in rows:
            if r'\notag' in row or r'\nonumber' in row:
                continue
            counter += 1
            numbers.append(prefix+'.'+str(counter))
        result[ordinal] = numbers
    return result
