// Compile the reading edition's mathematics with the deployed MathJax version.
const fs=require('node:fs'),path=require('node:path');
const root=path.join(__dirname,'..');
const modules=path.join(root,'output/vendor/mnr-mathjax/node_modules/mathjax-full/js/');
const {mathjax}=require(modules+'mathjax.js');
const {TeX}=require(modules+'input/tex.js');
const {SVG}=require(modules+'output/svg.js');
const {liteAdaptor}=require(modules+'adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=require(modules+'handlers/html.js');
const {AllPackages}=require(modules+'input/tex/AllPackages.js');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const tex=new TeX({packages:AllPackages.filter(x=>!['autoload','require','noerrors','noundefined'].includes(x)),maxBuffer:50000});
const doc=mathjax.document('',{InputJax:tex,OutputJax:new SVG({fontCache:'none'})});
const data=JSON.parse(fs.readFileSync(path.join(root,'output/mnr-html-work/rendered.json'),'utf8'));
const expressions=[];
function walk(x){
  if(Array.isArray(x))for(const y of x)walk(y);
  else if(x&&typeof x==='object'){
    if(x.t==='Math')expressions.push(x.c);
    for(const y of Object.values(x))walk(y);
  }
}
walk(data.blocks);
const errors=[],unique=new Map();
for(let i=0;i<expressions.length;i++){
  const [kind,source]=expressions[i],key=kind.t+'|'+source;
  if(unique.has(key))continue;
  unique.set(key,true);
  try{
    tex.reset();
    const node=doc.convert(source,{display:kind.t==='DisplayMath'});
    const markup=adaptor.outerHTML(node);
    if(markup.includes('data-mjx-error')||markup.includes('data-mml-node="merror"')){
      errors.push({index:i,error:/data-mjx-error="([^"]*)"/.exec(markup)?.[1]||'MathJax merror',source});
    }
  }catch(error){errors.push({index:i,error:error.message,source});}
  if(i%2000===0)process.stdout.write(JSON.stringify({checked:i,errors:errors.length})+'\n');
}
const result={version:'3.2.2',expressions:expressions.length,unique:unique.size,errors};
fs.writeFileSync(path.join(root,'output/mnr-html-work/MATHJAX_AUDIT.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({expressions:result.expressions,unique:result.unique,errors:errors.length,examples:errors.slice(0,10)}));
if(errors.length)process.exitCode=1;
