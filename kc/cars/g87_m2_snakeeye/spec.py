"""BMW M2 (G87) with snake-eye DRLs: the approved G87 spec with its hockey-stick DRL stroke (prim 3) replaced by two
near-vertical bars per headlight (see ../_snakeeye.py). The approved G87 stays untouched."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import _snakeeye
_sp = importlib.util.spec_from_file_location('g87base', os.path.join(HERE, '..', 'g87_m2', 'spec_APPROVED_by_user.py') if os.path.exists(os.path.join(HERE, '..', 'g87_m2', 'spec_APPROVED_by_user.py')) else os.path.join(HERE, '..', 'g87_m2', 'spec.py'))
_m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m)
_base = dict(_m.SPEC); _base['_dir'] = os.path.join(HERE, '..', 'g87_m2')
# user feedback 2026-10-01: bars a little shorter and a little more tilted than the first version (1.0 / 0.35 mm)
SPEC = _snakeeye.make(_base, 3, 'g87_m2_snakeeye', 'BMW M2 (G87) - snake-eye DRL', length=0.75, lean=1.1)
