"""Source-bound generalized families, kept distinct from integer records."""
from copy import deepcopy
import csv
from functools import lru_cache
from hashlib import sha256
from html import escape as e
import json
import io
from pathlib import Path
from urllib.parse import quote, urlencode
from sequence_archive_families import ARCHIVE_MEMBERSHIP, archive_definitions, archive_parameters

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='manifests/sequence-generalized-sources.json'
BASE='https://github.com/KomorebiP/Operation-KOMOREBI/blob/8a97573e979e868e675629b091ed3f5841ac2eb3/'
REG='monographs/special-functions/supporting-sources/projector-special-functions-registry/Projector_Special_Functions_Registry.tex'
# The general coefficient-section construction applies beyond the finite set
# of parent generators offered by the exact browser controls.
SECTION_EXPLORER_PARENTS=frozenset(('fibonacci','lucas','pell','factorial','catalan','central-binomial','triangular','square','cube','power-two','power-three','bell','fubini'))
SECTION_DEFINITION_PARENTS=frozenset(('naturals','odd','partition'))


@lru_cache(maxsize=1)
def source_manifest():
    return json.loads((ROOT/MANIFEST).read_text(encoding='utf-8'))


def membership(entry):
    kind=entry['kind'];identifier=entry['id'];result=[]
    if identifier in ARCHIVE_MEMBERSHIP:
        return [ARCHIVE_MEMBERSHIP[identifier]]
    for match,key in [(kind in ('reciprocal','reciprocal power'),'GF-RECIPROCAL'),(kind=='logarithmic companion','GF-TANGENT'),(kind.startswith('congruential ') or kind=='euler','GF-CONGRUENTIAL'),(kind.startswith('Appell '),'GF-APPELL'),(kind=='secancy parameter column','GF-SECANCY'),(kind=='Euler-transfer theta','GF-THETA'),(kind=='theta polynomial column','GF-THETA-COLUMN'),(kind=='classical multisection','GF-SECTIONS'),(kind=='k-step reciprocal power','GF-LINEAR'),(kind=='k-bonacci' or identifier in ('KOM013','KOM014','KOM015','KOM016'),'GF-KBONACCI')]:
        if match:result.append(key)
    if identifier.startswith(('KFOR-TRI-P-','KFOR-TRI-H','KFOR-TRI-A-','KFOR-TRI-B-','KFOR-TRI-BI-')):
        result.append('GF-SECANCY' if identifier.startswith('KFOR-TRI-P-') else 'GF-THETA' if identifier=='KFOR-TRI-H' else 'GF-APPELL')
    if identifier.startswith('KFOR-AC-'):result.append('GF-APPELL')
    if identifier.startswith('KSEQ-') and kind in SECTION_EXPLORER_PARENTS|SECTION_DEFINITION_PARENTS:result.append('GF-SECTIONS')
    if kind=='fibonacci':result.append('GF-KBONACCI')
    if kind=='lucas':result.append('GF-LINEAR')
    return result


