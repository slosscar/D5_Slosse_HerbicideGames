"""Herbicide Games: posters on a Rome posting frame (mock-up scene, same low-poly style as the Arena Bus).
Run: HG_OUT=/path/out.png HG_RES=1600x900 HG_SAMPLES=16 python3 stall.py"""
import bpy, math, os

FONT = os.environ.get("HG_FONT", "")
TICKET = os.environ.get("HG_TICKET", "")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def mat(name, hexcol, rough=0.8, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    h = hexcol.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    c = tuple(x ** 2.2 for x in c)
    bsdf.inputs["Base Color"].default_value = (*c, 1)
    bsdf.inputs["Roughness"].default_value = rough
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*c, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    return m

M = {k: mat(k, v) for k, v in dict(
    red="#911C23", marble="#EBEAE6", grey="#3C3C3C", dark="#232323", travertine="#D8CDB6",
    trav_dark="#A99C83", shadow="#5E554A", sand="#CDBB98", wood="#7A5534", pig="#E3A79A",
    pigdark="#C98476", steel="#B9BCBF", skin="#D9A57E", jeans="#3E5A78", shirt1="#6F7F5A",
    shirt2="#B88A3A", shirt3="#4B4B5A", hair="#2A211C", blood="#5E0F14").items()}

def box(name, loc, size, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    o.data.materials.append(M[m])
    return o

def cyl(name, loc, r, depth, m, rot=(0, 0, 0), verts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(M[m])
    return o

def text(body, loc, size, m, rot=(math.radians(90), 0, 0), align="CENTER", extrude=0.01):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.active_object
    t.data.body = body
    if FONT and os.path.exists(FONT):
        t.data.font = bpy.data.fonts.load(FONT)
    t.data.size = size
    t.data.align_x = align
    t.data.align_y = "CENTER"
    t.data.extrude = extrude
    t.data.materials.append(M[m])
    return t

# street
box("Pavement", (0, 0, -0.05), (60, 14, 0.1), "travertine")
box("Road", (0, -10, -0.06), (60, 8, 0.1), "dark")
box("Kerb", (0, -6.0, 0.04), (60, 0.3, 0.12), "marble")
# buildings behind
cols = ["#C47A5A", "#E3CFAE", "#B9644A", "#D9B98C", "#C98E6A"]
for i, x in enumerate(range(-20, 21, 8)):
    mm = mat(f"bld{i}", cols[i % len(cols)])
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 6.5, 9))
    b = bpy.context.active_object; b.scale = (7.9, 4, 18); b.data.materials.append(mm)
    for fx in (-2.4, 0, 2.4):
        for fz in (4.2, 7.4, 10.6, 13.8):
            box("Win", (x + fx, 4.48, fz), (1.0, 0.05, 1.7), "dark")
    box("Door", (x - 2.4, 4.48, 1.3), (1.3, 0.05, 2.6), "grey")
# Rome-style posting frame: three 70 x 100 sheets
FX, FY = 0.6, 1.2
box("FrameTop", (FX, FY, 2.72), (2.6, 0.08, 0.08), "shirt1")
box("FrameBottom", (FX, FY, 1.48), (2.6, 0.08, 0.08), "shirt1")
for lx in (-1.27, 1.27):
    box("Leg", (FX + lx, FY, 1.38), (0.08, 0.08, 2.76), "shirt1")
box("Back", (FX, FY + 0.05, 2.1), (2.55, 0.03, 1.25), "grey")
tm = bpy.data.materials.new("PosterImg"); tm.use_nodes = True
nt = tm.node_tree; tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(os.environ["HG_POSTER"])
bsdf = nt.nodes.get("Principled BSDF"); nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.55
for k, px in enumerate((-0.84, 0.0, 0.84)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(FX + px, FY - 0.01, 2.1), rotation=(math.radians(90), 0, 0))
    p = bpy.context.active_object; p.scale = (0.8, 1.15, 1); p.data.materials.append(tm)

def person(x, y, shirt, h=1.75, yaw=0):
    r = math.radians(yaw)
    box("Legs", (x, y, h * 0.24), (0.32, 0.2, h * 0.48), "jeans", (0, 0, r))
    box("Torso", (x, y, h * 0.62), (0.44, 0.24, h * 0.32), shirt, (0, 0, r))
    box("Head", (x, y, h * 0.86), (0.2, 0.22, 0.24), "skin", (0, 0, r))
    box("Hair", (x, y - 0.03, h * 0.93), (0.22, 0.22, 0.1), "hair", (0, 0, r))
person(2.7, -0.4, "red", 1.74, -70)
person(-2.4, 0.3, "shirt3", 1.68, 80)

bpy.ops.object.light_add(type="SUN", location=(0, 0, 20), rotation=(math.radians(52), math.radians(8), math.radians(-30)))
sun = bpy.context.active_object; sun.data.energy = 4.2; sun.data.angle = math.radians(2)
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes.get("Background"); bg.inputs["Color"].default_value = (0.55, 0.66, 0.78, 1); bg.inputs["Strength"].default_value = 0.9
bpy.ops.object.camera_add(location=(-0.5, -3.1, 1.7), rotation=(math.radians(92), 0, math.radians(-14)))
cam = bpy.context.active_object; cam.data.lens = 26; scene.camera = cam
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"
scene.cycles.samples = int(os.environ.get("HG_SAMPLES", "16")); scene.cycles.use_denoising = True
W, H = [int(v) for v in os.environ.get("HG_RES", "800x450").split("x")]
scene.render.resolution_x, scene.render.resolution_y = W, H; scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "Standard"
img = scene.render.image_settings
if hasattr(img, "media_type"): img.media_type = "IMAGE"
img.file_format = "PNG"; scene.render.filepath = os.environ["HG_OUT"]
bpy.ops.render.render(write_still=True)
print("DONE wall", W, H, flush=True)
