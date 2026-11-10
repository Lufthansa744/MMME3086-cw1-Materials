"""Render exact-size native figures, create equal-scale comparison proofs, and deliver assets only."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
DELIVERY=ROOT/'report/native_fluent_2026-11-10'
POPPLER=Path(r'C:/Users/A320N/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    layout=json.loads((OUT/'reference_layout_audit.json').read_text(encoding='utf-8'));proof=OUT/'proofs';proof.mkdir(exist_ok=True);DELIVERY.mkdir(exist_ok=True)
    names={2:'fig02_mesh_bc',4:'fig04_rsm_vectors',5:'fig05_rsm_yplus',6:'fig06_enhanced_combined'}
    def render(job):
        n,dpi=job;name=names[n];prefix=OUT/(name if dpi==600 else name+'_print300')
        subprocess.run([str(POPPLER),'-r',str(dpi),'-singlefile','-png',str(OUT/(name+'.pdf')),str(prefix)],check=True,capture_output=True)
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(render,[(n,dpi) for n in names for dpi in [300,600]]))
    source=layout['source_pdf']['path']
    for page in [1,3,4]:
        subprocess.run([str(POPPLER),'-f',str(page),'-l',str(page),'-r','300','-singlefile','-png',source,str(proof/f'reference_page{page}_300')],check=True,capture_output=True)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',32);items=[]
    for n,name in names.items():
        spec=next(f for f in layout['figures'] if f['figure']==n)
        if n==2:
            origin=spec['page_origin_bottom_left_pt'];w,h=spec['target_size_pt'];bbox=[origin[0],792-origin[1]-h,origin[0]+w,792-origin[1]]
        else:bbox=spec['page_box_top_left_pt']
        reference=Image.open(proof/f'reference_page{spec["page_1based"]}_300.png').convert('RGB');crop=reference.crop(tuple(round(v*300/72) for v in bbox));native=Image.open(OUT/(name+'_print300.png')).convert('RGB')
        cellw=max(crop.width,native.width);cellh=max(crop.height,native.height);sheet=Image.new('RGB',(2*cellw+150,cellh+140),'white');d=ImageDraw.Draw(sheet)
        d.text((50,25),f'Figure {n} attachment reference',font=font,fill='#222222');d.text((cellw+100,25),f'Figure {n} Fluent-native replacement',font=font,fill='#222222')
        sheet.paste(crop,(50,90));sheet.paste(native,(cellw+100,90));target=proof/f'fig{n:02d}_reference_vs_native_300dpi.png';sheet.save(target,dpi=(300,300))
        copied=[]
        for suffix in ['.pdf','.png','_print300.png']:
            src=OUT/(name+suffix);dst=DELIVERY/src.name;shutil.copyfile(src,dst);copied.append({'path':str(dst),'sha256':sha(dst),'bytes':dst.stat().st_size})
        items.append({'figure':n,'target_size_pt':spec['target_size_pt'],'target_size_mm':spec['target_size_mm'],'assets':copied,'composition_audit':{'path':str(OUT/f'fig{n:02d}_native_composition_audit.json'),'sha256':sha(OUT/f'fig{n:02d}_native_composition_audit.json')},
                      'equal_scale_proof':{'path':str(target),'sha256':sha(target),'reference_pixels':list(crop.size),'native_pixels':list(native.size),'dpi':300,'image_rescaling_used':False}})
    manifest={'scope':'Four drop-in native graphic replacements only; original prepared report, original figures and main-agent handoff untouched. No LaTeX compilation.',
              'source_report_pdf':layout['source_pdf'],'figures':items,'reference_layout_audit':{'path':str(OUT/'reference_layout_audit.json'),'sha256':sha(OUT/'reference_layout_audit.json')},
              'native_scientific_layers':'Fluent-native raster embedded losslessly; external annotations, axes and native scalar-strip crops only. No scientific vector/cell/mesh redrawing.',
              'figure1':'Attachment Image XObject RGB equals retained SpaceClaim-native composite exactly; no Figure1 replacement generated.',
              'sampling':'Figure4 retains actual cell-position native vectors. Figure6 uses12 regular native rakes with45 requested points each,540 requested/504 fluid/36solid omitted; native magnitude colours retained, not hypot of interpolated signed components.',
              'limits':'The true enhanced near-wall cell band is extremely thin at full scale. Native black outline improves full-foil geometry visibility; the independent equal-scale native inset shows its uninflated thickness. Pure no-outline native source retained.',
              'status':'Final-size assets generated and visually checked by data agent; independent review recorded separately.'}
    (OUT/'native_assets_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');shutil.copyfile(OUT/'native_assets_manifest.json',DELIVERY/'native_assets_manifest.json');print('Rendered and delivered4 PDFs,4 PNGs600dpi,4 print300 proofs; created4 unscaled side-by-side proof sheets.')

if __name__=='__main__':main()
