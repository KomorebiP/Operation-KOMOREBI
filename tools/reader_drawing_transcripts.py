"""Source-preserving label transcripts shared by the HTML visual atlases.

Only literal drawing labels and the retained finite loops are interpreted.
Geometry is used for reading order and table structure, not as proof evidence.
"""
import re
from readable_chapters import group,original_math


def label_tex(text):
    """Present forced prose line breaks without changing math or matrix rows."""
    result=[]; position=0; in_math=False
    while position<len(text):
        if text.startswith(r'\\',position):
            result.append(r'\\' if in_math else r'\newline ')
            position+=2
        elif text[position]=='\\':
            result.append(text[position:position+2]); position+=2
        else:
            if text[position]=='$': in_math=not in_math
            result.append(text[position]); position+=1
    if in_math:
        raise ValueError('Unclosed drawing-label mathematics')
    return ''.join(result)


def drawing_nodes(text):
    text=expand_drawing_loops(text)
    result=[]
    pattern=r'(?:\\node|(?<!\\)\bnode)(?:\[[^\]]*\])?(?:\s*\([A-Za-z0-9_:-]+\))?(?:\s*at\s*\(([-+\d.]+),\s*([-+\d.]+)\))?\s*\{'
    for match in re.finditer(pattern,text):
        value,end=group(text,match.end()-1)
        if not text[end:].lstrip().startswith((';','(')):
            raise ValueError('Unsupported drawing label tail')
        result.append(dict(text=label_tex(value),source_text=value,
                           position=[coordinate(match[1]),coordinate(match[2])] if match[1] else None,
                           line=text.count('\n',0,match.start())+1))
    if len(result)!=len(re.findall(r'(?:\\node|(?<!\\)\bnode)\b',text)):
        raise ValueError('Unsupported drawing label')
    if [m for n in result for m in original_math(n['text'])]!=original_math(label_tex(text)):
        raise ValueError('Mathematics outside the drawing label transcript')
    return result


def coordinate(text):
    terms=re.findall(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)',text)
    if ''.join(terms)!=text:
        raise ValueError('Unsupported drawing coordinate')
    return sum(map(float,terms))


def expand_drawing_loops(text):
    """Expand only the two literal finite label loops in the frozen drawings."""
    from readable_chapters import split_cells
    while (match:=re.search(r'\\foreach\s+([^{}]+?)\s+in\s*\{',text)):
        variables=match[1].strip().split('/')
        if variables not in ([r'\x',r'\t'],[r'\x',r'\h',r'\t']):
            raise ValueError('Review the drawing loop variables')
        values,end=group(text,match.end()-1)
        while text[end].isspace():end+=1
        body,stop=group(text,end)
        if '\n' in text[match.start():stop]:
            raise ValueError('Review multiline drawing loop source anchors')
        items=split_cells(values,',')
        if len(items)!=3:
            raise ValueError('Review the drawing loop inventory')
        expanded=[]
        for item in items:
            bindings=split_cells(item,'/')
            if len(bindings)!=len(variables):
                raise ValueError('Irregular drawing loop values')
            rendered=body
            for variable,value in zip(variables,bindings):
                value=value.strip()
                if value.startswith('{'):
                    value,tail=group(value,0)
                    if tail!=len(bindings[variables.index(variable)].strip()):
                        raise ValueError('Unsupported drawing loop value')
                if not re.fullmatch(r'[\d./]+',value):
                    raise ValueError('Review nonliteral drawing loop value')
                rendered=re.sub(re.escape(variable)+r'\b',lambda m:value,rendered)
            expanded.append(rendered)
        text=text[:match.start()]+' '.join(expanded)+text[stop:]
    if r'\foreach' in text:
        raise ValueError('Unsupported drawing loop')
    return text


def matrix_label_blocks(nodes,source):
    """Group the original gridded labels into tables; keep all other labels."""
    cells=[]
    for match in re.finditer(r'\\path\[draw=black!30,[^\]]*\]\s*\(([-\d.]+),([-\d.]+)\) rectangle \(([-\d.]+),([-\d.]+)\)',source):
        x0,y0,x1,y1=map(float,match.groups())
        center=[(x0+x1)/2,(y0+y1)/2]
        found=[i for i,n in enumerate(nodes) if n['position'] and all(abs(a-b)<1e-5 for a,b in zip(n['position'],center))]
        if len(found)==1:
            cells.append(dict(x0=x0,y0=y0,x1=x1,y1=y1,index=found[0]))
    groups=[]
    while cells:
        component=[cells.pop(0)]; changed=True
        while changed:
            changed=False
            for cell in cells[:]:
                if any(abs(cell['x1']-cell['x0']-(other['x1']-other['x0']))<1e-5
                       and abs(cell['y1']-cell['y0']-(other['y1']-other['y0']))<1e-5
                       and ((abs(cell['x0']-other['x0'])<1e-5 and min(abs(cell['y0']-other['y1']),abs(cell['y1']-other['y0']))<1e-5)
                            or (abs(cell['y0']-other['y0'])<1e-5 and min(abs(cell['x0']-other['x1']),abs(cell['x1']-other['x0']))<1e-5))
                       for other in component):
                    component.append(cell);cells.remove(cell);changed=True
        columns=sorted({c['x0'] for c in component}); rows=sorted({c['y0'] for c in component},reverse=True)
        if len(component)>1 and len(component)==len(columns)*len(rows):
            groups.append([[next(c['index'] for c in component if c['x0']==x and c['y0']==y) for x in columns] for y in rows])
    lookup={index:(number,rows) for number,rows in enumerate(groups,1) for row in rows for index in row}
    seen=set();blocks=[]
    for index in range(len(nodes)):
        if index in lookup:
            number,rows=lookup[index]
            if number in seen:continue
            seen.add(number)
            blocks.append(dict(kind='table',caption='Matrix '+str(number)+' · rows top to bottom, columns left to right',
                               headers=['Row / column']+['Column '+str(i+1) for i in range(len(rows[0]))],
                               rows=[['Row '+str(i+1)]+row for i,row in enumerate(rows)]))
        elif blocks and blocks[-1]['kind']=='text':
            blocks[-1]['nodes'].append(index)
        else:
            blocks.append(dict(kind='text',nodes=[index]))
    return blocks
