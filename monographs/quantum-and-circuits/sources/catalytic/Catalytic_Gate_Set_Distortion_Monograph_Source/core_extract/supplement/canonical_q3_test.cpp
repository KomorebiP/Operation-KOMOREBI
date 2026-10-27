#include <bits/stdc++.h>
using namespace std;
static constexpr int N=6,Q=3,ROWS=729;
using State=uint64_t;
static uint16_t addrow[Q][ROWS][ROWS];
static uint8_t digit[ROWS][N];
static int p3[N+1];
inline uint16_t getrow(State s,int i){return (s>>(10*i))&1023u;}
inline State setrow(State s,int i,uint16_t r){return (s&~(State(1023)<<(10*i)))|(State(r)<<(10*i));}
inline State apply(State s,int src,int dst,int lambda){return setrow(s,dst,addrow[lambda][getrow(s,dst)][getrow(s,src)]);}
State identmat(){State s=0;for(int i=0;i<N;i++)s|=State(p3[i])<<(10*i);return s;}
State target(){
    State s=identmat();
    const int gates[][3]={{2,1,1},{1,3,1},{0,1,1},{1,4,1},{1,5,1},{2,1,2}};
    for(auto &g:gates)s=apply(s,g[0],g[1],g[2]);
    return s;
}
int main(){
    p3[0]=1;for(int i=1;i<=N;i++)p3[i]=p3[i-1]*Q;
    for(int x=0;x<ROWS;x++){int y=x;for(int j=0;j<N;j++){digit[x][j]=y%Q;y/=Q;}}
    for(int l=0;l<Q;l++)for(int a=0;a<ROWS;a++)for(int b=0;b<ROWS;b++){
        int c=0;for(int j=0;j<N;j++)c+=((digit[a][j]+l*digit[b][j])%Q)*p3[j];addrow[l][a][b]=c;
    }
    vector<array<int,3>> low,all;
    for(int s=0;s<N;s++)for(int t=0;t<N;t++)if(s!=t)for(int l=1;l<Q;l++){
        all.push_back({s,t,l});if(s<t)low.push_back({s,t,l});
    }
    State I=identmat(),T=target();
    unordered_map<State,uint8_t> dist;dist.reserve(7500000);dist.max_load_factor(0.75);vector<State> front{I};dist[I]=0;int found=-1;
    for(int d=0;d<7&&found<0;d++){
        vector<State> next;next.reserve(front.size()*8);
        for(State x:front)for(auto g:low){State y=apply(x,g[0],g[1],g[2]);if(!dist.count(y)){dist[y]=d+1;next.push_back(y);if(y==T)found=d+1;}}
        front.swap(next);cerr<<"lower depth "<<d+1<<" visited "<<dist.size()<<"\n";
    }
    auto ball3=[&](State start){unordered_map<State,uint8_t> d;d.reserve(80000);vector<State> f{start};d[start]=0;for(int dep=0;dep<3;dep++){vector<State> nx;for(State x:f)for(auto g:all){State y=apply(x,g[0],g[1],g[2]);if(!d.count(y)){d[y]=dep+1;nx.push_back(y);}}f.swap(nx);}return d;};
    auto a=ball3(I),b=ball3(T);int best=99,meet=0;for(auto &kv:a){auto it=b.find(kv.first);if(it!=b.end()){int v=kv.second+it->second;if(v<best){best=v;meet=1;}else if(v==best)meet++;}}
    cout<<"field 3 canonical target\n";
    cout<<"restricted_distance "<<found<<"\n";
    cout<<"ambient_distance "<<best<<"\n";
    cout<<"radius3_ball_size "<<a.size()<<"\n";
    cout<<"minimum_meeting_vertices "<<meet<<"\n";
}
