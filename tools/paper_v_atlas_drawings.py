"""Read literal Paper V drawing labels; never execute TikZ or its expressions."""
import re
from fractions import Fraction

from readable_chapters import group, original_math, split_cells
from reader_drawing_transcripts import label_tex, drawing_nodes as shared_nodes


def expand_loops(text):
    while (match := re.search(r'\\foreach\s+([^{}]+?)\s+in\s*\{', text)):
        variables = match[1].strip().split('/')
        values, end = group(text, match.end()-1)
        while end < len(text) and text[end].isspace():
            end += 1
        body, stop = group(text, end)
        if '\n' in text[match.start():stop]:
            raise ValueError('Review multiline Paper V drawing loop')
        inventory = { (r'\x', r'\s'): '3/{3/4},4/1,8/2,9/{9/4}',
                      (r'\y',): '0,2.2' }
        if inventory.get(tuple(variables)) != values:
            raise ValueError('Review changed Paper V literal drawing loop')
        rendered = []
        for item in split_cells(values, ','):
            bindings = split_cells(item, '/') if len(variables)>1 else [item]
            if len(bindings) != len(variables):
                raise ValueError('Irregular drawing loop')
            expanded = body
            for variable, value in zip(variables, bindings):
                value = value.strip()
                if value.startswith('{'):
                    value, _ = group(value, 0)
                if not re.fullmatch(r'[\d./]+', value):
                    raise ValueError('Nonliteral drawing loop value')
                expanded = re.sub(re.escape(variable)+r'\b', lambda m:value, expanded)
            rendered.append(expanded)
        text = text[:match.start()]+' '.join(rendered)+text[stop:]
    if r'\foreach' in text:
        raise ValueError('Unsupported Paper V drawing loop')
    return text


def drawing_nodes(text):
    # Existing retained drawings use the shared parser unchanged. Four drawings
    # need literal loops, fractional positions, or the prose phrase "node labels".
    try:
        return shared_nodes(text)
    except ValueError:
        pass
    text = expand_loops(text)
    pattern = r'(?:\\node|(?<!\\)\bnode)(?:\[[^\]]*\])?(?:\s*at\s*\(([-+\d./]+),\s*([-+\d./]+)\))?\s*\{'
    result=[]; masked=list(text)
    for match in re.finditer(pattern, text):
        value,end = group(text, match.end()-1)
        if not text[end:].lstrip().startswith((';','(')):
            raise ValueError('Unsupported Paper V drawing label tail')
        result.append(dict(text=label_tex(value),source_text=value,
                           position=[float(Fraction(match[1])),float(Fraction(match[2]))] if match[1] else None,
                           line=text.count('\n',0,match.start())+1))
        masked[match.start():end]=[' ']*(end-match.start())
    if re.search(r'(?:\\node|(?<!\\)\bnode)\b', ''.join(masked)):
        raise ValueError('Unsupported Paper V drawing label')
    if [m for n in result for m in original_math(n['text'])] != original_math(label_tex(text)):
        raise ValueError('Mathematics outside the drawing transcript')
    return result
