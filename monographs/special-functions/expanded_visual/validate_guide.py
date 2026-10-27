#!/usr/bin/env python3
"""Validate every lesson's page contract and PDF navigation."""
from pathlib import Path
import hashlib
import json
import re
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
GUIDE=ROOT/'build/Expanded_Visual_Guide.pdf'

def arguments(text,start,count):
    args=[];i=start
    for _ in range(count):
        while text[i].isspace():i+=1
        if text[i]!='{':raise ValueError(f'Expected argument at {i}')
        first=i+1;i+=1;depth=1
        while depth:
            if text[i]=='\\':i+=2;continue
            if text[i]=='{':depth+=1
            if text[i]=='}':depth-=1
            i+=1
        args.append(text[first:i-1])
    return args

def lesson_sources(path):
    text=path.read_text()
    pattern=re.compile(r'\\(input|lesson)\s*\{')
    output=[]
    for match in pattern.finditer(text):
        name=match.group(1)
        if name=='input':
            arg=arguments(text,match.end()-1,1)[0]
            nested=ROOT/(arg if arg.endswith('.tex') else arg+'.tex')
            if nested.name!='guide_macros.tex':output.extend(lesson_sources(nested))
        else:
            args=arguments(text,match.end()-1,8)
            output.append({'tag':args[0],'title':args[1],'figure':args[2],
                           'source':str(path.relative_to(ROOT)),'source_scope_note':args[7]})
    return output

def main():
    lessons=lesson_sources(ROOT/'main.tex')
    assert len(lessons)==171,len(lessons)
    assert len({x['figure'] for x in lessons})==171
    for i,item in enumerate(lessons,1):
        item['lesson']=i
        for suffix in ['.pdf','.png']:
            figure=ROOT/'figures'/(item['figure']+suffix)
            assert figure.is_file(),figure
    reader=PdfReader(GUIDE)
    seen={};page_checks=[]
    for i,page in enumerate(reader.pages,1):
        text=page.extract_text() or ''
        numbers=[int(x) for x in re.findall(r'LESSON\s+(\d+)',text)]
        assert len(numbers)<=1,(i,numbers)
        if numbers:
            n=numbers[0];assert n not in seen,(n,i)
            assert 'Source and scope.' in text,(i,'missing lesson source footer')
            assert 'Read the figure.' in text and 'Work an example.' in text,(i,'missing lesson blocks')
            assert 'Carry forward.' in text,(i,'missing carry block')
            resources=page['/Resources'].get_object()
            assert resources.get('/XObject'),(i,'missing figure resource')
            seen[n]=i
            lessons[n-1]['physical_page']=i
        page_checks.append({'physical_page':i,'lesson':numbers[0] if numbers else None,
                            'text_characters':len(text)})
    assert sorted(seen)==list(range(1,172)),sorted(set(range(1,172))-set(seen))
    named=reader.named_destinations
    for name,dest in named.items():
        assert 0<=reader.get_destination_page_number(dest)<len(reader.pages),name
    links=0
    for page in reader.pages:
        for ann in page.get('/Annots',[]):
            ann=ann.get_object();dest=ann.get('/Dest');action=ann.get('/A')
            if action is not None and action.get_object().get('/S')=='/GoTo':dest=action.get_object().get('/D')
            if dest is None:continue
            if isinstance(dest,str):assert str(dest) in named,str(dest)
            else:
                target=dest.get_object()[0].get_object()
                assert reader.get_page_number(target)>=0
            links+=1
    report={'guide':GUIDE.name,'physical_pages':len(reader.pages),'lessons':len(lessons),
            'one_page_per_lesson':True,'all_required_blocks_present':True,
            'named_destinations_valid':len(named),'internal_links_valid':links,
            'pdf_sha256':hashlib.sha256(GUIDE.read_bytes()).hexdigest(),
            'author':reader.metadata.author,'page_checks':page_checks,'all_passed':True}
    (ROOT/'build/lesson_index.json').write_text(json.dumps(lessons,indent=2)+'\n')
    (ROOT/'build/STRUCTURAL_QA.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='page_checks'}))

if __name__=='__main__':main()
