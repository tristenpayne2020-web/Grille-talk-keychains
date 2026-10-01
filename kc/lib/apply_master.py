"""Re-point project 3MFs at the master preset and copy its settings in - no geometry rebuild.
Use after changing the master preset: every car file is updated in seconds.
usage: python lib/apply_master.py <dir-or-3mf> [...]      (recurses into folders)"""
import json, os, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import master_preset as MP
from k2config import conform

CFG = 'Metadata/project_settings.config'
PER_FILE = {'wipe_tower_x', 'wipe_tower_y'}          # each plate file keeps its own tower spot


def patch_cfg(cfg, s):
    for k, v in s.items():
        if k in PER_FILE:
            continue
        cfg[k] = conform(v, cfg[k]) if k in cfg else v
    cfg['print_settings_id'] = MP.NAME
    ig = cfg.get('inherits_group')
    if isinstance(ig, list) and ig:
        ig[0] = MP.PARENT
    ds = cfg.get('different_settings_to_system')
    if isinstance(ds, list) and ds:
        ds[0] = ';'.join(sorted(k for k in s if k not in PER_FILE))
    return cfg


def patch_3mf(path, s):
    with zipfile.ZipFile(path) as z:
        if CFG not in z.namelist():
            return False
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
        for info, data in items:
            if info.filename == CFG:
                data = json.dumps(patch_cfg(json.loads(data.decode('utf-8')), s), indent=4).encode('utf-8')
            out.writestr(info, data)
    os.replace(tmp, path)
    return True


def targets(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if f.lower().endswith('.3mf'):
                        yield os.path.join(root, f)
        elif p.lower().endswith('.3mf'):
            yield p


if __name__ == '__main__':
    s = MP.settings()
    n = sum(patch_3mf(p, s) for p in targets(sys.argv[1:]))
    print('re-pointed', n, 'project 3MF files at', MP.NAME)
