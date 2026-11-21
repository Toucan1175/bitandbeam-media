"""EP11 (Knight Capital, 2012) 3D shots: one connected world (Standard v2).
Exec AFTER bb_kit in the same namespace (K). Original models: an open-plan trading floor (desks, screens,
ceiling panels, window wall), a glass server room with SMARS's eight racks, a wall switch (the reused flag),
order "tickets" streaming out of rack 8, a pile of unwanted stock, an inbox monitor, and a kill switch.
Assets (CC0): Quaternius "Animated Human" via Poly Pizza (characters), Poly Haven HDRI
"homecoming_center_rooftop" (sky seen through the windows), Poly Haven texture "grey_cartago_02" (floor).
Units: metres. Trading floor x -20..6, server room x 6..18, windows at y = +12.
Illustration only: generic company, no logos; rack count (8) and the 7-of-8 deployment are from the SEC order.
"""
import bpy, math, random
from mathutils import Vector, Euler

R = math.radians
LIB = "assets_lib"
RACK_Y = [-7 + 2 * i for i in range(8)]
RACK_X = 12.0


def _mats():
    return dict(
        wall=mat("e11_wall", (0.16, 0.17, 0.19), 0.0, 0.85, wear=0.08, wear_scale=3),
        ceil=mat("e11_ceil", (0.2, 0.2, 0.21), 0.0, 0.9),
        panel=glow("e11_panel", (1.0, 0.96, 0.9), 6.0),
        frame=mat("e11_frame", (0.08, 0.085, 0.09), 0.8, 0.35),
        glass=mat("e11_glass", (0.6, 0.75, 0.85), 0.0, 0.03, alpha=0.12),
        desk=mat("e11_desk", (0.32, 0.25, 0.18), 0.0, 0.45, wear=0.15, wear_scale=20),
        leg=mat("e11_leg", (0.1, 0.1, 0.11), 0.9, 0.3),
        bezel=mat("e11_bezel", (0.02, 0.02, 0.025), 0.3, 0.35),
        screen=mat("e11_screen", (0.01, 0.02, 0.05), 0.0, 0.2, emit=(0.06, 0.12, 0.3), strength=2.5),
        green=glow("e11_green", (0.1, 1.0, 0.35), 5.0),
        red=glow("e11_red", (1.0, 0.08, 0.05), 6.0),
        amber=glow("e11_amber", (1.0, 0.55, 0.05), 6.0),
        white=glow("e11_white", (1.0, 1.0, 1.0), 4.0),
        chair=mat("e11_chair", (0.05, 0.05, 0.06), 0.1, 0.6),
        rack=mat("e11_rack", (0.04, 0.045, 0.05), 0.7, 0.4, wear=0.1),
        unit=mat("e11_unit", (0.12, 0.13, 0.14), 0.8, 0.35, wear=0.15, wear_scale=90),
        card=mat("e11_card", (0.95, 0.92, 0.85), 0.0, 0.5, emit=(1.0, 0.75, 0.3), strength=1.5),
        box=mat("e11_box", (0.55, 0.4, 0.24), 0.0, 0.8, wear=0.25, wear_scale=30),
        tape=mat("e11_tape", (0.75, 0.6, 0.35), 0.0, 0.4),
        plate=mat("e11_plate", (0.85, 0.85, 0.82), 0.0, 0.35),
        btn=mat("e11_btn", (0.8, 0.02, 0.02), 0.0, 0.25, emit=(1, 0.05, 0.02), strength=0.5, coat=0.6),
        stripe=mat("e11_stripe", (0.9, 0.7, 0.0), 0.0, 0.5),
        ped=mat("e11_ped", (0.15, 0.15, 0.16), 0.6, 0.4, wear=0.1),
        cover=mat("e11_cover", (0.8, 0.9, 1.0), 0.0, 0.05, alpha=0.25),
    )


def _txt(name, body, loc, size, m, rot=(R(90), 0, 0), align='CENTER'):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'
    cu.extrude = size * 0.04
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot; o.data.materials.append(m)
    return o


def _keycol(m, frames_cols):
    """Keyframe a material's emission colour: [(frame, (r,g,b)), ...]."""
    p = m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"]
    for f, c in frames_cols:
        p.default_value = (*c, 1); p.keyframe_insert("default_value", frame=f)