@lru_cache(maxsize=1)
def family_definitions():
    basic=[
      ('GF-LINEAR','Weighted k-step reciprocal powers','linear','k>=2; r,c positive integers','A(z)=(1-c sum_(j=1)^k z^j)^(-r)','These are ordinary generating function coefficients. The calculator distinguishes the nonzero tail, the zero prefix, and a specified vector of initial values.','CONNECTIONS','generalized-k-step-coefficients'),
      ('GF-KBONACCI','Generalized k-bonacci initial-value families','kbonacci','k>=2; n>=0','sum_(n>=0) T(n;k)z^n=z^(k-1)/(1-sum_(j=1)^k z^j)','The usual initial values are k−1 zeros followed by one. The calculator also accepts a specified initial vector.','CONNECTIONS','generalized-k-step-coefficients'),
      ('GF-RECIPROCAL','Transfer secants and reciprocal-power towers','reciprocal','N>=2; integer r>=0 or complex order using the germ normalized to 1 at the origin; explorer uses positive integer r','D_N(z)=sum_(m>=0) (-1)^m z^(Nm)/(Nm)!; sum_(n>=0) A(n)z^(Nn)/(Nn)! = D_N(z)^(-r)','The exponential generating function uses source degree Nn. For complex order r, the defining germ is exp(-r log D_N), with log D_N(0)=0. Continuation around zeros depends on the chosen branch. The calculator evaluates positive integer orders.','REGISTRY','Transfer secants'),
      ('GF-CONGRUENTIAL','Congruential Euler inverse sections','congruential','N>=2; 0<=j<N; integer powers or normalized complex-order germs; explorer uses positive integer powers','CE_(N,j)(z)=(sum_(m>=0) j! z^(Nm)/(Nm+j)!)^(-1)','Each rational coefficient is reduced before its numerator or positive denominator is selected. This block denominator has positive terms, unlike the alternating D_N.','REGISTRY','Congruential Euler block functions'),
      ('GF-APPELL','Generalized block-Appell polynomial families','appell','N>=2; 0<=j<N; normalized complex order and complex x; explorer uses integer r and x','sum_(n>=0) P_n(x)z^n/n! = exp(xz) CE_(N,j)(z)^r','The source degree is n. Rational specializations use reduced numerators or positive denominators. Polynomial coefficient tables retain their row and column indices.','REGISTRY','Higher congruential powers and block-Appell polynomials'),
      ('GF-SECANCY','Transfer-secancy parameter polynomials','secancy','N>=2; n>=0; 1<=k<=n','P_(N,n)(r)=(Nn)! [z^(Nn)] D_N(z)^(-r); a(n)=[r^k] P_(N,n)(r)','These are ordinary polynomial coefficients, with no k! factor. Column k begins at n=k.','REGISTRY','Transfer-secancy parameter polynomials'),
      ('GF-THETA','Euler-transfer theta specializations','theta','n>=0; polynomial parameter x, with its normalized generating germ; explorer uses integer x','sum_(n>=0) Theta_(2n)(x) z^(2n)/(2n)! = sech(xz) sech(z)^x','These are signed exponential generating function coefficients of source degree 2n. The stated generating function determines their signs.','REGISTRY','Euler-transfer theta polynomials'),
      ('GF-THETA-COLUMN','Theta polynomial coefficient families','theta-column','k>=1; n>=ceil(k/2)','a(n)=[x^k] Theta_(2n)(x)','The tables retain ordinary coefficients of powers of x, including zeros. No k! factor is applied.','REGISTRY','Euler-transfer theta polynomials'),
      ('GF-TANGENT','Logarithmic-derivative transfer tangents','tangent','N>=2; n>=0','-D_N\'(z)/D_N(z)=sum_(n>=0) T_N(n)z^(N(n+1)-1)/(N(n+1)-1)!','The source degree is N(n+1)-1, which differs from the degree used for secancy parameter columns.','REGISTRY','Transfer tangents and logarithmic-derivative companions'),
      ('GF-SECTIONS','Universal coefficient sections and classical multisections','section','M>=1; 0<=r<M; scalar coefficient germ','F(z)=sum_(r=0)^(M-1) z^r F_(M,r)(z^M); F_(M,r)(u)=sum_(n>=0) a_(Mn+r) u^n','Combining every residue section reconstructs the original series. Each section retains its original index map.','SF-I',171),
    ]
    analytic=[
      ('GF-HYPERGEOMETRIC-PACKETS','Generalized hypergeometric packet systems','SF-I',420,'M>=1; p,q nonnegative integers; source hypergeometric parameters','(theta product_(j=1)^q (theta+b_j-1)-z product_(i=1)^p (theta+a_i))F=0; (Theta_M product_(j=1)^q (Theta_M+(b_j-1)I_M)-C_M product_(i=1)^p (Theta_M+a_i I_M))F_M=0','The scalar differential equation becomes a matrix system in packet coordinates. The definition retains the parameter restrictions and the analytic or formal interpretation given in the source.'),
      ('GF-BERNOULLI-HURWITZ','Complex-order Bernoulli–Hurwitz packets','SF-I',441,'a>0; complex order z; M>=1; 0<=r<M','B(z;a)=-z zeta(1-z,a)','The apparent pole at z=0 is removed before the residue sections are defined. Positive integer orders recover Bernoulli polynomials.'),
      ('GF-LERCH-DETAILS','Cyclotomic Bernoulli–Lerch details','SF-I',562,'Source packet parameters; positive refinement L; 0<=j<L','W_(M,r)^(L,j)(z;a)=-z M^(z-1) Phi(omega_L^(-j),1-z,(a+r)/M)/sqrt(L)','The source specifies the finite Fourier transform, analytic continuation, and zero frequency channel.'),
      ('GF-SQUAREFREE-ENERGY','Squarefree arithmetic moment families','SF-II',655,'a>1/2; beta>0; Dirichlet character chi; k>=0','E_(a,beta,chi)(k)=sum_(n>=1) mu(n)^2 abs(chi(n))^2 (1-n^(-beta))^(2k)/n^(2a)','These positive moments are generally not integers. The source distinguishes positivity from signed coherence.'),
      ('GF-STIELTJES-JACOBI','Squarefree Stieltjes–Jacobi and moment-exact families','SF-III',182,'a>1/2; beta>0; character conductor q','E(k)=sum_(n>=1) w_n x_n^k; x_n=(1-n^(-beta))^2; R(z)=sum_(k>=0) E(k)z^k=sum_(n>=1) w_n/(1-z x_n)','The same positive measure defines the moments, resolvent, Jacobi model, Hankel determinants, and quadrature rules. Each finite model has a stated range of exact moments.'),
      ('GF-GAMMA-DEPHASING','Universal Gamma dephasing family','SF-IV',490,'alpha=(2a-1)/beta>0; real tau; source large-depth regime','G(tau)=Gamma(alpha+i tau/beta)/Gamma(alpha)','This is the normalized limiting dephasing function, not the finite arithmetic kernel.'),
      ('GF-LOG-GAMMA','Log-Gamma packet and Gamma–sech kernels','SF-V',337,'alpha>0; real y,h,eta','g_alpha(y)=Gamma(alpha)^(-1/2) exp(alpha y/2-exp(y)/2)','The source gives exact Fourier, ambiguity, and orthogonal polynomial representations of this normalized packet.'),
      ('GF-CROSS-SHAPE','Cross-shape Gamma–sech ambiguity families','SF-VI',258,'alpha,beta>0; real h,eta','A_(alpha,beta)(h,eta)=exp((alpha-beta)h/4) Gamma((alpha+beta)/2+i eta) sech(h/2)^((alpha+beta)/2+i eta)/sqrt(Gamma(alpha)Gamma(beta))','The source relates the cross shape kernel to shape convolution, refinement, and coherent transforms.'),
      ('GF-SHAPE-TRANSFER','Shape-semigroup polynomial transfer families','SF-VI',182,'Positive shapes alpha and t; n>=0','sigma_n(alpha,t)=sqrt((alpha)_n/(alpha+t)_n)','These are the transfer singular values. The source specifies their rising factorials, normalization, and packet spaces.'),
      ('GF-RACAH','Racah polynomial and packet recoupling families','SF-VII',882,'Source terminating Racah parameters and finite support','R_n(lambda(x))=4F3(-n,n+alpha+beta+1,-x,x+gamma+delta+1; alpha+1,beta+delta+1,gamma+1; 1)','The Racah polynomials and projector recoupling matrices have different normalizations. Their entries should not be identified without the conversion given in the source.'),
      ('GF-Q-RACAH','q-Racah polynomial and recoupling families','SF-VIII',865,'0<q<1; nonnegative integer degree n; nonsingular lower factors in the finite range; source finite-support conditions','R_n(mu(y))=4phi3(q^(-n),alpha beta q^(n+1),q^(-y),gamma delta q^(y+1); alpha q,beta delta q,gamma q; q,q); mu(y)=q^(-y)+gamma delta q^(y+1)','The source gives the terminating 4-phi-3 formula, duality, classical limit, and the Askey–Wilson difference equation.'),
      ('GF-ASKEY-WILSON','Normalized Askey–Wilson transfer functions','SF-VIII',945,'z nonzero; nonnegative integer degree n; source q-domain and nonsingular lower factors','A_n(z)=4phi3(q^(-n),a b c d q^(n-1),a z,a z^(-1); a b,a c,a d; q,q)','This normalization has no additional polynomial prefactor. The defining passage specifies the q difference equation and continuous spectral coordinate.'),
    ]
    sources={s['id']:s for s in source_manifest()['sources']};result=[]
    for identifier,title,engine,domain,formula,note,source,locator in basic:
        result.append(dict(id=identifier,title=title,engine=engine,domain=domain,formula=formula,note=note,paper=source,locator=locator,mode='Exact coefficient explorer'))
    for identifier,title,source,line,domain,formula,note in analytic:
        result.append(dict(id=identifier,title=title,engine=None,domain=domain,formula=formula,note=note,paper=source,locator=line,mode='Source-defined analytic family'))
    result.extend(archive_definitions())
    for item in result:
        source=sources[item['paper']];locator=item['locator']
        if isinstance(locator,str) and item['paper']=='REGISTRY':locator=next(h['line'] for h in source['headings'] if h['title']==locator)
        if isinstance(locator,str):locator=next((h['line'] for h in source['headings'] if h['title'].lower().replace(' ','-')==locator),1)
        if item['id'] in ('GF-LINEAR','GF-KBONACCI','GF-SECANCY'):item['derivation']='https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-families/DERIVATIONS.md'
        refs=[item['paper']]+(['PAPER-IV'] if item['id'] in ('GF-RECIPROCAL','GF-TANGENT','GF-CONGRUENTIAL','GF-APPELL') else [])
        if item['id'] in ('GF-RECIPROCAL','GF-KBONACCI'):refs.append('ARCHIVE')
        item.setdefault('family_type','coefficient family' if item['engine'] else 'analytic family')
        item.update(source=source['url']+'#L'+str(locator),paper_title=source['title'],url='generalized-families/'+item['id']+'.html',kind='generalized family',tags=['generalized',item['mode'],item['paper']],status=item['mode'],offset=0,terms=[],formulas=[dict(title='General construction',kind='family definition',expression=item['formula'],source=source['url']+'#L'+str(locator))],recurrence='',explanation=item['note'],collection='generalized',paper_refs=refs,family_names=[item['title']])
        if item['paper']=='ARCHIVE':
            item['registry_source']=source['url'].rsplit('/',1)[0]+'/candidate_registry.json'
            item['reproduction_source']=source['url'].rsplit('/',1)[0]+'/reproduce.py'
        if item['id']=='GF-BLOCK-LOGARITHMIC':
            item['formulas'].append(dict(title='Transfer-tangent normalization',kind='index and scaling identity',
                expression='L_N(n)=Nn T_N(n-1), n>=1; L_N(0)=0',source=item['source']))
    return result


