"""Photoreal product renders in Blender (Cycles, GPU). Run by tools/make_images_blender.py, one Blender process per
product:  blender --background --factory-startup --python site/tools/blender_render.py -- <job.json>

The job gives the raw GLB (site/build/glb_raw/<id>.glb, nodes keychain > body / details / lights / back / lettering,
link_0..n, ring), the body colors and the views. Framing matches the old three.js renders exactly (20 degree field of
view, the target's bounding box x 1.12), so file names, crops and the headlight masks stay interchangeable.

Look: printed PLA (satin, faint 0.2 mm layer lines on the walls), matte or metallic body, glossy black details, a
glossy carbon-fibre back (textured build plate) with white lettering, brushed-steel chain and rings, lit by a softbox
studio (big key from the upper left, fill, rim, top strip) on a transparent background.
"""
import bpy, json, math, os, sys
from mathutils import Vector, Matrix

job = json.load(open(sys.argv[sys.argv.index('--') + 1]))


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h):
    h = h.lstrip('#')
    return tuple(srgb_to_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)


# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
cy = scene.cycles
cy.device = 'GPU'
prefs = bpy.context.preferences.addons['cycles'].preferences
for dev_type in ('OPTIX', 'CUDA'):
    try:
        prefs.compute_device_type = dev_type
        prefs.get_devices()
        if any(d.type == dev_type for d in prefs.devices):
            break
    except TypeError:
        continue
for d in prefs.devices:
    d.use = True
cy.samples = job.get('samples', 160)
cy.use_denoising = True
cy.use_adaptive_sampling = True
cy.max_bounces = 8
scene.render.film_transparent = True
scene.render.resolution_x = scene.render.resolution_y = job.get('size', 2000)
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'

world = bpy.data.worlds.new('studio')
scene.world = world
world.use_nodes = True
wn = world.node_tree.nodes
wn['Background'].inputs['Color'].default_value = (0.035, 0.035, 0.04, 1)
wn['Background'].inputs['Strength'].default_value = 1.0

bpy.ops.import_scene.gltf(filepath=job['glb'])
objs = {o.name.split('.')[0]: o for o in bpy.data.objects}
kc = objs.get('keychain')
chain = [o for n, o in objs.items() if n.startswith('link_') or n == 'ring']


