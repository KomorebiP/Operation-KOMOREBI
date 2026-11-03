"""Literal transcripts of the retained TikZ labels, including two finite display loops."""
import re
import ast
from readable_chapters import group,split_cells
from reader_drawing_transcripts import coordinate
from worked_atlas_drawings import drawing_nodes as literal_nodes


def drawing_nodes(source,name):
    if name.startswith('inline_'):
        phrase='reduced slice' if name=='inline_nilpotent_slice' else r'$V=T$'
        match=next(m for m in re.finditer(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',source,re.S) if phrase in m[0])
        source='\n'*source.count('\n',0,match.start())+match[0]
        if name=='inline_nilpotent_slice':return literal_nodes(source)
    if name not in ['derived_fibers','inline_packet_occupancy']:return literal_nodes(source)
    # These loops only repeat labels on a five-column explanatory diagram.
    # They are not mathematical computations or proof checks.
    result=[];position=0;loops=0
    pattern=r'\\foreach\s+([^{}]+?)\s+in\s*\{'
    for match in re.finditer(pattern,source):
        prefix=source[position:match.start()]
        for node in literal_nodes(prefix):node['line']+=source.count('\n',0,position);result.append(node)
        variables=match[1].strip().split('/');values,end=group(source,match.end()-1)
        while source[end].isspace():end+=1
        body,stop=group(source,end);items=split_cells(values,',')
        contracts=[([r'\x',r'\a'],['0/-2','1.5/-1','3/0','4.5/1','6/2']),([r'\x'],['0','1.5','4.5','6'])] if name=='derived_fibers' else [([r'\j'],['0','...','4']),([r'\j'],['0','1']),([r'\j'],['2','3','4'])]
        expected=contracts[loops]
        if (variables,items)!=expected:raise ValueError('Changed Paper XII literal label loop')
        if items==['0','...','4']:items=['0','1','2','3','4']
        for item in items:
            expanded=body
            for variable,value in zip(variables,item.split('/'),strict=True):expanded=re.sub(re.escape(variable)+r'\b',lambda m:value,expanded)
            expanded=re.sub(r'\(([\d.*+-]+),([\d.*+-]+)\)',lambda m:'('+str(literal_coordinate(m[1]))+','+str(literal_coordinate(m[2]))+')',expanded)
            for node in literal_nodes(expanded):
                node['line']+=source.count('\n',0,end+1);result.append(node)
        position=stop;loops+=1
    for node in literal_nodes(source[position:]):node['line']+=source.count('\n',0,position);result.append(node)
    if loops!=(2 if name=='derived_fibers' else 3):raise ValueError('Changed Paper XII literal loop inventory')
    return result


def literal_coordinate(text):
    def visit(node):
        if isinstance(node,ast.Constant) and type(node.value) in [int,float]:return node.value
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -visit(node.operand)
        if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Add,ast.Mult)):
            a,b=visit(node.left),visit(node.right);return a+b if isinstance(node.op,ast.Add) else a*b
        raise ValueError('Unsupported literal diagram coordinate')
    return visit(ast.parse(text,mode='eval').body)
