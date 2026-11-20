"""EP10 (Silver Bridge, 1967) 3D shots. Exec AFTER bb_kit in the same namespace (K).
All models are original: a heat-treated eyebar chain joint (2 bars per link, pin, nuts, hanger), the eye of
eyebar 330 with the stress-corrosion crack (shown enlarged), a 2-bar vs 8-bar link comparison, and a
simplified Silver Bridge (380-700-380 ft spans, rocker towers, eyebar chains forming the top chord of the
stiffening truss near mid-span). No vehicles and no collapse are depicted. No external assets.
Units: metres for the joint/eye shots (bar 12 in x 2 in -> 0.30 x 0.05, pin 11.5 in -> r 0.146);
1 unit = 10 ft for the whole-bridge shot.
"""
import bpy, math
from mathutils import Vector, Euler

R = math.radians


def M_():
    return dict(
        alu=mat("e10_alu", (0.62, 0.64, 0.66), 0.85, 0.42, wear=0.18, wear_scale=40),
        alu2=mat("e10_alu2", (0.55, 0.57, 0.6), 0.85, 0.5, wear=0.25, wear_scale=25),
        pin=mat("e10_pin", (0.4, 0.42, 0.45), 1.0, 0.3, wear=0.3, wear_scale=80),
        rust=mat("e10_rust", (0.32, 0.12, 0.05), 0.3, 0.8, wear=0.4, wear_scale=90),
        crack=glow("e10_crack", (1.0, 0.08, 0.02), 30.0),
        amber=glow("e10_amber", (1.0, 0.55, 0.0), 6.0),
        ambersoft=mat("e10_ambs", (0.9, 0.5, 0.08), 0.6, 0.35, emit=(1.0, 0.5, 0.0), strength=1.5),
        conc=mat("e10_conc", (0.42, 0.4, 0.37), 0.0, 0.9, wear=0.2, wear_scale=6),
        deck=mat("e10_deck", (0.12, 0.12, 0.13), 0.0, 0.85, wear=0.1),
        water=mat("e10_water", (0.03, 0.07, 0.08), 0.2, 0.08),
        load=mat("e10_load", (0.18, 0.2, 0.24), 0.6, 0.4, wear=0.1),
    )


