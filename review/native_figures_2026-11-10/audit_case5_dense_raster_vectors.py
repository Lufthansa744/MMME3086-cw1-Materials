"""Cross-check actual native dense-rake arrow pixels against native signed point values."""
from pathlib import Path
import contextlib,io,json,csv,math,hashlib
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'review/native_figures_2026-11-10'
code=(root/'review/audit_enhanced_mesh.py').read_text().replace("'enhanced_mesh_geometry_audit.json'","'native_figures_2026-11-10/case05_native_mesh_topology.json'")
mesh={'__file__':str(root/'review/audit_enhanced_mesh.py')}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(code,'native_enhanced_mesh','exec'),mesh)
source=root/'solver/native_figures_2026-11-10/case05/velocity_native_rakes_dense_75us_outline4.png';arr=np.asarray(Image.open(source).convert('RGB')).astype(float);h,w=arr.shape[:2]
yy,xx=np.where((arr.max(2)-arr.min(2)<3)&(arr.max(2)<100));q=np.c_[xx,yy][::max(1,len(xx)//2500)]
ids=[mesh['zones'][n]['id'] for n in ['aerofoil-pressure','aerofoil-suction','aerofoil-trail']];faces=[mesh['faces'][i] for z in ids for i in mesh['zone_faces'][z]]
a=np.array([mesh['nodes'][f[0]] for f in faces]);b=np.array([mesh['nodes'][f[1]] for f in faces]);A=w/.24;B=0;tx=w/2-A*.11;ty=h/2+A*(-.0025)
for _ in range(12):
    mat=np.array([[A,B],[B,-A]]);aa=a@mat.T+[tx,ty];bb=b@mat.T+[tx,ty];delta=bb-aa
    t=np.clip(((q[:,None,:]-aa)*delta).sum(2)/(delta*delta).sum(1),0,1);near=aa+t[:,:,None]*delta;idx=((q[:,None,:]-near)**2).sum(2).argmin(1);world=a[idx]+t[np.arange(len(q)),idx,None]*(b-a)[idx]
    d=np.zeros((2*len(q),4));d[::2,:2]=world;d[::2,2]=1;d[1::2,0]=-world[:,1];d[1::2,1]=world[:,0];d[1::2,3]=1;A,B,tx,ty=np.linalg.lstsq(d,q.reshape(-1),rcond=None)[0]
mat=np.array([[A,B],[B,-A]]);errors=np.linalg.norm((d@np.array([A,B,tx,ty])).reshape(-1,2)-q,axis=1)
csvpath=root/'solver/native_figures_2026-11-10/case05/native_rake_dense_outline4_evidence.csv';rows=[{k.strip():float(v) for k,v in r.items()} for r in csv.DictReader(csvpath.open())];assert len(rows)==504
legend=root/'solver/native_figures_2026-11-10/case05/velocity_native_legend_valid.png';bar=np.asarray(Image.open(legend).convert('RGB')).astype(float);palette=bar[483:1168,70];checks=[]
for r in rows:
    start=mat@np.array([r['x-coordinate'],r['y-coordinate']])+[tx,ty];vec=mat@np.array([r['x-velocity'],r['y-velocity']])*.000075
    # The head interior avoids subpixel-antialiased thin shaft and allows signed-direction verification.
    pos=start+.72*vec;x,y=np.rint(pos).astype(int)
    if not (3<=x<w-3 and 3<=y<h-3):continue
    patch=arr[y-2:y+3,x-2:x+3].reshape(-1,3);chroma=patch.max(1)-patch.min(1);colour=patch[chroma>20]
    hit=len(colour)>0;best_delta=None
    if hit:
        distances=((colour[:,None,:]-palette[None,:,:])**2).sum(2);cidx,bidx=np.unravel_index(distances.argmin(),distances.shape)
        scalar=120*(1-bidx/684);best_delta=abs(scalar-r['velocity-magnitude'])
    checks.append({'native_node':int(r['nodenumber']),'sample_world_m':[r['x-coordinate'],r['y-coordinate']],'predicted_native_head_interior_pixel':pos.tolist(),'signed_uv_prediction_hits_coloured_arrow':hit,'native_point_magnitude':r['velocity-magnitude'],'nearest_native_legend_magnitude_error_m_s':best_delta})
hits=sum(c['signed_uv_prediction_hits_coloured_arrow'] for c in checks);vals=[c['nearest_native_legend_magnitude_error_m_s'] for c in checks if c['signed_uv_prediction_hits_coloured_arrow']]
assert hits/len(checks)>.98
result={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'point_CSV':str(csvpath),'point_CSV_sha256':hashlib.sha256(csvpath.read_bytes()).hexdigest(),'original_dense_CSV_byte_identical':csvpath.read_bytes()==(root/'solver/native_figures_2026-11-10/case05/native_rake_dense_velocity_evidence.csv').read_bytes(),'foil_similarity_fit_median_px':float(np.median(errors)),'world_to_pixel_matrix':mat.tolist(),'world_to_pixel_translation':[tx,ty],'rake_vectors_tested_inside_image':len(checks),'predicted_signed_uv_arrow_head_interior_hits':hits,'hit_fraction':hits/len(checks),'native_palette_magnitude_error_m_s':{'median':float(np.median(vals)),'p95':float(np.quantile(vals,.95)),'max':float(max(vals))},'checks':checks,'limitation':'Image pixel predictions use actual native signed u/v and the recorded 75us scale. Native raster antialiasing/3D-arrow shading and native discrete palette prevent asserting exact scalar recovery from every pixel.'}
(out/'case05_native_dense_raster_vector_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
