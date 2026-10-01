import json, sys, os
dest = sys.argv[1]
rows = json.load(open(os.path.join(dest, 'summary.json')))

def row(r):
    return (f"{r['car']:<48} {r['size_mm']:>11}  {r['per_plate']:>3}   "
            f"{str(r.get('swap_plate_time','-')):>8} {str(r.get('swap_plate_changes','-')):>3} {str(r.get('swap_plate_grams','-')):>6}   "
            f"{str(r.get('classic_plate_time','-')):>8} {str(r.get('classic_plate_changes','-')):>3} {str(r.get('classic_plate_grams','-')):>6}")

table = '\n'.join(row(r) for r in rows)
txt = f"""CAR FRONT KEYCHAINS - Creality K2 (0.4 mm nozzle) + CFS, PLA, black + white
============================================================================

Car-front keychains in the style of your BMW M3 (G80) keychain, plus your G80 with its sub-nozzle details fixed
(and one front tow-hook cover per BMW). Every car comes in two builds made from the same artwork:

  1-swap_production\\   RECOMMENDED FOR BULK. Black base (0-1.6 mm) + white cap (1.6-3.0 mm).
                        The front shows the same black/white design; black areas sit 1.4 mm below
                        the white face (grilles and intakes read as real openings). Exactly ONE
                        filament change per plate, no matter how many keychains are on it.
  classic_full_inlay\\  Built exactly like your G80: flush, full-depth black inlays, double-sided.
                        Needs a filament change on every layer (15 per plate at 0.2 mm layers).

Per build folder:
  <car>_<build>_PLATE_<n>x.3mf   full K2 plate (n copies + prime tower spot), ready to slice
  <car>_<build>_single.3mf       one keychain
  <car>_<build>.step             black + white bodies for Fusion 360
  STL_parts\\                     one STL per colour
  <car>_<build>_plate_layout.png plate layout preview

HOW TO PRINT
  1. Open the PLATE 3MF in Creality Print 7.1 (open as project, keep the project's presets).
  2. Filament 1 = BLACK, filament 2 = WHITE (Hyper PLA). Map them to your CFS slots.
  3. Printer "Creality K2 0.4 nozzle", process based on your "0.20mm Standard - Copy(2)":
     0.2 mm layers, Arachne walls, 2 walls, 4 top / 3 bottom, 15 % gyroid, ironing on top,
     flush into infill, prime tower 35 mm, flush 670/200 mm3 x 1.3 (your values), no brim,
     Textured PEI plate. Nothing needs changing.
  4. Slice and print. For bulk runs use the 1-swap PLATE file.

VERIFIED PLATE NUMBERS (Creality Print 7.1 slicing engine, K2 0.4 profile, full plate)
                                                        size mm   per   ---- 1-swap plate ---   --- classic plate ---
car                                                              plate    time  swp   grams     time  swp   grams
{table}

  classic = real two-colour slice (every colour change, purge and prime tower included).
  1-swap  = real one-colour slice of the exact geometry + the one black->white change, costed with the
            per-change time/filament measured on the same car's classic two-colour slice.
  Purge per change on your settings: black->white 871 mm3 (~1.1 g), white->black 260 mm3 (~0.3 g).

WHAT I TOOK FROM YOUR G80 (the design language all cars follow)
  - straight-on front view, cropped at the base of the windshield, mirror-symmetric
  - body exactly 80.5 mm wide, height follows the car, 3.0 mm thick
  - white body; black headlights, grille, intakes, splitter lip, side vents, badge
  - white light signature (DRL) drawn inside the black headlights
  - grille recessed with slats/mesh standing up in it (your G80: 1 mm floor, slats to the face)
  - a few engraved shut lines (hood outline + fender lines)
  - keyring tab on the left side at about mid height, 4.5 mm hole

WHAT I CHANGED FOR PRINTING (your G80 file had these, all new cars avoid them)
  - hood shut lines were 0.3 mm wide and the sensor rings 0.1-0.2 mm: narrower than a 0.4 mm nozzle can
    print, they would vanish or smear. Now every feature and gap is >= 0.5 mm (checked automatically and
    by slicing each colour part and comparing the real tool paths with the design, layer by layer).
  - headlight rims around the DRLs were 0.15-0.3 mm: widened to >= 0.5 mm.
  - keyring loop wall was 0.75 mm (weak for a keychain): now 2.0 mm (8.5 mm tab, same 4.5 mm hole).
  - full-depth inlays = a colour change on every layer: the 1-swap build removes that.

CUSTOM BODY COLOUR (custom_body_colour\ in each car folder)
  3-filament versions of every car: filament 1 = BLACK (grilles, intakes, headlight housings, splitter),
  filament 2 = BODY (any colour - change it in Creality Print or map it to any CFS spool; the files ship with red
  as a placeholder), filament 3 = WHITE (DRL light signatures + badge details).
    1-swap_style\   black base + body-colour cap + white lights: about 8 filament changes per plate
    classic_style\  like your G80, white lights = top 1.2 mm of their inlay: about 21 changes per plate
  For a white body use the normal 2-colour files (1 change). Creality Print recalculates flush volumes when you
  change a filament colour. Pick body colours that contrast with black (red, blue, yellow, orange, grey, green).
  Preview images: <car>_preview_red/blue/yellow/grey.png.

SAMPLER PLATE
  All_Cars_Sampler_plate<k>of<n>_<m>x.3mf - one of each keychain, spread over as many K2 plates as needed
  (1-swap build, black + white Generic PLA @Creality K2 0.4 nozzle). Handy for test prints or a display set.

PRICING
  Pricing_Model.xlsx (editable costs -> per-car cost, prices, profit per channel) and PRICING_GUIDE.txt (summary).

NOTES
  - Plates were sliced with Creality Print's own engine from the command line (its multi-colour 3MF CLI
    path crashes, so each plate was sliced from per-colour STLs with the same settings). Please do one
    normal Slice in Creality Print before the first production run to confirm on your machine.
  - Badges (BMW roundel, Porsche/Lamborghini crest, Mercedes star, Audi rings, Corvette flags, Mustang
    pony) are brand trademarks. If you sell these, consider badge-free versions: set badge_on=False in the
    car's spec (see _source\\) and rebuild.
  - SOURCE.txt in each car folder lists the reference photo that was traced.
  - _source\\ has the generator (Python) and every car's spec, so any car can be edited and rebuilt:
      python _source\\lib\\export.py _source\\cars\\<car>\\spec.py <output folder>
"""
open(os.path.join(dest, 'README.txt'), 'w', encoding='utf-8').write(txt)
print(txt[:3000])
