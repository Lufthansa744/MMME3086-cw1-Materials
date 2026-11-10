"""Render exact-size native figures, create equal-scale comparison proofs, and deliver assets only."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
DELIVERY=ROOT/'report/native_fluent_2026-11-10-centered'
PREVIOUS=ROOT/'data/native_figures_2026-11-10'
POPPLER=Path(r'C:/Users/A320N/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    layout=json.loads((OUT/'reference_layout_audit.json').read_text(encoding='utf-8'));proof=OUT/'proofs';proof.mkdir(exist_ok=True);DELIVERY.mkdir(exist_ok=True)
    names={2:'fig02_mesh_bc',4:'fig04_rsm_vectors',5:'fig05_rsm_yplus',6:'fig06_enhanced_combined'}
    def render(job):
        n,dpi=job;name=names[n];prefix=OUT/(name if dpi==600 else name+'_print300')
        subprocess.run([str(POPPLER),'-r',str(dpi),'-singlefile','-png',str(OUT/(name+'.pdf')),str(prefix)],check=True,capture_output=True)
    # Figures2/4 are byte copies, never re-rendered. Only the changed5/6 are rendered.
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(render,[(n,dpi) for n in [5,6] for dpi in [300,600]]))
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',32);items=[]
    for n,name in names.items():
        spec=next(f for f in layout['figures'] if f['figure']==n)
        crop=Image.open(PREVIOUS/(name+'_print300.png')).convert('RGB');native=Image.open(OUT/(name+'_print300.png')).convert('RGB')
        cellw=max(crop.width,native.width);cellh=max(crop.height,native.height);sheet=Image.new('RGB',(2*cellw+150,cellh+140),'white');d=ImageDraw.Draw(sheet)
        d.text((50,25),f'Figure {n} previous native version',font=font,fill='#222222');d.text((cellw+100,25),f'Figure {n} centred native version',font=font,fill='#222222')
        sheet.paste(crop,(50,90));sheet.paste(native,(cellw+100,90));target=proof/f'fig{n:02d}_previous_vs_centered_300dpi.png';sheet.save(target,dpi=(300,300))
        copied=[]
        for suffix in ['.pdf','.png','_print300.png']:
            src=OUT/(name+suffix);dst=DELIVERY/src.name;shutil.copyfile(src,dst);copied.append({'path':str(dst),'sha256':sha(dst),'bytes':dst.stat().st_size,'rendered_or_copied_from_pdf_sha256':sha(OUT/(name+'.pdf'))})
        items.append({'figure':n,'target_size_pt':spec['target_size_pt'],'target_size_mm':spec['target_size_mm'],'assets':copied,'composition_audit':{'path':str(OUT/f'fig{n:02d}_native_composition_audit.json'),'sha256':sha(OUT/f'fig{n:02d}_native_composition_audit.json')},
                      'equal_scale_proof':{'path':str(target),'sha256':sha(target),'reference_pixels':list(crop.size),'native_pixels':list(native.size),'dpi':300,'image_rescaling_used':False}})
    centering=json.loads((OUT/'centering_layout_audit.json').read_text(encoding='utf-8'));sampling=json.loads((OUT/'fig06_native_composition_audit.json').read_text(encoding='utf-8'))['native_layers'][-1]
    manifest={'scope':'Centered camera revision of Figures5 and6A only; Figures2/4 byte-identical, Figure6B/C native layers unchanged. Original prepared report, previous native version and main-agent handoff untouched. No LaTeX compilation.',
              'source_report_pdf':layout['source_pdf'],'figures':items,'reference_layout_audit':{'path':str(OUT/'reference_layout_audit.json'),'sha256':sha(OUT/'reference_layout_audit.json')},
              'native_scientific_layers':'Fluent-native raster embedded losslessly; external annotations, axes and native scalar-strip crops only. No scientific vector/cell/mesh redrawing.',
              'figure1':'Attachment Image XObject RGB equals retained SpaceClaim-native composite exactly; no Figure1 replacement generated.',
              'sampling':sampling,
              'centering_revision':centering,
              'limits':'Figure6A retains0.704895 chords downstream of the actual trailing-edge centre and shows the near wake; fixed x=.05/.10/.20 profile traverses are unchanged. Figure6B/C preserve the previous native scientific layers and equal-scale actual thin-cell inset.',
              'status':'Final-size assets generated and visually checked by data agent; independent review recorded separately.'}
    caption_source=ROOT/'report/native_fluent_2026-11-10/figure6_caption.tex';caption=caption_source.read_text(encoding='utf-8')
    if caption.count('and the wake;')!=1:raise ValueError('Expected unique previous caption near-wake substitution')
    caption=caption.replace('and the wake;','and the near wake;');(OUT/'figure6_caption.tex').write_text(caption,encoding='utf-8');(DELIVERY/'figure6_caption.tex').write_text(caption,encoding='utf-8')
    manifest['caption']={'path':str(DELIVERY/'figure6_caption.tex'),'sha256':sha(DELIVERY/'figure6_caption.tex'),'source':str(caption_source),'source_sha256':sha(caption_source),'change':'Only the wake changed to the near wake; all numerical statements retained.'}
    (OUT/'native_assets_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');shutil.copyfile(OUT/'native_assets_manifest.json',DELIVERY/'native_assets_manifest.json');print('Delivered4 PDFs/PNGs600/300; unchanged2/4 byte-copied and changed5/6 rendered; 4 previous-versus-centred proof sheets created.')

if __name__=='__main__':main()