def catalogue(entries):
    families=deepcopy(family_definitions());by_id={f['id']:f for f in families}
    for family in families:family['record_ids']=[]
    for entry in entries:
        for identifier in membership(entry):by_id[identifier]['record_ids'].append(entry['id'])
    records={entry['id']:entry for entry in entries}
    for family in families:
        members=[records[identifier] for identifier in family['record_ids']]
        # Keep original labels and exact decimal strings, including triangle coordinates.
        selected=sorted(members,key=lambda entry:(entry.get('collection')!='recovered',bool(entry.get('triangle') or entry['id']=='KOM084'),entry['id']))[:3]
        family['examples']=[dict(id=item['id'],title=item['title'],url=item['url'],offset=item['offset'],
            index_symbol=item.get('index_symbol','n'),terms=list(map(str,item['terms'][:8])),status=item['status'],
            triangle=bool(item.get('triangle') or item['id']=='KOM084')) for item in selected]
        family['archive_record_ids']=[item['id'] for item in members if item['id'] in ARCHIVE_MEMBERSHIP]
    from sequence_research_notes import research_connections
    from sequence_atlas_index import connection_graph
    relations=[{k:v for k,v in edge.items() if k!='rows'} for edge in research_connections()['edges']]
    for edge in connection_graph([e for e in entries if e['collection']=='atlas'])['edges']:
        relations.append(dict(key='finite-'+edge['key'],source=edge['source_id'],target=edge['target_id'],kind='finite transform comparison',statement=edge['label']+' agrees at the twelve displayed stored positions. This is a finite comparison, not a proof of an infinite identity.',source_url='https://komorebip.github.io/Operation-KOMOREBI/sequences/'+edge['source_id']+'.html#connections',reversible=False,checked_overlaps=edge['matched_terms']))
    archived=[entry for entry in entries if entry['id'] in ARCHIVE_MEMBERSHIP]
    return dict(schema=1,families=families,sources=source_manifest()['sources'],relations=relations,
        record_coverage=dict(records=len(entries),assigned=sum(bool(membership(entry)) for entry in entries)),
        archive_coverage=dict(records=len(archived),assigned=sum(bool(membership(entry)) for entry in archived)),
        scope='The index covers coefficient families, analytic and discrete constructions, and classical references. Record totals count stored instances, not distinct infinite sequences. Source indexing does not replace independent proof review.')


