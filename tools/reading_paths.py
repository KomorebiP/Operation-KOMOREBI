"""Reading paths for complete HTML manuscripts with HTML visual companions."""
import html
import json
import posixpath

INDEX='read/start.html'
REPORT='documents/reading-paths.json'
QUANTUM='monographs-quantum-and-circuits'
LARGE_SIGNAL='monographs-large-signal-model'
CURATED={QUANTUM:('visual','study','formal'),LARGE_SIGNAL:('introduction','study','evidence')}
EXISTING_GUIDES={*CURATED,'monographs-machine-native-reasoning'}
GROUPS={'papers':'Core papers','monographs':'Books and monographs'}


def eligible_books():
    """A PDF or source-text viewer alone does not qualify a work for a guide."""
    from readable_chapters import BOOKS
    return {work:book for work,book in BOOKS.items() if book.get('chapters') and
            not book.get('partial') and (book.get('atlas_index') or book.get('visual_guide_index'))}


def guide_url(work):
    return 'read/'+work+'/start.html'


def guide_enabled(site,work):
    """Preserve standalone curated guides; enable new guides only on the site."""
    return work in EXISTING_GUIDES or (work in eligible_books() and getattr(site,'guided_reading',False) and
        any(c['id']==work for c in getattr(site,'registry',{}).get('components',[])))


