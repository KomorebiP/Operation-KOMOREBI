"""Classical reference definitions appended to the atlas; all indices start at zero."""
from math import comb

# kind, title, formula, recurrence, topics, OEIS reference, worked example
REFERENCES = [
    ('naturals', 'Nonnegative integers', 'a(n) = n', 'a(0)=0; a(n+1)=a(n)+1.', ['elementary', 'polynomial'], 'A001477', 'At n=4, a(4)=4. Partial sums give 0+1+2+3+4=10, the fourth triangular number.'),
    ('odd', 'Positive odd numbers', 'a(n) = 2n+1', 'a(0)=1; a(n+1)=a(n)+2.', ['elementary', 'polynomial'], 'A005408', 'The first four terms sum to 1+3+5+7=16=4^2.'),
    ('triangular', 'Triangular numbers', 'a(n) = n(n+1)/2', 'a(0)=0; a(n)=a(n-1)+n for n>=1.', ['elementary', 'polynomial', 'figurate'], 'A000217', 'At n=4, a(4)=4*5/2=10=1+2+3+4.'),
    ('square', 'Square numbers', 'a(n) = n^2', 'a(0)=0; a(n)=a(n-1)+2n-1 for n>=1.', ['elementary', 'polynomial', 'figurate'], 'A000290', 'At n=4, 4^2=16. The first difference there is 16-9=7; the second difference is 16-2*9+4=2.'),
    ('cube', 'Cube numbers', 'a(n) = n^3', 'a(0)=0; a(n)=a(n-1)+3n^2-3n+1 for n>=1.', ['elementary', 'polynomial'], 'A000578', 'At n=3, a(3)=27. The adjacent difference is 27-8=19.'),
    ('power-two', 'Powers of two', 'a(n) = 2^n', 'a(0)=1; a(n+1)=2a(n).', ['elementary', 'exponential'], 'A000079', 'At n=5, a(5)=32. Each successive ratio equals 2.'),
    ('power-three', 'Powers of three', 'a(n) = 3^n', 'a(0)=1; a(n+1)=3a(n).', ['elementary', 'exponential'], 'A000244', 'At n=4, a(4)=81. Each successive ratio equals 3.'),
    ('catalan', 'Catalan numbers', 'a(n) = binom(2n,n)/(n+1)', 'a(0)=1; a(n+1)=sum_{k=0}^n a(k)a(n-k).', ['combinatorics', 'counting', 'Catalan'], 'A000108', 'At n=3, binom(6,3)/(3+1)=20/4=5. The convolution gives 1*2+1*1+2*1=5.'),
    ('central-binomial', 'Central binomial coefficients', 'a(n) = binom(2n,n)', 'a(0)=1; n*a(n)=2(2n-1)*a(n-1) for n>=1.', ['combinatorics', 'binomial'], 'A000984', 'At n=3, binom(6,3)=20=(3+1)*5, relating this term to the third Catalan number.'),
    ('partition', 'Integer partition numbers', 'a(n) = [x^n] product_{k>=1} 1/(1-x^k)', 'Count unordered sums of positive integers; a(0)=1 includes the empty partition.', ['partitions', 'combinatorics', 'counting'], 'A000041', 'The five partitions of 4 are 4; 3+1; 2+2; 2+1+1; and 1+1+1+1. Thus a(4)=5.'),
    ('lucas', 'Lucas numbers', 'L(0)=2, L(1)=1; L(n)=L(n-1)+L(n-2)', 'Use the Fibonacci recurrence with initial terms 2 and 1.', ['recurrence', 'Lucas'], 'A000032', 'L(4)=L(3)+L(2)=4+3=7. The different initial values distinguish this from Fibonacci numbers.'),
    ('pell', 'Pell numbers', 'P(0)=0, P(1)=1; P(n)=2P(n-1)+P(n-2)', 'Use the second-order recurrence from n=2 onward.', ['recurrence', 'Pell'], 'A000129', 'P(4)=2P(3)+P(2)=2*5+2=12.'),
]
KINDS = {row[0] for row in REFERENCES}

