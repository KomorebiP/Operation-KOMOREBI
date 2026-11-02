"""Expand only the four literal finite loops in the retained extension drawings."""
import re
from readable_chapters import group,split_cells
from worked_atlas_drawings import drawing_nodes as literal_nodes

LOOPS={
 'complex_core':(r'\x/\y/\n/\v','1/2.03/0/29,3.5/.28/1/4,6/0/2/0'),
 'inverse_closure':(r'\x/\y/\n','0/1/0,2/2/1,2/0/2,4/1/3'),
 'shared_family':(r'\x','0,2,3,4'),
 'quantization':(r'\x/\v','0/0,2/{1/10},4/{1/5}'),
}


def drawing_nodes(source,name):
    if r'\foreach' not in source:return literal_nodes(source)
    match=re.search(r'\\foreach\s+([^{}]+?)\s+in\s*\{',source)
    if not match or name not in LOOPS:raise ValueError('Review the drawing loop')
    values,end=group(source,match.end()-1)
    variables=match[1].strip()
    if (variables,re.sub(r'\s+','',values))!=LOOPS[name]:raise ValueError('Review the literal drawing loop inventory')
    pos=end
    while source[pos].isspace():pos+=1
    if source[pos]=='{':body,stop=group(source,pos);body_start=pos+1
    else:
        stop=source.index(';',pos)+1;body=source[pos:stop];body_start=pos
    fragments=[(source[:match.start()],0,None)]
    for item in split_cells(values,','):
        fields=split_cells(item,'/');keys=variables.split('/')
        if len(fields)!=len(keys):raise ValueError('Irregular literal drawing loop')
        bindings={}
        for key,value in zip(keys,fields):
            value=value.strip()
            if value.startswith('{'):
                value,tail=group(value,0)
                if tail!=len(fields[keys.index(key)].strip()):raise ValueError('Review the drawing loop value')
            if not re.fullmatch(r'[\d./]+',value):raise ValueError('Nonliteral drawing loop value')
            bindings[key]=value
        rendered=body
        for key,value in bindings.items():rendered=re.sub(re.escape(key)+r'\b',lambda m:value,rendered)
        fragments.append((rendered,source.count('\n',0,body_start),bindings))
    fragments.append((source[stop:],source.count('\n',0,stop),None))
    expanded=''.join(part for part,_,_ in fragments)
    if r'\foreach' in expanded:raise ValueError('Review additional drawing loops')
    nodes=literal_nodes(expanded)
    positions=list(re.finditer(r'(?:\\node|(?<!\\)\bnode)\b',expanded))
    if len(nodes)!=len(positions):raise ValueError('Drawing label origin inventory differs')
    for node,position in zip(nodes,positions):
        offset=0
        for fragment,line,bindings in fragments:
            if offset<=position.start()<offset+len(fragment):
                node['line']=line+fragment.count('\n',0,position.start()-offset)+1
                if bindings:node['loop_bindings']=bindings
                break
            offset+=len(fragment)
    return nodes
