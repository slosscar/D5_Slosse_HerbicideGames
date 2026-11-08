# Herbicide Games · The Arena Bus · capture-video scene for Blender (4.x and 5.x)
#
# HOW TO USE
#   1. Open Blender, File > New > General.
#   2. Go to the "Scripting" tab, click "Open", choose this file, click "Run Script" (the play button).
#   3. The scene is built: a street in Rome, the Arena Bus with two gladiators fighting on the roof,
#      live screens on both sides, horn speakers, a crowd, and five camera shots (40 seconds).
#   4. Press Space in the 3D viewport (or the play button on the timeline) to preview.
#   5. Render > Render Animation (Ctrl+F12). The MP4 is saved in Videos/HerbicideGames.
#
# Everything is normal Blender objects: you can move, recolour and remodel anything afterwards.
# Change the settings below if you want a shorter test render first.

import bpy, math, os, random
from mathutils import Matrix

# ---------------------------------------------------------------- settings
FPS = 24
SECONDS = 40                    # total length of the capture video
RES = (1920, 1080)
RENDER_SAMPLES = 32             # lower = faster render
OUTPUT = os.path.join(os.path.expanduser("~"), "Videos", "HerbicideGames", "arena_bus_capture_")
SCREEN_LINES = ("LIVE FROM THE ARENA", "HERBICIDE GAMES", "21-23 APRIL  ROME")
BAND_TEXT = "THE KILLING WE PAY FOR, MADE VISIBLE"

# Herbicide Games colours
RED, GREY, MARBLE = "911C23", "3C3C3C", "EBEAE6"

LAST = FPS * SECONDS
SHOTS = [  # (name, first frame) - each shot runs until the next one starts
    ("1_street", 1),        # 0-8 s   you hear it before you see it
    ("2_look_up", 8 * FPS + 1),   # 8-18 s  two gladiators fight on the roof
    ("3_screens", 18 * FPS + 1),  # 18-28 s the screens: date and place
    ("4_speaker", 28 * FPS + 1),  # 28-36 s the speaker gives the info
    ("5_drive_away", 36 * FPS + 1),  # 36-40 s the bus drives on
]

random.seed(7)

# ---------------------------------------------------------------- helpers
def hex_rgba(h, a=1.0):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


