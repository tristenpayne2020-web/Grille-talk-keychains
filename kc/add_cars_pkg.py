"""Add finished cars to cars_pkg.json (the packaging list). usage: python add_cars_pkg.py id [id ...]"""
import json, os, sys
SP = os.path.dirname(os.path.abspath(__file__))
NAMES = {
    'r35_gtr': ('Nissan_GTR_R35', 'Nissan GT-R (R35, 2017+)'),
    'g20_m340i_lci': ('BMW_M340i_G20_LCI', 'BMW M340i (G20 LCI, 2023+)'),
    'camaro_zl1': ('Chevrolet_Camaro_ZL1', 'Chevrolet Camaro ZL1 (6th gen)'),
    'mclaren_720s': ('McLaren_720S', 'McLaren 720S'),
    'ct5v_blackwing': ('Cadillac_CT5V_Blackwing', 'Cadillac CT5-V Blackwing'),
    'charger_srt': ('Dodge_Charger_SRT_Hellcat', 'Dodge Charger SRT Hellcat (widebody)'),
    'mk5_supra': ('Toyota_GR_Supra_MK5', 'Toyota GR Supra (A90 / MK5)'),
    'challenger_hellcat': ('Dodge_Challenger_SRT_Hellcat', 'Dodge Challenger SRT Hellcat'),
    'f92_m8': ('BMW_M8_F92', 'BMW M8 Competition (F92)'),
    'e30_m3': ('BMW_M3_E30', 'BMW M3 (E30)'),
    'f87_m2': ('BMW_M2_F87', 'BMW M2 Competition (F87)'),
    'amg_gt63_4door': ('Mercedes_AMG_GT63_4door', 'Mercedes-AMG GT 63 S 4-Door'),
    'c7_z06': ('Corvette_C7_Z06', 'Chevrolet Corvette C7 Z06'),
    'g42_m240i_lci': ('BMW_M240i_G42', 'BMW M240i (G42)'),
    'lexus_is350': ('Lexus_IS350_FSport', 'Lexus IS 350 F Sport'),
    'civic_11th': ('Honda_Civic_11th_gen', 'Honda Civic (11th gen)'),
    'camry_xv80': ('Toyota_Camry_XV80', 'Toyota Camry (2025+)'),
}


def ref_info(cid):
    for fn in ('batch3_result.json', 'batch5_result.json'):
        if os.path.exists(fn):
            for c in json.load(open(fn)).get('cars', []):
                if c and c.get('id') == cid and c.get('result'):
                    return c['result'].get('ref_url'), c['result'].get('ref_license')
    src = os.path.join('cars', cid, 'ref', 'SOURCE.txt')
    if os.path.exists(src):
        t = open(src, encoding='utf-8', errors='ignore').read()
        url = next((w for w in t.split() if w.startswith('http')), 'see ref/SOURCE.txt')
        lic = next((l.split(':', 1)[1].strip() for l in t.splitlines() if l.lower().startswith(('licence', 'license'))), 'see ref/SOURCE.txt')
        return url, lic
    return 'n/a', 'n/a'


cars = json.load(open('cars_pkg.json'))
have = {c['id'] for c in cars}
for cid in sys.argv[1:]:
    if cid in have or not os.path.exists(f'cars/{cid}/out/build_report.json'):
        continue
    for qf in ('queue_batch6.json', 'queue_batch7.json', 'queue_batch8.json'):
        if cid not in NAMES and os.path.exists(qf):
            for q in json.load(open(qf))['cars']:
                NAMES[q['id']] = (q['folder'], q['name'])
    folder, name = NAMES[cid]
    url, lic = ref_info(cid)
    cars.append(dict(id=cid, folder=folder, name=name, spec=os.path.join(SP, 'cars', cid, 'spec.py'), out=f'cars/{cid}/out', ref_url=url, ref_license=lic))
json.dump(cars, open('cars_pkg.json', 'w'), indent=1)
print(len(cars), [c['id'] for c in cars])