def _world(sc):
    sc.world = bpy.data.worlds.get("PolyHaven homecoming_center_rooftop") or sc.world
    if sc.world and sc.world.use_nodes:
        bg = sc.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs[1].default_value = 1.2
    for s in (sc,):
        try:
            s.blendermcp_use_polyhaven = True; s.blendermcp_use_polypizza = True
        except Exception:
            pass


# ------------------------------------------------------------------ the world
def office(M, desks=True, racks=True, people=True):
    floor_m = bpy.data.materials.get("grey_cartago_02")
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-1, 0, 0)); fl = bpy.context.object; fl.name = "floor"
    fl.scale = (38, 24, 1); bpy.ops.object.transform_apply(scale=True)
    if floor_m:
        fl.data.materials.append(floor_m)
        mp = [n for n in floor_m.node_tree.nodes if n.type == 'MAPPING']
        if mp:
            mp[0].inputs["Scale"].default_value = (38 / 1.7, 24 / 1.7, 1)
    box("ceiling", (-1, 0, 3.7), (38, 24, 0.1), M["ceil"], bevel=0)
    for x in range(-18, 18, 3):
        for y in (-9, -5, -1, 3, 7):
            box(f"lp_{x}_{y}", (x, y, 3.64), (1.8, 0.6, 0.03), M["panel"], bevel=0)
    # walls: back (x=-20), right (y=-12), server-room end (x=18); window wall at y=+12
    box("wall_w", (-20, 0, 1.85), (0.2, 24, 3.7), M["wall"], bevel=0)
    box("wall_s", (-1, -12, 1.85), (38, 0.2, 3.7), M["wall"], bevel=0)
    box("wall_e", (18, 0, 1.85), (0.2, 24, 3.7), M["wall"], bevel=0)
    box("sill", (-1, 12, 0.35), (38, 0.3, 0.7), M["wall"], bevel=0)
    box("head", (-1, 12, 3.45), (38, 0.3, 0.5), M["wall"], bevel=0)
    for x in range(-20, 19, 3):
        box(f"mul_{x}", (x, 12, 1.95), (0.12, 0.2, 2.6), M["frame"], bevel=0.01)
    box("win_glass", (-1, 12.05, 1.95), (38, 0.02, 2.6), M["glass"], bevel=0)
    # glass partition to the server room (x = 6) with a door gap at y -1..1
    for y0, y1 in ((-12, -1.2), (1.2, 12)):
        box(f"part_{y0}", (6, (y0 + y1) / 2, 1.85), (0.03, y1 - y0, 3.7), M["glass"], bevel=0)
        for y in range(int(y0), int(y1) + 1, 2):
            box(f"pmul_{y}", (6, y, 1.85), (0.08, 0.08, 3.7), M["frame"], bevel=0)
    # ticker board on the back wall
    box("ticker", (-19.85, 0, 2.7), (0.1, 12, 0.9), M["bezel"], bevel=0.01)
    _txt("ticker_t", "NYSE  OPEN 9:30   ▲ 12.41  ▼ 3.07  ▲ 44.90  ▼ 18.22  ▲ 7.15", (-19.78, 0, 2.7), 0.42, M["amber"],
         rot=(R(90), 0, R(-90)))
    # sun through the windows + soft interior fill
    bpy.ops.object.light_add(type='SUN', rotation=(R(55), 0, R(200))); s = bpy.context.object; s.data.energy = 3.5
    s.data.angle = R(2)
    for x in (-14, -6, 2, 12):
        area((x, 0, 3.4), (x, 0, 0), 900, 6, (1.0, 0.95, 0.9), f"fill_{x}")
    if desks:
        trading_floor(M)
    if racks:
        server_room(M)
    if people:
        crowd()


