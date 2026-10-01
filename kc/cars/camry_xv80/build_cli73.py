"""Full build with the real-slicer check adapted to Creality Print 7.3 (read-only use of kc/lib).

Creality Print auto-updated to 7.3 on 2026-09-29 09:33; its executable no longer accepts the 7.1 command line used by
kc/lib/slicecheck.py (`--slice 1 --export-3mf out.3mf in.3mf` -> "Invalid option --export-3mf", exit 1).
The 7.3 CLI is `CrealityPrint.exe --cli --slice 1 --outputdir DIR --need-gcode-file in.3mf` -> DIR/plate_1.gcode.
This wrapper swaps only that one function at runtime (lib files untouched) and then runs the normal export.full(),
so geometry, 3MF files, renders and the slicecheck comparison are exactly the pipeline's.

  python kc/cars/camry_xv80/build_cli73.py kc/cars/camry_xv80/spec.py kc/cars/camry_xv80/out
"""
import os, sys, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'lib')))
import slicecheck, export, k2config, write3mf


def slice_single_part_73(mesh, name, workdir, thumb, cfg_over=None):
    os.makedirs(workdir, exist_ok=True)
    cfg = k2config.build(cfg_over or {})
    src = os.path.abspath(os.path.join(workdir, name + '_1part.3mf'))
    outdir = os.path.abspath(os.path.join(workdir, name + '_cli73'))
    write3mf.write_3mf(src, [dict(name=name, mesh=mesh, extruder=1)], cfg, object_name=name,
                       positions=[slicecheck.BEDC], thumbnail_png=thumb)
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir)
    r = subprocess.run([slicecheck.EXE, '--cli', '--slice', '1', '--outputdir', outdir, '--need-gcode-file', src],
                       capture_output=True, text=True, timeout=1800)
    g = os.path.join(outdir, 'plate_1.gcode')
    if not os.path.exists(g):
        return None, f'CLI(7.3) exit {r.returncode}'
    return open(g, encoding='utf-8', errors='ignore').read(), 'ok'


slicecheck.slice_single_part = slice_single_part_73

if __name__ == '__main__':
    a = sys.argv[1:]
    spec = export.load_spec(a[0])
    export.full(spec, a[1], do_step='--no-step' not in a, do_slice='--no-slice' not in a, do_plate='--no-plate' not in a)
