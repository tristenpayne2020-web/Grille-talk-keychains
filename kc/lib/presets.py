"""Resolve Creality Print system presets (with `inherits`) into a full project_settings.config."""
import json, os, copy

SYS = os.path.expandvars(r'C:\Users\trist\AppData\Roaming\Creality\Creality Print\7.0\system\Creality')
if not os.path.isdir(SYS):
    SYS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'slicer_presets', 'system')
CATS = {'machine': 'machine', 'process': 'process', 'filament': 'filament'}
PER_FILAMENT_EXTRA = {'activate_chamber_layer', 'cooling_perimeter_transition_distance', 'cooling_slowdown_logic', 'dont_slow_down_outer_wall',
                      'idle_temperature', 'smart_cooling_zones', 'pellet_flow_coefficient', 'transmittance_matrix', 'travel_slope',
                      'initial_layer_travel_acceleration'}
OBSOLETE_KEYS = {'adaptive_layer_height', 'bed_type', 'wall_infill_order'}
META_KEYS = {'inherits', 'from', 'name', 'type', 'instantiation', 'is_custom_defined', 'setting_id', 'base_id',
             'version', 'compatible_printers', 'compatible_printers_condition', 'compatible_prints', 'compatible_prints_condition',
             'print_compatible_printers', 'is_internal', 'filament_id', 'printer_model', 'printer_variant', 'inherits_group',
             'filament_vendor', 'default_materials', 'model_id', 'nozzle_type', 'bed_model', 'bed_texture', 'hotend_model', 'thumbnail', 'upward_compatible_machine'}


def load_chain(cat, name):
    """Return list of preset dicts from root ancestor to the named preset."""
    chain = []
    cur = name
    seen = set()
    while cur and cur not in seen:
        seen.add(cur)
        p = os.path.join(SYS, CATS[cat], cur + '.json')
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        d = json.load(open(p, encoding='utf-8'))
        chain.append(d)
        cur = d.get('inherits')
    return list(reversed(chain))


def resolve(cat, name):
    merged = {}
    for d in load_chain(cat, name):
        for k, v in d.items():
            if k == 'inherits':
                continue
            merged[k] = copy.deepcopy(v)
    return merged


def to_list_n(v, n):
    if isinstance(v, list):
        if len(v) == n:
            return v
        if len(v) == 1:
            return v * n
        return (v + [v[-1]] * n)[:n]
    return [v] * n


def build_project_settings(machine_name, process_name, filament_names, colours, version, overrides=None, template=None):
    n = len(filament_names)
    m = resolve('machine', machine_name)
    p = resolve('process', process_name)
    fs = [resolve('filament', f) for f in filament_names]

    cfg = {}
    if template:
        # start from a real project config so no app-default key is missing; everything below overrides.
        # per-filament vectors from the template are resized to n filaments (copy the last value).
        for k, v in template.items():
            v = copy.deepcopy(v)
            if isinstance(v, list) and len(v) == 1 and (k.startswith('filament_') or k in PER_FILAMENT_EXTRA):
                v = v * n
            cfg[k] = v
    # machine + process are scalar configs
    for src in (m, p):
        for k, v in src.items():
            if k in META_KEYS or k in OBSOLETE_KEYS:
                continue
            cfg[k] = v
    # filament keys: per-filament lists
    fkeys = set()
    for f in fs:
        fkeys.update(k for k in f if k not in META_KEYS)
    for k in fkeys:
        vals = []
        for f in fs:
            v = f.get(k, fs[0].get(k))
            if isinstance(v, list):
                v = v[0] if v else ''
            vals.append(v)
        cfg[k] = vals
    cfg['printer_settings_id'] = machine_name
    cfg['print_settings_id'] = process_name
    cfg['filament_settings_id'] = list(filament_names)
    cfg['filament_colour'] = list(colours)
    cfg['filament_ids'] = [f.get('filament_id', '') for f in fs]
    cfg['filament_vendor'] = [ (f.get('filament_vendor', ['Creality'])[0] if isinstance(f.get('filament_vendor'), list) else f.get('filament_vendor', 'Creality')) for f in fs]
    cfg['printer_model'] = m.get('printer_model', '')
    cfg['printer_variant'] = m.get('printer_variant', '0.4')
    cfg['nozzle_diameter'] = to_list_n(m.get('nozzle_diameter', ['0.4']), 1)
    cfg['inherits_group'] = ['', ''] + [''] * n
    cfg['upward_compatible_machine'] = m.get('upward_compatible_machine', [])
    cfg['version'] = version
    cfg['from'] = 'project'
    cfg['name'] = 'project_settings'
    # multi-filament bookkeeping
    cfg['flush_volumes_vector'] = ['140'] * n
    cfg['flush_volumes_matrix'] = ['0' if i == j else '140' for i in range(n) for j in range(n)]
    cfg['extruder_colour'] = to_list_n(cfg.get('extruder_colour', ['#FCE94F']), 1)
    cfg['default_filament_colour'] = [''] * n
    if overrides:
        cfg.update(overrides)
    return cfg, m, p, fs


if __name__ == '__main__':
    import sys
    tpl = json.load(open('bp/Metadata/project_settings.config', encoding='utf-8'))
    cfg, m, p, fs = build_project_settings('Creality K2 0.4 nozzle', '0.20mm Standard @Creality K2 0.4 nozzle',
                                           ['CR-PETG @Creality K2 0.4 nozzle'] * 2, ['#000000', '#FFFFFF'], '7.2.2.5483', template=tpl)
    missing = sorted(set(tpl) - set(cfg))
    extra = sorted(set(cfg) - set(tpl))
    print('keys resolved', len(cfg), 'template', len(tpl))
    print('MISSING vs template (%d):' % len(missing), missing)
    print('EXTRA vs template (%d):' % len(extra), extra)
    for k in ['filament_id', 'filament_settings_id', 'filament_type', 'nozzle_temperature', 'hot_plate_temp', 'textured_plate_temp', 'filament_max_volumetric_speed', 'filament_flow_ratio', 'filament_start_gcode']:
        print(k, '=', json.dumps(cfg.get(k))[:200])
    print('machine printer_model', m.get('printer_model'), 'printable_area', m.get('printable_area'), 'machine_start_gcode' in cfg)
    print('process layer_height', cfg.get('layer_height'), 'wall_generator', cfg.get('wall_generator'), 'enable_prime_tower', cfg.get('enable_prime_tower'))
