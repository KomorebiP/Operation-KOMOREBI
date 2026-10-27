// Independent modular q-product check. Arithmetic is exact throughout.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <utility>
#include <vector>
using i64 = long long;
using u64 = unsigned long long;
const int M = 1 << 19;
i64 power(i64 x,i64 n,i64 p){i64 r=1;for(;n;n>>=1,x=x*x%p)if(n&1)r=r*x%p;return r;}
void ntt(std::vector<int>& a, bool inverse,int mod){
 int n=(int)a.size();
 for(int i=1,j=0;i<n;i++){
   int bit=n>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;if(i<j)std::swap(a[i],a[j]);
 }
 for(int len=2;len<=n;len<<=1){
   i64 wlen=power(3,(mod-1)/len,mod);if(inverse)wlen=power(wlen,mod-2,mod);
   for(int i=0;i<n;i+=len){
     i64 w=1;
     for(int j=0;j<len/2;j++){
       int u=a[i+j];int v=(int)(a[i+j+len/2]*w%mod);
       int x=u+v;if(x>=mod)x-=mod;int y=u-v;if(y<0)y+=mod;
       a[i+j]=x;a[i+j+len/2]=y;w=w*wlen%mod;
     }
   }
 }
 if(inverse){i64 inv=power(n,mod-2,mod);for(int&v:a)v=(int)(v*inv%mod);}
}
std::vector<int> square_mod(const std::vector<int>&a){
 const int p1=998244353,p2=1004535809;
 int L=(int)a.size(),n=1;while(n<2*L-1)n<<=1;
 if((p1-1)%n || (p2-1)%n)throw std::runtime_error("unsupported NTT length");
 const u64 upper=(u64)L*(M-1)*(M-1),product=(u64)p1*p2;
 if(upper>=product)throw std::runtime_error("CRT bound insufficient");
 std::vector<int>x(n),y(n);std::copy(a.begin(),a.end(),x.begin());std::copy(a.begin(),a.end(),y.begin());
 ntt(x,false,p1);for(int&v:x)v=(int)((i64)v*v%p1);ntt(x,true,p1);
 ntt(y,false,p2);for(int&v:y)v=(int)((i64)v*v%p2);ntt(y,true,p2);
 i64 ip=power(p1,p2-2,p2);std::vector<int>r(L);
 for(int i=0;i<L;i++){
   i64 d=y[i]-(i64)x[i];if(d<0)d+=p2;
   i64 t=d*ip%p2;
   u64 c=(u64)x[i]+(u64)p1*t;
   r[i]=(int)(c%M);
 }
 return r;
}
int main(){
 auto start=std::chrono::steady_clock::now();
 const int N=1032190;
 std::vector<std::pair<int,int>>sparse;
 for(int m=0;m*(m+1)/2<=N;m++){
   int c=2*m+1;if(m&1)c=-c;c%=M;if(c<0)c+=M;
   sparse.push_back({m*(m+1)/2,c});
 }
 std::vector<int>A2(N+1);
 for(auto [i,a]:sparse)for(auto [j,b]:sparse){if(i+j>N)break;A2[i+j]=(A2[i+j]+(i64)a*b)%M;}
 auto A4=square_mod(A2);auto A8=square_mod(A4);
 std::cout<<"modulus "<<M<<"\n";
 for(int p: {2,3,5,7,11,13,2411,81919,131071,245759,294911,442367,524287,671743,737279,770047,786431,917503,1032191})
   std::cout<<p<<" "<<A8[p-1]<<"\n";
 auto stop=std::chrono::steady_clock::now();
 std::cout<<"seconds "<<std::chrono::duration<double>(stop-start).count()<<"\n";
}
