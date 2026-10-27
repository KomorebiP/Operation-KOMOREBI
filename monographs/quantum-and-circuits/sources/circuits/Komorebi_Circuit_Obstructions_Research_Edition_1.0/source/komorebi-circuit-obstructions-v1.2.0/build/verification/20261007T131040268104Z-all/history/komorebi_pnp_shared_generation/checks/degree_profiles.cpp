// Exact full truth-table calculation, n <= 4. No numerical arithmetic.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
int main(int argc,char**argv){
  if(argc!=3) throw std::runtime_error("usage: degree_profiles n output.bin");
  int n=std::stoi(argv[1]); if(n<1||n>4)throw std::runtime_error("n outside 1..4");
  int points=1<<n, count=1<<points;
  std::vector<uint8_t> deg(count), alpha(count,255), beta(count,0);
  std::vector<std::vector<uint8_t>> local(points,std::vector<uint8_t>(count,255));
  for(int f=0;f<count;++f){
    int c=f;
    for(int i=0;i<n;++i)
      for(int x=0;x<points;++x) if(x&(1<<i))
        if((c>>(x^(1<<i)))&1)c^=1<<x;
    int d=0;
    for(int x=0;x<points;++x)if((c>>x)&1)d=std::max(d,__builtin_popcount((unsigned)x));
    deg[f]=d;
    if(f){alpha[f]=d;for(int v=0;v<points;++v)if((f>>v)&1)local[v][f]=d;}
  }
  // min over all nonzero supported h; for local[v], require h(v)=1.
  for(int i=0;i<points;++i)for(int f=0;f<count;++f)if(f&(1<<i)){
    int prev=f^(1<<i); alpha[f]=std::min(alpha[f],alpha[prev]);
    for(int v=0;v<points;++v)local[v][f]=std::min(local[v][f],local[v][prev]);
  }
  for(int f=1;f<count;++f)for(int v=0;v<points;++v)if((f>>v)&1)
    beta[f]=std::max(beta[f],local[v][f]);
  alpha[0]=0;
  std::vector<int> affine;
  for(int s=0;s<(1<<n);++s)for(int b=0;b<2;++b){
    int a=0;for(int x=0;x<points;++x)if((__builtin_parity((unsigned)(s&x))^b))a|=1<<x;
    affine.push_back(a);
  }
  std::ofstream out(argv[2],std::ios::binary);if(!out)throw std::runtime_error("output");
  uint32_t header[3]={(uint32_t)n,(uint32_t)points,(uint32_t)count};out.write((char*)header,sizeof(header));
  int local_strict=0, orbit_strict=0, bound_strict=0;
  for(int f=0;f<count;++f){
    uint8_t ao=0,bo=0;
    for(int l:affine){ao=std::max(ao,alpha[f^l]);bo=std::max(bo,beta[f^l]);}
    uint8_t row[5]={deg[f],alpha[f],beta[f],ao,bo};out.write((char*)row,5);
    local_strict += beta[f]>alpha[f];orbit_strict += bo>ao;
    int old=std::max({0,(int)deg[f]-1,2*(int)ao-3});
    int nb=std::max({0,(int)deg[f]-1,2*(int)bo-3});
    bound_strict += nb>old;
  }
  for(int v=0;v<points;++v)out.write((char*)local[v].data(),count);
  std::cout<<"{\"n\":"<<n<<",\"functions\":"<<count<<",\"beta_greater_alpha\":"<<local_strict<<",\"beta_orbit_greater_alpha_orbit\":"<<orbit_strict<<",\"strict_orbit_lower_bound_improvements\":"<<bound_strict<<"}\n";
}
