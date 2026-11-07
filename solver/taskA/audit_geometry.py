# Python Script, API Version = V22
import traceback,System
out=r'C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\taskA'
try:
    DocumentOpen.Execute(out+r'\taskA_geometry.scdoc')
    body=GetRootPart().Bodies[0]
    f=open(out+r'\geometry_kernel_audit.txt','w')
    f.write('SurfaceArea_m2=%.14g\n'%body.Shape.SurfaceArea)
    f.write('FaceCount=%s\nEdgeCount=%s\n'%(body.Faces.Count,body.Edges.Count))
    for i,face in enumerate(body.Faces): f.write('Face%s_loop_count=%s\n'%(i,face.Shape.Loops.Count))
    for label,p in [('fluid',Point.Create(-.25,0,0)),('foil_interior',Point.Create(.05*.9902680687,-.05*.139173101,0))]:
        f.write(label+'_ContainsPoint='+str(body.Shape.ContainsPoint(p))+'\n')
    f.close()
except:
    System.IO.File.WriteAllText(out+r'\geometry_kernel_error.txt',traceback.format_exc())
