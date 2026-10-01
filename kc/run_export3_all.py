import subprocess, sys, time, json, os
cars=[('g80_m3','cars/g80_m3/spec_from_step.pkl')]+[(c,f'cars/{c}/spec.py') for c in ('g87_m2','f82_m4','gt3rs_992','c8_corvette','r8_audi','svj_aventador','amg_gt')]
if len(sys.argv)>1: cars=[c for c in cars if c[0] in sys.argv[1:]] or [(a, f'cars/{a}/spec.py') for a in sys.argv[1:]]
for cid,spec in cars:
    t=time.time()
    r=subprocess.run([sys.executable,'lib/export3.py',spec,f'cars/{cid}/out'],capture_output=True,text=True)
    rep=json.load(open(f'cars/{cid}/out/custom_colour_report.json')) if os.path.exists(f'cars/{cid}/out/custom_colour_report.json') else {}
    lost=sum((v or {}).get('n_lost') or 0 for st in ('production3','classic3') for v in rep.get(st,{}).get('slicecheck',{}).values())
    print(cid,'exit',r.returncode,round(time.time()-t),'s','lights',rep.get('light_islands'),'changes',rep.get('production3',{}).get('changes_per_plate'),rep.get('classic3',{}).get('changes_per_plate'),'lost',lost,flush=True)
    if r.returncode: print(r.stderr[-1200:],flush=True)
print('ALL DONE',flush=True)