# ---------------------------------------------------------------- materials
def principled(name, color, rough, metal=0.0, coat=0.0, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Specular IOR Level'].default_value = spec
    return m


def add_layer_lines(m, strength=0.08):
    """0.2 mm printed layers: bands along the print direction (glTF +Z face = Blender -Y), faint bump."""
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


def body_material(c):
    metal = float(c.get('metal', 0))
    if metal > 0.3:   # metallic PLA: fine sparkle, satin sheen
        m = principled('body', hex_lin(c['hex']), 0.34, metal=0.75, coat=0.15)
    else:
        m = principled('body', hex_lin(c['hex']), 0.52 if c['name'] == 'White' else 0.62, coat=0.05)
    add_layer_lines(m)
    return m


details = principled('details', (0.006, 0.006, 0.007, 1), 0.38, coat=0.1)
add_layer_lines(details, 0.06)
lights = principled('lights', (0.9, 0.9, 0.88, 1), 0.45)
add_layer_lines(lights, 0.05)
lettering = principled('lettering', (0.85, 0.85, 0.83, 1), 0.4)
steel = principled('metal', (0.72, 0.73, 0.75, 1), 0.2, metal=1.0)
# carbon back: keep the GLB's twill texture, make it glossy like a textured PEI print
back_obj = objs.get('back')
if back_obj and back_obj.active_material:
    bm = back_obj.active_material
    bb = bm.node_tree.nodes.get('Principled BSDF')
    if bb:
        bb.inputs['Roughness'].default_value = 0.22
        bb.inputs['Coat Weight'].default_value = 0.35
        bb.inputs['Coat Roughness'].default_value = 0.12

for name, mat in (('details', details), ('lights', lights), ('lettering', lettering)):
    if name in objs and objs[name].type == 'MESH':
        objs[name].data.materials.clear(); objs[name].data.materials.append(mat)
for o in chain:
    if o.type == 'MESH':
        o.data.materials.clear(); o.data.materials.append(steel)
for o in bpy.data.objects:
    if o.type == 'MESH':
        for p in o.data.polygons:
            p.use_smooth = True
        o.data.shade_auto_smooth(angle=math.radians(30)) if hasattr(o.data, 'shade_auto_smooth') else None

# ---------------------------------------------------------------- studio lights (sized to the product)
def area(name, loc, size, energy, target=(0, 0, 0), shape='RECTANGLE', size_y=None):
    l = bpy.data.lights.new(name, 'AREA')
    l.energy = energy; l.size = size; l.shape = shape
    if size_y:
        l.size_y = size_y
    o = bpy.data.objects.new(name, l)
    scene.collection.objects.link(o)
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o


def bbox(objs_):
    pts = [o.matrix_world @ Vector(c) for o in objs_ if o.type == 'MESH' for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


body_objs = [o for o in kc.children_recursive if o.type == 'MESH'] if kc else [o for o in bpy.data.objects if o.type == 'MESH']
lo, hi = bbox(body_objs)
ctr = (lo + hi) / 2
S = max((hi - lo).x, (hi - lo).z)               # product size (m)
E = job.get('exposure', 1.0) * (S / 0.088) ** 2      # light power scales with the product size (distance squared)
area('key', ctr + Vector((-1.2 * S, -2.2 * S, 1.5 * S)), 2.2 * S, 3.2 * E, ctr)
area('fill', ctr + Vector((1.8 * S, -2.0 * S, 0.2 * S)), 3.0 * S, 1.1 * E, ctr)
area('rim', ctr + Vector((0.6 * S, 1.8 * S, 1.4 * S)), 1.6 * S, 2.2 * E, ctr)
area('top', ctr + Vector((0, -0.6 * S, 2.4 * S)), 2.6 * S, 1.6 * E, ctr, size_y=0.6 * S)
area('back', ctr + Vector((0.4 * S, 2.6 * S, 0.6 * S)), 2.4 * S, 1.8 * E, ctr)   # for the carbon back views

# ---------------------------------------------------------------- camera (same framing as the three.js renders)
cam_data = bpy.data.cameras.new('cam')
cam_data.sensor_fit = 'VERTICAL'
cam_data.angle = math.radians(20)
cam_data.clip_start = 0.001; cam_data.clip_end = 20
cam = bpy.data.objects.new('cam', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam


def frame(targets):
    bpy.context.view_layer.update()
    l, h = bbox(targets)
    c = (l + h) / 2
    s = h - l
    fit = max(s.x, s.z) * 1.12
    dist = fit / 2 / math.tan(math.radians(10))
    cam.location = Vector((c.x, c.y - dist, c.z))        # the face looks along -Y (glTF +Z)
    cam.rotation_euler = (math.radians(90), 0, 0)


holdout = bpy.data.materials.new('holdout')
holdout.use_nodes = True
hn = holdout.node_tree.nodes
hn.clear()
ho = hn.new('ShaderNodeHoldout'); out = hn.new('ShaderNodeOutputMaterial')
holdout.node_tree.links.new(ho.outputs[0], out.inputs['Surface'])
glow = bpy.data.materials.new('maskwhite')
glow.use_nodes = True
gn = glow.node_tree.nodes
gn.clear()
em = gn.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.0; gout = gn.new('ShaderNodeOutputMaterial')
glow.node_tree.links.new(em.outputs[0], gout.inputs['Surface'])

body_obj = objs.get('body')
saved = {o.name: list(o.data.materials) for o in bpy.data.objects if o.type == 'MESH'}


base_matrix = kc.matrix_basis.copy() if kc else None


def set_view(view):
    show_chain = view.get('chain', False)
    for o in chain:
        o.hide_render = not show_chain
    if kc:   # turn the keychain about the vertical axis through its pivot (the keyring hole), chain left as it hangs
        kc.matrix_basis = Matrix.Rotation(view.get('angle', 0.0), 4, 'Z') @ base_matrix
    targets = body_objs + ([o for o in chain if o.type == 'MESH'] if show_chain else [])
    frame(targets)


def render(path, mask=False):
    if mask:
        cy.samples = 1; cy.use_denoising = False
        for o in bpy.data.objects:
            if o.type == 'MESH':
                o.data.materials.clear()
                o.data.materials.append(glow if o.name.split('.')[0] == 'lights' else holdout)
        scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    if mask:
        for o in bpy.data.objects:
            if o.type == 'MESH':
                o.data.materials.clear()
                for m in saved[o.name]:
                    o.data.materials.append(m)
        cy.samples = job.get('samples', 160); cy.use_denoising = True
        scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'


for v in job['views']:
    set_view(v)
    if v.get('mask'):
        render(v['out'], mask=True)
        continue
    for c in v.get('colors', [None]):
        if c and body_obj:
            body_obj.data.materials.clear(); body_obj.data.materials.append(body_material(c))
            saved[body_obj.name] = list(body_obj.data.materials)
        render(v['out'].format(slug=c['slug']) if c else v['out'])
print('BLENDER_DONE', job['id'])
