"""Build the G80 spec (mm) directly from the user's STEP sections, fixing only the sub-nozzle features."""
import sys, json, pickle
sys.path.insert(0,'../../lib')
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
import trimesh
from geom import polys, clean
SP='../../../g80/'
rows=json.load(open(SP+'bodies.json'))
S=pickle.load(open(SP+'sections.pkl','rb'))
def sec(i,y):
    m=trimesh.load(SP+f'body_{i:02d}.stl')
    s=m.section(plane_origin=[0,y,0],plane_normal=[0,1,0])
    g=Polygon()
    for e in s.discrete:
        g=g.symmetric_difference(Polygon([[v[2],v[0]] for v in e]).buffer(0))
    return clean(g)
L=S[0.2]
def U(idx,layer=L): return clean(unary_union([layer[i].buffer(0.003) for i in idx]).buffer(-0.003))
names={r['i']:r['name'] for r in rows}
col={r['i']:r['color'] for r in rows}
allu=U(list(L.keys()))
body=clean(allu.intersection(box(-40.26,-30,50,30)))       # remove the old tab
body=max(polys(body),key=lambda p:p.area)
body=Polygon(body.exterior)
Y0=body.bounds[1]
T=lambda g: affinity.translate(g,0,-Y0)
blk=[i for i in col if col[i]=='black']
small_ring=[5,24]; big_ring=[7,26]; cam_ring=[18,37]; roundel=[39,40,41,42,43,44]
white_isl=[i for i in col if col[i]=='white' and i!=0 and i not in (1,2,20,21,17,36,40)]   # DRLs only (19,38)
grille_back=[8,27]
slats=[9,10,11,12,13,14,15,28,29,30,31,32,33,34]
black_main=U([i for i in blk if i not in small_ring+big_ring+cam_ring+roundel+slats])
drl=U(white_isl)
grille=U(grille_back)
ribs=U(slats, S[1.5])
w1=sec(0,1.0); w3=sec(0,2.6)
grooves=clean(w1.difference(w3.buffer(0.001)))
grooves=unary_union([p for p in polys(grooves) if p.area>0.05]).buffer(0.1)   # 0.3 -> 0.5 mm wide
prims=[]
prims.append(dict(kind='geom',geom=T(black_main),color='black',mirror=False))
prims.append(dict(kind='geom',geom=T(grille),color='relief',mirror=False,relief={'type':'custom','ribs':T(ribs)}))
prims.append(dict(kind='geom',geom=T(drl),color='white',mirror=False))
# sensor rings (fixed to 0.5 mm wall) at original centres
def ctr(i): b=L[i].bounds; return ((b[0]+b[2])/2,(b[1]+b[3])/2-Y0)
for i,ro in ((7,1.42),(5,0.95),(24,0.95)):   # body 26 (the right-hand tow-hook cover) dropped: BMW has one, on the viewer's left
    c=ctr(i)
    prims.append(dict(kind='geom',geom=Point(c).buffer(ro,64).difference(Point(c).buffer(ro-0.5,64)),color='black',mirror=False))
prims.append(dict(kind='geom',geom=Point(0.0,ctr(18)[1]).buffer(0.7,64),color='black',mirror=False))   # front camera: solid dot
prims.append(dict(kind='geom',geom=T(grooves),color='groove',mirror=False))
rc=ctr(44)
SPEC=dict(name='BMW M3 (G80)',id='g80_m3',units='mm',outline=dict(kind='geom',geom=T(body)),prims=prims,
          badge=dict(type='roundel',c=(0.0,rc[1]),d=3.2),tab=dict(y_mm=21.1,reach=3.3))
pickle.dump(SPEC,open('spec_from_step.pkl','wb'))
print('body bounds',T(body).bounds,'grooves area',round(grooves.area,2),'ribs area',round(ribs.area,1))
