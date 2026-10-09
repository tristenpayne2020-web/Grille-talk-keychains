"""The one-take ad, rendered in Blender (headless), in three acts that Remotion joins with zoom transitions:
  kc    the G80 keychain front and centre; eight keychains in other colours come out from inside it, circle it, go back
        in; it flips; the camera pushes in on the left of the carbon back, pans slowly to the right, then dives in
  wall  (out of the dive) the G80 wall key holder, detail by detail (light signature, grille, hooks); pull back; the
        other six holders come out of it and circle it, go back in; it flips; the camera dives into its back plate
  spin  (out of the dive) the three keychain spinners under their beams, spinning up and settling with the rings down
usage: blender -b --factory-startup -P video/blender/oner.py -- act=kc w=1080 h=1920 out=<dir> [test=0,100] [samples=64]
Timing (frames at 30 fps) comes from src/timeline.json ('oner'), which is cut to the song's bars."""
import bpy, json, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gt

A = dict(a.split('=', 1) for a in sys.argv[sys.argv.index('--') + 1:])
ACT, W, H = A['act'], int(A['w']), int(A['h'])
OUT = os.path.abspath(A['out'])
SAMPLES = int(A.get('samples', 64))
PORTRAIT = H > W
TL = json.load(open(os.path.join(HERE, '..', 'src', 'timeline.json')))['oner']
SEG = {s['name']: s for s in TL['shots']}
BAR = TL['bar_frames']
BEAT = BAR / 4
FPS = 30

scene = gt.new_scene(W, H, 'EEVEE', SAMPLES)
scene.view_settings.exposure = float(A.get('ev', -0.6 if ACT == 'spin' else -2.3))
gt.EMIT_GAIN = 5.0
T = gt.Track()


# ---------------------------------------------------------------- helpers
def clamp01(x):
    return max(0.0, min(1.0, x))


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def smoother(x):
    x = clamp01(x)
    return x * x * x * (x * (x * 6 - 15) + 10)


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def spring(t, w=11.0, z=0.4):
    if t <= 0:
        return 0.0
    wd = w * math.sqrt(1 - z * z)
    return 1 - math.exp(-z * w * t) * (math.cos(wd * t) + z * w / wd * math.sin(wd * t))


def lerp(a, b, t):
    return a + (b - a) * t


def vlerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def seg(name):
    s = SEG[name]
    return s['from'], s['from'] + s['dur']


def local(f, name):
    """0..1 progress of frame f through segment `name`"""
    a, b = seg(name)
    return clamp01((f - a) / max(1, b - a))


def stage(k=1.0, haze=0.05, beam=1.0, rim=1.0):
    """the dark stage of the other films, scaled by k (k = 2.7 for the wall key holder)"""
    gt.haze(center=(0, 0.2 * k, 0.2 * k), size=(2.2 * k, 2.2 * k, 1.8 * k), density=haze * 6.0 / k)
    beams = [gt.spot('beam', (0, 0.004 * k, 0.17 * k), (0, 0.004 * k, -0.1 * k), 55 * beam * k * k, angle_deg=30,
                     blend=0.35, radius=0.004 * k, volume=1.0)]
    key = gt.spot('key', (0.05 * k, -0.55 * k, 0.42 * k), (0, 0, -0.005 * k), 160 * k * k, angle_deg=14 if k == 1 else 18,
                  blend=0.6, radius=0.05 * k, volume=0.0)
    r1 = gt.area('rim_l', (-0.35 * k, 0.35 * k, 0.12 * k), (0, 0, 0), 40 * rim * k * k, 0.25 * k, color='#cfe0ff')
    r2 = gt.area('rim_r', (0.38 * k, 0.32 * k, 0.2 * k), (0, 0, 0), 32 * rim * k * k, 0.25 * k, color='#dce8ff')
    fill = gt.area('fill', (0.0, -0.6 * k, 0.05 * k), (0, 0, 0), 6 * k * k, 0.8 * k, color='#fff4e6')
    fl = gt.floor(-0.085 * k * (1.6 if k > 1 else 1.0), color=(0.004, 0.004, 0.005, 1), rough=0.3)
    gt.exclude_from(fl, r1, r2)
    return dict(beams=beams, key=key, rims=(r1, r2), fill=fill, floor=fl)