def desk(M, x, y, rotz=0, n_mon=2, red=False):
    g = pivot(f"desk_{x}_{y}", (x, y, 0), rot=(0, 0, rotz))
    box(f"dt_{x}_{y}", (0, 0, 0.74), (1.6, 0.8, 0.04), M["desk"], parent=g)
    for dx in (-0.75, 0.75):
        box(f"dl_{x}_{y}_{dx}", (dx, 0, 0.36), (0.05, 0.7, 0.72), M["leg"], parent=g)
    for i in range(n_mon):
        mx = (i - (n_mon - 1) / 2) * 0.62
        box(f"mb_{x}_{y}_{i}", (mx, 0.22, 1.08), (0.6, 0.04, 0.38), M["bezel"], parent=g, bevel=0.008)
        box(f"ms_{x}_{y}_{i}", (mx, 0.198, 1.09), (0.55, 0.005, 0.32), M["screen"], parent=g, bevel=0)
        for k in range(5):
            h = random.uniform(0.03, 0.2)
            col = M["red"] if (red or random.random() < 0.35) else M["green"]
            box(f"bar_{x}_{y}_{i}_{k}", (mx - 0.2 + k * 0.1, 0.195, 0.95 + h / 2), (0.05, 0.004, h), col, parent=g, bevel=0)
        box(f"mst_{x}_{y}_{i}", (mx, 0.24, 0.84), (0.06, 0.06, 0.2), M["leg"], parent=g, bevel=0)
    # chair
    box(f"cs_{x}_{y}", (0, -0.6, 0.48), (0.5, 0.5, 0.08), M["chair"], parent=g)
    box(f"cb_{x}_{y}", (0, -0.85, 0.85), (0.5, 0.06, 0.65), M["chair"], parent=g)
    cyl(f"cp_{x}_{y}", (0, -0.6, 0.24), 0.04, 0.48, M["leg"], parent=g)
    return g


def trading_floor(M):
    random.seed(11)
    for row, y in enumerate((-8, -4, 0, 4, 8)):
        for x in (-17, -15.2, -13.4, -9, -7.2, -5.4, -1, 0.8, 2.6):
            desk(M, x, y, R(180) if row % 2 else 0, n_mon=3 if random.random() < 0.5 else 2)


def rack(M, i, y):
    g = pivot(f"rack_{i}", (RACK_X, y, 0))
    box(f"rk_{i}", (0, 0, 1.0), (1.0, 0.62, 2.0), M["rack"], parent=g, bevel=0.015)
    for k in range(14):
        box(f"ru_{i}_{k}", (-0.505, 0, 0.18 + k * 0.125), (0.02, 0.54, 0.1), M["unit"], parent=g, bevel=0.004)
    led = glow(f"e11_led_{i}", (1.0, 0.55, 0.05), 7.0)
    for k in range(14):
        box(f"rl_{i}_{k}", (-0.518, 0.22, 0.18 + k * 0.125), (0.006, 0.05, 0.03), led, parent=g, bevel=0)
    box(f"rstrip_{i}", (-0.52, -0.29, 1.0), (0.008, 0.025, 1.8), led, parent=g, bevel=0)
    _txt(f"rnum_{i}", str(i + 1), (RACK_X - 0.55, y, 2.25), 0.32, M["white"], rot=(R(90), 0, R(-90)))
    return g, led


def server_room(M):
    box("sr_floor", (12, 0, 0.005), (11.8, 23.8, 0.01), mat("e11_raised", (0.2, 0.21, 0.22), 0.3, 0.5, wear=0.1, wear_scale=2),
        bevel=0)
    leds = []
    for i, y in enumerate(RACK_Y):
        _, led = rack(M, i, y)
        leds.append(led)
    bpy.context.scene["e11_leds"] = [m.name for m in leds]
    box("cable_tray", (RACK_X, 0, 2.55), (0.4, 16.5, 0.08), M["frame"], bevel=0.01)
    return leds


# ------------------------------------------------------------------ people (Quaternius CC0)
def person(name, loc, rotz=0.0, action="Working", f0=1, speed=1.0, scale=1.0):
    lib = bpy.data.scenes[LIB]
    arm0 = lib.objects["Human Armature"]; mesh0 = lib.objects["Human_Mesh"]
    root0 = arm0.parent
    arm = arm0.copy(); arm.data = arm0.data; arm.name = name
    mesh = mesh0.copy(); mesh.name = name + "_mesh"
    sc = bpy.context.scene
    sc.collection.objects.link(arm); sc.collection.objects.link(mesh)
    mesh.parent = arm
    for md in mesh.modifiers:
        if md.type == 'ARMATURE':
            md.object = arm
    if root0 is not None:
        arm.parent = None
        arm.matrix_world = root0.matrix_world @ arm0.matrix_basis
    arm.location = loc; arm.rotation_euler = (arm.rotation_euler[0], arm.rotation_euler[1], rotz)
    arm.scale = [s * scale for s in arm.scale]
    ad = arm.animation_data or arm.animation_data_create()
    act = bpy.data.actions.get(f"Human Armature|{action}")
    ad.action = None
    tr = ad.nla_tracks.new(); tr.name = action
    st = tr.strips.new(action, int(f0), act)
    try:
        if act.slots:
            st.action_slot = act.slots[0]
    except Exception:
        pass
    st.scale = 1.0 / speed
    n = act.frame_range[1] - act.frame_range[0]
    st.repeat = max(1.0, (sc.frame_end + 40) / max(1.0, n / speed))
    return arm


