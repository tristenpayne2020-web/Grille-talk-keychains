"""Grille Talk film - Blender side (Blender 5.2, run headless). Shared scene pieces for every shot:
look-dev (reused from site/tools/blender_render.py: PLA layer lines, glossy details, carbon back, steel), a dark haze
stage lit by a real spotlight (the beam is light scattering in the haze, so it actually lights the product and casts
shadows), emissive headlights, a glossy floor, the compositor "aura" (bloom, fog glow, anamorphic streaks, grade,
vignette), the deterministic keychain chain (port of the site's verlet rope), wall holders with real hook geometry,
the Talon spinner, and a modelled keyring with keys.

Coordinates: Blender Z up. Imported glTF faces look along -Y; the camera looks along +Y."""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector, Matrix, Quaternion, Euler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
GLB_RAW = os.path.join(ROOT, 'site', 'build', 'glb_raw')
GLB_WEB = os.path.join(ROOT, 'site', 'build', 'glb')
CATALOG = json.load(open(os.path.join(ROOT, 'site', 'catalog', 'launch.json'), encoding='utf-8'))
UP = Vector((0, 0, 1))


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h, a=1.0):
    h = h.lstrip('#')
    return tuple(srgb_to_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (a,)


def colour(name):
    return next(c for c in CATALOG['colors'] if c['name'].lower() == name.lower())


def headlight(name):
    return next(h['hex'] for h in CATALOG['headlights']['values'] if h['name'].lower() == name.lower())


# ================================================================ scene / engine
def new_scene(w, h, engine='EEVEE', samples=64):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.resolution_percentage = 100
    s.render.fps = 30
    s.view_settings.view_transform = 'AgX'
    s.view_settings.look = 'AgX - Medium High Contrast'
    s.render.image_settings.file_format = 'JPEG'
    s.render.image_settings.quality = 94
    if engine == 'CYCLES':
        s.render.engine = 'CYCLES'
        cy = s.cycles
        cy.device = 'GPU'
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for t in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = t
                prefs.get_devices()
                if any(d.type == t for d in prefs.devices):
                    break
            except TypeError:
                continue
        for d in prefs.devices:
            d.use = True
        cy.samples = samples
        cy.use_adaptive_sampling = True
        cy.use_denoising = True
        cy.max_bounces = 6
        cy.volume_bounces = 0
        cy.volume_step_rate = 4.0
    else:
        s.render.engine = 'BLENDER_EEVEE'
        e = s.eevee
        e.taa_render_samples = samples
        e.use_raytracing = True
        e.use_shadows = True
        e.shadow_ray_count = 2
        e.shadow_step_count = 8
        e.use_volumetric_shadows = True
        e.volumetric_tile_size = '4'
        e.volumetric_samples = 96
        e.volumetric_start = 0.02
        e.volumetric_end = 4.0
        e.volumetric_light_clamp = 0.0
        try:
            e.ray_tracing_options.resolution_scale = '1'
        except Exception:
            pass
    world = bpy.data.worlds.new('stage')
    s.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.004, 0.005, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    return s


def link(o, s=None):
    (s or bpy.context.scene).collection.objects.link(o)
    return o


# ================================================================ materials (look-dev from site/tools/blender_render.py)
def principled(name, color, rough, metal=0.0, coat=0.0, spec=0.5, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Specular IOR Level'].default_value = spec
    if emit is not None:
        b.inputs['Emission Color'].default_value = emit
        b.inputs['Emission Strength'].default_value = emit_strength
    return m


def add_layer_lines(m, strength=0.08):
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 2 * math.pi / 0.0002
    sin = nt.nodes.new('ShaderNodeMath'); sin.operation = 'SINE'
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = strength; bump.inputs['Distance'].default_value = 0.00002
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 9000; noise.inputs['Detail'].default_value = 4
    bump2 = nt.nodes.new('ShaderNodeBump'); bump2.inputs['Strength'].default_value = 0.04; bump2.inputs['Distance'].default_value = 0.00001
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    nt.links.new(sep.outputs['Y'], mul.inputs[0])
    nt.links.new(mul.outputs[0], sin.inputs[0])
    nt.links.new(sin.outputs[0], bump.inputs['Height'])
    nt.links.new(noise.outputs['Fac'], bump2.inputs['Height'])
    nt.links.new(bump2.outputs['Normal'], bump.inputs['Normal'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])


def body_material(c, name='body'):
    if float(c.get('metal', 0)) > 0.3:
        m = principled(name, hex_lin(c['hex']), 0.34, metal=0.75, coat=0.15)
    else:
        m = principled(name, hex_lin(c['hex']), 0.52 if c['name'] == 'White' else 0.6, coat=0.05)
    add_layer_lines(m)
    return m


def set_body(m, c):
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hex_lin(c['hex'])
    metal = float(c.get('metal', 0)) > 0.3
    b.inputs['Metallic'].default_value = 0.75 if metal else 0.0
    b.inputs['Roughness'].default_value = 0.34 if metal else (0.52 if c['name'] == 'White' else 0.6)
    b.inputs['Coat Weight'].default_value = 0.15 if metal else 0.05


EMIT_GAIN = 1.0


def lights_material(hexcol, strength):
    m = principled('lights', hex_lin(hexcol), 0.4, emit=hex_lin(hexcol), emit_strength=strength * EMIT_GAIN)
    add_layer_lines(m, 0.05)
    return m


def set_lights(m, hexcol, strength):
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hex_lin(hexcol)
    b.inputs['Emission Color'].default_value = hex_lin(hexcol)
    b.inputs['Emission Strength'].default_value = strength * EMIT_GAIN


MATS = {}


def shared_mats():
    if not MATS:
        MATS['details'] = principled('details', (0.006, 0.006, 0.007, 1), 0.38, coat=0.1)
        add_layer_lines(MATS['details'], 0.06)
        MATS['lettering'] = principled('lettering', (0.85, 0.85, 0.83, 1), 0.4)
        MATS['steel'] = principled('steel', (0.5, 0.51, 0.53, 1), 0.32, metal=1.0)
        MATS['brass'] = principled('brass', hex_lin('#c9a45c'), 0.28, metal=1.0)
        MATS['nickel'] = principled('nickel', (0.8, 0.8, 0.82, 1), 0.26, metal=1.0)
        MATS['rubber'] = principled('rubber', (0.012, 0.012, 0.014, 1), 0.55)
    return MATS


def assign(o, m):
    if o.type == 'MESH':
        o.data.materials.clear()
        o.data.materials.append(m)


def smooth(objs):
    for o in objs:
        if o.type == 'MESH':
            for p in o.data.polygons:
                p.use_smooth = True


# ================================================================ stage: haze, spotlight, floor, rims
def haze(center=(0, 0, 0), size=(2, 2, 2), density=0.06, anisotropy=0.55, swirl=True):
    """A box of haze around the set: the spotlight's beam becomes visible where it scatters."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.active_object
    o.name = 'haze'
    o.scale = size
    m = bpy.data.materials.new('haze')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    vol = nt.nodes.new('ShaderNodeVolumePrincipled')
    vol.inputs['Color'].default_value = (1, 0.97, 0.93, 1)
    vol.inputs['Anisotropy'].default_value = anisotropy
    if swirl:   # slow drifting density (W driven per frame by set_haze_time)
        tc = nt.nodes.new('ShaderNodeTexCoord')
        noise = nt.nodes.new('ShaderNodeTexNoise'); noise.noise_dimensions = '4D'; noise.name = 'hazenoise'
        noise.inputs['Scale'].default_value = 3.0; noise.inputs['Detail'].default_value = 3.0
        ramp = nt.nodes.new('ShaderNodeMapRange')
        ramp.inputs['From Min'].default_value = 0.3; ramp.inputs['From Max'].default_value = 0.75
        ramp.inputs['To Min'].default_value = density * 0.35; ramp.inputs['To Max'].default_value = density * 1.5
        nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
        nt.links.new(noise.outputs['Fac'], ramp.inputs['Value'])
        nt.links.new(ramp.outputs['Result'], vol.inputs['Density'])
    else:
        vol.inputs['Density'].default_value = density
    nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


def set_haze_time(t):
    m = bpy.data.materials.get('haze')
    if m and 'hazenoise' in m.node_tree.nodes:
        m.node_tree.nodes['hazenoise'].inputs['W'].default_value = t * 0.06


def spot(name, loc, target, energy, angle_deg=28, blend=0.35, color='#fff8ee', radius=0.02, volume=1.0):
    l = bpy.data.lights.new(name, 'SPOT')
    l.energy = energy
    l.spot_size = math.radians(angle_deg)
    l.spot_blend = blend
    l.color = hex_lin(color)[:3]
    l.shadow_soft_size = radius
    l.volume_factor = volume
    try:
        l.use_soft_falloff = True
    except Exception:
        pass
    o = link(bpy.data.objects.new(name, l))
    o.location = loc
    aim(o, target)
    return o


def area(name, loc, target, energy, size, color='#ffffff', size_y=None, volume=0.0):
    l = bpy.data.lights.new(name, 'AREA')
    l.energy = energy
    l.size = size
    if size_y:
        l.shape = 'RECTANGLE'; l.size_y = size_y
    l.color = hex_lin(color)[:3]
    l.volume_factor = volume
    o = link(bpy.data.objects.new(name, l))
    o.location = loc
    aim(o, target)
    return o


def set_rot(o, q):
    """rotation that works whatever the object's rotation mode is (tracked objects use quaternions)"""
    if o.rotation_mode == 'QUATERNION':
        o.rotation_quaternion = q
    else:
        o.rotation_euler = q.to_euler(o.rotation_mode)


def aim(o, target):
    d = Vector(target) - o.location
    set_rot(o, d.to_track_quat('-Z', 'Y'))


def floor(z, size=6, rough=0.22, color=(0.012, 0.012, 0.013, 1)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    o = bpy.context.active_object
    o.name = 'floor'
    m = principled('floor', color, rough, coat=0.12)
    nt = m.node_tree
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 40
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = rough * 0.6; mr.inputs['To Max'].default_value = rough * 1.6
    nt.links.new(noise.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], nt.nodes['Principled BSDF'].inputs['Roughness'])
    o.data.materials.append(m)
    return o


def backdrop(y, z0=-1, size=8, color=(0.006, 0.006, 0.007, 1)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, y, z0 + size / 2), rotation=(math.radians(90), 0, 0))
    o = bpy.context.active_object
    o.name = 'backdrop'
    o.data.materials.append(principled('backdrop', color, 0.8))
    return o


def exclude_from(obj, *lights):
    """light linking: these lights do not light `obj`"""
    coll = bpy.data.collections.new(f'excl_{obj.name}')
    coll.objects.link(obj)
    for l in lights:
        try:
            l.light_linking.receiver_collection = coll
            for co in coll.collection_objects:
                co.light_linking.link_state = 'EXCLUDE'
        except Exception as e:
            print('light linking unavailable:', e)


# ================================================================ camera
def camera(lens=85, sensor=36):
    c = bpy.data.cameras.new('cam')
    c.lens = lens
    c.sensor_width = sensor
    c.sensor_fit = 'AUTO'
    c.clip_start = 0.002
    c.clip_end = 40
    o = link(bpy.data.objects.new('cam', c))
    bpy.context.scene.camera = o
    return o


def place_cam(cam, pos, target, roll=0.0):
    cam.location = Vector(pos)
    d = Vector(target) - cam.location
    q = d.to_track_quat('-Z', 'Y')
    if roll:
        q = q @ Quaternion((0, 0, 1), roll)
    set_rot(cam, q)


def dof(cam, focus, fstop, blades=7):
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = focus
    cam.data.dof.aperture_fstop = fstop
    cam.data.dof.aperture_blades = blades


def fit_distance(cam, width, height, share_w=0.85, share_h=0.8):
    """distance at which a width x height box fills the given share of the frame"""
    s = bpy.context.scene
    aspect = s.render.resolution_x / s.render.resolution_y
    sw = cam.data.sensor_width
    hfov = 2 * math.atan(sw / 2 / cam.data.lens) if aspect >= 1 else 2 * math.atan(sw * aspect / 2 / cam.data.lens)
    vfov = 2 * math.atan(math.tan(hfov / 2) / aspect)
    return max(width / share_w / 2 / math.tan(hfov / 2), height / share_h / 2 / math.tan(vfov / 2))


def frame_width(cam, dist):
    s = bpy.context.scene
    aspect = s.render.resolution_x / s.render.resolution_y
    sw = cam.data.sensor_width
    hfov = 2 * math.atan(sw / 2 / cam.data.lens) if aspect >= 1 else 2 * math.atan(sw * aspect / 2 / cam.data.lens)
    return 2 * dist * math.tan(hfov / 2)


# ================================================================ compositor "aura"
def aura(bloom=0.25, streaks=0.35, fog=0.12, vignette=0.35, warm=0.06):
    s = bpy.context.scene
    ng = bpy.data.node_groups.new('aura', 'CompositorNodeTree')
    s.compositing_node_group = ng
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    N = ng.nodes
    rl = N.new('CompositorNodeRLayers')
    out = N.new('NodeGroupOutput')
    cur = rl.outputs['Image']

    def glare(kind, strength, size=None, threshold=0.9, streak_count=None, angle=None, fade=None):
        nonlocal cur
        g = N.new('CompositorNodeGlare')
        g.inputs['Type'].default_value = kind
        g.inputs['Quality'].default_value = 'High'
        g.inputs['Threshold'].default_value = threshold
        g.inputs['Strength'].default_value = strength
        if size is not None:
            g.inputs['Size'].default_value = size
        if streak_count is not None:
            g.inputs['Streaks'].default_value = streak_count
        if angle is not None:
            g.inputs['Streaks Angle'].default_value = angle
        if fade is not None:
            g.inputs['Fade'].default_value = fade
        ng.links.new(cur, g.inputs['Image'])
        cur = g.outputs['Image']

    if fog:
        glare('Fog Glow', fog, size=0.6, threshold=1.4)
    if bloom:
        glare('Bloom', bloom, size=0.5, threshold=1.6)
    if streaks:   # anamorphic: two horizontal streaks
        glare('Streaks', streaks, threshold=6.0, streak_count=2, angle=0.0, fade=0.9)
    # grade: cool shadows, warm highlights
    cb = N.new('CompositorNodeColorBalance')
    try:
        cb.inputs['Lift'].default_value = (1.0 - warm * 0.4, 1.0 - warm * 0.1, 1.0 + warm * 0.6, 1)
        cb.inputs['Gain'].default_value = (1.0 + warm, 1.0 + warm * 0.4, 1.0 - warm * 0.5, 1)
    except Exception:
        pass
    ng.links.new(cur, cb.inputs['Image'])
    cur = cb.outputs['Image']
    if vignette:
        em = N.new('CompositorNodeEllipseMask')
        try:
            em.inputs['Size'].default_value = (0.95, 0.95)
        except Exception:
            pass
        bl = N.new('CompositorNodeBlur')
        try:
            bl.inputs['Size'].default_value = (220, 220)
        except Exception:
            pass
        mix = N.new('ShaderNodeMix') if False else None
        mul = N.new('CompositorNodeMixRGB') if hasattr(bpy.types, 'CompositorNodeMixRGB') else None
        ng.links.new(em.outputs[0], bl.inputs['Image'])
        # image * (1 - vignette) + image * mask * vignette
        mx = N.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.blend_type = 'MULTIPLY'
        mx.inputs['Factor'].default_value = vignette
        ng.links.new(cur, mx.inputs['A'])
        ng.links.new(bl.outputs[0], mx.inputs['B'])
        cur = mx.outputs['Result']
    ng.links.new(cur, out.inputs[0])
    return ng


# ================================================================ keychain rig + deterministic chain
GRAVITY = -9.81
TIME_SCALE = 0.62
DAMPING = 0.986
ITER = 10
SUB = 3
WARMUP = 45


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    return {o.name.split('.')[0]: o for o in new}, new


def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


class Keychain:
    """A car keychain: posed by its body centre (pos, yaw about Z, pitch about X, roll about the view axis Y);
    the chain hangs from the keyring hole on a verlet rope stepped from frame 0."""

    def __init__(self, cid, body_colour, lights_hex='#f7f7f4', glow=3.0, chain=True):
        path = os.path.join(GLB_RAW, f'{cid}.glb')
        if not os.path.exists(path):
            path = os.path.join(GLB_WEB, f'{cid}.glb')
        objs, new = import_glb(path)
        M = shared_mats()
        self.root = objs.get('world')
        self.kc = objs['keychain']
        self.body_mat = body_material(body_colour, f'body_{cid}')
        self.light_mat = lights_material(lights_hex, glow)
        for n, o in objs.items():
            if n == 'body': assign(o, self.body_mat)
            elif n == 'details': assign(o, M['details'])
            elif n == 'lights': assign(o, self.light_mat)
            elif n == 'lettering': assign(o, M['lettering'])
            elif n == 'back' and o.active_material:
                bb = o.active_material.node_tree.nodes.get('Principled BSDF')
                if bb:
                    bb.inputs['Roughness'].default_value = 0.22
                    bb.inputs['Coat Weight'].default_value = 0.35
                    bb.inputs['Coat Roughness'].default_value = 0.12
        smooth(new)
        self.links = [objs[f'link_{i}'] for i in range(10) if f'link_{i}' in objs]
        if 'ring' in objs:
            self.links.append(objs['ring'])
        for o in self.links:
            assign(o, M['steel'])
        bpy.context.view_layer.update()
        body_objs = [o for o in self.kc.children_recursive if o.type == 'MESH']
        lo, hi = bbox(body_objs)
        self.c = (lo + hi) / 2          # body centre (world, at rest)
        self.size = hi - lo
        self.kc_rest = self.kc.matrix_world.copy()
        self.hole0 = self.kc_rest.translation.copy()   # the GLB origin of 'keychain' is the keyring hole
        self.rest = [self.hole0.copy()] + [o.matrix_world.translation.copy() for o in self.links]
        self.rest_len = [(self.rest[i] - self.rest[i - 1]).length for i in range(1, len(self.rest))]
        self.rest_q = []
        for i, o in enumerate(self.links):
            d = (self.rest[i] - self.rest[i + 1]).normalized()
            self.rest_q.append(UP.rotation_difference(d).inverted() @ o.matrix_world.to_quaternion())
        for o in self.links:   # links are driven in world space
            o.parent = None
            o.matrix_world = o.matrix_world.copy()
        self.kc.parent = None
        self.kc.matrix_world = self.kc_rest
        self.chain = chain
        for o in self.links:
            o.hide_render = not chain
        self.objects = new

    def q(self, p):
        return Euler((p.get('pitch', 0), p.get('roll', 0), p.get('yaw', 0)), 'XYZ').to_quaternion()

    def world_of(self, p, local_rest):
        """a point given in rest world coordinates -> world, for pose p (rotate about the body centre, then place)"""
        q = self.q(p)
        return Vector(p['pos']) + q @ (local_rest - self.c)

    def set_pose(self, p):
        q = self.q(p)
        T = Matrix.Translation(Vector(p['pos'])) @ q.to_matrix().to_4x4() @ Matrix.Translation(-self.c)
        self.kc.matrix_world = T @ self.kc_rest
        self.kc.hide_render = not p.get('visible', True)
        for o in self.kc.children_recursive:
            o.hide_render = not p.get('visible', True)
        for o in self.links:
            o.hide_render = (not self.chain) or (not p.get('visible', True))

    def simulate(self, pose_fn, frame, fps=30, kick=None):
        n = len(self.rest)
        if n < 2:
            return None
        P0 = pose_fn(0.0)
        h0 = self.world_of(P0, self.hole0)
        p = [h0 + (r - self.hole0) for r in self.rest]
        prev = [v.copy() for v in p]
        dt = 1 / fps

        def step(Pa, Pb, t):
            qa, qb = self.q(Pa), self.q(Pb)
            for s in range(1, SUB + 1):
                a = s / SUB
                pos = Vector(Pa['pos']).lerp(Vector(Pb['pos']), a)
                qq = qa.slerp(qb, a)
                qi = qq.inverted()
                hole = pos + qq @ (self.hole0 - self.c)
                sdt = dt * TIME_SCALE / SUB
                k = kick(t) if kick else 0.0
                for i in range(1, n):
                    v = (p[i] - prev[i]) * DAMPING
                    prev[i] = p[i].copy()
                    p[i] = p[i] + v + Vector((k * (i / n) * sdt * sdt, 0, GRAVITY * sdt * sdt))
                for _ in range(ITER):
                    p[0] = hole.copy()
                    for i in range(1, n):
                        A, B = p[i - 1], p[i]
                        d = B - A
                        L = d.length or 1e-9
                        diff = (L - self.rest_len[i - 1]) / L
                        if i == 1:
                            p[i] = B - d * diff
                        else:
                            p[i - 1] = A + d * diff * 0.5
                            p[i] = B - d * diff * 0.5
                    p[0] = hole.copy()
                    # jump ring threaded through the hole: its centre stays in the plate's plane (local y = hole y)
                    l1 = qi @ (p[1] - pos) + self.c
                    l1.y = self.hole0.y
                    p[1] = pos + qq @ (l1 - self.c)
                prev[0] = hole.copy()

        # incremental: frames rendered in order continue from the cached state (same result, O(1) per frame)
        cache = getattr(self, '_sim', None)
        if cache and cache['fn'] is pose_fn and cache['frame'] < frame:
            p[:] = cache['p']; prev[:] = cache['prev']; Pa = cache['Pa']; f0 = cache['frame']
        else:
            for _ in range(WARMUP):
                step(P0, P0, 0.0)
            Pa = P0; f0 = 0
        for f in range(f0 + 1, frame + 1):
            Pb = pose_fn(f / fps)
            step(Pa, Pb, f / fps)
            Pa = Pb
        self._sim = dict(fn=pose_fn, frame=frame, p=[v.copy() for v in p], prev=[v.copy() for v in prev], Pa=Pa)
        return p

    def apply(self, pose_fn, frame, fps=30, kick=None):
        P = pose_fn(frame / fps)
        self.set_pose(P)
        if not (self.chain and P.get('visible', True)) or not self.links:
            return
        p = self.simulate(pose_fn, frame, fps, kick)
        q = self.q(P)
        for i, o in enumerate(self.links):
            d = (p[i] - p[i + 1]).normalized()
            if i == 0:
                # jump ring: swing measured in the keychain frame, keeps its plane on the hole axis
                qi = q.inverted()
                dl = (qi @ d).normalized()
                rot = q @ UP.rotation_difference(dl) @ self.rest_q[0]
            else:
                rot = UP.rotation_difference(d) @ self.rest_q[i]
            o.matrix_world = Matrix.Translation(p[i + 1]) @ rot.to_matrix().to_4x4()


# ================================================================ wall holder (real hook geometry)
class WallHolder:
    def __init__(self, wid, body_colour, lights_hex='#f7f7f4', glow=2.0, x=0.0, wall_y=0.0):
        path = os.path.join(GLB_RAW, f'{wid}.glb')
        if not os.path.exists(path):
            path = os.path.join(GLB_WEB, f'{wid}.glb')
        objs, new = import_glb(path)
        M = shared_mats()
        self.body_mat = body_material(body_colour, f'body_{wid}')
        self.light_mat = lights_material(lights_hex, glow)
        for n, o in objs.items():
            if n == 'body': assign(o, self.body_mat)
            elif n == 'details': assign(o, M['details'])
            elif n == 'lights': assign(o, self.light_mat)
        smooth(new)
        kc = objs['keychain']
        bpy.context.view_layer.update()
        meshes = [o for o in new if o.type == 'MESH']
        lo, hi = bbox(meshes)
        # back flat on the wall (wall plane y = wall_y, faces toward -Y), centred on x, z = 0
        kc.location = kc.location + Vector((x - (lo.x + hi.x) / 2, wall_y - hi.y, -(lo.z + hi.z) / 2))
        bpy.context.view_layer.update()
        self.lo, self.hi = bbox(meshes)
        self.size = self.hi - self.lo
        self.objects = new
        self.body = objs['body']
        self.lights = objs.get('lights')
        self.details = objs.get('details')
        self.hooks = self._hooks()
        # a pivot at the face centre: move / turn the whole holder (used off the wall)
        self.pivot = bpy.data.objects.new(f'pivot_{wid}', None)
        link(self.pivot)
        self.pivot.location = Vector(((self.lo.x + self.hi.x) / 2, (self.lo.y + self.hi.y) / 2, (self.lo.z + self.hi.z) / 2))
        bpy.context.view_layer.update()
        mw = kc.matrix_world.copy()
        kc.parent = self.pivot
        kc.matrix_world = mw
        self.pivot.rotation_mode = 'QUATERNION'
        self.home = self.pivot.location.copy()

    def set(self, pos, yaw=0.0, pitch=0.0, roll=0.0, visible=True):
        self.pivot.location = Vector(pos)
        self.pivot.rotation_quaternion = Euler((pitch, roll, yaw), 'XYZ').to_quaternion()
        for o in self.objects:
            o.hide_render = not visible

    def _hooks(self):
        """hook arms: body vertices standing more than 12 mm off the wall, clustered by x. For each: x centre,
        top of the arm (z), the arm's span along y (from the face out to the up-turned lip) and the lip top."""
        mw = self.body.matrix_world
        vs = [mw @ v.co for v in self.body.data.vertices]
        ymin = min(v.y for v in vs)                      # the lip tips (furthest from the wall)
        face_y = ymin + 0.0265 - 0.012                  # just in front of the face plate
        far = [v for v in vs if v.y < face_y]
        far.sort(key=lambda v: v.x)
        clusters, cur = [], []
        for v in far:
            if cur and v.x - cur[-1].x > 0.004:
                clusters.append(cur); cur = []
            cur.append(v)
        if cur:
            clusters.append(cur)
        hooks = []
        for c in clusters:
            if len(c) < 20:
                continue
            xs = [v.x for v in c]
            ys = [v.y for v in c]
            arm = [v for v in c if v.y > min(ys) + 0.006]          # the straight part (not the lip)
            lip = [v for v in c if v.y < min(ys) + 0.004]
            hooks.append(dict(x=(min(xs) + max(xs)) / 2, w=max(xs) - min(xs),
                              arm_top=max(v.z for v in arm) if arm else max(v.z for v in c),
                              arm_bottom=min(v.z for v in arm) if arm else min(v.z for v in c),
                              y_out=min(ys), y_in=max(ys), lip_top=max(v.z for v in lip) if lip else None))
        return hooks


# ================================================================ keys on a split ring (modelled)
def _extrude(name, outline, depth, holes=(), mat=None, bevel=0.0004):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    def ring(pts):
        return [bm.verts.new((x, 0.0, z)) for x, z in pts]
    outer = ring(outline)
    f = bm.faces.new(outer)
    for h in holes:
        hv = ring(h)
        bm.faces.new(hv)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    # boolean-free hole: use a face with the hole subtracted by bmesh "faces from edges" is complex; instead build the
    # key head ring separately (see key()), so outlines here have no holes
    ext = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += depth
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    link(o)
    if mat:
        o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('bevel', 'BEVEL'); b.width = bevel; b.segments = 2; b.limit_method = 'ANGLE'
    return o


def _circle(cx, cz, r, n=40, a0=0.0, a1=2 * math.pi):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cz + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n)]


