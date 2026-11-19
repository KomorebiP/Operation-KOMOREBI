// Keep larger exact calculations off the interface thread.
// Author: Komorebi P.
import {computeExactWindow} from './sequence-closed-forms-core.mjs';

self.addEventListener('message',event=>{
  const {id,raw}=event.data||{};
  try{
    self.postMessage({id,report:computeExactWindow(raw)});
  }catch(error){
    self.postMessage({id,error:error instanceof Error?error.message:'The exact calculation failed.'});
  }
});
