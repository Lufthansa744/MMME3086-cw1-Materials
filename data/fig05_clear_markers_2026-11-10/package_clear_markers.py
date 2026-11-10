"""Package the accepted Fig5 markers; preserve Figures2/4/6 byte-for-byte."""
from pathlib import Path
import hashlib, json, shutil
from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).resolve().parent
OLD = ROOT / 'report/native_fluent_2026-11-10-exact-cells'
OUT = ROOT / 'report/native_fluent_2026-11-10-clear-markers'
OUT.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(im):
    im=im.convert('RGB')
    return hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()

records=[]
for n,name in [(2,'fig02_mesh_bc'),(4,'fig04_rsm_vectors'),(5,'fig05_rsm_yplus'),(6,'fig06_enhanced_combined')]:
    assets=[]
    for suffix in ['.pdf','.png','_print300.png']:
        src=(DATA if n==5 else OLD)/(name+suffix)
        dst=OUT/src.name
        shutil.copyfile(src,dst)
        assert sha(src)==sha(dst)
        assets.append({'path':str(dst.relative_to(ROOT)),'sha256':sha(dst),'bytes':dst.stat().st_size,'source':str(src.relative_to(ROOT)),'byte_identical_to_previous_exact_cells':n!=5})
    records.append({'figure':n,'assets':assets})

audit=json.loads((DATA/'fig05_native_composition_audit.json').read_text(encoding='utf-8'))
native=Path(audit['native_layers'][0]['path'])
source_rgb=rgb(Image.open(native))
pdf=OUT/'fig05_rsm_yplus.pdf'
pdf_image_hashes=[rgb(x.image) for x in PdfReader(pdf).pages[0].images]
assert source_rgb in pdf_image_hashes
page=PdfReader(pdf).pages[0]
assert [float(page.mediabox.width),float(page.mediabox.height)]==[468.,187.2]
annotation=next(x for x in audit['native_layers'] if x.get('role')=='Non-native annotation only')
assert annotation['cell_ids']==[7588,7316,69,7251,2573]
manifest={'scope':'Figure5 annotation only: five visible numbered red circles and precise centroid leaders. Native science RGB, centered world window and all physical sizes unchanged. Figures2/4/6 copied byte-for-byte. All previous versions preserved.',
          'external_annotation_disclosure':'Five filled red callout circles with white digits and leaders/arrowheads are post-annotations. Opaque circles cover gray mesh background only, never native coloured wall-cell fills. Scientific raster RGB remains losslessly embedded and unchanged.',
          'figures':records,'figure5_source_rgb_sha256':source_rgb,'figure5_embedded_image_rgb_sha256':pdf_image_hashes,
          'figure5_native_image_losslessly_preserved':True,'figure5_annotation':annotation,
          'generator':{'path':str((DATA/'compose_clear_markers.py').relative_to(ROOT)),'sha256':sha(DATA/'compose_clear_markers.py')},
          'package_script':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':sha(Path(__file__))},
          'prior_fig05_pdf_sha256':sha(OLD/'fig05_rsm_yplus.pdf')}
for dest in [DATA/'clear_markers_annotation_audit.json',OUT/'native_assets_manifest.json']:
    dest.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
shutil.copyfile(DATA/'fig05_native_composition_audit.json',OUT/'fig05_native_composition_audit.json')
shutil.copyfile(DATA/'fig05_rsm_yplus_print96.png',OUT/'fig05_rsm_yplus_print96.png')
print(json.dumps({'pdf':str(pdf),'sha256':sha(pdf),'native_RGB_unchanged':True}))
