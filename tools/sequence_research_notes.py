"""Typed research connections and finite-window facts; original records stay intact."""
from functools import lru_cache
from html import escape as e
from math import gcd
from urllib.parse import urlencode

BASE='https://komorebip.github.io/Operation-KOMOREBI/'
IDENTITIES='https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/research/sequence-connections/IDENTITIES.md'
EULER=BASE+'collection/demonstrations/EULER_PACKETS.html#transfer-the-euler-sequence-to-fibonacci-values'


@lru_cache(maxsize=1)
def research_connections():
    from sequence_atlas import catalogue
    from sequence_library import library_entries
    entries=library_entries(catalogue());lookup={item['id']:item for item in entries};edges=[]
    def add(source,target,kind,statement,source_url,rows=(),reversible=False):
        if source not in lookup or target not in lookup:raise ValueError('A research connection has a missing endpoint')
        edges.append(dict(key=source+'-'+kind.replace(' ','-')+'-'+target,source=source,target=target,kind=kind,statement=statement,source_url=source_url,reversible=reversible,checked_overlaps=len(rows),rows=list(rows)))
    for target in entries:
        parent=lookup.get(target.get('parent'))
        if parent and target['kind']=='classical multisection':
            rows=[]
            for i,value in enumerate(target['terms']):
                n=target['offset']+i;m=target['N']*n+target['j'];pos=m-parent['offset']
                if 0<=pos<len(parent['terms']):
                    assert value==parent['terms'][pos];rows.append(dict(source_index=m,target_index=n,value=value))
            add(parent['id'],target['id'],'subsequence',f'b(n)=a({target["N"]}n+{target["j"]}). Sampling generally loses the other residue classes.',target['formulas'][0]['source'],rows)
        if target['id'].startswith('KFOR-LR-') and target['power']==target['weight']==1:
            k=target['recurrence_order'];source='KSEQ-000025' if k==2 else f'KOM{k+10:03d}' if k<=6 else f'KFOR-KB-{k:02d}'
            original=lookup[source];rows=[]
            for n,value in enumerate(target['terms']):
                m=n+k-1
                if m<len(original['terms']):assert value==original['terms'][m];rows.append(dict(source_index=m,target_index=n,value=value))
            add(source,target['id'],'seed shift',f'b(n)=T(n+{k-1};{k}). The omitted initial {k-1} values are recorded zeros.',IDENTITIES+'#generalized-k-step-coefficients',rows,True)
        table=None;column=None;row_map=lambda n:n
        if target['id'].startswith('KFOR-P-'):table=lookup.get(f'KFOR-TRI-P-{target["N"]:02d}');column=target['k']
        elif target['id'].startswith('KFOR-HC-'):table=lookup['KFOR-TRI-H'];column=target['k']
        elif target['id'].startswith('KFOR-AC-'):
            table=lookup[f'KFOR-TRI-A-{target["N"]:02d}-{target["power"]:02d}'];column=target['k'];row_map=lambda n:target['N']*n+column
        if table:
            rows=[];meta=table['triangle']
            for i,value in enumerate(target['terms']):
                n=target['offset']+i;row=row_map(n)
                if row<len(meta['row_lengths']) and column<meta['row_lengths'][row]:
                    j=meta['row_offsets'][row]+column;assert table['terms'][j]==value;rows.append(dict(source_row=row,source_column=column,source_flat=j,target_index=n,value=value))
            mapping=f'{target["N"]}n+{column}' if target['id'].startswith('KFOR-AC-') else 'n'
            add(table['id'],target['id'],'coefficient extraction',f'b(n) is ordinary coefficient k={column} of source row {mapping}. No k! scaling is applied. Extraction does not recover the other columns.',table['source'],rows)
        if target['id'].startswith('KFOR-H-'):
            table=lookup['KFOR-TRI-H'];rows=[];meta=table['triangle'];x=target['x']
            for n in range(min(len(target['terms']),len(meta['row_lengths']))):
                start=meta['row_offsets'][n];value=str(sum(int(table['terms'][start+k])*x**k for k in range(meta['row_lengths'][n])));assert value==target['terms'][n];rows.append(dict(source_row=n,target_index=n,parameter=x,value=value))
            add(table['id'],target['id'],'polynomial evaluation',f'b(n)=Theta_(2n)({x}). Evaluating at one parameter does not retain every polynomial coefficient.',table['source'],rows)
    for N in range(2,13):add(f'KFOR-TRI-B-{N:02d}',f'KFOR-TRI-BI-{N:02d}','inverse matrices','The lower-triangular matrices are inverses under matrix multiplication. This is not ordinary convolution of their flattened records.',IDENTITIES.rsplit('/research/',1)[0]+'/docs/SEQUENCE_LIBRARY.md',reversible=True)
    source=next(item for item in entries if item['collection']=='atlas' and item['kind']=='euler');target=next(item for item in entries if item['collection']=='atlas' and item['kind']=='fibonacci')
    add(source['id'],target['id'],'ordinary convolution','H(z)A(z)=sum F(n+1)z^n, H=1/((1-z-z^2)A). The Fibonacci shift and transported shift boundary are part of the construction.',EULER,reversible=True)
    return dict(schema=1,scope='Definition relations and source-derived formal identities, with exact checks of available overlaps. Sampling/extraction/evaluation need not be invertible. Generic finite transfers are calculated separately.',edges=edges,urls={item['id']:item['url'] for item in entries})


