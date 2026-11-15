export function createReferenceClient(){
  let worker=null,active=null;
  function stop(){const pending=active;active=null;worker?.terminate();worker=null;pending?.reject(new DOMException('Reference activity cancelled.','AbortError'));}
  function request(type,payload,onProgress){
    if(active)return Promise.reject(Error('The reference engine is busy. Wait for it to finish or cancel its current activity.'));
    if(typeof Worker!=='function')return Promise.reject(Error('Background workers are unavailable. The reference downloads remain available.'));
    return new Promise((resolve,reject)=>{active={resolve,reject,onProgress};try{if(!worker){const current=new Worker(new URL('./sequence-oeis-worker.mjs',import.meta.url),{type:'module'});worker=current;
      current.onmessage=event=>{if(worker!==current||!active)return;const data=event.data;if(data.type==='progress'){active.onProgress?.(data.message);return;}const pending=active;active=null;if(data.type==='error')pending.reject(Error(data.message));else pending.resolve(data);};
      current.onerror=()=>{if(worker!==current)return;const pending=active;active=null;current.terminate();worker=null;pending?.reject(Error('Reference activity could not start. The snapshot downloads and recorded comparisons remain available.'));};}
      worker.postMessage({type,...payload});
    }catch(error){active=null;reject(error);}});
  }
  return {get busy(){return Boolean(active);},search:(query,onProgress)=>request('search',{query},onProgress),records:(records,onProgress)=>request('records',{records},onProgress),cancel:stop};
}