def crowd():
    random.seed(7)
    spots = [(-15.2, -8.75, 0), (-9, -8.75, 0), (-5.4, -4.75 + 1.5, R(180)), (-13.4, 0 - 0.75, 0), (-7.2, 0 - 0.75, 0),
             (0.8, -0.75, 0), (-1, 4 + 0.75, R(180)), (-15.2, 4 + 0.75, R(180)), (-9, 8 - 0.75, 0), (2.6, 8 - 0.75, 0)]
    for k, (x, y, rz) in enumerate(spots):
        person(f"trader_{k}", (x, y, 0), rz, random.choice(["Working", "Working", "Idle"]), f0=-random.randint(0, 120),
               scale=random.uniform(0.95, 1.05))


# ------------------------------------------------------------------ shots
def _shot(name, seconds, v, **kw):
    sc = stage(name + ("_v" if v else ""), seconds=seconds, res=(1080, 1920) if v else (1920, 1080), samples=16)
    _world(sc)
    return sc


def shot_floor(v=False):
    sc = _shot("ep11_floor", 8, v)
    M = _mats(); office(M)
    if v:
        camera("dolly", target=(-8, 2, 1.3), start=(-16, -11, 1.8), end=(-10, -5, 1.6), lens=22, fstop=5.6)
    else:
        camera("dolly", target=(-6, 3, 1.2), start=(-18, -10.5, 2.1), end=(-6, -6.5, 1.7), lens=26, fstop=5.6)
    return sc


def shot_switch(v=False):
    sc = _shot("ep11_switch", 7, v)
    M = _mats(); office(M, people=False)
    # pillar by the server-room door with a big wall switch labelled as the flag
    box("pillar", (5.4, -2.2, 1.85), (0.5, 0.5, 3.7), M["wall"], bevel=0.01)
    g = pivot("switch", (5.13, -2.2, 1.35))
    box("plate", (0, 0, 0), (0.02, 0.09, 0.13), M["plate"], parent=g, bevel=0.006)
    tog = pivot("toggle", (-0.012, 0, 0), parent=g)
    box("rocker", (-0.012, 0, 0), (0.02, 0.035, 0.07), M["plate"], parent=tog, bevel=0.005)
    tog.rotation_euler = (0, R(-14), 0)
    animate(tog, "rotation_euler", [(60, Euler((0, R(-14), 0))), (68, Euler((0, R(14), 0)))])
    lamp = glow("e11_switchlamp", (0.1, 1.0, 0.35), 0.0)
    box("lamp", (-0.006, 0, 0.055), (0.004, 0.02, 0.008), lamp, parent=g, bevel=0)
    p = lamp.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    p.default_value = 0.0; p.keyframe_insert("default_value", frame=67); p.default_value = 25.0; p.keyframe_insert("default_value", frame=69)
    _txt("lbl_flag", "FLAG", (5.12, -2.2, 1.5), 0.045, M["white"], rot=(R(90), 0, R(-90)))
    _txt("lbl_pp", "POWER PEG  (unused since 2003)", (5.12, -2.2, 1.255), 0.016, M["amber"], rot=(R(90), 0, R(-90)))
    if v:
        camera("dolly", target=(5.13, -2.2, 1.36), start=(4.2, -2.75, 1.42), end=(4.62, -2.4, 1.38), lens=50, fstop=2.0)
    else:
        camera("dolly", target=(5.13, -2.2, 1.36), start=(4.0, -2.9, 1.45), end=(4.55, -2.42, 1.38), lens=50, fstop=2.0)
    return sc


