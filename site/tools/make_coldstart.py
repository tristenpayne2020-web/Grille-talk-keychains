"""Cold start of a modified straight-six (S58-style, G80 M3), synthesised sample by sample. No recording is used, so
there is nothing to license. Writes:
  site/build/coldstart.wav             full-quality preview
  theme/assets/coldstart-audio.js      the MP3, base64 in an ES module (Shopify serves it like any theme script)

Model: an rpm curve (starter crank, catch, flare, cold high idle) drives individual combustion events (three per
crank revolution on a straight six) with per-cylinder strength and timing variation, shaped by exhaust resonances and
a soft clipper for the rasp; plus starter whir, a bark on the catch, crackle and pops on the lift-off after the flare
(the modified-exhaust character), turbo whoosh, intake noise, and a short garage reflection.
usage: python site/tools/make_coldstart.py
"""
import base64, os, subprocess, wave
import numpy as np
from scipy import signal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SR = 44100
DUR = 4.6
rng = np.random.default_rng(80)        # fixed seed: the same sound every build
t = np.arange(int(SR * DUR)) / SR


def smooth_step(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def rpm_curve(t):
    crank_end = 0.62
    r = np.full_like(t, 260.0)
    r += 40 * np.sin(2 * np.pi * 4.4 * t)                          # compression strokes load the starter
    catch = t >= crank_end
    tc = t[catch] - crank_end
    flare = 300 + 2950 * (1 - np.exp(-tc / 0.13))                  # snaps up to ~3250 rpm
    drop = np.where(tc > 0.42, (tc - 0.42), 0)
    flare = flare - (3250 - 1750) * smooth_step(drop / 0.75)        # lifts off to the cold high idle
    flare += np.where(tc > 1.2, 70 * np.sin(2 * np.pi * 0.9 * (tc - 1.2)), 0)   # idle hunting while cold
    r[catch] = flare
    return r, crank_end


def biquad_bandpass(x, f, q):
    b, a = signal.iirpeak(f / (SR / 2), q)
    return signal.lfilter(b, a, x)


def main():
    rpm, crank_end = rpm_curve(t)
    out = np.zeros_like(t)

    # ---- combustion events (after the catch): three per revolution on an inline six
    fire_hz = rpm / 60 * 3
    phase = np.cumsum(fire_hz) / SR
    events = np.where(np.diff(np.floor(phase)) > 0)[0]
    events = events[t[events] >= crank_end]
    load = np.interp(t, [0, crank_end, crank_end + 0.1, crank_end + 0.5, crank_end + 0.9, DUR], [0, 1.0, 1.0, 0.9, 0.55, 0.5])
    cyl_gain = 1 + rng.normal(0, 0.13, 6)                           # uneven cylinders while cold: the rasp
    pulses = np.zeros_like(t)
    for k, i in enumerate(events):
        j = i + int(rng.normal(0, 0.0004) * SR)
        if 0 <= j < len(t):
            pulses[j] += cyl_gain[k % 6] * load[j] * (1 + rng.normal(0, 0.06))
    # each event: a short damped thump plus a click
    n = int(0.03 * SR)
    tt = np.arange(n) / SR
    thump = np.exp(-tt / 0.0065) * np.sin(2 * np.pi * 105 * tt) + 0.5 * np.exp(-tt / 0.0025) * np.sin(2 * np.pi * 290 * tt)
    click = rng.normal(0, 1, int(0.003 * SR)) * np.exp(-np.arange(int(0.003 * SR)) / (0.0008 * SR))
    engine = signal.fftconvolve(pulses, thump)[: len(t)] + 0.12 * signal.fftconvolve(pulses, click)[: len(t)]
    # exhaust resonances (downpipes and a valved back box), then soft clipping for the rasp
    ex = 1.0 * biquad_bandpass(engine, 95, 2.0) + 0.8 * biquad_bandpass(engine, 240, 2.5) + 0.45 * biquad_bandpass(engine, 620, 3.0) + 0.25 * engine
    ex = np.tanh(ex * 2.6) * 0.8
    rasp = signal.lfilter(*signal.butter(2, [1400 / (SR / 2), 4200 / (SR / 2)], 'band'), ex) * 0.35
    out += ex + rasp * np.clip((rpm - 1400) / 1800, 0, 1)

    # ---- starter: whir, gear noise, compression chugs
    pre = t < crank_end + 0.05
    env = smooth_step(t / 0.05) * (1 - smooth_step((t - crank_end + 0.03) / 0.06))
    whir_f = 980 + 220 * smooth_step(t / crank_end)
    whir = np.sin(2 * np.pi * np.cumsum(whir_f) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(whir_f) / SR)
    gear = signal.lfilter(*signal.butter(2, [1800 / (SR / 2), 3600 / (SR / 2)], 'band'), rng.normal(0, 1, len(t)))
    chug_phase = np.cumsum(np.full_like(t, 260 / 60 * 3)) / SR
    chug = (0.5 + 0.5 * np.cos(2 * np.pi * chug_phase)) ** 6
    low = biquad_bandpass(rng.normal(0, 1, len(t)), 70, 1.5)
    starter = (0.16 * whir + 0.12 * gear) * (0.6 + 0.4 * chug) + 1.1 * low * chug
    out += np.where(pre, starter * env, 0)

    # ---- the catch: a bark
    i0 = int(crank_end * SR)
    nb = int(0.25 * SR)
    bark = biquad_bandpass(rng.normal(0, 1, nb), 140, 1.2) * np.exp(-np.arange(nb) / (0.05 * SR)) * 2.2
    out[i0:i0 + nb] += np.tanh(bark)

    # ---- crackle and pops on the lift-off (modified exhaust), thinning out as it settles
    tp = crank_end + 0.55
    while tp < crank_end + 2.1:
        tp += rng.uniform(0.045, 0.16) * (1 + (tp - crank_end - 0.55) * 1.4)
        i = int(tp * SR)
        m = int(rng.uniform(0.004, 0.012) * SR)
        if i + m >= len(t):
            break
        pop = rng.normal(0, 1, m) * np.exp(-np.arange(m) / (m / 4))
        pop = signal.lfilter(*signal.butter(2, 600 / (SR / 2), 'high'), pop) * rng.uniform(0.35, 0.9)
        out[i:i + m] += pop
        if rng.random() < 0.35:                                     # the occasional deeper pop
            m2 = int(0.03 * SR)
            out[i:i + m2] += 0.5 * np.exp(-np.arange(m2) / (0.006 * SR)) * np.sin(2 * np.pi * 80 * np.arange(m2) / SR)

    # ---- turbo whoosh and intake
    boost = np.clip((rpm - 1500) / 1700, 0, 1) * (t > crank_end)
    whoosh = signal.lfilter(*signal.butter(2, [2200 / (SR / 2), 5200 / (SR / 2)], 'band'), rng.normal(0, 1, len(t))) * 0.022 * boost
    whistle = 0.012 * boost * np.sin(2 * np.pi * np.cumsum(3800 + 1600 * boost) / SR)
    intake = signal.lfilter(*signal.butter(1, 900 / (SR / 2)), rng.normal(0, 1, len(t))) * 0.018 * load * (t > crank_end)
    out += whoosh + whistle + intake

    # ---- garage: a few early reflections
    for d, g in ((0.019, 0.28), (0.031, 0.2), (0.047, 0.14), (0.071, 0.08)):
        k = int(d * SR)
        out[k:] += g * out[:-k]

    # ---- master: fade out, normalise to -1 dBFS
    fade = 1 - smooth_step((t - (DUR - 1.1)) / 1.1)
    out *= fade * smooth_step(t / 0.01)
    out = out / np.max(np.abs(out)) * 0.89

    os.makedirs(os.path.join(ROOT, 'site', 'build'), exist_ok=True)
    wav = os.path.join(ROOT, 'site', 'build', 'coldstart.wav')
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype('<i2').tobytes())
    mp3 = os.path.join(ROOT, 'site', 'build', 'coldstart.mp3')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-codec:a', 'libmp3lame', '-b:a', '96k', mp3], check=True)
    data = base64.b64encode(open(mp3, 'rb').read()).decode()
    js = ('// Generated by site/tools/make_coldstart.py: a synthesised straight-six cold start (MP3, base64). Do not edit.\n'
          f'export const COLDSTART_MP3 = "data:audio/mpeg;base64,{data}";\n')
    open(os.path.join(ROOT, 'theme', 'assets', 'coldstart-audio.js'), 'w').write(js)
    print('coldstart.wav', round(len(t) / SR, 2), 's;', 'mp3', os.path.getsize(mp3) // 1024, 'KB')


if __name__ == '__main__':
    main()