def guide_model(reader, component):
    """Choose published resources, retaining their own labels and evidence scope."""
    from readable_chapters import BOOKS, statement_directory_url
    from reader_display import has_statement_finder
    from reader_guidance import reading_passage_url
    from reader_experience import GUIDED_DEMONSTRATIONS
    from build_reader_site import document_url
    site=reader.site;work=component['id'];config=BOOKS.get(work)
    if work not in eligible_books():raise ValueError('Reading guide requires a complete HTML manuscript and HTML visual guide: '+work)
    meta=site.components[work];assessment=site.assessments[work]
    overview='collection/works/'+work+'.html'
    intro=getattr(reader,'paper_introductions',{}).get(work)
    resources=[]
    for resource in component['resources']:
        record=reader.records.get(component['destination']+'/'+resource['path'])
        if not record and resource['kind'] in {'pdf','visual'} and resource['path'].lower().endswith('.pdf'):
            raise ValueError('Missing published reading resource: '+work+'/'+resource['path'])
        if record:
            if record['work']!=work:raise ValueError('Cross-work reading resource: '+work)
            resources.append((resource,record))
    def selected(kind):return [(r['label'],record['url']) for r,record in resources if r['kind']==kind]
    def step(title,url,description):return dict(title=title,url=url,description=description)
    def unique(steps):
        seen=set();result=[]
        for item in steps:
            if not item['url']:raise ValueError('Missing reading-path destination: '+work)
            if item['url'] not in seen:result.append(item);seen.add(item['url'])
        return result
    background=reader.learning['background'][meta['group']]
    topics=[t for t in reader.learning.get('learning_topics',[]) if work in t['works']]
    if intro:
        if not any(t['id']==intro['example'] for t in topics):raise ValueError('Reading example belongs to another work: '+work)
        topics.sort(key=lambda t:t['id']!=intro['example'])
    first=[]
    for topic in topics[:2]:
        first.append(step(topic['title'],document_url('collection',topic['example']),
                          topic.get('scope','Work through the introductory calculation, then follow its source routes.')))
    for path,(title,works) in GUIDED_DEMONSTRATIONS.items():
        if work in works:
            first.append(step(title,document_url('collection',path),'Follow the worked calculation, its expected output, and its source links.'))
            break
    visual=config.get('atlas_index') or config.get('visual_guide_index')
    has_visual=bool(visual)
    if visual:
        first.append(step('Visual guide in HTML',visual,'Explore the drawings and their accompanying explanations.'))
    else:
        first.extend(step(label,url,'Read the retained visual companion and its stated scope.') for label,url in selected('visual')[:2])
    has_examples=bool(first)
    if not first:
        first.extend(step(label,url,'Read the edition’s introduction, setup, and stated limits.') for label,url in selected('guide')[:1])
    maintained=assessment.get('reader_guide')
    if maintained and ('collection',maintained) in getattr(site,'documents',{}):
        first.append(step('Maintained edition guide',document_url('collection',maintained),'Read the edition-specific orientation and qualifications.'))
    first.append(step('Question, background, and scope',overview,'Use the work overview to identify the problem and required background.'))
    if work=='monographs-cos-method':
        from kcos_routes import label_targets
        book=reader.readable_books.get(work)
        if book is None:raise ValueError('K-COS reading guide requires its prepared manuscript')
        targets=label_targets(book)
        prefix='read/'+work+'/'
        background='Useful background: multivariate Gaussian distributions, quadratic forms, eigenvalues, and numerical integration.'
        first=[step('How to read this book',prefix+'how-to-read.html','Choose the probability, operator, or numerical route that matches your background.'),
               step('Visual studies',visual,'Follow the Gaussian form, spectral packets, and probability enclosure through the visual examples.'),
               step('A worked probability enclosure',targets['sec:worked-enclosure'],'Follow the directed-enclosure calculation and its stated input and error requirements.')]
    first=unique(first)
    study=[]
    edition=assessment.get('editorial_edition')
    if edition:
        study.append(step('Revised reading edition',document_url('collection',edition['manuscript']),'Follow the maintained reading edition and its revision scope.'))
    if config:
        study.append(step('Begin the HTML reading edition',config['chapters'][0]['url'],'Start at the opening section, then use previous and next to continue in order.'))
        for group in config.get('contents_groups',[])[:5]:
            study.append(step(group['title'],group['start'],'Enter this part of the retained reading sequence.'))
        if not config.get('contents_groups'):
            study.extend(step(chapter['title'],chapter['url'],'Continue through the opening chapters in the edition’s order.')
                         for chapter in config['chapters'][1:4] if chapter.get('title'))
        study.append(step('Full contents',config['index'],'Choose any chapter or companion section from the complete contents.'))
    else:
        study.extend(step(label,url,'Read the on-site PDF with selectable text and page navigation.') for label,url in selected('pdf')[:4])
        study.extend(step(label,url,'Inspect the retained manuscript text alongside the typeset edition.') for label,url in selected('text')[:2])
        if not study:
            study.extend(step(label,url,'Follow the supplied setup and usage sequence.') for label,url in selected('guide')[:2])
    study.append(step('All reading files',overview+'#read','Return to the edition’s full reading-file list.'))
    evidence=[]
    if intro:
        setup=intro['setup'];claim=next(c for c in site.claims['records'] if c['id']==intro['claim'])
        if claim['work_id']!=work:raise ValueError('Cross-work reading claim: '+work)
        def passage(path,line):
            if reader.records[path]['work']!=work:raise ValueError('Cross-work reading passage: '+work)
            return reading_passage_url(reader,path,line) or reader.records[path].get('source_url',reader.records[path]['url'])+'#L'+str(line)
        evidence.append(step(setup['label'],passage(setup['path'],setup['line']),'Read the selected setup or definition before using the result.'))
        evidence.append(step(claim['title'],passage(claim['statement_path'],claim['statement_line']),'Read the precise statement and its hypotheses.'))
        evidence.append(step('Read its written proof',passage(claim['statement_path'],claim['proof_line']),'Follow the recorded written argument for this statement.'))
    elif config and has_statement_finder(config):
        evidence.append(step('Find a statement and written proof',statement_directory_url(config),'Use the work’s statement directory to locate an argument.'))
    evidence.extend(step(label,url,'Read the correspondence map or formal guide before interpreting formal coverage.')
                    for kind in ('claims','formal_guide','lean_setup') for label,url in selected(kind)[:1])
    if work=='monographs-cos-method':
        evidence.extend([step('Formalization and theorem correspondence',prefix+'b-lean.html','Compare the written results with the finite formal companion and its assumptions.'),
                         step('Computation and reproducibility',prefix+'c-reproduction.html','Inspect the retained commands, replay results, and their tested scope.')])
    if work in getattr(reader,'lean_works',{}):
        from lean_reader import directory
        evidence.append(step('Inspect retained Lean sources',directory(work),'Compare the full types with the written statements and recorded coverage.'))
    elif any(r['kind']=='lean' for r in component['resources']):
        evidence.append(step('Lean sources and setup',overview+'#lean','Consult source availability and the work’s recorded Lean status.'))
    if any(r['kind']=='code' for r in component['resources']):
        evidence.append(step('Code and reproduction files',overview+'#code','Read the input limits, expected results, and reproduction instructions.'))
    evidence.append(step('Evidence and recorded limits',overview+'#evidence','Check the edition and evidence behind the work’s status.'))
    return dict(work=work,url=guide_url(work),title=meta['title'],group=meta['group'],
        summary=intro['contribution'] if intro else assessment.get('reader_summary',meta['summary']),
        question=intro['question'] if intro else None,limits=intro['limits'] if intro else meta['boundary'],
        scope=assessment['scope'],next_step=assessment['next_step'],
        lean=site.status['labels']['lean'][assessment['lean']][0],
        confidence=site.status['labels']['confidence'][assessment['confidence']][0],
        paths=[dict(id='introduction',title='Visual introduction' if has_visual else 'Worked introduction' if has_examples else 'First look',
                    summary='Begin with the visual companion and its explanations.' if has_visual else 'Begin with introductory calculations.' if has_examples else 'Begin with its question, background, and scope.',
                    background=background,steps=first,checkpoint='Explain the question and the model in your own words before continuing.'),
               dict(id='study',title='Full study' if config else 'Read the work',summary='Follow the reading edition and its source material.',
                    background='Keep the work’s definitions and hypotheses with each result.',steps=unique(study),
                    checkpoint='Choose a result or example and record its assumptions, conclusion, and source location.'),
               dict(id='evidence',title='Proof and evidence' if intro or assessment['lean'] in {'contract','partial','inherited'} else 'Evidence and limits',
                    summary='Follow the statements, source records, and recorded coverage.',
                    background='Read the corresponding statement and its assumptions before inspecting an evidence record.',steps=unique(evidence),
                    checkpoint='Distinguish the written claim, what was checked, and what remains open.')])


