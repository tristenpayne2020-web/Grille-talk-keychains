"""Talon spinner print files from spinner/out/talon_spinner_6804.stl: a STEP (faceted solid, ~15k triangles) and a
Creality Print 3MF, copied to Downloads/GrilleTalk_Extras/Spinners.
usage: python spinner/export_print.py [talon|karambit|shield]"""
import os, shutil, sys
import trimesh
from OCP.StlAPI import StlAPI_Reader
from OCP.TopoDS import TopoDS_Shape, TopoDS
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'kc', 'lib'))
import k2config, write3mf

import sys as _s
name = _s.argv[1] if len(_s.argv) > 1 else 'talon'
src = os.path.join(HERE, 'out', f'{name}_spinner_6804.stl')
stem = os.path.join(HERE, 'out', f'{name}_spinner_6804')
m = trimesh.load(src)
m = m.simplify_quadric_decimation(face_count=15000)   # ponytail: faceted STEP, fine for printing/CAD reference
m.export(stem + '_step_src.stl')

shape = TopoDS_Shape()
StlAPI_Reader().Read(shape, stem + '_step_src.stl')
sew = BRepBuilderAPI_Sewing(1e-4); sew.Add(shape); sew.Perform()
solid = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(sew.SewedShape())).Solid()
w = STEPControl_Writer(); w.Transfer(solid, STEPControl_AsIs); w.Write(stem + '.step')
os.remove(stem + '_step_src.stl')

full = trimesh.load(src)
full.apply_translation(-full.bounds[0])          # sit on the bed
write3mf.write_3mf(stem + '.3mf', [dict(name=f'{name.title()} spinner (6804 bearing)', mesh=full, extruder=1)],
                   k2config.build(), object_name=f'{name.title()} finger spinner', app_version=k2config.VERSION)

dl = os.path.join(os.path.expanduser('~'), 'Downloads', 'GrilleTalk_Extras', 'Spinners')
os.makedirs(dl, exist_ok=True)
for ext in ('.step', '.3mf', '.stl'):
    shutil.copy2(stem + ext, dl)
print('ok', round(os.path.getsize(stem + '.step') / 1e6, 1), 'MB step;', round(os.path.getsize(stem + '.3mf') / 1e6, 1), 'MB 3mf;',
      'watertight', full.is_watertight, [round(v, 1) for v in full.extents])