def key(name, mat, length=0.052, head_r=0.0125, kind='house'):
    """A flat key in the XZ plane, hanging from its hole at the origin (pointing down -Z), 2 mm thick along Y."""
    w = 0.0065
    head = []
    # head: a rounded bow with a 4 mm hole, made as an annulus (outer ring + inner ring bridged)
    o_r, i_r = head_r, 0.0028
    cz = -head_r + 0.001
    me = bpy.data.meshes.new(name + '_head')
    bm = bmesh.new()
    n = 48
    outer = [bm.verts.new((o_r * math.cos(2 * math.pi * i / n), -0.001, cz + 0.004 + o_r * math.sin(2 * math.pi * i / n))) for i in range(n)]
    inner = [bm.verts.new((i_r * math.cos(2 * math.pi * i / n), -0.001, 0.0 - 0.001 + i_r * math.sin(2 * math.pi * i / n))) for i in range(n)]
    # bow is an annulus around the hole, offset: build quads between rings
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((outer[i], outer[j], inner[j], inner[i]))
    ext = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co.y += 0.0022
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    head_o = link(bpy.data.objects.new(name + '_head', me))
    head_o.data.materials.append(mat)
    # blade with a shoulder and cuts (teeth on the right edge)
    top = cz + 0.004 - o_r + 0.002
    L = length - 2 * head_r
    pts = [(-0.004, top), (0.0045, top), (0.0045, top - 0.003), (w * 0.5, top - 0.004)]
    teeth = 7 if kind == 'house' else 0
    for k in range(teeth):
        z0 = top - 0.006 - k * (L - 0.008) / teeth
        depth = [0.0012, 0.0024, 0.0008, 0.002, 0.0016, 0.0026, 0.001][k % 7]
        pts += [(w * 0.5, z0), (w * 0.5 - depth, z0 - 0.0012), (w * 0.5, z0 - (L - 0.008) / teeth)]
    tip = top - L
    pts += [(w * 0.5, tip + 0.002), (0.0, tip), (-w * 0.5, tip + 0.003), (-w * 0.5, top - 0.004), (-0.004, top - 0.003)]
    blade = _extrude(name + '_blade', [(x, z) for x, z in pts], 0.0018, mat=mat)
    blade.location.y = -0.0008
    # groove along the blade
    g = _extrude(name + '_groove', [(-0.0012, top - 0.005), (0.0004, top - 0.005), (0.0004, tip + 0.004), (-0.0012, tip + 0.004)], 0.0003, mat=shared_mats()['rubber'])
    g.location.y = -0.0011
    grp = bpy.data.objects.new(name, None)
    link(grp)
    for o in (head_o, blade, g):
        o.parent = grp
    return grp


