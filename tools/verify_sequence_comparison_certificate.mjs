#!/usr/bin/env node
/** Independently replay an exported finite Komorebi sequence comparison. */
import {readFileSync,statSync} from 'node:fs';
import {verifyComparisonCertificate} from '../website/assets/sequence-comparison-certificate.mjs';

async function main(){
  const file=process.argv[2];
  if(!file){
    console.error('Usage: node tools/verify_sequence_comparison_certificate.mjs <certificate.json>');
    process.exitCode=2;return;
  }
  try {
    const info=statSync(file);
    if(info.size>8000000)throw Error('Certificate is larger than the supported eight-megabyte limit.');
    const certificate=JSON.parse(readFileSync(file,'utf8'));
    const result=await verifyComparisonCertificate(certificate);
    console.log(JSON.stringify({...result,
      scope:'Finite calculations verified against embedded exact inputs; not a proof of infinite identity or independent source authority.'},null,2));
  }catch(error){
    console.error('CERTIFICATE VERIFICATION FAILED: '+error.message);
    process.exitCode=1;
  }
}
await main();