def camera(lens=85):
    cam = gt.camera(lens=lens)
    T.obj(cam)
    T.prop(cam.data.dof, 'focus_distance')
    T.prop(cam.data.dof, 'aperture_fstop')
    return cam


def look(cam, pos, target, fstop=5.6, focus=None):
    gt.place_cam(cam, pos, target)
    gt.dof(cam, focus if focus is not None else (Vector(target) - Vector(pos)).length, fstop)


def keyed(light):
    T.prop(light.data, 'energy')
    return light


# ================================================================ act 1: keychains
HERO = ('g80_m3_snakeeye', 'Matte Gray', 'Yellow')
SATS = [('f90_m5', 'Matte Blue', 'White'), ('mk5_supra', 'Matte Red', 'White'), ('c8_corvette', 'Matte Yellow', 'White'),
        ('r35_gtr', 'Metallic Silver', 'Blue'), ('gt3rs_992', 'White', 'White'), ('svj_aventador', 'Matte Black', 'Yellow'),
        ('challenger_hellcat', 'Matte Red', 'Red'), ('mclaren_720s', 'Matte Blue', 'White')]


def ring_pos(theta, rx, rz, depth):
    """a point on the ring that circles the hero: an upright ellipse in the screen plane, tilted in depth so the
    keychains pass in front of it at the bottom and behind it at the top"""
    return Vector((rx * math.sin(theta), depth * math.cos(theta), rz * math.cos(theta)))


def orbit(name_burst, name_back, n, rx, rz, depth, turns=1.2):
    """per-satellite position over time: out of the hero (from behind it), around the ring, back in"""
    b0, b1 = seg(name_burst)
    r0, r1 = seg(name_back)
    total = r1 - b0

    def at(i, f):
        # emergence e: 0 (inside the hero, behind its face) -> 1 (on the ring) -> 0 (back inside)
        e_out = spring((f - b0 - i * 2.5) / FPS, w=4.6, z=0.8)
        e_in = smoother((f - r0 - (n - 1 - i) * 1.2) / max(1, (r1 - r0) * 0.85))
        e = max(0.0, e_out * (1 - e_in))
        # the ring turns: it speeds up, coasts, and slows as they go home
        u = clamp01((f - b0) / total)
        ang = 2 * math.pi * turns * (u * u * (3 - 2 * u)) + 2 * math.pi * i / n
        p = ring_pos(ang, rx, rz, depth) * e + Vector((0, 0.006 + 0.002 * i, 0)) * (1 - e)
        visible = f >= b0 - 1 and (e > 0.002 or f < r0)
        return p, e, ang, visible
    return at


