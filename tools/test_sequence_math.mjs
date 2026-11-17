import test from 'node:test';
import assert from 'node:assert/strict';
import {formulaLatex,readMathDisplay} from '../website/assets/math-display.mjs';
import {atlasDestination,archiveDestination} from '../website/assets/sequence-navigation.mjs';
import {sequenceTransfer} from '../website/assets/sequence-transfer-core.mjs';
import {rationalTeX,transferPolynomialPlain,transferPolynomialTeX,transferWitnessPlain,transferWitnessTeX,triangleRowExpressions} from '../website/assets/sequence-math.mjs';

test('formula transcription preserves denominator function arguments and sum scope',()=>{
  const quotient=formulaLatex("a(n)=-D_2'(z)/D_2(z)");
  assert.match(quotient,/\\frac\{[^}]*D_\{2\}'/);
  assert.ok(quotient.endsWith('{D_{2}\\!\\left(z\\right)}'));
  assert.match(formulaLatex('a(n)=sum_(k=1)^n 1/k'),/\\sum_\{k=1\}\^\{n\}\{\\frac\{1\}\{k\}\}/);
  assert.ok(formulaLatex('a(n)=n!!').endsWith('n!!'));
  assert.ok(formulaLatex('a(n)=+n').endsWith('+n'));
});
test('hypergeometric parameters, polynomial columns, and substitutions retain their roles',()=>{
  const hyper=formulaLatex('0F1(;1/2;z^2/4)');
  assert.match(hyper,/\{\}_\{0\}F_\{1\}/);assert.match(hyper,/\\frac\{1\}\{2\}/);assert.match(hyper,/\\frac\{z\^\{2\}\}\{4\}/);
  assert.match(formulaLatex('a(n)=[r^2 z^(3n)] D_3(z)^(-r)'),/\\left\[r\^\{2\}/);
  assert.match(formulaLatex('a(n)=4^n (1/2)_n/(2)_n'),/\\frac/);
  assert.match(formulaLatex('F(n)=2^n; replace every source index n by (3n+1)'),/Replace source index/);
});
test('unsupported or ambiguous notation retains its literal source instead of guessing',()=>{
  for(const input of ['x^2^3','x_n_n','2^v_2(n)','sqrt(a;b)','x^)',String.raw`\href{https://example.test}{x}`,'a(n)=the number of words','('.repeat(60)+'1'+')'.repeat(60)])assert.equal(formulaLatex(input),null,input);
  assert.equal(formulaLatex('x'.repeat(12001)),null);
});
test('one math preference has robust defaults without requiring browser storage',()=>{
  assert.equal(readMathDisplay({getItem:()=>null}),'typeset');assert.equal(readMathDisplay({getItem:()=> 'plain'}),'plain');assert.equal(readMathDisplay({getItem:()=> 'invalid'}),'typeset');assert.equal(readMathDisplay({getItem:()=>{throw Error('Denied');}}),'typeset');
});
test('old atlas search links open the complete library while plot links keep their state',()=>{
  const search=new URL(atlasDestination('https://example.test/site/sequences.html?q=id%3AKOM085#find'));assert.equal(search.pathname,'/site/sequence-library.html');assert.equal(search.searchParams.get('q'),'id:KOM085');assert.equal(search.hash,'#library-search');
  const plot=new URL(atlasDestination('https://example.test/site/sequences.html?seq=KSEQ-000025&view=mod&modulus=11#explorer'));assert.equal(plot.pathname,'/site/sequence-explorer.html');assert.equal(plot.searchParams.get('modulus'),'11');assert.equal(plot.searchParams.get('seq'),'KSEQ-000025');
  const archive=new URL(archiveDestination('https://example.test/site/sequence-archive.html',{query:'1, ?, 251',family:'Euler/block',review:'Known family',sort:'name',match:'start'}));assert.equal(archive.pathname,'/site/sequence-library.html');assert.equal(archive.searchParams.get('collection'),'recovered');assert.equal(archive.searchParams.get('q'),'1, ?, 251');assert.equal(archive.searchParams.get('status'),'Known family');assert.equal(archive.searchParams.get('match'),'start');
});

test('factorials keep their order relative to powers; definitions and constraints have separate rows',()=>{
  assert.equal(formulaLatex('n!^2'),String.raw`\left(n!\right)^{2}`);
  assert.equal(formulaLatex('n^2!'),null);
  assert.ok(formulaLatex('a(n)=n!\nb(n)=n+1').includes(String.raw`\\[.55em]`));
  assert.ok(formulaLatex('sum_(q_1+q_2=n; q_i>=1) 1/q_i!').includes(String.raw`\substack`));
  const hyper=formulaLatex('0F1(;1/2;z)');assert.ok(!hyper.includes(';'));assert.ok(hyper.includes(String.raw`\vphantom{1}`));assert.ok(hyper.includes(String.raw`\middle|`));
});

test('factorial normalization followed by equality cannot turn into an inequality',()=>{
  const reciprocal=formulaLatex('sum_(n>=0) A(n)z^(Nn)/(Nn)! = D_N(z)^(-r)');
  const theta=formulaLatex('sum_(n>=0) Theta_(2n)(x) z^(2n)/(2n)! = sech(xz) sech(z)^x');
  const appell=formulaLatex('sum_(n>=0) P_n(x)z^n/n! = exp(xz) CE_(N,j)(z)^r');
  for(const tex of [reciprocal,theta,appell]){assert.ok(tex);assert.ok(tex.includes('!}}='));assert.ok(!tex.includes(String.raw`\ne `));}
  assert.ok(reciprocal.includes(String.raw`{\left(N\,n\right)!}`));
  assert.ok(theta.includes(String.raw`{\left(2\,n\right)!}`));
  assert.ok(appell.includes(String.raw`{n!}`));
  assert.equal(formulaLatex('n!=0'),String.raw`n\ne 0`);
  assert.equal(formulaLatex('n! = m'),String.raw`n!=m`);
});

test('family function parameters and residue indices preserve their separators and coordinates',()=>{
  assert.equal(formulaLatex('f(a;b)'),String.raw`f\!\left(a\,;\,b\right)`);
  assert.equal(formulaLatex('W_(M,r)^(L,j)(z;a)'),String.raw`W_{M, r}^{L, j}\!\left(z\,;\,a\right)`);
  assert.ok(formulaLatex('B(z;a)=-z zeta(1-z,a)').includes(String.raw`B\!\left(z\,;\,a\right)`));
  const packet=formulaLatex('F_(M,r)(u)=sum_(n>=0) a_(Mn+r) u^n');
  assert.ok(packet.includes(String.raw`a_{M\,n+r}`));
  assert.ok(formulaLatex('CE_(N,j)(z)').includes(String.raw`\operatorname{CE}_{N, j}`));
  assert.equal(formulaLatex('abs(chi(n))^2'),String.raw`\left|\chi\!\left(n\right)\right|^{2}`);
});

test('Racah and q-Racah families retain lower-case gamma and terminating parameters',()=>{
  const racah=formulaLatex('R_n(lambda(x))=4F3(-n,n+alpha+beta+1,-x,x+gamma+delta+1; alpha+1,beta+delta+1,gamma+1; 1)');
  assert.ok(racah.includes(String.raw`{}_{4}F_{3}`));
  assert.ok(racah.includes(String.raw`x+\gamma+\delta+1`));
  assert.ok(racah.includes(String.raw`\gamma+1\end{matrix}`));
  const basic=formulaLatex('R_n(mu(y))=4phi3(q^(-n),alpha beta q^(n+1),q^(-y),gamma delta q^(y+1); alpha q,beta delta q,gamma q; q,q); mu(y)=q^(-y)+gamma delta q^(y+1)');
  assert.ok(basic.includes(String.raw`{}_{4}\phi_{3}`));
  assert.ok(basic.includes(String.raw`\gamma\,\delta\,q^{y+1}`));
  assert.ok(basic.includes(String.raw`\mu\!\left(y\right)`));
  assert.ok(!basic.includes(String.raw`\Gamma`));
});

test('archive constructions preserve finite set counts, divisibility conditions and residue exponents',()=>{
  const prefix=formulaLatex('D(n)=#{phi(k):1<=k<=n}');
  assert.ok(prefix.includes(String.raw`\#\left\{\phi\!\left(k\right):1\le k\le n\right\}`));
  assert.equal(formulaLatex('#phi(n)'),null);
  assert.equal(formulaLatex('p|n'),String.raw`p\mid n`);
  assert.equal(formulaLatex('|n|'),null);
  const masks=formulaLatex('C_K(n)=sum_(h|n, h<=K) n/h');
  assert.ok(masks.includes(String.raw`\sum_{h\mid n, h\le K}{\frac{n}{h}}`));
  const digits=formulaLatex('C_(b,m,r)(n)=sum_(j>=0) [x^(mj+r)] (1+x+...+x^(b-1))^n');
  assert.ok(digits.includes(String.raw`x^{m\,j+r}`));
  assert.ok(digits.includes(String.raw`\cdots`));
  const counts=formulaLatex('C_(p,j)(n)=sum_(k=0)^n [v_p(binom(n,k))=j]');
  assert.ok(counts.includes(String.raw`\left[v_{p}`));
  assert.ok(counts.includes(String.raw`\binom{n}{k}`));
  assert.ok(counts.includes(String.raw`=j\right]`));
});

test('triangle row windows and polynomials retain sparse zeros, signs and variable row lengths',async()=>{
 const {triangleLayout,triangleWindow,trianglePolynomial}=await import('../website/assets/sequence-archive-core.mjs');
 const entry={id:'KFOR-TRI-H',offset:0,terms:['1','0','-1','-1','0','2','3','6','5'],triangle:{row_lengths:[1,3,5],variable:'x'}};
 assert.deepEqual(triangleLayout(entry).map(row=>[row.start,row.size]),[[0,1],[1,3],[4,5]]);
 assert.equal(trianglePolynomial(entry,1),'p(x)=-x - x^2');assert.equal(trianglePolynomial(entry,2),'p(x)=2x + 3x^2 + 6x^3 + 5x^4');
 assert.deepEqual(triangleWindow(entry,2),{start:4,size:5,view:'raw',scale:'linear',marks:'line',color:'single'});assert.throws(()=>triangleWindow(entry,3));
});

test('mixed source definitions separate prose from complete equations without splitting parameters',async()=>{
 const {readableFormulaParts}=await import('../website/assets/math-display.mjs');
 assert.deepEqual(readableFormulaParts('The row is indexed by n. P_0=1; P_(n+1)=(1+s)P_n.'),['The row is indexed by n.','P_0=1','P_(n+1)=(1+s)P_n.']);
 assert.equal(readableFormulaParts('0F1(;1/2;z)').length,1);
});

test('transfer equations are exact and agree with the coefficient certificate',()=>{
  const entry=(id,values)=>({id,terms:values.map(String),offset:0,index_symbol:'n'});
  const map=sequenceTransfer(entry('Euler',[1,-1,5,-61]),entry('Fibonacci',[0,1,1,2,3]),4);
  assert.equal(map.verified,true);
  assert.equal(transferPolynomialPlain(map.rows,'kernel','H'),'H(z) = 1 + 2z - z^2 + 53z^3 (mod z^4)');
  assert.equal(transferPolynomialPlain(map.rows,'inverse','K'),'K(z) = 1 - 2z + 5z^2 - 65z^3 (mod z^4)');
  const tex=transferPolynomialTeX(map.rows,'kernel','H');
  assert.ok(tex.startsWith(String.raw`H(z)\equiv 1 + 2\,z - z^{2} + 53\,z^{3}`));
  assert.ok(tex.endsWith(String.raw`\pmod{z^{4}}`));
  assert.match(transferWitnessPlain(map.rows,2),/= 2; target=2; residual=0/);
  assert.ok(transferWitnessTeX(map.rows,2).includes(String.raw`\sum_{i=0}^{2}`));
  assert.ok(transferWitnessTeX(map.rows,2).includes(String.raw`\mathrm{residual}=0`));
});
test('rational source coefficients remain exact and malformed data fails closed',()=>{
  const entry=(id,terms)=>({id,terms:terms.map(String),offset:0,index_symbol:'n'});
  const map=sequenceTransfer(entry('A',[-2,3,7]),entry('B',[3,-2,1]),3);
  assert.equal(map.rows[0].kernel,'-3/2');
  assert.equal(rationalTeX('-3/2'),String.raw`-\frac{3}{2}`);
  assert.ok(transferPolynomialTeX(map.rows,'kernel','H').includes(String.raw`-\frac{3}{2}`));
  assert.match(transferPolynomialPlain(map.rows,'kernel','H'),/\-3\/2/);
  assert.throws(()=>rationalTeX('1/0'),/rational coefficient/);
  assert.throws(()=>rationalTeX('1.5'),/rational coefficient/);
  assert.throws(()=>transferWitnessTeX(map.rows,3),/outside the coefficient window/);
});

test('triangle rows typeset from the exact indexed integers without dropping signs',()=>{
  const entry={id:'KFOR-TRI-P-03',N:3,triangle:{variable:'r',row_lengths:[1,2,3]}};
  const row=[0,9,10].map((raw,k)=>({n:2,k,raw:String(raw)}));
  const result=triangleRowExpressions(entry,row);
  assert.equal(result.plain,'P_(3,2)(r) = 9r + 10r^2');
  assert.equal(result.tex,String.raw`P_{3,2}(r)=9\,r + 10\,r^{2}`);
  const theta={id:'KFOR-TRI-H',triangle:{variable:'x',row_lengths:[1,3]}};
  const thetaRow=[-1,0,2].map((raw,k)=>({n:1,k,raw:String(raw)}));
  assert.equal(triangleRowExpressions(theta,thetaRow).plain,'Theta_(2)(x) = -1 + 2x^2');
  const matrix={id:'KFOR-TRI-B-03',triangle:{variable:'x',row_lengths:[1,2]}};
  assert.equal(triangleRowExpressions(matrix,[{n:1,k:0,raw:'1'},{n:1,k:1,raw:'-1'}]).plain,'R_1(x) = 1 - x');
  assert.throws(()=>triangleRowExpressions(entry,[{n:2,k:1,raw:'10'}]),/complete coefficient row|index map/);
  assert.throws(()=>triangleRowExpressions(theta,[{n:1,k:0,raw:'1/2'},{n:1,k:1,raw:'0'},{n:1,k:2,raw:'1'}]),/exact integers/);
});