def links_for(entry):
    ids=membership(entry)
    if not ids:return ''
    families={f['id']:f for f in family_definitions()}
    def params(identifier):
        p=dict(count=24)
        p.update(archive_parameters(entry['id']) or {})
        if 'N' in entry:p['N']=entry['N']
        if 'power' in entry:p['r']=entry['power']
        if 'j' in entry:p['j']=entry['j']
        if 'x' in entry:p['x']=entry['x']
        if 'k' in entry:p['column']=entry['k']
        if 'component' in entry:p['component']=entry['component']
        if entry['kind']=='euler':p.update(N=2,j=0,r=1)
        if identifier in ('GF-CONGRUENTIAL','GF-APPELL'):p.setdefault('j',0)
        if identifier=='GF-APPELL' and entry['kind']=='block-Appell coefficient column':
            p.update(appellMode='column',column=entry['k'],j=0)
        if identifier=='GF-SECTIONS':p.update(parent=entry.get('source_kind',entry['kind']),N=entry.get('N',1),j=entry.get('j',0))
        if identifier in ('GF-LINEAR','GF-KBONACCI'):
            order=entry['recurrence_order'] if 'recurrence_order' in entry else 2 if entry['kind'] in ('fibonacci','lucas') else int(entry['id'][3:])-10
            p.update(k=order,c=entry.get('weight',1))
            if entry['kind']=='lucas':p.update(seedMode='custom',seeds='2, 1',r=1)
        return p
    def link(identifier):
        family=families[identifier];url='../'+family['url']
        supported_parent=identifier!='GF-SECTIONS' or entry.get('source_kind',entry['kind']) in SECTION_EXPLORER_PARENTS
        if family['engine'] and supported_parent and not entry.get('triangle') and entry['id']!='KOM084':
            url+='?'+urlencode({'family':identifier,'parameters':json.dumps(params(identifier),separators=(',',':'))})+'#family-explorer'
        else:url+='#definition'
        return '<a href="'+e(url)+'">'+e(family['title'])+'</a>'
    return '<p>Definition or reference: '+' · '.join(link(identifier) for identifier in ids)+'.</p>'


