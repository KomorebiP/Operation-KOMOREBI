// Local catalogue search. Numeric matching stays exact; text ranking never changes terms.
export const normalizeText = value => String(value).normalize('NFKD').replace(/\p{M}/gu,'').replace(/\u2212/g,'-').toLowerCase().replace(/\s+/g,' ').trim();
const numeric = value => /^[-+?\d\s,;]+$/.test(value);
const fields = new Set(['id','name','formula','tag','kind','oeis','n','j','r','x','k','order','weight','parent','family','paper','representation','collection','status','terms']);
const aliases = {title:'name',keyword:'tag',topic:'tag',type:'kind',power:'r'};

export function canonicalID(value) {
  const match = /^(a|kseq-?|kom-?)(\d{1,6})$/i.exec(value.trim());
  return match ? (match[1].toLowerCase()==='a'?'A':match[1].toLowerCase().startsWith('kom')?'KOM':'KSEQ-')+match[2].padStart(match[1].toLowerCase().startsWith('kom')?3:6,'0') : value;
}

export function termPattern(value) {
  const tokens = value.replace(/\u2212/g,'-').trim().split(/[\s,;]+/).filter(Boolean);
  if(!tokens.length || tokens.length>1000 || tokens.some(v=>v!=='?'&&!/^[-+]?\d{1,2000}$/.test(v)))
    throw Error('Use comma- or space-separated integers (at most 2,000 digits per term), with ? for one unknown term.');
  if(tokens.every(v=>v==='?')) throw Error('Include at least one known integer in a term pattern.');
  return tokens.map(v=>v==='?'?null:String(BigInt(v)));
}

export function parseQuery(query) {
  if(query.length>20000) throw Error('Keep the search below 20,000 characters.');
  const q=query.replace(/\u2212/g,'-').trim();
  if(!q) return [[]];
  if(numeric(q)) return [[{field:'terms',value:termPattern(q),exclude:false}]];
  const tokens=[];let buffer='',quoted=false;
  for(const c of q){
    if(c==='"'){quoted=!quoted;continue;}
    if(!quoted&&(c==='|'||/\s/.test(c))){if(buffer){tokens.push(buffer);buffer='';}if(c==='|')tokens.push('|');}
    else buffer+=c;
  }
  if(quoted) throw Error('Close the quoted phrase to finish this search.');
  if(buffer)tokens.push(buffer);
  const groups=[[]];
  for(let i=0;i<tokens.length;i++){
    let token=tokens[i];
    if(token==='|'){if(!groups.at(-1).length)throw Error('Put a search on each side of |.');groups.push([]);continue;}
    const exclude=token.startsWith('-')&&!numeric(token);
    if(exclude)token=token.slice(1);
    const colon=token.indexOf(':');
    let field=colon>0?token.slice(0,colon).toLowerCase():'text',value=colon>0?token.slice(colon+1):token;
    field=aliases[field]||field;
    if(field!=='text'&&!fields.has(field))throw Error(`Unknown search field “${field}”. Try name:, formula:, tag:, id:, oeis:, n:, r:, or terms:.`);
    if(!value)throw Error(`Add a value after ${field}:.`);
    if(field==='terms'||field==='text'&&numeric(value)){
      while(i+1<tokens.length&&tokens[i+1]!=='|'&&numeric(tokens[i+1]))value+=' '+tokens[++i];
      groups.at(-1).push({field:'terms',value:termPattern(value),exclude});
    }else groups.at(-1).push({field,value:normalizeText(canonicalID(['n','j','r','x','k','order','weight'].includes(field)&&/^[-+]?\d+$/.test(value)?String(BigInt(value)):value)),exclude});
  }
  if(!groups.at(-1).length)throw Error('Put a search on each side of |.');
  return groups;
}

export function matchTerms(values, pattern, mode='any') {
  const positions=[];
  const limit=mode==='start'?Math.min(1,values.length-pattern.length+1):values.length-pattern.length+1;
  for(let at=0;at<limit;at++)if(pattern.every((v,k)=>v===null||values[at+k]===v))positions.push(at);
  return positions;
}

const indexes=new WeakMap();
function index(entry){
  if(indexes.has(entry))return indexes.get(entry);
  const record={id:entry.id,name:entry.title,formula:entry.formula+' '+entry.recurrence+' '+(entry.formulas||[]).map(f=>f.expression).join(' '),
    tag:entry.tags.join(' '),kind:entry.kind,oeis:[entry.oeis||'',...(entry.matches||[]).map(m=>m.id)].join(' '),
    n:String(entry.N??''),j:String(entry.j??''),r:String(entry.power??''),x:String(entry.x??''),k:String(entry.k??''),order:String(entry.recurrence_order??''),weight:String(entry.weight??''),parent:entry.parent||'',family:[entry.kind,entry.source_kind||'',...(entry.generalized_family_ids||[]),...(entry.family_names||[])].join(' '),paper:[...(entry.paper_refs||[]),...(entry.paper_titles||[]),entry.paper_title||''].join(' | '),representation:(entry.formulas||[]).map(f=>f.kind).join(' '),collection:entry.collection||'',status:entry.status+' '+(entry.status.startsWith('Known')?'reference':'family')};
  record.text=Object.values(record).join(' ')+' '+entry.explanation+' '+(entry.matches||[]).map(m=>m.name).join(' ');
  for(const key of Object.keys(record))record[key]=normalizeText(record[key]);
  indexes.set(entry,record);return record;
}

