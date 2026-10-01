"""Creality Print project 3MF with SEVERAL different objects on one plate (each object = coloured parts).
Same layout as write3mf.py (which writes N copies of one object)."""
import zipfile, json, uuid, io
import numpy as np
from write3mf import NS, _uuid, _fmt, mesh_xml


def write_3mf_multi(path, objects, project_settings, app_version='7.2.2.5483', date='2026-09-27', thumbnail_png=None, title='plate'):
    """objects: list of {name, parts: [{name, mesh, extruder}], pos: (x, y) bed position of the object's bbox centre}."""
    res, build, objfiles, ms_objects, instances, assemble = [], [], {}, [], [], []
    for oi, ob in enumerate(objects, 1):
        parts = ob['parts']
        pids = [((k + 1) << 16) | oi for k in range(len(parts))]
        allv = np.vstack([np.asarray(p['mesh'].vertices) for p in parts])
        mn, mx = allv.min(0), allv.max(0)
        tx, ty, tz = ob['pos'][0] - (mn[0] + mx[0]) / 2, ob['pos'][1] - (mn[1] + mx[1]) / 2, -mn[2]
        tf = f"1 0 0 0 1 0 0 0 1 {_fmt(tx)} {_fmt(ty)} {_fmt(tz)}"
        comps = '\n'.join(f'    <component p:path="/3D/Objects/object_{oi}.model" objectid="{pid}" p:UUID="{_uuid(pid)}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' for pid in pids)
        res.append(f'  <object id="{oi}" p:UUID="{_uuid(oi)}" type="model">\n   <components>\n{comps}\n   </components>\n  </object>')
        build.append(f'  <item objectid="{oi}" p:UUID="{_uuid(oi + 4096)}" transform="{tf}" printable="1"/>')
        objs = [f'  <object id="{pid}" p:UUID="{_uuid(pid)}" type="model">\n{mesh_xml(p["mesh"])}\n  </object>' for pid, p in zip(pids, parts)]
        objfiles[f'3D/Objects/object_{oi}.model'] = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
                                                     f' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n' + '\n'.join(objs) + '\n </resources>\n <build/>\n</model>\n')
        pxml = []
        for pid, p in zip(pids, parts):
            v = np.asarray(p['mesh'].vertices)
            pxml.append(f'''    <part id="{pid}" subtype="normal_part">
      <metadata key="name" value="{p['name']}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="{p['name']}.stl"/>
      <metadata key="source_object_id" value="0"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="{_fmt((v[:,0].min()+v[:,0].max())/2 + tx)}"/>
      <metadata key="source_offset_y" value="{_fmt((v[:,1].min()+v[:,1].max())/2 + ty)}"/>
      <metadata key="source_offset_z" value="{_fmt((v[:,2].min()+v[:,2].max())/2 + tz)}"/>
      <metadata key="extruder" value="{p['extruder']}"/>
      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>''')
        ms_objects.append(f'  <object id="{oi}">\n    <metadata key="name" value="{ob["name"]}"/>\n    <metadata key="extruder" value="1"/>\n' + '\n'.join(pxml) + '\n  </object>')
        instances.append(f'''    <model_instance>
      <metadata key="object_id" value="{oi}"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="{100 + oi}"/>
    </model_instance>''')
        assemble.append(f'   <assemble_item object_id="{oi}" instance_id="0" transform="{tf}" offset="0 0 0" />')
    model = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
             f' <metadata name="Application">Creality_Print V{app_version} Release</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
             f' <metadata name="CreationDate">{date}</metadata>\n <metadata name="ModificationDate">{date}</metadata>\n'
             f' <metadata name="Thumbnail_Middle">/Metadata/plate_1.png</metadata>\n <metadata name="Thumbnail_Small">/Metadata/plate_1_small.png</metadata>\n'
             f' <metadata name="Title">{title}</metadata>\n <resources>\n' + '\n'.join(res) + f'\n </resources>\n <build p:UUID="{uuid.uuid4()}">\n' + '\n'.join(build) + '\n </build>\n</model>\n')
    model_settings = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(ms_objects) + '''
  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value=""/>
    <metadata key="locked" value="false"/>
    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>
    <metadata key="thumbnail_no_light_file" value="Metadata/plate_no_light_1.png"/>
    <metadata key="top_file" value="Metadata/top_1.png"/>
    <metadata key="pick_file" value="Metadata/pick_1.png"/>
''' + '\n'.join(instances) + '\n  </plate>\n  <assemble>\n' + '\n'.join(assemble) + '\n  </assemble>\n</config>\n')
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
    model_rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
                  '\n'.join(f' <Relationship Target="/3D/Objects/object_{oi}.model" Id="rel-{oi}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
                            for oi in range(1, len(objects) + 1)) + '\n</Relationships>\n')
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
        for n, s in objfiles.items():
            z.writestr(n, s)
        z.writestr('Metadata/model_settings.config', model_settings)
        z.writestr('Metadata/project_settings.config', json.dumps(project_settings, indent=4, ensure_ascii=False))
        z.writestr('Metadata/creality.config', creality_cfg)
        z.writestr('Metadata/slice_info.config', slice_info)
        if thumbnail_png is not None:
            from PIL import Image
            im = Image.open(thumbnail_png).convert('RGBA')
            for name, size in (('Metadata/plate_1.png', 512), ('Metadata/plate_1_small.png', 128), ('Metadata/plate_no_light_1.png', 512),
                               ('Metadata/top_1.png', 512), ('Metadata/pick_1.png', 512)):
                t = im.copy(); t.thumbnail((size, size))
                canvas = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                canvas.paste(t, ((size - t.width) // 2, (size - t.height) // 2))
                b = io.BytesIO(); canvas.save(b, 'PNG'); z.writestr(name, b.getvalue())
    return path
