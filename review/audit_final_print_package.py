"""Read-only final source/asset/ZIP identity audit, without TeX execution."""
from pathlib import Path
import hashlib,json,re,zipfile
root=Path(__file__).resolve().parents[1];prepared=root/'report/prepared'
sha=lambda b:hashlib.sha256(b).hexdigest()
main=prepared/'main.tex';text=main.read_text(encoding='utf-8')
assets=json.loads((prepared/'asset_manifest.json').read_text());assert len(assets)==13
refs=re.findall(r'\\evidence\{[\d.]+mm\}\{([^}]+)\}',text);assert len(refs)==13 and len(set(refs))==13
assert set(refs)=={a['report_asset'] for a in assets}
vector=json.loads((root/'review/vector_pdf_independent_audit.json').read_text())
accepted={Path(v['render']).stem+'.pdf':v['pdf_sha256'] for v in vector['figures']}
assetchecks=[]
for a in assets:
    p=prepared/a['report_asset'];original=root/a['original'];h=sha(p.read_bytes())
    assert h==a['sha256']==sha(original.read_bytes())
    if p.suffix=='.pdf':assert h==accepted[p.name]
    assetchecks.append({'name':p.name,'sha256':h,'source':a['original'],'accepted_vector_identity':p.suffix=='.pdf'})
assert len([a for a in assetchecks if a['accepted_vector_identity']])==11
classhash=sha((prepared/'new-aiaa.cls').read_bytes())
assert classhash=='aead59d4596beda8879a84d074722e16ef3152ee625087d8e25337f1750f759f'
sections=re.findall(r'\\section\{([^}]+)\}',text)
assert sections==['Task A Geometry [16]','Task B Solution and data extraction [34]','Task C Analysis [50]','Task C Boundary Conditions and Results']
assert '\\clearpage' not in text and 'PAGE 1' not in text
assert '{\\footnotesize\\noindent' in text and '\\par}' in text
assert 'near-terminal dissipation history' in text
assert not re.search(r'\\(?:Fill|NA)\b|TODO|working draft',text,re.I)
stack=[]
for m in re.finditer(r'\\(begin|end)\{([^}]+)\}',text):
    if m[1]=='begin':stack.append(m[2])
    else:assert stack.pop()==m[2],m.group()
assert not stack
zpath=root/'report/LIU_Yang_20617209_CFD_Overleaf_Source.zip';members=[]
with zipfile.ZipFile(zpath) as z:
    assert z.testzip() is None
    names=[n for n in z.namelist() if not n.endswith('/')]
    assert len(names)==20 and len(set(names))==20
    assert set(names)==set(refs+['main.tex','new-aiaa.cls','new-aiaa.bst','verified_table.tex','AI_prompt_record.txt','asset_manifest.json','verified_results.json'])
    for n in names:
        b=z.read(n);assert b==(prepared/n).read_bytes()
        members.append({'name':n,'bytes':len(b),'sha256':sha(b),'matches_prepared':True})
result={'main_tex_sha256':sha(main.read_bytes()),'class_sha256':classhash,'class_approved_identity':True,'sections':sections,'artificial_pagebreaks':0,'environment_nesting_balanced':True,'assets':assetchecks,'zip_path':str(zpath),'zip_sha256':sha(zpath.read_bytes()),'zip_member_count':20,'zip_members':members,'status':'Final source/vector/package identity PASS; not compiled','outstanding':['Allowed Overleaf compilation','Actual page/appendix count','Rendered page breaks/overflow/legibility']}
(root/'review/final_print_package_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['assets','zip_members']},indent=2))
