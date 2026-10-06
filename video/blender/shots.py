"""Grille Talk film shots, rendered in Blender (headless):
  blender -b --factory-startup -P video/blender/shots.py -- shot=hook w=1080 h=1920 frames=152 out=<dir> [engine=EEVEE]
                                                           [samples=64] [test=0,40,80]
Each shot builds its set, keyframes everything that moves (camera, keychain, chain links, lights, colours) and renders
the frames as an animation (JPEG). `test=` renders only those frames as stills, for look-dev."""
import bpy, math, os, sys
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gt

A = dict(a.split('=', 1) for a in sys.argv[sys.argv.index('--') + 1:])
SHOT, W, H, FR = A['shot'], int(A['w']), int(A['h']), int(A['frames'])
OUT = os.path.abspath(A['out'])
ENGINE = A.get('engine', 'EEVEE')
SAMPLES = int(A.get('samples', 64))
PORTRAIT, LAND = H > W, W / H > 1.2
FPS = 30
BEAT = 2.5265 / 4 * FPS   # frames per beat (18.95)

scene = gt.new_scene(W, H, ENGINE, SAMPLES)
WALLISH = SHOT in ('wall', 'w_keys', 'w_colours', 'w_mount', 'w_lineup')
# the dark-stage shots are lit hot for the beam: -2.3 EV brings the PLA colours back to their catalog values
SPINNERISH = SHOT in ('spinner', 'sp_spin', 'sp_macro', 'sp_specs', 'sp_price')
scene.view_settings.exposure = float(A.get('ev', 0.0 if WALLISH else (-1.1 if SPINNERISH else -2.3)))
gt.EMIT_GAIN = 1.0 if WALLISH else 5.0     # headlights keep their glow after the exposure cut
T = gt.Track()


# ================================================================ helpers
def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def spring(t, w=11.0, z=0.32):
    """unit step response of a damped spring (0 -> 1 with overshoot)"""
    if t <= 0:
        return 0.0
    wd = w * math.sqrt(1 - z * z)
    return 1 - math.exp(-z * w * t) * (math.cos(wd * t) + z * w / wd * math.sin(wd * t))


def pose(x=0.0, y=0.0, z=0.0, yaw=0.0, pitch=0.0, roll=0.0, visible=True):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch, roll=roll, visible=visible)


def frame_keychain(cam, w=0.106, h=0.09, share=None):
    """distance + target offset so the keychain (and its chain) sits upper-middle in portrait / right of centre in
    landscape, leaving room for the type"""
    if share is None:
        share = (0.86, 0.5) if PORTRAIT else ((0.42, 0.62) if LAND else (0.66, 0.6))
    d = gt.fit_distance(cam, w, h, *share)
    fw = gt.frame_width(cam, d)
    fh = fw * H / W
    if PORTRAIT:
        return d, Vector((0, 0, -0.13 * fh))
    if LAND:
        return d, Vector((-0.2 * fw, 0, -0.03 * fh))
    return d, Vector((0, 0, -0.1 * fh))


KEY_W = float(A.get('key', 160))
HAZE = float(A.get('haze', 2.0))      # haze density multiplier      # spotlight power (W); the product is 8 cm, the lamp about 1 m away


def void_stage(spot_energy=1.0, floor_z=-0.085, haze_density=0.05, rim=1.0, beam=1.0, beam_xy=(0.0, 0.004)):
    """black void with a real beam: a narrow spotlight just above the product shines straight down through haze (the
    cone is visible and lights the top of the product), a front key (no haze) models the face, cool rims behind,
    a glossy black floor catching the pool of light"""
    gt.haze(center=(0, 0.2, 0.2), size=(2.0, 2.0, 1.6), density=haze_density * 3.0 * HAZE)
    beam_o = gt.spot('beam', (beam_xy[0], beam_xy[1], 0.17), (beam_xy[0], beam_xy[1], -0.1), 55 * beam * spot_energy,
                     angle_deg=30, blend=0.35, radius=0.004, volume=1.0)
    key = gt.spot('key', (0.05, -0.55, 0.42), (0, 0, -0.005), KEY_W * spot_energy, angle_deg=14, blend=0.6, radius=0.05, volume=0.0)
    r1 = gt.area('rim_l', (-0.35, 0.35, 0.12), (0, 0, 0), 40 * rim, 0.25, color='#cfe0ff')
    r2 = gt.area('rim_r', (0.38, 0.32, 0.2), (0, 0, 0), 32 * rim, 0.25, color='#dce8ff')
    fill = gt.area('fill', (0.0, -0.6, 0.05), (0, 0, 0), 6, 0.8, color='#fff4e6')
    fl = gt.floor(floor_z, color=(0.004, 0.004, 0.005, 1), rough=0.3)
    gt.exclude_from(fl, r1, r2)         # the rims shape the product only (no glare spots on the floor)
    BEAMS.append(beam_o)
    FLOORS.append(fl)
    return key, r1, r2, fill


