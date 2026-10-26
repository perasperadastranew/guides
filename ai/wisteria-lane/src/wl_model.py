"""
Wisteria Lane — procedural low-poly street, house by house.

One script, two modes:
  * Inside Blender (Scripting tab -> Run Script, or MCP execute_blender_code):
      builds every house as its own collection, assembles the street scene,
      and (optionally) saves wisteria_lane.blend + exports glTF.
  * Plain Python 3 (no Blender):  python3 wl_model.py <out_dir>
      writes the same geometry as glTF files for the website.

Units: metres. Y is up in the modelling code (glTF convention); the Blender
backend converts to Z-up. Every house is modelled in its own local frame:
front facade faces +Z, ground at y=0, centred on the origin.
"""
import math, json, os, sys, base64, struct

# --------------------------------------------------------------------------
# 1. PLAN — street layout in metres (the traced map)
# --------------------------------------------------------------------------
ROAD_W = 9.0          # carriageway
WALK_W = 2.0          # sidewalk on each side
SET_Z = 21.5          # house centre distance from the road axis
CUL_R = 15.0          # Circle Drive turning circle radius
ISLAND_R = 5.5

# Traced from the labelled aerial of Universal's Colonial Street (north at -Z):
# the lane comes in from the north, swings east around the Solis house,
# runs back south-west past Bree's, then bends east again into Circle Drive.
CTRL = [(x * .62, z * .62) for x, z in [(-6, -175), (-4, -140), (8, -105), (26, -72), (22, -40), (0, -12),
        (-20, 18), (-24, 50), (-10, 80), (8, 102)]]

