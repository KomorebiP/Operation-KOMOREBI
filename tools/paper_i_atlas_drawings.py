"""Preserve Paper I label text while excluding the TikZ node-style selector."""
import re
from readable_chapters import original_math
from reader_drawing_transcripts import drawing_nodes as shared_nodes


def drawing_nodes(source):
    text=re.sub(r'\bevery node/\.style=\{[^{}]*\}',lambda m:' '*len(m[0]),source)
    nodes=shared_nodes(text)
    if [m for node in nodes for m in original_math(node['text'])]!=original_math(source):
        raise ValueError('Paper I drawing has mathematics outside the transcript')
    return nodes
