"""Read-only numerical calibration of a native black foil outline; never redraw the field."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'data'))
from plot_taskA_mesh import parse_mesh

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--image',required=True);p.add_argument('--mesh',required=True);p.add_argument('--name',required=True);p.add_argument('--axis-aligned',action='store_true');p.add_argument('--initial-camera',nargs=4,type=float,metavar=('CX','CY','WIDTH','HEIGHT'));p.add_argument('--white-hole',action='store_true');p.add_argument('--black-limit',type=int,default=170);p.add_argument('--native-line-width',type=float,default=1);p.add_argument('--native-blue-orange-foil',action='store_true');args=p.parse_args()
    image=ROOT/args.image;mesh=ROOT/args.mesh;rgb=np.asarray(Image.open(image).convert('RGB'));height,width=rgb.shape[:2]
    # On these clean native exports, the only achromatic dark graphic is the native foil outline.
    mask=(rgb.max(2).astype(int)-rgb.min(2).astype(int)<5)&(rgb.max(2)<args.black_limit)
    method='achromatic native black foil-outline pixels'
    if args.native_blue_orange_foil:
        a=rgb.astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];mask=((b>r+80)&(b>g+80))|((r>b+120)&(g>b+20)&(r>g));method='native blue/orange foil boundary pixels, excluding achromatic mesh and green/pink end boundaries'
        if args.initial_camera:
            nn,ff,zz,cc=parse_mesh(mesh);ids=set()
            for name in ['aerofoil_suction','aerofoil_pressure','aerofoil_te']:
                for fi in zz[name]['faces']:ids.update(ff[fi][:2])
            points=np.array([nn[i] for i in ids]);cx,cy,fw,fh=args.initial_camera;ss=min(width/fw,height/fh);xp=points[:,0]*ss+width/2-ss*cx;yp=height/2+ss*cy-points[:,1]*ss
            region=np.zeros_like(mask);pad=12+args.native_line_width;region[max(0,int(yp.min()-pad)):min(height,int(yp.max()+pad)+1),max(0,int(xp.min()-pad)):min(width,int(xp.max()+pad)+1)]=True;mask&=region
    if args.white_hole:
        white=rgb.min(2)>250;region=np.zeros((height,width),bool);stack=[(width//2,height//2)]
        while stack:
            x,y=stack.pop()
            if region[y,x] or not white[y,x]:continue
            allowed=white[y]&~region[y];false=np.where(~allowed[:x])[0];left=int(false[-1]+1) if len(false) else 0
            false=np.where(~allowed[x:])[0];right=int(x+false[0]) if len(false) else width;region[y,left:right]=True
            for ny in [y-1,y+1]:
                if not 0<=ny<height:continue
                available=white[ny,left:right]&~region[ny,left:right];starts=np.where(np.diff(np.r_[False,available].astype(int))==1)[0]
                stack.extend((int(left+sx),ny) for sx in starts)
        if region[0].any() or region[-1].any() or region[:,0].any() or region[:,-1].any():raise ValueError('Native white foil interior leaks to image boundary; no inference made')
        inside=np.zeros_like(region);inside[1:-1,1:-1]=region[1:-1,:-2]&region[1:-1,2:]&region[:-2,1:-1]&region[2:,1:-1];mask=region&~inside;method='boundary pixels of the connected native white solid interior (native coloured cell band encloses it)'
    yy,xx=np.where(mask)
    if len(xx)<100:raise ValueError('Insufficient native black foil pixels; no calibration inferred')
    allpixels=np.column_stack((xx+.5,yy+.5));weights=1-rgb[yy,xx].mean(1)/255
    if args.white_hole:weights=np.ones(len(xx))
    if len(xx)>2400:
        indices=np.random.default_rng(20617209).choice(len(xx),2400,replace=False);pixels=allpixels[indices];weights=weights[indices]
    else:pixels=allpixels
    nodes,faces,zones,counts=parse_mesh(mesh)
    names=['aerofoil_suction','aerofoil_pressure','aerofoil_te']
    if not all(n in zones for n in names):names=['aerofoil-suction','aerofoil-pressure','aerofoil-trail']
    segments=np.array([[nodes[faces[fi][0]],nodes[faces[fi][1]]] for name in names for fi in zones[name]['faces']])
    world=segments.reshape(-1,2);s=(allpixels[:,0].max()-allpixels[:,0].min())/np.ptp(world[:,0]);bx=allpixels[:,0].min()-s*world[:,0].min();by=allpixels[:,1].max()+s*world[:,1].min();params=np.array([s,0,bx,by])
    if args.initial_camera:
        cx,cy,fw,fh=args.initial_camera;s=min(width/fw,height/fh);params=np.array([s,0,width/2-s*cx,height/2+s*cy])
    def mapped(points,q):
        a,b,bx,by=q;x=points[...,0];y=points[...,1]
        return np.stack((a*x+b*y+bx,b*x-a*y+by),axis=-1)
    def correspondence(q):
        edges=mapped(segments,q);start=edges[:,0];delta=edges[:,1]-start;relative=pixels[:,None,:]-start
        t=np.clip((relative*delta).sum(2)/(delta*delta).sum(1),0,1);closest=start+t[:,:,None]*delta
        dist=((pixels[:,None,:]-closest)**2).sum(2);which=dist.argmin(1);u=t[np.arange(len(pixels)),which]
        return segments[which,0]+u[:,None]*(segments[which,1]-segments[which,0])
    for iteration in range(150):
        q=correspondence(params);design=np.zeros((len(q)*2,4));target=pixels.reshape(-1)
        design[0::2,0]=q[:,0];design[0::2,1]=q[:,1];design[0::2,2]=1
        design[1::2,0]=-q[:,1];design[1::2,1]=q[:,0];design[1::2,3]=1
        w=np.repeat(np.sqrt(weights),2)
        if args.axis_aligned:
            fitted=np.linalg.lstsq(design[:,[0,2,3]]*w[:,None],target*w,rcond=None)[0];new=np.array([fitted[0],0,fitted[1],fitted[2]])
        else:new=np.linalg.lstsq(design*w[:,None],target*w,rcond=None)[0]
        if np.max(np.abs(new-params))<1e-8:params=new;break
        params=new
    q=correspondence(params);pred=mapped(q,params);error=np.linalg.norm(pred-pixels,axis=1);scale=math.hypot(params[0],params[1]);rotation=math.degrees(math.atan2(params[1],params[0]))
    matrix=np.array([[params[0],params[1]],[params[1],-params[0]]]);inverse=np.linalg.inv(matrix);offset=params[2:]
    pixel_corners=np.array([[0,0],[width,0],[width,height],[0,height]]);worldcorners=(pixel_corners-offset)@inverse.T
    # Independent free-affine fit is a diagnostic only. It is never used to stretch a native image.
    affine=np.linalg.lstsq(np.column_stack((q,np.ones(len(q)))),pixels,rcond=None)[0].T;sv=np.linalg.svd(affine[:,:2],compute_uv=False)
    result={'native_source':{'path':str(image),'sha256':sha(image),'pixels':[width,height]},'mesh':{'path':str(mesh),'sha256':sha(mesh),'foil_face_count':len(segments)},
            'method':'Match '+method+' to the exact original mesh boundary segments using iterative closest points and an equal-scale similarity. No data layer is edited, traced into a final figure or generated.',
            'selected_outline_pixel_count':len(pixels),'all_black_outline_pixel_count':len(allpixels),'iterations':iteration+1,'axis_aligned_native_camera_constraint':args.axis_aligned,'native_hardcopy_line_width_pixels':args.native_line_width,'calibration_acceptance_tolerance_pixels':max(1.5,args.native_line_width/2+.9),
            'world_to_pixel_matrix':matrix.tolist(),'world_to_pixel_offset':offset.tolist(),'scale_pixels_per_m':scale,'native_camera_roll_deg':rotation,
            'pixel_corner_world_coordinates_m':worldcorners.tolist(),'outline_fit_error_pixels':{'weighted_rms':float(np.sqrt(np.average(error**2,weights=weights))),'median':float(np.median(error)),'p95':float(np.quantile(error,.95)),'max':float(error.max())},
            'free_affine_diagnostic':{'singular_values_pixels_per_m':sv.tolist(),'relative_axis_scale_difference':float(sv.max()/sv.min()-1),'matrix':affine.tolist(),'not_for_image_placement':True},
            'status':'Provisional numeric calibration; independent inspection of the black mask and original native outline is required before composition.',
            'script_sha256':sha(Path(__file__))}
    (OUT/f'{args.name}_calibration.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:result[k] for k in ['scale_pixels_per_m','native_camera_roll_deg','outline_fit_error_pixels','free_affine_diagnostic']},indent=2))

if __name__=='__main__':main()