def act_kc():
    st = stage()
    beam = keyed(st['beams'][0]); keyed(st['key']); keyed(st['fill'])
    hero = gt.Keychain(HERO[0], gt.colour(HERO[1]), gt.headlight(HERO[2]), glow=6.0)
    T.obj(hero.kc, *hero.links)
    T.prop(hero.light_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'], 'default_value')
    sats = [gt.Keychain(cid, gt.colour(c), gt.headlight(l), glow=4.0) for cid, c, l in SATS]
    for k in sats:
        T.obj(k.kc, *k.links, *k.kc.children_recursive)
    cam = camera(85)
    ringlight = keyed(gt.spot('ringlight', (0.0, -0.75, 0.55), (0, 0, 0), 0, angle_deg=55, blend=0.8, radius=0.25, volume=0.0))
    ringrim = keyed(gt.area('ringrim', (0.0, 0.5, 0.35), (0, 0, 0), 0, 0.8, color='#d8e4ff'))
    gt.exclude_from(st['floor'], ringlight, ringrim)
    n = len(sats)
    rx, rz, depth = (0.125, 0.16, 0.07) if PORTRAIT else (0.2, 0.12, 0.07)
    at = orbit('burst', 'home', n, rx, rz, depth, turns=1.25)
    d0 = gt.fit_distance(cam, 0.106, 0.09, *((0.66, 0.5) if PORTRAIT else (0.42, 0.6)))
    d_ring = gt.fit_distance(cam, 2 * rx + 0.1, 2 * rz + 0.1, *((0.98, 0.7) if PORTRAIT else (0.8, 0.95)))
    zc = 0.0
    flip_a, flip_b = seg('flip')
    on_at = int(BEAT)

    def hero_pose(t):
        f = t * FPS
        s = spring((f - flip_a - 2) / FPS, w=7.0, z=0.3)
        sway = 0.06 * math.sin(t * 0.8) * (1 - smooth((f - flip_a) / 20))
        return dict(pos=(0, 0, zc), yaw=math.pi * s + sway, pitch=0.0, roll=0.0)

    sat_fns = []
    for i, k in enumerate(sats):
        def fn(t, i=i):
            p, e, ang, vis = at(i, t * FPS)
            return dict(pos=(p.x, p.y, p.z + zc), yaw=0.35 * math.cos(ang) * e, pitch=0.0, roll=-0.12 * math.sin(ang) * e, visible=vis)
        sat_fns.append(fn)

    pan_a, pan_b = seg('back')
    dive_a, dive_b = seg('dive')

    def update(f):
        lvl = 0.0 if f < on_at else {0: 0.55, 1: 0.12, 2: 0.85}.get(f - on_at, 1.0)
        beam.data.energy = 55 * lvl
        st['key'].data.energy = 160 * lvl
        st['fill'].data.energy = 6 * lvl
        gt.set_lights(hero.light_mat, gt.headlight(HERO[2]), 6.0 * lvl)
        ring_on = smooth((f - seg('burst')[0] + 4) / 14) * (1 - smooth((f - seg('home')[0]) / (seg('home')[1] - seg('home')[0])))
        ringlight.data.energy = 260 * ring_on
        ringrim.data.energy = 40 * ring_on
        hero.apply(hero_pose, f)
        for k, fn in zip(sats, sat_fns):
            k.apply(fn, f)
        # ---- camera
        if f < seg('burst')[0] - 8:                               # intro: slow push on the hero
            p = smooth(f / seg('intro')[1])
            d = d0 * (1.06 - 0.06 * p)
            look(cam, (0, -d, zc + 0.006), (0, 0, zc))
        elif f < seg('flip')[0]:                                  # pull back for the ring, push back in as they return
            u_out = smoother((f - seg('burst')[0] + 8) / 40)
            u_in = smoother(local(f, 'home'))
            d = lerp(d0, d_ring, u_out * (1 - u_in))
            look(cam, (0, -d, zc + 0.006 + 0.01 * u_out * (1 - u_in)), (0, 0, zc), fstop=8.0)
        elif f < pan_a:                                           # the flip
            look(cam, (0, -d0, zc + 0.006), (0, 0, zc))
        elif f < dive_a:                                          # push in on the left of the back, pan right
            u = local(f, 'back')
            push = smoother(u / 0.22)
            dist = lerp(d0, 0.11, push)
            x = lerp(0.0, -0.026, push) + 0.05 * smoother((u - 0.18) / 0.82)
            tgt = (x, 0, zc)
            look(cam, (x, -dist, zc + 0.003), tgt, fstop=2.8, focus=dist - 0.0015)
        else:                                                     # dive into the carbon back
            u = smoother(local(f, 'dive'))
            x = 0.024
            dist = lerp(0.11, 0.004, u)
            look(cam, (x, -dist, zc + 0.003 * (1 - u)), (x, 0, zc), fstop=2.8, focus=max(0.002, dist - 0.0015))
    return update, seg('dive')[1]


# ================================================================ act 2: wall key holders
W_HERO = ('g80_wall_snakeeye', 'Matte Gray', 'Yellow')
W_SATS = [('charger_srt_wall', 'Matte Red'), ('mk5_supra_wall', 'White'), ('gt500_mustang_wall', 'Matte Blue'),
          ('camaro_zl1_wall', 'Matte Yellow'), ('c8_corvette_wall', 'Metallic Silver'), ('f90_m5_wall', 'Matte Black')]


def act_wall():
    k = 2.7
    st = stage(k=k, haze=0.04)
    hero = gt.WallHolder(W_HERO[0], gt.colour(W_HERO[1]), gt.headlight(W_HERO[2]), glow=6.0)
    sats = [gt.WallHolder(w, gt.colour(c), gt.headlight('White'), glow=3.0) for w, c in W_SATS]
    for h in [hero] + sats:
        T.obj(h.pivot)
        T.prop(h.pivot, 'hide_render', constant=True)
        for o in h.objects:
            T.prop(o, 'hide_render', constant=True)
    cam = camera(85)
    ringlight = keyed(gt.spot('ringlight', (0.0, -0.75 * k, 0.55 * k), (0, 0, 0), 0, angle_deg=55, blend=0.8, radius=0.25 * k, volume=0.0))
    gt.exclude_from(st['floor'], ringlight)
    c0 = hero.home.copy()
    for h in [hero] + sats:                                       # all centred on the same point
        h.set(c0)
    face = hero.lo.y
    # detail targets on the hero's face: left light signature, grille centre, the hooks
    lv = [hero.lights.matrix_world @ v.co for v in hero.lights.data.vertices] if hero.lights else []
    left = [v for v in lv if v.x < c0.x]
    if left:
        light_pt = Vector((sum(v.x for v in left) / len(left), face, sum(v.z for v in left) / len(left)))
    else:
        light_pt = Vector((c0.x - 0.08, face, c0.z + 0.02))
    grille_pt = Vector((c0.x, face, c0.z + 0.0))
    hk = hero.hooks
    hook_pt = Vector(((hk[1]['x'] + hk[2]['x']) / 2 if len(hk) > 2 else c0.x, (hk[0]['y_out'] if hk else face) + 0.004,
                      (hk[0]['arm_top'] if hk else c0.z - 0.04)))
    rx, rz, depth = (0.36, 0.44, 0.16) if PORTRAIT else (0.55, 0.3, 0.16)
    at = orbit('w_burst', 'w_home', len(sats), rx, rz, depth, turns=1.0)
    d_full = gt.fit_distance(cam, hero.size.x * 1.05, hero.size.z * 1.2, *((0.92, 0.5) if PORTRAIT else (0.5, 0.6)))
    d_ring = gt.fit_distance(cam, 2 * rx + 0.26, 2 * rz + 0.13, *((0.98, 0.7) if PORTRAIT else (0.85, 0.95)))
    det_a, det_b = seg('w_details')
    flip_a, flip_b = seg('w_flip')

    def hero_pose(f):
        s = spring((f - flip_a - 2) / FPS, w=6.5, z=0.32)
        return math.pi * s

    shots = [(light_pt, 0.16, (-0.03, -0.012)), (grille_pt, 0.2, (0.0, 0.02)), (hook_pt, 0.19, (0.04, -0.03))]

    def detail_cam(f):
        u = (f - det_a) / max(1, det_b - det_a) * 3
        i = min(2, int(u))
        v = u - i
        tgt, dist, (ox, oz) = shots[i]
        # each detail: a slow drift; the last 30 % glides to the next one
        drift = Vector((ox * (v - 0.5), 0, oz * (v - 0.5) * 0.5))
        pos_t = tgt + drift
        if v > 0.7 and i < 2:
            w_ = smoother((v - 0.7) / 0.3)
            n_tgt, n_dist, (nox, noz) = shots[i + 1]
            pos_t = pos_t.lerp(n_tgt + Vector((nox * -0.5, 0, noz * -0.25)), w_)
            dist = lerp(dist, n_dist, w_)
        return pos_t, dist

    out_a, out_b = seg('w_out')
    dive_a, dive_b = seg('w_dive')
    back_c = Vector((c0.x, hero.hi.y, c0.z))

    def update(f):
        yaw = hero_pose(f)
        hero.set(c0, yaw=yaw)
        ring_on = smooth((f - seg('w_burst')[0] + 4) / 14) * (1 - smooth((f - seg('w_home')[0]) / (seg('w_home')[1] - seg('w_home')[0])))
        ringlight.data.energy = 220 * k * k * ring_on
        for i, h in enumerate(sats):
            p, e, ang, vis = at(i, f)
            h.set(c0 + p, yaw=0.3 * math.cos(ang) * e, roll=-0.08 * math.sin(ang) * e, visible=vis)
        if f < det_b:
            tgt, dist = detail_cam(f)
            look(cam, (tgt.x, tgt.y - dist, tgt.z + dist * 0.12), tgt, fstop=5.6, focus=dist)
        elif f < out_b:                                           # pull back to the whole holder
            u = smoother(local(f, 'w_out'))
            tgt0, dist0 = detail_cam(det_b - 1)
            tgt = tgt0.lerp(c0, u)
            dist = lerp(dist0, d_full, u)
            look(cam, (tgt.x, c0.y - dist - (c0.y - tgt.y) * (1 - u), tgt.z + dist * 0.06), tgt, fstop=5.6)
        elif f < flip_a:                                          # the other holders circle it
            u_out = smoother(local(f, 'w_burst') * 2.0)
            u_in = smoother(local(f, 'w_home'))
            d = lerp(d_full, d_ring, u_out * (1 - u_in))
            look(cam, (c0.x, c0.y - d, c0.z + 0.02), c0, fstop=8.0)
        elif f < dive_a:                                          # the flip
            look(cam, (c0.x, c0.y - d_full, c0.z + 0.02), c0, fstop=5.6)
        else:                                                     # dive into the back plate
            u = smoother(local(f, 'w_dive'))
            dist = lerp(d_full, 0.01, u)
            look(cam, (c0.x, c0.y - dist, c0.z + 0.02 * (1 - u)), c0, fstop=4.0, focus=max(0.005, dist - 0.004))
    a0 = seg('w_details')[0]
    return update, seg('w_dive')[1], a0


# ================================================================ act 3: the three spinners
def spinner_profile(frames, start, hold, stop, full=36.0, ring_down=0.0):
    w = []
    for f in range(frames + 1):
        t = f / frames
        v = 0.0
        if start <= t < hold:
            v = 1 - math.exp(-((t - start) * frames) / FPS / 0.18)
        elif hold <= t < stop:
            u = (t - hold) / (stop - hold)
            v = (1 - math.exp(-((hold - start) * frames) / FPS / 0.18)) * (1 - u) ** 2.2
        w.append(v)
    ang = [0.0]
    for f in range(1, frames + 1):
        ang.append(ang[-1] + (w[f - 1] + w[f]) / 2)
    raw = ang[-1] or 1
    k = max(1, round((full * frames / 120 - ring_down) / (2 * math.pi)))
    s = (ring_down + 2 * math.pi * k) / raw
    return [a * s for a in ang]


def ring_down_angle(sp):
    best = None
    for i in range(360):
        a = 2 * math.pi * i / 360
        sp.set(a, loc=tuple(sp.pivot.location))
        bpy.context.view_layer.update()
        z = sp.torus.matrix_world.translation.z
        if best is None or z < best[0]:
            best = (z, a)
    return best[1]


def act_spin():
    st = stage(beam=0.0, haze=0.05, rim=1.6)
    st['beams'][0].data.energy = 0
    kinds = ['talon', 'karambit', 'shield']
    sps = [gt.Spinner(kd) for kd in kinds]
    rds = [ring_down_angle(sp) for sp in sps]
    boxes = []
    for sp, rd in zip(sps, rds):
        sp.set(rd, loc=tuple(sp.pivot.location))
        bpy.context.view_layer.update()
        lo, hi = gt.bbox([sp.frame, sp.torus])
        c = sp.inner.matrix_world.translation
        boxes.append((lo.x - c.x, hi.x - c.x, lo.z - c.z, hi.z - c.z))
    gap = 0.024
    xs, cur = [], 0.0
    for i, (l, r, b, t) in enumerate(boxes):
        if i == 0:
            xs.append(0.0); cur = r
        else:
            x = cur + gap - l
            xs.append(x); cur = x + r
    mid = (boxes[0][0] + cur) / 2
    top = max(t for (l, r, b, t) in boxes)
    locs, beams = [], []
    for i, (sp, x, (l, r, b, t)) in enumerate(zip(sps, xs, boxes)):
        c = sp.inner.matrix_world.translation.copy()
        back = 0.035 if i == 1 else 0.0           # the middle one sits back: their sweeps pass without touching
        sp.pivot.location = sp.pivot.location + Vector((x - mid - c.x, back, (top - t) * 0.6 - c.z))
        locs.append(tuple(sp.pivot.location))
        bx = x - mid + (l + r) / 2
        bm = gt.spot(f'beam_{i}', (bx, 0.004 + back, 0.2), (bx, 0.004 + back, -0.1), 0, angle_deg=26, blend=0.35, radius=0.004, volume=1.0)
        keyed(bm)
        beams.append(bm)
        T.obj(sp.spin)
    width = cur - boxes[0][0]
    height = max(t - b for (l, r, b, t) in boxes)
    cam = camera(85)
    d = gt.fit_distance(cam, width * 1.06, height * 1.15, *((0.96, 0.5) if PORTRAIT else (0.55, 0.7)))
    fw = gt.frame_width(cam, d)
    zoff = -0.1 * fw * H / W if PORTRAIT else 0.0
    a, b = seg('spin')
    N = b - a
    profs = [spinner_profile(N, 0.1 + 0.08 * i, 0.38 + 0.06 * i, 0.8 + 0.06 * i, full=30.0, ring_down=rd) for i, rd in enumerate(rds)]
    ons = [int(round(i * BEAT * 0.5)) + 6 for i in range(3)]
    mid_c = Vector((locs[1][0], locs[1][1], 0)) + (sps[1].inner.matrix_world.translation - sps[1].pivot.location)

    def update(f):
        for i, (sp, prof, loc, bm) in enumerate(zip(sps, profs, locs, beams)):
            lvl = 0.0 if f < ons[i] else {0: 0.6, 1: 0.15}.get(f - ons[i], 1.0)
            bm.data.energy = 55 * lvl
            sp.set(prof[min(f, N)], loc=loc)
        u = smoother(f / (N * 0.45))                                  # out of the dive: from the middle bearing to all three
        tgt = mid_c.lerp(Vector((0, 0, zoff)), u)
        dist = lerp(0.075, d, u)
        look(cam, (tgt.x, tgt.y - dist, tgt.z + 0.015 * u), tgt, fstop=lerp(2.8, 5.6, u))
    return update, N


# ================================================================ run
if ACT == 'kc':
    update, FR = act_kc(); START = 0
elif ACT == 'wall':
    update, end, START = act_wall(); FR = end - START
else:
    update, FR = act_spin(); START = 0

os.makedirs(OUT, exist_ok=True)
gt.aura()


def upd(fl):                # local frame -> act frame (the wall act's segments are in film frames)
    update(fl + (START if ACT == 'wall' else 0))


if 'test' in A:
    want = [int(x) for x in A['test'].split(',')]
    for fl in range(max(want) + 1):
        upd(fl)
        if fl in want:
            gt.set_haze_time(fl / 30)
            scene.render.filepath = os.path.join(OUT, f'test_{ACT}_{fl:04d}.jpg')
            bpy.ops.render.render(write_still=True)
            print('TEST', scene.render.filepath, flush=True)
else:
    gt.bake_render(upd, FR, OUT, T, motion_blur=0.5, mb_steps=4 if ACT == 'spin' else 1)