def set_input(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return


MATS = {}
def mat(name, color, rough=0.6, metal=0.0, emit=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    m.diffuse_color = hex_rgba(color)
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        set_input(bsdf, ["Base Color"], hex_rgba(color))
        set_input(bsdf, ["Roughness"], rough)
        set_input(bsdf, ["Metallic"], metal)
        if emit:
            set_input(bsdf, ["Emission Color", "Emission"], hex_rgba(color))
            set_input(bsdf, ["Emission Strength"], emit)
    MATS[name] = m
    return m


def finish(obj, material, parent, bevel=0.0):
    if material:
        obj.data.materials.clear()
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    if bevel:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    return obj


def box(name, x0, x1, y0, y1, z0, z1, material, parent=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    o.data.transform(Matrix.Diagonal((abs(x1 - x0), abs(y1 - y0), abs(z1 - z0), 1)))
    return finish(o, material, parent, bevel)


def cyl(name, r, depth, loc, rot, material, parent=None, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return finish(o, material, parent)


def cone(name, r1, r2, depth, loc, rot, material, parent=None):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, vertices=24, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    return finish(o, material, parent)


def sphere(name, r, loc, material, parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=24, ring_count=12, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.data.transform(Matrix.Diagonal((*scale, 1)))
    bpy.ops.object.shade_smooth()
    return finish(o, material, parent)


def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.empty_display_size = 0.3
    if parent:
        o.parent = parent
    return o


def text(name, body, size, loc, rot, material, parent=None, align="CENTER", extrude=0.01):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.extrude = extrude
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    o.data.materials.append(material)
    if parent:
        o.parent = parent
    return o


# ---------------------------------------------------------------- clean start
scene = bpy.context.scene
if bpy.context.object and bpy.context.object.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
for o in list(scene.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, LAST
scene.frame_set(1)
try:
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
except Exception:
    pass

# materials
M = {
    "body": mat("HG body grey", GREY, 0.45, 0.2),
    "red": mat("HG red", RED, 0.5),
    "marble": mat("HG marble", MARBLE, 0.5),
    "black": mat("HG black", "111111", 0.4),
    "glass": mat("HG glass", "1B2630", 0.08, 0.4),
    "tyre": mat("HG tyre", "141414", 0.9),
    "rim": mat("HG rim", "B9B9B9", 0.3, 0.9),
    "sand": mat("HG arena sand", "C8AB7C", 0.95),
    "screen": mat("HG screen", "2A0507", 0.4, 0.0, 1.0),
    "screen_text": mat("HG screen text", "FFF4E6", 0.4, 0.0, 6.0),
    "screen_gold": mat("HG screen gold", "E8B74A", 0.4, 0.0, 5.0),
    "live_dot": mat("HG live dot", "FF2A2A", 0.4, 0.0, 8.0),
    "light": mat("HG headlight", "FFF6DD", 0.2, 0.0, 10.0),
    "skin": mat("HG skin", "B47F5A", 0.6),
    "bronze": mat("HG bronze", "9A7434", 0.3, 0.9),
    "steel": mat("HG steel", "CFCFCF", 0.25, 1.0),
    "cloth_red": mat("HG cloth red", RED, 0.8),
    "cloth_grey": mat("HG cloth grey", "6E6A64", 0.8),
    "leather": mat("HG leather", "5A3A22", 0.7),
    "asphalt": mat("HG asphalt", "3B3B3D", 0.9),
    "paint": mat("HG road paint", "E8E6DF", 0.7),
    "pavement": mat("HG pavement", "BDB6A8", 0.85),
}

# ---------------------------------------------------------------- the bus
bus = empty("ArenaBus")

# chassis, cargo box, cab
box("Chassis", -4.6, 4.7, -1.2, 1.2, 0.55, 0.9, M["black"], bus)
box("Body", -4.6, 2.4, -1.3, 1.3, 0.9, 3.6, M["body"], bus, bevel=0.06)
box("Cab", 2.5, 4.8, -1.25, 1.25, 0.9, 3.0, M["body"], bus, bevel=0.12)
box("Windshield", 4.79, 4.84, -1.05, 1.05, 2.0, 2.8, M["glass"], bus)
for s in (-1, 1):
    box("CabWindow", 3.0, 4.4, s * 1.24, s * 1.27, 2.0, 2.75, M["glass"], bus)
    cyl("Headlight", 0.14, 0.05, (4.82, s * 0.85, 1.2), (0, math.radians(90), 0), M["light"], bus)
box("Bumper", 4.7, 4.95, -1.25, 1.25, 0.6, 0.95, M["black"], bus)

# wheels
wheels = []
for wx in (-3.3, -1.9, 3.6):
    for s in (-1, 1):
        w = cyl("Wheel", 0.52, 0.32, (wx, s * 1.08, 0.52), (math.radians(90), 0, 0), M["tyre"], bus, verts=32)
        cyl("Rim", 0.3, 0.34, (0, 0, 0), (0, 0, 0), M["rim"], w, verts=16)
        wheels.append(w)

# live screens on both sides
for s in (-1, 1):
    face_rot = (math.radians(90), 0, 0) if s < 0 else (math.radians(90), 0, math.radians(180))
    y = s * 1.315
    box("ScreenFrame", -4.2, 2.0, y - 0.01 * s, y + 0.02 * s, 1.15, 3.35, M["black"], bus)
    box("Screen", -4.05, 1.85, y + 0.02 * s, y + 0.035 * s, 1.25, 3.25, M["screen"], bus)
    ty = y + 0.05 * s
    text("ScreenLive", SCREEN_LINES[0], 0.26, (-1.1 + 0.25 * -s, ty, 2.85), face_rot, M["screen_gold"], bus)
    sphere("LiveDot", 0.09, (-2.8 if s < 0 else 0.6, ty, 2.85), M["live_dot"], bus)
    text("ScreenName", SCREEN_LINES[1], 0.5, (-1.1, ty, 2.2), face_rot, M["screen_text"], bus)
    text("ScreenDate", SCREEN_LINES[2], 0.3, (-1.1, ty, 1.6), face_rot, M["screen_gold"], bus)
    text("BandText", BAND_TEXT, 0.17, (-1.1, s * 1.31, 3.47), face_rot, M["marble"], bus)
    text("CabName", "HERBICIDE GAMES", 0.16, (3.65, s * 1.26, 1.6), face_rot, M["red"], bus)

# the arena on the roof
box("ArenaFloor", -4.45, 2.25, -1.25, 1.25, 3.6, 3.72, M["sand"], bus)
post_xs = [-4.4 + i * 0.67 for i in range(11)]
for s in (-1, 1):
    for px in post_xs:
        cyl("RailPost", 0.035, 0.55, (px, s * 1.2, 3.99), (0, 0, 0), M["red"], bus, verts=8)
    cyl("RailTop", 0.03, 6.7, (-1.1, s * 1.2, 4.25), (0, math.radians(90), 0), M["red"], bus, verts=8)
for ex in (-4.4, 2.2):
    cyl("RailEnd", 0.03, 2.4, (ex, 0, 4.25), (math.radians(90), 0, 0), M["red"], bus, verts=8)

# horn speakers on poles at the front of the roof (classic loudspeaker-van horns)
speaker_target = empty("SpeakerTarget", (1.9, -0.9, 4.6), bus)
box("Amplifier", 1.55, 2.15, -0.35, 0.35, 3.72, 4.05, M["black"], bus, bevel=0.03)
for s in (-1, 1):
    px, py = 1.9, s * 0.9
    cyl("SpeakerPole", 0.04, 1.0, (px, py, 4.22), (0, 0, 0), M["black"], bus, verts=8)
    for k, yaw in enumerate((s * 40, s * 140)):  # one horn aims forward, one backward, both outward
        d = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
        z = 4.55 + 0.22 * k
        cone("Horn", 0.2, 0.05, 0.5, (px + 0.3 * d[0], py + 0.3 * d[1], z), (0, math.radians(-90), math.radians(yaw)), M["black"], bus)
        cyl("HornDriver", 0.07, 0.14, (px + 0.02 * d[0], py + 0.02 * d[1], z), (0, math.radians(90), math.radians(yaw)), M["black"], bus, verts=12)

# two gladiators
def gladiator(name, x, facing, tunic, shield_shape, phase):
    root = empty(name, (x, 0, 3.72), bus)
    root.rotation_euler = (0, 0, math.radians(facing))
    for s in (-1, 1):
        cyl("Leg", 0.08, 0.8, (0.05 * s, s * 0.12, 0.4), (0, 0, 0), M["skin"], root, verts=12)
        box("Greave", -0.06 + 0.05 * s, 0.1 + 0.05 * s, s * 0.12 - 0.07, s * 0.12 + 0.07, 0.05, 0.45, M["bronze"], root)
    box("Belt", -0.16, 0.16, -0.23, 0.23, 0.78, 1.0, M["leather"], root)
    box("Tunic", -0.17, 0.17, -0.24, 0.24, 0.62, 0.82, tunic, root)
    box("Torso", -0.14, 0.14, -0.21, 0.21, 0.98, 1.5, M["skin"], root, bevel=0.05)
    sphere("Head", 0.13, (0, 0, 1.68), M["skin"], root)
    sphere("Helmet", 0.16, (0, 0, 1.72), M["bronze"], root, scale=(1.05, 1, 1.15))
    box("Visor", 0.12, 0.17, -0.1, 0.1, 1.62, 1.76, M["black"], root)
    box("Crest", -0.18, 0.12, -0.03, 0.03, 1.86, 2.0, M["cloth_red"], root)
    # sword arm (right) on a shoulder pivot
    sh = empty(name + "_SwordShoulder", (0, -0.27, 1.42), root)
    cyl("Arm", 0.06, 0.6, (0, 0, -0.3), (0, 0, 0), M["skin"], sh, verts=12)
    box("Hilt", -0.03, 0.03, -0.03, 0.03, -0.7, -0.6, M["leather"], sh)
    box("Guard", -0.09, 0.09, -0.03, 0.03, -0.73, -0.7, M["bronze"], sh)
    box("Blade", -0.035, 0.035, -0.012, 0.012, -1.3, -0.73, M["steel"], sh)
    # shield arm (left)
    sl = empty(name + "_ShieldShoulder", (0, 0.27, 1.42), root)
    cyl("Arm", 0.06, 0.6, (0, 0, -0.3), (0, 0, 0), M["skin"], sl, verts=12)
    if shield_shape == "scutum":
        box("Shield", -0.05, 0.05, -0.32, 0.32, -0.95, 0.0, M["cloth_red"], sl, bevel=0.02)
        box("ShieldBoss", -0.08, -0.04, -0.07, 0.07, -0.55, -0.41, M["bronze"], sl)
    else:
        cyl("Shield", 0.33, 0.06, (0, 0, -0.5), (0, math.radians(90), 0), M["bronze"], sl, verts=32)
    # fight: sword swings, shield follows, small steps
    beat = 14
    for f in range(1, LAST + 1, beat // 2):
        k = (f // (beat // 2) + phase) % 4
        swing = {0: -165, 1: -120, 2: -55, 3: -100}[k]
        sh.rotation_euler = (math.radians(-10), math.radians(swing), 0)
        sh.keyframe_insert("rotation_euler", frame=f)
        sl.rotation_euler = (0, math.radians(-70 + (15 if k in (1, 2) else 0)), math.radians(-20))
        sl.keyframe_insert("rotation_euler", frame=f)
        step = 0.12 * math.sin((f / beat + phase) * math.pi)
        root.location = (x + step * (1 if facing == 0 else -1), 0, 3.72)
        root.keyframe_insert("location", frame=f)
    return root

gladiator("Gladiator_Murmillo", -2.0, 0, M["cloth_red"], "scutum", 0)
gladiator("Gladiator_Thraex", -0.2, 180, M["cloth_grey"], "parma", 2)
roof_target = empty("RoofTarget", (-1.1, 0, 4.9), bus)
screen_target = empty("ScreenTarget", (-1.1, -1.3, 2.2), bus)

# bus drives through the street; wheels turn
X0, X1 = -30.0, 30.0
bus.location = (X0, 0, 0)
bus.keyframe_insert("location", frame=1)
bus.location = (X1, 0, 0)
bus.keyframe_insert("location", frame=LAST)
for w in wheels:
    w.keyframe_insert("rotation_euler", frame=1)
    w.rotation_euler[1] += (X1 - X0) / 0.52
    w.keyframe_insert("rotation_euler", frame=LAST)

# ---------------------------------------------------------------- the street
box("Road", -90, 90, -5, 5, -0.05, 0, M["asphalt"], None)
for i in range(-22, 23):
    box("LaneDash", i * 4, i * 4 + 2, -0.08, 0.08, 0, 0.005, M["paint"], None)
for s in (-1, 1):
    box("Sidewalk", -90, 90, s * 5, s * 11, -0.05, 0.15, M["pavement"], None)
    x = -80.0
    tones = ["C9A26B", "B5653F", "E6DCC5", "D49A5C", "BFA88A", "E0C9A6"]
    while x < 80:
        w = random.uniform(7, 13)
        h = random.uniform(9, 19)
        tone = mat("Facade " + random.choice(tones), random.choice(tones), 0.85)
        yb = s * 11
        box("Building", x, x + w - 0.3, yb, yb + s * 10, 0, h, tone, None)
        win = box("Window", x + 1.0, x + 1.8, yb - s * 0.05, yb + s * 0.02, 3.0, 4.6, M["glass"], None)
        arr = win.modifiers.new("Columns", "ARRAY")
        arr.count = max(1, int((w - 2) / 2.2))
        arr.relative_offset_displace = (2.75, 0, 0)
        arr2 = win.modifiers.new("Floors", "ARRAY")
        arr2.count = max(1, int((h - 4) / 3.2))
        arr2.relative_offset_displace = (0, 0, 2.0)
        x += w

# crowd on both sidewalks
coats = ["911C23", "3C3C3C", "2F4A6A", "6E6A64", "C9A26B", "EBEAE6", "4F6B4A"]
cam_free = [(2.0, -1), (8.0, -1)]
for s in (-1, 1):
    for i in range(70):
        px = random.uniform(-45, 45)
        if any(abs(px - cx) < 4.5 and s == cs for cx, cs in cam_free):
            continue
        py = s * random.uniform(7.3, 10.3)
        h = random.uniform(1.55, 1.9)
        coat = mat("Coat " + random.choice(coats), random.choice(coats), 0.8)
        cyl("Person", 0.21, h - 0.25, (px, py, 0.15 + (h - 0.25) / 2), (0, 0, 0), coat, None, verts=10)
        sphere("PersonHead", 0.12, (px, py, 0.15 + h - 0.1), M["skin"], None)
        if random.random() < 0.35:  # a phone held up to film
            box("Phone", px - 0.04, px + 0.04, py - s * 0.35, py - s * 0.33, 0.15 + h + 0.05, 0.15 + h + 0.2, M["black"], None)

# ---------------------------------------------------------------- light and sky
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
if bg:
    bg.inputs[0].default_value = hex_rgba("A9C3DA")
    bg.inputs[1].default_value = 1.0
sun_data = bpy.data.lights.new("Sun", "SUN")
sun_data.energy = 4.0
sun_data.angle = math.radians(3)
sun = bpy.data.objects.new("Sun", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))

# ---------------------------------------------------------------- cameras, one per shot
def camera(name, loc, target, parent=None, lens=32):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_end = 400
    c = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(c)
    c.location = loc
    if parent:
        c.parent = parent
    con = c.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    return c

bus_target = empty("BusTarget", (0, 0, 2.6), bus)
cams = [
    camera("Cam_1_street", (2.0, -7.0, 1.7), bus_target, lens=45),
    camera("Cam_2_look_up", (0.8, -5.2, 2.0), roof_target, bus, lens=26),
    camera("Cam_3_screens", (-1.1, -6.8, 2.4), screen_target, bus, lens=24),
    camera("Cam_4_speaker", (6.0, -4.0, 4.3), speaker_target, bus, lens=35),
    camera("Cam_5_drive_away", (8.0, -6.6, 2.0), bus_target, lens=35),
]
scene.timeline_markers.clear()
for (name, start), cam in zip(SHOTS, cams):
    mk = scene.timeline_markers.new(name, frame=start)
    mk.camera = cam
scene.camera = cams[0]

# ---------------------------------------------------------------- render settings
engines = [e.identifier for e in scene.render.bl_rna.properties["engine"].enum_items]
for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
    if e in engines:
        scene.render.engine = e
        break
try:
    scene.eevee.taa_render_samples = RENDER_SAMPLES
except Exception:
    pass
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
scene.render.filepath = OUTPUT
img = scene.render.image_settings
try:
    if hasattr(img, "media_type"):
        img.media_type = "VIDEO"
    img.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
except Exception as e:
    print("Video output not available, rendering PNG frames instead:", e)
    img.file_format = "PNG"

print("Herbicide Games · Arena Bus scene ready:", LAST, "frames,", len(cams), "shots. Output:", OUTPUT)
