from pathlib import Path
import json,hashlib,subprocess,math
from PIL import Image,ImageChops
from pypdf import PdfReader
import pdfplumber
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent;delivery=root/'report/native_fluent_2026-11-10-exact-cells'
p=delivery/'fig05_rsm_yplus.pdf';sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
exact=json.loads((out/'exact_five_cells.json').read_text());xmin,xmax,ymin,ymax=-.008,.108,-.017470596533814834,.020529403466185165
px=lambda xx:38.025+(xx-xmin)/.116*356.265
py=lambda yy:42.705+(yy-ymin)/.038*116.7075
expected={r['cell_id']:[[px(x),187.2-py(y)] for x,y in r['vertices_m']] for r in exact['ordered_exact_cells']}
with pdfplumber.open(p) as doc:
 page=doc.pages[0];assert [page.width,page.height]==[468,187.2]
 curves=[r for r in page.curves if r.get('stroking_color') and len(r['stroking_color'])>=3 and r['stroking_color'][0]>.5 and r['stroking_color'][1]<.2 and r['stroking_color'][2]<.2]
 matches=[]
 for r in curves:
  pts=r['pts'];unique=[]
  for point in pts:
   if not any(math.dist(point,a)<.0001 for a in unique):unique.append(point)
  if len(unique)!=3:continue
  errors={cid:max(min(math.dist(v,u) for u in unique) for v in vertices) for cid,vertices in expected.items()};cid=min(errors,key=errors.get)
  assert errors[cid]<.01,(cid,errors[cid],r)
  matches.append({'cell_id':cid,'actual_red_pdf_vertices_top_origin_pt':unique,'maximum_vertex_error_pt':errors[cid],'stroke_width_pt':r['linewidth']})
 assert len(matches)==5 and {r['cell_id'] for r in matches}==set(expected)
 text=page.extract_text();assert '5 cells' not in text
 outside=[c for c in page.chars if c['x0']<-.1 or c['x1']>468.1 or c['top']<-.1 or c['bottom']>187.3];assert not outside
old=root/'report/native_fluent_2026-11-10-centered/fig05_rsm_yplus.pdf'
with pdfplumber.open(old) as doc:
 oldpage=doc.pages[0]
 def ticks(pg):return [(w['text'],round(w['x0'],4),round(w['top'],4)) for w in pg.extract_words() if (w['x1']<36 or 144<w['top']<160) and w['text'] in ['-10','−10','0','10','20','40','60','80','100']]
 assert ticks(oldpage)==ticks(page)
oldimages=[im.image.convert('RGB') for im in PdfReader(old).pages[0].images];newimages=[im.image.convert('RGB') for im in PdfReader(p).pages[0].images]
assert len(oldimages)==len(newimages) and all(a.size==b.size and ImageChops.difference(a,b).getbbox() is None for a,b in zip(oldimages,newimages))
poppler='C:/Users/A320N/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe';prefix=out/'fig05_independent300'
subprocess.run([poppler,'-r','300','-singlefile','-png',str(p),str(prefix)],check=True,capture_output=True)
render=Image.open(str(prefix)+'.png').convert('RGB');preview=Image.open(delivery/'fig05_rsm_yplus_print300.png').convert('RGB');assert render.size==preview.size and ImageChops.difference(render,preview).getbbox() is None
record={'PDF':str(p),'sha256':sha(p),'red_triangle_annotations':matches,'false_positive_cells':0,'false_negative_cells':0,'native_RGB_all_unchanged':True,'axis_tick_text_and_positions_unchanged':True,'physical_box_pt':[468,187.2],'glyphs_outside_canvas':0,'independent_render':str(prefix)+'.png','current_PDF_render_matches_delivery_preview':True,'original_bracket_removed':True}
(out/'final_pdf_identity_audit.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