def split_ring(name, r=0.0115, wire=0.0011, turns=2.0):
    """a double-turn split ring as a helix, ring plane XZ (its axis along Y)"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = wire
    cu.bevel_resolution = 4
    sp = cu.splines.new('POLY')
    n = int(64 * turns)
    sp.points.add(n - 1)
    for i in range(n):
        a = 2 * math.pi * turns * i / (n - 1)
        sp.points[i].co = (r * math.cos(a), -0.0006 + 0.0012 * i / (n - 1), r * math.sin(a), 1)
    o = link(bpy.data.objects.new(name, cu))
    o.data.materials.append(shared_mats()['steel'])
    return o


class KeyBunch:
    """split ring + two keys (+ optional car keychain hanging on the ring). The ring hangs from a contact point
    (e.g. the top of a hook arm); keys hang from the bottom of the ring. Pendulum angles are given per frame."""

    def __init__(self, with_keychain=None):
        M = shared_mats()
        self.ring = split_ring('keyring')
        self.k1 = key('key_house', M['nickel'], 0.054)
        self.k2 = key('key_brass', M['brass'], 0.046)
        self.kc = with_keychain
        self.r = 0.0115

    def place(self, contact, swing, spin=0.0, k_swing=(0.0, 0.0), visible=True):
        """contact: world point the ring hangs from (top inside of the ring, e.g. the top of a hook arm). The ring
        hangs in the XZ plane (facing the camera) and swings about Y (the hook arm's axis). Keys hang from the
        ring's bottom, each with its own small swing. Returns the ring bottom."""
        c = Vector(contact)
        R = Matrix.Rotation(swing, 3, 'Y')
        ring_c = c + R @ Vector((0, 0, -self.r))
        self.ring.matrix_world = Matrix.Translation(ring_c) @ Matrix.Rotation(swing, 4, 'Y') @ Matrix.Rotation(spin, 4, 'Z')
        bottom = c + R @ Vector((0, 0, -2 * self.r + 0.0012))
        for k, ang, dx, base in ((self.k1, k_swing[0], -0.001, -0.3), (self.k2, k_swing[1], 0.001, 0.45)):
            k.matrix_world = (Matrix.Translation(bottom + Vector((dx, 0.0009 if dx > 0 else -0.0009, 0)))
                              @ Matrix.Rotation(swing + ang, 4, 'Y') @ Matrix.Rotation(spin * 0.6 + base, 4, 'Z'))
        for o in [self.ring, self.k1, self.k2]:
            o.hide_render = not visible
        return bottom


# ================================================================ Talon spinner
class Spinner:
    """A keychain finger spinner (talon, karambit, shield). Parts are found by material, not by name (node names
    collide between the GLBs): frame = petg_cf, races = steel (the inner one is the smaller), bearing shield =
    shield, split ring = splitring. The frame, outer race, shield and ring turn together; the inner race stays put."""

    def __init__(self, kind='talon'):
        path = os.path.join(GLB_RAW, f'{kind}_spinner.glb')
        if not os.path.exists(path):
            path = os.path.join(GLB_WEB, f'{kind}_spinner.glb')
        objs, new = import_glb(path)
        M = shared_mats()
        self.pivot = next(o for o in new if o.name.split('.')[0] == 'pivot')
        role = {}
        steel = []
        for o in new:
            if o.type != 'MESH' or not o.data.materials:
                continue
            mn = o.data.materials[0].name.split('.')[0]
            if mn == 'petg_cf': role['frame'] = o
            elif mn == 'splitring': role['ring'] = o
            elif mn == 'shield': role['shield'] = o
            elif mn == 'steel': steel.append(o)
        steel.sort(key=lambda o: max(o.dimensions))
        role['inner'], role['outer'] = steel[0], steel[-1]
        cf = principled('petg_cf', (0.014, 0.014, 0.016, 1), 0.66, coat=0.0, spec=0.22)
        nt = cf.node_tree
        noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 4000
        bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.12; bump.inputs['Distance'].default_value = 0.00002
        nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
        assign(role['frame'], cf)
        race = principled('race', (0.8, 0.81, 0.83, 1), 0.12, metal=1.0)
        assign(role['inner'], race); assign(role['outer'], race)
        assign(role['shield'], principled('bshield', (0.55, 0.56, 0.58, 1), 0.3, metal=1.0))
        assign(role['ring'], M['steel'])
        smooth(new)
        bpy.context.view_layer.update()
        self.talon, self.torus, inner = role['frame'], role['ring'], role['inner']
        self.frame = role['frame']
        self.inner = role['inner']
        dims = inner.dimensions
        self.axis = min(range(3), key=lambda i: dims[i])
        self.spin = bpy.data.objects.new('spin', None)
        link(self.spin)
        self.spin.parent = self.pivot
        self.spin.location = inner.location.copy()
        bpy.context.view_layer.update()
        for k in ('frame', 'outer', 'shield', 'ring'):
            o = role[k]
            mw = o.matrix_world.copy()
            o.parent = self.spin
            o.matrix_world = mw
        self.pivot.rotation_mode = 'QUATERNION'
        self.q0 = self.pivot.rotation_quaternion.copy()
        ax = Vector((0, 0, 0)); ax[self.axis] = 1
        world_axis = (self.pivot.matrix_world.to_3x3() @ ax).normalized()
        self.q_fix = world_axis.rotation_difference(Vector((0, -1, 0)))
        self.objects = new
        self.set(0.0)

    def set(self, angle, loc=(0, 0, 0), rot=(0, 0, 0)):
        ax = Vector((0, 0, 0)); ax[self.axis] = 1
        set_rot(self.spin, Quaternion(ax, angle))
        self.pivot.location = loc
        self.pivot.rotation_quaternion = Euler(rot, 'XYZ').to_quaternion() @ self.q_fix @ self.q0


# ================================================================ bake + render
class Track:
    """Everything that changes over a shot is keyframed once per frame, then the shot renders as an animation
    (real motion blur, resumable: frames already on disk are skipped)."""

    def __init__(self):
        self.objs, self.props, self.const = [], [], []

    def obj(self, *objs):
        for o in objs:
            if o not in self.objs:
                o.rotation_mode = 'QUATERNION'
                self.objs.append(o)
        return self

    def prop(self, owner, path, constant=False):
        self.props.append((owner, path, constant))
        return self

    def key(self, f):
        for o in self.objs:
            o.keyframe_insert('location', frame=f)
            o.keyframe_insert('rotation_quaternion', frame=f)
            o.keyframe_insert('hide_render', frame=f)
        for owner, path, _ in self.props:
            owner.keyframe_insert(path, frame=f)

    def finish(self):
        def fix(ad, constant):
            if ad and ad.action:
                for fc in iter_fcurves(ad.action):
                    for k in fc.keyframe_points:
                        k.interpolation = 'CONSTANT' if (constant or fc.data_path == 'hide_render') else 'LINEAR'
        for o in self.objs:
            fix(o.animation_data, False)
        seen = set()
        for owner, path, constant in self.props:
            idb = owner.id_data
            if id(idb) in seen:
                continue
            seen.add(id(idb))
            fix(idb.animation_data, constant)


def iter_fcurves(action):
    try:
        for fc in action.fcurves:
            yield fc
        return
    except Exception:
        pass
    for layer in action.layers:          # Blender 5 layered actions
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    yield fc


def bake_render(update, frames, out_dir, track, motion_blur=0.5, mb_steps=1):
    os.makedirs(out_dir, exist_ok=True)
    s = bpy.context.scene
    haze_m = bpy.data.materials.get('haze')
    if haze_m and 'hazenoise' in haze_m.node_tree.nodes:
        track.prop(haze_m.node_tree.nodes['hazenoise'].inputs['W'], 'default_value')
    for f in range(frames):
        update(f)
        set_haze_time(f / 30)
        track.key(f)
    track.finish()
    s.frame_start, s.frame_end = 0, frames - 1
    s.render.use_motion_blur = bool(motion_blur)
    if motion_blur:
        s.render.motion_blur_shutter = motion_blur
        try:
            s.eevee.motion_blur_steps = mb_steps
        except Exception:
            pass
    s.render.use_overwrite = False
    s.render.use_placeholder = True
    s.render.filepath = os.path.join(out_dir, '')
    bpy.ops.render.render(animation=True)
    print('SHOT_DONE', out_dir, flush=True)
