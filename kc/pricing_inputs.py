"""Write pricing_inputs.json + pricing_cars.json for make_pricing.py (measured slicer data + researched inputs)."""
import json, os
R = json.load(open('pricing_research.json'))
CARS = [(c['id'], c['name']) for c in json.load(open('cars_pkg.json'))]
cars = []
for cid, name in CARS:
    p = f'cars/{cid}/out/verify_report.json'
    if not os.path.exists(p):
        continue
    v = json.load(open(p))
    est = v['production']['plate']['estimate']; c2 = v['classic']['plate']['two_colour']; pc = v['classic']['plate']['per_change']
    cars.append(dict(car=name, n=v['plate_count'], swap_h=round(est['time_s'] / 3600, 3), swap_g=est['grams_total'],
                     cl_h=round(c2['time_s'] / 3600, 3), cl_g=round(sum(c2['grams_per_filament']), 2),
                     chg_min=round(pc['seconds'] / 60, 2), chg_g=pc['grams']))
json.dump(cars, open('pricing_cars.json', 'w'), indent=1)

S = {}
for f in R['checked']['findings']:
    S[f['item'][:40]] = f
src = lambda *keys: '; '.join(s['url'] for f in R['checked']['findings'] for s in f['sources'] if any(k.lower() in f['item'].lower() for k in keys))[:400]

