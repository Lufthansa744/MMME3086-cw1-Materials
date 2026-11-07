import traceback
out=GRID_OUTPUT
f=open(out+r'\meshing_execution.txt','w')
def log(s): f.write(str(s)+'\n');f.flush()
try:
    mesh=ExtAPI.DataModel.Project.Model.Mesh
    log('Source aligned baseline; analyst-selected supplemental mesh, not assignment input')
    mesh.ClearGeneratedData()
    mesh.ElementSize=Quantity(GLOBAL_SIZE)
    mesh.GrowthRate=1.05
    sizings=[v for v in mesh.Children if v.Name=='TaskA Aerofoil 2mm Growth 1.05']
    if len(sizings)!=1: raise Exception('Expected one preserved foil sizing; got '+str(len(sizings)))
    sizing=sizings[0]
    sizing.ElementSize=Quantity(FOIL_SIZE)
    sizing.GrowthRate=1.05
    log('GlobalSize='+str(mesh.ElementSize)+' FoilSize='+str(sizing.ElementSize)+' growth='+str(mesh.GrowthRate)+' foilgrowth='+str(sizing.GrowthRate))
    log('Sizing zoneIDs='+str(list(sizing.Location.Ids)))
    mesh.GenerateMesh()
    log('MESH_GENERATED nodes='+str(mesh.Nodes)+' elements='+str(mesh.Elements))
    mesh.InternalObject.WriteFluentInputFile(out+r'\mesh.msh')
    log('NATIVE_FLUENT_EXPORT_COMPLETE')
    ExtAPI.DataModel.Project.Save()
except:
    log(str(__import__('sys').exc_info()))
f.close()