# ------------------------------------------------------------ 2D extruded shapes (eyebars)
def _poly(name, pts, thick, m, parent=None, bevel=0.004):
    """Filled 2D outline in local XY, extruded +-thick/2 along local Z."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'
    cu.extrude = thick / 2; cu.bevel_depth = bevel; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (c[0], c[1], 0, 1)
    sp.use_cyclic_u = True
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    cu.materials.append(m)
    if parent:
        o.parent = parent
    return o


def _arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(R(a0 + (a1 - a0) * k / n)), cy + r * math.sin(R(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


RH, HW, RP = 0.36, 0.15, 0.146   # head radius, bar half-width, pin radius


def _neck(p0, p1, n=8):
    out = []
    for k in range(1, n):
        t = k / n; s = t * t * (3 - 2 * t)
        out.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * s))
    return out


def eyebar_pieces(name, L, m, parent=None, thick=0.05):
    """Eyebar from pin at x=0 to pin at x=L, split through both limbs of the eye at x=L.
    Returns (main, crown): main = bar + eye A + the bar-side half of eye B; crown = far half-ring of eye B
    (stays on the pin when both limbs break)."""
    nk = 0.85
    pts = [(nk, HW), (L - nk, HW)]
    pts += _neck((L - nk, HW), (L + RH * math.cos(R(120)), RH * math.sin(R(120))))
    pts += _arc(L, 0, RH, 120, 90, 4)
    pts += [(L, RP)]
    pts += _arc(L, 0, RP, 90, 270, 24)
    pts += [(L, -RH)]
    pts += _arc(L, 0, RH, 270, 240, 4)
    pts += _neck((L + RH * math.cos(R(240)), RH * math.sin(R(240))), (L - nk, -HW))
    pts += [(L - nk, -HW), (nk, -HW)]
    pts += _neck((nk, -HW), (RH * math.cos(R(300)), RH * math.sin(R(300))))
    pts += _arc(0, 0, RH, 300, 60, 32)
    pts += _neck((RH * math.cos(R(60)), RH * math.sin(R(60))), (nk, HW))
    main = _poly(name + "_main", _clean(pts), thick, m, parent)
    sp = main.data.splines.new('POLY'); hole = _arc(0, 0, RP, 0, 360, 40)[:-1]
    sp.points.add(len(hole) - 1)
    for p, c in zip(sp.points, hole):
        p.co = (c[0], c[1], 0, 1)
    sp.use_cyclic_u = True
    crown = _poly(name + "_crown", _arc(L, 0, RH, -90, 90, 24) + _arc(L, 0, RP, 90, -90, 24), thick, m, parent)
    return main, crown


def _clean(pts):
    out = []
    for p in pts:
        if not out or (abs(p[0] - out[-1][0]) > 1e-5 or abs(p[1] - out[-1][1]) > 1e-5):
            out.append(p)
    return out


def eyebar(name, L, m, parent=None, thick=0.05):
    """Whole eyebar (no split), pins at x=0 and x=L."""
    nk = 0.85
    pts = []
    pts += _arc(0, 0, RH, 60, 300)
    pts += _neck((RH * math.cos(R(300)), RH * math.sin(R(300))), (nk, -HW))
    pts += [(nk, -HW), (L - nk, -HW)]
    pts += _neck((L - nk, -HW), (L + RH * math.cos(R(240)), RH * math.sin(R(240))))
    pts += _arc(L, 0, RH, 240, 480)
    pts += _neck((L + RH * math.cos(R(120)), RH * math.sin(R(120))), (L - nk, HW))
    pts += [(L - nk, HW), (nk, HW)]
    pts += _neck((nk, HW), (RH * math.cos(R(60)), RH * math.sin(R(60))))
    o = _poly(name, _clean(pts), thick, m, parent)
    for cx in (0, L):
        sp = o.data.splines.new('POLY'); hole = _arc(cx, 0, RP, 0, 360, 40)[:-1]
        sp.points.add(len(hole) - 1)
        for p, c in zip(sp.points, hole):
            p.co = (c[0], c[1], 0, 1)
        sp.use_cyclic_u = True
    return o


def pin_assembly(name, M, loc, length, parent=None, axis_rot=(R(90), 0, 0)):
    root = pivot(name, loc, parent=parent, rot=axis_rot)
    cyl(name + "_pin", (0, 0, 0), RP - 0.002, length, M["pin"], verts=48, parent=root)
    for s in (-1, 1):
        cyl(f"{name}_nut{s}", (0, 0, s * (length / 2 + 0.04)), 0.2, 0.08, M["pin"], verts=6, parent=root, bevel=0.01)
        cyl(f"{name}_cap{s}", (0, 0, s * (length / 2 + 0.1)), 0.15, 0.05, M["pin"], verts=32, parent=root, bevel=0.01)
    return root


# ------------------------------------------------------------ shot A: chain joint close-up
def shot_joint(out, v=False):
    sc = stage("ep10_joint" + ("_v" if v else ""), seconds=9.0, samples=16, res=(1080, 1920) if v else (1920, 1080))
    M = M_(); studio(target=(0, 0, 0.0), scale=0.5)
    L = 3.2
    # joint at origin; link A comes from the left (rising), link B goes right (rising)
    j = pivot("e10_joint", (0, 0, 2.3))
    pin_assembly("e10_pinA", M, (0, 0, 0), 0.62, parent=j)
    la = pivot("e10_linkA", (0, 0, 0), parent=j, rot=(R(90), R(166), 0))
    lb = pivot("e10_linkB", (0, 0, 0), parent=j, rot=(R(90), R(-22), 0))
    for k, z in enumerate((-0.2, 0.2)):          # link A bars outside, link B bars inside
        b = eyebar(f"e10_a{k}", L, M["alu"], parent=la); b.location = (0, 0, z)
    for k, z in enumerate((-0.11, 0.11)):
        b = eyebar(f"e10_b{k}", L, M["alu"], parent=lb); b.location = (0, 0, z)
    # hanger plates hanging from the pin
    hg = pivot("e10_hanger", (0, 0, 0), parent=j)
    for s in (-0.03, 0.03):
        box(f"e10_hang{s}", (0, s, -1.05), (0.22, 0.025, 2.0), M["alu2"], bevel=0.008, parent=hg)
    cyl("e10_hangpin", (0, 0, -1.9), 0.06, 0.2, M["pin"], rot=(R(90), 0, 0), verts=24, parent=hg)
    # load passing: links flex a couple of degrees, hanger swings slightly
    animate(la, "rotation_euler", [(1, Euler((R(90), R(166), 0))), (120, Euler((R(90), R(163.5), 0))), (270, Euler((R(90), R(166), 0)))])
    animate(lb, "rotation_euler", [(1, Euler((R(90), R(-22), 0))), (120, Euler((R(90), R(-19.5), 0))), (270, Euler((R(90), R(-22), 0)))])
    animate(hg, "rotation_euler", [(1, Euler((0, 0, 0))), (120, Euler((0, R(1.5), 0))), (270, Euler((0, 0, 0)))])
    # amber "load" pulse travelling along link A into the pin
    pulse = sphere("e10_pulse", (0, 0, 0), 0.09, M["amber"], parent=la)
    animate(pulse, "location", [(20, Vector((L, 0, 0.27))), (110, Vector((0.4, 0, 0.27))), (135, Vector((0.2, 0, 0.27)))])
    animate(pulse, "scale", [(15, Vector((0.01,) * 3)), (25, Vector((1,) * 3)), (125, Vector((1,) * 3)), (140, Vector((0.01,) * 3))])
    if v:
        camera("dolly", target=(0, 0, 2.0), start=(1.4, -4.8, 3.4), end=(0.6, -3.4, 2.8), lens=35, fstop=5.6)
    else:
        camera("orbit", target=(0, 0, 2.0), radius=4.4, height=0.9, deg=40, start_deg=-115, lens=40, fstop=5.6)
    polish(sc)
    return sc


# ------------------------------------------------------------ shot B: the eye of eyebar 330
def shot_eye(out, v=False):
    sc = stage("ep10_eye" + ("_v" if v else ""), seconds=10.0, samples=16, res=(1080, 1920) if v else (1920, 1080))
    M = M_(); studio(target=(0, 0, 1.0), scale=0.45)
    L = 2.6
    root = pivot("e10_root", (-L, 0, 1.0), rot=(R(90), 0, 0))     # bars in the XZ plane, pin along Y at x=0
    main, crown = eyebar_pieces("e10_330", L, M["alu"], parent=root)
    main.location.z = crown.location.z = -0.09
    sis = eyebar("e10_33", L, M["alu"], parent=root); sis.location.z = 0.09
    pin_assembly("e10_pin330", M, (0, 0, 1.0), 0.32, axis_rot=(R(90), 0, 0))
    # crack on the inner surface of the lower limb (enlarged): thin red sliver growing outwards
    cr = box("e10_crackm", (0, 0, 0), (0.012, 0.09, 0.056), M["crack"], bevel=0.0)
    cr.parent = root; cr.location = (L, -RP - 0.045, -0.09)
    animate(cr, "scale", [(1, Vector((1, 0.05, 1))), (60, Vector((1, 0.05, 1))), (120, Vector((1, 1.0, 1)))])
    bpy.ops.object.light_add(type='POINT', location=(0, -0.3, 0.75)); Lt = bpy.context.object
    Lt.data.color = (1.0, 0.12, 0.05)
    animate(Lt.data, "energy", [(1, 0.0), (60, 0.0), (120, 25.0), (150, 60.0), (170, 0.0)])
    # 150: lower limb cleaves (crack opens, bar rotates about the upper limb); 175: upper limb tears; bar pulls away
    hinge = pivot("e10_hinge", (L, RH, -0.09), parent=root)
    main.parent = hinge; main.location = (-L, -RH, 0)
    animate(hinge, "rotation_euler", [(150, Euler((0, 0, 0))), (156, Euler((0, 0, R(-4)))), (175, Euler((0, 0, R(-6))))])
    animate(hinge, "location", [(175, Vector((L, RH, -0.09))), (215, Vector((L - 1.4, RH - 0.25, -0.09)))])
    animate(cr, "scale", [(150, Vector((1, 1, 1))), (152, Vector((0.01, 0.01, 0.01)))])
    for nm in ("e10_pin330_nut1", "e10_pin330_cap1"):
        o = [x for x in bpy.context.scene.objects if x.name.split(".")[0] == nm][0]
        animate(o, "location", [(190, o.location.copy()), (205, o.location + Vector((0, 0, 0.5)))])
        animate(o, "scale", [(205, Vector((1, 1, 1))), (215, Vector((0.01, 0.01, 0.01)))])
    # sister eyebar 33 slides off the end of the pin (along local z = world -Y) and drops away
    animate(sis, "location", [(205, Vector((0, 0, 0.09))), (240, Vector((0, 0, 0.45))), (285, Vector((0, -0.9, 0.55)))])
    animate(sis, "rotation_euler", [(215, Euler((0, 0, 0))), (285, Euler((0, R(8), R(-14))))])
    if v:
        camera("dolly", target=(0, 0, 0.8), start=(0.9, -3.4, 1.5), end=(0.45, -2.2, 1.1), lens=35, fstop=5.6)
    else:
        camera("dolly", target=(-0.25, 0, 0.95), start=(1.2, -3.0, 1.8), end=(0.5, -1.9, 1.25), lens=40, fstop=5.6)
    polish(sc)
    return sc


# ------------------------------------------------------------ shot C: 2-bar vs 8-bar link
def _link(prefix, M, x, nbars, Lk=2.6):
    top = (x, 0, 3.4); bot = (x, 0, 3.4 - Lk)
    span = 0.16 * (nbars - 1) if nbars > 2 else 0.24
    zs = [-span / 2 + span * i / (nbars - 1) for i in range(nbars)]
    pin_assembly(prefix + "_top", M, top, span + 0.12, axis_rot=(R(90), 0, 0))
    botp = pin_assembly(prefix + "_bot", M, bot, span + 0.12, axis_rot=(R(90), 0, 0))
    bars = []
    for i, z in enumerate(zs):
        b = eyebar(f"{prefix}_bar{i}", Lk, M["alu"]); b.location = (x, z, 3.4); b.rotation_euler = (R(90), R(90), 0)
        bars.append(b)
    load = box(prefix + "_load", (x, 0, bot[2] - 0.75), (0.9, max(0.6, span + 0.4), 0.9), M["load"], bevel=0.03)
    tie = box(prefix + "_tie", (x, 0, bot[2] - 0.2), (0.12, 0.08, 0.5), M["alu2"], bevel=0.01)
    return bars, botp, load, tie


def shot_links(out, v=False):
    sc = stage("ep10_links" + ("_v" if v else ""), seconds=9.0, samples=16, res=(1080, 1920) if v else (1920, 1080))
    M = M_(); studio(target=(0, 0, 2.2), scale=0.6)
    xa, xb = (-1.3, 1.3)
    a_bars, a_bot, a_load, a_tie = _link("e10_two", M, xa, 2)
    b_bars, b_bot, b_load, b_tie = _link("e10_eight", M, xb, 8)
    # beam the links hang from
    box("e10_beam", (0, 0, 3.75), (4.6, 1.6, 0.25), M["alu2"], bevel=0.02)
    # frame 70: one bar in each link turns red; 90: it breaks away (moves out sideways and drops)
    for bars in (a_bars, b_bars):
        brk = bars[0]
        brk.data.materials.append(M["crack"])
        animate(brk, "location", [(90, brk.location.copy()), (130, brk.location + Vector((0, -0.9, -1.2)))])
        animate(brk, "rotation_euler", [(90, Euler(brk.rotation_euler)), (130, Euler((R(90), R(130), R(25))))])
        animate(brk, "scale", [(130, Vector((1, 1, 1))), (150, Vector((0.01, 0.01, 0.01)))])
    # warning glow: the broken bar flashes red before it goes
    for i, bars in enumerate((a_bars, b_bars)):
        bpy.ops.object.light_add(type='POINT', location=(bars[0].location.x, -0.6, 2.2)); Lt = bpy.context.object
        Lt.data.color = (1.0, 0.1, 0.05); animate(Lt.data, "energy", [(1, 0.0), (65, 0.0), (85, 80.0), (110, 0.0)])
    # 2-bar link: remaining bar now carries double -> amber, then it fails at 170 and the load drops away
    rem = a_bars[1]
    amb = M["ambersoft"]
    halo = box("e10_halo2", (xa, a_bars[1].location.y, 2.1), (0.09, 0.06, 2.0), amb, bevel=0.0)
    animate(halo, "scale", [(1, Vector((0.01, 0.01, 0.01))), (110, Vector((0.01, 0.01, 0.01))), (125, Vector((1, 1, 1))), (170, Vector((1, 1, 1))), (172, Vector((0.01, 0.01, 0.01)))])
    for o in (rem, a_bot, a_load, a_tie):
        animate(o, "location", [(170, o.location.copy()), (215, o.location + Vector((0, 0, -4.5)))], ease='EASE_IN')
    # 8-bar link: the other seven share the load, small amber glow, load stays put
    halo8 = box("e10_halo8", (xb, 0, 2.1), (0.08, 1.15, 2.0), mat("e10_amb8", (0.9, 0.55, 0.1), 0.5, 0.4, emit=(1.0, 0.55, 0.05), strength=0.35, alpha=0.4), bevel=0.0)
    animate(halo8, "scale", [(1, Vector((0.01, 0.01, 0.01))), (110, Vector((0.01, 0.01, 0.01))), (125, Vector((1, 1, 1)))])
    shake(b_load, amp=0.01, freq=6, f0=95, f1=140)
    if v:
        camera("dolly", target=(0, 0, 1.9), start=(4.0, -7.8, 3.2), end=(3.3, -6.7, 2.9), lens=35, fstop=11)
    else:
        camera("dolly", target=(0, 0, 1.9), start=(5.0, -6.0, 3.4), end=(4.1, -4.9, 3.0), lens=35, fstop=11)
    polish(sc)
    return sc


# ------------------------------------------------------------ shot D: the whole bridge (1 unit = 10 ft)
def shot_bridge(out, v=False):
    sc = stage("ep10_bridge" + ("_v" if v else ""), seconds=10.0, samples=16, res=(1080, 1920) if v else (1920, 1080))
    M = M_(); day(sun_elev=22, sun_rot=210, ground_color=(0.25, 0.27, 0.2))
    for o in list(bpy.context.scene.objects):
        if o.name.split(".")[0] == "ground":
            bpy.data.objects.remove(o, do_unlink=True)
    bank = mat("e10_bank", (0.16, 0.2, 0.1), 0.0, 0.95, wear=0.3, wear_scale=3)
    for k, sx in enumerate((-1, 1)):
        box(f"e10_bank{k}", (sx * 150, 0, -5.0), (140, 700, 9.6), bank, bevel=0.0)
    W = 1.6                       # half-width between chain planes
    xs = [-73, -35, 35, 73]        # anchorage(Ohio, west), Ohio tower, WV tower, anchorage (WV, east)
    TOP, HT = 12.5, 2.2            # tower top above deck; truss depth
    water = box("e10_water", (0, 0, -9.2), (900, 900, 0.2), M["water"], bevel=0.0)
    # piers + rocker towers
    towers = []
    for k, xt in enumerate(xs[1:3]):
        box(f"e10_pier{k}", (xt, 0, -5.0), (3.2, 2 * W + 3.0, 8.6), M["conc"], bevel=0.15)
        tp = pivot(f"e10_tower{k}", (xt, 0, -0.7))        # rocker seat
        for s in (-1, 1):
            box(f"e10_leg{k}{s}", (0, s * W, (TOP + 0.7) / 2), (0.7, 0.55, TOP + 0.7), M["alu"], bevel=0.05, parent=tp)
            cyl(f"e10_rock{k}{s}", (0, s * W, 0.0), 0.45, 0.6, M["pin"], rot=(R(90), 0, 0), verts=32, parent=tp)
        for zz in (HT + 1.6, TOP - 0.9, TOP - 3.4):
            box(f"e10_portal{k}{zz}", (0, 0, zz + 0.7), (0.5, 2 * W, 0.45), M["alu"], bevel=0.04, parent=tp)
        for s in (-1, 1):  # X-bracing between portals
            box(f"e10_xb{k}{s}", (0, 0, (HT + TOP) / 2 + 0.6), (0.18, 0.18, math.hypot(2 * W, TOP - HT - 3.0)), M["alu2"],
                rot=(s * math.atan2(2 * W, TOP - HT - 3.0), 0, 0), bevel=0.0, parent=tp)
        animate(tp, "rotation_euler", [(1, Euler((0, 0, 0))), (150, Euler((0, R(0.8 if k == 0 else -0.6), 0))), (300, Euler((0, 0, 0)))])
        towers.append(tp)
    # anchorages
    for k, xa in enumerate((xs[0], xs[3])):
        box(f"e10_anch{k}", (xa + (-2 if k == 0 else 2), 0, -1.5), (6, 2 * W + 2.4, 4.6), M["conc"], bevel=0.2)
    # chain geometry: parabola in main span from tower tops down to the truss top chord at mid-span;
    # side spans from tower tops down to the anchorages at truss height
    def chain_z(x):
        if -35 <= x <= 35:
            return HT + (TOP - HT) * (x / 35.0) ** 2
        if x < -35:
            t = (x - xs[0]) / (xs[1] - xs[0])
        else:
            t = (xs[3] - x) / (xs[3] - xs[2])
        return HT + (TOP - HT) * t ** 1.6
    xsamp = [xs[0] + i * (xs[3] - xs[0]) / 120 for i in range(121)]
    panels = [xs[0] + i * (xs[3] - xs[0]) / 42 for i in range(43)]
    for s in (-1, 1):
        y = s * W
        tube(f"e10_chain{s}", [(x, y, chain_z(x) + 0.7) for x in xsamp], 0.24, M["alu"])
        # stiffening truss: chords, verticals, diagonals; hangers from the chain to the top chord
        tube(f"e10_bot{s}", [(xs[0], y, 0.7), (xs[3], y, 0.7)], 0.14, M["alu"])
        tube(f"e10_topc{s}", [(xs[0], y, HT + 0.7), (xs[3], y, HT + 0.7)], 0.11, M["alu"])
        for i, x in enumerate(panels):
            tube(f"e10_v{s}{i}", [(x, y, 0.7), (x, y, HT + 0.7)], 0.06, M["alu2"])
            if i < len(panels) - 1:
                xn = panels[i + 1]
                a, b = ((x, y, 0.7), (xn, y, HT + 0.7)) if i % 2 == 0 else ((x, y, HT + 0.7), (xn, y, 0.7))
                tube(f"e10_d{s}{i}", [a, b], 0.05, M["alu2"])
            cz = chain_z(x) + 0.7
            if cz > HT + 0.95:
                tube(f"e10_h{s}{i}", [(x, y, HT + 0.7), (x, y, cz)], 0.035, M["alu2"])
    box("e10_deck", (0, 0, 0.75), (xs[3] - xs[0], 2 * W - 0.2, 0.18), M["deck"], bevel=0.0)
    # approach (concrete) toward both banks
    for k, xa in enumerate((xs[0] - 22, xs[3] + 22)):
        box(f"e10_appr{k}", (xa, 0, 0.6), (40, 2 * W, 0.4), M["conc"], bevel=0.05)
    # highlight: joint C13N, first chain joint west of the Ohio tower (north chain = +y here)
    xj = -35 - (xs[1] - xs[0]) / 7.0
    marker = sphere("e10_c13n", (xj, W, chain_z(xj) + 0.7), 0.7, M["amber"])
    animate(marker, "scale", [(1, Vector((0.01,) * 3)), (150, Vector((0.01,) * 3)), (175, Vector((1.4,) * 3))])
    bpy.ops.object.light_add(type='POINT', location=(xj, W + 1.2, chain_z(xj) + 1.5)); Lt = bpy.context.object
    Lt.data.color = (1.0, 0.6, 0.1); animate(Lt.data, "energy", [(1, 0.0), (150, 0.0), (180, 4000.0)])
    # load pulse running along the north chain from mid-span to the Ohio anchorage
    pulse = sphere("e10_flow", (0, W, HT + 0.7), 0.55, M["amber"])
    pts = [(x, W, chain_z(x) + 0.7) for x in [0 - i * 1.825 for i in range(41)]]
    follow(pulse, pts, f0=20, f1=150, ease='LINEAR')
    animate(pulse, "scale", [(15, Vector((0.01,) * 3)), (25, Vector((1,) * 3)), (145, Vector((1,) * 3)), (155, Vector((0.01,) * 3))])
    if v:
        camera("dolly", target=(-30, 0, 5.0), start=(-52, 46, 10), end=(-44, 40, 8), lens=26, fstop=16)
    else:
        camera("dolly", target=(-12, 0, 4.0), start=(-54, 92, 18), end=(-22, 78, 13), lens=30, fstop=16)
    return sc


SHOTS = [shot_joint, shot_eye, shot_links, shot_bridge]


def build_all(out, only=None, v=False):
    names = []
    for fn in SHOTS:
        if only and fn.__name__ not in only:
            continue
        sc = fn(out, v=v); names.append(sc.name)
        sc.view_settings.exposure = -1.0
    return names