export function searchEntries(entries, query, options={}) {
  const groups=parseQuery(query), saved=new Set(options.saved||[]),filter=options.filter||'all',topic=normalizeText(options.topic||'');
  const results=[];
  for(const entry of entries){
    if(filter==='reference'&&!entry.status.startsWith('Known')||filter==='family'&&entry.kind!=='reciprocal'||filter==='saved'&&!saved.has(entry.id))continue;
    if(topic&&!entry.tags.some(t=>normalizeText(t)===topic))continue;
    const record=index(entry);let best=null;
    for(const clauses of groups){
      let score=0,termMatch=null,reason='Catalogue entry',ok=true;
      for(const clause of clauses){
        let matched=false,weight=0,detail='';
        if(clause.field==='terms'){
          const positions=matchTerms(entry.terms,clause.value,options.match||'any');matched=positions.length>0;
          if(matched){weight=200+(positions[0]===0?20:0)+clause.value.filter(v=>v!==null).length;detail=`Term pattern at ${entry.index_symbol||'n'} = ${positions[0]+(entry.offset||0)}–${positions[0]+clause.value.length-1+(entry.offset||0)}`;
            if(!clause.exclude)termMatch={start:positions[0],length:clause.value.length,positions,pattern:clause.value};}
        }else{
          const value=clause.value,field=clause.field;
          matched=field==='paper'?new RegExp('(^|[^a-z0-9])'+value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(?=$|[^a-z0-9])').test(record.paper):['n','j','r','x','k','order','weight','parent'].includes(field)?record[field]===value:field==='id'&&value.startsWith('a')?record.oeis.split(' ').includes(value):(record[field]||'').includes(value);
          weight=field==='id'?1000:field==='oeis'?500:field==='name'?80:field==='text'&&record.id===value?1000:field==='text'&&record.oeis.split(' ').includes(value)?500:record.name===value?100:record.name.includes(value)?50:field==='formula'?20:5;
          detail=(field==='text'?(record.name.includes(value)?'Name':'Entry text'):field==='n'?'Spacing N':field==='r'?'Power r':field[0].toUpperCase()+field.slice(1))+' matches “'+value+'”';
        }
        if(clause.exclude?matched:!matched){ok=false;break;}
        if(!clause.exclude){score+=weight;if(weight>=20)reason=detail;}
      }
      if(ok&&(!best||score>best.score))best={entry,score,termMatch,reason:termMatch?`Term pattern at ${entry.index_symbol||'n'} = ${termMatch.start+(entry.offset||0)}–${termMatch.start+termMatch.length-1+(entry.offset||0)}`:reason};
    }
    if(best)results.push(best);
  }
  return results.sort((a,b)=>options.sort==='name'?a.entry.title.localeCompare(b.entry.title,'en')||a.entry.id.localeCompare(b.entry.id):options.sort==='id'?a.entry.id.localeCompare(b.entry.id):b.score-a.score||a.entry.id.localeCompare(b.entry.id));
}

function distance(a,b){let row=Array.from({length:b.length+1},(_,i)=>i);for(let i=1;i<=a.length;i++){const next=[i];for(let j=1;j<=b.length;j++)next[j]=Math.min(next[j-1]+1,row[j]+1,row[j-1]+(a[i-1]===b[j-1]?0:1));row=next;}return row[b.length];}
export function suggestions(entries, query){
  const q=normalizeText(query);if(!/^[a-z]{4,24}$/.test(q))return [];
  const words=new Map();for(const entry of entries)for(const word of (entry.title+' '+entry.tags.join(' ')).split(/[^\p{L}]+/u))if(word.length>=4)words.set(normalizeText(word),word);
  return [...words].map(([key,value])=>({value,distance:distance(q,key)})).filter(x=>x.distance>0&&x.distance<=Math.min(2,Math.floor(q.length/4))).sort((a,b)=>a.distance-b.distance||a.value.localeCompare(b.value)).slice(0,3).map(x=>x.value);
}

export function searchLink(base, query, options={}){
  const url=new URL(base);for(const key of ['q','filter','topic','match','sort'])url.searchParams.delete(key);
  for(const [key,value]of Object.entries({q:query,filter:options.filter,topic:options.topic,match:options.match,sort:options.sort}))if(value&&value!=='all'&&value!=='any'&&value!=='relevance')url.searchParams.set(key,value);
  url.hash='find';return url.href;
}
