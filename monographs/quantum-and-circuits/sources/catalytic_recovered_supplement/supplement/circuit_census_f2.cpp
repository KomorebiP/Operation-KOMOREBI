#include <bits/stdc++.h>
using namespace std;

static constexpr int N=6;
using Mat = uint64_t;

inline uint8_t getrow(Mat m,int i){ return (m>>(N*i)) & ((1u<<N)-1); }
inline Mat setrow(Mat m,int i,uint8_t r){
    Mat mask=((Mat)((1u<<N)-1))<<(N*i);
    return (m & ~mask) | ((Mat)r<<(N*i));
}
inline Mat identmat(){ Mat m=0; for(int i=0;i<N;i++) m|=(Mat(1)<<i)<<(N*i); return m; }
inline Mat gate(Mat m,int s,int t){ uint8_t rs=getrow(m,s), rt=getrow(m,t); return setrow(m,t,rt^rs); }
inline Mat mul(Mat A,Mat B){
    Mat C=0;
    for(int i=0;i<N;i++){
        uint8_t ar=getrow(A,i), cr=0;
        for(int k=0;k<N;k++) if((ar>>k)&1) cr ^= getrow(B,k);
        C |= (Mat)cr<<(N*i);
    }
    return C;
}
Mat inv(Mat A){
    uint8_t L[N],R[N];
    for(int i=0;i<N;i++){L[i]=getrow(A,i);R[i]=1u<<i;}
    for(int c=0;c<N;c++){
        int p=c; while(p<N && !((L[p]>>c)&1)) p++;
        if(p==N){ cerr<<"singular\n"; abort(); }
        if(p!=c){ swap(L[p],L[c]);swap(R[p],R[c]); }
        for(int i=0;i<N;i++) if(i!=c && ((L[i]>>c)&1)){L[i]^=L[c];R[i]^=R[c];}
    }
    Mat B=0; for(int i=0;i<N;i++) B|=(Mat)R[i]<<(N*i); return B;
}
inline bool isU(Mat A){
    for(int i=0;i<N;i++){
        uint8_t r=getrow(A,i);
        if(!((r>>i)&1)) return false;
        if(r & ~((1u<<(i+1))-1)) return false;
    }
    return true;
}
inline uint16_t encodeU(Mat A){
    uint16_t c=0; int b=0;
    for(int i=0;i<N;i++) for(int j=0;j<i;j++,b++) if((getrow(A,i)>>j)&1) c|=uint16_t(1)<<b;
    return c;
}
inline Mat decodeU(uint16_t c){
    Mat A=identmat(); int b=0;
    for(int i=0;i<N;i++){
        uint8_t r=getrow(A,i);
        for(int j=0;j<i;j++,b++) if((c>>b)&1) r|=1u<<j;
        A=setrow(A,i,r);
    }
    return A;
}
inline uint8_t getcol(Mat A,int j){
    uint8_t c=0; for(int i=0;i<N;i++) if((getrow(A,i)>>j)&1) c|=1u<<i; return c;
}
// Canonical representative of the right U-coset, obtained by reducing each
// column modulo the span of the columns to its right.
inline Mat right_coset_key(Mat A){
    uint8_t can[N]={0}; int piv[N];
    for(int j=N-1;j>=0;j--){
        uint8_t x=getcol(A,j);
        for(int k=N-1;k>j;k--) if((x>>piv[k])&1) x ^= can[k];
        if(!x){ cerr<<"bad flag reduction\n"; abort(); }
        int p=31-__builtin_clz((unsigned)x);
        can[j]=x; piv[j]=p;
    }
    Mat key=0; for(int j=0;j<N;j++) key|=(Mat)can[j]<<(N*j); return key;
}

int main(){
    vector<pair<int,int>> allgens,lowgens;
    for(int s=0;s<N;s++) for(int t=0;t<N;t++) if(s!=t){ allgens.push_back({s,t}); if(s<t) lowgens.push_back({s,t}); }
    Mat I=identmat();
    unordered_map<Mat,uint8_t> d4; d4.reserve(150000); d4.max_load_factor(0.7);
    vector<Mat> frontier{I}; d4[I]=0;
    for(int d=0;d<4;d++){
        vector<Mat> next; next.reserve(frontier.size()*10);
        for(Mat x:frontier) for(auto [s,t]:allgens){
            Mat y=gate(x,s,t);
            if(!d4.count(y)){d4[y]=d+1;next.push_back(y);}    
        }
        frontier.swap(next);
        cerr<<"depth "<<d+1<<" ball "<<d4.size()<<" frontier "<<frontier.size()<<"\n";
    }
    struct Item{Mat x;uint8_t d;};
    unordered_map<Mat,vector<Item>> buckets; buckets.reserve(10000);
    for(auto &kv:d4) buckets[right_coset_key(kv.first)].push_back({kv.first,kv.second});
    size_t sq=0,maxb=0; for(auto &kv:buckets){sq+=kv.second.size()*kv.second.size();maxb=max(maxb,kv.second.size());}
    cerr<<"buckets "<<buckets.size()<<" max "<<maxb<<" ordered pairs "<<sq<<"\n";
    vector<uint8_t> amb(1<<15,255);
    size_t checked=0;
    for(auto &kv:buckets){
        auto &v=kv.second;
        Mat r=v[0].x, rinv=inv(r);
        struct UItem{Mat u,ui;uint8_t d;};
        vector<UItem> us; us.reserve(v.size());
        for(auto &it:v){
            Mat u=mul(rinv,it.x);
            if(!isU(u)){ cerr<<"coset failure\n"; return 2; }
            us.push_back({u,inv(u),it.d});
        }
        for(auto &b:us) for(auto &a:us){
            Mat t=mul(b.ui,a.u);
            uint16_t c=encodeU(t);
            uint8_t cost=b.d+a.d;
            if(cost<amb[c]) amb[c]=cost;
        }
        checked += us.size()*us.size();
    }
    cerr<<"checked "<<checked<<"\n";
    // Restricted BFS on U_6.
    vector<uint8_t> low(1<<15,255);
    queue<Mat> q; low[0]=0;q.push(I);
    while(!q.empty()){
        Mat x=q.front();q.pop(); uint8_t dx=low[encodeU(x)];
        for(auto [s,t]:lowgens){
            Mat y=gate(x,s,t); uint16_t c=encodeU(y);
            if(low[c]==255){low[c]=dx+1;q.push(y);} 
        }
    }
    map<pair<int,int>,int> pairs;
    vector<uint16_t> defects;
    int missing=0;
    for(int c=0;c<(1<<15);c++){
        if(amb[c]==255) missing++;
        pairs[{low[c],amb[c]}]++;
        if(amb[c]<low[c]) defects.push_back(c);
    }
    cout<<"missing "<<missing<<"\n";
    for(auto &kv:pairs) cout<<"low "<<kv.first.first<<" amb "<<kv.first.second<<" count "<<kv.second<<"\n";
    cout<<"defects "<<defects.size()<<"\n";
    for(uint16_t c:defects){
        Mat A=decodeU(c);
        cout<<"code "<<c<<" low "<<(int)low[c]<<" amb "<<(int)amb[c]<<" rows";
        for(int i=0;i<N;i++) cout<<" "<<(int)getrow(A,i);
        cout<<"\n";
    }
}