def render_guide(site,model):
    e=html.escape;page=model['url']
    def link(title,url):return '<a href="'+e(site.rel(url,page),quote=True)+'">'+e(title)+'</a>'
    body='<div class="reading-guide" id="guide-top"><p class="eyebrow">'+e(model['title'])+' · Guided reading</p><h1>Start here</h1>'
    if model['question']:body+='<p class="lede">'+e(model['question'])+'</p>'
    body+='<p>'+e(model['summary'])+'</p><nav class="reading-path-cards" aria-label="Choose a reading path">'
    for i,path in enumerate(model['paths'],1):
        body+='<a class="route" href="#'+path['id']+'"><span class="eyebrow">Path '+str(i).zfill(2)+'</span><h2>'+e(path['title'])+'</h2><p>'+e(path['summary'])+'</p><span>Explore this path →</span></a>'
    body+='</nav><p>These suggested paths use this edition’s available material. '+e(model['limits'])+'</p>'
    for path in model['paths']:
        body+='<section class="reading-guide-path" id="'+path['id']+'" aria-labelledby="'+path['id']+'-title"><h2 id="'+path['id']+'-title">'+e(path['title'])+'</h2><p>'+e(path['background'])+'</p>'
        if path['id']=='evidence':
            body+='<p><strong>Recorded coverage.</strong> '+e(model['scope'])+'</p><p class="status">Lean: '+e(model['lean'])+' · Evidence basis: '+e(model['confidence'])+'</p><p><strong>Remaining work.</strong> '+e(model['next_step'])+'</p>'
        body+='<ol>'
        for step in path['steps']:body+='<li>'+link(step['title'],step['url'])+'<p>'+e(step['description'])+'</p></li>'
        body+='</ol><p class="notice">Checkpoint: '+e(path['checkpoint'])+'</p><p><a href="#guide-top">Choose another path ↑</a></p></section>'
    body+='<nav class="reading-guide-return" aria-label="Work resources">'+link('Work overview','collection/works/'+model['work']+'.html')+link('More reading guides',INDEX)+'</nav></div>'
    site.page(page,model['title']+': Start here',body)
    site.search.append(dict(title=model['title']+' / Start here',group='Collection',kind='Guides',work_ids=[model['work']],url=page,
        text='Guided reading prerequisites '+model['summary']+' '+ ' '.join(p['title'] for p in model['paths'])))


