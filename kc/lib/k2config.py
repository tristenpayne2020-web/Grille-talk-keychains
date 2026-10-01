"""Build a Creality Print 7.x project_settings.config for the K2 (0.4 nozzle, 2 filaments: black + white).

The shape of every key (scalar vs list, list length) is taken from a config that the Creality Print GUI itself
wrote for this user's two-filament K2 G80 session (gui_2filament_config.json). Values come from the resolved system
presets (machine / process / filament, following `inherits`), then the user's own tuned keychain process overrides
("0.20mm Standard @Creality K2 0.4 nozzle - Copy(2)"), then the keychain-production overrides below.
Mismatched list lengths are what crashed the CLI slicer, so everything is conformed to the GUI's shapes.
"""
import copy, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
GUI = json.load(open(os.path.join(HERE, 'gui_2filament_config.json'), encoding='utf-8'))
SYS = os.path.expandvars(r'%APPDATA%\Creality\Creality Print\7.0\system\Creality')
USER = os.path.expandvars(r'%APPDATA%\Creality\Creality Print\7.0\user\3477890751')
if not os.path.isdir(SYS):     # not on the user's Windows PC (e.g. a cloud session): use the presets bundled in the repo
    _P = os.path.join(os.path.dirname(HERE), 'slicer_presets')
    SYS, USER = os.path.join(_P, 'system'), os.path.join(_P, 'user')

MACHINE = 'Creality K2 0.4 nozzle'
PROCESS = '0.20mm Standard @Creality K2 0.4 nozzle'
FILAMENT = 'Hyper PLA @Creality K2 0.4 nozzle'
USER_PROCESS = 'process/0.20mm Standard @Creality K2 0.4 nozzle - Copy(2).json'
VERSION = GUI.get('version', '7.2.2.5483')

META = {'inherits', 'from', 'name', 'type', 'instantiation', 'is_custom_defined', 'setting_id', 'base_id', 'version',
        'compatible_printers', 'compatible_printers_condition', 'compatible_prints', 'compatible_prints_condition',
        'print_compatible_printers', 'is_internal', 'filament_id', 'printer_model', 'printer_variant', 'inherits_group',
        'filament_vendor', 'default_materials', 'model_id', 'nozzle_type', 'bed_model', 'bed_texture', 'hotend_model',
        'thumbnail', 'upward_compatible_machine', 'print_settings_id', 'printer_settings_id', 'filament_settings_id',
        'sync_info', 'user_id', 'updated_time'}


def _chain(cat, name):
    out, cur, seen = [], name, set()
    while cur and cur not in seen:
        seen.add(cur)
        d = json.load(open(os.path.join(SYS, cat, cur + '.json'), encoding='utf-8'))
        out.append(d)
        cur = d.get('inherits')
    return list(reversed(out))


def resolve(cat, name):
    merged = {}
    for d in _chain(cat, name):
        merged.update({k: copy.deepcopy(v) for k, v in d.items() if k != 'inherits'})
    return merged


def conform(v, like):
    """Give v the same shape (scalar / list of len L) as the GUI's value `like`."""
    if isinstance(like, list):
        L = len(like)
        if not isinstance(v, list):
            v = v.split(',') if (isinstance(v, str) and ',' in v and L > 1 and 'x' in v) else [v]
        if len(v) == L:
            return list(v)
        if len(v) == 1:
            return list(v) * L
        return (list(v) + [v[-1]] * L)[:L]
    if isinstance(v, list):
        return v[0] if v else ''
    return v


# Keychain production overrides (0.4 nozzle). Where the user's own Copy(2) process already sets a key, their value is
# kept unless there is a production reason to change it (noted inline).
KEYCHAIN = {
    'layer_height': '0.2', 'initial_layer_print_height': '0.2',        # 0.2 first layer: z-levels of both builds sit on a 0.2 grid
    'initial_layer_line_width': '0.45', 'initial_layer_speed': '40', 'initial_layer_infill_speed': '80',
    'wall_generator': 'arachne', 'min_bead_width': '85%', 'min_feature_size': '25%', 'detect_thin_wall': '1',
    'wall_loops': '2', 'top_shell_layers': '6', 'bottom_shell_layers': '3',   # user: top shells 6
    'wall_transition_angle': '50',                                          # user: wall transitioning threshold angle 50
    'sparse_infill_density': '15%', 'sparse_infill_pattern': 'gyroid',
    'ironing_type': 'top', 'ironing_angle': '45', 'ironing_speed': '60', 'ironing_flow': '25%', 'ironing_spacing': '0.12',   # user: ironing flow 25 %, line spacing 0.12 mm
    'top_surface_line_width': '0.4', 'top_surface_speed': '120', 'top_surface_acceleration': '3000',
    'top_surface_pattern': 'monotonicline', 'only_one_wall_top': '0',
    'precise_outer_wall': '1', 'elefant_foot_compensation': '0.15', 'seam_position': 'aligned',
    'brim_type': 'no_brim', 'skirt_loops': '1',
    'enable_prime_tower': '1', 'prime_tower_width': '35', 'prime_tower_brim_width': '3',
    'flush_into_infill': '1', 'flush_into_objects': '0', 'flush_into_support': '0',
    'flush_multiplier': '1.3', 'flush_volumes_matrix': ['0', '670', '200', '0'], 'flush_volumes_vector': ['140', '140'],
    'curr_bed_type': 'Textured PEI Plate',
    'print_sequence': 'by layer',
}
PROCESS_KEYS = sorted(k for k in KEYCHAIN if k not in ('flush_multiplier', 'flush_volumes_matrix', 'flush_volumes_vector', 'curr_bed_type'))


