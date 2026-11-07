# Python Script, API Version = V22
import math, traceback, System
from System.Collections.Generic import List
from SpaceClaim.Api.V22 import *
from SpaceClaim.Api.V22.Geometry import *
from SpaceClaim.Api.V22.Modeler import Body
out=r'C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1\solver\taskA'
try:
    root=GetRootPart()
    profile=List[ITrimmedCurve]()
    corners=[Point.Create(-.5,-.075,0),Point.Create(.5,-.075,0),Point.Create(.5,.075,0),Point.Create(-.5,.075,0)]
    for i in range(4): profile.Add(CurveSegment.Create(corners[i],corners[(i+1)%4]))
    angle=-8*math.pi/180
    def foil_point(t,sign):
        x=.1*t
        y=sign*.06*(.2969*math.sqrt(t)-.126*t-.3516*t*t+.2843*t*t*t-.1015*t*t*t*t)
        return Point.Create(x*math.cos(angle)-y*math.sin(angle),x*math.sin(angle)+y*math.cos(angle),0)
    points={}
    for side,sign in [('suction',1),('pressure',-1)]:
        pts=List[Point]()
        for i in range(401): pts.Add(foil_point((1-math.cos(math.pi*i/400))/2,sign))
        points[side]=pts
        crv=NurbsCurve.CreateThroughPoints(False,pts,1e-7)
        profile.Add(CurveSegment.Create(crv))
    profile.Add(CurveSegment.Create(points['suction'][400],points['pressure'][400]))
    body=DesignBody.Create(root,'fluid',Body.CreatePlanarBody(Plane.PlaneXY,profile))
    edge_report=[]
    for i,e in enumerate(body.Edges):
        a=e.EvalStart().Point
        b=e.EvalEnd().Point
        m=e.EvalMid().Point
        if abs(m.X+.5)<1e-8: name='inlet'
        elif abs(m.X-.5)<1e-8: name='outlet'
        elif abs(m.Y-.075)<1e-8: name='wall_top'
        elif abs(m.Y+.075)<1e-8: name='wall_bottom'
        elif (a-b).Magnitude<.001: name='aerofoil_te'
        elif m.X*math.sin(-angle)+m.Y*math.cos(-angle)>0: name='aerofoil_suction'
        else: name='aerofoil_pressure'
        sel=List[IDocObject]()
        sel.Add(e)
        Group.Create(root,name,sel)
        edge_report.append('%s,%s,%.14g,%.14g,%.14g,%.14g,%.14g,%.14g'%(i,name,a.X,a.Y,b.X,b.Y,m.X,m.Y))
    f=open(out+r'\boundary_edges.csv','w')
    f.write('edge_index,name,start_x_m,start_y_m,end_x_m,end_y_m,mid_x_m,mid_y_m\n'+'\n'.join(edge_report))
    f.close()
    f=open(out+r'\geometry_properties.txt','w')
    f.write('faces=%s\nedges=%s\n'%(body.Faces.Count,body.Edges.Count))
    f.write('shape_properties='+str(dir(body.Shape))+'\n')
    f.close()
    DocumentSave.Execute(out+r'\taskA_geometry.scdoc')
    f=open(out+r'\geometry_creation.txt','w')
    f.write('GEOMETRY_CREATED\n'+str(body)+'\n')
    f.write('DesignBody members: '+str(dir(body))+'\n')
    for i,e in enumerate(body.Edges):
        f.write('EDGE '+str(i)+' '+str(e)+'\n'+str(dir(e))+'\n')
    f.close()
    f=open(out+r'\foil_coordinates_m.csv','w')
    f.write('side,index,x_m,y_m,z_m\n')
    for side in ['suction','pressure']:
        for i,p in enumerate(points[side]): f.write('%s,%s,%.14g,%.14g,%.14g\n'%(side,i,p.X,p.Y,p.Z))
    f.close()
except:
    System.IO.File.WriteAllText(out+r'\geometry_error.txt',traceback.format_exc())

