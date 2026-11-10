"""Independent native PNG/actual-cell geometric coverage audit; no field painting."""
from pathlib import Path
import importlib.util,contextlib,io,json,csv,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
root=Path(__file__).resolve().parents[2];out=root/'review/native_figures_2026-11-10'
spec=importlib.util.spec_from_file_location('native_review_mesh',root/'review/verify_aligned_mesh.py')
mesh=importlib.util.module_from_spec(spec)
mesh.mesh_audit_target_override=out/'case03_native_mesh_topology.json'
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(mesh)
base=root/'solver/case03_aligned/raw'
def read(name):return [{k.strip():float(v) for k,v in r.items()} for r in csv.DictReader((base/name).open())]
domain=read('domain_cell_fields.csv');walls=sum([read(n) for n in ['suction_p_yplus.csv','pressure_p_yplus.csv','trailing_p_yplus.csv']],[])
ids={int(r['cell-id']) for r in walls};assert len(ids)==103
positive={int(r['cell-id']) for r in domain if r['y-plus']>0}
visible=set()
for cid in positive:
    ns={n for fi in mesh.cell_faces[cid] for n in mesh.faces[fi][:2]}
    p=np.array([mesh.nodes[n] for n in ns])
    if p[:,0].max()>=-.008 and p[:,0].min()<=.108 and p[:,1].max()>=-.024 and p[:,1].min()<=.014:visible.add(cid)
assert visible==ids,'Native positive-range plus viewport does not isolate exact foil cells'
native=root/'solver/native_figures_2026-11-10/case03/yplus_native_clean_full.png'
im=Image.open(native).convert('RGB');arr=np.asarray(im).astype(float);height,width=arr.shape[:2]
gray=(arr.max(2)-arr.min(2)<3)&(arr.min(2)<170)
yy,xx=np.where(gray);q=np.c_[xx,yy].astype(float)
wallfaces=[f for f in mesh.faces.values() if (f[2]==0 or f[3]==0) and f[2]+f[3] in ids and f[0] in {n for z in [5,6,7] for fi in mesh.zone_faces[z] for n in mesh.faces[fi][:2]} and f[1] in {n for z in [5,6,7] for fi in mesh.zone_faces[z] for n in mesh.faces[fi][:2]}]
assert len(wallfaces)==103
a=np.array([mesh.nodes[f[0]] for f in wallfaces]);b=np.array([mesh.nodes[f[1]] for f in wallfaces])
# Fit native orthographic scale/translation from all real foil edges and all gray outline pixels.
scale=width/.116;tx=.008*scale;ty=.014*scale
for _ in range(14):
    aa=a*np.array([scale,-scale])+[tx,ty];bb=b*np.array([scale,-scale])+[tx,ty];delta=bb-aa
    t=np.clip(((q[:,None,:]-aa)*delta).sum(2)/(delta*delta).sum(1),0,1)
    nearest=aa+t[:,:,None]*delta;dist=((q[:,None,:]-nearest)**2).sum(2);idx=dist.argmin(1)
    world=a[idx]+t[np.arange(len(q)),idx,None]*(b-a)[idx]
    design=np.zeros((2*len(q),3));design[::2,0]=world[:,0];design[::2,1]=1;design[1::2,0]=-world[:,1];design[1::2,2]=1
    scale,tx,ty=np.linalg.lstsq(design,q.reshape(-1),rcond=None)[0]
fit=design@np.array([scale,tx,ty]);errors=np.linalg.norm(fit.reshape(-1,2)-q,axis=1)
assert np.median(errors)<.6 and np.quantile(errors,.99)<1.5
expected=Image.new('L',(width,height),0);draw=ImageDraw.Draw(expected);cell_controls=[]
by={int(r['cell-id']):r for r in domain}
for cid in sorted(ids):
    ns={n for fi in mesh.cell_faces[cid] for n in mesh.faces[fi][:2]};pts=np.array([mesh.nodes[n] for n in ns]);pixels=pts*[scale,-scale]+[tx,ty]
    draw.polygon([tuple(p) for p in pixels],fill=255)
    ctr=pts.mean(0)*[scale,-scale]+[tx,ty];x,y=np.rint(ctr).astype(int)
    rgb=arr[y,x];cell_controls.append({'cell_id':cid,'yplus':by[cid]['y-plus'],'pixel_center':[int(x),int(y)],'native_center_RGB':list(map(int,rgb)),'center_is_coloured':bool(rgb.max()-rgb.min()>15)})
colour=(arr.max(2)-arr.min(2)>15)&(arr.min(2)<245)
dilated=np.asarray(expected.filter(ImageFilter.MaxFilter(5)))>0
outside=int((colour&~dilated).sum());fraction=outside/max(1,int(colour.sum()))
assert fraction<.001 and all(x['center_is_coloured'] for x in cell_controls)
result={'native_path':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'image_pixels':[width,height],'viewport_world_m':[-.008,.108,-.024,.014],'visible_positive_cell_ids_equal_exact_foil_103':True,'visible_cell_count':len(visible),'orthographic_pixel_map':{'u':f'{scale}*x + {tx}','v':f'-{scale}*y + {ty}','isotropic_scale_pixels_per_m':float(scale)},'foil_outline_fit_pixels':{'median':float(np.median(errors)),'p99':float(np.quantile(errors,.99)),'pixels':len(q)},'coloured_pixels':int(colour.sum()),'coloured_pixels_outside_actual_cell_union_plus_2px_edge_tolerance':outside,'outside_fraction':fraction,'all_103_actual_cell_centroids_coloured':True,'cell_controls':cell_controls,'status':'PASS actual native image/world geometry/103 cell coverage, pending final native palette scalar verification and assembled-layout QA'}
(out/'case03_native_cell_image_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='cell_controls'},indent=2))
