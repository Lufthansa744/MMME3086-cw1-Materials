"""Bind independent native-artwork acceptance to final delivery bytes, not intermediate candidates."""
from pathlib import Path
import json,hashlib,re
from pypdf import PdfReader
root=Path(__file__).resolve().parents[2];out=root/'review/native_figures_2026-11-10';delivery=root/'report/native_fluent_2026-11-10'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
renders=json.loads((out/'final_delivery_render_audit.json').read_text());layers=json.loads((out/'native_pdf_layer_audit.json').read_text());byfig={r['figure']:r for r in layers}
manifestpath=root/'solver/native_figures_2026-11-10/FINAL_NATIVE_MANIFEST.json';manifest=json.loads(manifestpath.read_text())
base=manifestpath.parent;nativefiles=[]
for records in manifest['selected_artifacts'].values():nativefiles+=records
nativefiles+=manifest['native_legend_donors']
for r in nativefiles:assert sha(base/r['path'])==r['sha256']
sources=[]
for r in manifest['source_hash_verification']:
    p=Path(r['Path']);h=sha(p);assert h==r['Before'].lower()==r['After'].lower() and r['Unchanged'];sources.append({'path':str(p),'sha256':h,'unchanged':True})
mesh=root/'solver/aligned_taskA/taskA_baseline.msh';assert sha(mesh)=='614e5eee90b0cadab2ba590711e98d79e9f02555f64c6881780ad099e02293be'
logs=list((base/'logs').glob('*.transcript'));text='\n'.join(p.read_text(errors='replace') for p in logs)
for forbidden in ['/solve/iterate','/solve/initialize','/file/write-case-data']:assert forbidden not in text,forbidden
assert 'case03_aligned_final.cas.h5' in text and 'case05_verified_final.cas.h5' in text
assert '/display/save-picture' in text and 'driver/png' in text
reasons={
2:'Native full/local mesh images match actual original connectivity and equal world scale. Seven boundary labels, 1000/150mm dimensions, outlet clearance, white callout pads and complete bottom xlabel independently viewed at actual print size.',
4:'Native Case3 main velocity arrows and fixed-length trailing-edge inset retain the attachment panel boxes. Actual arrow-tail loci support cell-centred placement. Native bold foil outlines and all titles/axes/legend are legible with no observed annotation/text collision.',
5:'Native node-values-off cellwise yplus scope is exactly the103 foil-neighbour cells. Actual polygon coverage and all103 centre colours agree with native legend bands/original yplus values. Red five-cell bracket uses independently checked actual cell IDs/extents; all leaders and text are clear.',
6:'Native enhanced-RSM rake vectors, native full-foil yplus and actual equal-scale max-cell inset match the stacked attachment form. Dense grid requests540 positions with36 solid positions excluded and504 fluid samples. Native black outlines fix low-contrast geometry; thin-layer colour is resolved honestly in the inset, without inflating cells.'}
record={'overall':'ACCEPT','scope':'Final standalone replacement artwork Figures2,4,5,6 only; not a newly compiled report','date':'2026-11-10','reviewer_role':'Independent read-only review agent; no Fluent operation and no local TeX compilation','native_identity':{'fluent':'2022 R2 build10212 native graphics-enabled SavePicture PNG','manifest':str(manifestpath),'manifest_sha256':sha(manifestpath),'selected_native_files_and_legend_hashes_verified':len(nativefiles),'source_case_data':sources,'baseline_mesh_sha256':sha(mesh),'no_iteration_reinitialisation_or_source_caseData_write_commands':True,'logs':[{'path':str(p),'sha256':sha(p)} for p in logs]},'presentation_type':'Losslessly embedded Fluent-native raster scientific layers plus post-export vector axes, typography, dimensions, callouts and legend labels. These PDFs are not all-vector field graphics or unedited whole-window native files.','review_evidence':['native_pdf_layer_audit.json','final_delivery_render_audit.json','case03_native_cell_image_audit.json','case03_native_palette_audit.json','case03_native_vector_origin_audit.json','case03_annotation_bracket_audit.json','case05_native_dense_inset_rake_audit.json','case05_native_dense_raster_vector_audit.json','taskA_native_final_mesh_pixel_audit.json','taskA_attachment_identity.json','reference_internal_rectangles.json'],'limitations':['Full enhanced wall-layer colours are not individually resolved in the full-foil print view; actual scale is preserved and colours are resolved in the equal-scale inset.','Rake CSV fields and rendered vector evaluation are not asserted to share identical node/cell interpolation semantics. Raster arrow-hit tests provide geometry/sign consistency support, not exact verification of every rendered vector value.','540 is the number of requested rake positions;504 is the actual fluid-sample count, not a certified count of visible clipped glyphs.','Native graphics changes do not change earlier convergence qualifications, spatial-sensitivity findings or physical-validation limitations.','No local TeX report compilation was performed. Final Mac Overleaf integration, captions/page breaks and report page count require permitted Overleaf compilation.']}
for n,rr in zip([2,4,5,6],renders):
    p=Path(rr['delivery_PDF']);r=byfig[n];assert sha(p)==rr['sha256']==r['PDF_sha256']
    assert p.read_bytes()==Path(r['PDF']).read_bytes() and rr['final_data_print300_pixel_identical_to_independent_render']
    page=PdfReader(p).pages[0];size=[float(page.mediabox.width),float(page.mediabox.height)];extracted=page.extract_text()
    if n==2:
        for label in ['inlet','outlet','wall_top','wall_bottom','aerofoil_suction','aerofoil_pressure','aerofoil_te']:assert label in extracted
    if n==4:assert 'Cell-centred' in extracted
    if n==6:assert 'rake-sampled' in extracted and 'Cell-centred' not in extracted
    record[f'fig{n}']={'accepted':True,'decision':'ACCEPT','path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'size_pt':size,'size_mm':[x*25.4/72 for x in size],'reference_box_match':True,'data_source_copy':r['PDF'],'delivery_data_bytes_identical':True,'native_scientific_layers':r['native_image_layers'],'final_current_bytes_independently_rendered':rr['independent_render'],'render_matches_visually_reviewed_print300_pixel_for_pixel':True,'annotations_and_print':'ACCEPT: independently viewed current-byte print rendering; readable glyphs, no observed annotation/text overlap and no clipped text','reason':reasons[n]}
caption=delivery/'figure6_caption.tex';s=caption.read_text();clean=re.sub(r'\\[a-zA-Z]+',' ',s);count=len(re.findall(r"[\w]+(?:[.'’-][\w]+)*",clean));assert count<=150
for token in ['158.85','5.233','413','0.147','6.586','57','354']:assert token in s
record['figure6_caption']={'path':str(caption),'sha256':sha(caption),'accepted':True,'words_including_numeric_math_tokens':count,'limit':150,'actual_force_yplus_counts_verified':True,'not_compiled':True}
(out/'final_acceptance.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'overall':record['overall'],'figures':[{k:v for k,v in record[f'fig{n}'].items() if k in ['decision','path','sha256','size_mm','bytes']} for n in [2,4,5,6]],'caption_words':count},indent=2))
