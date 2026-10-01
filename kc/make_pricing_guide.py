"""PRICING_GUIDE.txt from the evaluated workbook."""
import sys, warnings, formulas
warnings.filterwarnings('ignore')
xlsx, out = sys.argv[1], sys.argv[2]
sol = formulas.ExcelModel().loads(xlsx).finish().calculate()
V = {}
for k, v in sol.items():
    try: V[k.upper().split(']')[-1]] = v.value[0][0]
    except Exception: pass
g = lambda sh, c: V.get(f"{sh.upper()}'!{c}", V.get(f"{sh.upper()}!{c}"))
money = lambda x: f'${float(x):,.2f}' if x not in (None, '') else '-'
lines = ['KEYCHAIN PRICING GUIDE (US, Creality K2, 1-swap plate files)', '=' * 62, '',
         'Open Pricing_Model.xlsx to change any cost (blue cells) - every number below recalculates.', '']
lines.append('COST TO MAKE ONE KEYCHAIN (average car, batched on a full plate)')
for lab, col in (('Filament (incl. purge + 5% failures)', 'I'), ('Printer time (depreciation, wear, power)', 'J'),
                 ('Key ring + chain + jump ring ($6.99 / 100)', 'K'), ('Your time (plate + ring + bag, $20/h)', 'L'),
                 ('Bag + backing card + thank-you card', 'M'), ('TOTAL (1-swap build)', 'N'), ('Classic build (15 swaps/plate)', 'O'),
                 ('Custom body colour (8 swaps/plate)', 'P')):
    r = 5
    while g('Per Car', f'A{r}') not in ('Average', None):
        r += 1
    lines.append(f'  {lab:<46} {money(g("Per Car", f"{col}{r}"))}')
lines += ['', 'Printer time per keychain is about 19-25 minutes; one K2 running 100 h/week makes ~240-310 keychains.', '']
lines.append('RECOMMENDED PRICES AND PROFIT PER KEYCHAIN')
lines.append(f"  {'channel':<44}{'price':>9}{'profit':>9}{'margin':>8}")
r = 5
while g('Price Guide', f'A{r}'):
    a = g('Price Guide', f'A{r}')
    if not isinstance(a, str) or a.startswith('Etsy price needed'):
        break
    lines.append(f"  {a:<44}{money(g('Price Guide', f'B{r}')):>9}{money(g('Price Guide', f'H{r}')):>9}{float(g('Price Guide', f'I{r}')) * 100:>7.0f}%")
    r += 1
lines += ['', '  (profit is after making cost, Etsy/payment fees, the ~$6 shipping label, mailer and packing time)', '']
lines.append('ETSY PRICE FOR A TARGET PROFIT (single keychain, free shipping)')
for q in range(r + 1, r + 8):
    t, p = g('Price Guide', f'A{q}'), g('Price Guide', f'B{q}')
    if isinstance(t, (int, float)):
        lines.append(f'  profit {money(t):>7} per keychain  ->  price {money(p)}')
lines += ['', 'PER CAR (1-swap build)']
lines.append(f"  {'car':<34}{'per plate':>10}{'plate time':>12}{'min/keychain':>14}{'cost':>8}")
r = 5
while g('Per Car', f'A{r}') not in ('Average', None):
    h = float(g('Per Car', f'C{r}'))
    lines.append(f"  {g('Per Car', f'A{r}'):<34}{int(g('Per Car', f'B{r}')):>10}{int(h):>6}h {int(round((h % 1) * 60)):02d}m{float(g('Per Car', f'R{r}')):>14.1f}{money(g('Per Car', f'N{r}')):>8}")
    r += 1
r0 = r
lines += ['', 'NOTES']
r = 5
while g('Price Guide', f'A{r}') is not None or r < 60:
    a = g('Price Guide', f'A{r}')
    if isinstance(a, str) and a[:2] in ('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '  ') and not a.startswith('Etsy'):
        lines.append('  ' + a)
    r += 1
    if r > 80: break
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