def publish(reader):
    site=reader.site;models=[];rows=[]
    for component in site.registry['components']:
        if component['id'] not in eligible_books():continue
        model=guide_model(reader,component);models.append(model)
        if model['work'] not in CURATED:render_guide(site,model)
        else:
            if not (site.output/model['url']).is_file():raise ValueError('Missing curated reading guide: '+model['work'])
        rows.append(dict(work=model['work'],url=model['url'],paths=list(CURATED.get(model['work'],[p['id'] for p in model['paths']])),
                         targets=[] if model['work'] in CURATED else sorted({s['url'] for p in model['paths'] for s in p['steps']})))
    e=html.escape
    body='<p class="eyebrow">Guided reading</p><h1>Choose a reading path</h1><p>Begin with a visual introduction, study a complete manuscript, or follow its supporting evidence. These '+str(len(models))+' papers and books have both an HTML reading edition and an HTML visual guide.</p><p><a href="index.html">HTML reading library</a> · <a href="../works.html">Browse all works by subject</a></p>'
    body+='<form class="filters" role="search"><label for="work-query">Find a reading guide</label><input id="work-query" data-result-label="guides" type="search" name="q" autocomplete="off"><label for="work-group">Collection</label><select id="work-group"><option value="">All collections</option>'
    body+=''.join('<option value="'+key+'">'+label+'</option>' for key,label in GROUPS.items())+'</select><button type="reset">Clear filters</button></form><p id="work-count" role="status" aria-live="polite">'+str(len(models))+' guides</p><div class="work-list">'
    for model in models:
        searchable=' '.join((model['title'],model['summary'],model['work'],GROUPS[model['group']]))
        body+='<section class="work" data-search="'+e(searchable,quote=True)+'" data-group="'+model['group']+'"><p class="eyebrow">'+GROUPS[model['group']]+'</p><h2>'+e(model['title'])+'</h2><p>'+e(model['summary'])+'</p><a class="button" href="'+e(site.rel(model['url'],INDEX),quote=True)+'">Start here</a></section>'
    site.page(INDEX,'Start here: guided reading',body+'</div>')
    site.search.append(dict(title='Choose a reading path',group='Collection',kind='Guides',work_ids=[m['work'] for m in models],url=INDEX,text='Guided reading visual introduction full study proof evidence '+ ' '.join(m['title'] for m in models)))
    site.write(REPORT,json.dumps(dict(source_revision=site.revision,selection='Complete HTML manuscript and HTML visual guide',guides=rows),ensure_ascii=False)+'\n')
    return rows


def verify(root,documents,pages):
    from pathlib import Path
    from check_reader_site import check_search_targets
    registry=json.loads((Path(__file__).resolve().parents[1]/'manifests/browse-resources.json').read_bytes())
    report=json.loads((root/REPORT).read_bytes())
    rows=report['guides'];expected=[c['id'] for c in registry['components'] if c['id'] in eligible_books()]
    assert report['source_revision']==documents['source_revision']
    assert [r['work'] for r in rows]==expected,'Start here guides must cover every eligible work once'
    for row in rows:
        assert row['url']==guide_url(row['work'])
        assert len(row['paths'])==3 and len(set(row['paths']))==3
        assert set(row['paths'])<=set(pages[row['url']].ids)
        check_search_targets([dict(url=u) for u in row['targets']],pages)
        for target in row['targets']:
            assert posixpath.relpath(target,posixpath.dirname(row['url'])) in pages[row['url']].links
        overview='collection/works/'+row['work']+'.html'
        assert posixpath.relpath(row['url'],posixpath.dirname(overview)) in pages[overview].links
        assert posixpath.relpath(row['url'],posixpath.dirname(INDEX)) in pages[INDEX].links
    return dict(works=len(rows),paths=3*len(rows))