def _catmull(P, n=24):
    out = []
    P = [P[0]] + P + [P[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for k in range(n):
            t = k / n; t2, t3 = t*t, t*t*t
            out.append(tuple(.5 * ((2*p1[j]) + (-p0[j]+p2[j])*t + (2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2 + (-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3) for j in (0, 1)))
    out.append(P[-2])
    return out

ROAD = _catmull(CTRL)                      # dense centreline, (x, z)
_S = [0.0]
for i in range(1, len(ROAD)):
    _S.append(_S[-1] + math.dist(ROAD[i], ROAD[i-1]))
ROAD_LEN = _S[-1]

def road_at(s):
    """Point, unit tangent and the east-pointing normal at arc length s."""
    s = max(0.0, min(ROAD_LEN, s))
    for i in range(1, len(_S)):
        if _S[i] >= s: break
    f = (s - _S[i-1]) / ((_S[i] - _S[i-1]) or 1)
    a, b = ROAD[i-1], ROAD[i]
    p = (a[0] + (b[0]-a[0])*f, a[1] + (b[1]-a[1])*f)
    l = math.dist(a, b) or 1
    t = ((b[0]-a[0])/l, (b[1]-a[1])/l)
    return p, t, (t[1], -t[0])

_end, _tend, _ = road_at(ROAD_LEN)
CUL = (_end[0] + _tend[0] * (CUL_R - 3), _end[1] + _tend[1] * (CUL_R - 3))

def _lot_road(s, side):
    """House on the lane: side=+1 east, -1 west; local +Z faces the road."""
    p, t, n = road_at(s)
    x, z = p[0] + n[0]*SET_Z*side, p[1] + n[1]*SET_Z*side
    return x, z, math.atan2(p[0] - x, p[1] - z)

def _lot_cul(ang_deg, r=36.0):
    a = math.atan2(_tend[1], _tend[0]) + math.radians(ang_deg)
    x, z = CUL[0] + r * math.cos(a), CUL[1] + r * math.sin(a)
    return x, z, math.atan2(CUL[0] - x, CUL[1] - z)

# along the lane from the north entrance: (id, arc length, side)
LOTS = [("4347", 14, +1), ("4349", 50, +1), ("4351", 78, +1), ("4353", 106, +1), ("4355", 143, +1),
        ("4344", 8, -1), ("4350", 32, -1), ("4352", 62, -1), ("4354", 112, -1), ("4356", 140, -1)]
PLAN = [(hid, *_lot_road(s, side)) for hid, s, side in LOTS]
for hid, ang in (("4358", -70.0), ("4360", 0.0), ("4362", 70.0)):
    PLAN.append((hid, *_lot_cul(ang)))

# --------------------------------------------------------------------------
# 2. Materials (one shared palette; soft pastel suburb)
# --------------------------------------------------------------------------
MAT = {
    "int_floor": ("#c08f5e", 1.0), "int_wall": ("#efe7d8", 1.0), "int_tile": ("#e4e6e1", 1.0), "int_counter": ("#f6f3ec", 1.0), "int_cab": ("#dfe4dc", 1.0),
    "int_sofa": ("#8f9d7a", 1.0), "int_rug": ("#a8463c", 1.0), "int_wood": ("#6e4b33", 1.0), "int_fabric": ("#d9c7a3", 1.0), "int_steel": ("#c7cbcc", .5),
    "int_concrete": ("#bdb9b0", 1.0), "int_stall": ("#7f97a6", 1.0), "int_porcelain": ("#fbfbf8", .6), "int_case": ("#2f3236", 1.0), "int_tape": ("#e8c33a", 1.0),
    # ground
    "lawn":      ("#b9d59a", 1.0), "lawn_lt": ("#c6dea7", 1.0), "lawn2": ("#a9cb8a", 1.0),
    "road":      ("#a7a9a4", 1.0), "walk": ("#e3e1d8", 1.0), "curb": ("#f1efe8", 1.0),
    "drive":     ("#d4d1c6", 1.0), "soil": ("#b09a7f", 1.0), "mark": ("#f6f3e6", 1.0),
    # houses
    "white":     ("#f5f2ea", 0.9), "cream": ("#efe4c8", 0.9), "mustard": ("#e5bf62", 0.9),
    "sage":      ("#a8c2a0", 0.9), "skyblue": ("#b7cfe0", 0.9), "brick": ("#b5654e", 0.95),
    "blueboard": ("#8fb0cc", 0.9), "butter": ("#f0dca0", 0.9), "craft": ("#9a8d7c", 0.9),
    "grey":      ("#c9ccc8", 0.9), "mint": ("#cfe5c7", 0.9), "blush": ("#ecc9bd", 0.9),
    "tan":       ("#d9c3a2", 0.9), "darkgrey": ("#7b7f7e", 0.95), "stone": ("#bfb7a8", 1.0),
    "roof_dk":   ("#5d6670", 0.85), "roof_rd": ("#9b5c4c", 0.85), "roof_gn": ("#5f7a64", 0.85),
    "roof_br":   ("#7d6656", 0.85), "roof_bl": ("#56708c", 0.85), "roof_lt": ("#8e9296", 0.85),
    "trim":      ("#fbfaf6", 0.8), "door_rd": ("#b8463a", 0.7), "door_bl": ("#3f5f86", 0.7),
    "door_gn":   ("#3f6b4f", 0.7), "door_wd": ("#8a5a3b", 0.7), "glass": ("#9fc0d4", 0.15),
    "shutter_gn":("#557a5e", 0.8), "shutter_bl":("#4f6d8f", 0.8), "shutter_bk": ("#3d4245", 0.8),
    "board":     ("#c9b994", 1.0),
    "yellow":    ("#f1d886", 0.9), "green_lyn": ("#9fb79c", 0.9), "slate": ("#6f7c88", 0.9),
    "teal":      ("#9fb5ad", 0.9), "leaf_lt": ("#8fc46e", 1.0), "grass_tuft": ("#5d9a4c", 1.0),
    "rock": ("#a9aeb0", 1.0), "rock_lt": ("#c4c8c8", 1.0), "wood_cut": ("#e3bf7f", 1.0), "berry": ("#d0443a", 1.0), "hedge_lt": ("#73ac6c", 1.0), "brass": ("#c9a24a", 0.4), "terracotta": ("#c4704f", 0.9), "glass_lt": ("#e8f3fa", 0.1), "meadow": ("#a9c98a", 1.0), "meadow_dk": ("#93b878", 1.0), "hill_dry": ("#d9c48c", 1.0),
    "oak": ("#5e9150", 1.0), "oak_lt": ("#76a860", 1.0), "cypress": ("#3f6e4a", 1.0), "pine": ("#3e7a52", 1.0), "pine_lt": ("#529063", 1.0),
    "palm_trunk": ("#a08462", 1.0), "palm_leaf": ("#6aa35a", 1.0), "jacaranda": ("#a98ad8", 1.0), "jacaranda_lt": ("#c3aaea", 1.0),
    "magnolia": ("#f2c4d3", 1.0), "magnolia_lt": ("#fbe2ea", 1.0), "char": ("#3b3633", 1.0), "ash": ("#8d8781", 1.0), "storm": ("#9aa4ad", 1.0),
    "towel": ("#f2a7b8", 1.0), "grass_bag": ("#4f7a4b", 1.0), "wicker": ("#b98a52", 1.0), "muffin": ("#a4683a", 1.0),
    "muffin_case": ("#f4e3c4", 1.0), "pizza_box": ("#d9b98a", 1.0), "felt": ("#2f7a52", 1.0),
    "cat_or": ("#e09a4d", 1.0), "cat_gr": ("#9a9a9a", 1.0), "cat_bk": ("#3a3a3a", 1.0), "gaby": ("#ecc56a", 0.9), "roof_slate": ("#6b7584", 0.85), "blue_vic": ("#a7c3dc", 0.9), "roof_bn": ("#8a6a52", 0.85),
    # nature & props
    "trunk":     ("#8a6f5a", 1.0), "leaf": ("#6fae6a", 1.0), "leaf2": ("#8cc07a", 1.0),
    "hedge":     ("#5f9a5f", 1.0), "wisteria": ("#b79be0", 1.0), "wisteria2": ("#9c7fd2", 1.0),
    "rose":      ("#e98aa0", 1.0), "flower_y": ("#f2d26b", 1.0), "metal": ("#9aa3a8", 0.4),
    "black":     ("#2e3133", 0.6), "red": ("#d44a3a", 0.6), "car_bl": ("#6f93c4", 0.4),
    "car_rd": ("#d0644f", 0.4), "car_wh": ("#eef0f0", 0.4), "car_bk": ("#43484d", 0.4),
    "water":     ("#9fd0e6", 0.2), "lamp": ("#fff3c8", 0.5), "sign": ("#ffffff", 0.8),
}

# --------------------------------------------------------------------------
# 3. Tiny mesh kit
# --------------------------------------------------------------------------
class Mesh:
    """Polygons grouped by material, built through a transform stack."""
    def __init__(self, name):
        self.name = name
        self.parts = {}            # mat -> list of polygons (list of xyz tuples)
        self.stack = []            # list of (tx, ty, tz, ry)

    # ---- transforms
    def push(self, x=0, y=0, z=0, ry=0.0):
        self.stack.append((x, y, z, ry)); return self
    def pop(self):
        self.stack.pop()
    class _At:
        def __init__(s, m, a): s.m, s.a = m, a
        def __enter__(s): s.m.push(*s.a); return s.m
        def __exit__(s, *e): s.m.pop()
    def at(self, x=0, y=0, z=0, ry=0.0):
        return Mesh._At(self, (x, y, z, ry))
    def tf(self, p):
        x, y, z = p
        for tx, ty, tz, ry in reversed(self.stack):
            if ry:
                c, s = math.cos(ry), math.sin(ry)
                x, z = x * c + z * s, -x * s + z * c
            x, y, z = x + tx, y + ty, z + tz
        return (x, y, z)

    # ---- raw polygons
    def poly(self, mat, pts, up=None):
        """Add one polygon. `up` (optional vector) forces its normal side."""
        P = [self.tf(p) for p in pts]
        if up is not None:
            upw = _sub(self.tf(up), self.tf((0, 0, 0)))
            if _dot(_newell(P), upw) < 0: P.reverse()
        self.parts.setdefault(mat, []).append(P)
    def solid(self, mat, polys, matmap=None):
        """Convex solid: every face is oriented away from the solid's centroid."""
        allp = [p for pl in polys for p in pl]
        cx = sum(p[0] for p in allp) / len(allp); cy = sum(p[1] for p in allp) / len(allp); cz = sum(p[2] for p in allp) / len(allp)
        for i, pl in enumerate(polys):
            P = [self.tf(p) for p in pl]
            c = self.tf((cx, cy, cz))
            m = sum(q[0] for q in P) / len(P), sum(q[1] for q in P) / len(P), sum(q[2] for q in P) / len(P)
            if _dot(_newell(P), _sub(m, c)) < 0: P.reverse()
            mm = matmap(i) if matmap else mat
            self.parts.setdefault(mm, []).append(P)

    # ---- primitives
    def box(self, mat, x0, y0, z0, x1, y1, z1, top=None):
        v = [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1),(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]
        F = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
        self.solid(mat, [[v[i] for i in f] for f in F], (lambda i: top if (top and i == 1) else mat))
    def cbox(self, mat, cx, y0, cz, w, h, d, top=None):
        self.box(mat, cx - w/2, y0, cz - d/2, cx + w/2, y0 + h, cz + d/2, top)
    def frustum(self, mat, x0, z0, x1, z1, y0, ins, y1, top_mat=None, insz=None):
        """Rectangular frustum: footprint rect at y0, rect inset by `ins` at y1."""
        iz = ins if insz is None else insz
        b = [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)]
        t = [(x0+ins,y1,z0+iz),(x1-ins,y1,z0+iz),(x1-ins,y1,z1-iz),(x0+ins,y1,z1-iz)]
        F = [b, t] + [[b[i], b[(i+1)%4], t[(i+1)%4], t[i]] for i in range(4)]
        self.solid(mat, F, (lambda i: top_mat if (top_mat and i == 1) else mat))
    def cyl(self, mat, cx, y0, cz, r0, r1, h, n=8, rot=0.0):
        b = [(cx + r0*math.cos(rot+2*math.pi*i/n), y0, cz + r0*math.sin(rot+2*math.pi*i/n)) for i in range(n)]
        if r1 <= 1e-4:
            ap = (cx, y0 + h, cz)
            F = [b] + [[b[i], b[(i+1)%n], ap] for i in range(n)]
        else:
            t = [(cx + r1*math.cos(rot+2*math.pi*i/n), y0+h, cz + r1*math.sin(rot+2*math.pi*i/n)) for i in range(n)]
            F = [b, t] + [[b[i], b[(i+1)%n], t[(i+1)%n], t[i]] for i in range(n)]
        self.solid(mat, F)
    def blob(self, mat, cx, cy, cz, rx, ry, rz, seed=0.0):
        """Faceted crown: an icosahedron, slightly jittered."""
        t = (1 + 5 ** .5) / 2
        V = [(-1,t,0),(1,t,0),(-1,-t,0),(1,-t,0),(0,-1,t),(0,1,t),(0,-1,-t),(0,1,-t),(t,0,-1),(t,0,1),(-t,0,-1),(-t,0,1)]
        F = [(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),
             (3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
        L = math.sqrt(1 + t*t); P = []
        for i, (a, b, c) in enumerate(V):
            j = 1 + 0.14 * math.sin(seed * 12.9 + i * 7.31)
            P.append((cx + a/L*rx*j, cy + b/L*ry*j, cz + c/L*rz*j))
        for f in F:
            self.poly(mat, [P[i] for i in f], up=_sub(_avg([P[i] for i in f]), (cx, cy, cz)))

    # ---- roofs (built along X; rotate with the stack for other axes)
    def gable(self, mat, wall, x0, x1, z0, z1, ye, yr, over=0.45, th=0.18, attic=True):
        """Gable roof, ridge parallel to X. Gable triangles in `wall` material."""
        zc = (z0 + z1) / 2; zo0, zo1 = z0 - over, z1 + over
        k = (yr - ye) / ((z1 - z0) / 2)
        ylo = ye - over * k
        X0, X1 = x0 - over * 0.6, x1 + over * 0.6
        for zs, ze in ((zo0, zc), (zo1, zc)):   # two slabs
            a = [(X0, ylo, zs), (X1, ylo, zs), (X1, yr, ze), (X0, yr, ze)]
            b = [(p[0], p[1] + th, p[2]) for p in a]
            self.solid(mat, [a, b] + [[a[i], a[(i+1)%4], b[(i+1)%4], b[i]] for i in range(4)])
            self.courses(mat, X0, X1, zs, ylo + th, ze, yr + th)
        self.box(mat + "_dk", X0, yr + th - .02, zc - .16, X1, yr + th + .14, zc + .16)   # ridge cap
        for zs in (zo0, zo1):                                   # fascia boards along both eaves
            sg = 1 if zs > zc else -1
            self.box("trim", X0, ylo - .14, min(zs, zs + sg * .08), X1, ylo + th + .02, max(zs, zs + sg * .08))
        for X, sg in ((X0, -1), (X1, 1)):                      # rake boards following the slopes
            for zs in (zo0, zo1):
                a = [(X, ylo - .12, zs), (X, yr - .12, zc), (X + sg * .1, yr - .12, zc), (X + sg * .1, ylo - .12, zs)]
                b = [(p[0], p[1] + th + .2, p[2]) for p in a]
                self.solid("trim", [a, b] + [[a[i], a[(i+1)%4], b[(i+1)%4], b[i]] for i in range(4)])
        for x in (x0, x1):
            self.poly(wall, [(x, ye, z0), (x, ye, z1), (x, yr, zc)], up=(x - (x0+x1)/2, 0, 0))
        rise, span = yr - ye, z1 - z0
        if attic and span >= 6 and rise >= 2.0:                # attic window in each big gable end
            for x, sg, key in ((x0, -1, "x0"), (x1, 1, "x1")):
                if attic is True or attic == key:
                    h = min(1.25, rise * .42); self.xwin(x, sg, zc, ye + rise * .22, min(1.0, h * .8), h)
    def xwin(self, x, sg, zc, y, w, h, trim="trim"):
        """Framed window on a wall facing +-X (sg) at plane x: frame, glass, cross muntins, sill and crown."""
        X = lambda a, b: (min(x + sg * a, x + sg * b), max(x + sg * a, x + sg * b))
        f = .12
        x0, x1 = X(-.02, .08); self.box(trim, x0, y - f, zc - w/2 - f, x1, y + h + f, zc + w/2 + f)
        x0, x1 = X(.06, .1); self.box("glass", x0, y, zc - w/2, x1, y + h, zc + w/2)
        x0, x1 = X(.08, .13); self.box(trim, x0, y, zc - .03, x1, y + h, zc + .03); self.box(trim, x0, y + h/2 - .03, zc - w/2, x1, y + h/2 + .03, zc + w/2)
        x0, x1 = X(-.02, .22); self.box(trim, x0, y - .2, zc - w/2 - .18, x1, y - .08, zc + w/2 + .18)
        x0, x1 = X(-.02, .2); self.box(trim, x0, y + h + f, zc - w/2 - .2, x1, y + h + f + .1, zc + w/2 + .2)
    def xocul(self, x, sg, zc, y, r, trim="trim", n=12):
        """Round window on a wall facing +-X."""
        ring = lambda rr, xx: [(xx, y + rr*math.sin(2*math.pi*i/n), zc + rr*math.cos(2*math.pi*i/n)) for i in range(n)]
        bo, fo = ring(r + .13, x), ring(r + .13, x + sg * .1)
        self.solid(trim, [bo, fo] + [[bo[i], bo[(i+1)%n], fo[(i+1)%n], fo[i]] for i in range(n)])
        self.poly("glass", ring(r, x + sg * .12), up=(sg, 0, 0))
        a, b = sorted((x + sg * .1, x + sg * .15)); self.box(trim, a, y - r, zc - .035, b, y + r, zc + .035); self.box(trim, a, y - .035, zc - r, b, y + .035, zc + r)
    def courses(self, mat, X0, X1, za, ya, zb, yb, n=4):
        """Shingle course lines on a roof slope from (za, ya) up to (zb, yb)."""
        for i in range(1, n + 1):
            f = i / (n + 1)
            z = za + (zb - za) * f; y = ya + (yb - ya) * f
            dz = (zb - za) / abs(zb - za) * .1
            q = [(X0, y, z), (X1, y, z), (X1, y + .06, z + dz), (X0, y + .06, z + dz)]
            self.poly(mat + "_dk", q, up=(0, 1, 0))
    def hip(self, mat, x0, x1, z0, z1, ye, h, over=0.45):
        X0, X1, Z0, Z1 = x0 - over, x1 + over, z0 - over, z1 + over
        yf = ye - over * h / (min(X1 - X0, Z1 - Z0) / 2)
        if over >= .3:
            self.box("trim", X0 - .05, yf - .16, Z0 - .05, X1 + .05, yf + .02, Z0 + .06)
            self.box("trim", X0 - .05, yf - .16, Z1 - .06, X1 + .05, yf + .02, Z1 + .05)
            self.box("trim", X0 - .05, yf - .16, Z0, X0 + .06, yf + .02, Z1)
            self.box("trim", X1 - .06, yf - .16, Z0, X1 + .05, yf + .02, Z1)
        w, d = X1 - X0, Z1 - Z0
        y0 = ye - over * h / (min(w, d) / 2)
        if w >= d:
            r = d / 2; a, b = (X0 + r, Z0 + r), (X1 - r, Z0 + r)
            ridge = [(a[0], ye + h, (Z0+Z1)/2), (b[0], ye + h, (Z0+Z1)/2)]
        else:
            r = w / 2
            ridge = [((X0+X1)/2, ye + h, Z0 + r), ((X0+X1)/2, ye + h, Z1 - r)]
        base = [(X0,y0,Z0),(X1,y0,Z0),(X1,y0,Z1),(X0,y0,Z1)]
        if w >= d:
            F = [[base[0], base[1], ridge[1], ridge[0]], [base[1], base[2], ridge[1]],
                 [base[2], base[3], ridge[0], ridge[1]], [base[3], base[0], ridge[0]], base]
        else:
            F = [[base[0], base[1], ridge[0]], [base[1], base[2], ridge[1], ridge[0]],
                 [base[2], base[3], ridge[1]], [base[3], base[0], ridge[0], ridge[1]], base]
        self.solid(mat, F)
    def gambrel(self, mat, wall, x0, x1, z0, z1, ye, h1, h2, knee=.28, over=.4, th=.18, attic=True):
        """Dutch-colonial roof, ridge along X: steep lower slope, shallow upper slope."""
        zc = (z0 + z1) / 2; half = (z1 - z0) / 2
        kz = half * knee
        prof = [(z0 - over, ye - over * 1.6), (z0 + kz, ye + h1), (zc, ye + h1 + h2), (z1 - kz, ye + h1), (z1 + over, ye - over * 1.6)]
        X0, X1 = x0 - over * .5, x1 + over * .5
        for i in range(4):
            (za, ya), (zb, yb) = prof[i], prof[i+1]
            a = [(X0, ya, za), (X1, ya, za), (X1, yb, zb), (X0, yb, zb)]
            b = [(p[0], p[1] + th, p[2]) for p in a]
            self.solid(mat, [a, b] + [[a[j], a[(j+1)%4], b[(j+1)%4], b[j]] for j in range(4)])
        for x in (x0, x1):
            pts = [(x, ye, z0), (x, ye + h1, z0 + kz), (x, ye + h1 + h2, zc), (x, ye + h1, z1 - kz), (x, ye, z1)]
            self.poly(wall, pts, up=(x - (x0 + x1)/2, 0, 0))
        if attic and h2 >= 1.0:                                 # little round window up in the gambrel peak
            for x, sg, key in ((x0, -1, "x0"), (x1, 1, "x1")):
                if attic is True or attic == key: self.xocul(x, sg, zc, ye + h1 + h2 * .3, min(.42, h2 * .3))
        for X, sg in ((X0, -1), (X1, 1)):                      # rake boards along the broken profile
            for i in range(4):
                (za, ya), (zb, yb) = prof[i], prof[i+1]
                a = [(X, ya - .1, za), (X, yb - .1, zb), (X + sg * .1, yb - .1, zb), (X + sg * .1, ya - .1, za)]
                b = [(p[0], p[1] + th + .18, p[2]) for p in a]
                self.solid("trim", [a, b] + [[a[j], a[(j+1)%4], b[(j+1)%4], b[j]] for j in range(4)])
        for (zz, yy), sg in ((prof[0], -1), (prof[4], 1)):     # eave fascia
            self.box("trim", X0, yy - .14, min(zz, zz + sg * .08), X1, yy + th + .02, max(zz, zz + sg * .08))
    def oculus(self, x, y, z, r=.45, trim="trim"):
        """Round window on a +Z facing wall at (x, y, z)."""
        n = 12
        ring = lambda rr, zz: [(x + rr*math.cos(2*math.pi*i/n), y + rr*math.sin(2*math.pi*i/n), zz) for i in range(n)]
        bo, fo = ring(r + .14, z), ring(r + .14, z + .1)
        self.solid(trim, [bo, fo] + [[bo[i], bo[(i+1)%n], fo[(i+1)%n], fo[i]] for i in range(n)])
        self.poly("glass", ring(r, z + .12), up=(0, 0, 1))
        self.box(trim, x - .04, y - r, z + .1, x + .04, y + r, z + .15)
    def shed(self, mat, x0, x1, z0, z1, yback, yfront, th=0.15):
        a = [(x0, yback, z0), (x1, yback, z0), (x1, yfront, z1), (x0, yfront, z1)]
        b = [(p[0], p[1] + th, p[2]) for p in a]
        self.solid(mat, [a, b] + [[a[i], a[(i+1)%4], b[(i+1)%4], b[i]] for i in range(4)])

def _sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def _dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def _avg(P): n = len(P); return (sum(p[0] for p in P)/n, sum(p[1] for p in P)/n, sum(p[2] for p in P)/n)
def _newell(P):
    nx = ny = nz = 0.0
    for i in range(len(P)):
        a, b = P[i], P[(i+1) % len(P)]
        nx += (a[1]-b[1])*(a[2]+b[2]); ny += (a[2]-b[2])*(a[0]+b[0]); nz += (a[0]-b[0])*(a[1]+b[1])
    return (nx, ny, nz)

# --------------------------------------------------------------------------
# 4. Facade parts (windows, doors, porches) — placed on a face of a W x D box
# --------------------------------------------------------------------------
FACE_RY = {"front": 0.0, "back": math.pi, "left": -math.pi/2, "right": math.pi/2}
def face_half(face, W, D): return D/2 if face in ("front", "back") else W/2

def window(m, face, W, D, u, y, w=1.1, h=1.5, trim="trim", shutters=None, arch=False, box=False):
    hd = face_half(face, W, D)
    with m.at(ry=FACE_RY[face]):
        f = .13                                                              # frame width
        m.box(trim, u - w/2 - f, y - f, hd - .02, u + w/2 + f, y + h + f, hd + .03)   # back frame
        for x0, x1 in ((u - w/2 - f, u - w/2), (u + w/2, u + w/2 + f)):       # jambs stand proud
            m.box(trim, x0, y - f, hd + .03, x1, y + h + f, hd + .12)
        m.box(trim, u - w/2 - f, y + h, hd + .03, u + w/2 + f, y + h + f, hd + .12)
        m.box("glass", u - w/2, y, hd + .03, u + w/2, y + h, hd + .05)       # glass sits back
        m.box("glass_lt", u - w/2 + .06, y + h*.62, hd + .05, u - w/2 + .2, y + h - .08, hd + .055)   # glint
        for xm in (u,):
            m.box(trim, xm - .035, y, hd + .05, xm + .035, y + h, hd + .09)   # muntins
        m.box(trim, u - w/2, y + h*.52 - .035, hd + .05, u + w/2, y + h*.52 + .035, hd + .09)
        m.box(trim, u - w/2 - .24, y - .26, hd - .02, u + w/2 + .24, y - .1, hd + .24)   # sill
        m.box(trim, u - w/2 - .26, y + h + f, hd - .02, u + w/2 + .26, y + h + f + .1, hd + .2)   # crown
        m.box(trim + "_dk", u - w/2 - .22, y + h + f + .1, hd - .02, u + w/2 + .22, y + h + f + .16, hd + .15)
        if arch:
            m.cyl(trim, u, y + h + f + .14, hd - .02, w/2 + .1, w/2 + .1, .14, n=10)
        if box:                                                              # window box with flowers
            m.box("door_wd", u - w/2 - .1, y - .62, hd + .02, u + w/2 + .1, y - .28, hd + .42)
            for k in range(int(w / .32) + 1):
                xx = u - w/2 + k * .32
                m.blob("hedge", xx, y - .2, hd + .22, .2, .16, .18, k + u)
                m.blob(box if isinstance(box, str) else "rose", xx + .05, y - .08, hd + .3, .09, .08, .09, k)
        if shutters:
            for sgn in (-1, 1):
                x = u + sgn * (w/2 + .44)
                m.box(shutters, x - .3, y - .04, hd, x + .3, y + h + .04, hd + .09)
                for k in range(1, int(h / .18)):
                    yy = y + k * .18
                    m.box(shutters + "_dk", x - .25, yy - .02, hd + .09, x + .25, yy + .015, hd + .11)

def bay_window(m, face, W, D, u, yb, yt, wall, w=2.6, dep=.85, roof="roof_dk", trim="trim"):
    """Three-sided bay projecting from a wall: angled sides, glass on all three faces, a little hipped cap."""
    hd = face_half(face, W, D)
    with m.at(ry=FACE_RY[face]):
        fw = w * .55
        A, B, C, Dd = (u - w/2, hd - .05), (u - fw/2, hd + dep), (u + fw/2, hd + dep), (u + w/2, hd - .05)
        bot = [(p[0], yb, p[1]) for p in (A, B, C, Dd)]; top = [(p[0], yt, p[1]) for p in (A, B, C, Dd)]
        m.solid(wall, [bot, top] + [[bot[i], bot[i+1], top[i+1], top[i]] for i in range(3)] + [[bot[3], bot[0], top[0], top[3]]])
        gy0, gy1 = yb + .6, yt - .3
        for (P, Q) in ((A, B), (B, C), (C, Dd)):               # glass + frame on each face, pushed out along its normal
            dx, dz = Q[0] - P[0], Q[1] - P[1]; L = math.hypot(dx, dz); nx, nz = dz / L, -dx / L
            if nz < 0: nx, nz = -nx, -nz
            off = lambda q, k: (q[0] + nx * k, q[1] + nz * k)
            pa, pb = (P[0] + dx * .12, P[1] + dz * .12), (P[0] + dx * .88, P[1] + dz * .88)
            fa, fb = off((P[0] + dx * .06, P[1] + dz * .06), .02), off((P[0] + dx * .94, P[1] + dz * .94), .02)
            m.poly(trim, [(fa[0], gy0 - .12, fa[1]), (fb[0], gy0 - .12, fb[1]), (fb[0], gy1 + .12, fb[1]), (fa[0], gy1 + .12, fa[1])], up=(nx, 0, nz))
            ga, gb = off(pa, .04), off(pb, .04)
            m.poly("glass", [(ga[0], gy0, ga[1]), (gb[0], gy0, gb[1]), (gb[0], gy1, gb[1]), (ga[0], gy1, ga[1])], up=(nx, 0, nz))
            ma, mb = off(pa, .06), off(pb, .06); ym = gy0 + (gy1 - gy0) * .66
            m.poly(trim, [(ma[0], ym - .035, ma[1]), (mb[0], ym - .035, mb[1]), (mb[0], ym + .035, mb[1]), (ma[0], ym + .035, ma[1])], up=(nx, 0, nz))
        e = .16
        A2, B2, C2, D2 = (A[0] - e, A[1]), (B[0] - e * .6, B[1] + e), (C[0] + e * .6, C[1] + e), (Dd[0] + e, Dd[1])
        for y0, y1 in ((yt, yt + .14), (yb + .45, yb + .55)):     # cornice and sill bands
            lo = [(p[0], y0, p[1]) for p in (A2, B2, C2, D2)]; hi = [(p[0], y1, p[1]) for p in (A2, B2, C2, D2)]
            m.solid(trim, [lo, hi] + [[lo[i], lo[(i+1)%4], hi[(i+1)%4], hi[i]] for i in range(4)])
        yr = yt + .14 + .8; T1, T2 = (A2[0], yr, A2[1]), (D2[0], yr, D2[1])
        b2 = [(p[0], yt + .14, p[1]) for p in (A2, B2, C2, D2)]
        m.solid(roof, [b2, [b2[0], b2[1], T1], [b2[1], b2[2], T2, T1], [b2[2], b2[3], T2], [b2[3], b2[0], T1, T2]])

def door(m, face, W, D, u, w=1.15, h=2.3, mat="door_rd", y=0.45, trim="trim", glass_top=True, lamps=True):
    hd = face_half(face, W, D)
    with m.at(ry=FACE_RY[face]):
        m.box(trim, u - w/2 - .2, y, hd - .02, u + w/2 + .2, y + h + .22, hd + .1)
        m.box(trim, u - w/2 - .32, y + h + .22, hd - .02, u + w/2 + .32, y + h + .36, hd + .2)    # pediment cap
        m.box(mat, u - w/2, y, hd + .06, u + w/2, y + h, hd + .11)
        for (py, ph) in ((.25, .8), (1.25, .85)):                                          # raised panels
            for sx in (-1, 1):
                m.box(mat + "_lt", u + sx * w/4 - w/5, y + py, hd + .11, u + sx * w/4 + w/5, y + py + ph, hd + .14)
        if glass_top:
            m.box("glass", u - w/2 + .05, y + h + .02, hd + .05, u + w/2 - .05, y + h + .2, hd + .08)
        m.cyl("brass", u + w/2 - .17, y + h*.47, hd + .12, .05, .05, .06, n=6)
        if lamps:
            for sx in (-1, 1):
                x = u + sx * (w/2 + .48)
                m.box("black", x - .08, y + h*.62, hd, x + .08, y + h*.62 + .4, hd + .14)
                m.box("lamp", x - .1, y + h*.62 + .06, hd + .14, x + .1, y + h*.62 + .36, hd + .3)
                m.cyl("black", x, y + h*.62 + .36, hd + .22, .14, 0, .18, n=4, rot=math.pi/4)

def porch(m, x0, x1, z0, depth, y=0.45, cols=4, col_mat="trim", roof="hip", roof_mat="roof_dk",
          rail=True, h=2.7, steps_u=None, deck="board"):
    z1 = z0 + depth
    m.box(deck, x0, 0, z0, x1, y, z1)
    if y > .35:                                       # white lattice under the porch deck
        m.box("trim", x0, y - .1, z1 - .02, x1, y, z1 + .04)
        n = int((x1 - x0) / .32)
        for k in range(n + 1):
            xx = x0 + (x1 - x0) * k / n
            m.box("trim_dk", xx - .02, .02, z1, xx + .02, y - .1, z1 + .03)
        m.box("trim_dk", x0, y * .45, z1, x1, y * .45 + .03, z1 + .03)
    for i in range(cols):
        x = x0 + .25 + (x1 - x0 - .5) * i / max(cols - 1, 1)
        m.cyl(col_mat, x, y, z1 - .3, .16, .13, h, n=8)
        m.cbox(col_mat, x, y, z1 - .3, .42, .22, .42)
        m.cbox(col_mat, x, y + h - .2, z1 - .3, .4, .2, .4)
    if rail:
        for zz in (z1 - .3,):
            for a, b in ((x0 + .25, (steps_u or 0) - .9), ((steps_u or 0) + .9, x1 - .25)):
                if b > a:
                    m.box(col_mat, a, y + .8, zz - .05, b, y + .9, zz + .05)
                    k = int((b - a) / .35)
                    for j in range(k + 1):
                        xx = a + (b - a) * j / max(k, 1)
                        m.box(col_mat, xx - .03, y, zz - .03, xx + .03, y + .85, zz + .03)
    if roof == "hip":
        m.hip(roof_mat, x0, x1, z0 - .1, z1, y + h, .9, over=.3)
    elif roof == "shed":
        m.shed(roof_mat, x0 - .3, x1 + .3, z0 - .1, z1 + .35, y + h + .8, y + h, th=.15)
    elif roof == "flat":
        m.box(roof_mat, x0 - .2, y + h, z0 - .1, x1 + .2, y + h + .35, z1 + .2)
        m.box("trim", x0 - .25, y + h + .35, z0 - .1, x1 + .25, y + h + .5, z1 + .25)
    su = steps_u if steps_u is not None else (x0 + x1) / 2
    for k in range(3):
        m.box("stone", su - .9, 0, z1 + k * .32, su + .9, y - k * .15, z1 + (k + 1) * .32)

def chimney(m, x, z, y0, h, mat="brick", w=.9, d=.9):
    m.cbox(mat, x, y0, z, w, h, d)
    m.cbox(mat + "_dk", x, y0 + h - .55, z, w + .14, .14, d + .14)
    m.cbox(mat, x, y0 + h, z, w + .22, .2, d + .22)
    m.cbox("stone", x, y0 + h + .2, z, w + .1, .08, d + .1)
    for k, sx in enumerate((-.2, .2) if w > .8 else (0,)):
        m.cyl("terracotta", x + sx, y0 + h + .28, z, .12, .1, .38 + .08 * k, n=6)

def foundation(m, W, D, h=0.45, mat="stone"):
    m.cbox(mat, 0, 0, 0, W + .2, h, D + .2)

NO_SIDING = {"brick", "stone", "darkgrey"}
def walls(m, W, D, y0, h, mat, siding=True, back=True):
    m.cbox(mat, 0, y0, 0, W, h, D)
    if back and h > 2.4:                       # the back facade is seen from the overview too
        n = max(2, int(W / 3.0)); ys = [y0 + .85] + ([y0 + 3.55] if h > 5 else [])
        for y in ys:
            for k in range(n):
                u = -W/2 + W * (k + .5) / n
                window(m, "back", W, D, u, y, 1.0, 1.45 if y == ys[0] else 1.3)
    if siding and mat not in NO_SIDING:
        clapboard(m, W, D, y0, h, mat)
        for sx in (-1, 1):
            for sz in (-1, 1):
                x, z = sx * W/2, sz * D/2
                m.box("trim", x - .14 if sx > 0 else x - .04, y0, z - .14 if sz > 0 else z - .04,
                      x + .04 if sx > 0 else x + .14, y0 + h, z + .04 if sz > 0 else z + .14)

def clapboard(m, W, D, y0, h, mat, step=.42):
    """Horizontal lap-siding lines on all four faces (cheap, reads well from above)."""
    k = int(h / step)
    for i in range(1, k):
        y = y0 + i * step
        m.box(mat + "_dk", -W/2 - .04, y - .03, D/2, W/2 + .04, y + .02, D/2 + .04)
        m.box(mat + "_dk", -W/2 - .04, y - .03, -D/2 - .04, W/2 + .04, y + .02, -D/2)
        m.box(mat + "_dk", W/2, y - .03, -D/2, W/2 + .04, y + .02, D/2)
        m.box(mat + "_dk", -W/2 - .04, y - .03, -D/2, -W/2, y + .02, D/2)

def band(m, W, D, y, mat="trim", t=.18):
    m.cbox(mat, 0, y, 0, W + .12, t, D + .12)

# --------------------------------------------------------------------------
# 5. Yard kit: trees, hedges, fences, mailbox, cars
# --------------------------------------------------------------------------
def _jag_cone(m, mat, x, y, z, r, h, n=10, rot=0.0, droop=.28):
    """Spruce tier: a star-shaped skirt (alternating long/short points) drooping into a cone."""
    pts = []
    for i in range(n * 2):
        a = rot + math.pi * i / n; rr = r if i % 2 == 0 else r * .62
        pts.append((x + rr * math.cos(a), y - (droop * r if i % 2 == 0 else 0), z + rr * math.sin(a)))
    ap = (x, y + h, z)
    for i in range(len(pts)):
        m.poly(mat, [pts[i], pts[(i + 1) % len(pts)], ap], up=(pts[i][0] - x, .4, pts[i][2] - z))
    m.poly(mat + "_dk", list(reversed(pts)), up=(0, -1, 0))

def _crown(m, x, y, z, r, seed, mats=("leaf", "leaf2", "leaf_lt")):
    """Rounded broadleaf crown: a central dome and a ring of smaller puffs in three greens."""
    m.blob(mats[0], x, y, z, r, r * .85, r, seed)
    k = 5
    for i in range(k):
        a = seed * 1.3 + i * 2 * math.pi / k
        rr = r * (.55 + .12 * math.sin(seed + i * 2.1))
        m.blob(mats[1 + i % 2], x + math.cos(a) * r * .72, y - r * .18 + (i % 2) * r * .3, z + math.sin(a) * r * .72, rr, rr * .85, rr, seed + i * 1.7)
    m.blob(mats[2], x - r * .15, y + r * .62, z + r * .1, r * .55, r * .45, r * .55, seed + 9)

def _trunk(m, x, z, s, h, lean=0.0, mat="trunk"):
    m.cyl(mat, x, 0, z, .3 * s, .2 * s, h * .55, n=6)
    m.cyl(mat, x + lean * .5, h * .55, z, .2 * s, .13 * s, h * .45, n=6)
    for i in range(3):                                     # root flare
        a = i * 2.1 + x
        m.cyl(mat + "_dk", x + math.cos(a) * .25 * s, 0, z + math.sin(a) * .25 * s, .16 * s, .05 * s, .35 * s, n=4, rot=a)

def tree(m, x, z, s=1.0, kind="leaf", seed=0.0):
    lean = .4 * math.sin(seed * 3.1)
    _trunk(m, x, z, s, 2.8 * s, lean)
    for i, a in enumerate((seed, seed + 2.3)):          # two side branches
        m.cyl("trunk", x + lean * .3, 1.9 * s, z, .1 * s, .05 * s, 1.3 * s, n=4, rot=a)
    mats = ("wisteria", "wisteria2", "wisteria2") if kind == "wisteria" else (("oak", "oak_lt", "leaf_lt") if kind == "leaf2" else ("leaf", "leaf2", "leaf_lt"))
    _crown(m, x + lean, 3.9 * s, z, 1.9 * s, seed, mats)

def wisteria_tree(m, x, z, s=1.0, seed=0.0):
    m.cyl("trunk", x, 0, z, .2*s, .12*s, 2.2*s, n=6)
    m.blob("leaf", x, 3.0*s, z, 1.8*s, 1.3*s, 1.8*s, seed)
    for i in range(7):
        a = i * 0.9 + seed
        px, pz = x + 1.5*s*math.cos(a), z + 1.5*s*math.sin(a)
        m.cyl("wisteria" if i % 2 else "wisteria2", px, 1.6*s, pz, .05, .38*s, 1.3*s, n=6, rot=a)

def hedge(m, x0, z0, x1, z1, h=.9, mat="hedge"):
    m.box(mat, min(x0, x1), 0, min(z0, z1), max(x0, x1), h, max(z0, z1))

def picket(m, x0, x1, z, h=.95, step=.32, mat="trim"):
    m.box(mat, x0, .45, z - .04, x1, .55, z + .04)
    m.box(mat, x0, .75, z - .04, x1, .85, z + .04)
    n = int(abs(x1 - x0) / step)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / max(n, 1)
        m.box(mat, x - .05, 0, z - .03, x + .05, h, z + .03)
        m.poly(mat, [(x - .05, h, z + .03), (x + .05, h, z + .03), (x, h + .1, z + .03)], up=(0, 0, 1))

def flowerbed(m, x0, x1, z, mat="rose"):
    m.box("soil", x0, 0, z - .45, x1, .12, z + .45)
    n = int((x1 - x0) / .7)
    for i in range(n):
        x = x0 + .35 + i * .7
        m.blob("hedge", x, .4, z, .38, .32, .38, i)
        m.blob(mat, x + .1, .62, z + .1, .16, .14, .16, i + 2)

def car(m, x, z, ry=0.0, mat="car_bl"):
    with m.at(x, 0, z, ry):
        m.cbox(mat, 0, .35, 0, 1.8, .7, 4.3)
        m.frustum(mat, -.85, -1.2, .85, 1.0, 1.05, .1, 1.7)
        m.frustum("glass", -.88, -1.1, .88, .9, 1.06, .16, 1.62)
        for sx in (-.92, .92):
            for sz in (-1.35, 1.35):
                with m.at(sx, .36, sz, 0):
                    m.push(ry=math.pi/2)
                    m.cyl("black", 0, -.12, 0, .36, .36, .24, n=8)
                    m.pop()
        m.cbox("lamp", -.55, .55, 2.16, .35, .18, .05); m.cbox("lamp", .55, .55, 2.16, .35, .18, .05)

def lamp_post(m, x, z):
    m.cyl("black", x, 0, z, .09, .07, 3.6, n=6)
    m.cyl("lamp", x, 3.6, z, .22, .3, .45, n=6)
    m.cyl("black", x, 4.05, z, .34, 0, .25, n=6)

# --------------------------------------------------------------------------
# 6. Moving details (each is its own mesh with its own pivot)
# --------------------------------------------------------------------------
def d_mailbox(post_x, post_z):
    """Returns (static part builder, detail mesh, pivot). The flag swings up."""
    flag = Mesh("flag")
    flag.box("red", -.02, 0, -.02, .02, .45, .02)
    flag.box("red", -.02, .3, -.02, .03, .45, .25)
    return flag

def mailbox_static(m, x, z, mat="white"):
    m.cbox("trunk", x, 0, z, .14, 1.0, .14)
    m.cbox(mat, x, 1.0, z, .45, .45, .75)
    m.cyl(mat, x, 1.45, z - .37, .22, .22, .74, n=8, rot=0) if False else None

def make_detail(kind):
    d = Mesh(kind)
    if kind == "flag":                    # mailbox flag, pivot at its hinge
        d.box("red", -.03, -.05, -.03, .03, .45, .03)
        d.box("red", -.03, .25, -.03, .04, .45, .3)
    elif kind == "door":                  # pivot at the hinge, opens outward
        d.box("door_bl", 0, 0, -.03, 1.15, 2.3, .03)
        d.cyl("glass", .575, 2.3, -.03, .5, .5, .06, n=8)
        d.box("metal", .95, 1.0, .03, 1.05, 1.1, .1)
    elif kind == "vane":                  # weathervane: arrow spins on the post
        d.box("black", -.9, 0, -.04, .9, .06, .04)
        d.poly("black", [(.9, -.02, 0), (.9, .14, 0), (1.25, .06, 0)], up=(0, 0, 1))
        d.poly("black", [(.9, -.02, 0), (.9, .14, 0), (1.25, .06, 0)], up=(0, 0, -1))
        d.box("black", -1.0, -.12, -.03, -.75, .25, .03)
        d.cyl("metal", 0, -.1, 0, .09, .09, .2, n=6)
    elif kind == "swing":                 # tyre swing: hangs from the branch pivot
        d.box("black", -.02, -2.4, -.02, .02, 0, .02)
        with d.at(0, -2.6, 0):
            d.push(ry=0)
            for i in range(10):
                a0, a1 = 2*math.pi*i/10, 2*math.pi*(i+1)/10
                d.solid("black", _ring_seg(a0, a1, .38, .2, .22))
            d.pop()
    elif kind == "sprinkler":             # lawn sprinkler arms rotate
        d.cyl("metal", 0, 0, 0, .05, .05, .35, n=6)
        d.box("metal", -.55, .3, -.03, .55, .36, .03)
        d.cyl("water", .6, .2, 0, .05, .12, .3, n=6); d.cyl("water", -.6, .2, 0, .05, .12, .3, n=6)
    elif kind == "rocker":                # rocking chair on the porch
        for s in (-.3, .3):
            d.solid("door_wd", [[(s-.03, .0, -.5), (s+.03, .0, -.5), (s+.03, .08, .5), (s-.03, .08, .5)],
                                [(s-.03, .08, -.5), (s+.03, .08, -.5), (s+.03, .16, .5), (s-.03, .16, .5)]])
        d.box("door_wd", -.32, .45, -.3, .32, .52, .3)
        d.box("door_wd", -.32, .5, -.32, .32, 1.25, -.26)
        for s in (-.3, .3):
            d.box("door_wd", s - .03, .1, -.3, s + .03, .5, -.24); d.box("door_wd", s - .03, .1, .24, s + .03, .5, .3)
    elif kind == "sign":                  # realtor sign swings under its arm
        d.box("black", -.02, -.15, -.02, .02, 0, .02); d.box("black", .58, -.15, -.02, .62, 0, .02)
        d.box("sign", -.05, -.85, -.04, .65, -.15, .04)
        d.box("red", -.05, -.35, .04, .65, -.15, .06)
    elif kind == "pennant":               # flag on a pole
        d.solid("red", [[(0, 0, -.01), (1.1, -.3, -.01), (0, -.6, -.01)], [(0, 0, .01), (1.1, -.3, .01), (0, -.6, .01)]])
    return d

def _ring_seg(a0, a1, R, r, h):
    pts = []
    for a in (a0, a1):
        for rr, yy in ((R, -h/2), (R + r, -h/2), (R + r, h/2), (R, h/2)):
            pts.append((rr * math.cos(a), yy, rr * math.sin(a)))
    a, b = pts[:4], pts[4:]
    return [a, b] + [[a[i], a[(i+1)%4], b[(i+1)%4], b[i]] for i in range(4)]

# --------------------------------------------------------------------------
# 7. The houses
# --------------------------------------------------------------------------
class House:
    def __init__(self, hid):
        self.id = hid
        self.body = Mesh(hid + "_body")
        self.details = []   # (kind, Mesh, (px,py,pz), rest_ry)
    def detail(self, kind, pivot, ry=0.0):
        self.details.append((kind, make_detail(kind), pivot, ry))

# ---- garden dressing
def birdbath(m, x, z):
    m.cyl("stone", x, 0, z, .35, .2, .2, n=8); m.cyl("stone", x, .2, z, .14, .12, .7, n=8)
    m.cyl("stone", x, .9, z, .3, .55, .18, n=10); m.cyl("water", x, 1.0, z, .45, .45, .1, n=10)

def planter(m, x, z, flower="rose"):
    m.cyl("terracotta", x, 0, z, .3, .4, .5, n=8)
    m.blob("hedge", x, .7, z, .38, .3, .38, x + z); m.blob(flower, x + .1, .9, z, .18, .14, .18, x)

def gnome(m, x, z, ry=0.0):
    with m.at(x, 0, z, ry):
        m.cyl("door_bl", 0, 0, 0, .16, .12, .3, n=6); m.blob("white", 0, .38, .04, .1, .12, .08, 1)
        m.blob("blush", 0, .48, .06, .07, .07, .07, 2); m.cyl("red", 0, .52, 0, .12, 0, .32, n=6)

def bench(m, x, z, ry=0.0):
    with m.at(x, 0, z, ry):
        for sx in (-.75, .75): m.box("black", sx - .05, 0, -.25, sx + .05, .45, .25)
        for k in range(3): m.box("door_wd", -.9, .45, -.25 + k * .17, .9, .5, -.13 + k * .17)
        for k in range(2): m.box("door_wd", -.9, .62 + k * .2, -.3, .9, .75 + k * .2, -.24)

def wheelbarrow(m, x, z, ry=0.0):
    with m.at(x, 0, z, ry):
        m.frustum("car_rd", -.35, -.5, .35, .4, .3, -.08, .65); m.cyl("black", 0, .1, .55, .15, .15, .1, n=8)
        for sx in (-.25, .25): m.box("door_wd", sx - .03, .3, -.5, sx + .03, .36, -1.1)
        m.blob("soil", 0, .62, 0, .28, .1, .35, 3)

def wildflowers(m, x, z, n=7, seed=0.0, cols=("flower_y", "white", "wisteria", "rose")):
    for k in range(n):
        a = seed * 2.3 + k * 2.4; r = .3 + (k % 4) * .35
        px, pz = x + r * math.cos(a), z + r * math.sin(a)
        m.blob("hedge_lt", px, .18, pz, .22, .18, .22, seed + k + 5)
        m.blob(cols[(k + int(seed)) % len(cols)], px, .42 + (k % 2) * .12, pz, .17, .12, .17, seed + k)

def pebbles(m, x, z, seed=0.0):
    for k in range(4):
        a = seed + k * 1.7
        m.blob("rock_lt" if k % 2 else "rock", x + math.cos(a) * .5, .08, z + math.sin(a) * .4, .2 + .05 * (k % 3), .12, .18, seed + k)

GARDEN = [birdbath, planter, gnome, bench, wheelbarrow]

def _lot_world(hid):
    for e in PLAN:
        if e[0] == hid: return e[1], e[2], e[3]
    return 0.0, 0.0, 0.0

def _clear_fn(hid):
    """f(lx, lz, margin) -> True when the house-local point stays off the sidewalk/road (by `margin` metres)."""
    X, Z, Rr = _lot_world(hid); c, sn = math.cos(Rr), math.sin(Rr); edge = ROAD_W / 2 + .25 + WALK_W
    def f(lx, lz, margin=0.3):
        return dist_main(X + lx * c + lz * sn, Z - lx * sn + lz * c) >= edge + margin
    return f

def _clip_back(ok, x, z0, z1, margin, step=.4):
    """Pull the far end z1 back toward z0 until the point is clear."""
    while z1 > z0 and not ok(x, z1, margin): z1 -= step
    return z1

PUMPKINS = []   # world spots for the site's Halloween pumpkins: [x, z, scale, carved]

def yard(h, W, D, walk_u=0.0, lot_w=22.0, fence=False, hedges=True, drive_side=1, car_mat=None,
         trees=(), mailbox=True, flowers="rose", lot_front=None):
    m = h.body
    zf = D / 2
    if lot_front is None: lot_front = SET_Z - (ROAD_W / 2 + .25 + WALK_W) - D / 2
    # mown front lawn: alternating stripes, like the reference renders
    L0, L1 = -lot_w/2 + 1.4, lot_w/2 - 1.0
    z = zf + .3; k = 0
    ok = _clear_fn(h.id)
    while z < zf + lot_front - .4:
        z2 = min(z + 1.5, zf + lot_front - .4)
        x = L0
        while x < L1 - .01:
            x2 = min(x + 1.5, L1)
            if ok(x, z2, .15) and ok(x2, z2, .15):
                m.poly("lawn_lt" if k % 2 else "lawn", [(x, .025, z), (x2, .025, z), (x2, .025, z2), (x, .025, z2)], up=(0, 1, 0))
            x = x2
        z = z2; k += 1
    # front walkway to the sidewalk, laid as pavers
    m.box("walk", walk_u - .7, 0, zf, walk_u + .7, .06, zf + lot_front)
    zz = zf + .6
    while zz < zf + lot_front - .3:
        m.box("walk_dk", walk_u - .7, .06, zz, walk_u + .7, .075, zz + .06); zz += .9
    # driveway along one side, to the road
    dx = drive_side * (lot_w / 2 - 2.6)
    zd = zf + lot_front + WALK_W + .25
    zd = min(_clip_back(ok, dx - 1.6, zf, zd, -WALK_W - .25), _clip_back(ok, dx + 1.6, zf, zd, -WALK_W - .25))
    m.box("drive", dx - 1.6, 0, -D/2 + 1, dx + 1.6, .05, zd)
    if car_mat:
        car(m, dx, zf + 3.2, 0.0, car_mat)
    def fence_run(x0, x1, z):
        a, b = min(x0, x1), max(x0, x1); xs = [a + (b - a) * i / 24 for i in range(25)]
        run = None
        for x in xs + [None]:
            good = x is not None and ok(x, z, .5)
            if good and run is None: run = x
            if not good and run is not None:
                end = xs[xs.index(x) - 1] if x is not None else b
                if end - run > .6: picket(m, run, end, z)
                run = None
    if fence:
        fence_run(-lot_w/2 + .4, walk_u - .9, zf + lot_front - .7)
        fence_run(walk_u + .9, dx - 1.9, zf + lot_front - .7)
    if hedges:
        hx0, hx1 = -lot_w/2 + .5, -lot_w/2 + 1.3
        hz = min(_clip_back(ok, hx0, -D/2, zf + lot_front - 1.5, .6), _clip_back(ok, hx1, -D/2, zf + lot_front - 1.5, .6))
        if hz > -D/2 - 4 + 1: hedge(m, hx0, -D/2 - 4, hx1, hz)
    if flowers:
        flowerbed(m, -W/2 + .2, walk_u - 1.4, zf + .9, flowers)
        if W/2 - .2 - (walk_u + 1.4) > 1.5: flowerbed(m, walk_u + 1.4, W/2 - .2, zf + .9, flowers)
    for k in range(int(W / 1.4)):                    # clipped boxwood along the foundation
        x = -W/2 + .7 + k * 1.4
        if abs(x - walk_u) < 1.6: continue
        m.blob("hedge" if k % 3 else "hedge_lt", x, .55, zf + .45, .72, .6, .55, k * 2.3 + W)
    for sx in (-1, 1):   # rounded shrubs at the front corners
        bush(m, sx * (W/2 + .8), zf - .3, 1.05, sx * 3.1 + W, "rose" if sx > 0 else None)
        grass(m, sx * (W/2 + 1.9), zf + .9, sx + W)
    for (x, z, s, k) in trees:
        if k == "wisteria": wisteria_tree(m, x, z, s, seed=x * .37 + z)
        else: tree(m, x, z, s, k, seed=x * .37 + z)
    # garden life: tufts and flowers across the lawn, a couple of props, pebbles by the walk
    seed = W * 3.1 + D * 1.7 + walk_u
    for k in range(9):
        gx = -lot_w/2 + 2 + ((k * 4.7 + seed * 2.3) % (lot_w - 4))
        gz = zf + 1.5 + ((k * 2.9 + seed) % max(1.0, lot_front - 3))
        if abs(gx - walk_u) < 1.3 or abs(gx - dx) < 2.2: continue
        grass(m, gx, gz, seed + k) if k % 3 else wildflowers(m, gx, gz, seed=seed + k)
    k0 = int(seed) % len(GARDEN)
    GARDEN[k0](m, -W/2 - 1.6, zf + 2.4)
    GARDEN[(k0 + 2) % len(GARDEN)](m, W/2 + 1.4, zf + 1.8)
    planter(m, walk_u - 1.1, zf + .6); planter(m, walk_u + 1.1, zf + .6, "flower_y")
    pebbles(m, walk_u + 1.3, zf + lot_front * .55, seed)
    for k in range(3):                              # back garden: a bush and flowers
        bush(m, -W/2 + 1 + k * (W - 2) / 2, -D/2 - 3.2, .8, seed + k * 4, ("berry", None, "rose")[k])
    # Halloween: a few pumpkins by the walk and on the lawn (the site shows them in autumn)
    X, Z, Rr = _lot_world(h.id); cR, sR = math.cos(Rr), math.sin(Rr); k0p = int(abs(W * 7 + D * 3 + walk_u * 11))
    for i, (lx, lz, sc, carved) in enumerate(((walk_u - 1.15, zf + 3.3, 1.0, 1), (walk_u - 1.55, zf + 3.9, .7, 0), (walk_u + 1.2, zf + 3.5, .85, (k0p % 2)),
                                             (walk_u + 1.15, zf + lot_front - 1.3, .75, 0), (-W/2 - .6, zf + 1.9, 1.15, (k0p // 2) % 2))):
        if h.id == "4344" and i > 1: continue
        if not ok(lx, lz, .6) or abs(lx - dx) < 2.0: continue
        PUMPKINS.append([round(X + lx * cR + lz * sR, 2), round(Z - lx * sR + lz * cR, 2), sc, carved])
    if mailbox and ok(walk_u + 1.4, zf + lot_front - .5, .3):
        mx = walk_u + 1.4
        m.cbox("trunk", mx, 0, zf + lot_front - .5, .14, 1.0, .14)
        m.cbox("white", mx, 1.0, zf + lot_front - .5, .45, .42, .7)
        h.detail("flag", (mx + .26, 1.15, zf + lot_front - .6))

def rail(m, x0, x1, z, mat="trim"):
    """Two-rail ranch fence, like the one in front of Susan's lawn."""
    m.box(mat, x0, .55, z - .05, x1, .68, z + .05); m.box(mat, x0, .95, z - .05, x1, 1.08, z + .05)
    n = max(1, int(abs(x1 - x0) / 2.4))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        m.box(mat, x - .09, 0, z - .09, x + .09, 1.25, z + .09)


def h4349():  # Solis — yellow Victorian: dark mansard, centre gable with an oculus, wraparound porch with a balcony
    h = House("4349"); m = h.body; W, D = 12.5, 10.0
    foundation(m, W, D, .6); walls(m, W, D, .6, 6.2, "gaby")
    band(m, W, D, 3.6, "trim", .16); band(m, W, D, 6.8, "trim", .28)
    m.frustum("roof_dk", -W/2 - .35, -D/2 - .35, W/2 + .35, D/2 + .35, 7.05, .85, 9.9, insz=.85)
    m.box("trim", -W/2 + .45, 9.9, -D/2 + .45, W/2 - .45, 10.02, D/2 - .45)
    m.hip("roof_slate", -W/2 + .5, W/2 - .5, -D/2 + .5, D/2 - .5, 10.0, .9, over=.05)
    for x in (-W/2 + .55, W/2 - .55):          # iron cresting finials
        for z in (-D/2 + .55, D/2 - .55): m.cyl("black", x, 10.0, z, .07, 0, .7, n=4)
    for u in (-4.0, 4.0):                       # mansard dormers
        with m.at(u, 7.4, D/2 - .2):
            m.cbox("gaby", 0, 0, 0, 1.5, 1.7, 1.3)
            m.push(ry=math.pi/2); m.gable("roof_dk", "gaby", -.65, .65, -.75, .75, 1.7, 2.4, over=.12); m.pop()
            m.box("trim", -.5, .25, .62, .5, 1.45, .68); m.box("glass", -.38, .35, .66, .38, 1.35, .74)
    # centre gable that rises through the mansard, with an oculus and an arched window
    with m.at(0, 0, D/2 + .4):
        m.cbox("gaby", 0, .6, 0, 4.2, 8.4, 1.0)
        clapboard(m, 4.2, 1.0, .6, 8.4, "gaby")
        m.push(ry=math.pi/2); m.gable("roof_dk", "gaby", -.5, .5, -2.3, 2.3, 9.0, 11.2, over=.25); m.pop()
        m.oculus(0, 9.9, .52, .42)
        m.box("trim", -.95, 4.1, .48, .95, 6.4, .56); m.box("glass", -.8, 4.2, .52, .8, 6.3, .62)
        m.cyl("trim", 0, 6.35, .48, 1.0, 1.0, .1, n=12)
        m.box("board", -1.4, 4.0, .5, 1.4, 4.12, 1.4)          # little balcony
        for x in (-1.35, -.7, 0, .7, 1.35): m.box("trim", x - .04, 4.12, 1.3, x + .04, 4.85, 1.38)
        m.box("trim", -1.4, 4.8, 1.28, 1.4, 4.9, 1.4)
    for u in (-4.3, -2.6, 2.6, 4.3):
        window(m, "front", W, D, u, 4.2, .9, 1.7, arch=True)
    for f in ("left", "right"):
        for u in (-2.5, 2.5): window(m, f, W, D, u, 1.5, 1.0, 1.9, arch=True); window(m, f, W, D, u, 4.2, 1.0, 1.7, arch=True)
    bay_window(m, "right", W, D, 0, .6, 3.4, "gaby")
    # wraparound porch: front + left side, flat roof with a white balustrade on top
    py, ph = .6, 2.75
    m.box("board", -W/2 - 2.6, 0, D/2, W/2 + .4, py, D/2 + 3.2)
    m.box("board", -W/2 - 2.6, 0, -D/2 + 1.0, -W/2, py, D/2)
    cols = [(-W/2 - 2.3 + i * 2.4, D/2 + 2.9) for i in range(7)] + [(-W/2 - 2.3, D/2 + 2.9 - i * 2.6) for i in range(1, 5)]
    for x, z in cols:
        m.cyl("trim", x, py, z, .16, .13, ph, n=8)
        m.blob("hedge", x, py + 1.3, z + .05, .32, .9, .3, x + z)     # climbing roses on the posts
        m.blob("rose", x + .1, py + 1.9, z + .2, .14, .14, .14, x)
    m.box("trim", -W/2 - 2.7, py + ph, D/2 - .05, W/2 + .5, py + ph + .3, D/2 + 3.3)
    m.box("trim", -W/2 - 2.7, py + ph, -D/2 + .9, -W/2, py + ph + .3, D/2)
    rx0, rx1, rz = -W/2 - 2.6, W/2 + .4, D/2 + 3.2
    m.box("trim", rx0, py + ph + 1.05, rz - .1, rx1, py + ph + 1.15, rz)
    k = int((rx1 - rx0) / .5)
    for i in range(k + 1):
        x = rx0 + (rx1 - rx0) * i / k; m.box("trim", x - .04, py + ph + .3, rz - .08, x + .04, py + ph + 1.1, rz - .02)
    for k in range(3): m.box("stone", 1.6 - 1.0, 0, D/2 + 3.2 + k * .32, 1.6 + 1.0, py - k * .2, D/2 + 3.52 + k * .32)
    door(m, "front", W, D + 0.8, 1.6, mat="door_wd", y=py)
    window(m, "front", W, D, -3.8, 1.5, 1.6, 1.9)
    window(m, "front", W, D, 4.4, 1.5, 1.2, 1.9)
    chimney(m, 3.8, -2.6, 8.6, 2.6, "brick")
    # gate pillars with lanterns at the street
    zf = SET_Z - (ROAD_W / 2 + .25 + WALK_W) - .6
    for x in (.6, 2.6):
        m.cbox("trim", x, 0, zf, .45, 1.2, .45); m.cyl("lamp", x, 1.2, zf, .18, .22, .35, n=6)
    yard(h, W, D + 6.4, 1.6, lot_w=25, fence=False, car_mat="car_rd", flowers="flower_y",
         trees=[(-10, 4, 1.15, "leaf"), (10, -6, 1.0, "leaf")])
    h.detail("sprinkler", (-5.5, .05, D/2 + 5.2))
    return h


def h4354():  # Van de Kamp — brick ground floor, blue gambrel upper storey with dormers, tall chimney
    h = House("4354"); m = h.body; W, D = 13.0, 9.5
    foundation(m, W, D, .45); walls(m, W, D, .45, 3.2, "brick")
    for y in (1.2, 2.2, 3.1): m.box("brick_dk", -W/2 - .03, y, D/2, W/2 + .03, y + .05, D/2 + .03)
    band(m, W, D, 3.65, "trim", .22)
    m.gambrel("roof_slate", "blueboard", -W/2, W/2, -D/2, D/2, 3.87, 3.4, 1.6, knee=.24, over=.35, attic="x1")
    for u in (-4.0, 0.0, 4.0):                  # three dormers in the steep lower slope
        with m.at(u, 4.3, D/2 - 1.2):
            m.cbox("blueboard", 0, 0, 0, 2.0, 2.3, 2.2)
            clapboard(m, 2.0, 2.2, 0, 2.3, "blueboard")
            m.push(ry=math.pi/2); m.gable("roof_slate", "blueboard", -1.1, 1.1, -1.0, 1.0, 2.3, 3.1, over=.15); m.pop()
            m.box("trim", -.6, .35, 1.08, .6, 1.9, 1.14); m.box("glass", -.48, .45, 1.12, .48, 1.8, 1.2)
            for sx in (-.95, .95): m.box("shutter_bk", sx - .2, .35, 1.08, sx + .2, 1.9, 1.16)
    for u in (-4.5, -2.0, 2.0, 4.5):
        window(m, "front", W, D, u, 1.25, 1.1, 1.75, shutters="shutter_bk")
    for f in ("left", "right"):
        for u in (-2, 2): window(m, f, W, D, u, 1.25, 1.0, 1.6)
        window(m, f, W, D, 0, 5.4, 1.0, 1.3)
    # pedimented portico with a fanlight
    m.box("board", -1.7, 0, D/2, 1.7, .45, D/2 + 1.9)
    for x in (-1.35, 1.35): m.cyl("trim", x, .45, D/2 + 1.6, .18, .15, 2.9, n=10)
    with m.at(0, 0, D/2 + .95):
        m.push(ry=math.pi/2); m.gable("trim", "trim", -1.0, 1.0, -1.7, 1.7, 3.35, 4.35, over=.15); m.pop()
    door(m, "front", W, D, 0, mat="door_rd")
    m.cyl("glass", 0, 2.95, D/2 + .05, .62, .62, .1, n=12)
    for k in range(3): m.box("stone", -1.1, 0, D/2 + 1.9 + k * .32, 1.1, .45 - k * .15, D/2 + 2.22 + k * .32)
    # tall brick chimney on the gable end, like the aerial photo
    m.cbox("brick", -W/2 - .45, 0, .5, 1.3, 10.6, 1.7); m.cbox("brick", -W/2 - .45, 10.6, .5, 1.6, .3, 2.0)
    for y in (3.9, 7.0): m.cbox("brick_dk", -W/2 - .45, y, .5, 1.42, .14, 1.82)
    # side garage wing
    with m.at(W/2 + 2.7, 0, -.4):
        m.cbox("brick", 0, 0, 0, 5.2, 3.0, 7.5)
        m.push(ry=math.pi/2); m.gable("roof_slate", "blueboard", -3.75, 3.75, -2.6, 2.6, 3.0, 4.7, over=.3); m.pop()
        m.box("trim", -2.1, 0, 3.75, 2.1, 2.4, 3.85); m.box("grey", -1.95, 0, 3.8, 1.95, 2.3, 3.9)
        for y in (.6, 1.2, 1.8): m.box("grey_dk", -1.95, y, 3.9, 1.95, y + .04, 3.93)
    m.cyl("metal", 0, 9.0, 0, .05, .05, .9, n=6)
    h.detail("vane", (0, 9.9, 0))
    for x in (-5.6, -3.2, 3.2, 5.6): m.blob("hedge", x, .7, D/2 + .8, .85, .7, .7, x)
    for x in (-2.3, 2.3): m.cyl("stone", x, 0, D/2 + 2.4, .35, .3, .6, n=8); m.blob("rose", x, .9, D/2 + 2.4, .45, .4, .45, x)
    yard(h, W, D, 0, lot_w=27, fence=False, car_mat=None, drive_side=1, flowers="rose",
         trees=[(-10.5, 7, 1.0, "wisteria"), (-10.5, -6, 1.1, "leaf")])
    return h



# --------------------------------------------------------------------------
# 7b. Interiors (cutaway view on the site): ground floor only, in house-local
# coordinates. Two versions: the house as the show presents it, and what the
# backlot really has inside (Bree's house: toilets for the crew).
# --------------------------------------------------------------------------
INTERIOR_ROOMS = {}

def _iwall(m, x0, z0, x1, z1, y0, h=2.25, t=.12, gaps=()):
    """Interior partition from (x0,z0) to (x1,z1) with door gaps given as (start, end) along its length."""
    L = math.hypot(x1 - x0, z1 - z0); ux, uz = (x1 - x0) / L, (z1 - z0) / L
    cuts = [0.0] + [v for g in sorted(gaps) for v in g] + [L]
    for a, b in zip(cuts[::2], cuts[1::2]):
        if b - a < .05: continue
        ax, az, bx, bz = x0 + ux * a, z0 + uz * a, x0 + ux * b, z0 + uz * b
        m.box("int_wall", min(ax, bx) - (t/2 if uz else 0), y0, min(az, bz) - (t/2 if ux else 0),
              max(ax, bx) + (t/2 if uz else 0), y0 + h, max(az, bz) + (t/2 if ux else 0))

def _chair(m, x, z, ry, mat="int_wood", y0=0.0):
    with m.at(x, y0, z, ry):
        m.box(mat, -.22, .42, -.22, .22, .47, .22)
        for a, b in ((-.2, -.2), (.17, -.2), (-.2, .17), (.17, .17)): m.box(mat, a, 0, b, a + .04, .42, b + .04)
        m.box(mat, -.22, .47, -.24, .22, 1.0, -.19)

def interior_4354_show():
    m = Mesh("int_4354_show"); W, D, F = 13.0, 9.5, .45
    m.box("int_floor", -W/2 + .05, F - .02, -D/2 + .05, W/2 - .05, F + .02, D/2 - .05)
    m.box("int_tile", 1.6, F + .021, -D/2 + .1, W/2 - .1, F + .03, -.1)                       # kitchen tiles
    # partitions: hall in the middle, living left, dining front right, kitchen back right, study back left
    _iwall(m, -1.6, -D/2, -1.6, D/2, F, gaps=((5.6, 7.0),))
    _iwall(m, 1.6, -D/2, 1.6, D/2, F, gaps=((1.5, 2.6), (6.0, 7.3)))
    _iwall(m, -W/2, -.4, -1.6, -.4, F, gaps=((2.2, 3.2),))
    _iwall(m, 1.6, -.1, W/2, -.1, F, gaps=((1.2, 3.0),))
    # hall: stair rising toward the back, runner rug, console
    for k in range(12):
        m.box("int_wood", -1.45, F, -D/2 + .2 + k * .3, -.15, F + .2 + k * .2, -D/2 + .5 + k * .3)
    m.box("int_wood", -.2, F + .9, -D/2 + .2, -.12, F + 1.0, -D/2 + 3.8)
    m.box("int_rug", -.6, F + .03, .4, .9, F + .05, 4.2)
    m.box("int_wood", .95, F, 1.2, 1.45, F + .85, 2.6)
    m.blob("rose", 1.2, F + 1.05, 1.9, .22, .2, .22, 3)
    # living room: fireplace on the chimney wall, sofa, armchairs, coffee table, piano
    m.box("brick", -W/2 + .05, F, 1.0, -W/2 + .55, F + 1.3, 2.9); m.box("int_case", -W/2 + .4, F, 1.55, -W/2 + .58, F + .8, 2.35)
    m.box("int_wood", -W/2 + .05, F + 1.3, .9, -W/2 + .7, F + 1.42, 3.0)
    m.box("int_rug", -5.4, F + .03, .8, -2.4, F + .05, 3.9)
    m.box("int_sofa", -3.0, F, .9, -2.2, F + .45, 3.8); m.box("int_sofa", -2.55, F, .9, -2.2, F + .9, 3.8)
    for z in (.95, 3.75): m.box("int_sofa", -3.0, F, z - .12, -2.2, F + .65, z + .12)
    for z in (1.0, 3.7): m.box("int_sofa", -5.6, F, z - .45, -4.8, F + .45, z + .45); m.box("int_sofa", -5.6, F, z - .45, -5.35, F + .85, z + .45)
    m.box("int_wood", -4.4, F, 1.8, -3.4, F + .42, 2.9); m.blob("flower_y", -3.9, F + .55, 2.35, .18, .14, .18, 1)
    m.box("int_case", -5.9, F, 4.1, -4.4, F + 1.1, 4.6); m.box("int_case", -5.1, F, 3.75, -4.7, F + .5, 4.05)
    # dining room: table for eight, sideboard with candles
    m.box("int_wood", 2.9, F + .72, .9, 5.6, F + .78, 3.9)
    for x, z in ((3.0, 1.0), (5.5, 1.0), (3.0, 3.8), (5.5, 3.8)): m.box("int_wood", x - .05, F, z - .05, x + .05, F + .72, z + .05)
    for z in (1.4, 2.4, 3.4):
        _chair(m, 2.55, z, -math.pi/2, y0=F); _chair(m, 5.95, z, math.pi/2, y0=F)
    m.box("int_rug", 2.3, F + .03, .5, 6.2, F + .045, 4.3)
    m.box("int_wood", W/2 - .55, F, 1.2, W/2 - .1, F + .9, 3.6)
    for z in (1.8, 3.0): m.cyl("int_counter", W/2 - .33, F + .9, z, .05, .05, .35, n=6)
    m.cyl("int_counter", 4.25, F + .78, 2.4, .32, .25, .1, n=10); m.blob("rose", 4.25, F + 1.0, 2.4, .25, .18, .25, 2)
    # kitchen: L of counters with sink and range, island with stools, double fridge
    m.box("int_cab", 1.8, F, -D/2 + .1, W/2 - .1, F + .9, -D/2 + .75); m.box("int_counter", 1.75, F + .9, -D/2 + .1, W/2 - .1, F + .96, -D/2 + .8)
    m.box("int_cab", W/2 - .75, F, -D/2 + .75, W/2 - .1, F + .9, -1.3); m.box("int_counter", W/2 - .8, F + .9, -D/2 + .75, W/2 - .1, F + .96, -1.3)
    m.box("int_steel", 3.2, F + .96, -D/2 + .2, 4.0, F + .99, -D/2 + .65)
    m.box("int_case", 4.8, F + .96, -D/2 + .15, 5.6, F + 1.0, -D/2 + .7)
    m.box("int_steel", 1.75, F, -D/2 + .1, 2.65, F + 2.1, -D/2 + .85)
    m.box("int_cab", 3.2, F, -2.6, 5.2, F + .9, -1.6); m.box("int_counter", 3.1, F + .9, -2.7, 5.3, F + .97, -1.5)
    for x in (3.5, 4.2, 4.9): m.cyl("int_wood", x, F, -1.15, .18, .18, .72, n=8)
    m.blob("berry", 4.2, F + 1.1, -2.1, .2, .12, .2, 5)                                          # the muffins, naturally
    # study (Rex's, later Orson's): desk, chair, bookshelves
    m.box("int_wood", -5.6, F, -3.6, -3.8, F + .76, -2.8); _chair(m, -4.7, -2.3, math.pi, y0=F)
    m.box("int_wood", -W/2 + .1, F, -D/2 + .1, -1.8, F + 2.1, -D/2 + .45)
    for y in (.5, 1.0, 1.5): m.box("int_case", -W/2 + .2, F + y, -D/2 + .12, -1.9, F + y + .3, -D/2 + .4)
    m.box("int_rug", -5.9, F + .03, -3.9, -2.4, F + .045, -1.0)
    # garage wing: Bree's car and a tidy workbench
    with m.at(W/2 + 2.7, 0, -.4):
        m.box("int_concrete", -2.5, .01, -3.65, 2.5, .04, 3.65)
        car(m, 0, -.3, 0.0, "car_rd")
        m.box("int_wood", -2.4, 0, -3.6, 2.2, .9, -3.0); m.box("int_case", -2.3, 1.3, -3.6, 2.1, 2.0, -3.4)
    return m

def interior_4354_set():
    m = Mesh("int_4354_set"); W, D, F = 13.0, 9.5, .45
    m.box("int_concrete", -W/2 + .05, F - .02, -D/2 + .05, W/2 - .05, F + .02, D/2 - .05)
    m.box("int_tape", -W/2 + .3, F + .021, -.05, W/2 - .3, F + .03, .05)
    # a row of crew toilet stalls along the back wall
    for k in range(7):
        x0 = -5.9 + k * 1.55
        m.box("int_stall", x0, F + .15, -D/2 + .1, x0 + .05, F + 2.0, -D/2 + 1.8)
        m.box("int_stall", x0 + .05, F + .15, -D/2 + 1.75, x0 + 1.05, F + 2.0, -D/2 + 1.8)
        m.box("int_porcelain", x0 + .4, F, -D/2 + .15, x0 + 1.05, F + .42, -D/2 + .75)
        m.box("int_porcelain", x0 + .45, F + .42, -D/2 + .12, x0 + 1.0, F + .85, -D/2 + .3)
    m.box("int_stall", 4.95, F + .15, -D/2 + .1, 5.0, F + 2.0, -D/2 + 1.8)
    # wash basins on the front wall, a mirror strip above
    m.box("int_counter", -4.0, F + .8, D/2 - .7, 4.0, F + .88, D/2 - .1)
    for k in range(5): m.box("int_porcelain", -3.4 + k * 1.6, F + .62, D/2 - .6, -2.8 + k * 1.6, F + .8, D/2 - .2)
    m.box("glass_lt", -4.0, F + 1.2, D/2 - .1, 4.0, F + 2.1, D/2 - .05)
    # crates, a folding chair, a light stand and coiled cable — it is still a working set
    for x, z, h in ((-5.6, 1.6, .7), (-4.9, 1.7, .5), (-5.4, 2.4, .9)): m.box("int_case", x - .35, F, z - .3, x + .35, F + h, z + .3)
    _chair(m, 5.2, 1.4, 2.4, mat="int_case", y0=F)
    m.cyl("int_case", 5.6, F, 3.2, .04, .04, 2.2, n=5); m.box("int_steel", 5.35, F + 2.1, 3.0, 5.85, F + 2.45, 3.3)
    m.cyl("int_case", 2.6, F, 2.4, .45, .45, .12, n=12)
    with m.at(W/2 + 2.7, 0, -.4):
        m.box("int_concrete", -2.5, .01, -3.65, 2.5, .04, 3.65)
        for k in range(4): m.box("int_case", -2.2 + k * 1.1, 0, -3.5, -1.4 + k * 1.1, .6 + .2 * (k % 2), -2.7)
        m.box("int_tape", -2.4, .041, 1.0, 2.4, .05, 1.1)
    return m

INTERIOR_ROOMS["4354"] = {
    "show": [["Кухня с маффинами", 4.6, 1.3, -3.4], ["Столовая", 4.2, 1.2, 3.4], ["Гостиная", -4.6, 1.2, 3.6], ["Лестница", -0.8, 1.2, -2.6], ["Кабинет Рекса", -4.4, 1.2, -3.4], ["Гараж", 9.4, 1.2, 1.4]],
    "box": [-8.1, 12.2, -5.4, 7.2], "cut": 2.88,
    "set": [["Туалеты для съёмочной группы", -0.4, 2.4, -3.6], ["Умывальники", 0.0, 1.6, 3.6], ["Склад реквизита", -5.2, 1.4, 2.0], ["Кофры с техникой", 9.4, 1.2, -1.6]],
}
INTERIORS = {"4354": (interior_4354_show, interior_4354_set)}


def h4353():  # Mayer — yellow Dutch colonial: gambrel roof, shed dormer, front gable bay, white rail fence
    h = House("4353"); m = h.body; W, D = 12.0, 9.0
    foundation(m, W, D); walls(m, W, D, .45, 3.2, "yellow")
    m.gambrel("roof_br", "yellow", -W/2, W/2, -D/2, D/2, 3.65, 2.6, 1.5, knee=.3)
    with m.at(1.2, 3.85, 2.6):  # wide shed dormer pushed out through the lower slope
        m.cbox("yellow", 0, 0, 0, 5.0, 2.3, 3.4)
        clapboard(m, 5.0, 3.4, 0, 2.3, "yellow")
        m.shed("roof_br", -2.75, 2.75, -1.8, 2.05, 2.75, 2.3)
        m.box("trim", -2.75, 2.15, 1.98, 2.75, 2.35, 2.08)
        for u in (-1.5, 0, 1.5):
            m.box("trim", u - .6, .45, 1.68, u + .6, 1.85, 1.76); m.box("glass", u - .48, .55, 1.74, u + .48, 1.75, 1.78)
            m.box("trim", u - .03, .55, 1.78, u + .03, 1.75, 1.82); m.box("trim", u - .7, .32, 1.68, u + .7, .45, 1.9)
    with m.at(-3.6, 0, D/2 + .9):  # front gable sunroom bay
        m.cbox("yellow", 0, .45, 0, 4.0, 2.9, 1.8)
        m.push(ry=math.pi/2); m.gable("roof_br", "yellow", -.9, .9, -2.0, 2.0, 3.35, 4.7, over=.3); m.pop()
        m.box("trim", -1.75, 1.1, .9, 1.75, 2.75, .96); m.box("glass", -1.6, 1.2, .94, 1.6, 2.65, 1.0)
        for u in (-.8, 0, .8): m.box("trim", u - .04, 1.2, .98, u + .04, 2.65, 1.03)
        m.oculus(0, 3.9, .92, .3)
    window(m, "front", W, D, 3.6, 1.2, 1.3, 1.6)
    for f in ("left", "right"):
        for u in (-2.2, 2.2): window(m, f, W, D, u, 1.2, 1.0, 1.5)
        window(m, f, W, D, 0, 4.4, 1.0, 1.2)
    bay_window(m, "right", W, D, 0, .45, 3.0, "yellow", roof="roof_br")
    m.box("board", 0, 0, D/2, 2.4, .45, D/2 + 1.6)
    with m.at(1.2, 0, D/2 + .6): m.shed("roof_br", -1.4, 1.4, -.6, 1.2, 3.4, 3.1)
    for x in (.15, 2.25): m.cyl("trim", x, .45, D/2 + 1.4, .1, .1, 2.6, n=6)
    hd = D/2
    m.box("trim", .45, .45, hd - .02, 1.95, 2.95, hd + .06)     # door frame; the leaf is a moving detail
    m.box("black", .62, .45, hd + .03, 1.78, 2.75, hd + .07)
    h.detail("door", (.625, .45, hd + .1))
    chimney(m, -W/2 + .6, 0, 3.0, 5.6, "brick")
    for x in (-5.0, -1.2, 4.5): m.blob("hedge", x, .7, D/2 + 2.2 if x != -1.2 else D/2 + 2.6, 1.1, .75, .8, x)
    yard(h, W, D, 1.2, lot_w=24, fence=False, car_mat="car_wh", drive_side=1, flowers="rose",
         trees=[(-9.5, 6.0, 1.1, "leaf"), (-9.5, -6, 1.0, "leaf")])
    zf = SET_Z - (ROAD_W / 2 + .25 + WALK_W) - .7
    rail(m, -11.5, -.4, zf); rail(m, 2.6, 6.0, zf)
    return h

def h4355():  # Scavo — sage-green two-storey, brown roof, white trim, vine-covered porch and picket fence
    h = House("4355"); m = h.body; W, D = 12.5, 10.0
    foundation(m, W, D, .5); walls(m, W, D, .5, 5.9, "green_lyn"); band(m, W, D, 3.4, "trim", .16)
    m.gable("roof_br", "green_lyn", -W/2, W/2, -D/2, D/2, 6.4, 9.4, over=.5)
    with m.at(2.0, 0, D/2 - 1.0):   # front gable wing with an oculus
        m.cbox("green_lyn", 0, .5, 0, 5.0, 5.9, 2.4)
        m.push(ry=math.pi/2); m.gable("roof_br", "green_lyn", -3.8, 1.6, -2.5, 2.5, 6.4, 9.0, over=.4); m.pop()
        m.oculus(0, 7.4, 1.22, .4)
    for u in (.8, 3.2): window(m, "front", W, D + 0.5, u, 4.0, 1.0, 1.5)
    window(m, "front", W, D, -4.2, 4.0, 1.0, 1.5); window(m, "front", W, D, -1.6, 4.0, 1.0, 1.5)
    for f in ("left", "right"):
        for u in (-2.6, 2.6): window(m, f, W, D, u, 1.3, 1.0, 1.8); window(m, f, W, D, u, 4.0, 1.0, 1.5)
    bay_window(m, "right", W, D, 0, .5, 3.2, "green_lyn", roof="roof_br")
    porch(m, -W/2 - .2, W/2 + .2, D/2 + .2, 2.6, y=.5, cols=6, roof="shed", roof_mat="roof_br", steps_u=-2.6)
    for x in (-5.8, -3.2, 3.6, 6.2):  # climbing vines on the porch posts
        m.blob("hedge", x, 2.6, D/2 + 2.5, .45, 1.2, .4, x)
    for u in (-4.4, -.8, 2.0, 4.6): window(m, "front", W, D, u, 1.3, 1.1, 1.8)
    door(m, "front", W, D, -2.6, mat="door_gn", y=.5)
    chimney(m, -4.6, -2.0, 6.0, 4.6, "brick")
    tree(m, -9.0, 8.0, 1.25, "leaf", 3.3)
    h.detail("swing", (-7.7, 4.0, 8.3))
    m.box("red", 3.5, 0, D/2 + 5.5, 4.4, .5, D/2 + 6.2)   # toy wagon
    yard(h, W, D, -2.6, lot_w=26, fence=True, car_mat="car_bk", drive_side=1, flowers="flower_y",
         trees=[(-10.5, -5, 1.0, "leaf")])
    return h

def h4352():  # Young — the Cleaver house replica: cream clapboard, brown shingle roof, cross gables
    h = House("4352"); m = h.body; W, D = 12.0, 9.5
    foundation(m, W, D); walls(m, W, D, .45, 5.6, "cream"); band(m, W, D, 3.2, "trim", .14)
    m.gable("roof_bn", "cream", -W/2, W/2, -D/2, D/2, 6.05, 9.2, over=.55)
    with m.at(-2.6, 0, D/2 - .6):   # projecting front gable
        m.cbox("cream", 0, .45, .6, 4.4, 5.6, 2.4)
        m.push(ry=math.pi/2); m.gable("roof_bn", "cream", -.6, 1.8, -2.2, 2.2, 6.05, 8.6, over=.4); m.pop()
    window(m, "front", 4.4, D + 2.5, -2.6, 1.2, 2.2, 1.7, shutters="shutter_bk")
    window(m, "front", 4.4, D + 2.5, -2.6, 3.9, 1.2, 1.4, shutters="shutter_bk")
    m.box("board", .4, 0, D/2, 5.8, .45, D/2 + 2.0)                   # side porch with a low roof
    m.shed("roof_bn", .2, 6.0, D/2 - .1, D/2 + 2.3, 3.6, 3.1)
    for x in (.6, 3.2, 5.6): m.cyl("trim", x, .45, D/2 + 1.8, .11, .11, 2.65, n=6)
    door(m, "front", W, D, 1.6, mat="door_wd")
    window(m, "front", W, D, 4.2, 1.2, 1.2, 1.6, shutters="shutter_bk")
    for u in (1.6, 4.2): window(m, "front", W, D, u, 3.9, 1.0, 1.4, shutters="shutter_bk")
    for f in ("left", "right"):
        for u in (-2.2, 2.2): window(m, f, W, D, u, 1.2, 1.0, 1.6); window(m, f, W, D, u, 3.9, 1.0, 1.4)
    bay_window(m, "left", W, D, 0, .45, 3.0, "cream", roof="roof_bn")
    chimney(m, W/2 - 1.2, -1.0, 6.0, 4.0, "brick")
    yard(h, W, D, 1.6, lot_w=24, fence=True, car_mat=None, drive_side=1, flowers="rose",
         trees=[(-9.5, 6.0, 1.0, "wisteria"), (-9, -6.5, 1.0, "leaf")])
    m.box("stone", 4.5, 0, -D/2 - 3.6, 7.0, .1, -D/2 - .9)  # backyard pool
    m.box("water", 4.7, .05, -D/2 - 3.4, 6.8, .12, -D/2 - 1.1)
    return h

def h4356():  # Mayfair — Craftsman bungalow, low wide gables, grey-brown boards
    h = House("4356"); m = h.body; W, D = 12.5, 10.0
    foundation(m, W, D, .55, "stone"); walls(m, W, D, .55, 3.4, "slate")
    m.gable("roof_dk", "slate", -W/2, W/2, -D/2, D/2, 3.95, 6.6, over=.9, attic="x1")
    with m.at(0, 4.4, 0):    # shed dormer
        m.cbox("slate", 0, 0, 2.0, 4.6, 1.8, 3.2)
        m.shed("roof_dk", -2.6, 2.6, .2, 3.95, 2.25, 1.75)
        for u in (-1.3, 0, 1.3):
            m.box("trim", u - .52, .3, 3.58, u + .52, 1.42, 3.64); m.box("glass", u - .42, .38, 3.62, u + .42, 1.34, 3.68)
    with m.at(1.5, 0, D/2):   # porch under its own low gable, tapered columns on stone piers
        m.box("board", -3.2, 0, 0, 3.2, .55, 2.8)
        for x in (-2.9, 2.9):
            m.cbox("stone", x, .55, 2.45, .7, 1.0, .7); m.frustum("trim", x - .3, 2.15, x + .3, 2.75, 1.55, .08, 3.6)
        m.push(ry=math.pi/2); m.gable("roof_dk", "slate", -.1, 3.1, -3.4, 3.4, 3.6, 5.0, over=.4); m.pop()
        for k in range(3): m.box("stone", -.9, 0, 2.8 + k*.32, .9, .55 - k*.17, 3.12 + k*.32)
    door(m, "front", W, D, 1.5, mat="door_wd", y=.55, glass_top=False)
    for u in (-4.5, -3.0): window(m, "front", W, D, u, 1.4, 1.2, 1.6)
    window(m, "front", W, D, 4.4, 1.4, 1.2, 1.6)
    for f in ("left", "right"):
        for u in (-2.8, 0, 2.8): window(m, f, W, D, u, 1.4, 1.0, 1.5)
    chimney(m, -W/2 - .1, -1.0, .0, 8.0, "stone", 1.1, 1.3)
    # flag pole by the walk
    m.cyl("metal", -4.0, 0, D/2 + 4.5, .06, .05, 5.5, n=6)
    h.detail("pennant", (-4.0, 5.4, D/2 + 4.5))
    yard(h, W, D, 1.5, lot_w=24, fence=False, car_mat="car_wh", drive_side=1, flowers="flower_y",
         trees=[(-9.5, 6.0, 1.1, "leaf"), (9.5, -6.5, 1.0, "leaf")])
    return h

def h4358():  # McCluskey — rebuilt farmhouse with a full-width porch
    h = House("4358"); m = h.body; W, D = 11.0, 9.0
    foundation(m, W, D); walls(m, W, D, .45, 5.6, "grey"); band(m, W, D, 3.3, "trim", .14)
    m.gable("roof_lt", "grey", -W/2, W/2, -D/2, D/2, 6.05, 8.6, over=.45)
    for u in (-3, 0, 3): window(m, "front", W, D, u, 4.0, 1.0, 1.4, shutters="shutter_bl")
    for u in (-3.3, 3.3): window(m, "front", W, D, u, 1.2, 1.1, 1.6, shutters="shutter_bl")
    for f in ("left", "right"):
        for u in (-2, 2): window(m, f, W, D, u, 1.2, 1.0, 1.5); window(m, f, W, D, u, 4.0, 1.0, 1.4)
    bay_window(m, "left", W, D, 0, .45, 3.0, "mint")
    porch(m, -W/2, W/2, D/2, 2.6, cols=5, roof="shed", roof_mat="roof_lt", steps_u=0)
    door(m, "front", W, D, 0, mat="door_bl")
    h.detail("rocker", (-3.2, .45, D/2 + 1.1), ry=0.3)
    chimney(m, W/2 - .8, -1.5, 5.5, 3.5, "brick")
    yard(h, W, D, 0, lot_w=22, fence=False, car_mat=None, drive_side=-1, flowers="rose",
         trees=[(8, 5, 1.0, "leaf")])
    return h

def h4362():  # Britt — pink clapboard, brown roof, twin front gables with oculi, columned entry, white gate
    h = House("4362"); m = h.body; W, D = 14.0, 9.5
    foundation(m, W, D, .4, "stone"); walls(m, W, D, .4, 6.0, "blush")
    band(m, W, D, 3.3, "trim", .14)
    m.hip("roof_bn", -W/2, W/2, -D/2, D/2, 6.4, 2.6, over=.6)
    for u in (-4.4, 4.4):                       # twin front gables
        with m.at(u, 0, D/2):
            m.cbox("blush", 0, .4, .6, 4.2, 3.5, 1.2)
            clapboard(m, 4.2, 1.2, .4, 3.5, "blush")
            m.push(ry=math.pi/2); m.gable("roof_bn", "blush", -.2, 1.4, -2.3, 2.3, 3.9, 5.7, over=.3); m.pop()
            m.oculus(0, 4.75, 1.22, .36)
            m.box("trim", -1.5, 1.0, 1.18, 1.5, 3.0, 1.24); m.box("glass", -1.35, 1.1, 1.22, 1.35, 2.9, 1.3)
            for x in (-.45, .45): m.box("trim", x - .04, 1.1, 1.26, x + .04, 2.9, 1.32)
    # recessed entry with paired white columns and a small pediment
    m.box("board", -2.3, 0, D/2, 2.3, .4, D/2 + 2.0)
    for x in (-1.9, -1.2, 1.2, 1.9): m.cyl("trim", x, .4, D/2 + 1.7, .15, .12, 2.9, n=8)
    with m.at(0, 0, D/2 + 1.0):
        m.push(ry=math.pi/2); m.gable("roof_bn", "trim", -1.1, 1.1, -2.4, 2.4, 3.3, 4.3, over=.2); m.pop()
    door(m, "front", W, D, 0, mat="door_wd", y=.4)
    for u in (-1.6, 1.6): window(m, "front", W, D, u, 1.1, .7, 1.8)
    for u in (-2.0, 0.0, 2.0): window(m, "front", W, D, u, 4.1, 1.0, 1.4)
    for f in ("left", "right"):
        for u in (-2, 2): window(m, f, W, D, u, 1.2, 1.0, 1.6); window(m, f, W, D, u, 4.0, 1.0, 1.4)
    bay_window(m, "right", W, D, 0, .4, 3.3, "blush", roof="roof_bn")
    chimney(m, -3.5, -2.0, 6.0, 3.2, "stone")
    # white gate in a picket run, and the realtor sign
    zf = SET_Z - (ROAD_W / 2 + .25 + WALK_W) - .7
    picket(m, -12.0, -9.0, zf, h=1.4)
    m.box("trim", -9.0, 0, zf - .06, -8.85, 1.7, zf + .06); m.box("trim", -11.0, 1.55, zf - .05, -9.0, 1.65, zf + .05)
    sx, sz = 4.5, zf - .9
    m.cyl("trim", sx, 0, sz, .07, .07, 2.0, n=6); m.box("trim", sx, 1.85, sz - .05, sx + 1.0, 1.95, sz + .05)
    h.detail("sign", (sx + .2, 1.85, sz))
    m.box("stone", -8.0, 0, -D/2 - 4.4, -2.6, .1, -D/2 - .6)      # pool out back
    m.box("water", -7.7, .02, -D/2 - 4.1, -2.9, .14, -D/2 - .9)
    yard(h, W, D, 0, lot_w=26, fence=False, car_mat="car_rd", drive_side=1, flowers="rose",
         trees=[(-10.5, 3, 1.0, "wisteria")])
    return h

def h4350():  # Huber — tiny one-storey cottage
    h = House("4350"); m = h.body; W, D = 9.0, 8.0
    foundation(m, W, D, .4); walls(m, W, D, .4, 3.1, "cream")
    m.gable("roof_br", "cream", -W/2, W/2, -D/2, D/2, 3.5, 5.8, over=.5)
    for u in (-2.6, 2.6): window(m, "front", W, D, u, 1.1, 1.2, 1.5, shutters="shutter_gn")
    porch(m, -1.5, 1.5, D/2, 1.8, y=.4, cols=2, roof="hip", roof_mat="roof_br", rail=False, h=2.5, steps_u=0)
    door(m, "front", W, D, 0, mat="door_gn", y=.4)
    for f in ("left", "right"):
        for u in (-1.6, 1.6): window(m, f, W, D, u, 1.1, 1.0, 1.4)
    chimney(m, -2.5, -1.5, 3.0, 3.6, "brick")
    yard(h, W, D, 0, lot_w=20, fence=True, car_mat=None, drive_side=1, flowers="rose",
         trees=[(-7.5, 5.0, .9, "leaf")])
    return h

def h4347():  # Greenberg — powder-blue Victorian with an exterior stair and grey hip roof
    h = House("4347"); m = h.body; W, D = 12.0, 10.0
    foundation(m, W, D, .5); walls(m, W, D, .5, 6.2, "blue_vic"); band(m, W, D, 3.5, "trim", .16)
    m.hip("roof_dk", -W/2, W/2, -D/2, D/2, 6.7, 3.4, over=.5)
    with m.at(-2.8, 0, D/2 - .2):
        m.cbox("blue_vic", 0, .5, .2, 4.2, 6.2, 1.2)
        m.push(ry=math.pi/2); m.gable("roof_dk", "blue_vic", -.3, 1.1, -2.1, 2.1, 6.7, 9.4, over=.3); m.pop()
        m.oculus(0, 7.6, .82, .35)
    for u in (-3.8, -1.8): window(m, "front", W, D + 1.3, u, 1.3, 1.0, 1.8, shutters="shutter_bk"); window(m, "front", W, D + 1.3, u, 4.3, 1.0, 1.5, shutters="shutter_bk")
    window(m, "front", W, D, 4.7, 1.3, 1.0, 1.7)
    for u in (1.6, 4.2): window(m, "front", W, D, u, 4.3, 1.0, 1.5)
    porch(m, .2, W/2 + .2, D/2, 2.6, y=.5, cols=4, roof="flat", roof_mat="blue_vic", steps_u=2.9)
    door(m, "front", W, D, 2.9, mat="door_wd", y=.5)
    # outside stair to the side deck
    for k in range(10):                                   # open treads
        m.box("board", W/2 + .15, .45 + k * .35, D/2 - 1 - k * .55, W/2 + 1.25, .53 + k * .35, D/2 - .45 - k * .55)
    for x in (W/2 + .12, W/2 + 1.22):                      # stringers and a handrail, stepped
        for k in range(10):
            m.box("trim", x, .2 + k * .35, D/2 - 1 - k * .55, x + .08, .5 + k * .35, D/2 - .45 - k * .55)
    for k in range(0, 10, 3): m.box("trim", W/2 + 1.22, .53 + k * .35, D/2 - .8 - k * .55, W/2 + 1.3, 1.45 + k * .35, D/2 - .72 - k * .55)
    m.box("board", W/2 + .1, 3.9, -D/2 + .5, W/2 + 2.2, 4.02, D/2 - 5.5)
    for z in (-D/2 + .6, -D/2 + 2.3, D/2 - 5.6):           # deck posts and balustrade
        m.box("trim", W/2 + 2.0, 0, z - .08, W/2 + 2.16, 4.95, z + .08)
    m.box("trim", W/2 + 2.05, 4.85, -D/2 + .5, W/2 + 2.2, 4.97, D/2 - 5.5)
    for k in range(13): m.box("trim", W/2 + 2.08, 4.02, -D/2 + .7 + k * .32, W/2 + 2.14, 4.85, -D/2 + .76 + k * .32)
    for f in ("left", "right"):
        for u in (-2.4, 2.4): window(m, f, W, D, u, 1.3, 1.0, 1.7); window(m, f, W, D, u, 4.3, 1.0, 1.5)
    chimney(m, -4.5, -2.0, 7.0, 3.6, "brick")
    yard(h, W, D, 2.9, lot_w=24, fence=False, car_mat="car_bl", drive_side=-1, flowers="flower_y",
         trees=[(9.5, 6, 1.1, "leaf"), (-9.8, -5, 1.0, "leaf")])
    return h
def h4351():  # Applewhite — grey-green Victorian with a corner turret (the old Munster house)
    h = House("4351"); m = h.body; W, D = 11.5, 10.0
    foundation(m, W, D, .55); walls(m, W, D, .55, 6.0, "teal"); band(m, W, D, 3.5, "trim", .16)
    m.hip("roof_lt", -W/2, W/2, -D/2, D/2, 6.55, 3.4, over=.45)
    with m.at(1.5, 0, D/2 - .2):   # front gable
        m.cbox("teal", 0, .55, .2, 3.8, 6.0, 1.0)
        m.push(ry=math.pi/2); m.gable("roof_lt", "teal", -.3, .9, -1.9, 1.9, 6.55, 8.9, over=.3); m.pop()
    tx, tz = -W/2 + 1.2, D/2 - .4    # turret
    m.cyl("teal", tx, .55, tz, 1.75, 1.75, 7.0, n=8, rot=math.pi/8)
    m.cyl("trim", tx, 7.55, tz, 1.95, 1.95, .2, n=8, rot=math.pi/8)
    m.cyl("roof_lt", tx, 7.75, tz, 2.0, 0, 3.6, n=8, rot=math.pi/8)
    m.cyl("black", tx, 11.3, tz, .06, 0, .9, n=4)
    for a in (-0.4, 0.6, 1.6):
        with m.at(tx + 1.72 * math.sin(a), 0, tz + 1.72 * math.cos(a), a):
            for y in (1.4, 4.5):
                m.box("trim", -.42, y - .1, -.05, .42, y + 1.5, .05); m.box("glass", -.32, y, .0, .32, y + 1.35, .08)
    window(m, "front", W, D + 1.1, 1.5, 4.4, 1.2, 1.5)
    with m.at(1.5, 0, D/2 - .2): m.oculus(0, 7.25, .92, .36)
    for y, hh in ((1.4, 1.7), (4.4, 1.5)): window(m, "front", W, D, -1.6, y, .9, hh)
    porch(m, -.6, W/2 + .3, D/2 + .3, 2.4, y=.55, cols=4, roof="hip", roof_mat="roof_lt", steps_u=3.6)
    door(m, "front", W, D, 3.6, mat="door_wd", y=.55)
    window(m, "front", W, D + 1.1, 1.5, 1.4, 1.1, 1.8)
    for f in ("left", "right"):
        for u in (-2.4, 2.4): window(m, f, W, D, u, 1.4, 1.0, 1.7); window(m, f, W, D, u, 4.4, 1.0, 1.5)
    chimney(m, 3.5, -2.5, 8.0, 3.2, "brick")
    yard(h, W, D, 3.6, lot_w=24, fence=False, car_mat=None, drive_side=-1, flowers="rose",
         trees=[(-9, 6, 1.0, "leaf"), (9.5, -6, 1.1, "leaf")])
    return h

def h4344():  # Seven Gables — dark, steep and empty
    h = House("4344"); m = h.body; W, D = 11.0, 9.0
    foundation(m, W, D, .5); walls(m, W, D, .5, 5.6, "darkgrey")
    m.gable("roof_dk", "darkgrey", -W/2, W/2, -D/2, D/2, 6.1, 10.2, over=.4)
    for u in (-3.2, 0.0, 3.2):
        with m.at(u, 0, D/2 - .5):
            m.cbox("darkgrey", 0, .5, 0, 2.4, 5.6, 1.6)
            m.push(ry=math.pi/2); m.gable("roof_dk", "darkgrey", -.8, .8, -1.2, 1.2, 6.1, 9.0, over=.2); m.pop()
    for u in (-3.2, 3.2):
        window(m, "front", W, D + .7, u, 1.3, .9, 1.6, trim="board")
        window(m, "front", W, D + .7, u, 4.1, .9, 1.4, trim="board")
        with m.at(u, 0, D/2 + .45):  # boarded up
            m.box("board", -.6, 1.6, 0, .6, 1.8, .1); m.box("board", -.6, 2.3, 0, .6, 2.5, .1)
    door(m, "front", W, D + .6, 0, mat="black", y=.5, glass_top=False)
    yard(h, W, D, 0, lot_w=22, fence=False, car_mat=None, hedges=False, flowers=None,
         trees=[(-8, 5.5, 1.2, "leaf"), (8, 6, 1.3, "leaf"), (-7, -6, 1.1, "leaf")])
    return h

def h4360():  # light-green house at the end of the lane
    h = House("4360"); m = h.body; W, D = 11.0, 9.0
    foundation(m, W, D); walls(m, W, D, .45, 5.6, "mint"); band(m, W, D, 3.3, "trim", .14)
    m.hip("roof_lt", -W/2, W/2, -D/2, D/2, 6.05, 2.4, over=.5)
    for u in (-3, 0, 3): window(m, "front", W, D, u, 4.0, 1.0, 1.4)
    for u in (-3, 3): window(m, "front", W, D, u, 1.2, 1.2, 1.6, shutters="shutter_gn")
    porch(m, -1.6, 1.6, D/2, 2.0, cols=2, roof="flat", roof_mat="mint", rail=False, h=2.8, steps_u=0)
    door(m, "front", W, D, 0, mat="door_gn")
    for f in ("left", "right"):
        for u in (-2, 2): window(m, f, W, D, u, 1.2, 1.0, 1.5); window(m, f, W, D, u, 4.0, 1.0, 1.4)
    yard(h, W, D, 0, lot_w=22, fence=True, car_mat=None, drive_side=1, flowers="flower_y",
         trees=[(-8, 5, 1.0, "wisteria")])
    return h

BUILDERS = {f.__name__[1:]: f for f in (h4344, h4347, h4349, h4350, h4351, h4352, h4353, h4354, h4355, h4356, h4358, h4360, h4362)}

# --------------------------------------------------------------------------
# 8b. Story props ("artefacts"): each is its own mesh, placed in a house's
#     local frame, shown on the site only in the seasons it belongs to.
# --------------------------------------------------------------------------
def p_letter(m):          # the blackmail note on Mary Alice's doormat
    m.box("door_rd", -.7, 0, -.45, .7, .04, .45)
    with m.at(0, .04, 0, .3):
        m.box("sign", -.32, 0, -.22, .32, .03, .22)
        m.poly("cream", [(-.32, .031, -.22), (.32, .031, -.22), (0, .031, .02)], up=(0, 1, 0))
        m.box("red", -.05, .031, -.03, .05, .045, .05)

def p_toychest(m):        # Dana's blue toy chest, pulled up by the pool
    m.box("door_bl", -.6, 0, -.35, .6, .65, .35)
    m.box("door_bl_dk", -.62, .65, -.37, .62, .78, .37)
    for x in (-.6, .6): m.box("metal", x - .03, .1, -.36, x + .03, .7, .36)
    m.box("metal", -.08, .45, .35, .08, .6, .4)

def p_cellar(m):          # Betty's locked cellar hatch with a chain
    m.box("stone", -1.0, 0, -.8, 1.0, .25, .8)
    for s in (-1, 1):
        with m.at(s * .45, .25, 0, 0):
            m.solid("door_wd", [[(-.42, 0, -.7), (.42, 0, -.7), (.42, .18, .7), (-.42, .18, .7)],
                                [(-.42, .08, -.7), (.42, .08, -.7), (.42, .26, .7), (-.42, .26, .7)]])
    for i in range(6):
        m.cyl("metal", -.25 + i * .1, .5, (-1) ** i * .05, .05, .05, .05, n=6)
    m.box("black", -.12, .35, -.1, .12, .62, .1)

def p_freezer(m):         # Karen's chest freezer beside the garage
    m.box("white", -.9, 0, -.45, .9, 1.0, .45)
    m.box("grey", -.92, 1.0, -.47, .92, 1.08, .47)
    m.box("metal", -.2, .85, .45, .2, .95, .5)
    m.cyl("black", .9, .2, 0, .03, .03, .5, n=4)

def p_ruins(m):           # Edie's house after Susan's candle (season 1)
    m.box("soil_dk", -8.5, 0, -6.0, 8.5, .08, 6.0)
    m.box("ash", -7.1, 0, -4.8, 7.1, .45, 4.8)
    m.box("char", -6.9, .45, -4.6, 6.9, .5, 4.6)
    for (x, z, w, d, h) in [(-6.6, -4.4, .6, .6, 2.4), (6.4, -4.2, .6, 1.6, 3.2), (-6.8, 3.6, .7, .5, 1.6),
                            (0, -4.5, 3.2, .4, 1.2), (3.5, 4.4, 2.2, .4, .9), (-3, 4.4, 1.0, .4, 2.0)]:
        m.cbox("char", x, .45, z, w, h, d)
    for i in range(9):
        a = i * 0.7
        with m.at(-3 + i * .8, .45, -1.5 + (i % 3) * 1.2, a):
            m.box("char", -1.6, 0, -.1, 1.6, .18, .1)
    m.cbox("brick_dk", -3.5, .45, -2.0, 1.0, 4.6, 1.0)        # the chimney is all that stands
    for (x, z) in [(-1, 1), (2, -1), (4, 2)]:
        m.cyl("ash", x, .5, z, .9, .1, .5, n=7)
    for (x, z) in [(-5.5, 5.4), (5.5, 5.6), (0, 5.8)]:      # scorched shrubs where the beds were
        m.blob("char", x, .5, z, .6, .45, .5, x)

def p_tornado(m):         # the season-4 twister and McCluskey's flattened house
    m.box("soil_dk", -6.5, 0, -5, 6.5, .06, 5)
    m.box("stone", -5.8, 0, -4.6, 5.8, .45, 4.6)
    for i in range(14):
        x = -5 + (i * 3.7) % 10; z = -4 + (i * 2.3) % 8
        with m.at(x, .45 + (i % 3) * .2, z, i * .9):
            m.box("grey" if i % 2 else "roof_lt", -1.2, 0, -.08, 1.2, .16, .08)
    m.cbox("brick", 3.5, .45, -1.5, .9, 3.2, .9)
    m.cbox("roof_lt", -2.0, .45, 1.2, 4.0, .9, 3.2)

def tornado_funnel():
    t = Mesh("tornado")
    for i in range(9):
        y = i * 2.4; r0 = .5 + i * .55; r1 = .5 + (i + 1) * .55
        t.cyl("storm" if i % 2 else "storm_dk", (i % 3 - 1) * .3, y, (i % 2) * .3, r0, r1, 2.4, n=9, rot=i * .5)
    return t

def p_plane(m):           # wreckage of the small plane, season 6 Christmas
    m.box("soil_dk", -5, 0, -2.5, 5, .06, 2.5)
    with m.at(0, 0, 0, .35):
        m.cyl("white", 0, .55, 0, .7, .55, .1, n=8)
        m.frustum("white", -3.6, -.6, 2.4, .6, .2, .1, 1.3, insz=.15)
        m.box("red", -3.6, .55, -.62, 2.4, .75, .62)
        with m.at(-.4, 1.05, 0, 0):
            m.solid("white", [[(-.9, 0, -4.2), (.6, 0, -4.2), (.9, 0, 4.2), (-.6, 0, 4.2)],
                              [(-.9, .12, -4.2), (.6, .12, -4.2), (.9, .12, 4.2), (-.6, .12, 4.2)]])
        with m.at(-3.4, 1.0, 0, 0):
            m.solid("red", [[(0, 0, -.06), (.9, 0, -.06), (.2, 1.4, -.06)], [(0, 0, .06), (.9, 0, .06), (.2, 1.4, .06)]])
        m.box("glass", 1.2, .9, -.55, 2.0, 1.25, .55)
        m.box("black", 2.4, .3, -.1, 2.6, 1.3, .1)
        for x in (-1.5, .5): m.cyl("black", x, 0, .9, .25, .25, .2, n=6)
    for (x, z) in [(3.8, 1.5), (-4.2, -1.8), (2.5, -2.0)]:
        m.box("white", x - .5, 0, z - .2, x + .5, .15, z + .2)
    m.cyl("ash", -1.5, 0, 1.8, 1.0, .2, 1.2, n=7)

def p_towel(m):           # Susan locked out naked: a towel left on the bushes
    m.blob("hedge", 0, .7, 0, 1.0, .75, .8, 4.2)
    with m.at(0, 1.25, .1, .4):
        m.solid("towel", [[(-.55, 0, -.4), (.55, 0, -.4), (.5, -.05, .45), (-.5, -.05, .45)],
                          [(-.55, .07, -.4), (.55, .07, -.4), (.5, .02, .45), (-.5, .02, .45)]])
        m.box("towel_dk", -.55, .075, -.15, .55, .085, -.05)

def p_mower(m):           # John the gardener's lawnmower
    m.box("red", -.4, .15, -.55, .4, .45, .45)
    m.box("black", -.3, .45, -.3, .3, .65, .2)
    for x in (-.42, .42):
        for z in (-.45, .35):
            with m.at(x, .15, z, math.pi / 2): m.cyl("black", 0, -.05, 0, .15, .15, .1, n=8)
    for x in (-.32, .32): m.solid("black", [[(x - .03, .45, .4), (x + .03, .45, .4), (x + .03, 1.3, 1.2), (x - .03, 1.3, 1.2)],
                                            [(x - .03, .5, .4), (x + .03, .5, .4), (x + .03, 1.35, 1.2), (x - .03, 1.35, 1.2)]])
    m.box("black", -.35, 1.3, 1.17, .35, 1.36, 1.25)
    m.box("grass_bag", -.3, .2, .45, .3, .7, 1.0)

def p_muffins(m):         # Bree's welcome basket
    m.cyl("wicker", 0, 0, 0, .38, .45, .35, n=10)
    for a in range(5):
        x, z = .2 * math.cos(a * 1.26), .2 * math.sin(a * 1.26)
        m.cyl("muffin_case", x, .35, z, .1, .12, .1, n=8); m.blob("muffin", x, .5, z, .14, .1, .14, a)
    m.cyl("wicker", -.36, .35, 0, .03, .03, .1, n=4); m.cyl("wicker", .36, .35, 0, .03, .03, .1, n=4)
    m.box("wicker", -.38, .62, -.03, .38, .67, .03)
    m.poly("red", [(-.3, .36, .4), (.3, .36, .4), (0, .25, .47)], up=(0, 0, 1))

def p_van(m):             # Mike's plumbing van
    m.box("white", -1.0, .35, -2.6, 1.0, 2.2, 1.6)
    m.box("white", -1.0, .35, 1.6, 1.0, 1.4, 2.6)
    m.solid("glass", [[(-.95, 1.4, 1.6), (.95, 1.4, 1.6), (.95, 2.1, 1.65), (-.95, 2.1, 1.65)],
                      [(-.95, 1.4, 1.7), (.95, 1.4, 1.7), (.95, 2.1, 1.75), (-.95, 2.1, 1.75)]])
    m.box("car_bl", -1.02, 1.0, -2.4, 1.02, 1.5, 1.2)
    for z in (-1.8, 1.8):
        for x in (-1.0, 1.0):
            with m.at(x, .38, z, math.pi / 2): m.cyl("black", 0, -.12, 0, .38, .38, .24, n=8)
    m.box("metal", -.6, 2.2, -2.2, .6, 2.3, 1.0)
    for z in (-1.8, -.6, .6): m.box("metal", -.6, 2.3, z, .6, 2.36, z + .08)

def p_pizza(m):           # Scavo's Pizzeria box + the twins' bikes
    m.box("pizza_box", -.4, 0, -.4, .4, .1, .4)
    m.box("red", -.4, .1, -.4, .4, .11, -.25)
    for i, (x, z, a) in enumerate([(1.4, .2, .4), (1.9, -.8, -.6)]):
        with m.at(x, 0, z, a):
            for zz in (-.55, .55):
                for k in range(8):
                    a0 = 2 * math.pi * k / 8
                    m.box("black", -.03, .35 + .32 * math.sin(a0) - .03, zz + .32 * math.cos(a0) - .03,
                          .03, .35 + .32 * math.sin(a0) + .03, zz + .32 * math.cos(a0) + .03)
            m.solid("car_bl" if i else "car_rd", [[(-.03, .35, -.55), (.03, .35, -.55), (.03, .75, .3), (-.03, .75, .3)],
                                                  [(-.03, .42, -.55), (.03, .42, -.55), (.03, .82, .3), (-.03, .82, .3)]])
            m.box("black", -.12, .82, -.2, .12, .88, .05); m.box("metal", -.3, .95, .45, .3, 1.0, .5)

def p_binoculars(m):      # Mrs Huber's binoculars on the window sill
    m.box("trim", -.6, 0, -.15, .6, .08, .2)
    for x in (-.11, .11):
        with m.at(x, .2, 0, 0):
            m.push(); m.cyl("black", 0, -.12, 0, .09, .09, .34, n=8); m.pop()
    m.box("black", -.06, .15, -.04, .06, .25, .04)

def p_cats(m):            # Ida Greenberg's cats
    for i, (x, z, a, col) in enumerate([(0, 0, .3, "cat_or"), (1.1, .6, -1.2, "cat_gr"), (-.9, .9, 2.0, "cat_bk")]):
        with m.at(x, 0, z, a):
            m.blob(col, 0, .22, 0, .16, .15, .28, i)
            m.blob(col, 0, .38, .28, .12, .11, .11, i + 3)
            for s in (-1, 1): m.poly(col, [(s * .05, .46, .3), (s * .11, .46, .3), (s * .08, .56, .3)], up=(0, 0, 1))
            m.cyl(col, 0, .2, -.28, .03, .02, .35, n=4)

def p_poker(m):           # the Thursday poker table
    m.cyl("trunk", 0, 0, 0, .12, .12, .75, n=6)
    m.cyl("felt", 0, .75, 0, 1.0, 1.0, .06, n=12)
    m.cyl("door_wd", 0, .72, 0, 1.08, 1.08, .04, n=12)
    for k in range(4):
        a = k * math.pi / 2 + .4
        x, z = 1.45 * math.cos(a), 1.45 * math.sin(a)
        with m.at(x, 0, z, -a + math.pi / 2):
            m.box("white", -.25, .45, -.25, .25, .5, .25); m.box("white", -.25, .5, -.27, .25, 1.05, -.22)
            for sx in (-.2, .2):
                for sz in (-.2, .2): m.box("white", sx - .03, 0, sz - .03, sx + .03, .45, sz + .03)
    for k in range(5):
        m.cyl("red" if k % 2 else "white", .3 * math.cos(k), .81, .3 * math.sin(k), .05, .05, .08 + (k % 3) * .04, n=6)
    for k in range(4): m.box("sign", -.1 + k * .06, .81, -.1, -.02 + k * .06, .815, .02)

# id, title, house, local (x, z, ry), seasons [first, last], hides house in those seasons, builder
PROPS = [
    ("letter",    "Письмо шантажиста",       "4352", (1.6, 6.3, 0),     (1, 1), False, p_letter),
    ("toychest",  "Сундук для игрушек",      "4352", (3.5, -9.6, .3),   (1, 1), False, p_toychest),
    ("cellar",    "Подвал Эпплуайтов",       "4351", (-7.4, -2.0, 0),   (2, 2), False, p_cellar),
    ("freezer",   "Морозильник Карен",       "4358", (7.2, -2.0, -.4),  (4, 4), False, p_freezer),
    ("ruins",     "Пепелище Иди",            "4362", (0, 0, 0),         (1, 1), True,  p_ruins),
    ("tornado",   "Торнадо",                 "4358", (0, 0, 0),         (4, 4), True,  p_tornado),
    ("plane",     "Упавший самолёт",         "4360", (0, 9.5, .2),      (6, 6), False, p_plane),
    ("towel",     "Полотенце в кустах",      "4353", (-5.6, 5.6, 0),    (1, 1), False, p_towel),
    ("mower",     "Газонокосилка садовника", "4349", (-6.5, 11.0, .6),  (1, 1), False, p_mower),
    ("muffins",   "Корзина маффинов",        "4350", (0, 5.6, 0),       (1, 8), False, p_muffins),
    ("van",       "Фургон «Delfino Plumbing»", "4356", (8.6, 9.0, 0),   (1, 5), False, p_van),
    ("pizza",     "Пицца и велосипеды",      "4355", (3.0, 12.0, .2),   (3, 8), False, p_pizza),
    ("binoculars","Бинокль миссис Хубер",    "4350", (-2.6, 4.12, 0),   (1, 1), False, p_binoculars),
    ("cats",      "Кошки Иды Гринберг",      "4347", (-5.0, 10.5, 0),   (1, 4), False, p_cats),
    ("poker",     "Стол для покера",         "4355", (0, -9.5, 0),      (1, 8), False, p_poker),
]

def build_props():
    """[(id, mesh, world (x, z), world ry, seasons, hides, title)]"""
    plan = {hid: (x, z, ry) for hid, x, z, ry in PLAN}
    out = []
    for pid, title, hid, (lx, lz, lr), seasons, hides, fn in PROPS:
        X, Z, R = plan[hid]
        c, s = math.cos(R), math.sin(R)
        wx, wz = X + lx * c + lz * s, Z - lx * s + lz * c
        mesh = Mesh("art_" + pid); fn(mesh)
        out.append((pid, mesh, (wx, wz), R + lr, seasons, hides, title, hid))
    return out

# --------------------------------------------------------------------------
# 8. The land: road, Circle Drive, sidewalks, lamp posts, street trees
# --------------------------------------------------------------------------
def _strip(L, mat, a, b, y, step=1, P=None):
    """Band between signed offsets a..b from the centreline, at height y."""
    P = P or ROAD
    pts = P[::step] + ([P[-1]] if (len(P) - 1) % step else [])
    def off(i, d):
        j0, j1 = max(i-1, 0), min(i+1, len(pts)-1)
        tx, tz = pts[j1][0]-pts[j0][0], pts[j1][1]-pts[j0][1]; l = math.hypot(tx, tz) or 1
        nx, nz = tz/l, -tx/l
        return (pts[i][0] + nx*d, y, pts[i][1] + nz*d)
    for i in range(len(pts) - 1):
        L.poly(mat, [off(i, a), off(i, b), off(i+1, b), off(i+1, a)], up=(0, 1, 0))

# The lane continues north past 4344/4347 to a cross street; both run on into the haze.
_J = (-6.0, -192.0)
EXT_CTRL = [
    [ROAD[0], (-3.7, -126.0), (-5.5, -160.0), _J, (-3.0, -235.0), (9.0, -300.0), (-7.0, -380.0), (3.0, -495.0)],
    [(-430.0, -204.0), (-300.0, -198.0), (-180.0, -186.0), (-90.0, -194.0), _J, (80.0, -186.0), (180.0, -197.0), (300.0, -188.0), (440.0, -198.0)],
]
EXT = [_catmull(c, n=10) for c in EXT_CTRL]

def _dist_poly(P, x, z):
    best = 1e9
    for i in range(len(P) - 1):
        (ax, az), (bx, bz) = P[i], P[i+1]
        dx, dz = bx-ax, bz-az; L2 = dx*dx + dz*dz or 1
        t = max(0, min(1, ((x-ax)*dx + (z-az)*dz) / L2))
        best = min(best, math.hypot(x - ax - t*dx, z - az - t*dz))
    return best

def dist_ext(x, z):
    return min(_dist_poly(P, x, z) for P in EXT)

def dist_to_road(x, z):
    return min(dist_main(x, z), dist_ext(x, z))

def _poly_at(P, s):
    acc = 0.0
    for i in range(1, len(P)):
        l = math.dist(P[i], P[i-1])
        if acc + l >= s or i == len(P) - 1:
            f = max(0.0, min(1.0, (s - acc) / (l or 1))); a, b = P[i-1], P[i]
            t = ((b[0]-a[0])/(l or 1), (b[1]-a[1])/(l or 1))
            return (a[0] + (b[0]-a[0])*f, a[1] + (b[1]-a[1])*f), t, (t[1], -t[0])
        acc += l

def build_ext_roads(L, tree=None, oak=None, pine=None, cypress=None, palm=None):
    """Approach and cross street: asphalt, curbs, dashes, a lamp now and then, verge trees fading into the haze."""
    G = globals(); tree, oak, pine, cypress, palm = [f or G[n] for f, n in ((tree, "tree"), (oak, "oak"), (pine, "pine"), (cypress, "cypress"), (palm, "palm"))]
    hw = ROAD_W / 2
    for k, P in enumerate(EXT):
        for sd in (-1, 1): _strip(L, "curb", sd*hw, sd*(hw + .3), .1, P=P)
        _strip(L, "road", -hw, hw, .05, P=P)
        length = sum(math.dist(P[i], P[i-1]) for i in range(1, len(P)))
        s = 4.0
        while s < length - 4:
            (p, t, _), (q, _t, _m) = _poly_at(P, s), _poly_at(P, s + 2.4)
            if math.hypot(p[0] - _J[0], p[1] - _J[1]) > hw + 2:
                nx, nz = t[1] * .08, -t[0] * .08
                L.poly("mark", [(p[0]-nx, .07, p[1]-nz), (p[0]+nx, .07, p[1]+nz), (q[0]+nx, .07, q[1]+nz), (q[0]-nx, .07, q[1]-nz)], up=(0, 1, 0))
            s += 5.0
        s, j = 22.0 if k == 0 else 8.0, 0
        while s < length - 6:
            p, t, nn = _poly_at(P, s); side = 1 if j % 2 else -1
            x, z = p[0] + nn[0]*(hw + 1.2)*side, p[1] + nn[1]*(hw + 1.2)*side
            if dist_main(x, z) > 12 and abs(p[1]) < 330 and abs(p[0]) < 260: lamp_post(L, x, z)
            s += 36.0; j += 1
        # verge trees, now one side now the other, sometimes a small grove
        s, j = 10.0, 0
        while s < length - 4:
            p, t, nn = _poly_at(P, s); side = -1 if (j * 7) % 3 else 1
            d = hw + 3.5 + (j * 5 % 4)
            x, z = p[0] + nn[0]*d*side, p[1] + nn[1]*d*side
            if dist_main(x, z) > 16 and dist_ext(x, z) > hw + 2.5 and min(math.hypot(x - a, z - b) for _, a, b, _r in PLAN) > 18:
                y = ground_h(x, z)
                with L.at(0, y - .1, 0):
                    r = (j * 37 % 11) / 11
                    if y > 9: pine(L, x, z, .9 + r * .3, j)
                    elif r < .4: oak(L, x, z, .8 + r * .4, j)
                    elif r < .6: cypress(L, x, z, .9, j)
                    elif r < .75: palm(L, x, z, .9 + r * .2, j)
                    else: tree(L, x, z, .85 + r * .3, "leaf" if j % 2 else "leaf2", j * 1.3)
                if j % 4 == 0:
                    for q in range(3):
                        qx, qz = x + nn[0] * side * (5 + q * 4) + t[0] * (q - 1) * 3, z + nn[1] * side * (5 + q * 4) + t[1] * (q - 1) * 3
                        if dist_ext(qx, qz) > hw + 2.5 and dist_main(qx, qz) > 16:
                            with L.at(0, ground_h(qx, qz) - .1, 0): (pine if ground_h(qx, qz) > 8 else tree)(L, qx, qz, .8 + q * .1, j + q * .3)
            s += 13.0 + (j * 3 % 5); j += 1

def dist_main(x, z):
    best = 1e9
    for i in range(0, len(ROAD) - 1):
        (ax, az), (bx, bz) = ROAD[i], ROAD[i+1]
        dx, dz = bx-ax, bz-az; L2 = dx*dx + dz*dz or 1
        t = max(0, min(1, ((x-ax)*dx + (z-az)*dz) / L2))
        best = min(best, math.hypot(x - ax - t*dx, z - az - t*dz))
    return min(best, math.hypot(x - CUL[0], z - CUL[1]) - CUL_R)

# --------------------------------------------------------------------------
# 8c. Landscape: flat street & lots, rolling lawns behind, golden Hollywood-style hills
# --------------------------------------------------------------------------
LAND_X = (-135, 144); LAND_Z = (-171, 153)      # detailed area, on the 9 m lattice of the far terrain
FAR_X = (-414, 423); FAR_Z = (-495, 477)        # rolling hills out to the haze

def _noise(x, z):
    return (math.sin(x * .045 + 1.3) * math.cos(z * .038 - .7) * .55 + math.sin(x * .11 + z * .07) * .25
            + math.cos(x * .021 - z * .029 + 2.1) * .6 + math.sin(z * .13 - x * .05) * .12)

_LOTS_CACHE = None
def ground_h(x, z):
    """Terrain height: zero along the street and lots, rising into hills further out."""
    global _LOTS_CACHE
    if _LOTS_CACHE is None: _LOTS_CACHE = [(a, b) for _, a, b, _r in PLAN]
    d = dist_main(x, z)
    dl = min(math.hypot(x - a, z - b) for a, b in _LOTS_CACHE)
    flat = min(d - 34, dl - 22, dist_ext(x, z) - 12)
    if flat <= 0: return 0.0
    t = min(1.0, flat / 55.0); t = t * t * (3 - 2 * t)
    # hills grow toward the north-east, like the Hollywood Hills above Colonial Street
    big = .5 + .5 * max(0.0, min(1.0, (x * .4 - z * .6 + 60) / 160))
    return t * (3.5 + 9 * big + 7 * big * (_noise(x, z) + 1)) + .6 * t * _noise(z * 1.7, x * 1.3)

def _terrain_mat(hy, slope):
    return "lawn" if hy < 2.5 else ("meadow" if hy < 9 and slope > .82 else ("hill_dry" if hy > 14 or slope < .8 else "meadow_dk"))

def _grid(L, x0, z0, nx, nz, step, H, skip=None):
    for j in range(nz):
        for i in range(nx):
            if skip and skip(i, j): continue
            xa, za = x0 + i * step, z0 + j * step
            a = (xa, H[j][i], za); b = (xa + step, H[j][i+1], za)
            c = (xa + step, H[j+1][i+1], za + step); d = (xa, H[j+1][i], za + step)
            for tri in ((a, b, c), (a, c, d)) if (i + j) % 2 else ((a, b, d), (b, c, d)):
                hy = sum(p[1] for p in tri) / 3
                if hy < .05: continue                       # flat: the lawn plane shows through
                n = _newell(list(tri)); slope = abs(n[1]) / (math.sqrt(_dot(n, n)) or 1)
                L.poly(_terrain_mat(hy, slope), list(tri), up=(0, 1, 0))

def build_terrain(L, step=3.0, far=9.0):
    """Fine 3 m grid around the street, 9 m grid out to the horizon; the seam is welded
    by giving fine edge vertices the heights the coarse grid would interpolate there."""
    k = int(far / step)
    # far ring
    fnx, fnz = int((FAR_X[1] - FAR_X[0]) / far), int((FAR_Z[1] - FAR_Z[0]) / far)
    FH = [[ground_h(FAR_X[0] + i * far, FAR_Z[0] + j * far) for i in range(fnx + 1)] for j in range(fnz + 1)]
    i0, i1 = int((LAND_X[0] - FAR_X[0]) / far), int((LAND_X[1] - FAR_X[0]) / far)
    j0, j1 = int((LAND_Z[0] - FAR_Z[0]) / far), int((LAND_Z[1] - FAR_Z[0]) / far)
    _grid(L, FAR_X[0], FAR_Z[0], fnx, fnz, far, FH, skip=lambda i, j: i0 <= i < i1 and j0 <= j < j1)
    # detailed centre
    nx, nz = int((LAND_X[1] - LAND_X[0]) / step), int((LAND_Z[1] - LAND_Z[0]) / step)
    xs = [LAND_X[0] + i * step for i in range(nx + 1)]; zs = [LAND_Z[0] + j * step for j in range(nz + 1)]
    H = [[ground_h(x, z) for x in xs] for z in zs]
    for j in range(nz + 1):
        for i in range(nx + 1):
            on_edge = i in (0, nx) or j in (0, nz)
            if not on_edge or (i % k == 0 and j % k == 0): continue
            if i in (0, nx):                                  # left/right edge: lerp along z
                fi = i0 + i // k; jj = j0 + j // k; f = (j % k) / k
                H[j][i] = FH[jj][fi] * (1 - f) + FH[jj + 1][fi] * f
            else:                                             # top/bottom edge: lerp along x
                fj = j0 + j // k; ii = i0 + i // k; f = (i % k) / k
                H[j][i] = FH[fj][ii] * (1 - f) + FH[fj][ii + 1] * f
    _grid(L, LAND_X[0], LAND_Z[0], nx, nz, step, H)
    L.box("lawn", FAR_X[0], -.3, FAR_Z[0], FAR_X[1], -.01, FAR_Z[1])

# ---- more kinds of trees
def oak(m, x, z, s=1.0, seed=0.0):
    _trunk(m, x, z, s * 1.2, 3.2 * s, .3 * math.sin(seed))
    for i in range(3):
        a = seed + i * 2.1
        m.cyl("trunk", x, 2.4 * s, z, .14 * s, .07 * s, 1.8 * s, n=4, rot=a)
    _crown(m, x, 4.6 * s, z, 2.5 * s, seed, ("oak", "oak_lt", "leaf2"))
    for i in range(3):
        a = seed * .7 + i * 2.1
        _crown(m, x + math.cos(a) * 2.1 * s, 4.0 * s, z + math.sin(a) * 2.1 * s, 1.35 * s, seed + i * 3, ("oak_lt", "oak", "leaf_lt"))

def cypress(m, x, z, s=1.0, seed=0.0):
    m.cyl("trunk", x, 0, z, .14*s, .1*s, .8*s, n=5)
    for k in range(5):
        r = (.8 - .08 * k) * s
        m.blob("cypress" if k % 2 else "pine_lt", x, (1.2 + k * 1.1) * s, z, r, .9 * s, r, seed + k)
    m.cyl("cypress", x, 6.1 * s, z, .45 * s, 0, 1.4 * s, n=6, rot=seed)

def pine(m, x, z, s=1.0, seed=0.0):
    m.cyl("trunk", x, 0, z, .22 * s, .14 * s, 1.3 * s, n=5)
    mats = ("pine", "pine_lt", "pine", "pine_lt")
    for k in range(4):
        r = (2.0 - .4 * k) * s; y = (1.0 + 1.15 * k) * s
        _jag_cone(m, mats[k], x, y, z, r, 1.9 * s, n=9, rot=seed + k * .37)

def palm(m, x, z, s=1.0, seed=0.0):
    lean = .6 * math.sin(seed)
    for k in range(7):
        m.cyl("palm_trunk", x + lean * k / 7, k * 1.3 * s, z, .28*s - k*.015, .26*s - k*.015, 1.3*s, n=6)
    tx, ty = x + lean, 9.1 * s
    for k in range(8):
        a = seed + k * math.pi / 4
        with m.at(tx, ty, z, a):
            m.solid("palm_leaf", [[(-.25, 0, 0), (.25, 0, 0), (.08, -1.4*s, 3.2*s), (-.08, -1.4*s, 3.2*s)],
                                  [(-.25, .08, 0), (.25, .08, 0), (.08, -1.32*s, 3.2*s), (-.08, -1.32*s, 3.2*s)]])
    m.blob("palm_trunk", tx, ty, z, .45*s, .4*s, .45*s, seed)

def bloom(m, x, z, s=1.0, seed=0.0, kind="jacaranda"):
    m.cyl("trunk", x, 0, z, .2*s, .14*s, 2.2*s, n=6)
    for k, (dx, dy, dz, r) in enumerate([(0, 3.2, 0, 1.9), (1.2, 2.8, .6, 1.2), (-1.1, 3.0, -.5, 1.3), (.2, 4.0, -.6, 1.1)]):
        m.blob(kind if k % 2 == 0 else kind + "_lt", x + dx*s, dy*s, z + dz*s, r*s, r*.8*s, r*s, seed + k)

def flower_patch(m, x, z, seed=0):
    cols = ("rose", "flower_y", "wisteria", "white", "jacaranda_lt")
    for k in range(9):
        a = seed * 1.7 + k * 2.4; r = .5 + (k % 3) * .5
        px, pz = x + r * math.cos(a), z + r * math.sin(a)
        m.cyl("hedge", px, 0, pz, .03, .03, .35, n=3)
        m.blob(cols[(k + int(seed)) % 5], px, .42, pz, .17, .12, .17, seed + k)
    grass(m, x + .4, z - .6, seed)

def bush(m, x, z, s=1.0, seed=0.0, berries=None):
    """Layered garden shrub: a cluster of puffs in two greens, optional berries/blossoms."""
    for i in range(4):
        a = seed + i * 1.6; r = (.55 + .2 * (i % 2)) * s
        m.blob("hedge" if i % 2 else "hedge_lt", x + math.cos(a) * .45 * s, r * .8, z + math.sin(a) * .45 * s, r, r * .8, r, seed + i)
    m.blob("leaf_lt", x, 1.0 * s, z, .55 * s, .45 * s, .55 * s, seed + 7)
    if berries:
        for i in range(7):
            a = seed * 2 + i * .9; h = .55 + (i % 3) * .2
            m.blob(berries, x + math.cos(a) * .75 * s, h * s, z + math.sin(a) * .75 * s, .09, .09, .09, i)

def grass(m, x, z, seed=0.0, s=1.0):
    for i in range(6):
        a = seed + i * 1.05; lx, lz = math.cos(a) * .12, math.sin(a) * .12
        tip = (x + lx * 5, (.55 + .2 * (i % 3)) * s, z + lz * 5)
        m.poly("grass_tuft" if i % 2 else "hedge_lt", [(x - lz, 0, z + lx), (x + lz, 0, z - lx), tip], up=(lx, .3, lz))
        m.poly("grass_tuft" if i % 2 else "hedge_lt", [(x + lz, 0, z - lx), (x - lz, 0, z + lx), tip], up=(-lx, .3, -lz))

def rock(m, x, z, s=1.0, seed=0.0):
    m.blob("rock", x, .25 * s, z, .8 * s, .55 * s, .65 * s, seed)
    m.blob("rock_lt", x + .5 * s, .18 * s, z + .3 * s, .4 * s, .3 * s, .35 * s, seed + 2)

def stump(m, x, z, s=1.0, seed=0.0):
    m.cyl("trunk", x, 0, z, .45 * s, .38 * s, .5 * s, n=7, rot=seed)
    m.cyl("wood_cut", x, .5 * s, z, .36 * s, .36 * s, .03, n=7, rot=seed)

def pergola(m, x, z, ry=0.0, n=6):
    with m.at(x, 0, z, ry):
        for i in range(n):
            for sx in (-1.6, 1.6):
                m.cbox("trim", sx, 0, -n * 1.1 + i * 2.2 + 1.1, .22, 2.8, .22)
        m.box("trim", -1.75, 2.8, -n * 1.1, -1.45, 3.05, n * 1.1); m.box("trim", 1.45, 2.8, -n * 1.1, 1.75, 3.05, n * 1.1)
        for i in range(n * 2 + 1):
            zz = -n * 1.1 + i * 1.1
            m.box("trim", -2.1, 3.05, zz - .07, 2.1, 3.2, zz + .07)
        for i in range(n * 2):
            zz = -n * 1.1 + .55 + i * 1.1
            m.blob("leaf" if i % 3 else "leaf2", (-1 if i % 2 else 1) * .8, 3.35, zz, .9, .35, .7, i)
            m.cyl("wisteria" if i % 2 else "wisteria2", (-1 if i % 2 else 1) * 1.4, 2.2, zz, .05, .32, 1.0, n=6, rot=i)
            m.cyl("wisteria2" if i % 2 else "wisteria", (1 if i % 2 else -1) * .3, 2.4, zz + .3, .05, .28, .8, n=6, rot=i + 1)

import inspect, json as _json
def _scat(fn, rec):
    sig = inspect.signature(fn)
    def w(m, x, z, *a, **kw):
        b = sig.bind(m, x, z, *a, **kw); b.apply_defaults(); A = dict(b.arguments)
        sc = A.pop("s", 1.0); seed = A.pop("seed", 0.0); A.pop("m"); A.pop("x"); A.pop("z")
        var = int(abs(seed) * 7.13) % 3
        key = fn.__name__ + "|" + _json.dumps(A, sort_keys=True) + "|" + str(var)
        y = m.tf((0, 0, 0))[1]
        e = rec.setdefault(key, {"fn": fn, "kw": A, "var": var, "has_s": "s" in sig.parameters, "inst": []})
        e["inst"] += [round(x, 2), round(y, 2), round(z, 2), round(sc, 3), round((seed * 2.399) % 6.283, 3)]
    return w

def build_kit(rec):
    out = []
    for key, e in rec.items():
        M = Mesh(key); kw = dict(e["kw"]); kw["seed"] = e["var"] * 3.7 + 1
        if e["has_s"]: kw["s"] = 1.0
        e["fn"](M, 0, 0, **kw); out.append((key, M, e["inst"]))
    return out

def build_land(scatter=None):
    if scatter is not None:
        tree, oak, pine, cypress, bloom, palm, wisteria_tree, bush, rock, stump, grass, wildflowers, pebbles, flower_patch = [
            _scat(f, scatter) for f in (globals()[n] for n in ("tree", "oak", "pine", "cypress", "bloom", "palm", "wisteria_tree", "bush", "rock", "stump", "grass", "wildflowers", "pebbles", "flower_patch"))]
    else:
        G = globals(); tree, oak, pine, cypress, bloom, palm, wisteria_tree, bush, rock, stump, grass, wildflowers, pebbles, flower_patch = [
            G[n] for n in ("tree", "oak", "pine", "cypress", "bloom", "palm", "wisteria_tree", "bush", "rock", "stump", "grass", "wildflowers", "pebbles", "flower_patch")]
    L = Mesh("land")
    build_terrain(L)
    hw = ROAD_W / 2
    for s in (-1, 1):
        _strip(L, "curb", s*hw, s*(hw + .25), .14)
        _strip(L, "walk", s*(hw + .25), s*(hw + .25 + WALK_W), .1)
    _strip(L, "road", -hw, hw, .05)
    build_ext_roads(L, tree, oak, pine, cypress, palm)
    n = 40
    ring = lambda r, y: [(CUL[0] + r*math.cos(2*math.pi*i/n), y, CUL[1] + r*math.sin(2*math.pi*i/n)) for i in range(n)]
    L.poly("walk", ring(CUL_R + WALK_W + .25, .1), up=(0, 1, 0))
    L.poly("curb", ring(CUL_R + .25, .12), up=(0, 1, 0))
    L.poly("road", ring(CUL_R, .14), up=(0, 1, 0))
    # island with a wisteria
    L.cyl("curb", CUL[0], 0, CUL[1], ISLAND_R + .25, ISLAND_R + .25, .3, n=24)
    L.cyl("lawn2", CUL[0], .3, CUL[1], ISLAND_R, ISLAND_R, .06, n=24)
    wisteria_tree(L, CUL[0], CUL[1], 1.3, 2.0)
    # dashed centre line that follows the bends
    s = 3.0
    while s < ROAD_LEN - 6:
        (p, t, _n), (q, _t, _m) = road_at(s), road_at(s + 2.4)
        nx, nz = t[1] * .08, -t[0] * .08
        L.poly("mark", [(p[0]-nx, .07, p[1]-nz), (p[0]+nx, .07, p[1]+nz), (q[0]+nx, .07, q[1]+nz), (q[0]-nx, .07, q[1]-nz)], up=(0, 1, 0))
        s += 5.0
    # lamp posts on alternating sides
    s, k = 10.0, 0
    while s < ROAD_LEN - 8:
        p, t, nn = road_at(s); side = 1 if k % 2 else -1
        d = hw + WALK_W + 1.0
        lamp_post(L, p[0] + nn[0]*d*side, p[1] + nn[1]*d*side)
        s += 17.0; k += 1
    # street trees: big oaks along the verges, as in the aerial photo
    lots = [(x, z) for _, x, z, _r in PLAN]
    s = 18.0; k = 0
    while s < ROAD_LEN - 10:
        p, t, nn = road_at(s); side = -1 if k % 2 else 1
        d = hw + WALK_W + 2.4
        x, z = p[0] + nn[0]*d*side, p[1] + nn[1]*d*side
        if min(math.hypot(x - a, z - b) for a, b in lots) > 9:
            oak(L, x, z, .85 + (k % 3) * .1, k * 1.7)
        s += 21.0; k += 1
    # the white wisteria pergola at Circle Drive
    a = math.atan2(_tend[1], _tend[0])
    pergola(L, CUL[0] + math.cos(a + 1.9) * (CUL_R + 7), CUL[1] + math.sin(a + 1.9) * (CUL_R + 7), -a + .3)
    # woods, meadows and hills: species picked by height, kept off the road and the lots
    import random
    rnd = random.Random(7)
    placed = tries = 0
    while placed < 430 and tries < 30000:
        tries += 1
        x, z = rnd.uniform(LAND_X[0] + 4, LAND_X[1] - 4), rnd.uniform(LAND_Z[0] + 4, LAND_Z[1] - 4)
        dr = dist_to_road(x, z)
        if dr < 9: continue
        if min(math.hypot(x - a, z - b) for a, b in lots) < 17: continue
        if dr < 36 and rnd.random() < .3: continue
        y = ground_h(x, z); r = rnd.random(); sc = .85 + rnd.random() * .45
        with L.at(0, y - .1, 0):
            if y > 12:
                (pine if r < .75 else cypress)(L, x, z, sc, placed)
                for q in range(2):
                    qx, qz = x + rnd.uniform(-4, 4), z + rnd.uniform(-4, 4)
                    with L.at(0, ground_h(qx, qz) - y, 0): pine(L, qx, qz, sc * rnd.uniform(.7, 1.0), placed + q + .5)
            elif y > 3:
                if r < .35: oak(L, x, z, sc, placed)
                elif r < .6: pine(L, x, z, sc, placed)
                elif r < .75: cypress(L, x, z, sc, placed)
                elif r < .88: bloom(L, x, z, sc, placed, "jacaranda")
                else: flower_patch(L, x, z, placed)
            else:
                if r < .22: wisteria_tree(L, x, z, sc, placed)
                elif r < .42: oak(L, x, z, sc, placed)
                elif r < .55: bloom(L, x, z, sc, placed, "jacaranda" if placed % 2 else "magnolia")
                elif r < .65: palm(L, x, z, sc, placed)
                elif r < .78: cypress(L, x, z, sc, placed)
                elif r < .84: flower_patch(L, x, z, placed)
                elif r < .9: bush(L, x, z, sc, placed, "berry" if placed % 3 == 0 else ("rose" if placed % 3 == 1 else None))
                else: tree(L, x, z, sc, "leaf" if placed % 2 else "leaf2", placed * 1.3)
            if r > .5 and y < 9:
                if placed % 3 == 0: rock(L, x + 2.6, z + 1.4, .9, placed)
                elif placed % 7 == 0: stump(L, x + 2.6, z + 1.4, .9, placed)
                else: grass(L, x + 2.6, z + 1.4, placed)
        placed += 1
    # property lines between neighbours: shrub rows with a big tree or two, like the backlot
    for side in (1, -1):
        ss = sorted(sv for _, sv, sd in LOTS if sd == side)
        for a_s, b_s in zip(ss, ss[1:]):
            ms = (a_s + b_s) / 2; p, t, nn = road_at(ms)
            k = 0; d = hw + WALK_W + 3.0
            while d < 36:
                x, z = p[0] + nn[0] * d * side, p[1] + nn[1] * d * side
                if dist_main(x, z) < hw + WALK_W + 1.6: d += 1.7; k += 1; continue     # a bend brings the road back: keep off it
                bush(L, x + t[0] * .4 * (k % 2), z + t[1] * .4 * (k % 2), .95 + .25 * ((k * 7) % 3) / 2, ms + k, ("rose", None, None, "berry")[k % 4])
                if k % 5 == 2 and dist_main(x + t[0] * 2.2, z + t[1] * 2.2) > hw + WALK_W + 3: (oak if k % 2 else tree)(L, x + t[0] * 2.2, z + t[1] * 2.2, .95, ms + k)
                d += 1.7; k += 1
    # verge & meadow dressing: tufts, wildflowers, rocks and shrubs everywhere near the street
    dress = 0; tries = 0
    while dress < 1500 and tries < 60000:
        tries += 1
        x, z = rnd.uniform(LAND_X[0] + 4, LAND_X[1] - 4), rnd.uniform(LAND_Z[0] + 4, LAND_Z[1] - 4)
        dr = dist_to_road(x, z)
        if dr < 7.2: continue
        if min(math.hypot(x - a, z - b) for a, b in lots) < 13: continue
        y = ground_h(x, z); r = rnd.random()
        if r > .9 and dr > 12 and y < 5:
            with L.at(0, y - .1, 0): (oak if dress % 3 == 0 else tree)(L, x, z, .8 + rnd.random() * .3, dress)
            dress += 1; continue
        with L.at(0, y - .05, 0):
            if r < .45: grass(L, x, z, dress, 1.0 + rnd.random() * .4)
            elif r < .68: wildflowers(L, x, z, 5 + dress % 4, dress, ("flower_y", "white", "wisteria", "rose") if y < 6 else ("flower_y", "white", "hill_dry"))
            elif r < .8: pebbles(L, x, z, dress)
            elif r < .88: rock(L, x, z, .7 + rnd.random() * .9, dress)
            elif r < .97: bush(L, x, z, .7 + rnd.random() * .5, dress, ("berry", None, "rose", None)[dress % 4])
            else: stump(L, x, z, .8, dress)
        dress += 1
    # shrubs and flower beds lining the sidewalks
    s = 6.0; k = 0
    while s < ROAD_LEN - 6:
        p, t, nn = road_at(s)
        for side in (-1, 1):
            d = hw + WALK_W + 1.1
            x, z = p[0] + nn[0] * d * side, p[1] + nn[1] * d * side
            if min(math.hypot(x - a, z - b) for a, b in lots) > 7.5:
                grass(L, x, z, k) if k % 3 else wildflowers(L, x, z, seed=k)
        s += 3.3; k += 1
    # a few benches along the lane and at Circle Drive
    for sa in (40, 95, 150):
        p, t, nn = road_at(sa); d = hw + WALK_W + 1.4
        bench(L, p[0] - nn[0] * d, p[1] - nn[1] * d, math.atan2(nn[0], nn[1]) + math.pi)
    # sparse woods on the far hills, fading into the haze
    far_n = 0
    while far_n < 110:
        x, z = rnd.uniform(FAR_X[0] + 20, FAR_X[1] - 20), rnd.uniform(FAR_Z[0] + 20, FAR_Z[1] - 20)
        if LAND_X[0] - 6 < x < LAND_X[1] + 6 and LAND_Z[0] - 6 < z < LAND_Z[1] + 6: continue
        if math.hypot(x, z) > 340: continue
        y = ground_h(x, z); sc = 1.0 + rnd.random() * .6
        with L.at(0, y - .1, 0):
            for q in range(2):
                qx, qz = x + rnd.uniform(-5, 5), z + rnd.uniform(-5, 5)
                with L.at(0, ground_h(qx, qz) - y, 0):
                    (pine if y > 8 or rnd.random() < .7 else cypress)(L, qx, qz, sc * rnd.uniform(.8, 1.1), far_n + q)
        far_n += 1
    return L

# --------------------------------------------------------------------------
# 9. glTF writer (positions + flat normals, one primitive per material)
# --------------------------------------------------------------------------
def mat_def(name):
    """Palette entry; '<base>_dk' / '<base>_lt' are derived shades of a base colour."""
    if name in MAT: return MAT[name]
    for suf, k in (("_dk", .86), ("_lt", 1.12)):
        if name.endswith(suf) and name[:-len(suf)] in MAT:
            col, rough = MAT[name[:-len(suf)]]
            r, g, b = (min(255, int(int(col[i:i+2], 16) * k)) for i in (1, 3, 5))
            return ("#%02x%02x%02x" % (r, g, b), rough)
    raise KeyError(name)

def _hex_lin(h):
    def c(v):
        v = int(v, 16) / 255
        return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    return [c(h[1:3]), c(h[3:5]), c(h[5:7]), 1.0]

class GLTF:
    def __init__(self):
        self.j = {"asset": {"version": "2.0", "generator": "wl_model.py"}, "scenes": [{"nodes": []}], "scene": 0,
                  "nodes": [], "meshes": [], "materials": [], "accessors": [], "bufferViews": [], "buffers": []}
        self.bin = bytearray(); self.mats = {}
    def mat(self, name):
        if name not in self.mats:
            col, rough = mat_def(name)
            self.mats[name] = len(self.j["materials"])
            self.j["materials"].append({"name": name, "pbrMetallicRoughness": {"baseColorFactor": _hex_lin(col), "metallicFactor": 0.0, "roughnessFactor": rough},
                                        "doubleSided": name in ("leaf", "leaf2", "wisteria", "wisteria2", "red", "palm_leaf", "soil")})
        return self.mats[name]
    def _view(self, data, target):
        while len(self.bin) % 4: self.bin.append(0)
        off = len(self.bin); self.bin += data
        self.j["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target})
        return len(self.j["bufferViews"]) - 1
    def mesh(self, M, normals=True, quant=0):
        prims = []
        for mname, polys in M.parts.items():
            P, N = [], []
            for pl in polys:
                n = _newell(pl); l = math.sqrt(_dot(n, n)) or 1; n = (n[0]/l, n[1]/l, n[2]/l)
                for i in range(1, len(pl) - 1):
                    for q in (pl[0], pl[i], pl[i+1]): P.extend(q); N.extend(n)
            if not P: continue
            cnt = len(P) // 3
            xs, ys, zs = P[0::3], P[1::3], P[2::3]
            a = len(self.j["accessors"])
            if quant:                       # KHR_mesh_quantization: int16 positions, node scales back by 1/quant
                Q = [max(-32767, min(32767, int(round(v * quant)))) for v in P]
                qx, qy, qz = Q[0::3], Q[1::3], Q[2::3]
                data = b"".join(struct.pack("<3hxx", Q[i], Q[i+1], Q[i+2]) for i in range(0, len(Q), 3))
                pv = self._view(data, 34962); self.j["bufferViews"][pv]["byteStride"] = 8
                self.j["accessors"].append({"bufferView": pv, "componentType": 5122, "count": cnt, "type": "VEC3",
                                            "min": [min(qx), min(qy), min(qz)], "max": [max(qx), max(qy), max(qz)]})
                for ext in ("extensionsUsed", "extensionsRequired"):
                    self.j.setdefault(ext, [])
                    if "KHR_mesh_quantization" not in self.j[ext]: self.j[ext].append("KHR_mesh_quantization")
            else:
                pv = self._view(struct.pack("<%df" % len(P), *P), 34962)
                self.j["accessors"].append({"bufferView": pv, "componentType": 5126, "count": cnt, "type": "VEC3",
                                            "min": [min(xs), min(ys), min(zs)], "max": [max(xs), max(ys), max(zs)]})
            attrs = {"POSITION": a}
            if normals and quant:
                NB = b"".join(struct.pack("<3bx", *[max(-127, min(127, int(round(v * 127)))) for v in N[i:i+3]]) for i in range(0, len(N), 3))
                nv = self._view(NB, 34962); self.j["bufferViews"][nv]["byteStride"] = 4
                self.j["accessors"].append({"bufferView": nv, "componentType": 5120, "normalized": True, "count": cnt, "type": "VEC3"})
                attrs["NORMAL"] = len(self.j["accessors"]) - 1
            elif normals:
                nv = self._view(struct.pack("<%df" % len(N), *N), 34962)
                self.j["accessors"].append({"bufferView": nv, "componentType": 5126, "count": cnt, "type": "VEC3"})
                attrs["NORMAL"] = a + 1
            prims.append({"attributes": attrs, "material": self.mat(mname)})
        self.j["meshes"].append({"name": M.name, "primitives": prims})
        return len(self.j["meshes"]) - 1
    def node(self, name, mesh=None, t=(0, 0, 0), ry=0.0, children=None, extras=None, root=False):
        n = {"name": name}
        if mesh is not None: n["mesh"] = mesh
        if any(t): n["translation"] = list(t)
        if ry: n["rotation"] = [0, math.sin(ry/2), 0, math.cos(ry/2)]
        if children: n["children"] = children
        if extras: n["extras"] = extras
        self.j["nodes"].append(n); i = len(self.j["nodes"]) - 1
        if root: self.j["scenes"][0]["nodes"].append(i)
        return i
    def save(self, path):
        if path.endswith(".gltf"):          # single self-contained file for other tools
            self.j["buffers"] = [{"byteLength": len(self.bin), "uri": "data:application/octet-stream;base64," + base64.b64encode(bytes(self.bin)).decode()}]
        else:                               # site models: JSON + a separate .bin next to it
            binp = os.path.splitext(path)[0] + ".bin"
            with open(binp, "wb") as f: f.write(bytes(self.bin))
            self.j["buffers"] = [{"byteLength": len(self.bin), "uri": os.path.basename(binp)}]
        with open(path, "w") as f: json.dump(self.j, f, separators=(",", ":"))

Q = 256
def _qnode(g, i):
    g.j["nodes"][i]["scale"] = [1/Q, 1/Q, 1/Q]; return i

def add_house(g, h, x, z, ry, root=True, quant=False):
    q = Q if quant else 0
    body = g.node(h.id + "_body", g.mesh(h.body, quant=q)); quant and _qnode(g, body)
    kids = [body]
    for i, (kind, M, piv, r0) in enumerate(h.details):
        n = g.node("%s_%s_%d" % (h.id, kind, i), g.mesh(M, quant=q), t=piv, ry=r0, extras={"kind": kind})
        if quant:   # keep the pivot node unscaled: put the scaled mesh in a child
            g.j["nodes"][n].pop("mesh"); c = g.node("%s_%s_%d_m" % (h.id, kind, i), g.mesh(M, quant=q)); _qnode(g, c); g.j["nodes"][n]["children"] = [c]
        kids.append(n)
    return g.node(h.id, None, (x, 0, z), ry, kids, extras={"house": h.id}, root=root)

def export_all(out):
    os.makedirs(out, exist_ok=True); PUMPKINS.clear()
    scene = GLTF()
    rec = {}
    land = build_land(scatter=rec)                   # site: terrain + street, vegetation as instances
    g = GLTF(); n = g.node("land", g.mesh(land, normals=False, quant=64), root=True)
    g.j["nodes"][n]["scale"] = [1/64, 1/64, 1/64]; g.save(os.path.join(out, "land.json"))
    g = GLTF(); inst = {}; fns = {}
    for k, (key, M, I) in enumerate(build_kit(rec)):
        i = g.node("k%d" % k, g.mesh(M, quant=Q), root=True); _qnode(g, i); inst["k%d" % k] = I; fns["k%d" % k] = key.split("|")[0]
    g.save(os.path.join(out, "kit.json"))
    inst["_fn"] = fns
    for hid, (f_show, f_set) in INTERIORS.items():                     # cutaway interiors, loaded on demand
        g2 = GLTF()
        for nm, M in (("show", f_show()), ("set", f_set())):
            i = g2.node(nm, g2.mesh(M, quant=Q), root=True); _qnode(g2, i)
        g2.save(os.path.join(out, "int_%s.json" % hid))
    with open(os.path.join(out, "rooms.json"), "w") as f: json.dump(INTERIOR_ROOMS, f, ensure_ascii=False)
    with open(os.path.join(out, "scatter.json"), "w") as f: json.dump(inst, f, separators=(",", ":"))
    scene.node("land", scene.mesh(build_land()), root=True)   # the full scene keeps every plant as geometry
    stats = {}
    for hid, x, z, ry in PLAN:
        h = BUILDERS[hid]()
        g = GLTF(); add_house(g, h, 0, 0, 0, quant=True); g.save(os.path.join(out, hid + ".json"))
        add_house(scene, h, x, z, ry)
        stats[hid] = sum(len(p) for p in h.body.parts.values())
    g = GLTF(); arts = []
    for pid, mesh, (wx, wz), ry, seasons, hides, title, hid in build_props():
        _qnode(g, g.node("art_" + pid, g.mesh(mesh, quant=Q), (wx, 0, wz), ry, extras={"art": pid, "s": list(seasons), "hides": hid if hides else None}, root=True))
        scene.node("art_" + pid, scene.mesh(mesh), (wx, 0, wz), ry, root=True)
        arts.append({"id": pid, "title": title, "house": hid, "x": round(wx, 2), "z": round(wz, 2), "s": list(seasons), "hides": hid if hides else None})
    tor = [a for a in arts if a["id"] == "tornado"][0]
    _qnode(g, g.node("art_tornado_funnel", g.mesh(tornado_funnel(), quant=Q), (tor["x"] + 6, 0, tor["z"] - 6), 0, extras={"art": "tornado_funnel", "s": [4, 4]}, root=True))
    g.save(os.path.join(out, "props.json"))
    scene.save(os.path.join(out, "wisteria_lane.gltf"))
    plan = {"road": {"w": ROAD_W, "walk": WALK_W, "centre": [[round(a, 2), round(b, 2)] for a, b in ROAD], "ext": [[[round(a, 1), round(b, 1)] for a, b in P] for P in EXT]}, "pumpkins": PUMPKINS, "cul": {"c": CUL, "r": CUL_R, "island": ISLAND_R},
            "houses": [{"id": hid, "x": round(x, 3), "z": round(z, 3), "ry": round(ry, 5)} for hid, x, z, ry in PLAN],
            "arts": arts}
    with open(os.path.join(out, "plan.json"), "w") as f: json.dump(plan, f, indent=1)
    return stats

# --------------------------------------------------------------------------
# 10. Blender backend
# --------------------------------------------------------------------------
def build_in_blender(save_blend=None, export_glb=None):
    import bpy
    def mat(name):
        m = bpy.data.materials.get("WL_" + name)
        if m: return m
        col, rough = mat_def(name)
        m = bpy.data.materials.new("WL_" + name); m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        rgba = _hex_lin(col)
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = rough
        m.diffuse_color = rgba
        return m
    def to_obj(M, name, coll):
        verts, faces, mats, mi = [], [], [], {}
        for mname, polys in M.parts.items():
            mi[mname] = len(mats); mats.append(mname)
            for pl in polys:
                base = len(verts)
                verts.extend([(p[0], -p[2], p[1]) for p in pl])   # Y-up -> Z-up
                faces.append(list(range(base, base + len(pl))))
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        for mname in mats: me.materials.append(mat(mname))
        k = 0
        for mname, polys in M.parts.items():
            for _ in polys:
                me.polygons[k].material_index = mi[mname]; k += 1
        me.update()
        ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
        return ob
    # start clean: drop an earlier build of the street
    old = bpy.data.collections.get("Wisteria Lane")
    if old:
        def wipe(c):
            for ch in list(c.children): wipe(ch)
            for ob in list(c.objects): bpy.data.objects.remove(ob, do_unlink=True)
            bpy.data.collections.remove(c)
        wipe(old)
    for me in list(bpy.data.meshes):
        if me.users == 0: bpy.data.meshes.remove(me)
    root = bpy.data.collections.get("Wisteria Lane") or bpy.data.collections.new("Wisteria Lane")
    if root.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(root)
    land_c = bpy.data.collections.new("Land"); root.children.link(land_c)
    to_obj(build_land(), "land", land_c)
    for hid, x, z, ry in PLAN:
        h = BUILDERS[hid]()
        c = bpy.data.collections.new(hid + " Wisteria Lane"); root.children.link(c)
        empty = bpy.data.objects.new(hid, None); c.objects.link(empty)
        empty.location = (x, -z, 0); empty.rotation_euler = (0, 0, ry)
        body = to_obj(h.body, hid + "_body", c); body.parent = empty
        for i, (kind, M, piv, r0) in enumerate(h.details):
            ob = to_obj(M, "%s_%s_%d" % (hid, kind, i), c); ob.parent = empty
            ob.location = (piv[0], -piv[2], piv[1]); ob.rotation_euler = (0, 0, r0)
    pc = bpy.data.collections.new("Artefacts"); root.children.link(pc)
    for pid, mesh, (wx, wz), ry, seasons, hides, title, hid in build_props():
        ob = to_obj(mesh, "art_" + pid, pc); ob.location = (wx, -wz, 0); ob.rotation_euler = (0, 0, ry)
        ob["seasons"] = "%d-%d" % seasons; ob["title"] = title
        hide = pid in ("ruins", "tornado", "plane")      # seasonal disasters sit on top of houses
        if pid == "tornado":
            f = to_obj(tornado_funnel(), "art_tornado_funnel", pc); f.location = (wx + 6, -(wz - 6), 0)
            f.hide_viewport = f.hide_render = True
        ob.hide_viewport = ob.hide_render = hide
    # isometric camera like the website: looking along (1, 0.86, 1)
    scn = bpy.context.scene
    for ob in list(bpy.data.objects):
        if ob.name in ("Cube", "Camera", "Light"): bpy.data.objects.remove(ob, do_unlink=True)
    cam_d = bpy.data.cameras.new("WL_Camera"); cam_d.type = "ORTHO"; cam_d.ortho_scale = 190; cam_d.clip_end = 2000
    cam = bpy.data.objects.new("WL_Camera", cam_d); root.objects.link(cam)
    import mathutils
    d = mathutils.Vector((1, -1, 0.86)).normalized()
    target = mathutils.Vector((-25, 0, 0))
    cam.location = target + d * 400
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scn.camera = cam
    sun_d = bpy.data.lights.new("WL_Sun", "SUN"); sun_d.energy = 3.5; sun_d.angle = 0.12
    sun_d.color = (1.0, 0.95, 0.88)
    sun = bpy.data.objects.new("WL_Sun", sun_d); root.objects.link(sun)
    sun.rotation_euler = (math.radians(45), 0, math.radians(-30))
    world = scn.world or bpy.data.worlds.new("World"); scn.world = world; world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg: bg.inputs[0].default_value = (0.85, 0.89, 0.83, 1); bg.inputs[1].default_value = 0.9
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    try: scn.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception: pass
    # viewport: material colours, flat light from the camera angle
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            sp = area.spaces.active
            sp.shading.type = "SOLID"; sp.shading.color_type = "MATERIAL"
            sp.shading.show_shadows = True; sp.shading.show_cavity = True
            sp.region_3d.view_perspective = "CAMERA"
    if save_blend:
        os.makedirs(os.path.dirname(save_blend), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=save_blend)
    if export_glb: bpy.ops.export_scene.gltf(filepath=export_glb, export_format="GLB")

# --------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        import bpy  # noqa: F401
        IN_BLENDER = True
    except ImportError:
        IN_BLENDER = False
    if IN_BLENDER:
        import traceback
        base = os.path.expanduser("~/Sites/wisteria-lane/blender")
        if not os.path.isdir(base):  # anywhere else: save next to this script
            base = os.path.dirname(os.path.abspath(globals().get("__file__", "."))) or "."
        log = []
        try:
            build_in_blender()
            log.append("built ok")
            import bpy
            res = bpy.ops.wm.save_as_mainfile(filepath=os.path.join(base, "wisteria_lane.blend"))
            log.append("save: %s" % res)
            res = bpy.ops.export_scene.gltf(filepath=os.path.join(base, "wisteria_lane.glb"), export_format="GLB")
            log.append("glb: %s" % res)
        except Exception:
            log.append(traceback.format_exc())
        with open(os.path.join(base, "build_log.txt"), "w") as f: f.write("\n".join(log))
    else:
        out = sys.argv[1] if len(sys.argv) > 1 else "out"
        st = export_all(out)
        print(json.dumps(st))