def entry_details(entry):
    from sequence_generalized import links_for
    values=list(map(int,entry['terms']));start=entry['offset'];first=next((start+i for i,value in enumerate(values) if value),None);g=0
    for value in values:g=gcd(g,value)
    normalization='Stored integers at their stated indices; consult the defining formula for its generating-function normalization.'
    if entry.get('triangle') or entry['id']=='KOM084':normalization='Ordinary polynomial coefficients. Flat j, row n and column k are different coordinates; zeros are retained.'
    elif entry.get('linear_addition'):normalization='Ordinary coefficients, without factorial scaling. The initial conditions distinguish zero-seeded k-bonacci from its nonzero tail.'
    elif entry['kind'] in ('reciprocal','euler','reciprocal power','logarithmic companion'):normalization='These values use the displayed compressed EGF degree and factorial normalization. They are not unscaled Taylor coefficients.'
    elif entry.get('component'):normalization='The stored integers are the '+entry['component']+' of reduced rational coefficients; the denominator is positive. The rational coefficient remains separate.'
    elif entry.get('parent'):normalization='A source subsequence. Its original index map is part of the definition; the local n is not the original source index.'
    facts=[('Stored indices',str(start)+' to '+str(start+len(values)-1)),('First stored nonzero',str(first) if first is not None else 'None in this window'),('Signs in this window',f'{sum(v>0 for v in values)} positive, {sum(v<0 for v in values)} negative, {sum(v==0 for v in values)} zero'),('GCD of stored values',str(g)),('Maximum digit count',str(max(len(str(abs(v))) for v in values))+' decimal digits')]
    pairs=research_connections();related=[edge for edge in pairs['edges'] if entry['id'] in (edge['source'],edge['target'])];neighbors=sorted({edge['target'] if entry['id']==edge['source'] else edge['source'] for edge in related})
    cards=[]
    for edge in related[:12]:
        other=edge['target'] if entry['id']==edge['source'] else edge['source'];direction='To ' if entry['id']==edge['source'] else 'From '
        cards.append('<li><a href="../'+e(pairs['urls'][other])+'">'+direction+e(other)+'</a> · '+e(edge['kind'])+'<p>'+e(edge['statement'])+'</p><p><a href="'+e(edge['source_url'])+'">Definition and derivation</a>'+(' · '+str(edge['checked_overlaps'])+' stored overlaps checked' if edge['checked_overlaps'] else '')+'</p></li>')
    connection='<details><summary>Research connections ('+str(len(related))+')</summary>'+('<ol>'+''.join(cards)+'</ol>' if cards else '<p>A finite ordinary convolution transfer to another scalar record can be constructed in the transfer tool.</p>')
    if len(related)>12:connection+='<p><a href="../sequence-library.html?'+e(urlencode({'q':' | '.join('id:'+identifier for identifier in neighbors)}))+'#library-search">Browse all connected records</a></p>'
    connection+='<p>Each connection retains its map type and direction. Reversibility is stated only where supported.</p></details>'
    tools=''
    if not entry.get('triangle') and entry['id']!='KOM084':tools='<p><a href="../sequence-library.html?'+e(urlencode({'tr-source':entry['id']}))+'#transfers">Build a transfer from this sequence</a></p>'
    citation='Komorebi Sequence Library. '+entry['id']+': '+entry['title']+'. '+BASE+(entry.get('url') or ('sequences/' if entry['id'].startswith('KSEQ') else 'sequence-archive/' if entry['id'].startswith('KOM') else 'sequence-families/')+entry['id']+'.html')
    return '<section id="sequence-details"><h2>Sequence details and connections</h2><p>'+e(normalization)+'</p><dl class="sar-facts">'+''.join('<div><dt>'+e(label)+'</dt><dd>'+e(value)+'</dd></div>' for label,value in facts)+'</dl><p>These sign, support, and GCD observations describe the stored window.</p>'+links_for(entry)+connection+tools+'<details><summary>Cite this record</summary><p class="sr-citation">'+e(citation)+'</p><button type="button" data-copy-citation hidden>Copy citation</button><label for="sr-citation-copy" hidden>Copy this citation<textarea id="sr-citation-copy" readonly></textarea></label><p role="status"></p></details></section>'
