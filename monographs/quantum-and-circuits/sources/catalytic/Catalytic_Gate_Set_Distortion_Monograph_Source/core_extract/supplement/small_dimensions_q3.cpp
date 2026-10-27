#include <bits/stdc++.h>
using namespace std; using State=uint64_t;
struct Model{
 int n,Q=3,rows,rbits; uint64_t rmask; vector<int> powq; vector<vector<array<int,2>>> dummy; vector<vector<vector<uint16_t>>> add;
 vector<array<int,3>> low,all;
 Model(int n_):n(n_){powq.resize(n+1);powq[0]=1;for(int i=1;i<=n;i++)powq[i]=powq[i-1]*Q;rows=powq[n];rbits=0;while((1<<rbits)<rows)rbits++;rmask=(1ULL<<rbits)-1;
  vector<vector<uint8_t>> dig(rows,vector<uint8_t>(n));for(int x=0;x<rows;x++){int y=x;for(int j=0;j<n;j++){dig[x][j]=y%Q;y/=Q;}}
  add.assign(Q,vector<vector<uint16_t>>(rows,vector<uint16_t>(rows)));
  for(int l=0;l<Q;l++)for(int a=0;a<rows;a++)for(int b=0;b<rows;b++){int c=0;for(int j=0;j<n;j++)c+=((dig[a][j]+l*dig[b][j])%Q)*powq[j];add[l][a][b]=c;}
  for(int s=0;s<n;s++)for(int t=0;t<n;t++)if(s!=t)for(int l=1;l<Q;l++){all.push_back({s,t,l});if(s<t)low.push_back({s,t,l});}
 }
 inline int getrow(State s,int i)const{return (s>>(rbits*i))&rmask;}
 inline State setrow(State s,int i,int r)const{State mask=rmask<<(rbits*i);return (s&~mask)|(State(r)<<(rbits*i));}
 inline State gate(State s,int src,int dst,int l)const{return setrow(s,dst,add[l][getrow(s,dst)][getrow(s,src)]);}
 State ident()const{State s=0;for(int i=0;i<n;i++)s|=State(powq[i])<<(rbits*i);return s;}
 bool isU(State s)const{for(int i=0;i<n;i++){int r=getrow(s,i);for(int j=i+1;j<n;j++)if((r/powq[j])%Q)return false;if((r/powq[i])%Q!=1)return false;}return true;}
 uint32_t encodeU(State s)const{uint32_t c=0,m=1;for(int i=0;i<n;i++){int r=getrow(s,i);for(int j=0;j<i;j++){c+=((r/powq[j])%Q)*m;m*=Q;}}return c;}
};
int main(){for(int n=2;n<=4;n++){Model M(n);int usize=1;for(int i=0;i<n*(n-1)/2;i++)usize*=3;State I=M.ident();vector<uint8_t> low(usize,255);queue<State>q;q.push(I);low[0]=0;int diam=0;while(!q.empty()){auto x=q.front();q.pop();int dx=low[M.encodeU(x)];diam=max(diam,dx);for(auto g:M.low){auto y=M.gate(x,g[0],g[1],g[2]);auto c=M.encodeU(y);if(low[c]==255){low[c]=dx+1;q.push(y);}}}
 unordered_map<State,uint8_t> amb;amb.reserve(n==5?5000000:100000);amb.max_load_factor(.7);vector<State>front{I};amb[I]=0;for(int d=0;d<diam;d++){vector<State>nx;nx.reserve(front.size()*5);for(auto x:front)for(auto g:M.all){auto y=M.gate(x,g[0],g[1],g[2]);if(!amb.count(y)){amb[y]=d+1;nx.push_back(y);}}front.swap(nx);cerr<<"n "<<n<<" depth "<<d+1<<" ball "<<amb.size()<<"\n";}
 int rec=0,def=0;for(auto&kv:amb)if(M.isU(kv.first)){rec++;if(kv.second<low[M.encodeU(kv.first)])def++;}
 cout<<"q 3 n "<<n<<" U_size "<<usize<<" restricted_diameter "<<diam<<" ambient_ball "<<amb.size()<<" recovered_U "<<rec<<" missing "<<(usize-rec)<<" defects "<<def<<"\n";
 }}