def shot_racks(v=False):
    """Deployment: a technician walks the row; racks 1-7 turn green as he passes, rack 8 stays amber (old code)."""
    sc = _shot("ep11_racks", 10, v)
    M = _mats(); office(M, desks=v is False, people=False)
    leds = [bpy.data.materials[n] for n in sc["e11_leds"]]
    amber, green = (1.0, 0.55, 0.05), (0.1, 1.0, 0.35)
    fps = sc.render.fps
    for i, m in enumerate(leds):
        f = int(25 + i * 0.95 * fps)
        if i < 7:
            _keycol(m, [(f - 2, amber), (f + 4, green)])
        else:
            _keycol(m, [(f - 2, amber), (f + 4, amber)])
    _txt("lbl_old", "OLD CODE", (RACK_X - 0.56, RACK_Y[7], 2.62), 0.2, M["red"], rot=(R(90), 0, R(-90)))
    tech = person("tech", (10.7, -8.5, 0), sc.get("e11_face_y", 0.0), "Walk", speed=1.0)
    animate(tech, "location", [(1, Vector((10.7, -8.5, 0))), (sc.frame_end - 20, Vector((10.7, 7.2, 0)))], interp='LINEAR')
    if v:
        camera("dolly", target=(RACK_X, 0, 1.0), start=(7.4, -9.5, 1.6), end=(7.6, -6.5, 1.6), lens=24, fstop=4)
    else:
        camera("dolly", target=(RACK_X, 0.5, 1.0), start=(7.0, -10.0, 1.7), end=(7.4, -7.5, 1.6), lens=24, fstop=4)
    return sc


def _stream(name, src_loc, rate_start, frame_end, count, direction=(-1, 0, 0), speed=5.0, card=None):
    bpy.ops.mesh.primitive_plane_add(size=0.4, location=src_loc, rotation=(0, R(-90), 0)); em = bpy.context.object
    em.name = name; em.hide_render = True
    ps_mod = em.modifiers.new(name + "_ps", 'PARTICLE_SYSTEM'); ps = ps_mod.particle_system.settings
    ps.count = count; ps.frame_start = rate_start; ps.frame_end = frame_end; ps.lifetime = 140
    ps.emit_from = 'FACE'; ps.normal_factor = speed; ps.factor_random = 1.2; ps.effector_weights.gravity = 0.0
    ps.render_type = 'OBJECT'; ps.instance_object = card; ps.particle_size = 1.0; ps.size_random = 0.3
    ps.use_rotations = True; ps.rotation_mode = 'VEL'; ps.angular_velocity_mode = 'RAND'; ps.angular_velocity_factor = 4.0
    ps.use_dynamic_rotation = True
    return em


def _card(M):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -50)); c = bpy.context.object; c.name = "order_card"
    c.scale = (0.14, 0.08, 1); bpy.ops.object.transform_apply(scale=True); c.data.materials.append(M["card"])
    return c


def shot_flood(v=False):
    """Zoom toward rack 8: order tickets pour out of it, non-stop, over the trading floor."""
    sc = _shot("ep11_flood", 9, v)
    M = _mats(); office(M)
    leds = [bpy.data.materials[n] for n in sc["e11_leds"]]
    for i, m in enumerate(leds):
        _keycol(m, [(1, (0.1, 1.0, 0.35) if i < 7 else (1.0, 0.08, 0.05))])
    card = _card(M)
    _stream("flood8", (RACK_X - 0.6, RACK_Y[7], 1.2), 12, 270, 2600, speed=6.0, card=card)
    _txt("lbl_srv8", "SERVER 8 · POWER PEG", (RACK_X - 0.56, RACK_Y[7], 2.62), 0.16, M["red"], rot=(R(90), 0, R(-90)))
    if v:
        camera("dolly", target=(RACK_X - 0.5, RACK_Y[7], 1.3), start=(7.2, 3.6, 1.5), end=(9.6, 6.0, 1.4), lens=24, fstop=3.5)
    else:
        camera("dolly", target=(RACK_X - 0.5, RACK_Y[7] - 0.5, 1.3), start=(6.6, 2.0, 1.6), end=(9.4, 5.4, 1.45), lens=26, fstop=3.5)
    return sc


