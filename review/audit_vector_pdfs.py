"""Independent parse/raster comparison of scientific figure PDFs; no TeX invocation."""
from pathlib import Path
import json,re,hashlib,subprocess,xml.etree.ElementTree as ET
from pypdf import PdfReader
import pdfplumber
from PIL import Image,ImageChops,ImageStat
root=Path(__file__).resolve().parents[1];manifest=json.loads((root/'data/print_assets/print_asset_audit.json').read_text())
outdir=root/'review/vector_pdf_renders';outdir.mkdir(exist_ok=True)
poppler=Path('C:/Users/A320N/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
results=[]
for f in manifest['figures']:
    if 'pdf' not in f:continue
    path=Path(f['pdf']['path']);svg=Path(f['source_svg']);png=Path(f['source_png'])
    assert hashlib.sha256(path.read_bytes()).hexdigest()==f['pdf']['sha256']
    assert hashlib.sha256(svg.read_bytes()).hexdigest()==f['svg_sha256']
    assert hashlib.sha256(png.read_bytes()).hexdigest()==f['png_sha256_before']
    doc=PdfReader(path);assert len(doc.pages)==1;page=doc.pages[0]
    assert list(page.mediabox)==list(page.cropbox)
    psize=[float(page.mediabox.width),float(page.mediabox.height)]
    physical=f['actual_print_size_mm'];assert max(abs(psize[j]-physical[j]/25.4*72) for j in [0,1])<1e-4
    fonts=[]
    for key,value in page['/Resources']['/Font'].items():
        font=value.get_object();desc=font.get('/FontDescriptor');desc=desc.get_object() if desc else {}
        fonts.append({'resource':str(key),'basefont':str(font['/BaseFont']),'embedded':any(k in desc for k in ['/FontFile','/FontFile2','/FontFile3'])})
    assert any(x['embedded'] and 'Arial' in x['basefont'] for x in fonts)
    xobj=page['/Resources'].get('/XObject',{})
    assert not any(v.get_object().get('/Subtype')=='/Image' for v in xobj.values())
    src=ET.parse(svg).getroot();source_text=''.join(''.join(e.itertext()) for e in src.iter() if e.tag.split('}')[-1]=='text')
    clean=lambda s:re.sub(r'\s+','',s)
    extracted=page.extract_text();assert clean(source_text)==clean(extracted)
    with pdfplumber.open(path) as pdf:
        chars=pdf.pages[0].chars
        outside=[c for c in chars if c['x0']<-.1 or c['x1']>psize[0]+.1 or c['top']<-.1 or c['bottom']>psize[1]+.1]
        assert not outside
    w,h=f['png_pixels'];prefix=outdir/path.stem
    subprocess.run([str(poppler),'-png','-singlefile','-scale-to-x',str(w),'-scale-to-y',str(h),str(path),str(prefix)],check=True,capture_output=True)
    a=Image.open(png).convert('RGB');b=Image.open(prefix.with_suffix('.png')).convert('RGB');assert a.size==b.size
    diff=ImageChops.difference(a,b);mae=sum(ImageStat.Stat(diff).mean)/3
    result={'figure':f['figure'],'pdf_sha256':f['pdf']['sha256'],'source_svg_sha256':f['svg_sha256'],'source_png_sha256':f['png_sha256_before'],'page_size_pt':psize,'fonts':fonts,'raster_images':0,'extractable_text_matches_all_source_text':True,'text_chars_outside_page':0,'render':str(prefix.with_suffix('.png')),'render_vs_source_png_mean_absolute_RGB_difference_0to255':mae}
    results.append(result)
    print(f"Figure {f['figure']}: text/font/box PASS; PNG comparison RGB MAE {mae:.3f}")
(root/'review/vector_pdf_independent_audit.json').write_text(json.dumps({'figures':results,'limitation':'Source/PDF text, resource, physical box and independent raster comparisons. Small rasterizer/font antialiasing differences are expected. Final report pagination and Overleaf rendering are not checked.'},indent=2),encoding='utf-8')
