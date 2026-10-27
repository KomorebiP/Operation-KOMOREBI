import sympy as s
b,x,w=s.symbols('b x w');J=2+3*w
G=s.groebner([b**3-7,x**3-J,w**2+w+1],b,x,w)
def red(p):return s.factor(G.reduce(s.expand(p))[1])
xinv=red(x*x*(-1-3*w)/7)
nu=red((x+b*xinv-b*b)/3);v=red(-b*b*nu-2*nu*nu)
A=red((21*b-42)*v*v+(-15*b*b+30*b)*v-b*b-4*b+11)
B=red(3*b*b*v*v+(18*b-42)*v-11*b*b+13*b+7)
W=red((A+w*B)/3);eps=2-b;r=b*b+2*b+4
print('W',W)
print('W/eps',red(W*r))
print('W*eps',red(W*eps))
print('W^3 / eps^3',red(W**3*r**3))
