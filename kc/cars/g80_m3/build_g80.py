import sys, pickle, json, time
sys.path.insert(0,'../../lib')
import geom, build3d, render
SPEC=pickle.load(open('spec_from_step.pkl','rb'))
t=time.time()
M=geom.build_maps(SPEC)
rep=geom.check_maps(M)
print('maps',round(time.time()-t,1),'s', json.dumps({k:v for k,v in rep.items() if k!='warnings'},indent=1)[:3000])
render.face_png(M,'face.png',title='G80 remake (from STEP)')
for style,fn in (('production',build3d.build_production),('classic',build3d.build_classic)):
    parts,slabs=fn(M)
    print(style, build3d.check_parts(parts))
    tb=build3d.to_trimesh(parts['black']); tw=build3d.to_trimesh(parts['white'])
    tb.export(f'{style}_black.stl'); tw.export(f'{style}_white.stl')
    render.render3d([(tw,(0.91,0.90,0.86)),(tb,(0.10,0.10,0.11))],f'{style}_3d.png')