def reference_terms(kind, count):
    if kind == 'naturals': return list(range(count))
    if kind == 'odd': return [2*n+1 for n in range(count)]
    if kind == 'triangular': return [n*(n+1)//2 for n in range(count)]
    if kind == 'square': return [n*n for n in range(count)]
    if kind == 'cube': return [n**3 for n in range(count)]
    if kind == 'power-two': return [2**n for n in range(count)]
    if kind == 'power-three': return [3**n for n in range(count)]
    if kind == 'catalan': return [comb(2*n,n)//(n+1) for n in range(count)]
    if kind == 'central-binomial': return [comb(2*n,n) for n in range(count)]
    if kind == 'partition':
        values = [1]+[0]*(count-1)
        for part in range(1,count):
            for n in range(part,count): values[n] += values[n-part]
        return values
    if kind in ('lucas','pell'):
        a,b = (2,1) if kind == 'lucas' else (0,1)
        values=[]
        for _ in range(count):
            values.append(a); a,b=b,(b+a if kind=='lucas' else 2*b+a)
        return values
    raise ValueError('Unknown reference definition')

def program(entry):
    """A self-contained, copyable program using only the Python standard library."""
    kind=entry['kind']
    start='from math import comb, factorial\n\ncount = 16\n'
    if kind in ('reciprocal','euler'):
        N,r=entry.get('N',2),entry.get('power',1)
        code=f'N, r = {N}, {r}\nbase = [1]\nfor n in range(1, count):\n    base.append(sum((-1)**(k+1)*comb(N*n,N*k)*base[n-k] for k in range(1,n+1)))\na = [1]+[0]*(count-1)\nfor _ in range(r):\n    a = [sum(comb(N*n,N*k)*a[k]*base[n-k] for k in range(n+1)) for n in range(count)]\n'
        if kind=='euler': code+='a = [(-1)**n*v for n,v in enumerate(a)]\n'
    elif kind in ('bell','fubini'):
        weight='factorial(k)' if kind=='fubini' else '1'
        code=f'row, a = [1], []\nfor n in range(count):\n    a.append(sum(v*{weight} for k,v in enumerate(row)))\n    row = [0]+[k*(row[k] if k<len(row) else 0)+row[k-1] for k in range(1,n+2)]\n'
    elif kind in ('fibonacci','lucas','pell'):
        x,y=(2,1) if kind=='lucas' else (0,1)
        code=f'x, y, a = {x}, {y}, []\nfor _ in range(count):\n    a.append(x)\n    x, y = y, '+('2*y+x' if kind=='pell' else 'x+y')+'\n'
    elif kind=='partition':
        code='a = [1]+[0]*(count-1)\nfor part in range(1,count):\n    for n in range(part,count):\n        a[n] += a[n-part]\n'
    else:
        expression={'factorial':'factorial(n)','naturals':'n','odd':'2*n+1','triangular':'n*(n+1)//2','square':'n*n','cube':'n**3','power-two':'2**n','power-three':'3**n','catalan':'comb(2*n,n)//(n+1)','central-binomial':'comb(2*n,n)'}[kind]
        code='a = ['+expression+' for n in range(count)]\n'
    return start+code+'print(a)\n'

def connections(entry, entries):
    """Find finite twelve-term relations, labelled as checks rather than identities."""
    a=list(map(int,entry['terms']))
    probes=[('alternating signs',0,[(-1)**n*v for n,v in enumerate(a)]),('absolute values',0,list(map(abs,a))),('first differences',1,[a[n]-a[n-1] for n in range(1,len(a))])]
    total=0; sums=[]
    for v in a: total+=v; sums.append(total)
    probes.append(('partial sums',0,sums))
    found=[]
    for label,start,values in probes:
        if values==a: continue
        pattern=list(map(str,values[:12]))
        if len(set(pattern))<3: continue
        for other in entries:
            if other['id']==entry['id']: continue
            for at in range(len(other['terms'])-len(pattern)+1):
                if other['terms'][at:at+len(pattern)]==pattern:
                    found.append(dict(id=other['id'],title=other['title'],transform=label,source_start=start,target_start=at,matched_terms=len(pattern)))
                    break
    return found