def build(overrides=None, colours=('#000000', '#FFFFFF')):
    m, p, f = resolve('machine', MACHINE), resolve('process', PROCESS), resolve('filament', FILAMENT)
    cfg = copy.deepcopy(GUI)
    for src in (m, p):
        for k, v in src.items():
            if k in META or k not in GUI:
                continue
            cfg[k] = conform(v, GUI[k])
    for k, v in f.items():
        if k in META or k not in GUI:
            continue
        cfg[k] = conform(v if not isinstance(v, list) else v[:1], GUI[k])
    user = json.load(open(os.path.join(USER, USER_PROCESS), encoding='utf-8'))
    for k, v in user.items():
        if k in META or k not in GUI:
            continue
        cfg[k] = conform(v, GUI[k])
    import master_preset                                    # the ONE master process preset wins over KEYCHAIN
    master = master_preset.settings()
    allover = dict(KEYCHAIN)
    allover.update(master)
    if overrides:
        allover.update(overrides)
    for k, v in allover.items():
        cfg[k] = conform(v, GUI[k]) if k in GUI else v
    cfg['printer_settings_id'] = MACHINE
    cfg['print_settings_id'] = master_preset.NAME
    cfg['filament_settings_id'] = [FILAMENT, FILAMENT]
    cfg['filament_colour'] = list(colours)
    cfg['filament_ids'] = [f.get('filament_id', '01001')] * 2
    cfg['print_compatible_printers'] = [MACHINE]
    cfg['printer_model'] = m.get('printer_model', 'Creality K2')
    cfg['printer_variant'] = m.get('printer_variant', '0.4')
    cfg['nozzle_diameter'] = ['0.4']
    cfg['inherits_group'] = [master_preset.PARENT, '', '', '']
    pk = sorted(set(PROCESS_KEYS) | set(master) | {k for k in (overrides or {}) if k in p})
    cfg['different_settings_to_system'] = [';'.join(pk), '', '', '']
    cfg['printer_select_mac'] = ''
    cfg['version'] = VERSION
    return cfg


if __name__ == '__main__':
    c = build()
    for k in ['printer_settings_id', 'print_settings_id', 'layer_height', 'nozzle_diameter', 'printable_area', 'wipe_tower_x',
              'retraction_length', 'change_filament_gcode', 'nozzle_temperature', 'enable_prime_tower', 'flush_into_infill']:
        print(k, '=', str(c[k])[:120])
    bad = [(k, len(v), len(GUI[k])) for k, v in c.items() if isinstance(v, list) and k in GUI and isinstance(GUI[k], list) and len(v) != len(GUI[k])]
    print('shape mismatches:', bad)


# ---------------------------------------------------------------------------------------------- n filaments
NOT_PER_FILAMENT = {'machine_min_extruding_rate', 'machine_min_travel_rate', 'start_end_points', 'flush_volumes_vector'}


def build_n(n, colours, flush_matrix, overrides=None):
    """Same as build() but for n filaments (e.g. 3 = black details, body colour, white lights)."""
    cfg = build(overrides, colours=tuple(colours[:2]))
    for k, v in list(cfg.items()):
        g = GUI.get(k)
        if isinstance(g, list) and len(g) == 2 and k not in NOT_PER_FILAMENT and isinstance(v, list) and len(v) == 2:
            cfg[k] = list(v) + [v[-1]] * (n - 2)
    cfg['filament_colour'] = list(colours)
    cfg['flush_volumes_matrix'] = [str(x) for x in flush_matrix]
    cfg['transmittance_matrix'] = ['0.8'] * (n * n)
    cfg['different_settings_to_system'] = [cfg['different_settings_to_system'][0]] + [''] * (n + 1)
    cfg['inherits_group'] = [cfg['inherits_group'][0]] + [''] * (n + 1)
    cfg['filament_settings_id'] = [FILAMENT] * n
    return cfg
