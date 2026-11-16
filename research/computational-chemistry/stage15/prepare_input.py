"""Create a deterministic, explicitly identified selected-array H10 input view."""
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
import zipfile
import numpy as np

KEEP=['h1','eri','source','ground_state','ao_to_mo','ground_energy','ground_sector','ion_sector','n_orbitals','source_index']
EXPECTED='e6a3540d254b54a77902bd13049f302eb6dec647088b086d3948a887d0da9166'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    raw=args.source.read_bytes()
    if sha(raw)!=EXPECTED:raise ValueError('Different original fixture')
    if args.output.exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True);records=[]
    with np.load(BytesIO(raw),allow_pickle=False) as data,zipfile.ZipFile(args.output/'h10_view.npz','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted(KEEP):
            array=data[name];buffer=BytesIO();np.lib.format.write_array(buffer,array,allow_pickle=False)
            item=zipfile.ZipInfo(name+'.npy',date_time=(2026,11,16,0,0,0));item.create_system=0;item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o100644<<16
            archive.writestr(item,buffer.getvalue())
            records.append(dict(name=name,shape=list(array.shape),dtype=str(array.dtype),array_bytes_sha256=sha(array.tobytes())))
    record=dict(original_container_sha256=EXPECTED,view_container_sha256=sha((args.output/'h10_view.npz').read_bytes()),retained_arrays=records,
        identity='Selected arrays retain every original shape, dtype and element byte. This NPZ container is a new identified view, not the original container.',
        source_scope='Stored approximate neutral vector and stored local alpha-removal source; no exact ground-state or continuum-chemistry qualification.',
        omitted='Nine unused source columns, AO labels, nuclear energy, original runtime metadata and unrelated history')
    (args.output/'INPUT_VIEW.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\r\n')
    print(json.dumps(dict(bytes=(args.output/'h10_view.npz').stat().st_size,sha256=record['view_container_sha256'])))
if __name__=='__main__':main()