def shot_rollback(v=False):
    """The fix that made it worse: racks 1-7 flip from green to red and start streaming too."""
    sc = _shot("ep11_rollback", 9, v)
    M = _mats(); office(M, desks=False, people=False)
    leds = [bpy.data.materials[n] for n in sc["e11_leds"]]
    green, red = (0.1, 1.0, 0.35), (1.0, 0.08, 0.05)
    card = _card(M)
    _keycol(leds[7], [(1, red)])
    _stream("flood8", (RACK_X - 0.6, RACK_Y[7], 1.2), 1, 270, 900, speed=5.0, card=card)
    for i in range(7):
        f = 45 + (6 - i) * 14
        _keycol(leds[i], [(f - 2, green), (f + 3, red)])
        _stream(f"flood{i}", (RACK_X - 0.6, RACK_Y[i], 1.2), f, 270, 700, speed=5.0, card=card)
    _txt("lbl_rb", "UNDO THE UPDATE", (RACK_X - 0.56, 0, 2.95), 0.26, M["amber"], rot=(R(90), 0, R(-90)))
    if v:
        camera("dolly", target=(RACK_X, 0, 1.1), start=(4.5, -6.5, 2.0), end=(5.2, -5.6, 1.9), lens=20, fstop=6)
    else:
        camera("dolly", target=(RACK_X, 0, 1.1), start=(5.0, -8.5, 2.3), end=(5.6, -7.2, 2.1), lens=24, fstop=6)
    return sc


def shot_pile(v=False):
    """Unwanted stock piles up on the trading floor while traders step back."""
    sc = _shot("ep11_pile", 9, v)
    M = _mats(); office(M, people=False)
    random.seed(3)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -60)); b0 = bpy.context.object; b0.name = "sbox"
    b0.scale = (0.45, 0.35, 0.3); bpy.ops.object.transform_apply(scale=True); b0.data.materials.append(M["box"])
    bv = b0.modifiers.new("bevel", 'BEVEL'); bv.width = 0.015; bv.segments = 2
    cx, cy = -8.1, 2.0
    fps = sc.render.fps; n = 260
    for k in range(n):
        layer = int((k / n) ** 0.6 * 9)
        rad = max(0.4, 2.6 - layer * 0.26)
        a = random.uniform(0, 2 * math.pi); r = rad * math.sqrt(random.random())
        x, y, z = cx + r * math.cos(a), cy + r * math.sin(a), 0.15 + layer * 0.29
        o = b0.copy(); o.data = b0.data; o.name = f"sbox_{k}"; sc.collection.objects.link(o)
        o.rotation_euler = (0, 0, random.uniform(0, math.pi))
        f = int(8 + k * (sc.frame_end - 40) / n)
        animate(o, "location", [(f, Vector((x, y, 3.5))), (f + 9, Vector((x, y, z)))], interp='BEZIER', ease='EASE_IN')
    for k, (x, y, rz) in enumerate([(-11.5, -1.5, R(-50)), (-4.6, -1.2, R(60)), (-5.0, 5.4, R(140)), (-11.0, 5.6, R(-140))]):
        person(f"obs_{k}", (x, y, 0), rz, "Idle", f0=-k * 30)
    _txt("lbl_pile", "$3.5 BILLION OF UNWANTED STOCK", (cx, cy - 3.4, 3.1), 0.3, M["amber"])
    if v:
        camera("orbit", target=(cx, cy, 1.4), radius=9.5, height=2.6, deg=25, start_deg=-105, lens=22, fstop=5)
    else:
        camera("orbit", target=(cx, cy, 1.3), radius=10.5, height=2.8, deg=30, start_deg=-110, lens=26, fstop=5)
    return sc


