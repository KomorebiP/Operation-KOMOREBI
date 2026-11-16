const plotKeys=['sequence','seq','view','transform','scale','marks','start','count','modulus','N','power','compare','color','custom'];
export function atlasDestination(href){
  const url=new URL(href),plot=plotKeys.some(key=>url.searchParams.has(key))||['#explorer','#discover','#connections'].includes(url.hash);
  url.pathname=url.pathname.replace(/sequences\.html$/,'')+(plot?'sequence-explorer.html':'sequence-library.html');
  if(!plot&&['','#find','#catalogue','#saved','#reference'].includes(url.hash))url.hash='library-search';
  return url.href;
}
export function archiveDestination(href,filters={}){
  const url=new URL(href);url.pathname=url.pathname.replace(/sequence-archive\.html$/,'sequence-library.html');url.search='';url.hash='library-search';
  url.searchParams.set('collection','recovered');
  for(const [key,target]of [['query','q'],['family','kind'],['review','status'],['match','match'],['sort','sort']])if(filters[key])url.searchParams.set(target,filters[key]);
  return url.href;
}
