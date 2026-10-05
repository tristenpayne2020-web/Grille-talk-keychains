"""Blender side of make_spinners.py: organic smoothing, exact bearing pocket + keyring hole, print STLs, renders.
run: blender --background --factory-startup --python spinner/spinner_blender.py -- spinner/out/job.json"""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector

job = json.load(open(sys.argv[sys.argv.index('--') + 1]))
OUT, MM = job['out'], 0.001
B = job['bearing']
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)


def mat(name, rgb, rough, metal=0.0, bump=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if bump:   # fine noise: the matte, fibrous skin of carbon-filled PETG
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 9000; n.inputs['Detail'].default_value = 8
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.00004
        nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def lathe(name, prof, m, seg=96):
    """solid of revolution about Z from an (r, z) profile in mm"""
    bm = bmesh.new()
    vs = [bm.verts.new((r * MM, 0, z * MM)) for r, z in prof]
    edges = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.spin(bm, geom=vs + edges, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=seg, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    o.data.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    return o


def cutter(x, y, d, h):   # in mm: the frame is processed in mm (OpenVDB remesh is unreliable at metre-scale voxels)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=d / 2, depth=h, location=(x, y, 0))
    return bpy.context.active_object


def apply(o, mod):
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=mod.name)


def build_frame(d):
    bpy.ops.wm.stl_import(filepath=d['raw'])
    o = bpy.context.active_object
    r = o.modifiers.new('remesh', 'REMESH'); r.mode = 'VOXEL'; r.voxel_size = 0.3; apply(o, r)
    s = o.modifiers.new('smooth', 'CORRECTIVE_SMOOTH'); s.factor = 1.0; s.iterations = 30; s.use_only_smooth = True; apply(o, s)
    t = job['t_full']
    for c in (cutter(0, 0, job['pocket_d'], t * 3), cutter(*d['lug'], job['lug_hole_d'], t * 3)):
        bm_ = o.modifiers.new('cut', 'BOOLEAN'); bm_.operation = 'DIFFERENCE'; bm_.object = c; bm_.solver = 'EXACT'; apply(o, bm_)
        bpy.data.objects.remove(c)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    o.name = d['name']
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    bpy.ops.wm.stl_export(filepath=os.path.join(OUT, f"{d['name']}_spinner_{B['name']}.stl"), export_selected_objects=True)
    o.scale = (MM, MM, MM)
    bpy.ops.object.transform_apply(scale=True)
    return o


steel = mat('steel', (0.75, 0.76, 0.78), 0.18, metal=1.0)
shield = mat('shield', (0.62, 0.63, 0.66), 0.32, metal=1.0)
ring_m = mat('splitring', (0.72, 0.73, 0.75), 0.22, metal=1.0)


def bearing(x, y):
    ro, ri, w = B['od'] / 2, B['id'] / 2, B['w'] / 2
    parts = [lathe('outer', [(ro - 0.3, -w), (ro, -w + 0.3), (ro, w - 0.3), (ro - 0.3, w), (ro - 2.2, w), (ro - 2.2, -w)], steel),
             lathe('inner', [(ri + 2.2, -w), (ri + 2.2, w), (ri + 0.3, w), (ri, w - 0.3), (ri, -w + 0.3), (ri + 0.3, -w)], steel),
             lathe('shield', [(ro - 2.2, -w + 0.45), (ro - 2.2, w - 0.45), (ri + 2.2, w - 0.45), (ri + 2.2, -w + 0.45)], shield)]
    for p in parts:
        p.location = (x * MM, y * MM, 0)
    return parts


def split_ring(lug):
    dx, dy = lug
    n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
    R = 12.0
    bpy.ops.mesh.primitive_torus_add(major_radius=R * MM, minor_radius=0.75 * MM, major_segments=96, minor_segments=16,
                                     location=((dx + ux * R) * MM, (dy + uy * R) * MM, 0),
                                     rotation=(math.radians(90), 0, math.atan2(uy, ux)))
    t = bpy.context.active_object; t.data.materials.append(ring_m); bpy.ops.object.shade_smooth()
    t.rotation_euler.rotate_axis('Z', 0)
    return t


# ---------------------------------------------------------------- studio
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
prefs = bpy.context.preferences.addons['cycles'].preferences
for dev in ('OPTIX', 'CUDA'):
    try:
        prefs.compute_device_type = dev; prefs.get_devices()
        if any(d.type == dev for d in prefs.devices):
            for d in prefs.devices: d.use = True
            break
    except TypeError:
        pass
scene.cycles.samples = 128; scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'
scene.render.resolution_x = scene.render.resolution_y = 1600
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.02, 0.02, 0.022, 1)
bpy.ops.mesh.primitive_plane_add(size=2)   # dark matte floor for real contact shadows
floor = bpy.context.active_object; floor.data.materials.append(mat('floor', (0.035, 0.035, 0.038), 0.6))


def light(name, loc, size, energy):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy
    o = bpy.data.objects.new(name, l); bpy.context.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


light('key', (-0.18, -0.22, 0.30), 0.25, 2.2)
light('rim', (0.25, 0.20, 0.12), 0.15, 1.6)
light('top', (0.0, 0.0, 0.40), 0.40, 0.7)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam); scene.camera = cam
cam.data.lens = 85


def shoot(objs, path, elev=38, azim=-35, fill=1.25):
    lo = Vector((1, 1, 1)); hi = -lo
    for o in objs:
        for v in o.bound_box:
            w = o.matrix_world @ Vector(v); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    c = (lo + hi) / 2; size = (hi - lo).length * fill
    dist = size / (2 * math.tan(cam.data.angle / 2))
    e, a = math.radians(elev), math.radians(azim)
    cam.location = c + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


COLORS = {'truss': ('carbon black', (0.03, 0.03, 0.032)), 'talon': ('carbon blue', (0.03, 0.09, 0.30)),
          'halo': ('carbon red', (0.32, 0.03, 0.025))}
built = []
for d in job['designs']:
    f = build_frame(d)
    z = job['t_full'] / 2 * MM
    group = [f] + bearing(0, 0) + [split_ring(d['lug'])]
    for o in group:
        o.location.z += z
    built.append((d, f, group))

for d, f, group in built:   # one at a time: black PETG-CF hero, then its colour
    others = [o for _, _, g in built if g is not group for o in g]
    for o in others: o.hide_render = True
    for label, rgb in (('carbon black', (0.03, 0.03, 0.032)), COLORS[d['name']]):
        f.data.materials.clear(); f.data.materials.append(mat('petg_cf', rgb, 0.62, bump=0.35))
        shoot(group, os.path.join(OUT, f"{d['name']}_{label.replace(' ', '_')}.png"))
    for o in others: o.hide_render = False

# lineup: all three side by side, in their colours
for i, (d, f, group) in enumerate(built):
    f.data.materials.clear(); f.data.materials.append(mat('petg_cf', COLORS[d['name']][1], 0.62, bump=0.35))
    for o in group:
        o.location.x += (i - 1) * 0.085
scene.render.resolution_x = 2400; scene.render.resolution_y = 1200
shoot([o for _, _, g in built for o in g], os.path.join(OUT, 'lineup.png'), elev=55, azim=0, fill=0.75)
print('SPINNERS_DONE')
