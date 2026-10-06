"""The film's timeline, cut to "Ritual" by BalloonPlanet (Artlist licence, tagged in the file).
Analysis of the track (numpy/scipy, see analyse()): about 95 BPM, a bar is 2.5265 s, the drop lands at 94.69 s and
downbeats follow every bar from there. Every shot boundary below is a bar or beat of the song.
usage: python timeline.py [song.mp3]   -> src/timeline.json (read by Remotion and by blender/shots.py)
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SONG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'public', 'music', 'ritual.mp3')
FPS = 30
BAR = 2.5265
BEAT = BAR / 4
DROP = 94.69


def analyse(path):
    """re-measure the drop (largest rise in loudness between 85 s and 100 s) so a different edit of the file still lines up"""
    sr = 11025
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    win = sr // 8
    rms = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, 'same'))[::sr // 40]
    t = np.arange(len(rms)) / 40
    m = (t > 85) & (t < 100)
    rise = np.r_[0, np.diff(rms)]
    i = np.argmax(np.where(m, rise, -1))
    return float(t[i])


def fr(sec):
    return int(round(sec * FPS))


def build(start_bar, length_s, shots):
    """shots: [(name, bars)] from the window start; the last shot runs to the end of the window"""
    start = DROP + start_bar * BAR
    out, t = [], 0.0
    for i, (name, bars) in enumerate(shots):
        a = fr(t)
        t = length_s if bars is None else t + bars * BAR
        b = fr(t)
        out.append(dict(name=name, from_=a, dur=b - a))
    total = fr(length_s)
    beats = [fr(k * BEAT) for k in range(int(length_s / BEAT) + 2) if fr(k * BEAT) < total]
    drop_frame = fr(DROP - start)
    return dict(song_start=round(start, 3), frames=total, beats=beats, drop=drop_frame,
                shots=[{**s, 'from': s.pop('from_')} for s in out])


if __name__ == '__main__':
    # DROP is the kick onset measured on the low band (94.69 s); analyse() only reports the loudness rise as a check
    if os.path.exists(SONG):
        print('loudness rise at', round(analyse(SONG), 2), 's (kick onset used:', DROP, 's)')
    T = {
        'fps': FPS, 'bar': BAR, 'beat': BEAT, 'drop_s': round(DROP, 3),
        # 30 s: 4 moody bars of the breakdown, the drop on the headlights, then one idea per bar
        'launch': build(-4, 30.0, [('hook', 2), ('detail', 2), ('headlights', 1), ('colours', 1), ('flip', 1),
                                   ('garage', 1.5), ('wall', 1.25), ('spinner', 1), ('end', None)]),
        # 15 s: one bar before the drop
        'cutdown': build(-1, 15.0, [('hook', 1), ('headlights', 1), ('garage', 1), ('wall', 1), ('spinner', 1), ('end', None)]),
        'spinner_ad': build(-1, 12.0, [('macro', 1), ('spin', 1.5), ('specs', 1.25), ('price', None)]),
        'wall_ad': build(-1, 12.0, [('keys', 1.5), ('colours', 1.25), ('mount', 1), ('lineup', None)]),
    }
    out = os.path.join(HERE, 'src', 'timeline.json')
    json.dump(T, open(out, 'w'), indent=1)
    for k in ('launch', 'cutdown', 'spinner_ad', 'wall_ad'):
        print(k, T[k]['song_start'], 'drop@', T[k]['drop'], [(s['name'], s['from'], s['dur']) for s in T[k]['shots']])
