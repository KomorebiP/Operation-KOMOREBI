"""Source-preserving label transcripts shared by the HTML visual atlases.

Only literal drawing labels and the retained finite loops are interpreted.
Geometry is used for reading order and table structure, not as proof evidence.
"""
import re
from readable_chapters import group,original_math,MATH_PATTERN


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
    result=[];label_spans=[]
    pattern=r'(?:\\node|(?<!\\)\bnode)(?:\[[^\]]*\])?(?:\s*\([A-Za-z0-9_:-]+\))?(?:\s*at\s*\(([-+\d.]+),\s*([-+\d.]+)\))?\s*\{'
    for match in re.finditer(pattern,text):
        value,end=group(text,match.end()-1)
        label_spans.append((match.end(),end-1))
        if not text[end:].lstrip().startswith((';','(')):
            raise ValueError('Unsupported drawing label tail')
        result.append(dict(text=label_tex(value),source_text=value,
                           position=[coordinate(match[1]),coordinate(match[2])] if match[1] else None,
                           line=text.count('\n',0,match.start())+1))
    # A label may itself say "Filled node". Inventory commands outside the
    # label bodies, rather than treating that ordinary word as TikZ syntax.
    outside=text
    for start,end in reversed(label_spans):outside=outside[:start]+(' '*(end-start))+outside[end:]
    if len(result)!=len(re.findall(r'(?:\\node|(?<!\\)\bnode)\b',outside)):
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
    """Recover literal, regular cell grids without interpreting their values.

    Drawings use absolute and relative rectangles, several border colours,
    and small gaps between cells. Accept only complete rectangular grids with
    one centred mathematical label per cell. Every other label stays in the
    transcript; unique aligned axis labels become real table headers.
    """
    cells=[]
    number=r'([-+]?\d*\.?\d+)'
    rectangle=r'\\(?:path|draw|filldraw)(?:\[[^\]]*\])?\s*\(\s*'+number+r'\s*,\s*'+number+r'\s*\)\s*rectangle\s*(\+\+)?\(\s*'+number+r'\s*,\s*'+number+r'\s*\)'
    for match in re.finditer(rectangle,source):
        command=match[0].split('(',1)[0]
        if command.startswith(r'\path') and not re.search(r'(?:\[|,)\s*(?:draw|fill)(?:=|,|\])',command):continue
        x0,y0=float(match[1]),float(match[2]);x1,y1=float(match[4]),float(match[5])
        if match[3]:x1+=x0;y1+=y0
        x0,x1=sorted((x0,x1));y0,y1=sorted((y0,y1))
        width,height=x1-x0,y1-y0
        if min(width,height)<=0:continue
        center=[(x0+x1)/2,(y0+y1)/2]
        tolerance=min(width,height)*.13
        found=[i for i,n in enumerate(nodes) if n.get('position') and all(abs(a-b)<=tolerance for a,b in zip(n['position'],center))]
        if len(found)!=1:continue
        index=found[0];value=nodes[index]['text'].strip()
        if not (MATH_PATTERN.fullmatch(value) or re.fullmatch(r'[-+\d./·⋅…]+',value)):continue
        previous=next((c for c in cells if c['index']==index),None)
        if previous:
            if (previous['x1']-previous['x0'])*(previous['y1']-previous['y0'])<=width*height:continue
            cells.remove(previous)
        cells.append(dict(x0=round(x0,5),y0=round(y0,5),x1=round(x1,5),y1=round(y1,5),index=index))
    all_cells={c['index'] for c in cells}
    groups=[]
    while cells:
        component=[cells.pop(0)]; changed=True
        while changed:
            changed=False
            for cell in cells[:]:
                if any(abs(cell['x1']-cell['x0']-(other['x1']-other['x0']))<1e-5
                       and abs(cell['y1']-cell['y0']-(other['y1']-other['y0']))<1e-5
                       and ((abs(cell['x0']-other['x0'])<1e-5 and 0<abs(cell['y0']-other['y0'])<=(cell['y1']-cell['y0'])*1.6)
                            or (abs(cell['y0']-other['y0'])<1e-5 and 0<abs(cell['x0']-other['x0'])<=(cell['x1']-cell['x0'])*1.6))
                       for other in component):
                    component.append(cell);cells.remove(cell);changed=True
        columns=sorted({c['x0'] for c in component}); rows=sorted({c['y0'] for c in component},reverse=True)
        regular=lambda values:len(values)<3 or max(abs((b-a)-(values[1]-values[0])) for a,b in zip(values,values[1:]))<1e-4
        if min(len(columns),len(rows))<2 or len(component)!=len(columns)*len(rows) or not regular(columns) or not regular(rows):continue
        grid=[[next(c['index'] for c in component if c['x0']==x and c['y0']==y) for x in columns] for y in rows]
        groups.append(dict(cells=component,grid=grid))
    claimed=set(all_cells);blocks_by_group=[]
    for number,data in enumerate(groups,1):
        component,grid=data['cells'],data['grid'];first=component[0]
        width,height=first['x1']-first['x0'],first['y1']-first['y0']
        left=min(c['x0'] for c in component);top=max(c['y1'] for c in component)
        def headers(positions,axis):
            result=[]
            for position in positions:
                found=[]
                for index,node in enumerate(nodes):
                    point=node.get('position')
                    if index in claimed or not point:continue
                    aligned=abs(point[1-axis]-position[1-axis])<=min(width,height)*.13
                    distance=left-point[0] if axis==0 else point[1]-top
                    if aligned and 0<distance<=(width if axis==0 else height)*2:
                        found.append((distance,index))
                if not found:return []
                result.append(min(found)[1])
            return result if len(set(result))==len(result) else []
        row_headers=headers([nodes[row[0]]['position'] for row in grid],0)
        column_headers=headers([nodes[index]['position'] for index in grid[0]],1)
        if set(row_headers)&set(column_headers):row_headers=[];column_headers=[]
        claimed.update(row_headers+column_headers)
        blocks_by_group.append(dict(kind='table',caption='Drawing grid '+str(number)+' · rows top to bottom, columns left to right',
            headers=['Row / column']+(column_headers or ['Column '+str(i+1) for i in range(len(grid[0]))]),
            rows=[[(row_headers[i] if row_headers else 'Row '+str(i+1))]+row for i,row in enumerate(grid)]))
    lookup={index:number for number,block in enumerate(blocks_by_group)
            for index in [*block['headers'],*[value for row in block['rows'] for value in row]] if isinstance(index,int)}
    seen=set();blocks=[]
    for index in range(len(nodes)):
        if index in lookup:
            number=lookup[index]
            if number in seen:continue
            seen.add(number)
            blocks.append(blocks_by_group[number])
        elif blocks and blocks[-1]['kind']=='text':
            blocks[-1]['nodes'].append(index)
        else:
            blocks.append(dict(kind='text',nodes=[index]))
    return blocks
