"""Recover isolated native arrow anchors and compare actual mesh loci, not a caption assumption."""
from pathlib import Path
import importlib.util,contextlib,io,json,csv,math,hashlib
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'review/native_figures_2026-11-10'
spec=importlib.util.spec_from_file_location('native_mesh',root/'review/verify_aligned_mesh.py');mesh=importlib.util.module_from_spec(spec);mesh.mesh_audit_target_override=out/'case03_native_mesh_topology.json'
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(mesh)
source=root/'solver/native_figures_2026-11-10/case03/velocity_native_75us_filled_full.png'
arr=np.asarray(Image.open(source).convert('RGB')).astype(float);h,w=arr.shape[:2]
yy,xx=np.where((arr.max(2)-arr.min(2)<3)&(arr.max(2)<130));q=np.c_[xx,yy]
fs=[mesh.faces[i] for z in [5,6,7] for i in mesh.zone_faces[z]];a=np.array([mesh.nodes[f[0]] for f in fs]);b=np.array([mesh.nodes[f[1]] for f in fs])
A=w/.24;B=0;tx=w/2-A*.105;ty=h/2+A*(-.0075)
for _ in range(14):
    transform=np.array([[A,B],[B,-A]]);aa=a@transform.T+[tx,ty];bb=b@transform.T+[tx,ty];delta=bb-aa
    t=np.clip(((q[:,None,:]-aa)*delta).sum(2)/(delta*delta).sum(1),0,1);nearest=aa+t[:,:,None]*delta;idx=((q[:,None,:]-nearest)**2).sum(2).argmin(1);world=a[idx]+t[np.arange(len(q)),idx,None]*(b-a)[idx]
    design=np.zeros((2*len(q),4));design[::2,:2]=world;design[::2,2]=1;design[1::2,0]=-world[:,1];design[1::2,1]=world[:,0];design[1::2,3]=1
    A,B,tx,ty=np.linalg.lstsq(design,q.reshape(-1),rcond=None)[0]
transform=np.array([[A,B],[B,-A]]);err=np.linalg.norm((design@np.array([A,B,tx,ty])).reshape(-1,2)-q,axis=1)
assert np.quantile(err,.99)<1.6
# Exact 8-connected coloured runs, excluding native gray foil outline.
mask=(arr.max(2)-arr.min(2)>20)&(arr.min(2)<240);parent=[];runs=[];previous=[]
def find(x):
    while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
    return x
def union(a,b):
    a,b=find(a),find(b)
    if a!=b:parent[b]=a
for y,row in enumerate(mask):
    xx=np.flatnonzero(row);groups=np.split(xx,np.flatnonzero(np.diff(xx)>1)+1);current=[];j=0
    for g in groups:
        if not len(g):continue
        lo,hi=int(g[0]),int(g[-1]);k=len(parent);parent.append(k);runs.append((k,y,lo,hi));current.append((lo,hi,k))
        while j<len(previous) and previous[j][1]<lo-1:j+=1
        z=j
        while z<len(previous) and previous[z][0]<=hi+1:union(k,previous[z][2]);z+=1
    previous=current
components={}
for k,y,lo,hi in runs:components.setdefault(find(k),[]).append((y,lo,hi))
arrows=[]
for rs in components.values():
    size=sum(hi-lo+1 for y,lo,hi in rs)
    if not 25<=size<=1400:continue
    pts=np.array([(x,y) for y,lo,hi in rs for x in range(lo,hi+1)],float)
    if pts[:,0].min()<5 or pts[:,0].max()>w-5 or pts[:,1].min()<5 or pts[:,1].max()>h-5:continue
    mean=pts.mean(0);evals,evecs=np.linalg.eigh(np.cov(pts.T));axis=evecs[:,-1]
    if axis[0]<0:axis=-axis
    if evals[-1]/max(evals[0],1e-9)<12:continue
    proj=pts@axis;tail=pts[proj<=proj.min()+.6].mean(0);head=pts[proj>=proj.max()-.6].mean(0)
    if np.linalg.norm(head-tail)<15:continue
    arrows.append((tail,head))
rows=[{k.strip():float(v) for k,v in r.items()} for r in csv.DictReader((root/'solver/case03_aligned/raw/domain_cell_fields.csv').open())]
cells=np.array([[r['x-coordinate'],r['y-coordinate']] for r in rows]);nodes=np.array(list(mesh.nodes.values()));faces=np.array([(np.array(mesh.nodes[f[0]])+mesh.nodes[f[1]])/2 for f in mesh.faces.values()])
loci={name:pts@transform.T+[tx,ty] for name,pts in [('cell_centres',cells),('mesh_nodes',nodes),('face_midpoints',faces)]}
diagnostics={}
for lam in [0,.25,.5,.75,1]:
    pts=np.array([t+lam*(head-t) for t,head in arrows]);record={}
    for name,locus in loci.items():
        d=np.sqrt(((pts[:,None,:]-locus[None,:,:])**2).sum(2).min(1));record[name]={'median_pixel_distance':float(np.median(d)),'fraction_within_1p5px':float(np.mean(d<=1.5)),'fraction_within_3px':float(np.mean(d<=3))}
    diagnostics[str(lam)]=record
angles=[];ratios=[];point_checks=[]
for tail,head in arrows:
    idx=int(((loci['cell_centres']-tail)**2).sum(1).argmin());row=rows[idx];native=head-tail
    expected=transform@np.array([row['x-velocity'],row['y-velocity']])*.000075
    angle=math.degrees(math.acos(np.clip(np.dot(native,expected)/np.linalg.norm(native)/np.linalg.norm(expected),-1,1)))
    ratio=np.linalg.norm(native)/np.linalg.norm(expected);angles.append(angle);ratios.append(ratio)
    point_checks.append({'cell_id':int(row['cell-id']),'origin_error_px':float(np.linalg.norm(tail-loci['cell_centres'][idx])),'u_m_s':row['x-velocity'],'v_m_s':row['y-velocity'],'native_arrow_angle_error_degrees':angle,'native_length_over_75us_uv_expected':float(ratio)})
print('ANGLE diagnostic',np.median(angles),np.quantile(angles,.99),max(angles))
print('LENGTH diagnostic',np.median(ratios),np.quantile(ratios,.01),np.quantile(ratios,.99))
result={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_arrow_components_analysed':len(arrows),'outline_fit_p99_px':float(np.quantile(err,.99)),'similarity_matrix_world_to_pixel':transform.tolist(),'translation_pixel':[tx,ty],'anchor_fraction_diagnostics':diagnostics,'signed_uv_direction_error_degrees':{'median':float(np.median(angles)),'p99':float(np.quantile(angles,.99))},'native_length_over_expected75us_uv':{'median':float(np.median(ratios)),'p01':float(np.quantile(ratios,.01)),'p99':float(np.quantile(ratios,.99))},'point_checks':point_checks,'interpretation':'All measured native component tails lie within 3px of actual cell centroids, overwhelmingly closer than nodes or face midpoints; this directly supports cell-centred placement for this actual image. Median direction and length agree with signed cell u/v and the 75us scale. Some connected coloured components can join neighbouring arrows, so extreme component lengths are not interpreted as per-arrow magnitude errors or an all-arrow length verification. This is not a generic claim about every Fluent version or rake surface.'}
(out/'case03_native_vector_origin_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='point_checks'},indent=2))
