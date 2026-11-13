"""Source-bound inclusion and presentation rules for the retained cosmology book."""
import re

BASE = 'monographs/physics/source/cosmology/'
MAIN = BASE+'Projector_Refinement_Physics_Volume_II.tex'
VALUES = [BASE+'source/generated_values.tex', BASE+'source/generated_subhalo_macros.tex']
CONTEXT = ['part_intros/part'+str(i) for i in range(1,6)]
NESTED = dict(zip(['01_general_flrw_background','08_hidden_detail_sector',
    '10_collisionless_boltzmann','14_nonlinear_structure_halos','20_linked_falsifiability'], CONTEXT))
NESTED = {'chapters/'+name: [child] for name, child in NESTED.items()}
NESTED.update({'chapters/18_cooling_feedback_reionization':['source/generated_values'],
    'chapters/19_subhalo_core_tidal_audit':['source/generated_subhalo_macros']})


def source_blocks(load, treatment):
    """Retain the opening, every ordered body input, and closing scope note."""
    from readable_chapters import clean_tex
    raw = load(MAIN)
    body = raw.split(r'\begin{document}',1)[1].split(r'\end{document}',1)[0]
    matches = list(re.finditer(r'\\input\{([^{}]+)\}', body))
    if [m[1] for m in matches] != treatment['inputs']:
        raise ValueError('Review Physics cosmology body input order')
    if body.count(r'\appendix')!=1 or not re.search(r'\\appendix\s*$',body[:matches[-3].start()]):
        raise ValueError('Review Physics cosmology appendix switch')
    skipped = body[matches[0].start():matches[-1].end()]
    if re.sub(r'\\input\{[^{}]+\}|\\appendix\b','',clean_tex(skipped)).strip():
        raise ValueError('Review Physics cosmology main-file passage coverage')
    offset = raw.index(r'\begin{document}')+len(r'\begin{document}')
    first = raw.count('\n',0,offset+matches[0].start())+1
    last = raw.count('\n',0,offset+matches[-1].end())+1
    blocks = [(MAIN,raw.count('\n',0,offset)+2,first-1)]
    for name in treatment['inputs']:
        source = BASE+name+'.tex'
        text = load(source)
        declared = re.findall(r'\\input\{([^{}]+)\}', clean_tex(text))
        if declared != NESTED.get(name,[]):
            raise ValueError('Review Physics cosmology nested input order')
        for child in declared:
            included = load(BASE+child+'.tex')
            if child in CONTEXT:
                context(included)  # A single prose-only context, expanded in place.
            else:
                from readable_chapters import group
                remaining = clean_tex(included).strip()
                while remaining:
                    declaration = re.match(r'\\newcommand\{\\[A-Za-z]+\}',remaining)
                    if not declaration:
                        raise ValueError('Review Physics cosmology generated macro input')
                    _, end = group(remaining,declaration.end())
                    remaining = remaining[end:].strip()
        blocks.append((source,1,len(text.splitlines())))
    blocks.append((MAIN,last+1,raw.count('\n',0,raw.index(r'\end{document}'))))
    return blocks


def context(raw):
    from readable_chapters import group, original_math
    if len(raw.splitlines())!=1 or not raw.startswith(r'\PhysicsContext{') or original_math(raw):
        raise ValueError('Review Physics cosmology context inclusion')
    title, end = group(raw,len(r'\PhysicsContext'))
    prose, end = group(raw,end)
    if raw[end:].strip():
        raise ValueError('Review Physics cosmology context inclusion')
    return title, prose


def normalize(text, load=None):
    """Translate print wrappers and inline the five authenticated prose contexts."""
    from physics_fiber import normalize as book_normalize
    from physics_reading import mask
    from foundational_reading import rewrite
    text = rewrite(text,'texorpdfstring',2,lambda tex,pdf:tex)
    text = re.sub(r'\\(chapter|section|subsection)\[[^\]]+\]',lambda m:'\\'+m[1],text)
    text = book_normalize(text)
    if load:
        for name in CONTEXT:
            command = r'\input{'+name+'}'
            if command in text:
                title, prose = context(load(BASE+name+'.tex'))
                text = text.replace(command,r'\begin{readerroadmap}[title={'+title+'}]'+prose+r'\end{readerroadmap}')
    for name in ['source/generated_values','source/generated_subhalo_macros']:
        text = text.replace(r'\input{'+name+'}',mask(r'\input{'+name+'}'))
    text = re.sub(r'\\begin\{monographnote\}\[([^\]]+)\]',
        lambda m:r'\begin{readerroadmap}[title={'+m[1]+'}]',text)
    text = text.replace(r'\end{monographnote}',r'\end{readerroadmap}')
    text = text.replace(r'\begin{nextsteps}',r'\begin{itemize}').replace(r'\end{nextsteps}',r'\end{itemize}')
    text = re.sub(r'\\begin\{minipage\}\[t\]\{\.49\\linewidth\}|\\end\{minipage\}|\\hfill\b',lambda m:mask(m[0]),text)
    text = re.sub(r'\\allowdisplaybreaks(?:\[\d\])?',lambda m:mask(m[0]),text)
    text = re.sub(r'\\normalfont\b',lambda m:mask(m[0]),text)
    return text


def macros(load):
    from readable_chapters import manuscript_macros, group
    text = '\n'.join(load(path) for path in [MAIN,*VALUES])
    result = manuscript_macros(text,[])
    for name in ['ip','comm']:
        match = re.search(r'\\newcommand\{\\'+name+r'\}\[2\]',text)
        if not match:
            raise ValueError('Missing Physics cosmology two-argument macro')
        body,_ = group(text,match.end())
        result[name] = dict(arguments=2,body=body)
    return result


def context_provenance(chapter, selected):
    """Expose the included member beside the parent input's source-line link."""
    for name in CONTEXT:
        command = r'\input{'+name+'}'
        if command not in selected:
            continue
        line = selected.count('\n',0,selected.index(command))+1
        node = next(n for n in chapter.nodes if n['line']==line and n['kind']=='readerroadmap')
        node['source_spans'] = [dict(source=BASE+name+'.tex',line=1,end_line=1)]


def make_chapter(text, macros, state):
    """Expand retained numeric prose macros while leaving math tokens untouched."""
    from readable_chapters import Chapter, MATH_PATTERN
    class CosmologyChapter(Chapter):
        def inline(self, text):
            numeric = {k:v for k,v in self.macros.items()
                if isinstance(v,str) and re.fullmatch(r'-?\d+(?:\.\d+)?',v)}
            def expand(prose):
                return re.sub(r'\\([A-Za-z]+)',lambda m:numeric.get(m[1],m[0]),prose)
            result, pos = [], 0
            for match in MATH_PATTERN.finditer(text):
                result.extend([expand(text[pos:match.start()]),match[0]])
                pos = match.end()
            return super().inline(''.join(result)+expand(text[pos:]))
    return CosmologyChapter(text,macros,state=state,check_refs=False)