BEAMS = []
FLOORS = []


def kc_stage_cam(lens=85):
    cam = gt.camera(lens=lens)
    T.obj(cam)
    T.prop(cam.data.dof, 'focus_distance')
    return cam


def keyed_light(light_obj):
    T.prop(light_obj.data, 'energy')
    T.prop(light_obj.data, 'color')
    return light_obj


MOUNT = []


def write_meta(name, pts):
    """normalised screen positions (x right, y down) of world points, through the shot camera"""
    import json
    from bpy_extras.object_utils import world_to_camera_view
    cam = bpy.context.scene.camera
    res = {}
    for k, p in pts.items():
        v = world_to_camera_view(bpy.context.scene, cam, p)
        res[k] = (round(v.x, 4), round(1 - v.y, 4))
    json.dump(res, open(os.path.join(OUT, f'{name}_meta.json'), 'w'), indent=1)


# ================================================================ keychain shots
HERO = 'g80_m3_snakeeye'


def shot_hook():
    key, r1, r2, fill = void_stage(haze_density=0.06)
    keyed_light(key); keyed_light(fill); keyed_light(BEAMS[0])
    k = gt.Keychain(HERO, gt.colour('Matte Gray'), gt.headlight('Yellow'), glow=0.0)
    T.obj(k.kc, *k.links)
    T.prop(k.light_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'], 'default_value')
    cam = kc_stage_cam(85)
    d, off = frame_keychain(cam)
    on_at = int(BEAT)                               # the light snaps on on beat 1
    drop_at = on_at + 2

    def kp(t):
        f = t * FPS
        s = spring((f - drop_at) / FPS, w=11, z=0.55)        # about 12 % overshoot: a settle, not a floor hit
        return pose(z=0.22 * (1 - s), yaw=0.16 * math.sin(t * 1.7) * math.exp(-max(0, t - 1) * 0.4), roll=0.04 * (1 - s))

    def update(f):
        lvl = 0.0 if f < on_at else {0: 0.55, 1: 0.1, 2: 0.85}.get(f - on_at, 1.0)
        key.data.energy = KEY_W * lvl
        fill.data.energy = 6 * lvl
        BEAMS[0].data.energy = 55 * lvl
        gt.set_lights(k.light_mat, gt.headlight('Yellow'), 6.0 * lvl * smooth((f - on_at) / 20))
        k.apply(kp, f)
        p = ease(f / FR)
        dd = d * (1.05 - 0.08 * p)
        tgt = off + Vector((0, 0, 0.004 * p))
        gt.place_cam(cam, (tgt.x, -dd, tgt.z - 0.02), tgt)
        gt.dof(cam, dd, 4.0)
    return update


def shot_detail():
    key, r1, r2, fill = void_stage(spot_energy=0.35, haze_density=0.012, beam=0.0)
    rake = gt.spot('rake', (-0.45, -0.03, 0.2), (0, 0, 0), 22, angle_deg=30, blend=0.6, radius=0.01, volume=0.0)
    T.obj(rake)
    k = gt.Keychain(HERO, gt.colour('Matte Gray'), gt.headlight('Yellow'), glow=6.0)
    T.obj(k.kc, *k.links)
    cam = kc_stage_cam(100)

    def update(f):
        p = smooth(f / FR)
        k.apply(lambda t: pose(yaw=0.03 * math.sin(t * 0.7)), f)
        rake.location = Vector((-0.45 + 0.9 * p, -0.035, 0.2))      # grazing from above, across the face
        gt.aim(rake, (0, 0, 0))
        ang = -0.38 + 0.6 * p                         # about 25 degrees of orbit
        dist = 0.13 - 0.03 * p
        tgt = Vector((-0.024 + 0.024 * p, 0, 0.008 - 0.01 * p))      # from the left headlight to the grille
        if LAND:
            tgt += Vector((-0.012, 0, 0))
        gt.place_cam(cam, (tgt.x + math.sin(ang) * dist, tgt.y - math.cos(ang) * dist, tgt.z + 0.012), tgt)
        lights_pt = Vector((-0.026, -0.002, 0.009))
        grille_pt = Vector((0.0, -0.002, -0.002))
        focus_pt = lights_pt.lerp(grille_pt, smooth((f - FR * 0.35) / (FR * 0.4)))     # focus pull
        gt.dof(cam, (focus_pt - cam.location).length, 1.8)
    return update


LIGHT_SEQ = ['White', 'Yellow', 'Red', 'Blue']


def shot_headlights():
    key, r1, r2, fill = void_stage(haze_density=0.05)
    keyed_light(key)
    k = gt.Keychain(HERO, gt.colour('Matte Gray'), gt.headlight('White'), glow=6.0)
    T.obj(k.kc, *k.links)
    T.prop(k.light_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'], 'default_value', constant=True)
    T.prop(k.light_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'], 'default_value', constant=True)
    T.prop(k.light_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'], 'default_value')
    cam = kc_stage_cam(85)
    d, off = frame_keychain(cam)
    beats = [int(round(i * BEAT)) for i in range(4)]

    def kick(t):
        fr_ = t * FPS
        return sum(-8.0 for b in beats[1:] if b <= fr_ < b + 2)

    def update(f):
        i = max(j for j, b in enumerate(beats) if f >= b)
        since = f - beats[i]
        flash = max(0.0, 1 - since / 4) if i or f < 3 else 0.0
        gt.set_lights(k.light_mat, gt.headlight(LIGHT_SEQ[i]), 7.0 + 14.0 * flash)
        key.data.energy = KEY_W * (1 + 0.5 * flash)
        k.apply(lambda t: pose(yaw=0.05 * math.sin(t * 0.8)), f, kick=kick)
        shake = math.exp(-since / 3) * 0.0006 if i else 0.0
        gt.place_cam(cam, (off.x + math.sin(f * 2.3) * shake, -d, off.z + math.cos(f * 3.1) * shake), off)
        gt.dof(cam, d, 5.6)
    return update


def shot_colours():
    key, r1, r2, fill = void_stage(haze_density=0.045)
    k = gt.Keychain(HERO, gt.colour('White'), gt.headlight('White'), glow=5.0)
    T.obj(k.kc, *k.links)
    b = k.body_mat.node_tree.nodes['Principled BSDF']
    for nm in ('Base Color', 'Metallic', 'Roughness', 'Coat Weight'):
        T.prop(b.inputs[nm], 'default_value', constant=True)
    cam = kc_stage_cam(85)
    d, off = frame_keychain(cam)
    cols = gt.CATALOG['colors']
    step = BEAT / 2

    def update(f):
        i = min(len(cols) - 1, int(f / step))
        gt.set_body(k.body_mat, cols[i])
        k.apply(lambda t: pose(yaw=-0.22 + 0.32 * smooth(t / (FR / FPS))), f)
        gt.place_cam(cam, (off.x, -d * (1.02 - 0.05 * smooth(f / FR)), off.z), off)
        gt.dof(cam, d, 5.6)
    return update


def shot_flip():
    key, r1, r2, fill = void_stage(haze_density=0.05)
    sweep = gt.spot('sweep', (-0.3, 0.45, 0.25), (0, 0, 0), 0, angle_deg=14, blend=0.5, radius=0.005, volume=0.4)
    T.obj(sweep); keyed_light(sweep)
    gt.exclude_from(FLOORS[0], sweep)          # the sweep plays on the carbon back only, not on the floor
    k = gt.Keychain(HERO, gt.colour('Matte Gray'), gt.headlight('Yellow'), glow=5.0)
    T.obj(k.kc, *k.links)
    cam = kc_stage_cam(85)
    d, off = frame_keychain(cam)

    def kp(t):
        s = spring(t - 0.15, w=7.5, z=0.28)
        return pose(yaw=math.pi * s)

    def update(f):
        k.apply(kp, f)
        p = smooth((f - FR * 0.45) / (FR * 0.45))       # light sweep across the carbon weave
        sweep.location = Vector((-0.35 + 0.7 * p, 0.42, 0.2))
        gt.aim(sweep, (0, 0, 0))
        sweep.data.energy = 120 * math.sin(math.pi * p)
        gt.place_cam(cam, (off.x, -d, off.z), off)
        gt.dof(cam, d, 5.6)
    return update


GARAGE = [('f90_m5', 'Matte Blue'), ('mk5_supra', 'Matte Red'), ('c8_corvette', 'Matte Yellow'), ('r35_gtr', 'Metallic Silver'),
          ('gt3rs_992', 'White'), ('svj_aventador', 'Matte Black'), ('challenger_hellcat', 'Matte Gray'), ('ram_trx', 'Matte Red'),
          ('escalade', 'Metallic Silver'), ('tesla_models_plaid', 'White'), ('mclaren_720s', 'Matte Blue'), ('g87_m2_snakeeye', 'Matte Yellow')]


def shot_garage():
    key, r1, r2, fill = void_stage(haze_density=0.05, rim=1.4)
    cars = [gt.Keychain(cid, gt.colour(c), gt.headlight('White'), glow=4.0) for cid, c in GARAGE]
    for k in cars:
        T.obj(k.kc, *k.links, *[o for o in k.kc.children_recursive])
    cam = kc_stage_cam(85)
    d, off = frame_keychain(cam)
    step = BEAT / 2

    def update(f):
        i = min(len(cars) - 1, int(f / step))
        local = f - i * step
        for j, k in enumerate(cars):
            vis = j == i
            k.chain = True
            k.apply(lambda t, j=j: pose(yaw=0.06 * math.sin(t * 1.3 + j), visible=vis), int(local) if vis else 0)
        push = 1.06 - 0.06 * ease(local / 5)
        gt.place_cam(cam, (off.x, -d * push, off.z), off)
        gt.dof(cam, d * push, 5.6)
    return update


# ================================================================ wall
def wall_stage(lamp=1.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0.3, 0.0004, 0), rotation=(math.radians(90), 0, 0))
    wall = bpy.context.active_object
    wall.scale = (4, 2.6, 1)
    m = gt.principled('plaster', gt.hex_lin('#6e6961'), 0.92)
    nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    n1 = nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 18; n1.inputs['Detail'].default_value = 8
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 900; n2.inputs['Detail'].default_value = 3
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35; bump.inputs['Distance'].default_value = 0.0004
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'FLOAT'; mix.inputs['Factor'].default_value = 0.5
    cr = nt.nodes.new('ShaderNodeMapRange'); cr.inputs['To Min'].default_value = 0.85; cr.inputs['To Max'].default_value = 1.0
    hsv = nt.nodes.new('ShaderNodeMix'); hsv.data_type = 'RGBA'; hsv.blend_type = 'MULTIPLY'; hsv.inputs['Factor'].default_value = 1.0
    nt.links.new(tc.outputs['Object'], n1.inputs['Vector']); nt.links.new(tc.outputs['Object'], n2.inputs['Vector'])
    nt.links.new(n1.outputs['Fac'], mix.inputs['A']); nt.links.new(n2.outputs['Fac'], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
    nt.links.new(n1.outputs['Fac'], cr.inputs['Value'])
    hsv.inputs['A'].default_value = gt.hex_lin('#6e6961')
    nt.links.new(cr.outputs['Result'], hsv.inputs['B'])
    nt.links.new(hsv.outputs['Result'], nt.nodes['Principled BSDF'].inputs['Base Color'])
    wall.data.materials.append(m)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.3, -0.006, -0.42))
    sk = bpy.context.active_object
    sk.scale = (4, 0.012, 0.07)
    sk.data.materials.append(gt.principled('skirting', gt.hex_lin('#e4ddd1'), 0.45))
    gt.haze(center=(0.3, -0.5, 0.2), size=(3, 1.0, 1.6), density=0.012)
    lampspot = gt.spot('lamp', (0.05, -0.42, 0.62), (0.0, 0.0, -0.05), 85 * lamp, angle_deg=40, blend=0.9, color='#ffd9a8', radius=0.06, volume=1.0)
    bounce = gt.area('bounce', (0.3, -0.9, -0.2), (0.3, 0, 0), 5, 1.2, color='#ffe8cc')
    gt.area('cool', (0.9, -0.5, 0.4), (0.3, 0, 0), 1.2, 0.6, color='#cfdcff')
    return lampspot, bounce


def wall_cam(lens=60):
    cam = gt.camera(lens=lens)
    T.obj(cam)
    T.prop(cam.data.dof, 'focus_distance')
    return cam


def keys_on(holder, hook_i, fps_land, f, start_from=(0.32, -0.12, 0.2)):
    """contact point on the hook arm and the swing angle for frame f (keys swing in and land on frame fps_land)"""
    h = holder.hooks[hook_i]
    contact = Vector((h['x'], h['y_out'] + 0.007, h['arm_top']))
    t_land = fps_land
    if f < t_land:
        p = smooth(f / t_land)
        arc = Vector(start_from) * (1 - p) + Vector((0, 0, 0.05 * math.sin(math.pi * p)))
        return contact + arc, 0.9 * (1 - p) + 0.35, True
    t = (f - t_land) / FPS
    swing = 0.35 * math.exp(-t * 1.5) * math.cos(t * 6.8)
    return contact, swing, True


def shot_wall(pan=True, land=None):
    lamp, bounce = wall_stage()
    supra = gt.WallHolder('mk5_supra_wall', gt.colour('White'), gt.headlight('White'), x=0.0)
    gt.WallHolder('f90_m5_wall', gt.colour('Matte Blue'), gt.headlight('White'), x=0.34)
    gt.WallHolder('g80_wall_snakeeye', gt.colour('Matte Black'), gt.headlight('Yellow'), x=0.68)
    kb = gt.KeyBunch()
    T.obj(kb.ring, kb.k1, kb.k2)
    cam = wall_cam(50)
    land = land or int(FR * 0.3)
    hook = 1 if len(supra.hooks) > 1 else 0
    d = gt.fit_distance(cam, 0.27, 0.16, *((0.92, 0.5) if PORTRAIT else ((0.4, 0.5) if LAND else (0.66, 0.6))))
    fw = gt.frame_width(cam, d)
    side = -0.2 * fw if LAND else 0.0
    zoff = -0.12 * fw * H / W if PORTRAIT else 0.0

    def update(f):
        c, sw, vis = keys_on(supra, hook, land, f)
        kb.place(c, sw, spin=0.3 * math.sin(f / 9), k_swing=(0.25 * sw, -0.18 * sw))
        p = smooth((f - FR * 0.62) / (FR * 0.36)) if pan else 0.0
        x = side + 0.68 * p
        push = 1.0 - 0.06 * smooth(f / (FR * 0.6))
        gt.place_cam(cam, (x, -d * push, zoff + 0.015), (x, 0, zoff))
        gt.dof(cam, d * push, 4.0)
    return update


# ================================================================ spinner
def spinner_profile(frames, start=0.12, hold=0.45, stop=0.86, full=36.0, ring_down=0.0):
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
    want = full * frames / 120
    k = max(1, round((want - ring_down) / (2 * math.pi)))
    s = (ring_down + 2 * math.pi * k) / raw
    return [a * s for a in ang]


def ring_down_angle(sp):
    best = None
    for i in range(360):
        a = 2 * math.pi * i / 360
        sp.set(a)
        bpy.context.view_layer.update()
        z = sp.torus.matrix_world.translation.z
        if best is None or z < best[0]:
            best = (z, a)
    return best[1]


def spinner_stage(beam=1.0, haze=0.05):
    key, r1, r2, fill = void_stage(haze_density=haze, floor_z=-0.09, rim=1.6, beam=beam)
    return key


def shot_spinner(start=0.12, hold=0.45, stop=0.86, orbit=(-0.45, 0.35)):
    spinner_stage()
    sp = gt.Spinner()
    T.obj(sp.spin)
    cam = kc_stage_cam(85)
    rd = ring_down_angle(sp)
    ang = spinner_profile(FR, start, hold, stop, ring_down=rd)
    d = gt.fit_distance(cam, 0.15, 0.15, *((0.95, 0.55) if PORTRAIT else ((0.42, 0.7) if LAND else (0.85, 0.85))))
    fw = gt.frame_width(cam, d)
    side = -0.2 * fw if LAND else 0.0
    zoff = -0.12 * fw * H / W if PORTRAIT else 0.0

    def update(f):
        sp.set(ang[f])
        o = orbit[0] + (orbit[1] - orbit[0]) * smooth(f / FR)
        tgt = Vector((side + 0.012, 0, zoff))
        gt.place_cam(cam, (tgt.x + math.sin(o) * d, -math.cos(o) * d, tgt.z + 0.02), tgt)
        gt.dof(cam, d, 4.0)
    return update


def shot_sp_macro():
    spinner_stage(beam=0.0, haze=0.012)
    sp = gt.Spinner()
    rake = gt.spot('rake', (-0.45, -0.03, 0.2), (0.02, 0, 0), 12, angle_deg=30, blend=0.6, radius=0.01, volume=0.0)
    T.obj(rake)
    cam = kc_stage_cam(100)
    sp.set(0.0)

    def update(f):
        p = smooth(f / FR)
        o = -0.55 + 0.55 * p
        dist = 0.11 - 0.02 * p
        tgt = Vector((0.026, 0, 0.002))
        gt.place_cam(cam, (tgt.x + math.sin(o) * dist, -math.cos(o) * dist, tgt.z + 0.012), tgt)
        rake.location = Vector((-0.45 + 0.9 * p, -0.035, 0.2)); gt.aim(rake, (0.02, 0, 0))
        gt.dof(cam, dist * (1.0 - 0.15 * p), 2.0)
    return update


def shot_sp_specs():
    spinner_stage()
    sp = gt.Spinner()
    cam = kc_stage_cam(85)
    sp.set(0.0)
    bpy.context.view_layer.update()
    lo, hi = gt.bbox([sp.talon])
    cx = (lo.x + hi.x) / 2
    d = gt.fit_distance(cam, 0.1, 0.06, *((0.8, 0.4) if PORTRAIT else (0.4, 0.4)))

    def update(f):
        gt.place_cam(cam, (cx, -d * (1.03 - 0.03 * smooth(f / FR)), 0.0), (cx, 0, 0))
        gt.dof(cam, d, 8.0)
    # screen positions (0..1, y down) of the callout points, for the 2D labels in Remotion
    update(FR // 2)
    bpy.context.view_layer.update()
    inner = next(o for o in sp.objects if o.name.startswith('inner'))
    ilo, ihi = gt.bbox([inner])
    ic = (ilo + ihi) / 2
    pts = {'bearing_edge': ic + Vector((-(ihi.x - ilo.x) * 0.5 * 1.35, 0, (ihi.z - ilo.z) * 0.5 * 0.9)), 'hole': ic,
           'left': Vector((lo.x, 0, lo.z)), 'right': Vector((hi.x, 0, lo.z))}
    write_meta('specs', pts)
    return update


def shot_sp_price():
    spinner_stage()
    sp = gt.Spinner()
    T.obj(sp.spin)
    cam = kc_stage_cam(85)
    d = gt.fit_distance(cam, 0.1, 0.1, *((0.7, 0.4) if PORTRAIT else (0.34, 0.5)))

    def update(f):
        sp.set(-0.6 + 0.4 * smooth(f / FR))
        gt.place_cam(cam, (0, -d, -0.004), (0, 0, -0.004 - (0.012 if PORTRAIT else 0)))
        gt.dof(cam, d, 5.6)
    return update


# ================================================================ wall ad
def shot_w_colours():
    lamp, bounce = wall_stage()
    supra = gt.WallHolder('mk5_supra_wall', gt.colour('White'), gt.headlight('White'))
    b = supra.body_mat.node_tree.nodes['Principled BSDF']
    for nm in ('Base Color', 'Metallic', 'Roughness', 'Coat Weight'):
        T.prop(b.inputs[nm], 'default_value', constant=True)
    cam = wall_cam(50)
    d = gt.fit_distance(cam, 0.27, 0.16, *((0.92, 0.5) if PORTRAIT else (0.4, 0.5)))
    fw = gt.frame_width(cam, d)
    zoff = -0.12 * fw * H / W if PORTRAIT else 0.0
    cols = gt.CATALOG['colors']
    step = BEAT / 2

    def update(f):
        gt.set_body(supra.body_mat, cols[min(len(cols) - 1, int(f / step))])
        a = 0.12 * math.sin(f / FR * math.pi)
        gt.place_cam(cam, (math.sin(a) * d, -math.cos(a) * d, zoff + 0.02), (0, 0, zoff))
        gt.dof(cam, d, 5.6)
    return update


def shot_w_mount():
    lamp, bounce = wall_stage()
    supra = gt.WallHolder('mk5_supra_wall', gt.colour('Matte Red'), gt.headlight('White'))
    cam = wall_cam(50)
    d = gt.fit_distance(cam, 0.27, 0.16, *((0.92, 0.5) if PORTRAIT else (0.4, 0.5)))
    fw = gt.frame_width(cam, d)
    zoff = -0.12 * fw * H / W if PORTRAIT else 0.0
    MOUNT.append(supra)

    def update(f):
        gt.place_cam(cam, (0, -d * (1.02 - 0.04 * smooth(f / FR)), zoff + 0.02), (0, 0, zoff))
        gt.dof(cam, d, 8.0)
    # the two countersunk holes (kc/wall build: x = +-113.2 mm, 21.2 mm below the outline centre)
    update(FR // 2)
    bpy.context.view_layer.update()
    face = supra.lo.y
    write_meta('mount', {'hole_l': Vector((-0.1132, face, -0.0212)), 'hole_r': Vector((0.1132, face, -0.0212)),
                         'back_l': Vector((supra.lo.x, supra.hi.y, supra.lo.z + 0.02)),
                         'back_r': Vector((supra.hi.x, supra.hi.y, supra.lo.z + 0.02))})
    return update


def shot_w_lineup():
    lamp, bounce = wall_stage(lamp=1.4)
    ids = [w['id'] for w in gt.CATALOG['wall']['items']]
    cols = ['Matte Black', 'Matte Red', 'White', 'Matte Blue', 'Matte Yellow', 'Metallic Silver', 'Matte Gray']
    per = 2 if PORTRAIT else 4
    sx, sz = 0.27, 0.15
    rows = math.ceil(len(ids) / per)
    for i, wid in enumerate(ids):
        r, c = divmod(i, per)
        in_row = min(per, len(ids) - r * per)
        hd = gt.WallHolder(wid, gt.colour(cols[i % len(cols)]), gt.headlight('Yellow' if i == 0 else 'White'),
                           x=(c - (in_row - 1) / 2) * sx)
        for o in hd.objects:
            if o.parent is None:
                o.location.z += ((rows - 1) / 2 - r) * sz
    lamp.location = Vector((0, -0.9, 1.0)); gt.aim(lamp, (0, 0, 0)); lamp.data.spot_size = math.radians(60)
    cam = wall_cam(50)
    d = gt.fit_distance(cam, sx * per, sz * rows + 0.06, *((0.94, 0.55) if PORTRAIT else (0.94, 0.66)))

    def update(f):
        dd = d * (1.04 - 0.04 * smooth(f / FR))
        gt.place_cam(cam, (0, -dd, -0.03 if PORTRAIT else -0.01), (0, 0, -0.03 if PORTRAIT else -0.01))
        gt.dof(cam, dd, 8.0)
    return update


SHOTS = {
    'hook': shot_hook, 'detail': shot_detail, 'headlights': shot_headlights, 'colours': shot_colours, 'flip': shot_flip,
    'garage': shot_garage, 'wall': lambda: shot_wall(pan=True), 'spinner': lambda: shot_spinner(),
    'sp_macro': shot_sp_macro, 'sp_spin': lambda: shot_spinner(0.08, 0.5, 0.95, orbit=(0.3, -0.2)), 'sp_specs': shot_sp_specs,
    'sp_price': shot_sp_price,
    'w_keys': lambda: shot_wall(pan=False, land=int(BEAT * 4)), 'w_colours': shot_w_colours, 'w_mount': shot_w_mount,
    'w_lineup': shot_w_lineup,
}

os.makedirs(OUT, exist_ok=True)
update = SHOTS[SHOT]()
gt.aura()
if 'test' in A:
    for f in range(FR):
        update(f)
        gt.set_haze_time(f / 30)
        T.key(f)
    T.finish()
    for f in [int(x) for x in A['test'].split(',')]:
        scene.frame_set(f)
        scene.render.filepath = os.path.join(OUT, f'test_{SHOT}_{f:04d}.jpg')
        bpy.ops.render.render(write_still=True)
        print('TEST', scene.render.filepath, flush=True)
else:
    gt.bake_render(update, FR, OUT, T, motion_blur=0.5, mb_steps=4 if SHOT.startswith(('sp_', 'spinner')) else 1)