def sections():
    return '''<section id="generalized"><h2>Generalized families</h2><p>Browse the definitions and their sources. Calculate exact coefficients for supported families, or read the analytic definitions in Special Functions I–VIII.</p><p><a href="sequence-library.html?scope=families#library-search">Search generalized families</a> · <a href="generalized-families/index.html">Complete family index</a></p><details><summary>Open the family explorer</summary><div id="family-explorer"></div><p class="sg-static">The general definitions and source links are readable in the family index without JavaScript.</p></details></section>
<section id="research-graph"><h2>Explore connections</h2><p>Browse recorded relationships, follow directed paths, and compose exact scalar transfer kernels while tracking their index shifts.</p><details><summary>Open the connection graph</summary><div id="connection-explorer"></div></details></section>
<section id="identify"><h2>Identify a sequence</h2><p>Compare transformed terms with scalar library records or the retained OEIS data. Results identify the transformation and matching positions.</p><details><summary>Open sequence identification</summary><div id="sequence-identification"></div></details></section>
<section id="modular-dynamics"><h2>Modular dynamics</h2><p>Examine a k-step recurrence modulo m. A repeated complete state certifies a cycle and its preceding transient. A bounded search may end without a repeat.</p><details><summary>Open modular dynamics</summary><div id="modular-explorer"></div></details></section>
<section id="research-notebooks"><h2>Research notebooks</h2><p>Save family parameters, searches, comparisons, transfers, graph paths, modular experiments, and notes in a named notebook. Export it or share a link.</p><details><summary>Open research notebooks</summary><div id="notebook-explorer"></div></details></section>'''


