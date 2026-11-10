"""Compare actual cell-centre native pixels to the native legend donor, without recolouring."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'review/native_figures_2026-11-10'
r=json.loads((out/'case03_native_cell_image_audit.json').read_text())
legend=root/'solver/native_figures_2026-11-10/case03/yplus_native_legend_valid.png'
im=np.asarray(Image.open(legend).convert('RGB')).astype(int)
mask=(im.max(2)-im.min(2)>20)&(im.min(2)<245)
runs=[]
for x in range(200):
    yy=np.flatnonzero(mask[:,x]);groups=np.split(yy,np.where(np.diff(yy)>1)[0]+1)
    if groups:
        g=max(groups,key=len)
        if len(g):runs.append((len(g),x,int(g[0]),int(g[-1])))
longest=max(x[0] for x in runs);best=[x for x in runs if x[0]==longest]
length,x,top,bottom=best[len(best)//2];assert length>500
bar=im[top:bottom+1,x];palette={}
for j,c in enumerate(bar):palette.setdefault(tuple(c),[]).append(j)
checks=[]
for p in r['cell_controls']:
    c=tuple(p['native_center_RGB']);assert c in palette,c
    ys=palette[c];low=180*(1-(max(ys)+1)/length);high=180*(1-min(ys)/length)
    tol=180/length*2
    ok=low-tol<=p['yplus']<=high+tol
    assert ok,(p['cell_id'],p['yplus'],low,high)
    checks.append({'cell_id':p['cell_id'],'raw_yplus':p['yplus'],'native_RGB':c,'same_colour_native_legend_value_interval':[low,high],'agrees_with_legend_band':ok})
result={'field_image_sha256':r['native_sha256'],'native_legend':str(legend),'native_legend_sha256':hashlib.sha256(legend.read_bytes()).hexdigest(),'legend_sample_column':x,'legend_sample_top_bottom':[top,bottom],'legend_unique_colours':len(palette),'field_source_cell_count':103,'native_103_cell_colours_match_original_yplus_via_independent_native_legend':True,'checks':checks,'precision_limitation':'Native banded palette is quantized; this verifies the displayed value falls in the correct native legend band, not more precision than the native display supports.'}
(out/'case03_native_palette_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
