import traceback
out=r'C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\taskA'
f=open(out+r'\mesh_native_image_log.txt','w')
try:
    mesh=ExtAPI.DataModel.Project.Model.Mesh
    f.write('saved_mesh_nodes=%s elements=%s\n'%(mesh.Nodes,mesh.Elements)); f.flush()
    if mesh.Elements==0:
        execfile(out+r'\configure_mesh.py')
    mesh.Activate()
    camera=ExtAPI.Graphics.Camera
    camera.SetSpecificViewOrientation(ViewOrientationType.Front)
    camera.SetFit(None)
    ExtAPI.Graphics.ExportImage(out+r'\taskA_mesh_native.png',GraphicsImageExportFormat.PNG)
    f.write('FULL_NATIVE_MESH_IMAGE_EXPORTED\n'); f.flush()
    camera.Pan(Quantity('50 [mm]'),Quantity('-7 [mm]'))
    camera.SceneWidth=Quantity('180 [mm]')
    camera.SceneHeight=Quantity('110 [mm]')
    ExtAPI.Graphics.ExportImage(out+r'\taskA_mesh_native_local.png',GraphicsImageExportFormat.PNG)
    f.write('LOCAL_NATIVE_MESH_IMAGE_EXPORTED\n'); f.flush()
except:
    f.write(traceback.format_exc()); f.flush()
f.close()
