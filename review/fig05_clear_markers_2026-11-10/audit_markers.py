"""Inspect actual PDF annotation primitives independently of producer metadata."""
from pathlib import Path
import json,hashlib,math,subprocess,sys
from PIL import Image,ImageChops
from pypdf import PdfReader
import pdfplumber
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent
folder=Path(sys.argv[1]) if len(sys.argv)>1 else root/'report/native_fluent_2026-11-10-clear-markers'
p=folder/'fig05_rsm_yplus.pdf';old=root/'report/native_fluent_2026-11-10-exact-cells/fig05_rsm_yplus.pdf'
sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
raw=json.loads((root/'review/fig05_exact_five_cells_2026-11-10/exact_five_cells.json').read_text())
transform=lambda xy:(38.025+(xy[0]+.008)/.116*356.265,187.2-(42.705+(xy[1]+.017470596533814834)/.038*116.7075))
expected={r['cell_id']:transform(tuple(sum(q[j] for q in r['vertices_m'])/3 for j in [0,1])) for r in raw['ordered_exact_cells']}
red=lambda rgb:rgb and len(rgb)>=3 and rgb[0]>.5 and rgb[1]<.2 and rgb[2]<.2
with pdfplumber.open(p) as d:
 pg=d.pages[0];assert [pg.width,pg.height]==[468,187.2]
 primitives={'lines':[x for x in pg.lines if red(x.get('stroking_color'))],'curves':[x for x in pg.curves if red(x.get('stroking_color')) or red(x.get('non_stroking_color'))]}
 hits=[]
 for cid,tip in expected.items():
  matches=[]
  for line in primitives['lines']:
   pts=[(line['x0'],line['top']),(line['x1'],line['bottom']),(line['x0'],line['bottom']),(line['x1'],line['top'])]
   # Native line endpoints are also directly available in pts; use these where present.
   pts=line.get('pts',pts);error=min(math.dist(tip,q) for q in pts)
   if error<.01:matches.append({'endpoint_error_pt':error,'points':pts,'width_pt':line['linewidth']})
  hits.append({'cell_id':cid,'actual_mesh_centroid_pdf_pt':tip,'matching_red_leaders':matches})
 outside=[c for c in pg.chars if c['x0']<-.1 or c['x1']>468.1 or c['top']<-.1 or c['bottom']>187.3];assert not outside
 text=pg.extract_text()
 assert all(r['matching_red_leaders'] for r in hits)
 # Isolate five long shafts; arrowhead wings are short and excluded.
 shafts=[line for line in primitives['lines'] if len(line.get('pts',[]))==2 and math.dist(*line['pts'])>10]
 assert len(shafts)==5
 def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 for i,a in enumerate(shafts):
  for b in shafts[i+1:]:
   p0,p1=a['pts'];q0,q1=b['pts'];assert not (orient(p0,p1,q0)*orient(p0,p1,q1)<0 and orient(q0,q1,p0)*orient(q0,q1,p1)<0)
 circles=[r for r in primitives['curves'] if r.get('fill') and 7<r['width']<9 and 7<r['height']<9]
 assert len(circles)==5
 numbers=[]
 for circle in sorted(circles,key=lambda r:r['x0']):
  chars=[c for c in pg.chars if circle['x0']<(c['x0']+c['x1'])/2<circle['x1'] and circle['top']<(c['top']+c['bottom'])/2<circle['bottom']]
  assert len(chars)==1
  numbers.append({'text':chars[0]['text'],'font_size_pt':chars[0]['size'],'circle_diameter_mm':circle['width']*25.4/72})
 assert [n['text'] for n in numbers]==list('12345')
 # Embedded field/legend RGB must be identical to previously accepted source.
 images=[im.image.convert('RGB') for im in PdfReader(p).pages[0].images];oldimages=[im.image.convert('RGB') for im in PdfReader(old).pages[0].images]
 assert len(images)==len(oldimages) and all(a.size==b.size and ImageChops.difference(a,b).getbbox() is None for a,b in zip(images,oldimages))
 poppler='C:/Users/A320N/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
 for dpi in [300,96]:
  prefix=out/f'fig05_independent{dpi}';subprocess.run([poppler,'-r',str(dpi),'-singlefile','-png',str(p),str(prefix)],check=True,capture_output=True)
 rendered=Image.open(out/'fig05_independent300.png').convert('RGB');preview=Image.open(folder/'fig05_rsm_yplus_print300.png').convert('RGB');assert rendered.size==preview.size and ImageChops.difference(rendered,preview).getbbox() is None
 record={'PDF':str(p.resolve()),'sha256':sha(p),'physical_box_pt':[468,187.2],'physical_box_mm':[165.1,66.04],'actual_tip_checks':hits,'five_non_crossing_leader_shafts':True,'false_positive_cells':0,'false_negative_cells':0,'numbered_circle_checks':numbers,'native_RGB_unchanged':True,'glyphs_outside_canvas':0,'current_bytes_independently_rendered':True,'preview_matches_independent_render':True,'actual_red_primitives':primitives,'extracted_text':text}
 (out/'PDF_marker_identity_audit.json').write_text(json.dumps(record,indent=2));print(json.dumps({k:v for k,v in record.items() if k not in ['actual_red_primitives','extracted_text']},indent=2))

