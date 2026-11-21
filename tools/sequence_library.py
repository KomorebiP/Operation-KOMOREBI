"""Unified formula library and on-demand matching against retained OEIS exports."""
import csv
import hashlib
from html import escape as e
from urllib.parse import quote,urlencode
import io
import json
from pathlib import Path
import shutil
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
from sequence_formula_catalogue import expanded_catalogue, formula_variants, formula_block, REGISTRY_PATH
from sequence_archive import records, plot_section
from sequence_research_tables import cell_coordinates, triangle_section
from sequence_research_notes import entry_details, research_connections
from sequence_generalized import catalogue as generalized_catalogue, build_pages as generalized_pages, sections as generalized_sections


def source_degree(entry,n):
    if entry.get('linear_addition'):return n
    if entry.get('triangle'):
        row,_=cell_coordinates(entry,n);return row*entry['triangle']['degree_multiplier']
    if 'source_shift' in entry:return entry['N']*n+entry['source_shift']
    if entry['kind']=='logarithmic companion':return entry['N']*(n+1)-1
    if entry['kind'].startswith('Appell '):return n
    return entry['N']*n+(entry.get('j',0) if entry['kind']=='classical multisection' else 0)


CALCULATOR_PARAMETERS={
    'sparse':('p','q','r','u','v'),
    'padovan':('h',),
    'fourblock':('a',),
    'jet':('d','lambda','c'),
    'hankel':('d','c'),
    'beta_moments':('L','a','b'),
    'beta_hankel':('L','a','b'),
    'meixner':('s','twox'),
    'central_binomial':('r',),
}
CALCULATOR_BOUNDS={'sparse':96,'padovan':96,'fourblock':32,'jet':80,'hankel':12,'beta_moments':96,'beta_hankel':17,'meixner':96,'central_binomial':160}


def calculator_link(entry,path='sequence-library.html'):
    """Canonical exact calculator handoff from a source record.

    Parameters are recorded by the exact generator, not parsed from a title.
    Links contain no stored coefficients and leave the original record intact.
    """
    spec=entry.get('calculator')
    if not spec:return None
    mode=spec['mode']
    if mode not in CALCULATOR_PARAMETERS:raise ValueError('Unrecognized exact calculation mode')
    keys=CALCULATOR_PARAMETERS[mode]
    if set(spec)!={'mode',*keys}:raise ValueError('Incomplete exact calculator parameters: '+entry['id'])
    index=entry['offset']
    count=min(12,len(entry['terms']),CALCULATOR_BOUNDS[mode]-index+1)
    if count<1:raise ValueError('Exact calculator cannot represent the source index')
    values={'q':'id:'+entry['id'],'cf-version':'1','cf-mode':mode,'cf-start':str(index),'cf-count':str(count)}
    for key in keys:values['cf-'+key]=str(spec[key])
    return path+'?'+urlencode(values)+'#closed-calculator-panel'


def library_entries(atlas):
    groups=[('atlas',atlas,'sequences/'),('recovered',records(atlas),'sequence-archive/'),('formulas',expanded_catalogue(),'sequence-families/')]
    entries=[]
    for collection,values,prefix in groups:
        for original in values:
            entry=dict(original,collection=collection,url=prefix+original['id']+'.html')
            entry.setdefault('source','https://komorebip.github.io/Operation-KOMOREBI/'+entry['url']+'#definition')
            entry.setdefault('index_symbol','n');entry.setdefault('classification','family' if collection=='formulas' else 'reference')
            if entry['id']=='KOM084':entry['tags']=[*entry['tags'],'triangle']
            entry['formulas']=formula_variants(entry)
            if entry.get('calculator'):entry['calculator_url']=calculator_link(entry)
            entries.append(entry)
    return entries


def exact_record_receipt(entry):
    """Digest the indexed integer data, never the rounded plot coordinates."""
    payload=[entry['id'],entry['collection'],entry['offset'],
             entry.get('index_symbol','n'),entry['terms'],
             entry.get('source_degrees')]
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()


def verified_oeis_coverage(entries,snapshot):
    """Resolve compared IDs only after binding their terms and reference hashes.

    An absent receipt means pending, even when another record in the same
    collection has been compared. Empty hit lists are completed finite scans.
    """
    covered=set(snapshot['matches'])
    if covered!=set(snapshot['total_matches']):
        raise ValueError('OEIS comparison record sets differ')
    ids={entry['id'] for entry in entries}
    if len(ids)!=len(entries) or not covered<=ids:
        raise ValueError('OEIS comparison references missing or duplicate local records')
    compared=[entry for entry in entries if entry['id'] in covered]
    signature=hashlib.sha256(json.dumps(
        [(entry['id'],entry['terms']) for entry in compared],
        separators=(',',':')).encode()).hexdigest()
    if signature!=snapshot['catalogue_terms_sha256']:
        raise ValueError('Regenerate the full-library OEIS comparison after term changes')
    files={item['file']:item for item in snapshot['snapshot']['files']}
    for name,key in [('stripped.gz','stripped_sha256'),('names.gz','names_sha256')]:
        if name not in files or files[name]['sha256']!=snapshot[key]:
            raise ValueError('OEIS comparison reference hash differs: '+name)
    return covered


def oeis_prefix_note(entry,minimum=8):
    """Explain zero-heavy initial matches without changing comparison scope."""
    prefix=entry['terms'][:minimum]
    if not entry.get('matches') or len(prefix)<minimum:
        return ''
    zeros=prefix.count('0')
    if zeros==minimum:
        beginning=f'The first {minimum} compared terms are zero. A shared initial zero block can account for these finite hits. '
    elif zeros==minimum-1:
        beginning=f'The first {minimum} compared terms contain one nonzero value and a long block of zeros. A shared starting pattern can account for these finite hits. '
    else:
        return ''
    return beginning+'Agreement need not extend to later nonzero terms. Check the reported match lengths.'


def oeis_comparison_summary(entry):
    """Short status for the closed-form index, consistent with record pages."""
    if entry.get('oeis_checked') is not True:
        return 'Not yet compared'
    hits=entry.get('matches',[])
    if not hits:
        return 'No eight-term hit in the snapshot'
    total=entry['match_count']
    longest=max(hit['matched_terms'] for hit in hits)
    return f'{total:,} finite '+('hit' if total==1 else 'hits')+f' · longest {longest} terms'


def matches_block(entry):
    if entry.get('oeis_checked') is not True:
        stated=('<p>The source identifies <a href="https://oeis.org/'+e(entry['oeis'])+'">'+e(entry['oeis'])+'</a>. '
                'That identification has not been checked against the retained OEIS snapshot.</p>') if entry.get('source_claimed_oeis') and entry.get('oeis') else ''
        return ('<section id="oeis-matches"><h2>OEIS comparisons</h2>'+stated+
                '<p>OEIS comparison pending: this record has not been checked '
                'against the retained snapshot.</p></section>')
    hits=entry.get('matches',[]);total=entry.get('match_count',len(hits))
    quality='<p>'+e(entry['oeis_prefix_note'])+'</p>' if entry.get('oeis_prefix_note') else ''
    return '<section id="oeis-matches"><h2>OEIS comparisons</h2><p>The comparison uses stored terms beginning at local index '+str(entry['offset'])+'. Positions in the bulk export start at zero and do not represent OEIS mathematical offsets. A finite match does not prove that two infinite sequences are identical.</p>'+quality+(
        '<ol>'+''.join('<li><a href="https://oeis.org/'+x['id']+'">'+x['id']+'</a> — '+e(x['name'])+'<br>'+str(x['matched_terms'])+' matching terms · OEIS excerpt position '+str(x['position'])+'</li>' for x in hits[:8])+'</ol><p>Showing '+str(min(8,len(hits)))+' of '+str(total)+' recorded matches. Up to 50 ranked matches are retained in the entry JSON.</p>' if hits else '<p>No contiguous match of eight terms was found in the recorded export. This does not establish novelty.</p>')+'<p>Reference names and terms: <a href="https://oeis.org/">The Online Encyclopedia of Integer Sequences</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Matching and presentation are adaptations.</p></section>'


