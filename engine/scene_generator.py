# Run with Blender: blender -b -P engine/scene_generator.py
import bpy, math, json, pathlib, random
from mathutils import Vector

ROOT = pathlib.Path(__file__).resolve().parents[1]
story = json.loads((ROOT/"output/story.json").read_text(encoding="utf-8"))
cfg = json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
W, H = cfg["video"]["width"], cfg["video"]["height"]
outdir = ROOT/"output/scenes"
outdir.mkdir(parents=True, exist_ok=True)

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for m in bpy.data.materials:
        if m.users == 0: bpy.data.materials.remove(m)

def mat(name, color, rough=0.8):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = rough
    return m

def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def cylinder(name, loc, radius, depth, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    return o

def tree(x,y, trunk, leaf):
    cylinder("Tree trunk",(x,y,1.4),0.22,2.8,trunk)
    uv("Tree crown",(x,y,3.2),(1.0,0.9,1.1),leaf)
    uv("Tree crown",(x-0.55,y,2.9),(0.7,0.7,0.8),leaf)
    uv("Tree crown",(x+0.55,y,2.9),(0.7,0.7,0.8),leaf)

def make_character(kind, x, y, bodymat, cream, dark):
    uv("Character body",(x,y,1.05),(0.52,0.38,0.72),bodymat)
    uv("Character head",(x,y-0.02,2.0),(0.58,0.48,0.55),bodymat)
    # eyes
    for dx in [-0.20,0.20]:
        uv("Eye white",(x+dx,y-0.445,2.10),(0.105,0.06,0.13),cream)
        uv("Pupil",(x+dx,y-0.50,2.10),(0.045,0.035,0.065),dark)
    uv("Nose",(x,y-0.51,1.94),(0.09,0.05,0.06),dark)
    if kind == "rabbit":
        uv("Rabbit ear",(x-0.24,y,2.72),(0.15,0.13,0.52),bodymat)
        uv("Rabbit ear",(x+0.24,y,2.72),(0.15,0.13,0.52),bodymat)
    elif kind == "lion":
        for a in range(10):
            ang=2*math.pi*a/10
            uv("Mane",(x+0.55*math.cos(ang),y,2+0.55*math.sin(ang)),(0.25,0.22,0.27),dark)
        uv("Lion muzzle",(x,y-0.48,1.86),(0.25,0.12,0.17),cream)
    elif kind == "bird":
        uv("Bird wing",(x-0.34,y-0.02,1.15),(0.28,0.18,0.42),dark)
        uv("Bird beak",(x,y-0.56,1.98),(0.13,0.12,0.08),mat("Beak",(1.0,0.55,0.08)))
    else:
        # simple friendly humanoid arms
        for dx in [-0.65,0.65]:
            uv("Arm",(x+dx,y,1.15),(0.16,0.18,0.48),bodymat)
    return

def setup_scene(scene_no, text, chars):
    clear()
    ground=mat("Grass",(0.20,0.52,0.22))
    trunk=mat("Bark",(0.28,0.12,0.06))
    leaves=mat("Leaves",(0.10,0.42,0.16))
    sky=mat("Sky",(0.48,0.75,0.96))
    cream=mat("Eye white",(1,1,0.92))
    dark=mat("Dark",(0.08,0.05,0.04))
    # ground and sky backdrop
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,0))
    bpy.context.object.data.materials.append(ground)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0,8,12), rotation=(math.radians(90),0,0))
    bpy.context.object.data.materials.append(sky)
    for x in [-7,-4,4,7]:
        tree(x,2,trunk,leaves)
    # path
    pathmat=mat("Path",(0.62,0.46,0.28))
    bpy.ops.mesh.primitive_plane_add(size=5, location=(0,-1,0.015))
    bpy.context.object.scale=(1.0,3.0,1)
    bpy.context.object.data.materials.append(pathmat)
    palette={
      "lion":mat("Lion gold",(0.95,0.52,0.10)),
      "rabbit":mat("Rabbit cream",(0.92,0.88,0.78)),
      "girl":mat("Meera pink",(0.94,0.42,0.55)),
      "bird":mat("Bird blue",(0.15,0.55,0.92)),
      "woodcutter":mat("Mohan green",(0.20,0.48,0.24)),
      "fairy":mat("Fairy violet",(0.62,0.40,0.92)),
      "boy":mat("Boy teal",(0.12,0.55,0.58))
    }
    kinds=chars[:2] if chars else ["rabbit","lion"]
    if len(kinds)<2: kinds += ["bird"]
    make_character(kinds[0],-1.25,0,palette.get(kinds[0],palette["rabbit"]),cream,dark)
    make_character(kinds[1],1.25,0,palette.get(kinds[1],palette["lion"]),cream,dark)
    # soft lighting
    bpy.ops.object.light_add(type='AREA', location=(0,-5,9))
    light=bpy.context.object; light.data.energy=1500; light.data.shape='DISK'; light.data.size=8
    # camera
    bpy.ops.object.camera_add(location=(0,-12,5.0))
    cam=bpy.context.object
    direction=Vector((0,0,1.6))-cam.location
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    cam.data.lens=42
    scene=bpy.context.scene
    scene.camera=cam
    available_engines = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in available_engines else 'BLENDER_EEVEE'
    scene.render.resolution_x=W; scene.render.resolution_y=H; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False
    scene.world.color=(0.12,0.12,0.12)
    scene.view_settings.view_transform='Standard'
    scene.render.filepath=str(outdir/f"scene_{scene_no:02d}.png")
    scene.render.image_settings.color_mode='RGB'
    scene.render.resolution_percentage=75  # reduce free-run render time
    bpy.ops.render.render(write_still=True)

for item in story["scenes"]:
    setup_scene(item["number"], item["narration"], story.get("characters",[]))
print("Rendered", len(story["scenes"]), "3D story scenes.")
