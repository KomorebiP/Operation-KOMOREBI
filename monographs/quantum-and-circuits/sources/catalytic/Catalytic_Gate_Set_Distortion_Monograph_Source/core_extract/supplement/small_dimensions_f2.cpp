#include <bits/stdc++.h>
using namespace std;
using Mat=uint64_t;

struct Model {
    int n;
    uint64_t rowmask;
    vector<pair<int,int>> lowgens, allgens;
    explicit Model(int n_): n(n_), rowmask((1ULL<<n)-1) {
        for(int s=0;s<n;s++) for(int t=0;t<n;t++) if(s!=t){
            allgens.push_back({s,t});
            if(s<t) lowgens.push_back({s,t});
        }
    }
    inline uint64_t getrow(Mat m,int i) const {return (m>>(n*i))&rowmask;}
    inline Mat setrow(Mat m,int i,uint64_t r) const {
        Mat mask=rowmask<<(n*i); return (m&~mask)|(r<<(n*i));
    }
    inline Mat gate(Mat m,int s,int t) const {return setrow(m,t,getrow(m,t)^getrow(m,s));}
    Mat ident() const {Mat m=0;for(int i=0;i<n;i++)m|=(Mat(1)<<i)<<(n*i);return m;}
    bool isU(Mat A) const {
        for(int i=0;i<n;i++){
            uint64_t r=getrow(A,i);
            if(!((r>>i)&1)) return false;
            if(r&~((1ULL<<(i+1))-1)) return false;
        }
        return true;
    }
    uint32_t encodeU(Mat A) const {
        uint32_t c=0;int b=0;
        for(int i=0;i<n;i++)for(int j=0;j<i;j++,b++)if((getrow(A,i)>>j)&1)c|=1u<<b;
        return c;
    }
};

int main(){
    for(int n=2;n<=5;n++){
        Model M(n); Mat I=M.ident(); const int usize=1<<(n*(n-1)/2);
        vector<uint8_t> low(usize,255); queue<Mat> q; q.push(I);low[0]=0;int maxlow=0;
        while(!q.empty()){
            Mat x=q.front();q.pop();int dx=low[M.encodeU(x)];maxlow=max(maxlow,dx);
            for(auto [s,t]:M.lowgens){Mat y=M.gate(x,s,t);auto c=M.encodeU(y);if(low[c]==255){low[c]=dx+1;q.push(y);}}
        }
        unordered_map<Mat,uint8_t> amb; amb.reserve(n==5?800000:10000);amb.max_load_factor(0.7);
        vector<Mat> front{I};amb[I]=0;
        for(int d=0;d<maxlow;d++){
            vector<Mat> next; next.reserve(front.size()*max(2,n));
            for(Mat x:front)for(auto [s,t]:M.allgens){Mat y=M.gate(x,s,t);if(!amb.count(y)){amb[y]=d+1;next.push_back(y);}}
            front.swap(next);
        }
        int defects=0,missing=0;map<pair<int,int>,int> census;
        for(auto &kv:amb) if(M.isU(kv.first)){
            int dl=low[M.encodeU(kv.first)],da=kv.second;census[{dl,da}]++;if(da<dl)defects++;
        }
        for(int c=0;c<usize;c++){
            // Every U target has ambient distance <= restricted distance <= maxlow,
            // so all must occur in the ambient radius-maxlow ball.
            // Count recovered targets through the census below.
        }
        int recovered=0;for(auto &kv:census)recovered+=kv.second;missing=usize-recovered;
        cout<<"n "<<n<<" U_size "<<usize<<" restricted_diameter "<<maxlow
            <<" ambient_ball "<<amb.size()<<" recovered_U "<<recovered
            <<" missing "<<missing<<" defects "<<defects<<"\n";
    }
}
