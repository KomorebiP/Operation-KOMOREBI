"""Prepare a source-bound HTML reading edition without editing retained inputs."""
from pathlib import Path
import argparse,collections,copy,gzip,hashlib,html,json,re,shutil,subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'output/MNR'
WORK=ROOT/'output/mnr-html-work'
PANDOC=ROOT/'output/vendor/pandoc-3.13/pandoc.exe'

def group(text,pos):
    if text[pos]!='{':raise ValueError('Expected TeX group')
    start=pos+1;depth=1;pos+=1
    while depth:
        if text[pos]=='\\':pos+=2;continue
        if text[pos]=='{':depth+=1
        if text[pos]=='}':depth-=1
        pos+=1
    return text[start:pos-1],pos

def normalized_tables(text):
    """Adapt printer column widths; keep cell text and mathematics unchanged."""
    out=[];pos=0
    pattern=re.compile(r'\\begin\{(tabularx|longtable|tabular)\}(?:\[[^\]]*\])?\s*\{')
    while m:=pattern.search(text,pos):
        kind=m[1];first,end=group(text,m.end()-1)
        if kind=='tabularx':
            while text[end].isspace():end+=1
            columns,end=group(text,end)
        else:columns=first
        columns=re.sub(r'[PL](?=\{)','p',columns)
        columns=re.sub(r'[XY]',lambda _:r'p{.3\linewidth}',columns)
        replacement='\\begin{'+('tabular' if kind=='tabularx' else kind)+'}{'+columns+'}'
        out.extend([text[pos:m.start()],replacement]);pos=end
    out.append(text[pos:]);result=''.join(out)
    return result.replace(r'\end{tabularx}',r'\end{tabular}')

def bibliography_markup(text):
    labels=dict(re.findall(r'\\bibcite\{([^}]+)\}\{([^}]+)\}',(SOURCE/'main.aux').read_text(encoding='utf-8')))
    text=re.sub(r'\\begin\{thebibliography\}\{[^}]+\}',lambda _:r'\begin{description}',text)
    text=text.replace(r'\end{thebibliography}',r'\end{description}')
    def item(m):
        key=m[2];label=m[1] or labels[key]
        return r'\item[{['+label+r']}]\hypertarget{bib-'+key+'}{} '
    return re.sub(r'\\bibitem(?:\[([^]]+)\])?\{([^}]+)\}',item,text)

def prose_layout(text):
    """Expose text hidden in typesetting boxes, protecting math and code verbatim."""
    import sys
    sys.path.insert(0,str(ROOT/'site/tools'))
    from readable_chapters import MATH_PATTERN
    protected=[]
    def freeze(m):
        protected.append(m[0]);return 'MNRFROZENCONTENT'+str(len(protected)-1)+'TOKEN'
    text=re.sub(r'\\begin\{(lstlisting|verbatim|Verbatim)\}[\s\S]*?\\end\{\1\}',freeze,text)
    text=MATH_PATTERN.sub(freeze,text)
    # Pandoc interprets LaTeX's literal-file \path as a drawing command and
    # otherwise drops its argument, including names in source-register cells.
    text=re.sub(r'\\(?:protect\s*\\)?path\s*(?=\{)',lambda _:r'\nolinkurl',text)
    for command,args,keep in [('fbox',1,0),('parbox',2,1),('textcolor',2,1)]:
        pattern=re.compile(r'\\'+command+r'(?:\[[^]]*\])?\s*\{')
        pos=0
        while m:=pattern.search(text,pos):
            values=[];end=m.end()-1
            for _ in range(args):
                while text[end].isspace():end+=1
                value,end=group(text,end);values.append(value)
            replacement=values[keep];text=text[:m.start()]+replacement+text[end:];pos=m.start()
    text=re.sub(r'\\begin\{minipage\}(?:\[[^]]*\])?\s*\{[^}]+\}',lambda _:r'\begin{mnrpanel}',text).replace(r'\end{minipage}',r'\end{mnrpanel}')
    text=re.sub(r'\\fontsize\{[^}]+\}\{[^}]+\}|\\color\{[^}]+\}','',text)
    text=re.sub(r'\\(?:sffamily|rmfamily|ttfamily|small|footnotesize|scriptsize|tiny|large|Large|LARGE|huge|Huge|bfseries|itshape|normalfont|normalsize|selectfont|centering|raggedright)\b','',text)
    for i,value in enumerate(protected):text=text.replace('MNRFROZENCONTENT'+str(i)+'TOKEN',value)
    return text

