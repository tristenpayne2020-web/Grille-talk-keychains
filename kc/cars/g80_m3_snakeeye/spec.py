"""BMW M3 (G80) with snake-eye DRLs: the user's own G80 (spec_from_step.pkl) with the stock hexagonal L DRL replaced by
two near-vertical bars per headlight (see ../_snakeeye.py). The approved G80 stays untouched."""
import os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import _snakeeye
_base = pickle.load(open(os.path.join(HERE, '..', 'g80_m3', 'spec_from_step.pkl'), 'rb'))
SPEC = _snakeeye.make(_base, 2, 'g80_m3_snakeeye', 'BMW M3 (G80) - snake-eye DRL')
