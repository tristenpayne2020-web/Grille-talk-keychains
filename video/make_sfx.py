"""Synthesise the film's sound design (no samples, no music): python make_sfx.py -> public/sfx/*.wav (48 kHz mono).
Also writes music_bed_PLACEHOLDER.wav (silence) per composition length so a licensed song can be dropped in."""
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'sfx')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def t_(d):
    return np.arange(int(SR * d)) / SR


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)


def lp(x, hi, order=2):
    return sosfilt(butter(order, hi, btype='low', fs=SR, output='sos'), x)


def hp(x, lo, order=2):
    return sosfilt(butter(order, lo, btype='high', fs=SR, output='sos'), x)


def save(name, x, peak=0.8):
    x = np.asarray(x, dtype=np.float64)
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    fade = min(len(x), int(0.004 * SR))
    x[-fade:] *= np.linspace(1, 0, fade)
    wavfile.write(os.path.join(OUT, name), SR, (x * 32767).astype(np.int16))


# light snap: a relay clunk + a low thump + a faint mains hum tail (the spotlight switching on)
t = t_(0.9)
click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t / 0.004)
thump = np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.07)
hum = (np.sin(2 * np.pi * 100 * t) + 0.4 * np.sin(2 * np.pi * 200 * t)) * 0.06 * np.clip((t - 0.03) / 0.05, 0, 1) * np.exp(-t / 0.45)
save('snap.wav', click * 0.8 + thump * 0.9 + hum)

# whoosh: band-passed noise with a rising then falling sweep
for name, d in (('whoosh.wav', 0.7), ('whoosh_short.wav', 0.35)):
    t = t_(d)
    n = rng.standard_normal(len(t))
    env = np.sin(np.pi * t / d) ** 2
    lo_band = bp(n, 300, 1400) * (1 - t / d)
    hi_band = bp(n, 1200, 6000) * (t / d)
    save(name, (lo_band + hi_band) * env, 0.6)

# tick: a crisp click (headlight change, colour snaps, garage cuts)
t = t_(0.12)
save('tick.wav', bp(rng.standard_normal(len(t)), 1800, 9000) * np.exp(-t / 0.006) + 0.5 * np.sin(2 * np.pi * 1900 * t) * np.exp(-t / 0.01), 0.55)

# chain rattle: a few tiny metallic hits (the keychain settling on its chain)
t = t_(0.6)
x = np.zeros_like(t)
for k, at in enumerate((0.0, 0.07, 0.13, 0.2, 0.29, 0.4)):
    m = t >= at
    tt = t[m] - at
    a = 1.0 * (0.75 ** k)
    x[m] += a * sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.03) for f in (3100, 4700, 6900))
save('chain.wav', x, 0.4)

# keys: jingle on landing on the hook
t = t_(1.0)
x = np.zeros_like(t)
for k, at in enumerate((0.0, 0.05, 0.11, 0.18, 0.3, 0.45)):
    m = t >= at
    tt = t[m] - at
    a = 0.8 ** k
    x[m] += a * sum(np.sin(2 * np.pi * f * tt + p) * np.exp(-tt / d) for f, p, d in ((2300, 0.1, 0.12), (3550, 1.2, 0.08), (5200, 2.0, 0.05), (7300, 0.5, 0.03)))
save('keys.wav', x, 0.45)

# low impact: sub drop + soft noise burst (logo)
t = t_(1.8)
f = 62 * np.exp(-t / 0.9) + 32
ph = 2 * np.pi * np.cumsum(f) / SR
sub = np.sin(ph) * np.exp(-t / 0.55)
burst = lp(rng.standard_normal(len(t)), 900) * np.exp(-t / 0.08) * 0.5
save('impact.wav', sub + burst, 0.85)

# shimmer: the light sweep over the logo
t = t_(1.0)
n = rng.standard_normal(len(t))
env = np.sin(np.pi * t / 1.0) ** 3
save('shimmer.wav', bp(n, 5000, 12000) * env * 0.6 + bp(n, 2500, 5000) * env * 0.3, 0.35)

# bearing whirr: tone and band-passed noise that follow a spin-up / coast-down (4 s and 2.6 s versions)
for name, d in (('whirr.wav', 4.0), ('whirr_short.wav', 2.6)):
    t = t_(d)
    u = t / d
    speed = np.where(u < 0.12, 0, np.where(u < 0.45, 1 - np.exp(-(u - 0.12) * d / 0.18), (1 - np.exp(-(0.33) * d / 0.18)) * np.clip(1 - (u - 0.45) / 0.41, 0, 1) ** 2.2))
    fr = 90 + 520 * speed
    ph = 2 * np.pi * np.cumsum(fr) / SR
    tone = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.2 * np.sin(5.3 * ph)) * speed
    noise = bp(rng.standard_normal(len(t)), 1500, 7000) * speed ** 1.5 * 0.5
    rattle = bp(rng.standard_normal(len(t)), 300, 900) * speed * 0.25 * (1 + 0.5 * np.sin(ph / 7))
    save(name, tone * 0.5 + noise + rattle, 0.55)

# music bed placeholder: silence, one per composition length
for name, d in (('music_bed_PLACEHOLDER_30s.wav', 30), ('music_bed_PLACEHOLDER_15s.wav', 15), ('music_bed_PLACEHOLDER_12s.wav', 12)):
    wavfile.write(os.path.join(OUT, name), SR, np.zeros(int(SR * d), dtype=np.int16))
print('wrote', sorted(os.listdir(OUT)))