def prepare():
    WORK.mkdir(parents=True,exist_ok=True)
    for folder in ['chapters','definitions','sources']:
        shutil.copytree(SOURCE/folder,WORK/folder,dirs_exist_ok=True)
    for p in SOURCE.glob('*.tex'):shutil.copyfile(p,WORK/p.name)
    # Explicit semantic forms prevent the LaTeX reader from dropping prose
    # hidden inside printer-only font/colour switches. Arguments are untouched.
    definitions=WORK/'definitions/components.tex'
    with definitions.open('a',encoding='utf-8',newline='\n') as stream:
        stream.write(r'''
\renewcommand{\Corequestion}[1]{\par\textbf{#1}\par}
\renewcommand{\PPTcalloutbox}[2]{\par\textbf{#1}\par #2\par}
\renewcommand{\PPTstudyhead}[2]{\subsection*{Visual study #1: #2}}
\renewcommand{\CRformal}[1]{\par\textit{Formal counterpart:} \nolinkurl{#1}.\par}
\renewcommand{\CRsourcescope}[1]{\par #1\par}
\renewcommand{\CRrecord}[3]{\par\textbf{\nolinkurl{#1}} (line #2)\par #3\par}
\renewcommand{\CRmoduleheading}[2]{\section{#1}\label{CR:#2}\textit{Source:} \nolinkurl{lean/KomorebiRepair/#1.lean}.\par}
\renewcommand{\SRWTcenterbox}[1]{\begin{quote}#1\end{quote}}
\renewcommand{\LSMAtlasplate}[4]{\subsection*{#1: #2}\textit{#4}\par #3\par}
\renewcommand{\LSMAtlasclaim}[1]{\par\textbf{The mathematical point.} #1\par}
\renewcommand{\LSMAtlasboundary}[1]{\par\textbf{Scope.} #1\par}
\renewcommand{\LSMAtlasnav}[1]{\par\textbf{Formal route.} #1\par}
''')
    for p in [WORK/'main.tex',*(WORK/'chapters').glob('*.tex')]:
        raw=p.read_text(encoding='utf-8')
        if p.name=='main.tex':
            before,separator,after=raw.partition(r'\begin{document}');raw=before+separator+prose_layout(after)
        else:raw=prose_layout(raw)
        p.write_text(bibliography_markup(normalized_tables(raw)),encoding='utf-8',newline='\n')
    p=WORK/'main.tex'
    result=subprocess.run([str(PANDOC),'--from=latex','--to=json','main.tex','--output=reading.json'],cwd=WORK,capture_output=True,text=True)
    (WORK/'pandoc-console.txt').write_text(result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(result.stderr)
    data=json.loads((WORK/'reading.json').read_bytes());counts=collections.Counter();raw=[]
    def walk(x):
        if isinstance(x,list):
            for y in x:walk(y)
        elif isinstance(x,dict):
            counts[x.get('t')]+=1
            if x.get('t') in ('RawBlock','RawInline'):raw.append(x['c'])
            for y in x.values():walk(y)
    walk(data['blocks'])
    (WORK/'conversion-inventory.json').write_text(json.dumps({'types':dict(counts),'raw':raw},indent=2),encoding='utf-8')
    print(json.dumps({'phase':'prepared','blocks':len(data['blocks']),'types':dict(counts),'raw':len(raw)}),flush=True)

def plain(x):
    if isinstance(x,list):return ''.join(plain(y) for y in x)
    if not isinstance(x,dict):return ''
    t=x.get('t');c=x.get('c')
    if t in ('Space','SoftBreak','LineBreak'):return ' '
    if t in ('Str','Code'):return c if isinstance(c,str) else c[-1]
    if t=='Math':return c[1]
    if t in ('Link','Image','Span'):return plain(c[1])
    return plain(c)

def walk(x):
    if isinstance(x,list):
        for y in x:yield from walk(y)
    elif isinstance(x,dict):
        if 't' in x:yield x
        for y in x.values():yield from walk(y)

def aux_labels():
    result={};text=(SOURCE/'main.aux').read_text(encoding='utf-8')
    for m in re.finditer(r'\\newlabel\{([^}]+)\}\{',text):
        if m[1].endswith('@cref'):continue
        body,end=group(text,m.end()-1);values=[];pos=0
        while pos<len(body) and body[pos]=='{':
            value,pos=group(body,pos);values.append(value)
        if len(values)>=4:result[m[1]]=dict(number=values[0],page=values[1],title=values[2],destination=values[3])
    return result

def toc_entries():
    text=(SOURCE/'main.toc').read_text(encoding='utf-8');result=[]
    for m in re.finditer(r'\\contentsline\s*\{([^}]+)\}\{',text):
        title,end=group(text,m.end()-1);page,end=group(text,end);destination,end=group(text,end)
        number=''
        if title.startswith(r'\numberline '):
            number,pos=group(title,title.index('{'));title=title[pos:]
        elif m[1]=='part':
            part=re.match(r'([IVX]+)\\hspace\s*\{1em\}(.*)',title)
            if part:number,title=part.groups()
        result.append(dict(kind=m[1],title_tex=title,number=number,page=page,destination=destination))
    document='\\documentclass{book}\n'+(SOURCE/'definitions/components.tex').read_text(encoding='utf-8')+'\n\\begin{document}\n'
    document+='\n'.join(r'\section*{'+prose_layout(r['title_tex'])+r'}\label{mnr-toc-'+str(i)+'}' for i,r in enumerate(result))
    document+='\n\\end{document}\n'
    (WORK/'toc-labels.tex').write_text(document,encoding='utf-8',newline='\n')
    subprocess.run([str(PANDOC),'--from=latex','--to=json','toc-labels.tex','--output=toc-labels.json'],cwd=WORK,check=True,capture_output=True)
    data=json.loads((WORK/'toc-labels.json').read_bytes())
    for node in data['blocks']:
        if node['t']=='Header':
            i=int(node['c'][1][0].removeprefix('mnr-toc-'));result[i]['title']=plain(node['c'][2])
    return result

def render_figures():
    import pypdfium2 as pdf
    import pdfplumber
    from PIL import Image
    output=WORK/'figures';output.mkdir(exist_ok=True)
    rawpdf=ROOT/'output/mnr-figure-work/figure-export.pdf'
    document=pdf.PdfDocument(rawpdf);metadata=[]
    with pdfplumber.open(rawpdf) as extracted:
        for i in range(len(document)):
            page=document[i];width,height=page.get_size();text=extracted.pages[i].extract_text() or ''
            matches=extracted.pages[i].search(r'Figure\s*([\d.]+):',regex=True)
            match=matches[-1] if matches else None
            bitmap=page.render(scale=1600/width).to_pil().convert('RGB')
            cropped=False
            if match and match['top']>height*.25:
                bitmap=bitmap.crop((0,0,bitmap.width,max(1,int((match['top']-2)*1600/width))))
                cropped=True
            path=output/('figure-'+str(i+1).zfill(3)+'.webp');bitmap.save(path,format='WEBP',lossless=True,method=6)
            metadata.append(dict(file=path.name,width=bitmap.width,height=bitmap.height,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,number=match['groups'][0] if match else '',caption_cropped=cropped,pdf_page=i+1))
    # Standalone plates are already retained vector files, outside figure floats.
    data=json.loads((WORK/'reading.json').read_bytes());images=[]
    def outside(x,inside=False):
        if isinstance(x,list):
            for y in x:outside(y,inside)
        elif isinstance(x,dict):
            if x.get('t')=='Figure':inside=True
            if x.get('t')=='Image' and not inside:images.append(x['c'][2][0])
            for y in x.values():outside(y,inside)
    outside(data['blocks'])
    for i,source in enumerate(dict.fromkeys(images),1):
        sourcepdf=pdf.PdfDocument(SOURCE/source);page=sourcepdf[0];width,height=page.get_size()
        image=page.render(scale=1600/width).to_pil().convert('RGB');path=output/('plate-'+str(i).zfill(3)+'.webp');image.save(path,format='WEBP',lossless=True,method=6)
        metadata.append(dict(file=path.name,width=image.width,height=image.height,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,source=source))
    (WORK/'figures.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'phase':'images','floats':len(document),'plates':len(images),'bytes':sum(x['bytes'] for x in metadata),'uncropped':[x['file'] for x in metadata if 'caption_cropped' in x and not x['caption_cropped']]}),flush=True)

def attributes(node):
    t=node.get('t');c=node.get('c')
    if t=='Header':return c[1]
    if t in ('Div','Span','Figure','Image','Link','Table','Code','CodeBlock'):return c[0]
    return None

def canonical_title(text):
    return re.sub(r'\s+',' ',text).strip().casefold()

def render_pages():
    from pypdf import PdfReader
    document=json.loads((WORK/'reading.json').read_bytes())
    toc=toc_entries();labels=aux_labels();toc_index=0;heading_matches=[];unmatched=[]
    levels={'part':1,'chapter':2,'section':3,'subsection':4,'subsubsection':5,'paragraph':6}
    for node in walk(document['blocks']):
        if node.get('t')!='Header':continue
        c=node['c'];title=canonical_title(plain(c[2]))
        expected=toc[toc_index] if toc_index<len(toc) else None
        if expected and c[0]==levels[expected['kind']] and title==canonical_title(expected['title']):
            heading_matches.append((node,expected));toc_index+=1
            c[1][2].append(['data-source-number',expected['number']])
        elif 'unnumbered' not in c[1][1]:unmatched.append((c[0],c[1][0],plain(c[2]),expected and expected['title']))
    (WORK/'heading-matches.json').write_text(json.dumps({'matched':toc_index,'total':len(toc),'unmatched':unmatched,'remaining':toc[toc_index:toc_index+4]},ensure_ascii=False,indent=2),encoding='utf-8')
    if toc_index!=len(toc):raise ValueError('TOC alignment incomplete: '+str(toc_index)+'/'+str(len(toc)))
    theorem_trace=[line.split('|')[1:] for line in (ROOT/'output/mnr-figure-work/figure-export.numbers').read_text().splitlines() if line.startswith('ENV|')]
    theorem_types={x[0] for x in theorem_trace};theorem_pos=0;theorem_records=[];proof_count=0
    for node in walk(document['blocks']):
        if node.get('t')!='Div':continue
        attr,blocks=node['c'];kind=next((x for x in attr[1] if x in theorem_types),None)
        if 'proof' in attr[1]:
            proof_count+=1
            if not attr[0]:attr[0]='proof-'+str(proof_count)
        if not kind:continue
        actual,number=theorem_trace[theorem_pos];theorem_pos+=1
        if actual!=kind:raise ValueError('Statement order changed')
        strong=next(x for x in walk(blocks[0]) if x.get('t')=='Strong')
        if strong['c'][-1]['t']!='Str':raise ValueError('Unrecognized statement number')
        strong['c'][-1]['c']=number
        if not attr[0]:attr[0]='statement-'+str(theorem_pos)
        if attr[0] in labels and labels[attr[0]]['number']!=number:
            raise ValueError('Statement number differs from compiled PDF: '+attr[0])
        short=re.sub(r'^(Core|KS|GA|LSM|PRIQ|MU|PPT|CR|SII|SRWT|MS)','',kind)
        attr[1].extend(['mnr-statement',short]);attr[2].extend([['data-statement-number',number],['data-statement-kind',short]])
        theorem_records.append(dict(id=attr[0],kind=short,number=number,title=plain(blocks[0]['c'])[:260]))
    if theorem_pos!=len(theorem_trace) or proof_count!=527:raise ValueError('Statement/proof inventory changed')
    # Split at actual chapter boundaries; part introductions travel with the next chapter.
    pages=[];pending=[];part='Introduction';current=None
    for block in document['blocks']:
        if block['t']=='Div' and 'titlepage' in block['c'][0][1]:continue
        if block['t']=='Header' and block['c'][0]==1:
            part=plain(block['c'][2]);pending=[];current=None;continue
        if block['t']=='Header' and block['c'][0]==2:
            identifier=block['c'][1][0];m=re.search(r':book:chapter-(\d+)$',identifier)
            number=int(m[1]) if m else None
            filename='chapter-'+str(number).zfill(2)+'.html' if number else identifier.replace(':','-')+'.html'
            current=dict(file=filename,id=identifier,title=plain(block['c'][2]),chapter=number,part=part,blocks=[*pending],headings=[])
            pages.append(current);pending=[];continue
        if current is None:pending.append(block)
        else:current['blocks'].append(block)
    if [p['chapter'] for p in pages if p['chapter']]!=list(range(1,98)):raise ValueError('Missing numbered chapter')
    owners={p['id']:(p['file'],p['id']) for p in pages};id_nodes={};math_labels={};header_by_destination={}
    for page in pages:
        for node in walk(page['blocks']):
            attr=attributes(node)
            if attr and isinstance(attr[0],str) and attr[0]:
                if attr[0] in owners:raise ValueError('Duplicate reading anchor: '+attr[0])
                owners[attr[0]]=(page['file'],attr[0]);id_nodes[attr[0]]=node
            if node.get('t')=='Math':
                for key in re.findall(r'\\label\{([^}]+)\}',node['c'][1]):
                    if key in owners:raise ValueError('Repeated equation label: '+key)
                    owners[key]=(page['file'],key);math_labels[key]=node
    for node,entry in heading_matches:
        identifier=node['c'][1][0]
        if identifier in owners:header_by_destination[entry['destination']]=owners[identifier]
    destinations=dict(header_by_destination)
    for key,value in labels.items():
        if key in owners:destinations.setdefault(value['destination'],owners[key])
    aliases={}
    for key,value in labels.items():
        if key not in owners and value['destination'] in destinations:
            owners[key]=destinations[value['destination']];aliases[key]=owners[key]
    citation_labels=dict(re.findall(r'\\bibcite\{([^}]+)\}\{([^}]+)\}',(SOURCE/'main.aux').read_text(encoding='utf-8')))
    reference_kinds=dict(re.findall(r'\\newlabel\{([^}]+)@cref\}\{\{\[([^]]+)\]',(SOURCE/'main.aux').read_text(encoding='utf-8')))
    figures=json.loads((WORK/'figures.json').read_bytes());floats=[f for f in figures if 'pdf_page' in f];plates={f['source']:f for f in figures if 'source' in f}
    figure_index=0;references=0;citations=0;missing=[];diagrams=0
    def link(key,display):
        if key not in owners:
            missing.append(key);return dict(t='Str',c='UNRESOLVED:'+key)
        filename,identifier=owners[key]
        return dict(t='Link',c=[['',[],[]],[dict(t='Str',c=display)],[filename+'#'+identifier,'']])
    def convert(node,page):
        nonlocal figure_index,references,citations,diagrams
        if isinstance(node,list):return [convert(x,page) for x in node]
        if not isinstance(node,dict):return node
        t=node.get('t');c=node.get('c')
        if t=='Cite':
            citations+=1;content=[dict(t='Str',c='[')]
            for i,citation in enumerate(c[0]):
                key=citation['citationId']
                if i:content.extend([dict(t='Str',c=','),dict(t='Space')])
                content.extend(convert(citation.get('citationPrefix',[]),page));content.append(link('bib-'+key,citation_labels.get(key,key)))
                content.extend(convert(citation.get('citationSuffix',[]),page))
            content.append(dict(t='Str',c=']'))
            return dict(t='Span',c=[['',['mnr-citation'],[]],content])
        if t=='Link':
            properties=dict(c[0][2]);key=properties.get('reference')
            if key:
                references+=1;kind=properties.get('reference-type','ref');record=labels.get(key)
                if kind in ('ref+Label','ref+label'):
                    keys=key.split(',');first=keys[0]
                    category=reference_kinds.get(first,labels.get(first,{}).get('destination','reference').split('.')[0])
                    category=re.sub(r'^(Core|KS|GA|LSM|PRIQ|MU|PPT|CR|SII|SRWT|MS)','',category)
                    if category in ('subsection','subsubsection'):category='section'
                    if len(keys)>1:category={'boundary':'boundaries'}.get(category,category+'s')
                    if kind=='ref+Label':category=category.capitalize()
                    content=[dict(t='Str',c=category),dict(t='Space')]
                    for i,k in enumerate(keys):
                        if i:content.extend([dict(t='Str',c=' and ' if i==len(keys)-1 else ', ')])
                        content.append(link(k,labels.get(k,{}).get('number',k)))
                    return dict(t='Span',c=[['',[],[]],content])
                if not record:missing.append(key)
                display=(record['page'] if kind=='pageref' else record['number']) if record else key
                if kind=='eqref':display='('+display+')'
                if kind=='nameref':display=record['title']
                return link(key,display)
            if c[2][0].startswith('#') and c[2][0][1:] in owners:
                key=c[2][0][1:];filename,identifier=owners[key];c[2][0]=filename+'#'+identifier
        if t=='Figure':
            info=floats[figure_index];figure_index+=1
            attr,caption,body=c;extra=[]
            for child in walk(body):
                a=attributes(child)
                if a and a[0] and a[0]!=attr[0]:extra.append(dict(t='RawInline',c=['html','<span class="figure-anchor" id="'+html.escape(a[0],quote=True)+'"></span>']))
            nested=[x for x in walk(body) if x.get('t')=='Figure']
            cap=convert(caption,page)
            for i,child in enumerate(nested):
                cap[1].append(dict(t='Para',c=[dict(t='Str',c='('+chr(97+i)+') ')]+convert(child['c'][1][1][0]['c'],page)))
            image=dict(t='Image',c=[['',[],[['width',str(info['width'])],['height',str(info['height'])]]],[dict(t='Str',c='Figure '+info.get('number','')+'. '+plain(caption[1])[:240])],['mnr-figure/'+info['file'],'']])
            return dict(t='Figure',c=[attr,cap,[dict(t='Plain',c=extra+[image])]])
        if t=='Image' and c[2][0] in plates:
            info=plates[c[2][0]];c[2][0]='mnr-figure/'+info['file'];c[0][2]=[['width',str(info['width'])],['height',str(info['height'])]]
            if not c[1]:c[1]=[dict(t='Str',c=page['title']+' — original visual plate')]
        if t=='Math':
            tex=c[1];keys=re.findall(r'\\label\{([^}]+)\}',tex)
            if r'\begin{minipage}' in tex:
                prose=re.fullmatch(r'\s*\\boxed\{\\begin\{minipage\}\{[^}]+\}\s*(.*?)\s*\\end\{minipage\}\}\s*',tex,re.S)
                if not prose or '\\' in prose[1]:raise ValueError('Review a mixed prose/mathematics box')
                return dict(t='RawInline',c=['html','<span class="mnr-callout">'+html.escape(' '.join(prose[1].split()))+'</span>'])
            if 'tikzcd' in tex:
                diagrams+=1
                anchors=''.join('<span id="'+html.escape(k,quote=True)+'"></span>' for k in keys)
                alt=['Commutative triangle: E maps O to V; the inclusion of O and q_D from V both map to Q_D.',"Commutative square: D maps U to V, a maps U to U-prime, b maps V to V-prime, and D-prime maps U-prime to V-prime; bD equals D-prime a."][diagrams-1]
                return dict(t='RawInline',c=['html',anchors+'<img class="mnr-commutative" src="mnr-figure/diagram-'+str(diagrams)+'.webp" width="1600" alt="'+html.escape(alt,quote=True)+'">'])
            tex=tex.replace(r'\ensuremath','').replace(r'\qedhere','').replace(r'\llbracket','⟦').replace(r'\rrbracket','⟧')
            def reference(m):
                nonlocal references
                references+=1;key=m[2]
                if key not in labels or key not in owners:missing.append(key);return m[0]
                value=labels[key]['page'] if m[1]=='pageref' else labels[key]['number']
                if m[1]=='eqref':value='('+value+')'
                file,identifier=owners[key]
                return r'\href{'+file+'#'+identifier+r'}{\text{'+value+'}}'
            tex=re.sub(r'\\(eqref|ref|pageref)\{([^}]+)\}',reference,tex)
            numbers=set()
            def label(m):
                key=m[1];number=labels.get(key,{}).get('number','')
                if c[0]['t']=='DisplayMath' and number and number not in numbers and r'\tag{' not in c[1]:
                    numbers.add(number);return r'\tag{'+number+'}'
                return ''
            tex=re.sub(r'\\label\{([^}]+)\}',label,tex);c[1]=tex
            if keys:
                anchors=''.join('<span class="equation-anchor" id="'+html.escape(k,quote=True)+'"></span>' for k in keys)
                return dict(t='Span',c=[['',[],[]],[dict(t='RawInline',c=['html',anchors]),node]])
            return node
        if t=='Header':
            number=dict(c[1][2]).get('data-source-number','')
            if number:c[2]=[dict(t='Str',c=number),dict(t='Space')]+c[2]
            c[0]=max(2,c[0]-1)
        return {key:(convert(value,page) if key!='c' or t not in ('Math',) else value) for key,value in node.items()}
    combined=[]
    for i,page in enumerate(pages):
        page['blocks']=convert(page['blocks'],page)
        page['headings']=[dict(id=n['c'][1][0],level=n['c'][0],title=plain(n['c'][2])) for n in walk(page['blocks']) if n.get('t')=='Header']
        combined.append(dict(t='RawBlock',c=['html','<!--MNR-PAGE:'+str(i)+'-->']));combined.extend(page['blocks'])
    if missing:raise ValueError('Unresolved HTML references: '+str(sorted(set(missing))[:30]))
    if figure_index!=len(floats) or diagrams!=2:raise ValueError('Figure sequence changed')
    document['blocks']=combined;(WORK/'rendered.json').write_text(json.dumps(document,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    subprocess.run([str(PANDOC),'--from=json','--to=html5','--math-method=mathjax','--wrap=none','rendered.json','--output=rendered.html'],cwd=WORK,check=True,capture_output=True)
    rendered=(WORK/'rendered.html').read_text(encoding='utf-8');chunks=re.split(r'<!--MNR-PAGE:\d+-->\s*',rendered)
    if len(chunks)!=len(pages)+1:raise ValueError('Page boundaries changed')
    out=WORK/'pages';out.mkdir(exist_ok=True)
    for page,body in zip(pages,chunks[1:]):
        body=body.replace('class="math inline"','class="arithmatex math-inline"').replace('class="math display"','class="arithmatex math-display" tabindex="0" role="group" aria-label="Displayed equation"')
        (out/page['file']).write_text(body,encoding='utf-8',newline='\n');page.pop('blocks')
    for row in theorem_records:
        row['file']=owners[row['id']][0]
    report=dict(schema=1,pages=pages,statements=theorem_records,numbered_chapters=97,parts=13,proofs=proof_count,statement_count=theorem_pos,citations=citations,references=references,toc_entries=len(toc),figures=figure_index,standalone_plates=len(plates),commutative_diagrams=diagrams,source_zip_sha256='14e635a4e910ab3062e5618b084841eff2e0504f048130cfd336985a7c94ef25',new_proof_audit=False,new_lean_execution=False,aliases=aliases)
    (WORK/'reading-metadata.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('pages','statements','aliases')}),flush=True)

def export_figures():
    compiler=Path(json.loads((SOURCE/'BUILD_RECEIPT.json').read_bytes())['command'][0])
    if not compiler.is_file():raise FileNotFoundError(compiler)
    # Use the original layout inputs, not the HTML table adaptations.
    target=ROOT/'output/mnr-figure-work';target.mkdir(parents=True,exist_ok=True)
    for folder in ['chapters','definitions','sources']:shutil.copytree(SOURCE/folder,target/folder,dirs_exist_ok=True)
    original=(SOURCE/'main.tex').read_text(encoding='utf-8')
    definitions=(SOURCE/'definitions/components.tex').read_text(encoding='utf-8')
    environments=list(dict.fromkeys(re.findall(r'\\newtheorem\{([^}]+)\}',definitions)))
    theorem_specs=re.findall(r'\\newtheorem\{([^}]+)\}(?:\[([^]]+)\])?',definitions)
    bases={name:(base or name) for name,base in theorem_specs}
    hooks='\n'.join(r'\AddToHook{env/'+name+r'/begin}{\begingroup\expandafter\advance\csname c@'+bases[name]+r'\endcsname by 1\immediate\write\mnrtrace{ENV|'+name+'|\\the'+name+r'}\endgroup}' for name in environments)
    preamble=r'''
\usepackage[active,tightpage]{preview}
\setlength\PreviewBorder{4pt}
\newwrite\mnrtrace
\immediate\openout\mnrtrace=figure-export.numbers
\makeatletter
\newcommand{\mnrbeginfigure}{\begin{preview}\def\@captype{figure}\centering}
\newcommand{\mnrendfigure}{\end{preview}}

\makeatother
'''+hooks+'\n'
    def nonfloating(text):
        text=re.sub(r'\\begin\{figure\}(?:\[[^\]]*\])?',lambda _:r'\mnrbeginfigure',text)
        return text.replace(r'\end{figure}',r'\mnrendfigure')
    for path in [*(target/'chapters').glob('*.tex'),*(target/'definitions').glob('*.tex')]:
        path.write_text(nonfloating(path.read_text(encoding='utf-8')),encoding='utf-8',newline='\n')
    original=nonfloating(original)
    (target/'figure-export.tex').write_text(original.replace(r'\begin{document}',preamble+'\n'+r'\begin{document}',1),encoding='utf-8',newline='\n')
    shutil.copyfile(SOURCE/'main.aux',target/'figure-export.aux')
    with (target/'console.txt').open('w',encoding='utf-8') as log:
        result=subprocess.run([str(compiler),'--keep-logs','--keep-intermediates','--reruns','0','figure-export.tex'],cwd=target,stdout=log,stderr=subprocess.STDOUT)
    print(json.dumps({'phase':'figures','exit':result.returncode,'pdf_exists':(target/'figure-export.pdf').exists()}),flush=True)
    if result.returncode:raise RuntimeError((target/'console.txt').read_text(encoding='utf-8')[-4000:])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['prepare','figures']);args=p.parse_args()
    prepare() if args.phase=='prepare' else export_figures()
