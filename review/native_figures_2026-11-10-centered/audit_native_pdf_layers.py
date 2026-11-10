"""Independent final PDF physical-box, glyph and lossless-native-layer checks."""
from pathlib import Path
import json,hashlib,sys
from pypdf import PdfReader
import pdfplumber
from PIL import Image
root=Path(__file__).resolve().parents[2];folder=root/'data/native_figures_2026-11-10-centered';out=root/'review/native_figures_2026-11-10-centered'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rawsha=lambda im:hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
expected={2:[453.536,209.7604],4:[468.,184.275],5:[468.,187.2],6:[468.,405.35433071]}
figures=[int(x) for x in sys.argv[1:]] if len(sys.argv)>1 else [2,4,5,6]
results=[]
for number in figures:
    audit=folder/f'fig{number:02d}_native_composition_audit.json'
    if not audit.exists():continue
    r=json.loads(audit.read_text());p=Path(r['path']);assert sha(p)==r['sha256'];doc=PdfReader(p);assert len(doc.pages)==1
    page=doc.pages[0];box=[float(page.mediabox.width),float(page.mediabox.height)];assert max(abs(box[j]-expected[number][j]) for j in [0,1])<.02
    text=page.extract_text();assert '\x00' not in text and '\ufffd' not in text
    embedded=[im.image.convert('RGB') for im in page.images];imagechecks=[]
    for layer in r['native_layers']:
        if 'path' in layer:
            source=Path(layer['path']);assert sha(source)==layer['sha256']
            assert 'solver/native_figures_2026-11-10' in str(source).replace('\\','/')
            original=Image.open(source).convert('RGB');kind='original Fluent PNG'
        elif 'output' in layer:
            source=Path(layer['output']);assert sha(source)==layer['sha256'];original=Image.open(source).convert('RGB');kind='exact native donor colour-strip crop'
            donor=Image.open(layer['native_donor']).convert('RGB');assert sha(layer['native_donor'])==layer['native_donor_sha256'];crop=donor.crop(tuple(layer['crop_box_pixels']))
            if layer['rotation']!='none':crop=crop.transpose(Image.Transpose.ROTATE_270)
            assert rawsha(crop)==rawsha(original)
        else:continue
        matches=[im for im in embedded if im.size==original.size and rawsha(im)==rawsha(original)]
        assert matches,(number,str(source),'no lossless matching PDF image')
        imagechecks.append({'source':str(source),'kind':kind,'source_sha256':sha(source),'embedded_RGB_exactly_matches':True,'pixels':original.size})
    with pdfplumber.open(p) as d:
        pg=d.pages[0];outside=[c for c in pg.chars if c['x0']<-.1 or c['x1']>box[0]+.1 or c['top']<-.1 or c['bottom']>box[1]+.1]
        assert not outside,(number,outside)
    fonts=[]
    for key,obj in page['/Resources'].get('/Font',{}).items():
        f=obj.get_object();descriptor=f.get('/FontDescriptor');descriptor=descriptor.get_object() if descriptor else {}
        fonts.append({'resource':str(key),'font':str(f.get('/BaseFont')),'embedded':any(k in descriptor for k in ['/FontFile','/FontFile2','/FontFile3'])})
    assert any(f['embedded'] for f in fonts)
    results.append({'figure':number,'PDF':str(p),'PDF_sha256':sha(p),'physical_box_pt':box,'matches_current_attachment_printed_box':True,'all_native_source_RGB_embedded_losslessly':True,'native_image_layers':imagechecks,'text_has_no_NUL_or_replacement_glyph':True,'glyphs_outside_canvas':0,'fonts':fonts,'limitation':'Programmatic source/PDF-layer and box checks only; independent visual inspection still required for overlap/legibility and final image acceptance.'})
(out/'native_pdf_layer_audit.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(json.dumps([{k:v for k,v in r.items() if k not in ['fonts','native_image_layers']} for r in results],indent=2))

