# Python Script, API Version = V22
import math,traceback,System
from SpaceClaim.Api.V22 import WindowExportFormat, Application
out=r'C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\aligned_taskA'
try:
    DocumentOpen.Execute(out+r'\taskA_geometry.scdoc')
    root=GetRootPart()
    body=root.Bodies[0]
    audit=open(out+r'\geometry_kernel_audit.txt','w')
    audit.write('SurfaceArea_m2=%.14g\n'%body.Shape.SurfaceArea)
    audit.write('FaceCount=%s\nEdgeCount=%s\n'%(body.Faces.Count,body.Edges.Count))
    for ai,af in enumerate(body.Faces): audit.write('Face%s_loop_count=%s\n'%(ai,af.Shape.Loops.Count))
    audit.write('fluid_ContainsPoint='+str(body.Shape.ContainsPoint(Point.Create(-.25,0,0)))+'\n')
    audit.write('translated_foil_interior_ContainsPoint='+str(body.Shape.ContainsPoint(Point.Create(.05*.9902680687+.00048367698354395,-.05*.139173101+.00691690311771526,0)))+'\n')
    audit.close()
    f=open(out+r'\cad_edge_dense_coordinates_m.csv','w')
    f.write('edge,index,x_m,y_m,z_m\n')
    for k,e in enumerate(body.Edges):
        if k>2: continue
        for i in range(1001):
            p=e.EvalProportion(i/1000.).Point
            f.write('%s,%s,%.15g,%.15g,%.15g\n'%(k,i,p.X,p.Y,p.Z))
    f.close()
    w=Window.ActiveWindow
    old_options=Application.UserOptions
    clean_options=Application.UserOptions
    clean_options.ShowWorldOrigin=False
    clean_options.ShowSpinCenter=False
    Application.UserOptions=clean_options
    w.SetProjection(Frame.World,.58)
    w.Export(WindowExportFormat.Png,out+r'\taskA_geometry_native.png')
    local_frame=Frame.Create(Point.Create(.05,0,0),Direction.DirX,Direction.DirY)
    w.SetProjection(local_frame,.09)
    w.Export(WindowExportFormat.Png,out+r'\taskA_geometry_native_local.png')
    Application.UserOptions=old_options
    System.IO.File.WriteAllText(out+r'\geometry_native_export.txt','NATIVE_WINDOW_PNG_EXPORTED\n'+str(w))
except:
    System.IO.File.WriteAllText(out+r'\geometry_native_export_error.txt',traceback.format_exc())





