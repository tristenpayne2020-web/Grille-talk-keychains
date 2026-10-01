import json, os, sys, shutil, subprocess, glob
sys.path.insert(0, 'lib')
import package
DEST = r'C:\Users\trist\Downloads\CarKeychains'
cars = json.load(open('cars_pkg.json'))
# every packaged car needs its build outputs here; stop BEFORE touching Downloads if any are missing
missing = [c['id'] for c in cars if not os.path.exists(os.path.join(c['out'], 'build_report.json'))]
if missing:
    sys.exit(f"finalize: no build outputs for {', '.join(missing)} - build them first "
             f"(python rebuild_all.py, or finish_cars.py --only=...). Downloads was not touched.")
# move the old package aside in one step: if anything inside is open (Explorer window, Creality Print, a terminal)
# the rename fails and nothing is deleted
if os.path.isdir(DEST):
    old = DEST + '_old'
    if os.path.exists(old):
        shutil.rmtree(old, ignore_errors=True)
    try:
        os.rename(DEST, old)
    except OSError:
        sys.exit("finalize: something in Downloads\\CarKeychains is open (File Explorer window, Creality Print, a terminal). "
                 "Close it and run again. Nothing was deleted.")
    shutil.rmtree(old, ignore_errors=True)
rows = package.package(DEST, cars)
# line-up + editable source
specs = ['kc_style_pkl'] if False else []
subprocess.run([sys.executable, 'lib/lineup.py', os.path.join(DEST, 'lineup_all_cars.png'), 'cars/g80_m3/spec_from_step.pkl'] +
               [f"cars/{c['id']}/spec.py" for c in cars if c['id'] != 'g80_m3'], check=True)
src = os.path.join(DEST, '_source')
shutil.copytree('lib', os.path.join(src, 'lib'), ignore=shutil.ignore_patterns('__pycache__', 'template_project_settings.json'))
os.makedirs(os.path.join(src, 'cars'))
shutil.copy('cars/README_SPEC.md', os.path.join(src, 'cars', 'README_SPEC.md'))
for c in cars:
    d = os.path.join(src, 'cars', c['id']); os.makedirs(d)
    if c['id'] == 'g80_m3':
        shutil.copy('cars/g80_m3/spec_from_step.pkl', os.path.join(d, 'spec_from_your_step.pkl'))
    else:
        shutil.copy(f"cars/{c['id']}/spec.py", os.path.join(d, 'spec.py'))
shutil.copytree('style', os.path.join(src, 'style'), ignore=shutil.ignore_patterns('g80_reference_photo_the_user_traced.png'))
subprocess.run([sys.executable, 'make_readme.py', DEST], check=True, capture_output=True)
subprocess.run([sys.executable, 'make_gallery.py', DEST], check=True)
subprocess.run([sys.executable, 'make_sampler.py', DEST], check=True)
subprocess.run([sys.executable, 'pricing_inputs.py'], check=True)
subprocess.run([sys.executable, 'make_pricing.py', os.path.join(DEST, 'Pricing_Model.xlsx'), 'pricing_inputs.json', 'pricing_cars.json'], check=True)
subprocess.run([sys.executable, 'make_pricing_guide.py', os.path.join(DEST, 'Pricing_Model.xlsx'), os.path.join(DEST, 'PRICING_GUIDE.txt')], check=True, capture_output=True)
for r in rows:
    print(r['folder'], r['per_plate'], r.get('swap_plate_time'), r.get('classic_plate_time'))

# ONE master slicer preset: (re)install it in Creality Print, put a copy + how-to in the delivery, re-point every 3MF at it
import master_preset
master_preset.install()
ms = master_preset.settings()
KEYS = [('layer_height', 'Layer height (mm)'), ('initial_layer_print_height', 'First layer height (mm)'), ('wall_loops', 'Wall loops'),
        ('top_shell_layers', 'Top shell layers'), ('bottom_shell_layers', 'Bottom shell layers'), ('wall_generator', 'Wall generator'),
        ('wall_transition_angle', 'Wall transitioning threshold angle'), ('sparse_infill_density', 'Infill'), ('sparse_infill_pattern', 'Infill pattern'),
        ('ironing_type', 'Ironing'), ('ironing_flow', 'Ironing flow'), ('ironing_spacing', 'Ironing line spacing (mm)'),
        ('ironing_speed', 'Ironing speed'), ('ironing_angle', 'Ironing angle'), ('top_surface_pattern', 'Top surface pattern'),
        ('elefant_foot_compensation', 'Elephant foot compensation (mm)'), ('enable_prime_tower', 'Prime tower'),
        ('prime_tower_width', 'Prime tower width (mm)'), ('flush_into_infill', 'Flush into infill'), ('brim_type', 'Brim')]
how = f"""GRILLE TALK - MASTER SLICER PRESET (Creality Print 7.3, K2 + CFS, 0.4 nozzle)

Preset name:  {master_preset.NAME}
It is already installed in Creality Print (Process preset list, under User presets).
If Creality Print was open while it was installed, close and reopen it once.
On another computer: Creality Print > File > Import > Import Configs... > pick the .json in this folder.

Two ways to print a car
  1. Open the car's .3mf (single or PLATE). It already uses this preset and has every part on the right filament.
  2. Or start from your own project: printer K2 0.4, process = this preset, filaments
       2-colour files:      1 = black, 2 = white
       custom body colour:  1 = black, 2 = body colour, 3 = white (lights/badge)
     then File > Import (Ctrl+I) the car's .3mf - only the geometry comes in, with its parts already on filaments 1/2/3,
     and the settings stay the master preset. PLATE files leave the back-right corner free for the prime tower.

Changing a setting
  Change it once in this preset in Creality Print and Save (overwrite the preset). Every car uses it from then on -
  there is nothing to change per car. (The car files carry a copy of the settings only so they open ready to print;
  one command re-syncs all of them to the preset in a few seconds, no rebuild.)

Settings in this preset (differences from the Creality system preset "{master_preset.PARENT}")
""" + '\n'.join(f"  {label:<40} {ms[k]}" for k, label in KEYS if k in ms) + '\n'
open(os.path.join(master_preset.DOWNLOADS, 'HOW_TO_USE.txt'), 'w', encoding='utf-8').write(how)
subprocess.run([sys.executable, 'lib/apply_master.py', DEST] + [c['out'] for c in cars], check=True)
