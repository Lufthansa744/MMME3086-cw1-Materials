"""Check native full/local mesh pictures against actual stored face connectivity."""
from pathlib import Path
import importlib.util,io,contextlib,json,hashlib
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'review/native_figures_2026-11-10'
spec=importlib.util.spec_from_file_location('native_taskA_mesh',root/'review/verify_aligned_mesh.py');mesh=importlib.util.module_from_spec(spec);mesh.mesh_audit_target_override=out/'taskA_native_original_mesh_audit.json'
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(mesh)
records=[]
for name,centre,field in [('mesh_full_native_final.png',(0,0),(1.,.15)),('mesh_local_native_final.png',(.05198367685079575,.0009169031400233507),(.115,.036))]:
    path=root/'solver/native_figures_2026-11-10/taskA'/name;im=np.asarray(Image.open(path).convert('RGB'));h,w=im.shape[:2]
    scale=min(w/field[0],h/field[1]);tx=w/2-scale*centre[0];ty=h/2+scale*centre[1]
    samples=[]
    for fid,f in sorted(mesh.faces.items()):
        a=np.array(mesh.nodes[f[0]]);b=np.array(mesh.nodes[f[1]]);mid=(a+b)/2
        px,py=np.rint(mid*[scale,-scale]+[tx,ty]).astype(int)
        if 12<=px<w-12 and 12<=py<h-12:samples.append((fid,px,py))
    def match(dx,dy):
        hits=0
        for fid,x,y in samples:
            patch=im[y+dy-2:y+dy+3,x+dx-2:x+dx+3]
            hits+=bool(patch.min()<235)
        return hits/len(samples)
    rate=match(0,0);assert rate>.97
    decoy=match(8,7)
    records.append({'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pixels':[w,h],'orthographic_camera_centre_m':centre,'camera_field_m':field,'native_isotropic_pixel_scale':scale,'actual_face_midpoint_controls':len(samples),'actual_edge_pixel_match_within_2px':rate,'decoy_shift8x7px_match_fraction':decoy,'source_mesh_sha256':hashlib.sha256(mesh.blob).hexdigest(),'original_counts':mesh.counts})
(out/'taskA_native_mesh_pixel_audit.json').write_text(json.dumps({'status':'Actual native edge-position sampling PASS; final composition labels, extents and print layout still pending','records':records},indent=2),encoding='utf-8');print(json.dumps(records,indent=2))
