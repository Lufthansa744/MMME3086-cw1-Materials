# Python Script, API Version = V22
import math,traceback,System
from SpaceClaim.Api.V22 import WindowExportFormat, Application
out=r'C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\taskA'
try:
    DocumentOpen.Execute(out+r'\taskA_geometry.scdoc')
    root=GetRootPart()
    body=root.Bodies[0]
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
    local_frame=Frame.Create(Point.Create(.05,-.007,0),Direction.DirX,Direction.DirY)
    w.SetProjection(local_frame,.09)
    w.Export(WindowExportFormat.Png,out+r'\taskA_geometry_native_local.png')
    Application.UserOptions=old_options
    System.IO.File.WriteAllText(out+r'\geometry_native_export.txt','NATIVE_WINDOW_PNG_EXPORTED\n'+str(w))
except:
    System.IO.File.WriteAllText(out+r'\geometry_native_export_error.txt',traceback.format_exc())



