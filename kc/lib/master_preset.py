"""ONE master Creality Print process preset for every keychain ("Grille Talk Keychain ...").

The car files are just geometry (+ which part is which filament); all slicer settings live in this one preset.
  python lib/master_preset.py install      write the preset into Creality Print 7.3 (user presets) + a copy in Downloads
  python lib/master_preset.py show         print the preset
Source of truth: if the installed preset exists it wins (so edits the user saves in Creality Print are picked up);
otherwise it is generated from the user's tuned Copy(2) process + k2config.KEYCHAIN.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

NAME = 'Grille Talk Keychain 0.20mm @Creality K2 0.4 nozzle'
PARENT = '0.20mm Standard @Creality K2 0.4 nozzle'
USER73 = os.path.expandvars(r'%APPDATA%\Creality\Creality Print\7.3\user\3477890751')
PRESET_DIR = os.path.join(USER73, 'process')
PRESET_JSON = os.path.join(PRESET_DIR, NAME + '.json')
if not os.path.isdir(USER73):  # cloud / other machine: read and write the copy bundled in the repo instead
    PRESET_DIR = os.path.join(os.path.dirname(HERE), 'slicer_presets')
    PRESET_JSON = os.path.join(PRESET_DIR, NAME + '.json')
DOWNLOADS = os.path.expandvars(r'%USERPROFILE%\Downloads\CarKeychains\_MASTER_SLICER_PRESET')
PROJECT_ONLY = {'flush_multiplier', 'flush_volumes_matrix', 'flush_volumes_vector', 'curr_bed_type'}   # not preset keys
META = {'base_id', 'from', 'inherits', 'is_custom_defined', 'name', 'print_settings_id', 'version', 'setting_id',
        'sync_info', 'user_id', 'updated_time'}


def generated():
    import k2config
    user = json.load(open(os.path.join(k2config.USER, k2config.USER_PROCESS), encoding='utf-8'))
    s = {k: v for k, v in user.items() if k not in META}
    s.update({k: v for k, v in k2config.KEYCHAIN.items() if k not in PROJECT_ONLY})
    return s


def settings():
    """The master's own settings (no metadata), from the installed preset if there is one."""
    if os.path.exists(PRESET_JSON):
        return {k: v for k, v in json.load(open(PRESET_JSON, encoding='utf-8')).items() if k not in META}
    return generated()


def preset_doc(s):
    d = {'base_id': 'GP004', 'from': 'User', 'inherits': PARENT, 'is_custom_defined': '0', 'name': NAME,
         'print_settings_id': NAME, 'version': '26.8.29.19'}
    d.update(s)
    return dict(sorted(d.items()))


def _write(path, text):
    tmp = path + '.tmp'
    open(tmp, 'w', encoding='utf-8', newline='\n').write(text)
    os.replace(tmp, path)


def install(regenerate=False):
    s = generated() if regenerate or not os.path.exists(PRESET_JSON) else settings()
    doc = json.dumps(preset_doc(s), indent=4) + '\n'
    info = f'sync_info = \nuser_id = \nsetting_id = \nbase_id = GP004\nupdated_time = {int(time.time())}\n'
    os.makedirs(PRESET_DIR, exist_ok=True)
    _write(PRESET_JSON, doc)
    _write(os.path.join(PRESET_DIR, NAME + '.info'), info)
    os.makedirs(DOWNLOADS, exist_ok=True)
    _write(os.path.join(DOWNLOADS, NAME + '.json'), doc)
    return PRESET_JSON


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'show'
    if cmd == 'install':
        print('installed', install('--regenerate' in sys.argv))
    print(json.dumps(preset_doc(settings()), indent=1))