def build(site,atlas):
    entries=library_entries(atlas)
    snapshot=json.loads((site.root/'manifests/sequence-library-oeis.json').read_text(encoding='utf-8'))
    checked_ids=verified_oeis_coverage(entries,snapshot)
    # Use the same audited index map as each record's exact data table.
    # These are source degrees, not inferred from the flattened display index.
    for entry in entries:
        if entry['collection']=='formulas':
            entry['source_degrees']=[source_degree(entry,entry['offset']+i) for i in range(len(entry['terms']))]
    for entry in entries:
        entry['oeis_checked']=entry['id'] in checked_ids
        entry['record_sha256']=exact_record_receipt(entry)
        entry['matches']=snapshot['matches'].get(entry['id'],[]);entry['match_count']=snapshot['total_matches'].get(entry['id'],0)
        entry['oeis_prefix_note']=oeis_prefix_note(entry,snapshot['minimum_terms'])
        entry['oeis_snapshot']=dict(attribution=snapshot['attribution'],license=snapshot['license'],source_urls=snapshot['source_urls'],downloaded_at=snapshot['snapshot']['downloaded_at'],stripped_sha256=snapshot['stripped_sha256'],names_sha256=snapshot['names_sha256'],scope='Finite contiguous comparisons; export positions are not mathematical offsets and matches do not prove infinite identity.')
    source=site.root/'research/oeis-snapshot'
    target=site.output/'assets/oeis';target.mkdir(parents=True,exist_ok=True)
    for file in snapshot['snapshot']['files']:
        raw=(source/file['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=file['sha256']:raise ValueError('OEIS snapshot hash differs: '+file['file'])
        shutil.copyfile(source/file['file'],target/file['file'])
    site.write('assets/oeis/snapshot.json',json.dumps(snapshot['snapshot'],indent=2)+'\n')
    data=dict(schema=1,entries=entries,snapshot={key:value for key,value in snapshot.items() if key not in ('matches','total_matches')})
    site.write('assets/sequence-library-data.json',json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    site.write('assets/sequence-oeis-meta.json',json.dumps({'stripped_sha256':snapshot['stripped_sha256']},separators=(',',':'))+'\n')
    site.write('assets/sequence-formulas.json',json.dumps({x['id']:x['formulas'] for x in entries},ensure_ascii=False,separators=(',',':'))+'\n')
    out=io.StringIO(newline='');writer=csv.writer(out);writer.writerow(['id','title','collection','family','offset','stored_terms','representations','entry_url'])
    for x in entries:writer.writerow([x['id'],x['title'],x['collection'],x['kind'],x['offset'],len(x['terms']),len(x['formulas']),x['url']])
    site.write('assets/sequence-library-index.csv',out.getvalue())
    source_files=['tools/'+name+'.py' for name in ['sequence_formula_catalogue','sequence_library','sequence_archive','sequence_closed_forms','sequence_closed_forms_extended','sequence_polynomial_hankel','sequence_differential_hankel','sequence_math_reading','sequence_research_tables','sequence_linear_research','sequence_research_notes','sequence_generalized','sequence_archive_families','sequence_atlas','sequence_atlas_reference','sequence_atlas_reading','sequence_atlas_study','sequence_atlas_index']]+[REGISTRY_PATH,'manifests/sequence-generalized-sources.json','research/sequence-connections/IDENTITIES.md','research/sequence-connections/sources/komorebi-math-families.py','research/sequence-closed-forms/IDENTITIES.md','research/sequence-closed-forms/COLLECTION_II_ADDITIONS.md','research/sequence-closed-forms/POLYNOMIAL_HANKEL_STRUCTURE.md','research/sequence-closed-forms/FINITE_DIFFERENTIAL_HANKEL.md','tools/test_sequence_closed_forms.py','tools/test_sequence_closed_forms_extended.py','tools/test_sequence_polynomial_hankel.py','tools/test_sequence_differential_hankel.py','tools/test_sequence_differential_hankel_bridge.py','tools/test_sequence_differential_hankel_bridge.mjs','tools/test_sequence_math_reading.py','tools/test_sequence_closed_forms_core.mjs','website/assets/sequence-closed-forms-core.mjs','website/assets/sequence-differential-hankel.mjs','website/assets/sequence-closed-forms-worker.mjs']
    source_files+=['tools/update_sequence_library_oeis.py','manifests/sequence-library-oeis.json','research/oeis-snapshot/snapshot.json','research/sequence-archive/candidate_registry.json']
    source_files+=['tools/sequence_central_binomial.py','tools/test_sequence_closed_forms_central.py','research/sequence-closed-forms/CENTRAL_BINOMIAL_RECURRENCE.md','tools/test_sequence_closed_form_handoffs.py','tools/test_sequence_closed_form_handoffs.mjs']
    source_files+=['research/sequence-closed-forms/ALGEBRAIC_KERNEL_EXAMPLES.md',
                   'tools/sequence_algebraic_kernel_examples.py',
                   'tools/test_sequence_algebraic_kernel_examples.py',
                   'website/assets/sequence-binomial-reading.mjs']
    source_files+=['tools/sequence_rational_hankel.py',
                   'tools/verify_sequence_rational_hankel.py',
                   'tools/verify_sequence_linear_hankel.py',
                   'tools/test_sequence_linear_hankel_bridge.py',
                   'tools/test_sequence_linear_hankel_bridge.mjs',
                   'website/assets/sequence-linear-hankel.mjs',
                   'research/sequence-closed-forms/RATIONAL_HANKEL_TAILS.md',
                   'research/sequence-closed-forms/LINEAR_WEIGHT_RECURRENCE.md',
                   'research/sequence-closed-forms/RATIONAL_HANKEL_REVIEW.md',
                   'research/sequence-closed-forms/RATIONAL_HANKEL_LITERATURE.md']
    source_files+=['research/sequence-closed-forms/RATIONAL_HANKEL_REPRODUCE.md']
    source_files+=['tools/sequence_parity_hankel.py',
                   'tools/verify_sequence_parity_structure.py',
                   'tools/verify_sequence_quadratic_hankel.py',
                   'tools/verify_sequence_hankel_symbol.py',
                   'tools/verify_sequence_quadratic_certificate.py',
                   'tools/verify_sequence_mixed_hankel.py',
                   'research/sequence-closed-forms/PARITY_HANKEL_RECURRENCES.md',
                   'research/sequence-closed-forms/MIXED_HANKEL_RECURRENCE.md',
                   'research/sequence-closed-forms/HANKEL_COMPRESSION_REVIEW.md',
                   'research/sequence-closed-forms/HANKEL_COMPRESSION_REPRODUCE.md',
                   'verification/sequence-library/hankel-compression/quadratic-certificate.json',
                   'verification/sequence-library/hankel-compression/mixed-certificate.json']
    with ZipFile(site.output/'assets/sequence-formula-source.zip','w',ZIP_DEFLATED) as bundle:
        for name in source_files:
            info=ZipInfo(name,date_time=(2026,11,15,0,0,0));info.create_system=3;info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16;bundle.writestr(info,(site.root/name).read_text(encoding='utf-8').encode('utf-8'))
        info=ZipInfo('README.txt',date_time=(2026,11,15,0,0,0));info.create_system=3;info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
        bundle.writestr(info,'Exact formula catalogue. Python 3.10+ standard library. The browser arithmetic and cross-language checks also require Node.js 24. Text sources use UTF-8/LF for portable reproduction.\nRun: python tools/sequence_formula_catalogue.py --id KFOR-S-catalan-03-01\nExport all records: python tools/sequence_formula_catalogue.py --output records.json\nCheck closed-form formulas: python -B -m unittest discover -s tools -p \"test_sequence_closed_forms*.py\" -v\nCheck weighted binomial recurrence: python -B -m unittest discover -s tools -p test_sequence_closed_forms_central.py -v\nCheck algebraic-kernel examples: python -B -m unittest discover -s tools -p test_sequence_algebraic_kernel_examples.py -v\nPrint worked example terms: python tools/sequence_algebraic_kernel_examples.py\nCheck browser arithmetic: node --test tools/test_sequence_closed_forms_core.mjs\nCheck indexed calculator presets: python -B -m unittest discover -s tools -p test_sequence_closed_form_handoffs.py -v\nCompare Python and JavaScript: python -B -m unittest discover -s tools -p test_sequence_differential_hankel_bridge.py -v\nRational Hankel proofs and reproduction: research/sequence-closed-forms/RATIONAL_HANKEL_REPRODUCE.md\nVerify rational Hankel certificates: python -B tools/verify_sequence_rational_hankel.py --output rational-hankel-checks.json\nVerify the uniform linear-weight identity: python -B tools/verify_sequence_linear_hankel.py --output linear-hankel-certificate.json\nCompare linear-weight Python and BigInt values: python -B -m unittest discover -s tools -p test_sequence_linear_hankel_bridge.py -v\nParity, quadratic, and mixed certificates: follow the five standard-library commands in research/sequence-closed-forms/HANKEL_COMPRESSION_REPRODUCE.md\nScalar records store 24 terms beginning at their explicit offsets, except standard k-bonacci records, which store 48. Coefficient triangles store complete rows n=0..12, including zeros. Triangle j is a flat cell index. Its row and column are n and k. Parameter records are not claims of novelty or pairwise distinctness.\n\nReproduce finite OEIS comparisons using the retained snapshot:\nThe comparison receipt and updater are included. The two bulk gzip files are separate downloads, not duplicated in this source ZIP. Download https://komorebip.github.io/Operation-KOMOREBI/assets/oeis/stripped.gz and https://komorebip.github.io/Operation-KOMOREBI/assets/oeis/names.gz. Place both files in research/oeis-snapshot/ beside the included snapshot.json. That file records the required byte counts and SHA-256 hashes; the updater rejects different bytes before scanning.\nRun: python tools/update_sequence_library_oeis.py --source research/oeis-snapshot --output reproduced-oeis-comparison.json\nThe reproduction timestamp changes. Compare the snapshot hashes, catalogue_terms_sha256, matches and total_matches with manifests/sequence-library-oeis.json. Comparisons use the first eight stored terms at every exported position and extend each hit. Export positions are not mathematical offsets; finite hits are not proofs of infinite identity or novelty.\n')
    generalized=generalized_catalogue(entries)
    site.write('assets/sequence-generalized-data.json',json.dumps(generalized,ensure_ascii=False,separators=(',',':'))+'\n')
    scripts=['math-display.mjs','sequence-research-ui.mjs','sequence-reading-theme.mjs','sequence-oeis-core.mjs','sequence-family-core.mjs','sequence-transfer-core.mjs','sequence-math.mjs','sequence-graph-core.mjs','sequence-modular-core.mjs','sequence-discovery-core.mjs','sequence-notebook-core.mjs','sequence-research-worker.mjs','sequence-research-common.mjs','sequence-oeis-worker.mjs','sequence-oeis-client.mjs','sequence-comparison-chart.mjs','sequence-chart-labels.mjs','sequence-workbench-core.mjs','sequence-comparison-certificate.mjs','sequence-certificate-inspection.mjs','sequence-workbench.mjs','sequence-triangle-core.mjs','sequence-triangle.mjs','sequence-transfers.mjs','sequence-families-ui.mjs','sequence-connections-ui.mjs','sequence-identification-ui.mjs','sequence-modular-ui.mjs','sequence-notebooks-ui.mjs','sequence-library-membership.mjs','sequence-research-studio.mjs','sequence-library-search.mjs','sequence-inspection-links.mjs','sequence-differential-hankel.mjs','sequence-closed-forms-core.mjs','sequence-closed-forms-worker.mjs','sequence-closed-forms-ui.mjs','sequence-library.js']
    scripts.append('sequence-linear-hankel.mjs')
    for name in scripts:
        content=(site.root/'website/assets'/name).read_text(encoding='utf-8')
        content=content.replace('__OEIS_TERMS_SHA256__',snapshot['stripped_sha256']).replace('__OEIS_NAMES_SHA256__',snapshot['names_sha256'])
        for dep in scripts+['sequence-atlas-search.mjs','sequence-archive-core.mjs','sequence-archive-plot.mjs','sequence-atlas-core.mjs','sequence-atlas-saved.mjs','sequence-plot-options.mjs','sequence-library-data.json','sequence-generalized-data.json','sequence-oeis-meta.json']:
            path=site.output/'assets'/dep
            if path.exists():content=content.replace("'./"+dep+"'","'./"+dep+'?v='+hashlib.sha256(path.read_bytes()).hexdigest()[:12]+"'")
        site.write('assets/'+name,content)
    site.write('assets/sequence-library.css',(site.root/'website/assets/sequence-library.css').read_text(encoding='utf-8'))
    site.write('assets/sequence-research.css',(site.root/'website/assets/sequence-research.css').read_text(encoding='utf-8'))
    site.write('assets/sequence-closed-forms.css',(site.root/'website/assets/sequence-closed-forms.css').read_text(encoding='utf-8'))
    def wrap(body,prefix='',entry=None,family=None,page_kind=None):
        attrs=' data-entry="'+e(entry['id'])+'.json"' if entry else (' data-family="'+e(family)+'"' if family else '')
        if page_kind:attrs+=' data-page="'+e(page_kind,quote=True)+'"'
        return ''.join('<link rel="stylesheet" href="'+prefix+'assets/'+name+'?v='+hashlib.sha256((site.output/'assets'/name).read_bytes()).hexdigest()[:12]+'">' for name in ['sequence-archive.css','sequence-plot-options.css','sequence-library.css','sequence-reading.css','sequence-research.css'])+'<div class="sar sl-library" data-library'+attrs+'>'+body+'</div><script type="module" src="'+prefix+'assets/sequence-library.js?v='+hashlib.sha256((site.output/'assets/sequence-library.js').read_bytes()).hexdigest()[:12]+'"></script>'
    site.write('assets/sequence-research-connections.json',json.dumps(research_connections(),ensure_ascii=False,separators=(',',':'))+'\n')
    generalized_pages(site,generalized,wrap)
    total=len(entries);representations=sum(len(x['formulas']) for x in entries)
    kinds=sorted({x['kind'] for x in entries});types=sorted({f['kind'] for x in entries for f in x['formulas']});statuses=sorted({x['status'] for x in entries})
    collections=[('', 'All records',total)]+[(key,label,sum(x['collection']==key for x in entries)) for key,label in [('formulas','Formula families'),('atlas','Curated sequences'),('recovered','Research archive')]]
    collection_buttons='<div class="sl-collections" role="group" aria-label="Search collections">'+''.join('<button type="button" data-collection="'+key+'" aria-pressed="'+('true' if not key else 'false')+'">'+label+' <span>'+f'{count:,}'+'</span></button>' for key,label,count in collections)+'</div>'
    def page_nav(active):
        pages=[('Search','sequence-library.html','search'),('Transfer','sequence-transfers.html#transfers','transfer'),('Compare','sequence-compare.html#comparison','compare'),('Research','sequence-research.html#research-families','research'),('OEIS','sequence-oeis.html#oeis','oeis')]
        return '<nav class="sl-page-tabs" aria-label="Sequence Library pages">'+''.join('<a href="'+url+'"'+(' aria-current="page"' if active==key else '')+'>'+label+'</a>' for label,url,key in pages)+'</nav>'
    def page_heading(title,description,active,anchor):
        return ('<a class="sl-skip" href="#'+anchor+'">Skip to '+e(title)+'</a>'
                '<header class="sl-section-head"><p class="sar-kicker">Komorebi / Sequence Library</p>'
                '<h1>'+e(title)+'</h1><p class="sl-section-lede">'+e(description)+'</p>'
                +page_nav(active)+'</header>')
    header=('<a class="sl-skip" href="#library-search">Skip to sequence search</a>'
            '<header class="sl-hero"><p class="sar-kicker">Komorebi / Sequence Library</p>'
            '<h1>Sequence Library</h1>'
            '<p class="sar-lede">Search exact sequences, calculate coefficients, and read their definitions and derivations.</p>'
            '<p class="sl-figures"><strong>'+f'{total:,}'+'</strong> records · <strong>'+f'{representations:,}'+'</strong> representations · <strong>'+f'{snapshot["sequence_count"]:,}'+'</strong> OEIS references</p>'
            +page_nav('search')+'</header>')
    research_entries=[item for item in entries if 'research-derived' in item['tags']]
    research_count=len(research_entries)
    triangle_count=sum('triangle' in item['tags'] for item in entries)
    research_groups=[
        ('Secancy parameter polynomials',
         'Polynomial coefficients and their complete triangular tables.',
         [('Coefficient columns','secancy parameter column'),
          ('Complete coefficient triangles','secancy coefficient triangle')],
         ('Read an N=3 triangle','sequence-families/KFOR-TRI-P-03.html#triangle')),
        ('Euler-transfer theta',
         'Integer evaluations, polynomial columns and the complete theta triangle.',
         [('Integer specializations','Euler-transfer theta'),
          ('Polynomial coefficient columns','theta polynomial column'),
          ('Theta coefficient triangle','theta coefficient triangle')],
         ('Read the x=2 specialization','sequence-families/KFOR-H-02.html')),
        ('Block-Appell polynomials',
         'Complete polynomial tables and nonzero supported columns.',
         [('Coefficient triangles','block-Appell coefficient triangle'),
          ('Supported coefficient columns','block-Appell coefficient column')],
         ('Read an N=3 Appell triangle','sequence-families/KFOR-TRI-A-03-01.html#triangle')),
        ('Linear recurrences',
         'Weighted k-step coefficients and standard zero-seeded k-bonacci sequences.',
         [('Weighted k-step families','k-step reciprocal power'),
          ('Standard k-bonacci sequences','k-bonacci')],
         ('Read a weighted recurrence','sequence-families/KFOR-LR-03-02-01.html'))
    ]
    named_kinds={kind for _,_,kinds,_ in research_groups for _,kind in kinds}
    remaining_kinds=sorted({item['kind'] for item in research_entries if item['kind'] not in named_kinds})
    if remaining_kinds:
        research_groups.append(('Additional indexed families',
                                'Other research records retained in this library.',
                                [(kind,kind) for kind in remaining_kinds],None))
    def research_link(query,label):
        href='sequence-library.html?q='+quote(query,safe='')+'#library-search'
        return '<a href="'+e(href,quote=True)+'">'+e(label)+'</a>'
    family_cards=[]
    for title,description,category_pairs,example in research_groups:
        counts=[(label,kind,sum(item['kind']==kind for item in research_entries)) for label,kind in category_pairs]
        total_group=sum(count for _,_,count in counts)
        if not total_group:continue
        links=''.join('<li>'+research_link('kind:"'+kind+'"',label+' ('+str(count)+')')+'</li>' for label,kind,count in counts if count)
        example_link=('<p class="sl-research-example">Example: <a href="'+e(example[1],quote=True)+'">'+e(example[0])+'</a></p>') if example else ''
        family_cards.append('<article class="sl-research-group"><h3>'+e(title)+' <span>'+str(total_group)+' records</span></h3><p>'+e(description)+'</p><ul>'+links+'</ul>'+example_link+'</article>')
    research=('<section id="research-families" class="sl-optional-section"><h2>Research families</h2>'
              '<p class="sl-research-intro">'+str(research_count)+' indexed research records. '
              'Explore each family below or '+research_link('tag:research-derived','browse all research records')+'. '
              'Records retain their definitions, exact coefficients, source links and review status. '
              'An indexed family is not a claim of historical novelty.</p>'
              '<details class="sl-topic-disclosure"><summary>Explore research families by type</summary>'
              '<div class="sl-research-index">'+''.join(family_cards)+'</div>'
              '<p class="sl-research-scope">Some parameter choices produce the same integer sequence. '
              'The links search all matching records, not just the examples. '
              'Filtered search requires JavaScript. Without it, open the '
              '<a href="sequence-library/index.html">complete static sequence index</a>.</p>'
              '</details></section>')
    controls='''<section id="library-search"><h2>Find a sequence or formula</h2><p><a href="generalized-families/index.html">Generalized family definitions and source papers</a></p><form id="sl-search" role="search" hidden><div class="sl-scope-buttons sp-actions" role="group" aria-label="Search scope"><button type="button" data-scope="records" aria-pressed="true">Integer records</button><button type="button" data-scope="families" aria-pressed="false">Generalized families</button></div>'''+collection_buttons+'''<label id="sl-query-label" for="sl-query">Name, formula, identifier, or exact terms</label><div class="sl-query"><input id="sl-query" type="search" maxlength="20000" placeholder="Try hypergeometric, j:1 r:2, or 1, 1, 69" aria-describedby="sl-help sl-error"><button type="submit">Search</button><button id="sl-clear" type="button">Clear</button></div><details><summary>Filters and search options</summary><div class="sar-controls"><label for="sl-scope">Search scope<select id="sl-scope"><option value="records">Integer records</option><option value="families">Generalized families</option></select></label><label for="sl-collection">Collection<select id="sl-collection"><option value="">All collections</option><option value="formulas">Formula families</option><option value="atlas">Curated sequences</option><option value="recovered">Research archive</option></select></label><label for="sl-kind">Family<select id="sl-kind"><option value="">All families</option>'''+''.join('<option>'+e(k)+'</option>' for k in kinds)+'''</select></label><label for="sl-representation">Formula type<select id="sl-representation"><option value="">All representations</option>'''+''.join('<option>'+e(k)+'</option>' for k in types)+'''</select></label><label for="sl-status">Review status<select id="sl-status"><option value="">All review statuses</option>'''+''.join('<option>'+e(status)+'</option>' for status in statuses)+'''</select></label><label for="sl-match">Term matching<select id="sl-match"><option value="any">Anywhere in stored terms</option><option value="start">At the first stored index</option></select></label><label for="sl-sort">Order<select id="sl-sort"><option value="relevance">Best match</option><option value="name">Name</option><option value="id">Identifier</option></select></label><label for="sl-hits">OEIS comparisons<select id="sl-hits"><option value="">All records</option><option value="matched">Has an eight-term reference match</option><option value="unmatched">No recorded eight-term match</option></select></label></div></details><div class="sp-actions"><button id="sl-generalized" type="button">Browse generalized families</button><button id="sl-research" type="button" hidden>Browse research families</button><button id="sl-triangles" type="button" hidden>Browse coefficient triangles ('''+str(triangle_count)+''')</button><button id="sl-share" type="button">Copy search link</button><button id="sl-export" type="button">Export results CSV</button></div><label id="sl-link-wrap" hidden for="sl-link">Copy this search link<input id="sl-link" readonly></label><p id="sl-error" role="alert" hidden></p><p id="sl-action-status" role="status" aria-live="polite"></p><div id="sl-active-filters" class="sl-active-filters" aria-label="Active search filters"></div></form><p id="sl-family-summary" class="sl-family-summary" hidden></p><p id="sl-family-help" hidden>Search family names, formulas, IDs, or source papers. Try <code>Hankel</code>, <code>id:GF-SMITH-POLYNOMIALS</code>, or <code>paper:SF-VI</code>. Use the Construction type and Source filters to narrow the list. Open a member record to see exact terms and their stored indices.</p><p id="sl-help">Search by name, identifier, formula, or exact terms. Open Search tips and field reference for examples and advanced search.</p><details class="sl-search-guide"><summary>Search tips and field reference</summary>
<p>Search a name, record ID, formula, or comma-separated integer terms. Matches are labelled with their original stored indices.</p>
<div class="sl-search-examples" aria-label="Search examples">
<div><strong>By name</strong><a href="sequence-library.html?q=theta#library-search"><code>theta</code></a></div>
<div><strong>By record ID</strong><a href="sequence-library.html?q=id%3AKFOR-P-03-02#library-search"><code>id:KFOR-P-03-02</code></a></div>
<div><strong>By exact terms</strong><a href="sequence-library.html?q=1%2C1%2C2%2C5%2C14#library-search"><code>1,1,2,5,14</code></a></div>
</div>
<h3>Combine search terms</h3>
<dl class="sl-search-rules">
<div><dt>Both (AND)</dt><dd><code>theta x:2</code></dd></div>
<div><dt>Either (OR)</dt><dd><code>theta | secancy</code></dd></div>
<div><dt>Exclude</dt><dd><code>theta -triangle</code></dd></div>
<div><dt>Exact phrase</dt><dd><code>name:"Euler-transfer theta"</code></dd></div>
<div><dt>Unknown integer</dt><dd><code>terms:1,?,2,3</code></dd></div>
</dl>
<h3>Search fields</h3>
<p><strong>Record details:</strong> <code>id:</code>, <code>name:</code>, <code>kind:</code>, <code>tag:</code>, <code>formula:</code>, <code>representation:</code>, <code>collection:</code> and <code>oeis:</code>.</p>
<p><strong>Parameters:</strong> <code>n:</code> (spacing N), <code>j:</code> (residue), <code>r:</code> (power), <code>x:</code> (specialization), <code>k:</code> (polynomial column), <code>order:</code> (recurrence order) and <code>weight:</code>.</p>
<p><strong>Relationships and sources:</strong> <code>parent:</code>, <code>family:</code> and <code>paper:</code> (for example <code>paper:SF-VI</code>). Use <code>terms:</code> for exact integer patterns.</p>
<p>Words separated by spaces must all match unless joined with <code>|</code>. Quoted phrases stay together. A question mark represents one unknown integer in a term pattern. All stored formula variants are searchable.</p>
</details><p id="sl-count" role="status" aria-live="polite">Browse the <a href="sequence-library/index.html">complete static index</a> without JavaScript.</p><div id="sl-result-layout" class="sl-layout-controls" role="group" aria-label="Sequence result layout" hidden><span>Results view</span><button type="button" data-layout="compact" aria-pressed="true">Compact rows</button><button type="button" data-layout="cards" aria-pressed="false">Cards</button></div><div id="sl-empty" class="sl-empty" hidden><h3>No matches in this view</h3><p>Try a shorter query or remove a filter. Clear removes the query and filters while keeping your selected search scope.</p><button id="sl-reset" type="button">Clear search and filters</button></div><ol id="sl-results" class="sl-results" tabindex="-1" aria-label="Sequence search results"></ol><div id="sl-pages" class="sp-actions" hidden><button id="sl-previous" type="button">Previous results</button><span id="sl-page"></span><button id="sl-next" type="button">Next results</button></div></section>'''
    mb=sum(x['bytes'] for x in snapshot['snapshot']['files'])/1048576
    reference='''<section id="oeis" class="sl-reference sl-optional-section"><h2>Compare with OEIS</h2><details class="sl-topic-disclosure"><summary>Open OEIS lookup and reference downloads</summary><p class="sar-kicker">Reference matching</p><p>Search an OEIS A-number, a name or at least three exact integer terms. Use ? for one unknown integer. This local snapshot uses the official names and terms exports from '''+e(snapshot['snapshot']['downloaded_at'][:10])+'''. Export positions are not mathematical offsets.</p><form id="sl-oeis-form" hidden><label for="sl-oeis-query">OEIS ID, name, or integer pattern</label><div class="sl-query"><input id="sl-oeis-query" maxlength="20000" placeholder="A000108 or 1,1,2,5,14,42,132,429"><button id="sl-oeis-search" type="submit">Search OEIS data</button><button id="sl-oeis-cancel" type="button" disabled>Cancel</button></div></form><details class="sl-oeis-info"><summary>Reference size and search limits</summary><p>The first search downloads about '''+f'{mb:.1f}'+''' MiB of reference data. Searches run in your browser, and queries are not sent to OEIS. Up to 50 results are displayed, with the total reported. The bulk files contain terms and names. Open an OEIS entry for its full formulas, comments and index offset.</p></details><p id="sl-oeis-status" role="status" aria-live="polite">Ready to search OEIS reference data.</p><ol id="sl-oeis-results"></ol><details class="sl-oeis-info"><summary>Source files and attribution</summary><p>Downloads: <a download href="assets/oeis/stripped.gz">OEIS terms</a> · <a download href="assets/oeis/names.gz">OEIS names</a> · <a href="assets/oeis/snapshot.json">Dates, sizes, and SHA-256 hashes</a></p><p>OEIS data © The OEIS Foundation Inc., <a href="https://oeis.org/">The Online Encyclopedia of Integer Sequences</a>, available under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Reference matching and presentation are adaptations. <a href="https://oeis.org/wiki/Download">Official download guidance</a>.</p></details></details></section>'''
    transfers=r'''<section id="transfers" class="sr-transfer-reading">
 <p class="sar-kicker">Exact coefficient transport</p>
 <h2>Transfer between sequences</h2>
 <p>Compare two stored scalar sequences through an exact forward and inverse convolution. Every coefficient is checked over the selected finite window. The calculation does not imply that the sequences share a recurrence.</p>
 <div id="sr-transfer-tool"></div>
 <p class="sr-transfer-static">Enable JavaScript to calculate and export other transfers. The worked example and sources remain available without it.</p>
 <details class="sr-transfer-method"><summary>How the transfer is calculated</summary>
 <div class="sr-transfer-overview">
 <div><h3>How to use this workbench</h3>
 <ol><li>Choose a source sequence and a target by name or record ID.</li><li>Select the number of coefficients, beginning at each sequence's first stored nonzero value.</li><li>Inspect the transfer kernel, inverse, coefficient residuals, and index shifts. Export the exact certificate to reproduce the comparison.</li></ol>
 <p>Only scalar records are eligible. For a coefficient triangle, first choose a scalar column or specialization.</p></div>
 <div class="sr-transfer-algebra"><h3>What is being calculated?</h3>
 <p>Remove each stored leading-zero prefix, retaining its original index separately. Write the resulting ordinary generating polynomials as</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="A(z)=\sum_{j=0}^{L-1}a_j z^j,\qquad B(z)=\sum_{j=0}^{L-1}b_j z^j">A(z) = sum_(j=0)^(L-1) a_j z^j; B(z) = sum_(j=0)^(L-1) b_j z^j</p>
 <p>Since <code>a_0</code> and <code>b_0</code> are nonzero, both series are invertible in the truncated rational power-series ring, and formal division over the rationals defines</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}H(z)&amp;\equiv B(z)A(z)^{-1}\pmod{z^L}\\K(z)&amp;\equiv A(z)B(z)^{-1}\pmod{z^L}\end{aligned}">H(z) = B(z)/A(z) (mod z^L); K(z) = A(z)/B(z) (mod z^L)</p>
 <p>Equivalently, the coefficient transport and its inverse are</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}b_j&amp;=\sum_{i=0}^{j}h_i a_{j-i}\\a_j&amp;=\sum_{i=0}^{j}k_i b_{j-i}\end{aligned}">b_j = sum_(i=0)^j h_i*a_(j-i); a_j = sum_(i=0)^j k_i*b_(j-i)</p>
 <p>The certificate verifies all three identities, modulo <code>z^L</code>:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="H(z)A(z)\equiv B(z),\quad K(z)B(z)\equiv A(z),\quad H(z)K(z)\equiv1\pmod{z^L}">H*A = B; K*B = A; H*K = 1 (mod z^L)</p>
 <p>Original sequence indices, leading-zero prefixes, and shifts are reported separately. The map acts on anchored tails, not on the original index domains without accounting for those shifts.</p></div>
 </div>
 </details>
 <details class="sr-transfer-example"><summary>Worked example: Euler values to shifted Fibonacci values</summary>
 <p>Use signed even Euler values <code>1, −1, 5, −61</code> and Fibonacci values <code>0, 1, 1, 2, 3</code>. The Fibonacci tail begins at original index 1. The anchored ordinary series, through four coefficients, are</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}A(z)&amp;\equiv 1-z+5z^2-61z^3\\B(z)&amp;\equiv 1+z+2z^2+3z^3\end{aligned}\pmod{z^4}">A(z) = 1 - z + 5z^2 - 61z^3; B(z) = 1 + z + 2z^2 + 3z^3 (mod z^4)</p>
 <p>Exact formal division gives the forward and inverse kernels</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}H(z)&amp;\equiv 1+2z-z^2+53z^3\\K(z)&amp;\equiv 1-2z+5z^2-65z^3\end{aligned}\pmod{z^4}">H(z) = 1 + 2z - z^2 + 53z^3; K(z) = 1 - 2z + 5z^2 - 65z^3 (mod z^4)</p>
 <p>For example, at tail position 2, convolution recovers the target coefficient:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\begin{aligned}b_2&amp;=h_0a_2+h_1a_1+h_2a_0\\&amp;=(1)(5)+(2)(-1)+(-1)(1)=2.\end{aligned}">b_2 = h_0*a_2 + h_1*a_1 + h_2*a_0 = 1*5 + 2*(-1) + (-1)*1 = 2</p>
 <p>The corresponding leading four-by-four convolution matrices are</p>
 <div class="sr-transfer-static-matrices">
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(H)=\begin{pmatrix}1&amp;0&amp;0&amp;0\\2&amp;1&amp;0&amp;0\\-1&amp;2&amp;1&amp;0\\53&amp;-1&amp;2&amp;1\end{pmatrix}">L(H) = [[1,0,0,0], [2,1,0,0], [-1,2,1,0], [53,-1,2,1]]</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(K)=\begin{pmatrix}1&amp;0&amp;0&amp;0\\-2&amp;1&amp;0&amp;0\\5&amp;-2&amp;1&amp;0\\-65&amp;5&amp;-2&amp;1\end{pmatrix}">L(K) = [[1,0,0,0], [-2,1,0,0], [5,-2,1,0], [-65,5,-2,1]]</p>
 </div>
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(H)L(K)=L(K)L(H)=I_4">L(H)*L(K) = L(K)*L(H) = I_4</p>
 <p>For local row n and column k, the product has the exact Toeplitz convolution formula</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\bigl(L(H)L(K)\bigr)_{n,k}=\sum_{\ell=k}^{n}h_{n-\ell}k_{\ell-k}=\delta_{n,k},\qquad 0\le k\le n<4">(L(H)*L(K))[n,k] = sum_(ell=k)^n h_(n-ell)*k_(ell-k) = delta(n,k), 0<=k<=n<4</p>
 <p>For example, the bottom-left entry cancels exactly:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="\bigl(L(H)L(K)\bigr)_{3,0}=(53)(1)+(-1)(-2)+(2)(5)+(1)(-65)=0">(L(H)*L(K))[3,0] = (53)*(1) + (-1)*(-2) + (2)*(5) + (1)*(-65) = 0</p>

 <p>Here is the corresponding action on the anchored sequence coefficients:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(H)\begin{pmatrix}1\\-1\\5\\-61\end{pmatrix}=\begin{pmatrix}1\\1\\2\\3\end{pmatrix}">L(H) [1, -1, 5, -61] = [1, 1, 2, 3]</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="L(K)\begin{pmatrix}1\\1\\2\\3\end{pmatrix}=\begin{pmatrix}1\\-1\\5\\-61\end{pmatrix}">L(K) [1, 1, 2, 3] = [1, -1, 5, -61]</p>
 <p>Matrix rows and columns use anchored tail positions. The displayed four-by-four matrices are exact inverses, with the original Euler and Fibonacci indices tracked separately.</p>
 <p>Only four coefficients are verified here. The cited derivation addresses the separate infinite formal relation and the boundary term required to transport a recurrence.</p>
 </details>
 <details class="sr-transfer-sources"><summary>Sources and derivations</summary><p class="sr-transfer-links"><a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-connections/IDENTITIES.md">Recurrence and transfer derivations</a> · <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-connections/AUDIT.md">Research audit</a> · <a href="collection/demonstrations/EULER_PACKETS.html#transfer-the-euler-sequence-to-fibonacci-values">Euler and Fibonacci worked derivation</a> · <a download href="assets/sequence-research-connections.json">Related connections JSON</a></p></details>
 <details class="sr-transfer-compose-details"><summary>Composition through a third sequence</summary><div class="sr-transfer-compose-static">
 <h3>Composition through an intermediate sequence</h3>
 <p>For three anchored series with nonzero constant coefficients, formal division gives the following finite composition:</p>
 <p class="sar-formula sr-transfer-equation" data-math-latex="H_{AC}(z)\equiv H_{BC}(z)H_{AB}(z)\pmod{z^L},\qquad L(H_{AC})=L(H_{BC})L(H_{AB})">H_AC(z) = H_BC(z)*H_AB(z) (mod z^L); L(H_AC) = L(H_BC)*L(H_AB)</p>
 <p>The original index shifts add: <code>Δ_AC = Δ_AB + Δ_BC</code>. This is an algebraic consequence of invertible anchored series, not evidence of a shared recurrence or agreement beyond stored coefficients. The interactive composition panel checks each coefficient and exports its exact certificate.</p>
 </div></details>
 </section>'''
    about='<section id="library-sources" class="sl-optional-section"><h2>Definitions, scope, and downloads</h2><details class="sl-topic-disclosure"><summary>Read catalogue scope and download source files</summary><p>The '+str(len(expanded_catalogue()))+' parameter records cover reciprocal powers (N=2–16, r=1–8, complementing the curated sequences), transfer tangents (N=2–16), congruential coefficient components (N=2–12, 1≤j&lt;N, r=1–4), Appell components (N=2–6, 0≤j&lt;N, r=1–2, x=1 or 2), and classical multisections (N=2–12, 0≤j&lt;N).</p><p>Research families include secancy parameter columns (N=2–12, k=1–8), theta specializations (x=1–12), and theta polynomial columns (k=1–12). Ordinary k-step families add 120 instances with order 2–16, power 1–4, and weight 1–2. Ten k-bonacci records with zero initial seeds use orders 7–16 and store 48 terms.</p><p>Other scalar records store 24 terms at their stated offsets. Polynomial columns begin at their first nonzero n. The coefficient triangles preserve complete rows n=0–12, with separate row, column, and flat indices. The supported Appell columns retain their polynomial row map Nn+k. Other parameter records use n=0–23. Each rational coefficient is reduced before its signed numerator or positive denominator is recorded. Every entry links to its definition and states its normalization.</p><p>Different parameter choices can yield the same sequence. Finite comparisons alone do not prove an identity or establish novelty. Hypergeometric labels distinguish term formulas, generating functions, and coefficient extraction.</p><p><a download href="assets/sequence-library-index.csv">Complete index CSV</a> · <a download href="assets/sequence-formulas.json">All formula representations JSON</a> · <a download href="assets/sequence-formula-source.zip">Exact Python generator and defining source</a> · <a href="sequence-archive.html">Research archive and generator</a></p></details></section>'
    # Keep older hash links functional. With JavaScript they redirect to focused
    # pages; without JavaScript the targeted gateway provides a usable link.
    legacy_routes=[
        ('transfers','sequence-transfers.html#transfers','Transfer workbench'),
        ('comparison','sequence-compare.html#comparison','Sequence comparison'),
        ('research-families','sequence-research.html#research-families','Research families'),
        ('generalized','sequence-research.html#generalized','Generalized families'),
        ('family-explorer','sequence-research.html#generalized','Generalized family explorer'),
        ('research-graph','sequence-connections.html#research-graph','Connection graph'),
        ('identify','sequence-identify.html#identify','Sequence identification'),
        ('modular-dynamics','sequence-modular.html#modular-dynamics','Modular dynamics'),
        ('research-notebooks','sequence-workspace.html#research-notebooks','Research notebooks and older workspaces'),
        ('oeis','sequence-oeis.html#oeis','OEIS reference lookup')]
    legacy=''.join('<section class="sl-legacy-gateway" id="'+key+'"><h2>'+label+'</h2><p>This tool now has its own page. <a href="'+url+'">Open '+label+'</a>.</p></section>'
                   for key,url,label in legacy_routes)
    closed_theorems=('''<section id="closed-theorems" class="sl-optional-section">
      <h2>Closed forms and proved identities</h2>
      <p>Choose a result to read its precise domain and normalization.
      For complete derivations, use the mathematical source linked below.</p>
      <details id="central-binomial-recurrence"><summary>A uniform recurrence for weighted binomial rows</summary>
      <p>The family a_n(r) = sum_(k=0)^n binom(n,floor(k/2)) (-r)^(n-k)
      satisfies one polynomial-coefficient recurrence for every complex r and every n at least 3:</p>
      <pre tabindex="0" role="region" aria-label="Universal weighted binomial recurrence">r n a_n + ((r^2+1)n-2r) a_(n-1)
      - (4r(n-2)+2(r^2+1)) a_(n-2)
      - 4(r^2+1)(n-2) a_(n-3) = 0</pre>
      <p>The initial values are 1, 1-r, and r^2-r+2. The proof includes r=0,
      where the leading coefficient vanishes and the defining sum supplies the values.
      A first-order inhomogeneous relation gives an efficient exact calculation.</p>
      <p>The r=4 example is A127363. Its conjecture-labelled recurrence also appears,
      after a sign change, in A133444. The proof credits these recorded results and
      Easwar's proof of the r=2 case.</p>
      <p><a href="sequence-central-binomial.html#central-binomial">Read the theorem, full proof and attribution</a> ·
      <a href="sequence-library.html?cf-version=1&amp;cf-mode=central_binomial&amp;cf-start=0&amp;cf-count=12&amp;cf-r=4#closed-calculator-panel">Calculate the r=4 example</a> ·
      <a href="generalized-families/GF-CF-CENTRAL-BINOMIAL.html">Explore the family and its six examples</a>.</p>
      </details>
      <details><summary>Universal Hankel 4F3 and real-zero theorem</summary>
      <p>The A163865 Hankel determinant is independent of the binomial-shift parameter.
      The empty determinant equals 1. For N at least 1 and arbitrary complex c:</p>
      <pre tabindex="0" role="region" aria-label="Hankel hypergeometric expression">H_N(c) = 2^(N-1) 4F3(-N/2, (1-N)/2, (N-1)/2, N/2;
                           -1/2, -1/4, 1/4; -c^2/16)</pre>
      <p>The series terminates. Its zeros as a polynomial in c are real and nonzero
      for N at least 2. The generating-function denominator divides
      ((1-2z)^4 + 4c^2 z^2)^3.</p>
      <p><a href="sequence-families/KFOR-CF-W-0-1.html">Inspect the exact c=1 determinants</a>.</p>
      </details>
      <details><summary>Arbitrary two-delay residue-class formulas</summary>
      <p>For C_n = [z^n](1-u z^p-v z^q)^(-r), p and q are positive integers.
      Removing their gcd and enumerating pi+qj=n gives one terminating
      QF(Q-1) for each admissible residue. The exact finite sum handles zero weights
      and negative integral r without undefined divisions.</p>
      <p><a href="sequence-families/KFOR-CF-S-2-5-1-1-1.html">Read the 2,5 delay example and its 5F4 subsequence</a>.</p>
      </details>
      <details><summary>Weighted A163865 and all polynomially weighted jets</summary>
      <p>For d at least 0, u_n = J_(n,d)(1)+n J_(n-1,d)(1), where
      J_(n,d)(lambda) = sum binom(n,2m) falling(m,d) binom(2m,m) lambda^(n-2m).
      Every polynomial weight decomposes into finitely many of these cases.</p>
      <pre tabindex="0" role="region" aria-label="Weighted jet generating function">sum u_n z^n =
      ((2d)!/d!) z^(2d) (1+(2d-1)z-(2d+4)z^2)
      / (1-2z-3z^2)^(d+3/2)</pre>
      <p>The d=0 case is identified as A163865 in the supplied source.
      <a href="sequence-families/KFOR-CF-JET-01.html">Read the d=1 exact sequence</a>.</p>
      </details>
      <details><summary>Fixed-size Chebyshev formula for weighted Hankel transforms</summary>
      <p>The Hankel transform of u_n at weight d is W_N^[d](1). Collection III
      proves a root-free formula using the remainders of two Chebyshev polynomials
      modulo x^2+(2d+1)cx-4. It works at repeated roots and the initial zero block.
      The generic minimal eventual recurrence order is 4(d+1)(d+2)+4.
      At c=1 the exact orders for d=0,1,2 are 12, 28, 52.</p>
      <p>The first d=1 quartic is W_4(c) = 48(27c^4+6c^2+2). It has no real zeros, unlike the unweighted family.</p>
      <p><a href="sequence-families/KFOR-CF-W-2-1.html">Read the d=2 determinant sequence</a>.</p>
      </details>
      <details><summary>Arbitrary polynomial weights: bounded-rank Hankel matrices</summary>
      <p>Let P(m) be any polynomial of degree D, and put
      F_P[x^(2m)] = P(m) binom(2m,m), with odd moments zero.
      The perturbed functional is L_(P,c)[f] = F_P[f] + c F_P[f'].
      Its Chebyshev Gram matrix has separated off-diagonal blocks
      of rank at most 2(D+1), independently of determinant size N.
      If c=0, the bound is 2D.</p>
      <p>The explicit Chebyshev moment formulas are finite products.
      They give a root-free, exact rational Schur algorithm with a
      fixed-width matrix state. After initialization, ordinary
      nonsingular steps take O(D^2) rational-arithmetic operations each.
      Exact block lookahead recovers zeros and later nonzero leading minors.
      This is not a uniform fixed-bit-complexity bound.</p>
      <p>The determinant remains independent of binomial shifts and even
      in c. An arbitrary nonconstant polynomial weight does not preserve
      positivity, so the unweighted all-real-zero theorem cannot be
      carried over without a separate argument.</p>
      <p><a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/POLYNOMIAL_HANKEL_STRUCTURE.md">Read the complete polynomial-weight theorem and proof</a> ·
      <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/sequence_polynomial_hankel.py">Run the exact structured solver</a> ·
      <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_polynomial_hankel.py">Inspect independent tests</a>.</p>
      </details>
      <details id="differential-hankel-theorem"><summary>Finite-order differential Hankel calculus</summary>
      <p>For a polynomial P(m) of degree D and a finite constant-coefficient
      operator D_x = c_0 + c_1 partial_x + ... + c_r partial_x^r,
      the associated Chebyshev Gram matrix has separated off-diagonal
      blocks of rank at most 2(D+r), independent of determinant size N.</p>
      <p>All derivative Chebyshev moments admit exact finite products.
      The weight-raising ladder is
      F_(d+1)[C_n^(k)] = (n^2-(k+2d)^2) F_d[C_n^(k)] / (4(d+k)),
      for d+k greater than zero. This leads to explicit row generators
      and a structured exact Schur solver, including initial zero blocks
      and singular-pivot lookahead. The runtime bound is stated in
      rational-arithmetic operations, not fixed-bit complexity.</p>
      <p>The bounded browser example uses P(m)=1+m and
      D_x=1+2 partial_x+partial_x^2. Its first determinant values are
      1, 1, 2, -84, -456, 52197296.</p>
      <p><a href="sequence-library.html?cf-version=1&cf-mode=differential_hankel&cf-start=0&cf-count=7&cf-a0=1&cf-a1=1&cf-a2=0&cf-a3=0&cf-c0=1&cf-c1=2&cf-c2=1&cf-c3=0#closed-calculator-panel">Calculate the differential Hankel example</a> ·
      <a href="sequence-differential-hankel.html#differential-hankel">Read the complete proof on .io</a> ·
      <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/FINITE_DIFFERENTIAL_HANKEL.md">Read the complete source proof</a> ·
      <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/sequence_differential_hankel.py">Run the general exact solver</a> ·
      <a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_differential_hankel.py">Inspect independent tests</a>.</p>
      </details>
      <details id="differential-moment-generating"><summary>Algebraic generating functions for all finite differential moment sequences</summary>
      <p>For any polynomial weight P(m) of degree D and any finite differential
      operator D_x=sum_(k=0)^r c_k partial_x^k, the moment series
      M(z)=sum_(n&gt;=0) F_P[D_x x^n] z^n
      has the exact algebraic form M(z)=R(z)/(1-4z^2)^(D+r+1/2),
      with deg R at most 2(D+r).</p>
      <p>The numerator follows from finite polynomial operations: begin with
      R_0(z)=sum_d a_d (2d)!/d! z^(2d)(1-4z^2)^(D-d), then apply the
      rationalized differential transform T[f]=z(f+zf') repeatedly
      to obtain every derivative contribution. The same representation
      supplies a first-order polynomial differential equation for M(z).</p>
      <p>For P(m)=1+m and D_x=1+2 partial_x+partial_x^2,
      the numerator is 1+2z-8z^2-4z^3+52z^4-16z^5-24z^6,
      with denominator (1-4z^2)^(7/2). These are moment coefficients,
      not the associated Hankel determinants.</p>
      <p><a href="sequence-library.html?cf-version=1&cf-mode=differential_moments&cf-start=0&cf-count=10&cf-a0=1&cf-a1=1&cf-a2=0&cf-a3=0&cf-c0=1&cf-c1=2&cf-c2=1&cf-c3=0#closed-calculator-panel">Calculate the exact moment sequence and its generating function</a> ·
      <a href="sequence-differential-hankel.html#math-proof-algebraic-ordinary-generating-function-for-every-finite-differential-operator">Read the complete generating-function derivation</a>.</p>
      </details>
      <details id="rational-hankel-theorem"><summary>Rational Hankel generating functions and a uniform order-nine recurrence</summary>
      <p>Every fixed polynomial weight and finite constant-coefficient differential
      operator in this calculus gives a Hankel determinant sequence with a rational
      generating function. The proof uses a boundary-safe finite-difference
      congruence and a stationary signed transfer; all zero minors are included.</p>
      <p>For the unperturbed linear weight P(m)=a+bm, the explicit identity is</p>
      <pre tabindex="0" role="region" aria-label="Uniform linear-weight Hankel recurrence">[(S-2a)(S^2-4(a-b)S+4a^2)]^3 W_n = 0, n &gt;= 1.</pre>
      <p>The order is nine generically, with possible reductions at exceptional
      parameters. The separated Gram rank 2(D+r) is sharp for nonzero inputs.
      A single rational coefficient kernel also produces every underlying moment.</p>
      <p><a href="sequence-rational-hankel.html">Read the proofs, explicit numerator, and exact certificates</a> ·
      <a href="sequence-library.html?cf-version=1&amp;cf-mode=linear_hankel&amp;cf-start=0&amp;cf-count=12&amp;cf-a0=1&amp;cf-a1=1#closed-calculator-panel">Calculate the linear-weight Hankel sequence</a>.</p>
      <p><a href="sequence-hankel-compression.html">Continue to parity compression, a uniform quadratic bound, and exact orders 63 and 112</a>.</p>
      </details>
      <details><summary>Six formulas recovered from source papers</summary>
      <p>The documented reductions cover Bernoulli four-block tangents, four-block
      Euler convolutions, integer Meixner–Pollaczek polynomials, beta-moment
      determinants, beta-binomial splitter polynomials, and the squarefree
      zeta-ratio identity already proved in Paper III. Their normalization,
      source locations and historical scope are in the full source note.</p>
      <p><a href="generalized-families/GF-CF-MEIXNER.html">Read the Meixner–Pollaczek family</a>.</p>
      </details>
    </section>''')
    closed_calculator=(
        '<details id="closed-calculator-panel" class="sl-topic-disclosure">'
        '<summary>Calculate exact coefficients and determinants</summary>'
        '<div id="closed-calculator-root">'
        '<p class="cf-placeholder">Choose a construction and calculate exact coefficients, moments, '
        'or Hankel determinants. The differential moment view also gives the algebraic generating function.</p>'
        '</div><noscript><p>JavaScript is not required to read the definitions and exact record tables above. '
        'Open any record for its complete static 24-term table.</p></noscript></details>')
    closed_css='<link rel="stylesheet" href="assets/sequence-closed-forms.css?v='+hashlib.sha256(
        (site.output/'assets/sequence-closed-forms.css').read_bytes()).hexdigest()[:12]+'">'
    # One central entry point. Specialized pages stay as focused views, not
    # separate catalogues. Expensive tools mount only when opened.
    workflow_nav=(
        '<nav id="sequence-research-desk" class="sl-workflow-nav" aria-label="Sequence research workflow">'
        '<a href="#library-search"><strong>1. Find</strong><span>Records and formulas</span></a>'
        '<a href="#closed-calculator-panel"><strong>2. Calculate</strong><span>Exact integer values</span></a>'
        '<a href="#sequence-research-hub"><strong>3. Investigate</strong><span>Connections and comparisons</span></a>'
        '<a href="#sequence-proof-path"><strong>4. Verify</strong><span>Proofs and evidence</span></a></nav>')
    research_hub=(
        '<section id="sequence-research-hub" class="sl-optional-section sl-research-hub">'
        '<h2>Continue your research</h2>'
        '<p>All '+f'{total:,}'+' integer records and their '+f'{representations:,}'+' formula representations share one index. '
        'The views below use those same records and retain their exact indices and review boundaries.</p>'
        '<div class="sl-workflow-choices">'
        '<article><h3>Compare and transfer</h3>'
        '<p>Compare exact prefixes, inspect finite disagreements, or build algebraic transfer certificates.</p>'
        '<p><a href="sequence-compare.html#comparison">Compare sequences</a> · '
        '<a href="sequence-transfers.html#transfers">Transfer workbench</a></p></article>'
        '<article><h3>Explore constructions</h3>'
        '<p>Browse all '+str(len(generalized['families']))+' generalized definitions, their source papers and member records.</p>'
        '<p><a href="sequence-research.html#research-families">Research families</a> · '
        '<a href="generalized-families/index.html">Complete family index</a></p></article>'
        '<article><h3>Cross-check and reproduce</h3>'
        '<p>Inspect the retained OEIS reference data, source notes, and reproducible exact generators.</p>'
        '<p><a href="sequence-oeis.html#oeis">OEIS reference lookup</a> · '
        '<a href="#sequence-proof-path">Proof and verification records</a></p></article>'
        '</div></section>'
        '<section id="sequence-proof-path" class="sl-optional-section sl-proof-path">'
        '<h2>Definitions, derivations, and verification</h2>'
        '<p>Formula records retain their original source and review status. The mathematical proofs, '
        'finite exact tests, and OEIS comparisons are separate forms of evidence.</p>'
        '<details class="sl-topic-disclosure" id="sl-theorem-disclosure"><summary>Read the main closed-form theorem summaries</summary>'
        +closed_theorems+'</details>'
        '<details class="sl-topic-disclosure"><summary>Open source notes and exact verification programs</summary>'
        '<p><a href="sequence-closed-forms.html#closed-theorems">Full Closed Forms reading page</a> · '
        '<a href="sequence-central-binomial.html">Weighted binomial recurrence proof</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/COLLECTION_II_ADDITIONS.md">'
        'Complete mathematical supplement</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_closed_forms_extended.py">'
        'Independent Python regression tests</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/POLYNOMIAL_HANKEL_STRUCTURE.md">'
        'Arbitrary polynomial-weight Hankel theorem</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_closed_forms_core.mjs">'
        'Exact browser arithmetic tests</a></p>'
        '<p>The retained OEIS snapshot has finite comparisons for '+f'{len(checked_ids):,}'+' of '+f'{len(entries):,}'+' current records. '
        'Each comparison is bound to the stored integer terms and retained reference data. '
        'Finite agreement is not a proof of infinite equality or historical novelty.</p></details>'
        '</section>')
    site.page('sequence-library.html','Sequence Library · Search',
              wrap(closed_css+header+workflow_nav+controls+closed_calculator+research_hub+about+legacy,page_kind='search'))
    site.page('sequence-transfers.html','Sequence Library · Transfer',
              wrap(page_heading('Transfer between sequences',
                  'Calculate exact forward and inverse convolution maps between stored scalar prefixes. All certificates refer to the selected finite window.',
                  'transfer','transfers')+transfers,page_kind='transfer'))
    site.page('sequence-compare.html','Sequence Library · Compare',
              wrap(page_heading('Compare sequences',
                  'Compare up to four stored sequences or OEIS excerpts. Exact values remain in the data table while plots show finite windows.',
                  'compare','comparison')+
                  '<section id="comparison"><h2>Comparison workbench</h2><p>Enable JavaScript to compare records. You can browse the <a href="sequence-library.html#library-search">sequence search</a> without it.</p></section>',
                  page_kind='compare'))
    research_nav=('<nav class="sl-research-nav" aria-label="Research and tool pages">'
                  '<a href="#research-families">Research families</a><a href="#generalized">Generalized families</a>'
                  '<a href="sequence-closed-forms.html#closed-forms">Closed forms II–III</a>'
                  '<a href="sequence-connections.html#research-graph">Connections</a>'
                  '<a href="sequence-identify.html#identify">Identify terms</a>'
                  '<a href="sequence-modular.html#modular-dynamics">Modular dynamics</a>'
                  '<a href="sequence-workspace.html#research-notebooks">Combined notebooks</a></nav>')
    closed_entries=[item for item in entries if item.get('closed_form_collection')]
    closed_families=[item for item in generalized['families'] if item['id'].startswith('GF-CF-')]
    active_closed_families=sum(bool(family['record_ids']) for family in closed_families)
    research_choices=('<div class="sl-research-choices" aria-label="Specialized research tools">'
                      '<article><h3><a href="sequence-closed-forms.html#closed-forms">Closed forms II–III</a></h3>'
                      '<p>Read '+str(active_closed_families)+' exact constructions, '+str(len(closed_entries))+
                      ' curated integer records and their source derivations.</p></article>'
                      '<article><h3><a href="sequence-connections.html#research-graph">Connection graph</a></h3>'
                      '<p>Inspect documented sequence relationships, directed paths and exact transfer compositions.</p></article>'
                      '<article><h3><a href="sequence-identify.html#identify">Identify terms</a></h3>'
                      '<p>Test integer patterns and transformations against local records or retained OEIS excerpts.</p></article>'
                      '<article><h3><a href="sequence-modular.html#modular-dynamics">Modular dynamics</a></h3>'
                      '<p>Explore recurrence states and verify a finite modular cycle certificate.</p></article>'
                      '<article><h3><a href="sequence-workspace.html#research-notebooks">Research notebooks</a></h3>'
                      '<p>Save settings across several tools in the combined compatibility workspace.</p></article></div>')
    research_legacy=''.join(
        '<section class="sl-legacy-gateway" id="'+key+'"><h2>'+label+'</h2>'
        '<p>Open the <a href="'+url+'">'+label.lower()+' page</a>.</p></section>'
        for key,url,label in [
            ('research-graph','sequence-connections.html#research-graph','Connection graph'),
            ('identify','sequence-identify.html#identify','Sequence identification'),
            ('modular-dynamics','sequence-modular.html#modular-dynamics','Modular dynamics'),
            ('research-notebooks','sequence-workspace.html#research-notebooks','Research notebooks')])
    site.page('sequence-research.html','Sequence Library · Research',
              wrap(page_heading('Research families',
                  'Browse exact research records and generalized family definitions. Each interactive research tool has its own page.',
                  'research','research-families')+research_nav+research.replace('<details class="sl-topic-disclosure">','<details class="sl-topic-disclosure" open>',1)+generalized_sections(only=['generalized'])+
                   '<h2 class="sl-tool-heading">Research workbenches</h2>'+research_choices+research_legacy,
                   page_kind='research'))
    # The closed-form supplement is a focused reading page, not a sixth tool
    # crowded into Search. Its exact records also appear in the unified index.
    closed_cards=''.join(
        '<article class="sar-card"><h3><a href="'+e(family['url'])+'">'+e(family['title'])+'</a></h3>'
        '<p>'+e(family['note'])+'</p><p>'+str(len(family['record_ids']))+' indexed integer records.</p></article>'
        for family in closed_families)
    closed_rows=''.join(
        '<tr><th scope="row"><a href="'+e(item['url'])+'">'+e(item['id'])+'</a></th>'
        '<td>'+e(item['title'])+'</td><td>'+str(item['offset'])+'</td>'
        '<td>'+e(', '.join(item['terms'][:5]))+'</td><td>'+('Source-supplied '+e(item['oeis'])+' · ' if item.get('source_claimed_oeis') else '')+e(oeis_comparison_summary(item))+'</td></tr>'
        for item in closed_entries)
    closed_body=(
        closed_css+
        page_heading('Closed forms: Collections II and III',
            'Exact integer records, source derivations and explicit review boundaries.',
            'research','closed-forms')+
        '<section id="closed-forms"><h2>What is in the collection?</h2><p>'+str(len(closed_entries))+' exact integer records across '+str(active_closed_families)+' constructions, '
        'plus '+str(len(closed_families)-active_closed_families)+' definition-only families. Every record has '
        '24 exact values, at least two formula representations, a stated index convention, and CSV/JSON downloads. '
        +str(sum(item['oeis_checked'] for item in closed_entries))+' of '+str(len(closed_entries))+' records have finite comparisons against the retained OEIS snapshot. '
        'A finite hit does not prove infinite identity, and an absent hit does not establish novelty.</p>'
        '<p><a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/IDENTITIES.md">'
        'Read definitions, proofs and reproduction notes</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_closed_forms.py">'
        'Review the exact independent tests</a> · '
        '<a href="sequence-library.html#library-search">Search the full library</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/COLLECTION_II_ADDITIONS.md">Read the complete theorem supplement</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/tools/test_sequence_closed_forms_extended.py">Review the extended exact tests</a></p></section>'+closed_theorems+
        closed_calculator+
        '<section><h2>'+str(len(closed_families))+' source-linked families</h2><div class="sar-grid">'+closed_cards+'</div></section>'+
        '<section><h2>'+str(len(closed_entries))+' integer records</h2><p>Displayed prefixes retain their original offsets. '
        'The four-block rows start at m=1 and refer to analytic exponent 4m-1; beta-binomial '
        'records contain explicitly unnormalized integer values. Follow each record for full tables, '
        'plots and exports.</p><div class="sar-scroll" tabindex="0" role="region" '
        'aria-label="Closed-form sequence records"><table><thead><tr><th scope="col">Record</th>'
        '<th scope="col">Construction</th><th scope="col">First index</th>'
        '<th scope="col">First five exact terms</th><th scope="col">OEIS</th></tr></thead>'
        '<tbody>'+closed_rows+'</tbody></table></div></section>')
    site.page('sequence-closed-forms.html','Sequence Library · Closed forms II and III',
              wrap(closed_body,page_kind='closed-forms'))

    # Full mathematical reading page from the same versioned source as GitHub.
    # A dependency-free renderer keeps preview and release output consistent.
    from sequence_math_reading import mathematical_reading_fragment, mathematical_example_gallery, KERNEL_EXAMPLE_COUNT
    note=(site.root/'research/sequence-closed-forms/FINITE_DIFFERENTIAL_HANKEL.md').read_text(encoding='utf-8')
    full_note=mathematical_reading_fragment(note,include_outline=True)
    differential_hankel_page=(
        closed_css+
        page_heading('Finite-order differential Hankel calculus',
            'Exact Chebyshev derivative products, algebraic moment generating functions, separated-block rank bounds and structured determinants.',
            'research','differential-hankel')+
        '<nav class="sl-tool-back" aria-label="Differential Hankel research routes">'
        '<a href="sequence-library.html#sequence-research-desk">Sequence research desk</a> · '
        '<a href="sequence-closed-forms.html#differential-hankel-theorem">Closed Forms collection</a> · '
        '<a href="sequence-rational-hankel.html">Rational Hankel continuation</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/FINITE_DIFFERENTIAL_HANKEL.md">Versioned source</a></nav>'
        '<section id="differential-hankel" class="sl-math-reading-intro"><h2>Reproduce the worked example</h2>'
        r'<p>For <span class="arithmatex">\(P(m)=1+m\)</span> and <span class="arithmatex">\(\mathcal D=1+2\partial_x+\partial_x^2\)</span>, the first exact determinants are '
        '1, 1, 2, −84, −456, 52197296. The browser calculates sizes 0 through 64 '
        'with polynomial weights and differential operators of degree and order at most 3. '
        'The general source solver supports arbitrary finite orders.</p>'
        '<p>The corresponding moments begin 1, 2, 6, 24, 66, 180. Their exact generating function is</p>'
        '<div class="arithmatex sl-math-display" tabindex="0" role="region" '
        'aria-label="Generating function for the worked example">'
        r'\[M(z)=\frac{1+2z-8z^2-4z^3+52z^4-16z^5-24z^6}{(1-4z^2)^{7/2}}.\]'
        '</div><p>'
        '<a href="sequence-library.html?cf-version=1&amp;cf-mode=differential_moments&amp;cf-start=0&amp;cf-count=10&amp;cf-a0=1&amp;cf-a1=1&amp;cf-a2=0&amp;cf-a3=0&amp;cf-c0=1&amp;cf-c1=2&amp;cf-c2=1&amp;cf-c3=0#closed-calculator-panel">Inspect the exact moment sequence and generating function</a>.</p>'
        '<p><a href="sequence-library.html?cf-version=1&amp;cf-mode=differential_hankel&amp;cf-start=0&amp;cf-count=7&amp;cf-a0=1&amp;cf-a1=1&amp;cf-a2=0&amp;cf-a3=0&amp;cf-c0=1&amp;cf-c1=2&amp;cf-c2=1&amp;cf-c3=0#closed-calculator-panel">Open the exact calculator with these parameters</a>.</p></section>'
        '<article id="differential-hankel-reading" class="sl-math-manuscript" aria-label="Full differential Hankel mathematical derivation">'
        +full_note+'</article>'
        '<nav class="sl-tool-back" aria-label="Return to verification"><a href="sequence-library.html#sequence-proof-path">Return to proof and verification index</a></nav>'
    )
    site.page('sequence-differential-hankel.html',
              'Sequence Library · Finite-order differential Hankel calculus',
              wrap(differential_hankel_page,page_kind='differential-hankel'))
    site.search.append(dict(title='Finite-order differential Hankel calculus',
                            group='Collection',kind='Mathematical derivations',
                            work_ids=[],url='sequence-differential-hankel.html',
                            text='Chebyshev higher derivatives exact finite operator rank 2(D+r) '
                                 'quasiseparable Hankel moments polynomial weight proof and calculator'))

    # Preserve complete source proofs in the static page, including without JS.
    from sequence_rational_hankel import linear_hankel_determinants
    rational_note=(site.root/'research/sequence-closed-forms/RATIONAL_HANKEL_TAILS.md').read_text(encoding='utf-8')
    linear_note=(site.root/'research/sequence-closed-forms/LINEAR_WEIGHT_RECURRENCE.md').read_text(encoding='utf-8')
    presets=[
        ('Linear weight, a=1 and b=1',1,1),
        ('Initial zero minors, a=0 and b=1',0,1),
        ('Constant weight, a=2 and b=0',2,0),
    ]
    preset_rows=[]
    for label,a,b in presets:
        link=('sequence-library.html?cf-version=1&amp;cf-mode=linear_hankel'
              '&amp;cf-start=0&amp;cf-count=12&amp;cf-a0='+str(a)+'&amp;cf-a1='+str(b)+
              '#closed-calculator-panel')
        terms=', '.join(str(x) for x in linear_hankel_determinants(a,b,7))
        preset_rows.append('<tr><th scope="row"><a href="'+link+'">'+e(label)+
                           '</a></th><td><code>'+e(terms)+'</code></td></tr>')
    rational_page=(
        closed_css+page_heading('Rational Hankel generating functions',
            'General finite differential families, sharp rank, a common rational moment kernel, and an explicit linear-weight recurrence.',
            'research','rational-hankel')+
        '<nav class="sl-tool-back" aria-label="Hankel reading routes">'
        '<a href="sequence-library.html#sequence-proof-path">Sequence proof index</a> · '
        '<a href="sequence-differential-hankel.html">Differential Hankel foundations</a> · '
        '<a href="sequence-hankel-compression.html">Quadratic and mixed recurrences</a> · '
        '<a href="sequence-central-binomial.html#math-proof-8-classical-coefficient-transfer">Binomial coefficient transfer</a></nav>'
        '<section id="rational-hankel" class="sl-math-reading-intro"><h2>From moments to determinant recurrences</h2>'
        '<p>The moment index and determinant size describe different sequences. '
        'The moment generating function is algebraic. For every fixed polynomial '
        'weight and finite constant-coefficient differential operator, the Hankel '
        'determinants also have a rational generating function, by the separate proof below.</p>'
        '<p>For the identity operator and a linear weight, one explicit order-nine '
        'recurrence works at every parameter. Its general bound includes exceptional '
        'cases with smaller minimal order and initial zero minors.</p>'
        '<nav aria-label="Rational Hankel sections"><a href="#rational-hankel-proof">General proof</a> · '
        '<a href="#linear-weight-proof">Linear-weight formula</a> · '
        '<a href="#rational-hankel-evidence">Review and reproduction</a></nav>'
        '<div class="sar-scroll" tabindex="0" role="region" aria-label="Worked Hankel determinant examples">'
        '<table><caption>Exact determinants W₀ through W₇; choose a row to calculate further</caption>'
        '<thead><tr><th scope="col">Weight</th><th scope="col">Exact determinants</th></tr></thead>'
        '<tbody>'+''.join(preset_rows)+'</tbody></table></div></section>'
        '<article id="rational-hankel-proof" class="sl-math-manuscript" aria-label="General rational Hankel proof">'
        +mathematical_reading_fragment(rational_note,include_outline=True)+'</article>'
        '<section id="linear-weight-proof" class="sl-math-manuscript" aria-label="Uniform linear-weight theorem">'
        '<h2>Explicit linear-weight recurrence and numerator</h2>'
        +mathematical_reading_fragment(linear_note,include_outline=True,id_prefix='linear-proof-')+'</section>'
        '<section id="rational-hankel-evidence" class="sl-math-reading-intro"><h2>Review and reproduction</h2>'
        '<p>The general result has a written proof and exact implementation checks. '
        'The linear-weight theorem additionally uses a complete degree-18 '
        'polynomial-identity certificate. Its nineteen full transfer-vector checks '
        'cover the uniform identity by the proved degree bound. '
        'The review is a project self-review; historical novelty is unassessed.</p>'
        '<p><a download href="assets/sequence-formula-source.zip">Download proofs, exact solvers, and verifiers</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/RATIONAL_HANKEL_REVIEW.md">Read the self-review</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/RATIONAL_HANKEL_LITERATURE.md">Read the literature scope</a></p>'
        '<p>The large transfer bound establishes existence; it is not an efficiency '
        'claim. The existing Schur calculator remains available for higher-order '
        'differential examples.</p></section>'
    )
    site.page('sequence-rational-hankel.html','Sequence Library · Rational Hankel generating functions',
              wrap(rational_page,page_kind='rational-hankel'))
    site.search.append(dict(title='Rational Hankel generating functions and linear-weight recurrences',
        group='Collection',kind='Mathematical derivations',work_ids=[],
        url='sequence-rational-hankel.html',
        text='rational OGF constant coefficient recurrence Hankel polynomial weight finite differential '
             'sharp rank common rational kernel order nine a+bm singular minors exact certificate'))

    parity_note=(site.root/'research/sequence-closed-forms/PARITY_HANKEL_RECURRENCES.md').read_text(encoding='utf-8')
    mixed_note=(site.root/'research/sequence-closed-forms/MIXED_HANKEL_RECURRENCE.md').read_text(encoding='utf-8')
    compression_presets=[
        ('Quadratic weight P(m)=1+m²', [1,1,1,0], [1,0,0,0], '63'),
        ('Mixed weight/operator P(m)=1+m, D=1+2∂ₓ', [1,1,0,0], [1,2,0,0], '112'),
    ]
    from sequence_differential_hankel import structured_differential_hankel
    compression_rows=[]
    for label,weights,operator,order in compression_presets:
        link=('sequence-library.html?cf-version=1&amp;cf-mode=differential_hankel'
              '&amp;cf-start=0&amp;cf-count=12'+
              ''.join('&amp;cf-a'+str(i)+'='+str(value) for i,value in enumerate(weights))+
              ''.join('&amp;cf-c'+str(i)+'='+str(value) for i,value in enumerate(operator))+
              '#closed-calculator-panel')
        terms=', '.join(str(value) for value in structured_differential_hankel(weights,operator,7))
        compression_rows.append('<tr><th scope="row"><a href="'+link+'">'+e(label)+
            '</a></th><td>'+order+'</td><td><code>'+e(terms)+'</code></td></tr>')
    compression_page=(
        closed_css+page_heading('Smaller Hankel transfers and exact recurrences',
            'Parity compression, a uniform quadratic bound, and certified minimal orders 63 and 112.',
            'research','hankel-compression-intro')+
        '<nav class="sl-tool-back" aria-label="Hankel continuation routes">'
        '<a href="sequence-rational-hankel.html">General rationality and linear-weight theorem</a> · '
        '<a href="sequence-differential-hankel.html">Differential Hankel foundations</a> · '
        '<a href="sequence-library.html#sequence-proof-path">Sequence proof index</a></nav>'
        '<section id="hankel-compression-intro" class="sl-math-reading-intro"><h2>From existence to usable recurrences</h2>'
        '<p>Parity reduces the quadratic case from 12,870 states to two 70-state '
        'blocks. A complete polynomial certificate gives a uniform recurrence '
        'bound of 126 for every quadratic weight. Two worked examples have '
        'smaller, exact minimal eventual orders: 63 for P(m)=1+m² and 112 '
        'for P(m)=1+m with D=1+2∂ₓ. Both worked recurrences begin at n=1.</p>'
        '<p>The mixed example includes a zero second determinant. Its certificate '
        'checks all 12,870 state coordinates over the integers. The quadratic '
        'example has a separate product-state certificate; neither result rests '
        'on fitting a finite list of determinant values.</p>'
        '<nav aria-label="Compression proof sections"><a href="#parity-compression-proof">Parity and quadratic proofs</a> · '
        '<a href="#mixed-recurrence-proof">Mixed recurrence proof</a> · '
        '<a href="#compression-reproduction">Reproduce the certificates</a></nav>'
        '<div class="sar-scroll" tabindex="0" role="region" aria-label="Worked recurrence examples">'
        '<table><caption>Exact determinants W₀ through W₇; choose an example to calculate further</caption>'
        '<thead><tr><th scope="col">Example</th><th scope="col">Minimal eventual order</th>'
        '<th scope="col">Exact determinants</th></tr></thead><tbody>'+''.join(compression_rows)+'</tbody></table></div></section>'
        '<article id="parity-compression-proof" class="sl-math-manuscript" aria-label="Parity compression and quadratic recurrence proofs">'
        +mathematical_reading_fragment(parity_note,include_outline=True,id_prefix='parity-proof-')+'</article>'
        '<article id="mixed-recurrence-proof" class="sl-math-manuscript" aria-label="Exact mixed recurrence proof">'
        '<h2>A mixed weight and differential operator</h2>'
        +mathematical_reading_fragment(mixed_note,include_outline=True,id_prefix='mixed-proof-')+'</article>'
        '<section id="compression-reproduction" class="sl-math-reading-intro"><h2>Reproduce the certificates</h2>'
        '<p>Download the source ZIP and run the five commands in '
        '<code>research/sequence-closed-forms/HANKEL_COMPRESSION_REPRODUCE.md</code>. '
        'Python 3.10+ and its standard library suffice. The replayers reconstruct '
        'the defining objects and check the saved coefficients.</p>'
        '<p>The uniform proof checks 351 parameter points covering every degree-25 '
        'coefficient: 702 full block identities and 5,616 early identities. '
        'The product-polynomial identity is checked symbolically over an integer '
        'polynomial ring. The worked examples include separate tensor and '
        'bitmask implementations and degree-preserving coprimality certificates.</p>'
        '<p><a download href="assets/sequence-formula-source.zip">Download proofs, coefficients, and standard-library verifiers</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/HANKEL_COMPRESSION_REVIEW.md">Read the self-review</a> · '
        '<a href="https://raw.githubusercontent.com/KomorebiP/Operation-KOMOREBI/main/research/sequence-closed-forms/retained-sources/sequence-formula-source-f3da1097.zip">Retained previous source edition</a></p>'
        '<p>Review provenance is project self-review. Independent review, Lean '
        'formalization, and historical novelty are unassessed. A sharp uniform '
        'quadratic order-63 formula and a general mixed-parameter minimal-order '
        'formula remain open.</p></section>'
    )
    site.page('sequence-hankel-compression.html','Sequence Library · Hankel compression and exact recurrences',
              wrap(compression_page,page_kind='hankel-compression'))
    site.search.append(dict(title='Hankel parity compression, quadratic weights and mixed recurrences',
        group='Collection',kind='Mathematical derivations',work_ids=[],url='sequence-hankel-compression.html',
        text='quadratic polynomial weights parity even odd finite differential operators '
             'minimal recurrence order 63 112 uniform 126 complete polynomial identity integer transfer certificate'))

    central_note=(site.root/'research/sequence-closed-forms/CENTRAL_BINOMIAL_RECURRENCE.md').read_text(encoding='utf-8')
    central_reading=mathematical_reading_fragment(central_note,include_outline=True)
    example_note=(site.root/'research/sequence-closed-forms/ALGEBRAIC_KERNEL_EXAMPLES.md').read_text(encoding='utf-8')
    central_examples=mathematical_example_gallery(example_note)
    binomial_script=(site.root/'website/assets/sequence-binomial-reading.mjs').read_bytes()
    site.write('assets/sequence-binomial-reading.mjs',binomial_script.decode('utf-8'))
    binomial_script_url='assets/sequence-binomial-reading.mjs?v='+hashlib.sha256(binomial_script).hexdigest()[:12]
    central_example=('sequence-library.html?cf-version=1&amp;cf-mode=central_binomial'
                     '&amp;cf-start=0&amp;cf-count=12&amp;cf-r=4#closed-calculator-panel')
    central_page=(
        closed_css+
        page_heading('Weighted binomial sums',
            f'Uniform recurrences and algebraic generating functions, with complete proofs and {KERNEL_EXAMPLE_COUNT} worked examples.',
            'research','central-binomial')+
        '<nav class="sl-tool-back" aria-label="Weighted binomial research routes">'
        '<a href="sequence-closed-forms.html#central-binomial-recurrence">Closed Forms collection</a> · '
        '<a href="generalized-families/GF-CF-CENTRAL-BINOMIAL.html">Family and indexed examples</a> · '
        '<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/CENTRAL_BINOMIAL_RECURRENCE.md">Source manuscript</a></nav>'
        '<nav class="sl-binomial-jumps" aria-label="Reading routes">'
        '<a href="#math-proof-using-the-formula">Start with a calculation</a>'
        '<a href="#math-proof-1-definition-and-universal-recurrence">Theorem and proof</a>'
        '<a href="#math-proof-9-arbitrary-block-lengths-and-residue-weights">Larger block family</a>'
        '<a href="#math-proof-10-polynomial-weights-and-recurrence-weights">Further weights</a>'
        f'<a href="#kernel-examples">{KERNEL_EXAMPLE_COUNT} examples</a>'
        '<a href="#binomial-attribution">Historical context</a>'
        '<a href="#math-proof-7-exact-computation-and-reproduction">Reproduction</a>'
        '<a href="#math-proof-11-references">References</a></nav>'
        '<section id="central-binomial" class="sl-math-reading-intro"><h2>From one sequence to a general family</h2>'
        '<p>At r=4, the sequence begins 1, −3, 14, −57, 246, −1038, 4424. '
        'One recurrence covers every complex value of r. The general construction allows arbitrary block lengths, '
        'independent residue weights, and weights satisfying a linear recurrence with constant coefficients. '
        f'The article develops these results and illustrates them in {KERNEL_EXAMPLE_COUNT} worked examples.</p>'
        '<p>For a first reading, start with the <a href="#math-proof-reading-the-parameters">parameter guide</a> '
        'and <a href="#math-proof-using-the-formula">worked substitution</a>. '
        'The examples apply the method to familiar sequences, larger blocks, and different weight rules.</p>'
        '<p>The browser calculator evaluates the original two-position family for integer r from −12 through 12 '
        'and indices from 0 through 160. The larger families have written formulas, worked values, and exact Python checks below.</p>'
        '<p><a href="'+central_example+'">Calculate and export the r=4 sequence</a> · '
        '<a href="sequence-families/KFOR-CF-CB-4.html">Read its exact stored terms and three formulas</a> · '
        '<a download href="assets/sequence-formula-source.zip">Download the manuscripts, code and tests</a></p></section>'
        '<section id="binomial-attribution" class="sl-binomial-status" aria-labelledby="binomial-status-heading">'
        '<h2 id="binomial-status-heading">Historical context and scope</h2>'
        '<p>The table identifies the established tools, previously recorded special cases, '
        'and the general statements proved in this article.</p>'
        '<table><caption>Attribution and scope of the results</caption>'
        '<thead><tr><th scope="col">Result</th><th scope="col">Status</th></tr></thead><tbody>'
        '<tr><th scope="row">Coefficient transfer</th><td>Classical Lagrange inversion. '
        '<a href="https://arxiv.org/html/1609.05988v1#S2.SS1">Gessel, equations (2.1.4) and (2.1.6)</a>.</td></tr>'
        '<tr><th scope="row">Original family and Catalan construction</th><td>Established in '
        '<a href="https://oeis.org/A107430">A107430</a>, <a href="https://oeis.org/A127361">A127361</a>, '
        'and <a href="https://oeis.org/A127363">A127363</a>.</td></tr>'
        '<tr><th scope="row">The r=2 recurrence</th><td>Already proved by '
        '<a href="https://arxiv.org/html/2608.22053v2#S7">Easwar, Theorem 7.1</a>. Recovered here.</td></tr>'
        '<tr><th scope="row">The r=4 recurrence</th><td>Recorded by Mathar in A127363 and, with alternating signs, '
        'by Kotesovec in <a href="https://oeis.org/A133444">A133444</a>. Included in the uniform proof below.</td></tr>'
        '<tr><th scope="row">The all-r recurrence</th><td>Derived and proved here for every complex r. '
        'It extends the fixed-parameter statement.</td></tr>'
        '<tr><th scope="row">Arbitrary blocks and further weights</th><td>Explicit applications of the classical identity, '
        'with complete derivations and worked examples.</td></tr>'
        '</tbody></table><p><a href="#math-proof-6-oeis-connections-and-attribution">'
        'Read the source comparison, priority statement, and r=4 sign change</a>.</p></section>'
        '<article id="central-binomial-reading" class="sl-math-manuscript" aria-label="Weighted binomial sums: complete article">'
        +central_reading+'</article>'
        +central_examples+
        '<p class="sl-tool-back"><a href="sequence-rational-hankel.html">'
        'Continue to the common rational moment kernel and Hankel determinant recurrences</a>.</p>'
        '<p class="sl-tool-back"><a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-closed-forms/ALGEBRAIC_KERNEL_EXAMPLES.md">'
        'Read the complete example source</a> · <a download href="assets/sequence-formula-source.zip">'
        'Download all derivations and exact checks</a></p>'
        '<nav class="sl-tool-back" aria-label="Return to sequence research">'
        '<a href="sequence-library.html#sequence-proof-path">Return to proof and verification index</a></nav>'
        '<script type="module" src="'+binomial_script_url+'"></script>'
    )
    site.page('sequence-central-binomial.html',
              'Sequence Library · Weighted binomial sums and algebraic generating functions',
              wrap(central_page,page_kind='central-binomial'))
    site.search.append(dict(title='Weighted binomial sums and algebraic generating functions',
                            group='Collection',kind='Mathematical derivations',
                            work_ids=[],url='sequence-central-binomial.html',
                            text='A107430 A127363 A133444 A127361 Mathar Kotesovec Easwar '
                                 'all complex parameters central binomial Catalan generating function recurrence proof '
                                 f'Lagrange inversion Gessel arbitrary blocks residue weights polynomial Fibonacci Lucas Pell periodic finite support {KERNEL_EXAMPLE_COUNT} worked examples'))

    for filename,title,description,section_id,page_kind in [
        ('sequence-connections.html','Sequence connections',
         'Inspect documented relationships, directed paths and exact scalar transfer compositions.',
         'research-graph','connections'),
        ('sequence-identify.html','Identify a sequence',
         'Check finite integer patterns and their transforms against local records or the retained OEIS data.',
         'identify','identify'),
        ('sequence-modular.html','Modular dynamics',
         'Explore recurrence states modulo m and check exact finite cycle certificates.',
         'modular-dynamics','modular')]:
        site.page(filename,'Sequence Library · '+title,
                  wrap(page_heading(title,description,'research',section_id)+
                       '<nav class="sl-tool-back"><a href="sequence-research.html#research-families">Research families and other tools</a>'
                       ' · <a href="sequence-workspace.html#research-notebooks">Combined workspace</a></nav>'+
                       generalized_sections(only=[section_id]).replace('<details>','<details open>',1),page_kind=page_kind))
    standalone_reference=reference.replace('<details class="sl-topic-disclosure">',
                                           '<details class="sl-topic-disclosure" open>',1)
    site.page('sequence-oeis.html','Sequence Library · OEIS',
              wrap(page_heading('OEIS reference lookup',
                  'Search the retained OEIS terms and names in your browser. Reference excerpts do not include mathematical offsets.',
                  'oeis','oeis')+standalone_reference,page_kind='oeis'))
    # Optional compatibility workspace supports notebooks spanning several tools.
    site.page('sequence-workspace.html','Sequence Library · Combined workspace',
              wrap(page_heading('Combined research workspace',
                  'Advanced compatibility view for saved notebooks and links that use several tools together.',
                  'research','library-search')+controls+transfers+research+generalized_sections()+
                  '<section id="comparison"></section>'+reference+about,
                  page_kind='workspace'))

    rows=''.join('<tr><th scope="row"><a href="../'+x['url']+'">'+e(x['id'])+'</a></th><td>'+e(x['title'])+'</td><td>'+e(x['kind'])+'</td><td>'+str(len(x['formulas']))+'</td><td>'+str(x['offset'])+'</td></tr>' for x in entries)
    site.page('sequence-library/index.html','Complete sequence index',wrap('<nav><a href="../sequence-library.html">Search the library</a></nav><h1>Complete sequence index</h1><p>This index lists all '+str(total)+' local records. Definitions and exact tables remain available without JavaScript.</p><div class="sar-scroll" tabindex="0" role="region" aria-label="Complete sequence index"><table><thead><tr><th scope="col">ID</th><th scope="col">Name</th><th scope="col">Family</th><th scope="col">Formulas</th><th scope="col">Offset</th></tr></thead><tbody>'+rows+'</tbody></table></div>','../'))
    urls={item['id']:item['url'] for item in entries}
    for entry in entries:
        if entry['collection']!='formulas':continue
        identifier=entry['id'];start=entry['offset'];end=start+len(entry['terms'])-1
        site.write('sequence-families/'+identifier+'.json',json.dumps(entry,ensure_ascii=False,separators=(',',':'))+'\n')
        if entry.get('triangle'):
            site.write('sequence-families/'+identifier+'.csv','j,row_n,column_k,source_degree,value\n'+''.join(f'{j},{cell_coordinates(entry,j)[0]},{cell_coordinates(entry,j)[1]},{source_degree(entry,j)},{v}\n' for j,v in enumerate(entry['terms'])))
        else:site.write('sequence-families/'+identifier+'.csv','n,a(n)\n'+''.join(f'{n},{v}\n' for n,v in enumerate(entry['terms'],start=start)))
        site.write('sequence-families/'+identifier+'.txt','# '+identifier+' '+entry['title']+'\n'+''.join(f'{n} {v}\n' for n,v in enumerate(entry['terms'],start=start)))
        rational=entry.get('rational_terms')
        related=''.join('<p>Related local definition: <a href="../'+e(urls[x['id']])+'#definition">'+e(x['id'])+'</a>. '+e(x['note'])+'</p>' for x in entry.get('related_records',[]))
        coordinates=lambda n:('<td>'+str(cell_coordinates(entry,n)[0])+'</td><td>'+str(cell_coordinates(entry,n)[1])+'</td>') if entry.get('triangle') else ''
        index_label='Flat j' if entry.get('triangle') else 'Local n'
        value_label='a(j)' if entry.get('triangle') else 'a(n)'
        index_note=('Stored cells use flat indices j='+str(start)+'–'+str(end)+'. Within each row n, columns k are listed in increasing order. The source degree is computed from the row, not from j. ' if entry.get('triangle') else 'Stored indices run from n='+str(start)+' to n='+str(end)+'. The source degree/index map is '+e(entry['degree'])+'. ')+'Stored sequence values are exact integers. '+('Original rational coefficients are listed separately. ' if rational else '')+'Plots use this stored window. '+e(entry['explanation'])
        rows=''.join('<tr id="n-'+str(n)+'"><th scope="row">'+str(n)+'</th>'+coordinates(n)+'<td>'+str(source_degree(entry,n))+'</td><td>'+value+'</td>'+('<td>'+e(rational[n-start])+'</td>' if rational else '')+'</tr>' for n,value in enumerate(entry['terms'],start=start))
        body='<nav aria-label="Breadcrumb"><a href="../sequence-library.html">Sequence library</a> / '+e(identifier)+'</nav><header class="sar-header"><p class="sar-kicker">'+e(identifier)+' / Parameter record</p><h1>'+e(entry['title'])+'</h1><p>'+e(entry['status'])+'</p><nav aria-label="Entry sections"><a href="#definition">Definition</a><a href="#formulas">Formula representations</a>'+('<a href="#triangle">Coefficient triangle</a>' if entry.get('triangle') else '')+'<a href="#plot">Plot</a><a href="#exact-data">Exact data</a><a href="#oeis-matches">OEIS comparisons</a></nav></header><section id="definition"><h2>Definition and indexing</h2><p class="sar-formula">'+e(entry['formula'])+'</p><p>'+index_note+'</p>'+related+'</section><section id="formulas"><h2>Equivalent representations</h2>'+formula_block(entry)+'</section>'+triangle_section(entry)+plot_section(entry)+'<section id="exact-data"><h2>Exact indexed data</h2><p><a download href="'+identifier+'.csv">CSV</a> · <a download href="'+identifier+'.txt">Indexed text</a> · <a download href="'+identifier+'.json">Entry JSON with all formulas and comparisons</a></p><div class="sar-scroll" tabindex="0" role="region" aria-label="Exact stored values"><table><thead><tr><th scope="col">'+index_label+'</th>'+('<th scope="col">Row n</th><th scope="col">Column k</th>' if entry.get('triangle') else '')+'<th scope="col">Source degree/index</th><th scope="col">'+value_label+'</th>'+('<th scope="col">Original rational q(n)</th>' if rational else '')+'</tr></thead><tbody>'+rows+'</tbody></table></div></section>'+matches_block(entry)+'<section id="sources"><h2>Sources and reproduction</h2><p><a href="'+e(entry['source'])+'">Definition and construction source</a></p><p>The terms and formulas use the parameters listed above. KFOR identifiers are local to this library. OEIS entries use A-numbers.</p><details><summary>Reproduce this record</summary><p>Read <a href="'+e(entry['source'])+'">this record’s construction source</a> for its definitions and parameters.</p><p><a download href="../assets/sequence-formula-source.zip">Download the generators and source notes</a>. To regenerate this record as JSON, extract the bundle and run <code>python tools/sequence_formula_catalogue.py --id '+identifier+'</code> from its root directory.</p></details></section>'
        body=body.replace('<section id="plot"',entry_details(entry)+'<section id="plot"',1)
        if entry.get('calculator_url'):
            handoff='<p class="sl-record-calculator"><a href="../'+e(entry['calculator_url'],quote=True)+'">Calculate exact values with these parameters</a>. The calculator opens at this record’s first stored index.</p>'
            body=body.replace('</section><section id="formulas">',handoff+'</section><section id="formulas">',1)
        if entry.get('linear_addition'):body=body.replace(REGISTRY_PATH,'research/sequence-connections/IDENTITIES.md')
        site.page(entry['url'],entry['title']+' · '+identifier,wrap(body,'../',entry))
        site.search.append(dict(title=entry['title']+' · '+identifier,group='Collection',kind='Examples',work_ids=[],url=entry['url'],text=' '.join(f['expression'] for f in entry['formulas'])))
    site.search.append(dict(title='Sequence Library · Search',group='Collection',kind='Examples',work_ids=[],url='sequence-library.html',text=f'{total} indexed records and {representations} exact formula representations.'))
    for title,url in [('Transfer between sequences','sequence-transfers.html'),('Compare sequences','sequence-compare.html'),('Research families and sequence tools','sequence-research.html'),('Connection graph','sequence-connections.html'),('Identify a sequence','sequence-identify.html'),('Modular dynamics','sequence-modular.html'),('OEIS reference lookup','sequence-oeis.html')]:
        site.search.append(dict(title=title,group='Collection',kind='Examples',work_ids=[],url=url,text='Sequence Library exact arithmetic and research tools.'))
    return dict(entries=total,new_entries=len(expanded_catalogue()),formulas=representations,oeis_sequences=snapshot['sequence_count'],oeis_bytes=sum(x['bytes'] for x in snapshot['snapshot']['files']),generalized_families=len(generalized['families']),generalized_sources=len(generalized['sources']))
