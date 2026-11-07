import System, traceback
from System import Enum
out=r'C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\taskA'
f=open(out+r'\meshing_execution.txt','w')
def log(s):
    f.write(str(s)+'\n'); f.flush()
try:
    model=ExtAPI.DataModel.Project.Model
    mesh=model.Mesh
    log('MESHER_PYTHON_OK')
    mesh.PhysicsPreference=MeshPhysicsPreferenceType.CFD
    mesh.SolverPreference=MeshSolverPreferenceType.Fluent
    mesh.ElementSize=Quantity('10 [mm]')
    mesh.GrowthRate=1.05
    log('Basic settings applied')
    body=model.Geometry.GetChildren(DataModelObjectCategory.Body,True)[0]
    log('body '+str(body.Name))
    body_sel=ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    body_sel.Ids=[body.GetGeoBody().Id]
    method=mesh.AddAutomaticMethod()
    method.Name='TaskA All Triangles'
    method.Location=body_sel
    method.Method=MethodType.AllTriAllTet
    foil_ids=[]
    for ns in model.NamedSelections.Children:
        log('named_selection '+ns.Name+' '+str(list(ns.Location.Ids)))
        if ns.Name.startswith('aerofoil_'): foil_ids.extend(list(ns.Location.Ids))
    if len(foil_ids)!=3: raise Exception('Expected exactly 3 foil edges, got '+str(foil_ids))
    sel=ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    sel.Ids=foil_ids
    sizing=mesh.AddSizing()
    sizing.Name='TaskA Aerofoil 2mm Growth 1.05'
    sizing.Location=sel
    sizing.ElementSize=Quantity('2 [mm]')
    sizing.GrowthRate=1.05
    log('GlobalSize='+str(mesh.ElementSize)+' growth='+str(mesh.GrowthRate)+' method='+str(method.Method))
    log('FoilSize='+str(sizing.ElementSize)+' growth='+str(sizing.GrowthRate)+' ids='+str(foil_ids))
    log('MESH_GENERATION_START')
    mesh.GenerateMesh()
    log('MESH_GENERATED nodes='+str(mesh.Nodes)+' elements='+str(mesh.Elements))
    log('NATIVE_EXPORT_START')
    mesh.InternalObject.WriteFluentInputFile(out+r'\taskA_baseline.msh')
    log('NATIVE_FLUENT_EXPORT_COMPLETE')
    ExtAPI.DataModel.Project.Save()
except:
    log(str(__import__('sys').exc_info()))
f.close()


