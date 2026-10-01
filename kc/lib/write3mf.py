"""Write a Creality Print / OrcaSlicer / Bambu Studio style project 3MF.

Layout mirrors what Creality Print 7.2.2 writes (see the real backup in ./bp):
  [Content_Types].xml, _rels/.rels, 3D/3dmodel.model (components object + build item),
  3D/_rels/3dmodel.model.rels, 3D/Objects/object_1.model (the meshes),
  Metadata/model_settings.config (parts + per-part extruder), Metadata/project_settings.config,
  Metadata/creality.config, Metadata/slice_info.config, Metadata/plate_1.png(+_small)
"""
import zipfile, json, uuid, io
import numpy as np

NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')


def _uuid(prefix_int):
    return f"{prefix_int:08x}-{uuid.uuid4().hex[8:12]}-{uuid.uuid4().hex[12:16]}-{uuid.uuid4().hex[16:20]}-{uuid.uuid4().hex[20:32]}"


def _fmt(x):
    return ('%.9g' % x)


def mesh_xml(mesh):
    v = np.asarray(mesh.vertices, dtype=np.float64)
    f = np.asarray(mesh.faces, dtype=np.int64)
    out = ['    <mesh>', '     <vertices>']
    out.extend(f'      <vertex x="{_fmt(x)}" y="{_fmt(y)}" z="{_fmt(z)}"/>' for x, y, z in v)
    out.append('     </vertices>')
    out.append('     <triangles>')
    out.extend(f'      <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in f)
    out.append('     </triangles>')
    out.append('    </mesh>')
    return '\n'.join(out)


def write_3mf(path, parts, project_settings, object_name='house keychain', app_version='7.2.2.5483',
              date='2026-09-23', bed_center=(130.0, 130.0), thumbnail_png=None, extra_object_metadata=None,
              positions=None, layer_ranges=None, pauses=None):
    """parts: list of dicts {name, mesh (trimesh), extruder (1-based int), config (optional dict of per-part
    process overrides, e.g. {'fuzzy_skin': 'none'})}.
    positions: optional list of (x, y) bed positions for the object's bbox centre -> one instance each
    (default: a single instance at bed_center).
    layer_ranges: optional list of (min_z, max_z, {opt_key: value}) height-range modifiers for the object
    (written to Metadata/layer_config_ranges.xml; a layer belongs to a range when min_z < print_z <= max_z).
    pauses: optional list of layer top_z values; the printer pauses (machine_pause_gcode) before printing that
    layer (written to Metadata/custom_gcode_per_layer.xml as CustomGCode type 1 = PausePrint)."""
    obj_id = 1
    part_ids = [((k + 1) << 16) | obj_id for k in range(len(parts))]
    obj_uuid = _uuid(obj_id)

    # place the object at the bed centre (XY) with Z on the plate
    allv = np.vstack([np.asarray(p['mesh'].vertices) for p in parts])
    mn, mx = allv.min(axis=0), allv.max(axis=0)
    cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
    if positions is None:
        positions = [bed_center]
    tfs = []
    for pos in positions:
        px, py = pos[0], pos[1]
        rot = pos[2] if len(pos) > 2 else 0.0
        c, s = np.cos(np.radians(rot)), np.sin(np.radians(rot))
        if abs(c) < 1e-12: c = 0.0
        if abs(s) < 1e-12: s = 0.0
        # 3MF: p' = p * M (row vector); rotation about Z by rot, then translate so the bbox centre lands on (px, py)
        rcx, rcy = c * cx - s * cy, s * cx + c * cy
        tx, ty, tz = px - rcx, py - rcy, -mn[2]
        tfs.append((tx, ty, tz, f"{_fmt(c)} {_fmt(s)} 0 {_fmt(-s)} {_fmt(c)} 0 0 0 1 {_fmt(tx)} {_fmt(ty)} {_fmt(tz)}"))
    tx, ty, tz, build_tf = tfs[0]
    build_items = '\n'.join(f'  <item objectid="{obj_id}" p:UUID="{_uuid(obj_id + 256 * i)}" transform="{t[3]}" printable="1"/>' for i, t in enumerate(tfs))
    model_instances = '\n'.join(f'''    <model_instance>
      <metadata key="object_id" value="{obj_id}"/>
      <metadata key="instance_id" value="{i}"/>
      <metadata key="identify_id" value="{obj_id * 100 + 1 + i}"/>
    </model_instance>''' for i in range(len(tfs)))
    assemble_items = '\n'.join(f'   <assemble_item object_id="{obj_id}" instance_id="{i}" transform="{t[3]}" offset="0 0 0" />' for i, t in enumerate(tfs))

    # ---------------- 3D/3dmodel.model
    comp = '\n'.join(
        f'    <component p:path="/3D/Objects/object_{obj_id}.model" objectid="{pid}" p:UUID="{_uuid((k+1) << 16 | obj_id)}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
        for k, pid in enumerate(part_ids))
    model = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" {NS}>
 <metadata name="Application">Creality_Print V{app_version} Release</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="Copyright"></metadata>
 <metadata name="CreationDate">{date}</metadata>
 <metadata name="Description"></metadata>
 <metadata name="Designer"></metadata>
 <metadata name="DesignerCover"></metadata>
 <metadata name="DesignerUserId"></metadata>
 <metadata name="License"></metadata>
 <metadata name="ModificationDate">{date}</metadata>
 <metadata name="Origin"></metadata>
 <metadata name="Thumbnail_Middle">/Metadata/plate_1.png</metadata>
 <metadata name="Thumbnail_Small">/Metadata/plate_1_small.png</metadata>
 <metadata name="Title">{object_name}</metadata>
 <resources>
  <object id="{obj_id}" p:UUID="{obj_uuid}" type="model">
   <components>
{comp}
   </components>
  </object>
 </resources>
 <build p:UUID="{uuid.uuid4()}">
{build_items}
 </build>
</model>
'''
    # ---------------- 3D/Objects/object_1.model
    objs = []
    for k, (pid, part) in enumerate(zip(part_ids, parts)):
        objs.append(f'  <object id="{pid}" p:UUID="{_uuid(pid)}" type="model">\n{mesh_xml(part["mesh"])}\n  </object>')
    objects_model = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" {NS}>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <resources>
{chr(10).join(objs)}
 </resources>
 <build/>
</model>
'''
    # ---------------- Metadata/model_settings.config
    parts_xml = []
    for pid, part in zip(part_ids, parts):
        v = np.asarray(part['mesh'].vertices)
        parts_xml.append(f'''    <part id="{pid}" subtype="normal_part">
      <metadata key="name" value="{part['name']}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="{part['name']}.stl"/>
      <metadata key="source_object_id" value="0"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="{_fmt((v[:,0].min()+v[:,0].max())/2 + tx)}"/>
      <metadata key="source_offset_y" value="{_fmt((v[:,1].min()+v[:,1].max())/2 + ty)}"/>
      <metadata key="source_offset_z" value="{_fmt((v[:,2].min()+v[:,2].max())/2 + tz)}"/>
      <metadata key="extruder" value="{part['extruder']}"/>''' + ''.join(f'\n      <metadata key="{k}" value="{v}"/>' for k, v in part.get('config', {}).items()) + '''
      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>''')
    extra_md = ''
    if extra_object_metadata:
        extra_md = '\n' + '\n'.join(f'    <metadata key="{k}" value="{v}"/>' for k, v in extra_object_metadata.items())
    model_settings = f'''<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="{obj_id}">
    <metadata key="name" value="{object_name}"/>
    <metadata key="extruder" value="1"/>{extra_md}
{chr(10).join(parts_xml)}
  </object>
  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value=""/>
    <metadata key="locked" value="false"/>
    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>
    <metadata key="thumbnail_no_light_file" value="Metadata/plate_no_light_1.png"/>
    <metadata key="top_file" value="Metadata/top_1.png"/>
    <metadata key="pick_file" value="Metadata/pick_1.png"/>
{model_instances}
  </plate>
  <assemble>
{assemble_items}
  </assemble>
</config>
'''
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>
'''
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>
 <Relationship Target="/Metadata/plate_1.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-middle"/>
 <Relationship Target="/Metadata/plate_1_small.png" Id="rel-5" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>
</Relationships>
'''
    model_rels = f'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/Objects/object_{obj_id}.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
'''
    creality_cfg = f'''<?xml version="1.0" encoding="UTF-8"?>
<config>
    <metadata key="Company" value="Creality"/>
    <metadata key="Application" value="Creality_Print"/>
    <metadata key="AppVersion" value="{app_version}"/>
    <metadata key="AppStage" value="Release"/>
    <metadata key="FileVersion" value="1.0"/>
    <metadata key="FileType" value="Undefined"/>
    <metadata key="CreationDate" value="{date}"/>
</config>
'''
    slice_info = '''<?xml version="1.0" encoding="UTF-8"?>
<config>
  <header>
    <header_item key="X-CX-Client-Type" value="creality_print"/>
    <header_item key="X-CX-Client-Version" value="07.02.02.5483"/>
  </header>
</config>
'''
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', model)
        z.writestr('3D/_rels/3dmodel.model.rels', model_rels)
        z.writestr(f'3D/Objects/object_{obj_id}.model', objects_model)
        z.writestr('Metadata/model_settings.config', model_settings)
        z.writestr('Metadata/project_settings.config', json.dumps(project_settings, indent=4, ensure_ascii=False))
        z.writestr('Metadata/creality.config', creality_cfg)
        z.writestr('Metadata/slice_info.config', slice_info)
        if pauses:
            pause_gcode = project_settings.get('machine_pause_gcode', 'PAUSE')
            cg = ['<?xml version="1.0" encoding="utf-8"?>', '<custom_gcodes_per_layer>', '<plate>', '<plate_info id="1"/>']
            cg += [f'<layer top_z="{_fmt(zp)}" type="1" extruder="1" color="" extra="" gcode="{pause_gcode}"/>' for zp in pauses]
            cg += ['<mode value="MultiExtruder"/>', '</plate>', '</custom_gcodes_per_layer>', '']
            z.writestr('Metadata/custom_gcode_per_layer.xml', '\n'.join(cg))
        if layer_ranges:
            ranges_xml =['<?xml version="1.0" encoding="UTF-8"?>', '<objects>', f' <object id="{obj_id}">']
            for zmin, zmax, opts in layer_ranges:
                ranges_xml.append(f'  <range min_z="{_fmt(zmin)}" max_z="{_fmt(zmax)}">')
                ranges_xml.extend(f'   <option opt_key="{k}">{v}</option>' for k, v in opts.items())
                ranges_xml.append('  </range>')
            ranges_xml += [' </object>', '</objects>', '']
            z.writestr('Metadata/layer_config_ranges.xml', '\n'.join(ranges_xml))
        if thumbnail_png is not None:
            from PIL import Image
            im = Image.open(thumbnail_png).convert('RGBA')
            for name, size in (('Metadata/plate_1.png', 512), ('Metadata/plate_1_small.png', 128), ('Metadata/plate_no_light_1.png', 512), ('Metadata/top_1.png', 512), ('Metadata/pick_1.png', 512)):
                t = im.copy(); t.thumbnail((size, size))
                canvas = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                canvas.paste(t, ((size - t.width) // 2, (size - t.height) // 2))
                b = io.BytesIO(); canvas.save(b, 'PNG'); z.writestr(name, b.getvalue())
    return path
