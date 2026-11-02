"""Literal label transcripts, including Paper II's two-line shortstack label."""
import re
from readable_chapters import group,original_math
from reader_drawing_transcripts import drawing_nodes as shared_nodes,label_tex


def drawing_nodes(source):
    text=re.sub(r'\bevery node/\.style=\{[^{}]*\}',lambda m:' '*len(m[0]),source)
    nodes=shared_nodes(text)
    for node in nodes:
        value=node['text']
        if value.startswith(r'\shortstack{'):
            body,end=group(value,len(r'\shortstack'))
            if end!=len(value):raise ValueError('Review the drawing shortstack wrapper')
            node['text']=body
    # A TeX line break immediately before $ is presentation, not an escaped $.
    # Normalize prose line breaks before independently inventorying formulas.
    if [m for n in nodes for m in original_math(n['text'])]!=original_math(label_tex(text)):
        raise ValueError('Mathematics outside the drawing label transcript')
    return nodes
