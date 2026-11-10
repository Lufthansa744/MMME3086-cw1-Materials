"""Independent read-only checks of final delivered centered artwork."""
from pathlib import Path
import hashlib,json,subprocess,re
from PIL import Image,ImageChops
import pdfplumber
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent
d=root/'report/native_fluent_2026-11-10-centered';old=root/'report/native_fluent_2026-11-10'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names={2:'fig02_mesh_bc',4:'fig04_rsm_vectors',5:'fig05_rsm_yplus',6:'fig06_enhanced_combined'}
poppler='C:/Users/A320N/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
results=[]
for n,name in names.items():
 p=d/(name+'.pdf');data=root/'data/native_figures_2026-11-10-centered'/p.name
 assert p.read_bytes()==data.read_bytes()
 if n in [2,4]:assert p.read_bytes()==(old/p.name).read_bytes()
 prefix=out/(name+'_independent300')
 subprocess.run([poppler,'-r','300','-singlefile','-png',str(p),str(prefix)],check=True,capture_output=True)
 im=Image.open(str(prefix)+'.png').convert('RGB');shown=Image.open(d/(name+'_print300.png')).convert('RGB')
 assert im.size==shown.size and ImageChops.difference(im,shown).getbbox() is None
 results.append({'figure':n,'delivery_PDF':str(p),'sha256':sha(p),'independent_render':str(prefix)+'.png','final_data_print300_pixel_identical_to_independent_render':True})
# Check the actual extracted final tick positions against the NEW world transforms.
checks=[]
with pdfplumber.open(d/'fig06_enhanced_combined.pdf') as doc:
 words=doc.pages[0].extract_words();ticks=[w for w in words if 120<w['top']<135 and w['text'] in ['−50','-50','0','50','100','150','200']]
 assert len(ticks)==5,ticks
 for value in [-50,0,50,100,150]:
  w=next(w for w in ticks if w['text'].replace('−','-')==str(value));expected=49.14+(value/1000+.07)/.24*355.68
  assert abs((w['x0']+w['x1'])/2-expected)<.1
 checks.append({'figure':6,'actual_A_ticks':ticks,'correct_world_positions':True})
with pdfplumber.open(d/'fig05_rsm_yplus.pdf') as doc:
 words=doc.pages[0].extract_words();ticks=[w for w in words if w['x1']<36 and w['text'] in ['−10','-10','0','10','20','−20','-20']]
 assert len(ticks)==4,ticks
 for value in [-10,0,10,20]:
  w=next(w for w in ticks if w['text'].replace('−','-')==str(value));expected=187.2-(42.705+(value/1000+.017470596533814834)/.038*116.7075)
  # Font optical centre can differ slightly from the typographic baseline.
  assert abs((w['top']+w['bottom'])/2-expected)<1.5
 checks.append({'figure':5,'actual_y_ticks':ticks,'correct_world_positions':True})
# Every pixel below the A-panel/inter-panel heading is unchanged in Figure6.
new=Image.open(d/'fig06_enhanced_combined_print300.png').convert('RGB');previous=Image.open(old/'fig06_enhanced_combined_print300.png').convert('RGB')
assert new.size==previous.size
roi=(0,650,new.width,new.height)
assert ImageChops.difference(new.crop(roi),previous.crop(roi)).getbbox() is None
(out/'final_delivery_render_audit.json').write_text(json.dumps(results,indent=2))
(out/'axes_and_preserved_BC_audit.json').write_text(json.dumps({'ticks':checks,'figure6_preserved_BC_pixel_ROI':roi,'BC_pixels_identical':True},indent=2))
print('PASS: four current delivery PDFs independently rendered, preview identical; new tick coordinates correct; B/C unchanged.')
