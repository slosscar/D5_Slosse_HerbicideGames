"""Herbicide Games: the slaughter stall next to the arena (mock-up scene, same low-poly style as the Arena Bus).
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

# ground
box("Ground", (0, 0, -0.05), (80, 80, 0.1), "sand")

# the arena: two storeys of arches behind the stall
for i in range(-9, 10):
    x = i * 3.4
    for lvl, (z0, h) in enumerate(((0, 6.0), (6.6, 5.2))):
        box(f"Pier{i}_{lvl}", (x, 14, z0 + h / 2), (0.9, 1.6, h), "travertine")
    box(f"Back{i}", (x + 1.7, 15.2, 6), (2.6, 0.3, 12), "shadow")
    for (top, spring) in ((6.0, 4.45), (11.8, 10.25)):
        sp = box(f"Spandrel{i}", (x + 1.7, 14, (spring + top) / 2), (2.6, 1.6, top - spring), "travertine")
        cut = cyl(f"Cut{i}", (x + 1.7, 14, spring), 1.25, 3.0, "shadow", rot=(math.radians(90), 0, 0), verts=32)
        mod = sp.modifiers.new("arch", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cut
        bpy.context.view_layer.objects.active = sp
        bpy.ops.object.modifier_apply(modifier="arch")
        bpy.data.objects.remove(cut, do_unlink=True)
for lvl, z in enumerate((6.3, 12.1, 14.6)):
    box(f"Cornice{lvl}", (0, 13.9, z), (66, 1.9, 0.6 if lvl < 2 else 4.4), "travertine" if lvl < 2 else "trav_dark")
# banner on the arena
box("Banner", (-6.8, 13.0, 9.2), (9.6, 0.05, 2.0), "red")
text("HERBICIDE GAMES", (-6.8, 12.95, 9.45), 0.85, "marble")
text("21–23 APRIL 2027 · ROME", (-6.8, 12.95, 8.65), 0.36, "marble")

# the stall
SX, SY = 1.5, 3.5
box("Counter", (SX, SY, 0.55), (3.6, 1.1, 1.1), "wood")
box("CounterTop", (SX, SY, 1.13), (3.8, 1.25, 0.06), "marble")
for dx in (-1.85, 1.85):
    for dy in (-0.55, 0.9):
        box("Post", (SX + dx, SY + dy, 1.3), (0.09, 0.09, 2.6), "dark")
# striped awning, sloping to the front
for k in range(8):
    w = 4.0 / 8
    x = SX - 2.0 + w / 2 + k * w
    box(f"Awning{k}", (x, SY - 0.1, 2.7), (w, 1.9, 0.05), "red" if k % 2 == 0 else "marble", rot=(math.radians(-14), 0, 0))
box("Valance", (SX, SY - 1.06, 2.37), (4.0, 0.04, 0.32), "red")
# sign board on top
box("SignBoard", (SX, SY + 0.35, 3.62), (3.4, 0.08, 0.86), "grey")
text("THE BUTCHER'S STALL", (SX, SY + 0.30, 3.74), 0.36, "marble")
text("NEXT TO THE ARENA · SEE WHAT YOU PAY FOR", (SX, SY + 0.30, 3.42), 0.14, "marble")
# butcher's block, cleaver, hooks
box("Block", (SX + 0.9, SY - 0.05, 1.32), (0.8, 0.6, 0.32), "wood")
box("CleaverBlade", (SX + 0.9, SY - 0.05, 1.55), (0.32, 0.03, 0.18), "steel", rot=(0, math.radians(-8), 0))
box("CleaverHandle", (SX + 1.17, SY - 0.05, 1.6), (0.22, 0.04, 0.05), "dark", rot=(0, math.radians(-8), 0))
box("Rail", (SX, SY + 0.55, 2.25), (3.6, 0.05, 0.05), "steel")
for hx in (-1.2, -0.7, -0.2):
    box("Hook", (SX + hx, SY + 0.55, 2.12), (0.03, 0.03, 0.22), "steel")
# price sign: the festival ticket as a price tag
if TICKET and os.path.exists(TICKET):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(SX - 0.8, SY - 0.66, 1.62), rotation=(math.radians(86), 0, math.radians(3)))
    p = bpy.context.active_object
    p.scale = (0.9, 1.15, 1)
    tm = bpy.data.materials.new("TicketImg")
    tm.use_nodes = True
    nt = tm.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(TICKET)
    bsdf = nt.nodes.get("Principled BSDF")
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.6
    p.data.materials.append(tm)
    box("TicketStand", (SX - 0.8, SY - 0.6, 1.2), (0.05, 0.05, 0.2), "dark")

# pen with pigs, to the right of the stall
PX, PY = 5.6, 3.4
for k in range(6):
    box(f"PenRailF{k}", (PX + k * 0.55 - 1.4, PY - 1.2, 0.5), (0.06, 0.06, 1.0), "wood")
box("PenTop", (PX, PY - 1.2, 0.95), (3.2, 0.07, 0.07), "wood")
box("PenMid", (PX, PY - 1.2, 0.5), (3.2, 0.07, 0.07), "wood")
box("PenSideL", (PX - 1.6, PY, 0.95), (0.07, 2.4, 0.07), "wood")
box("PenSideR", (PX + 1.6, PY, 0.95), (0.07, 2.4, 0.07), "wood")
box("PenStraw", (PX, PY, 0.03), (3.1, 2.3, 0.04), "shirt2")

def pig(x, y, yaw):
    r = math.radians(yaw)
    def L(dx, dy, dz):
        return (x + dx * math.cos(r) - dy * math.sin(r), y + dx * math.sin(r) + dy * math.cos(r), dz)
    rot = (0, 0, r)
    box("PigBody", L(0, 0, 0.42), (0.85, 0.48, 0.42), "pig", rot)
    box("PigHead", L(0.5, 0, 0.52), (0.3, 0.36, 0.32), "pig", rot)
    box("PigSnout", L(0.68, 0, 0.47), (0.08, 0.18, 0.12), "pigdark", rot)
    for ey in (-0.12, 0.12):
        box("PigEar", L(0.48, ey, 0.72), (0.08, 0.1, 0.1), "pigdark", rot)
    for lx in (-0.3, 0.3):
        for ly in (-0.16, 0.16):
            box("PigLeg", L(lx, ly, 0.12), (0.1, 0.1, 0.24), "pigdark", rot)
pig(PX - 0.6, PY - 0.2, 200)
pig(PX + 0.7, PY + 0.4, 160)
pig(PX + 0.1, PY + 0.7, 15)

# visitors (backs to camera)
def person(x, y, shirt, h=1.75, yaw=0):
    r = math.radians(yaw)
    box("Legs", (x, y, h * 0.24), (0.32, 0.2, h * 0.48), "jeans", (0, 0, r))
    box("Torso", (x, y, h * 0.62), (0.44, 0.24, h * 0.32), shirt, (0, 0, r))
    box("Head", (x, y, h * 0.86), (0.2, 0.22, 0.24), "skin", (0, 0, r))
    box("Hair", (x, y + 0.03, h * 0.93), (0.22, 0.22, 0.1), "hair", (0, 0, r))
person(-0.6, 0.6, "shirt1", 1.78, 8)
person(0.3, 0.9, "shirt3", 1.66, -6)
person(-1.5, 0.3, "red", 1.72, 20)
person(8.2, 1.2, "shirt2", 1.62, -15)

# light, world, camera
bpy.ops.object.light_add(type="SUN", location=(0, 0, 20), rotation=(math.radians(50), math.radians(10), math.radians(-35)))
sun = bpy.context.active_object
sun.data.energy = 4.2
sun.data.angle = math.radians(2)
world = bpy.data.worlds.new("W")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.55, 0.66, 0.78, 1)
bg.inputs["Strength"].default_value = 0.9

bpy.ops.object.camera_add(location=(2.7, -6.4, 1.7), rotation=(math.radians(92), 0, math.radians(3)))
cam = bpy.context.active_object
cam.data.lens = 26
scene.camera = cam

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = int(os.environ.get("HG_SAMPLES", "16"))
scene.cycles.use_denoising = True
W, H = [int(v) for v in os.environ.get("HG_RES", "800x450").split("x")]
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "Standard"
img = scene.render.image_settings
if hasattr(img, "media_type"):
    img.media_type = "IMAGE"
img.file_format = "PNG"
scene.render.filepath = os.environ["HG_OUT"]
bpy.ops.render.render(write_still=True)
print("DONE stall", W, H, flush=True)