def build_pages(site,data,wrap):
    site.write('assets/sequence-generalized-data.json',json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    cards=[];families={item['id']:item for item in data['families']}
    from sequence_library import library_entries
    from sequence_atlas import catalogue as atlas_catalogue
    records={item['id']:item for item in library_entries(atlas_catalogue())}
    public_base='https://komorebip.github.io/Operation-KOMOREBI/'
    def csv_text(rows):
        output=io.StringIO(newline='');writer=csv.writer(output);writer.writerows(rows);return output.getvalue()
    index_rows=[['id','title','construction_type','parameter_domain','definition','notes','source_id','source_title','source','indexed_records','url']]
    for family in data['families']:
        stem=family['url'].removesuffix('.html')
        index_rows.append([family['id'],family['title'],family['mode'],family['domain'],family['formula'],family['note'],family['paper'],family['paper_title'],family['source'],len(family['record_ids']),public_base+family['url']])
        export=dict(schema=1,family=family,sources=[source for source in data['sources'] if source['id'] in family['paper_refs']],scope=data['scope'])
        site.write(stem+'.json',json.dumps(export,ensure_ascii=False,indent=2)+'\n')
        rows=[['id','title','collection','kind','first_index','index_symbol','stored_terms','review_status','entry_url']]
        for identifier in family['record_ids']:
            entry=records[identifier]
            rows.append([identifier,entry['title'],entry['collection'],entry['kind'],entry['offset'],entry.get('index_symbol','n'),len(entry['terms']),entry['status'],public_base+entry['url']])
        site.write(stem+'-members.csv',csv_text(rows))
    site.write('assets/sequence-generalized-index.csv',csv_text(index_rows))
    archive_records={item['code']:item for item in json.loads((site.root/'research/sequence-archive/candidate_registry.json').read_text(encoding='utf-8'))}
    related={
        'GF-BLOCK-LOGARITHMIC':['GF-TANGENT','GF-RECIPROCAL'],
        'GF-TANGENT':['GF-BLOCK-LOGARITHMIC','GF-RECIPROCAL'],
        'GF-BLOCK-TRANSFORMS':['GF-RECIPROCAL','GF-CLASSICAL-REFERENCES'],
        'GF-BLOCK-HANKEL':['GF-RECIPROCAL'],
        'GF-BLOCK-VALUATIONS':['GF-RECIPROCAL','GF-PASCAL-VALUATIONS'],
        'GF-DIGIT-RESIDUES':['GF-CYCLIC-SUBSETS','GF-SECTIONS'],
        'GF-CYCLIC-SUBSETS':['GF-DIGIT-RESIDUES','GF-CYCLIC-MASKS'],
        'GF-PASCAL-VALUATIONS':['GF-BLOCK-VALUATIONS'],
        'GF-TOTIENT-PREFIX':['GF-PRIME-POWER-SUPPORT'],
        'GF-PRIME-POWER-SUPPORT':['GF-TOTIENT-PREFIX'],
        'GF-SMITH-POLYNOMIALS':['GF-LINEAR','GF-KBONACCI'],
        'GF-CYCLIC-MASKS':['GF-CYCLIC-SUBSETS'],
    }
    def examples_block(family):
        examples=family.get('examples',[])
        if not examples:return ''
        samples=[]
        for item in examples:
            values=item['terms'];symbol=item['index_symbol'];last=item['offset']+len(values)-1
            note='These are flat triangle positions. Open the record to see row and column coordinates.' if item['triangle'] else 'Original indices and exact integer values.'
            samples.append('<article class="sar-card"><p class="sar-kicker">'+e(item['id'])+'</p><h3><a href="../'+e(item['url'])+'">'+e(item['title'])+'</a></h3><p>'+e(item['status'])+'</p><div class="sl-term-preview"><p class="sl-term-caption">'+e(symbol)+' = '+str(item['offset'])+'–'+str(last)+'</p><div class="sl-term-values" tabindex="0" role="region" aria-label="Exact stored example '+e(item['id'])+'">'+e(', '.join(values))+'</div></div><p>'+note+'</p><p><a href="../'+e(item['url'])+'#definition">Definition, indexing, and complete data</a></p></article>')
        return '<section id="examples"><h2>Representative records</h2><p>Each example retains its original offset, exact values, and review status.</p><div class="sar-grid">'+''.join(samples)+'</div></section>'
    for family in data['families']:
        ids=family['record_ids'];members='<p>'+str(len(ids))+' indexed integer record'+('' if len(ids)==1 else 's')+' in this '+('collection' if family['family_type']=='reference collection' else 'construction')+'.</p>' if ids else ''
        if ids:members+='<p><a href="../sequence-library.html?'+e(urlencode({'q':'family:'+family['id']}))+'#library-search">Search its integer records</a></p>'
        body='<nav aria-label="Family navigation"><a href="../sequence-library.html?scope=families#library-search">Search families</a> · <a href="index.html">Family index</a></nav><header class="sar-header"><p class="sar-kicker">'+e(family['id'])+' / '+e(family['family_type'])+'</p><h1>'+e(family['title'])+'</h1><p>'+e(family['mode'])+'</p></header><section id="definition"><h2>'+('Reference definitions' if family['family_type']=='reference collection' else 'General construction')+'</h2><p class="sar-formula">'+e(family['formula'])+'</p><p><strong>Parameters and domain:</strong> '+e(family['domain'])+'</p><p>'+e(family['note'])+'</p>'
        for formula in family['formulas'][1:]:body+='<h3>'+e(formula['title'])+'</h3><p class="sar-formula">'+e(formula['expression'])+'</p>'
        body+='<p><a href="'+e(family['source'])+'">'+e(family['paper_title'])+' — defining passage</a>.</p>'+members+'</section>'+examples_block(family)
        body+='<section id="downloads"><h2>Download this construction</h2><p><a download href="'+e(family['id'])+'.json">Definition and examples (JSON)</a> · <a download href="'+e(family['id'])+'-members.csv">Member records (CSV)</a> · <a download href="../assets/sequence-generalized-index.csv">All definitions (CSV)</a></p>'+(('<p>The member CSV lists '+str(len(ids))+' integer records with their offsets, review status, and links.</p>') if ids else '<p>No integer records are linked to this analytic family. The member CSV contains only its header. The definition and source references are available in JSON.</p>')+'</section>'
        if family.get('archive_record_ids'):
            archived=family['archive_record_ids']
            body+='<section id="archive-records"><h2>Recovered archive records</h2><p>'+str(len(archived))+' original records mapped to this construction.</p><ul>'+''.join('<li><a href="../sequence-archive/'+identifier+'.html">'+identifier+' · '+e(archive_records[identifier]['name'])+'</a> · first index '+str(archive_records[identifier]['offset'])+'</li>' for identifier in archived)+'</ul></section>'
        if family['engine']:body+='<section id="family-explorer"><h2>Explore parameters and exact values</h2><noscript><p>Enable JavaScript to calculate values and compare constructions. The definitions, examples and source links remain available above.</p></noscript><div id="family-explorer-controls"></div></section>'
        elif family['family_type']=='analytic family':body+='<section id="reading"><h2>Read the analytic construction</h2><p>The linked paper gives the hypotheses, normalization, analytic interpretation, and derived identities.</p><p><a href="'+e(family['source'])+'">Open the defining passage</a> · <a href="index.html#research-coverage">Browse research source coverage</a></p></section>'
        else:body+='<section id="reproduce"><h2>Reproduce the archived values</h2><p>The original Python generator defines each construction and its recorded parameters. Extract the source bundle and run <code>python reproduce.py --output regenerated</code>.</p><p><a download href="../assets/sequence-archive-sources.zip">Download the exact generator and source records</a> · <a href="'+e(family['source'])+'">Read the generator</a> · <a href="'+e(family['registry_source'])+'">Original definitions and classifications</a></p></section>'
        if related.get(family['id']):body+='<section id="related"><h2>Related constructions</h2><ul>'+''.join('<li><a href="'+e(identifier)+'.html#definition">'+e(families[identifier]['title'])+'</a></li>' for identifier in related[family['id']])+'</ul></section>'
        site.page(family['url'],family['title'],wrap(body,'../',family=family['id']))
        site.search.append(dict(title=family['title'],group='Collection',kind='Examples',work_ids=['monographs-special-functions'] if family['paper'].startswith('SF-') or family['paper']=='REGISTRY' else [],url=family['url'],text=family['formula']+' '+family['domain']+' '+family['paper_title']+' '+family['note']))
        cards.append('<li><p class="sar-kicker">'+e(family['id'])+'</p><h2><a href="../'+family['url']+'">'+e(family['title'])+'</a></h2><p>'+e(family['mode'])+(' · '+str(len(ids))+' integer records' if ids else '')+' · '+e(family['paper_title'])+'</p><p>'+e(family['domain'])+'</p></li>')
    coverage=[]
    for source in data['sources']:
        mapped=[f for f in data['families'] if source['id'] in f['paper_refs']];coverage.append('<article class="sar-card"><h3>'+e(source['title'])+'</h3><p>'+str(len(mapped))+' indexed family definitions · '+str(len(source['headings']))+' source headings surveyed.</p><p><a href="'+e(source['url'])+'">Maintained source</a></p><ul>'+''.join('<li><a href="../'+f['url']+'">'+e(f['title'])+'</a></li>' for f in mapped)+'</ul><details><summary>Source contents and revision</summary><p>Some sections have no corresponding integer record or calculator.</p><p>Revision '+e(source['revision'])+'. Source SHA-256 (UTF-8/LF): <code>'+source['normalized_sha256']+'</code>.</p><ul>'+''.join('<li><a href="'+e(source['url'])+'#L'+str(h['line'])+'">'+e(h['title'])+'</a></li>' for h in source['headings'])+'</ul></details></article>')
    count=len(data['families']);engines=sum(bool(family['engine']) for family in data['families']);analytic=sum(family['family_type']=='analytic family' for family in data['families']);discrete=sum(family['family_type']=='discrete construction' for family in data['families']);references=sum(family['family_type']=='reference collection' for family in data['families'])
    body='<nav><a href="../sequence-library.html?scope=families#library-search">Search generalized families</a> · <a href="../sequence-library.html#family-explorer">Parameter explorer</a></nav><h1>Generalized families</h1><p>'+str(count)+' indexed definitions: '+str(engines)+' exact coefficient explorers, '+str(analytic)+' source-defined analytic families, '+str(discrete)+' discrete constructions and '+str(references)+' classical reference collection. All '+str(data['archive_coverage']['assigned'])+' recovered archive records link to a definition or reference collection.</p><p>Each construction links to its definition, examples, and source. Different parameter choices can produce the same sequence. Inclusion in this index does not establish historical novelty.</p><p><a download href="../assets/sequence-generalized-index.csv">All definitions (CSV)</a> · <a download href="../assets/sequence-generalized-data.json">Complete definitions and source bindings JSON</a></p><ol>'+''.join(cards)+'</ol><section id="research-coverage"><h2>Research source coverage</h2><p>'+e(data['scope'])+'</p><p><a download href="../assets/sequence-generalized-data.json">Family definitions and source bindings JSON</a></p><div class="sar-grid">'+''.join(coverage)+'</div></section>'
    site.page('generalized-families/index.html','Generalized families and research coverage',wrap(body,'../'))