inputs = {
 'groups': [
  {'title': 'Filament', 'rows': [
   {'key': 'filament_price_kg', 'label': 'PLA price per kg', 'value': 19.99, 'unit': '$/kg', 'fmt': 'usd', 'key_assumption': True,
    'note': 'Creality Hyper PLA 1 kg $19.99 (5 spools $16.99, 10 spools $15.99, 20 spools $14.99; RFID version $21). Budget PLA $10-14/kg.', 'source': src('Hyper PLA 1 kg')},
   {'key': 'failure_rate', 'label': 'Failed / reprinted share', 'value': 0.05, 'unit': '%', 'fmt': 'pct',
    'note': 'Allowance for failed plates and rejects. Proven files on a tuned K2: 3-5 %; new shop / new filament: 10 %.'},
  ]},
  {'title': 'Key ring hardware', 'rows': [
   {'key': 'ring_pack_price', 'label': 'Key ring pack price (ring + chain + jump ring)', 'value': 6.99, 'unit': '$', 'fmt': 'usd',
    'note': 'Your Amazon pack: KANSPHY 100 key rings with chain + 100 jump rings, 1 in split ring.', 'source': 'user (Amazon listing screenshot)'},
   {'key': 'ring_pack_qty', 'label': 'Sets per pack', 'value': 100, 'unit': 'pcs', 'fmt': 'int'},
   {'key': 'hardware_unit', 'label': 'Hardware cost per keychain', 'value': '={ring_pack_price}/{ring_pack_qty}', 'unit': '$', 'fmt': 'usd3'},
  ]},
  {'title': 'Printer (Creality K2 + CFS)', 'rows': [
   {'key': 'printer_price', 'label': 'Printer price', 'value': 549, 'unit': '$', 'fmt': 'usd', 'note': 'K2 Combo with CFS on the Creality store (K2 alone $399).', 'source': src('K2 printer price')},
   {'key': 'printer_life_h', 'label': 'Useful life', 'value': 5000, 'unit': 'print hours', 'fmt': 'int'},
   {'key': 'maint_h', 'label': 'Maintenance / wear (nozzles, plates, belts)', 'value': 0.03, 'unit': '$/h', 'fmt': 'usd3', 'source': src('wear cost')},
   {'key': 'power_kw', 'label': 'Average power while printing', 'value': 0.13, 'unit': 'kW', 'fmt': 'num2', 'note': 'Estimate (no measured K2 figure published; K1 ~0.10 kW).', 'source': src('power draw')},
   {'key': 'electricity_kwh', 'label': 'Electricity price', 'value': 0.1831, 'unit': '$/kWh', 'fmt': 'usd3', 'note': 'US average residential, EIA July 2026.', 'source': src('electricity')},
   {'key': 'machine_cost_h', 'label': 'Printer cost per print hour', 'value': '={printer_price}/{printer_life_h}+{maint_h}+{power_kw}*{electricity_kwh}', 'unit': '$/h', 'fmt': 'usd3'},
   {'key': 'print_hours_week', 'label': 'Print hours per week you run the printer', 'value': 100, 'unit': 'h/week', 'fmt': 'int', 'key_assumption': True},
  ]},
  {'title': 'Your time', 'rows': [
   {'key': 'labour_rate', 'label': 'Value of your time', 'value': 20, 'unit': '$/h', 'fmt': 'usd', 'key_assumption': True},
   {'key': 'labour_min_plate', 'label': 'Per plate: start print, remove plate, clean', 'value': 5, 'unit': 'min', 'fmt': 'num1'},
   {'key': 'labour_min_unit', 'label': 'Per keychain: pop off, check, fit ring, bag + card', 'value': 1.5, 'unit': 'min', 'fmt': 'num1'},
   {'key': 'labour_min_order', 'label': 'Per shipped order: pack, label, messages', 'value': 4, 'unit': 'min', 'fmt': 'num1'},
  ]},
  {'title': 'Packaging and shipping', 'rows': [
   {'key': 'packaging_unit', 'label': 'Per keychain: zip bag + backing card + thank-you card', 'value': 0.19, 'unit': '$', 'fmt': 'usd', 'source': src('Packaging')},
   {'key': 'mailer', 'label': 'Per order: #000 bubble mailer', 'value': 0.20, 'unit': '$', 'fmt': 'usd', 'note': '$0.11 each in 500s, ~$0.25 in small packs.'},
   {'key': 'label', 'label': 'Per order: USPS Ground Advantage label', 'value': 6.00, 'unit': '$', 'fmt': 'usd', 'key_assumption': True,
    'note': '$5.50-6.36 to normal lower-48 addresses via label platforms (incl. 2026 surcharge); up to $8.40 rural/AK/HI. A stamped letter is not valid for a rigid keychain.', 'source': src('USPS')},
  ]},
  {'title': 'Fees', 'rows': [
   {'key': 'etsy_listing', 'label': 'Etsy listing fee (charged per unit sold)', 'value': 0.20, 'unit': '$', 'fmt': 'usd', 'source': src('Etsy fee')},
   {'key': 'etsy_tx', 'label': 'Etsy transaction fee (on item + shipping)', 'value': 0.065, 'unit': '%', 'fmt': 'pct'},
   {'key': 'etsy_proc_pct', 'label': 'Etsy payment processing %', 'value': 0.03, 'unit': '%', 'fmt': 'pct'},
   {'key': 'etsy_proc_fixed', 'label': 'Etsy payment processing fixed (per order)', 'value': 0.25, 'unit': '$', 'fmt': 'usd'},
   {'key': 'etsy_offsite', 'label': 'Etsy Offsite Ads fee (when an order comes from an ad)', 'value': 0.15, 'unit': '%', 'fmt': 'pct', 'note': '15 % (12 % and mandatory after $10k sales/year), capped at $100 per order.'},
   {'key': 'etsy_offsite_share', 'label': 'Share of Etsy orders that come from Offsite Ads', 'value': 0.10, 'unit': '%', 'fmt': 'pct'},
   {'key': 'card_pct', 'label': 'In-person card reader % (e.g. Square)', 'value': 0.026, 'unit': '%', 'fmt': 'pct'},
   {'key': 'card_fixed', 'label': 'In-person card reader fixed (per sale)', 'value': 0.15, 'unit': '$', 'fmt': 'usd'},
   {'key': 'card_share', 'label': 'Share of in-person sales paid by card', 'value': 0.6, 'unit': '%', 'fmt': 'pct'},
  ]},
  {'title': 'Custom body colour', 'rows': [
   {'key': 'custom_extra_changes', 'label': 'Extra filament changes per plate (custom colour, 1-swap style)', 'value': 7, 'unit': 'changes', 'fmt': 'int',
    'note': 'Custom-colour plates need ~8 changes instead of 1 (body colour + white lights on every cap layer). Measured per-change cost per car is on Per Car.'},
  ]},
 ],
}
fee_etsy = '{etsy_listing}+({etsy_tx}+{etsy_proc_pct}+{etsy_offsite_share}*{etsy_offsite})*({price}+{ship}/{units})+{etsy_proc_fixed}/{units}'
ship_order = '({label}+{mailer}+{labour_min_order}/60*{labour_rate})/{units}'
inputs['channels'] = [
 {'name': 'Etsy - single, FREE shipping', 'price': 16.99, 'units': 1, 'ship_charged': 0, 'fee_formula': fee_etsy, 'ship_formula': ship_order,
  'note': 'Headline price. Sits under enamel/metal car-front keychains ($15.99-18.99 free shipping) and above plain single-colour prints ($10-15 + shipping).'},
 {'name': 'Etsy - single, $5.99 shipping', 'price': 12.99, 'units': 1, 'ship_charged': 5.99, 'fee_formula': fee_etsy, 'ship_formula': ship_order,
  'note': 'Same order value split into item + shipping. Etsy search favours free shipping in the US, so prefer the free-shipping version.'},
 {'name': 'Etsy - 3-pack (any cars), free shipping', 'price': 13.33, 'units': 3, 'ship_charged': 0, 'fee_formula': fee_etsy, 'ship_formula': ship_order,
  'note': '$39.99 for 3. One label for three keychains is where the profit is.'},
 {'name': 'Etsy - custom body colour, free shipping', 'price': 18.99, 'units': 1, 'ship_charged': 0, 'fee_formula': fee_etsy, 'ship_formula': ship_order, 'custom': True,
  'note': '+$2 for any body colour. Covers the ~7 extra filament changes and purge per plate; mostly printed as small batches.'},
 {'name': 'Car meet / in person - single', 'price': 10.00, 'units': 1, 'ship_charged': 0,
  'fee_formula': '{card_share}*({card_pct}*{price}+{card_fixed}/{units})', 'ship_formula': '0',
  'note': 'Cash-friendly round number. No shipping or platform fees.'},
 {'name': 'Car meet / in person - 3 for $25', 'price': 8.33, 'units': 3, 'ship_charged': 0,
  'fee_formula': '{card_share}*({card_pct}*{price}+{card_fixed}/{units})', 'ship_formula': '0',
  'note': 'Bundle to move volume at meets.'},
 {'name': 'Car club / group order (10+ same car)', 'price': 9.00, 'units': 10, 'ship_charged': 8.00, 'fee_formula': '0.029*({price}+{ship}/{units})+0.30/{units}',
  'ship_formula': ship_order, 'note': 'Invoice (e.g. PayPal/Stripe ~2.9 % + $0.30). Custom colour of the club at no extra charge.'},
 {'name': 'Wholesale to shops (20+)', 'price': 7.00, 'units': 20, 'ship_charged': 0, 'fee_formula': '0',
  'ship_formula': '({label}+2+{labour_min_order}/60*{labour_rate})/{units}', 'note': 'About 50 % of a ~$15 retail price (keystone). Shop sells at $14.99.'},
]
inputs['recommendations'] = [
 '1. Etsy: $16.99 with free shipping per keychain (or $12.99 + $5.99 shipping); 3 for $39.99; custom body colour +$2.',
 '2. Car meets / in person: $10 each or 3 for $25. Bring a mix of the 9 cars in black/white plus a few popular colours.',
 '3. Car clubs (10+ of one car, club colour): $9 each. Wholesale to shops (20+): $7 each (they retail at ~$15).',
 '4. Print the 1-swap PLATE files for stock. Keychains cost ~$0.25-0.35 in materials + printer time; your time and shipping are the real costs.',
 '5. Bundle to spread the ~$6 shipping label: a 3-pack earns far more per keychain than three single orders.',
 '6. Custom colours: printed as smaller batches (8 filament changes per plate); the +$2 covers the extra purge and printer time.',
 '7. Brand logos and names (BMW, Porsche, Mercedes, Ford/Shelby, Chevrolet, Audi, Lamborghini) are trademarks. Selling them risks takedowns on Etsy/eBay.',
 '   Lower-risk option: sell badge-free versions (set badge_on=False / SHOW_BADGE=False and rebuild) and describe cars generically, not with brand logos.',
 '8. Re-check your numbers every few months: filament deals, USPS prices and Etsy fees change. Edit the blue cells on Inputs.',
]
srcs = []
for f in R['checked']['findings']:
    srcs.append({'item': f['item'], 'finding': f['value'][:600], 'url': '; '.join(s['url'] for s in f['sources'])[:900]})
for blk in R['research']:
    for f in blk['r']['findings'][:14]:
        srcs.append({'item': f'[{blk["key"]}] ' + f['item'], 'finding': f['value'][:500], 'url': '; '.join(s['url'] for s in f['sources'])[:900]})
inputs['sources'] = srcs
json.dump(inputs, open('pricing_inputs.json', 'w'), indent=1)
print(len(cars), 'cars;', len(srcs), 'sources')
