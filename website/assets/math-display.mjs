// Display is a transcription. Stored formulas and exact arithmetic stay unchanged.
export const MATH_DISPLAY_KEY='komorebi.math-display.v1';
export function readMathDisplay(storage){try{return storage.getItem(MATH_DISPLAY_KEY)==='plain'?'plain':'typeset';}catch{return 'typeset';}}
const greek={ell:'\\ell',Gamma:'\\Gamma',Theta:'\\Theta',theta:'\\theta',pi:'\\pi',alpha:'\\alpha',beta:'\\beta',omega:'\\omega',infty:'\\infty',cdots:'\\cdots',dz:'\\mathrm{d}z'};
const functions=new Set(['exp','log','sin','cos','tan','sinh','cosh','tanh','sec','sech','csc','cot','gcd','lcm','min','max','det','tr','Tr','floor','ceil','sqrt','binom','numerator','denominator']);
const words=new Set(['for','if','use','and']);
const escapeText=text=>text.replace(/[{}%&#_$]/g,letter=>'\\'+letter);
const symbol=name=>greek[name]||(name.length===1?name:'\\operatorname{'+name+'}');
function render(n){
  if(n.type==='number'||n.type==='symbol')return n.type==='number'?n.value:symbol(n.value);
  if(n.type==='text')return '\\text{'+n.value+' }';
  if(n.type==='group')return ({'(':'\\left(', '[':'\\left[', '{':'\\left\\{'}[n.open])+n.items.map(render).join(n.separator||', ')+({'(':'\\right)', '[':'\\right]', '{':'\\right\\}'}[n.open]);
  if(n.type==='list')return n.items.map(render).join(n.separator||', ');
  if(n.type==='negative')return '-'+render(n.value);
  if(n.type==='positive')return '+'+render(n.value);
  if(n.type==='postfix')return render(n.base)+n.op;
  if(n.type==='bound')return (n.base.type==='postfix'?'\\left('+render(n.base)+'\\right)':render(n.base))+(n.lower?'_{'+render(n.lower)+'}':'')+(n.upper?'^{'+render(n.upper)+'}':'')+(n.prime?"'".repeat(n.prime):'')+'!'.repeat(n.factorial||0);
  if(n.type==='apply')return render(n.base)+'\\!\\left('+n.items.map(render).join(', ')+'\\right)';
  if(n.type==='binary'){
    if(n.op==='/')return '\\frac{'+render(n.left)+'}{'+render(n.right)+'}';
    return render(n.left)+({'*':'\\,','implicit':'\\,','>=':'\\ge ','<=':'\\le ','!=':'\\ne ','...':'\\cdots','%':'\\bmod '}[n.op]||n.op)+render(n.right);
  }
  if(n.type==='big')return (n.name==='sum'?'\\sum':'\\prod')+(n.lower?'_{'+(n.lower.type==='list'&&n.lower.separator==='; '?'\\substack{'+n.lower.items.map(render).join('\\\\')+'}':render(n.lower))+'}':'')+(n.upper?'^{'+render(n.upper)+'}':'')+'{'+render(n.body)+'}';
  if(n.type==='call'){
    const name=n.name,items=n.groups[0]||[],arg=items.map(render).join(', ');
    if(/^\d+F\d+$/.test(name)){
      if(n.groups.length!==3)throw Error('Hypergeometric arguments');const [p,q]=name.split('F');
      return '{}_{'+p+'}F_{'+q+'}\\!\\left(\\begin{matrix}'+(n.groups[0].map(render).join(', ')||'\\vphantom{1}')+'\\\\'+(n.groups[1].map(render).join(', ')||'\\vphantom{1}')+'\\end{matrix}\\,\\middle|\\,'+n.groups[2].map(render).join(', ')+'\\right)';
    }
    if(n.groups.length!==1)throw Error('Unsupported argument separators');
    if(name==='binom'){if(items.length!==2)throw Error('Binomial arguments');return '\\binom{'+render(items[0])+'}{'+render(items[1])+'}';}
    if(name==='sqrt'){if(items.length!==1)throw Error('Root arguments');return '\\sqrt{'+arg+'}';}
    if(name==='floor'||name==='ceil'){if(items.length!==1)throw Error('Rounding arguments');return '\\left'+(name==='floor'?'\\lfloor':'\\lceil')+arg+'\\right'+(name==='floor'?'\\rfloor':'\\rceil');}
    const fn=['exp','log','sin','cos','tan','sinh','cosh','tanh','gcd','min','max','det'].includes(name)?'\\'+name:symbol(name);
    return fn+'\\!\\left('+arg+'\\right)';
  }
  throw Error('Unsupported notation');
}
export function formulaStatements(source){
  const parts=[];let start=0,depth=0;
  for(let i=0;i<source.length;i++){const c=source[i];if('([{'.includes(c))depth++;else if(')]}'.includes(c))depth--;else if(depth===0&&(c===';'||c==='\n')){const part=source.slice(start,i).trim();if(part)parts.push(part);start=i+1;}}
  const last=source.slice(start).trim();if(last)parts.push(last);return parts;
}
// A bounded parser, rather than replacements that change division or sum scope.
export function formulaLatex(source,onFailure){
  if(typeof source!=='string'||source.length>12000||/\\/.test(source))return null;
  try{
    const section=/^(.*?), where b is (.*?)\. Source formula \(index m\): ([\s\S]*)$/.exec(source);
    if(section){const first=formulaLatex(section[1]),last=formulaLatex(section[3]);if(!first||!last)return null;return '\\begin{gathered}'+first+'\\\\[.4em]\\text{b: '+escapeText(section[2])+'}\\\\[.4em]\\text{Source index m:}\\quad '+last+'\\end{gathered}';}
    const substitution=/^(.*); replace every source index n by (\([^;]+\))$/.exec(source);
    if(substitution){const first=formulaLatex(substitution[1]),index=formulaLatex(substitution[2]);return first&&index?'\\begin{gathered}'+first+'\\\\[.4em]\\text{Replace source index }n\\text{ by }'+index+'\\end{gathered}':null;}
    const statements=formulaStatements(source);if(statements.length>1){const tex=statements.map(item=>formulaLatex(item));return tex.every(Boolean)?'\\begin{gathered}'+tex.join('\\\\[.55em]')+'\\end{gathered}':null;}
    const punctuation=source.trim().endsWith('.')?'.':'';
    const input=(punctuation?source.trim().slice(0,-1):source).replaceAll('−','-').replaceAll('≥','>=').replaceAll('≤','<=').replaceAll('∞','infty').replaceAll('π','pi').replaceAll('Θ','Theta');
    const tokens=[];let at=0;
    while(at<input.length){if(/\s/.test(input[at])){at++;continue;}const m=/^(?:\d+F\d+|\d+(?:\.\d+)?|[A-Za-z]+|\.\.\.|>=|<=|!=|[+\-*/^_!%=(),;:[\]{}<>'])/.exec(input.slice(at));if(!m||tokens.length>4000)return null;tokens.push(m[0]);at+=m[0].length;}
    let pos=0,depth=0;const peek=()=>tokens[pos],take=()=>tokens[pos++],node=(type,extra)=>({type,...extra});
    const relation=()=>{let left=add();while(['=','>=','<=','!=','>','<',':'].includes(peek())){const op=take();left=node('binary',{left,op,right:add()});}return left;};
    const add=()=>{let left=product();while(['+','-'].includes(peek())){const op=take();left=node('binary',{left,op,right:product()});}return left;};
    const starts=t=>t!==undefined&&!words.has(t)&&(/^(?:\d|[A-Za-z])/.test(t)||['(','[','{'].includes(t));
    const product=()=>{let left=unary();while(['*','/','%'].includes(peek())||starts(peek())){const op=starts(peek())?'implicit':take();left=node('binary',{left,op,right:unary()});}return left;};
    const unary=()=>{if(peek()==='+'){take();return node('positive',{value:unary()});}if(peek()==='-'){take();return node('negative',{value:unary()});}return power();};
    const bound=()=>{
      if(peek()==='-'){take();return node('negative',{value:bound()});}
      if(['(','[','{'].includes(peek())){const value=atom();return value.open==='('?(value.items.length===1?value.items[0]:node('list',{items:value.items})):value;}
      const t=take();if(/^\d+(?:\.\d+)?$/.test(t||''))return node('number',{value:t});
      if(functions.has(t)&&peek()==='('){take();return node('call',{name:t,groups:group('(')});}
      if(/^[A-Za-z]$/.test(t||'')||Object.hasOwn(greek,t))return node('symbol',{value:t});throw Error('Group a compound script explicitly');
    };
    const power=()=>{
      let base=atom();
      while(['_','^','!',"'"].includes(peek())||(peek()==='('&&((base.type==='bound'&&base.lower)||(base.type==='postfix'&&base.op==="'")))){
        const op=take();if(op==='('){const groups=group('(');if(groups.length!==1)throw Error('Function arguments');base=node('apply',{base,items:groups[0]});continue;}
        if(op==='!'&&base.type==='bound'&&base.upper)throw Error('Group a factorial exponent explicitly');
        if(op==='!'||op==="'"){base=node('postfix',{base,op});continue;}
        const result=base.type==='bound'?{...base}:node('bound',{base});
        if(op==='_'){if(result.lower||result.upper)throw Error('Ambiguous script order');result.lower=bound();}
        else {if(result.upper)throw Error('Repeated exponent');result.upper=bound();}
        base=result;
      }
      return base;
    };
    function group(open){
      if(++depth>48)throw Error('Nesting');const close={'(':')','[':']','{':'}'}[open],groups=[[]];
      while(peek()!==close){if(peek()===undefined)throw Error('Unclosed group');if(peek()===';'){take();groups.push([]);continue;}if(peek()===','){take();continue;}groups.at(-1).push(statement());if(![close,',',';'].includes(peek()))throw Error('Group separator');}
      take();depth--;return groups;
    }
    function atom(){
      const t=take();if(t===undefined)throw Error('Missing value');
      if(['(','[','{'].includes(t)){const groups=group(t);return node('group',{open:t,items:groups.length>1?[node('list',{items:groups.map(items=>node('list',{items})),separator:'; '})]:groups[0]});}
      if(/^\d+(?:\.\d+)?$/.test(t))return node('number',{value:t});
      if(t==='...')return node('symbol',{value:'cdots'});
      if(!/^[A-Za-z]+$|^\d+F\d+$/.test(t))throw Error('Literal notation');
      if(t==='sum'||t==='product'||t==='prod'){
        let lower,upper;while(['_','^'].includes(peek())){if(take()==='_')lower=bound();else upper=bound();}
        return node('big',{name:t==='sum'?'sum':'prod',lower,upper,body:product()});
      }
      if(peek()==='('){take();return node('call',{name:t,groups:group('(')});}
      if(['Nq','Nn','Nk','Nm','xz','nz'].includes(t))return node('list',{items:[...t].map(value=>node('symbol',{value})),separator:'\\,'});
      if(t.length>1&&!Object.hasOwn(greek,t)&&!functions.has(t)&&t!=='cdots')throw Error('Literal word');
      return node('symbol',{value:t});
    }
    function statement(){if(words.has(peek()))return node('list',{items:[node('text',{value:take()}),relation()],separator:' '});let result=relation();while(words.has(peek())){const word=take();result=node('list',{items:[result,node('text',{value:word}),relation()],separator:'\\quad '});}return result;}
    const rows=[];while(pos<tokens.length){rows.push(statement());if([';',','].includes(peek()))take();else if(pos<tokens.length)throw Error('Statement separator');}
    if(!rows.length)return null;
    const result=rows.map(render);return (result.length===1?result[0]:'\\begin{gathered}'+result.join('\\\\[.45em]')+'\\end{gathered}');
  }catch(error){onFailure?.(error.message);return null;}
}

let controller;
export function enhanceMath(root){return controller?.enhance(root);}
export function clearMath(root){window.MathJax?.typesetClear?.([root]);}
if(typeof document!=='undefined'&&!window.KomorebiMath){
  // Create the shared control once, without repeating it in every chapter shell.
  if(!document.getElementById('site-math-display')){
    const preference=document.createElement('div');preference.className='site-preferences';preference.innerHTML="<label class=\"math-display-control\" hidden for=\"site-math-display\">Math display<select id=\"site-math-display\" aria-describedby=\"site-math-help\"><option value=\"typeset\">Typeset math</option><option value=\"plain\">Plain text</option></select></label><span id=\"site-math-help\" class=\"math-display-status\">Choose typeset formulas or their original plain text. This choice is shared across the site.</span><span id=\"site-math-status\" class=\"math-display-status\" role=\"status\" aria-live=\"polite\"></span>";
    const footer=document.querySelector('body > footer');if(footer)footer.append(preference);else document.body.append(preference);
  }
  const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value)};
  let mode=readMathDisplay(storage),scheduled=false,queue=Promise.resolve();
  const originals=new WeakMap(),pairs=new Set(),hosts=new Set(),seen=new WeakSet(),seenText=new WeakMap(),plainRecords=new WeakMap();
  document.documentElement.dataset.mathDisplay=mode;
  const select=document.getElementById('site-math-display'),status=document.getElementById('site-math-status');
  const announce=text=>{if(status)status.textContent=text;};
  const content=source=>source.trim().replace(/^\\\[([\s\S]*)\\\]$/, '$1').replace(/^\\\(([\s\S]*)\\\)$/, '$1').trim();
  function capture(host){
    if(originals.has(host))return;
    const items=window.MathJax?.startup?.document?.getMathItemsWithin?.([host])||[];
    const source=items.length?items.map(item=>item.math).join('\n'):content(host.textContent);
    if(source)originals.set(host,source);hosts.add(host);
  }
  function show(){
    document.documentElement.dataset.mathDisplay=mode;if(select)select.value=mode;
    for(const host of hosts){
      if(!host.isConnected){hosts.delete(host);continue;}
      if(host.closest('.math-pair'))continue;
      const typed=host.querySelector('mjx-container');let plain=host.querySelector(':scope > .math-plain-source');
      if(typed&&!plain&&originals.has(host)){plain=document.createElement('code');plain.className='math-plain-source';plain.textContent=originals.get(host);host.append(plain);}
      if(plain)plain.hidden=mode!=='plain';
    }
    for(const pair of pairs){
      if(!pair.isConnected){pairs.delete(pair);continue;}
      const plain=pair.querySelector('[data-math-plain]'),math=pair.querySelector('[data-math-tex]'),ready=math?.querySelector('mjx-container')&&!math.querySelector('[data-mml-node="merror"],mjx-merror');
      const typed=mode==='typeset'&&ready;plain.hidden=Boolean(typed);math.hidden=!typed;pair.dataset.mathPairReady=ready?'true':'false';
      const legacy=pair.closest('[data-entry-id]');if(legacy)legacy.dataset.mathReady=ready?'true':'fallback';
    }
  }
  function mathNode(plain,tex){
    const math=document.createElement('div');math.className='arithmatex math-typeset';math.dataset.mathTex='true';math.hidden=true;math.tabIndex=0;math.setAttribute('role','region');math.setAttribute('aria-label',(plain.getAttribute('aria-label')||'Formula')+' · typeset; scroll horizontally if needed');if(tex)math.textContent='\\['+tex+'\\]';return math;
  }
  function pair(plain,tex){
    if(!tex)return;const wrapper=document.createElement('div');wrapper.className='math-pair';
    plain.before(wrapper);wrapper.append(plain);plain.dataset.mathPlain='true';
    plain.removeAttribute('data-math-notation');const math=mathNode(plain,tex);wrapper.append(math);pairs.add(wrapper);plainRecords.set(plain,{source:plain.textContent,wrapper,math});capture(math);return math;
  }
  function enhance(root=document){
    const pending=[];
    for(const plain of root.querySelectorAll('.sar-formula,.sa-formula,.sl-formula pre')){
      const record=plainRecords.get(plain),source=plain.textContent;
      if(record){
        if(record.source!==source){
          window.MathJax?.typesetClear?.([record.math]);record.math.remove();
          const tex=formulaLatex(source),math=mathNode(plain,tex);plain.dataset.mathNotation=tex?'':'source';record.wrapper.append(math);record.source=source;record.math=math;capture(math);if(tex)pending.push(math);
        }
        continue;
      }
      if(seenText.get(plain)===source||plain.closest('.math-pair,.sa-plain-formula')||plain.matches('[data-math-plain]'))continue;seenText.set(plain,source);
      if(plain.closest('#sl-oeis-results'))continue;
      const math=pair(plain,formulaLatex(plain.textContent));if(math)pending.push(math);else plain.dataset.mathNotation='source';
    }
    for(const legacy of root.querySelectorAll('.sa-typeset')){
      if(seen.has(legacy))continue;seen.add(legacy);const plain=legacy.nextElementSibling;
      if(!plain?.matches('.sa-plain-formula'))continue;
      const wrapper=document.createElement('div');wrapper.className='math-pair';legacy.before(wrapper);wrapper.append(legacy,plain);legacy.dataset.mathTex='true';plain.dataset.mathPlain='true';plain.open=true;pairs.add(wrapper);capture(legacy);pending.push(legacy);
    }
    for(const host of root.querySelectorAll('.arithmatex'))capture(host);
    show();
    if(pending.length){queue=queue.then(async()=>{await domReady;await window.MathJax?.startup?.promise;if(!window.MathJax?.typesetPromise)return;
      const live=pending.filter(node=>node.isConnected&&!node.querySelector('mjx-container'));
      if(live.length){const task=window.MathJax.startup.promise.then(()=>window.MathJax.typesetPromise(live));window.MathJax.startup.promise=task.catch(()=>{});await task;const removed=live.filter(node=>!node.isConnected);if(removed.length)window.MathJax.typesetClear(removed);}show();
    }).catch(()=>{show();announce('Typesetting is unavailable for this view. The original formula text remains available.');});}
    return queue;
  }
  function setMode(next,remember=true){
    mode=next==='plain'?'plain':'typeset';show();
    if(remember)try{storage.setItem(MATH_DISPLAY_KEY,mode);announce(mode==='plain'?'Plain text selected for the site.':'Typeset math selected for the site.');}catch{announce('Math display changed for this page. Browser storage is unavailable.');}
    dispatchEvent(new CustomEvent('math-display-change',{detail:{mode}}));
  }
  const domReady=document.readyState==='complete'?Promise.resolve():new Promise(resolve=>document.addEventListener('DOMContentLoaded',resolve,{once:true}));
  controller={enhance,clear:clearMath,get mode(){return mode;},setMode,get ready(){return queue;}};window.KomorebiMath=controller;
  if(select){select.value=mode;select.addEventListener('change',()=>setMode(select.value));select.closest('.math-display-control').hidden=false;}
  addEventListener('storage',event=>{if(event.key===MATH_DISPLAY_KEY||event.key===null)setMode(readMathDisplay(storage),false);});
  enhance();
  const changed=new Set(),selector='.sar-formula,.sa-formula,.sl-formula pre,.sa-typeset,.arithmatex';
  const observer=new MutationObserver(records=>{
    let relevant=false;
    for(const record of records){
      const target=record.target.nodeType===1?record.target:record.target.parentElement;
      if(target?.matches('.sar-formula,.sa-formula,.sl-formula pre')){changed.add(target.parentElement);relevant=true;}
      else if(target?.closest('.arithmatex'))relevant=true;
      for(const node of record.addedNodes||[])if(node.nodeType===1&&!node.matches('.math-plain-source')&&(node.matches(selector)||node.querySelector(selector))){changed.add(node.parentElement||node);relevant=true;}
    }
    if(!relevant||scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;for(const root of changed)if(root?.isConnected)enhance(root);changed.clear();show();});
  });
  observer.observe(document.body,{subtree:true,childList:true,characterData:true});
  domReady.then(async()=>{await window.MathJax?.startup?.promise;show();document.documentElement.dataset.mathDisplayReady='true';}).catch(()=>show());
  const revealHash=()=>{if(mode!=='plain')return;let target;try{target=document.getElementById(decodeURIComponent(location.hash.slice(1)));}catch{return;}target?.closest('.arithmatex')?.scrollIntoView({block:'center'});};
  addEventListener('hashchange',revealHash);domReady.then(()=>queue).then(revealHash);
}
else if(typeof window!=='undefined')controller=window.KomorebiMath;