def shot_emails(v=False):
    """8:01 a.m.: automated emails pile into an inbox nobody is watching."""
    sc = _shot("ep11_emails", 7, v)
    M = _mats(); office(M, people=False)
    d = desk(M, 2.6, -4, 0, n_mon=1)
    # one screen becomes an inbox: rows slide down as new mails arrive on top
    sx, sy, sz = 2.6, -4 + 0.193, 1.09
    inbox = pivot("inbox", (sx, sy, sz))
    rowm = mat("e11_row", (0.85, 0.87, 0.9), 0.0, 0.5, emit=(0.8, 0.85, 0.95), strength=0.6)
    for k in range(14):
        f = 10 + k * 11
        r = box(f"row_{k}", (0, 0, 0), (0.5, 0.003, 0.018), rowm, parent=inbox, bevel=0)
        dot = box(f"dot_{k}", (-0.23, -0.002, 0), (0.012, 0.003, 0.012), M["red"], parent=inbox, bevel=0)
        for o in (r, dot):
            base = o.location.copy()
            keys = [(f - 1, Vector((base.x, base.y, 0.2)))]
            for j in range(k + 1, 15):
                keys.append((10 + j * 11, Vector((base.x, base.y, 0.135 - (j - k - 1) * 0.024))))
            animate(o, "location", [(f - 1, Vector((base.x, base.y, 0.2))), (f, Vector((base.x, base.y, 0.135)))] +
                    [(10 + j * 11, Vector((base.x, base.y, 0.135 - (j - k) * 0.024))) for j in range(k + 1, 15)],
                    interp='CONSTANT')
    _txt("lbl_err", "Power Peg disabled", (sx, sy - 0.004, sz + 0.25), 0.03, M["red"])
    t97 = _txt("lbl_97", "97 EMAILS  ·  8:01–9:30", (sx, sy - 0.3, sz + 0.42), 0.07, M["amber"])
    animate(t97, "scale", [(150, Vector((0.001, 0.001, 0.001))), (160, Vector((1, 1, 1)))])
    if v:
        camera("dolly", target=(sx, sy, sz + 0.05), start=(sx - 0.25, sy - 1.6, 1.25), end=(sx - 0.1, sy - 1.0, 1.15), lens=35, fstop=2.2)
    else:
        camera("dolly", target=(sx, sy, sz + 0.05), start=(sx - 0.6, sy - 1.4, 1.3), end=(sx - 0.2, sy - 0.85, 1.15), lens=35, fstop=2.2)
    return sc


def shot_button(v=False):
    """The missing kill switch: a cover lifts, the big red button goes down, every rack goes dark."""
    sc = _shot("ep11_button", 7, v)
    M = _mats(); office(M, desks=False, people=False)
    g = pivot("killsw", (7.6, -1.6, 0))
    cyl("ped", (0, 0, 0.5), 0.22, 1.0, M["ped"], parent=g)
    cyl("ped_top", (0, 0, 1.02), 0.26, 0.05, M["stripe"], parent=g)
    for k in range(8):
        box(f"strp_{k}", (0, 0, 1.02), (0.53, 0.04, 0.052), M["leg"], rot=(0, 0, R(k * 22.5)), parent=g, bevel=0)
    cyl("btn_base", (0, 0, 1.07), 0.12, 0.05, M["leg"], parent=g)
    btn = pivot("btn_p", (0, 0, 1.1), parent=g)
    cyl("btn", (0, 0, 0.03), 0.1, 0.06, M["btn"], parent=btn, verts=48)
    sphere("btn_dome", (0, 0, 0.055), 0.1, M["btn"], parent=btn)
    hinge = pivot("cov_h", (0, 0.16, 1.07), parent=g)
    box("cover", (0, -0.16, 0.08), (0.3, 0.32, 0.16), M["cover"], parent=hinge, bevel=0.01)
    animate(hinge, "rotation_euler", [(30, Euler((0, 0, 0))), (52, Euler((R(-110), 0, 0)))])
    animate(btn, "location", [(80, Vector((0, 0, 1.1))), (84, Vector((0, 0, 1.06))), (96, Vector((0, 0, 1.06)))])
    leds = [bpy.data.materials[n] for n in sc["e11_leds"]]
    for m in leds:
        _keycol(m, [(1, (1.0, 0.08, 0.05)), (86, (1.0, 0.08, 0.05)), (90, (0.0, 0.0, 0.0))])
    _txt("lbl_kill", "KILL SWITCH", (7.6, -1.6 - 0.5, 1.75), 0.14, M["white"])
    if v:
        camera("dolly", target=(7.6, -1.6, 1.1), start=(6.4, -3.8, 1.7), end=(6.9, -3.0, 1.55), lens=32, fstop=3)
    else:
        camera("dolly", target=(7.7, -1.2, 1.1), start=(5.8, -3.9, 1.8), end=(6.6, -3.0, 1.6), lens=30, fstop=3)
    return sc


SHOTS = dict(floor=shot_floor, switch=shot_switch, racks=shot_racks, flood=shot_flood, rollback=shot_rollback,
             pile=shot_pile, emails=shot_emails, button=shot_button)
PORTRAIT = ["switch", "racks", "flood", "rollback", "emails"]


def build(names, v=False):
    out = []
    for n in names:
        sc = SHOTS[n](v)
        polish(sc)
        out.append(sc.name)
    return out
