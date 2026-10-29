"""
Nape Deck prototype case v5 - arms PIVOT around the ball
================================================================
The layout itself moves: the key arm (left) and the display arm
(right) are separate parts whose collars wrap a drum on the centre
unit, so each arm swings in the horizontal plane around the ball's
axis (about +-25 deg usable). A radial set screw in each collar
locks the angle. Wires cross the pivots in a loose ring channel
around the centre unit, so rotation does not pull them.

Centre unit: ball cavity + TANBOKU screwed to its bottom via the
retainer frame (as v3); its sensor wires leave through a duct at
the back. Display arm carries the top case (display + XIAO)
screwed from the back (as v4).

Parts (8): centre / ring / retainer / wire ring / left arm /
right arm / top case / bottom cover.
Coordinates: ball centre at origin, Z up, mm. Desk level z=-24.
Arms are modelled at 0 deg (straight); rotate them when assembling.
"""

import math
from build123d import *

# ---------------- parameters ----------------
BALL_R = 17.0
CLEAR = 0.4
CAV_R = BALL_R + CLEAR
RIM_Z = BALL_R - 12.0            # +5.0
OUT_R = 23.0                     # centre unit / drum radius
BEARING_R = 3.0
BEARING_POCKET_R = BEARING_R + 0.3
BEARING_DIST = BALL_R + BEARING_R
BEARING_AZ = [30.0, 150.0, 270.0]
BEARING_TILT = 55.0
LENS_GAP = 2.0
LENS_HEIGHT = 3.4
BOARD_TOP_Z = -(BALL_R + LENS_GAP) - LENS_HEIGHT   # -22.4
BOARD_POCKET_W = 8.2
BOARD_POCKET_L = 13.0
SCREW_R = 19.0
RING_SCREW_AZ = [0.0, 90.0, 180.0, 270.0]
RET_SCREW_X = 6.0
RET_SCREW_Y = 7.5

ARM_TOP = -12.0
ARM_BOT = -21.0                  # arms ride 3mm above the desk
COLLAR_R_OUT = 29.0
COLLAR_R_IN = 23.4
COLLAR_Z0 = -21.0
COLLAR_H = 7.5                   # z -21..-13.5
COLLAR_HALF = 65.0               # degrees

DISP_CX = 44.0                   # display centre on the right arm
DISP_W, DISP_L = 31.5, 39.0      # module (verify with calipers)
DISP_TILT = 10.0
XIAO_W, XIAO_L = 17.8, 21.0
KEY_XS = [-40.0, -59.0]          # on the left arm


def cyl(r, z0, h):
    return Solid.make_cylinder(r, h, Plane(origin=(0, 0, z0)))


def cyl_at(r, z0, h, x, y):
    return Solid.make_cylinder(r, h, Plane(origin=(x, y, z0)))


def sphere_at(r, x, y, z):
    return Solid.make_sphere(r, Plane(origin=(x, y, z)))


def box_at(sx, sy, sz, x, y, z):
    return Solid.make_box(sx, sy, sz, Plane(origin=(x, y, z)))


def rrect(cx, cy, sx, sy, r, z0, h):
    p = box_at(sx - 2 * r, sy, h, cx - sx / 2 + r, cy - sy / 2, z0)
    if sy - 2 * r > 0:
        p += box_at(sx, sy - 2 * r, h, cx - sx / 2, cy - sy / 2 + r, z0)
    for dx in (-1, 1):
        for dy in (-1, 1):
            p += cyl_at(r, z0, h, cx + dx * (sx / 2 - r), cy + dy * (sy / 2 - r))
    return p


def bearing_centres():
    out = []
    for az in BEARING_AZ:
        a = math.radians(az)
        t = math.radians(BEARING_TILT)
        hr = BEARING_DIST * math.sin(t)
        out.append((hr * math.cos(a), hr * math.sin(a),
                    -BEARING_DIST * math.cos(t)))
    return out


def sector_cutter(edge_deg, side, z0, h):
    """Half-plane cutter removing angles beyond edge_deg.
    side=+1 removes the increasing-angle side, -1 the other."""
    y0 = 0.0 if side > 0 else -140.0
    return Rot(Z=edge_deg) * box_at(140.0, 140.0, h, -70.0, y0, z0)


def collar(az_center_deg):
    c = cyl(COLLAR_R_OUT, COLLAR_Z0, COLLAR_H)
    c -= cyl(COLLAR_R_IN, COLLAR_Z0, COLLAR_H)
    c -= sector_cutter(az_center_deg + COLLAR_HALF, +1, COLLAR_Z0, COLLAR_H)
    c -= sector_cutter(az_center_deg - COLLAR_HALF, -1, COLLAR_Z0, COLLAR_H)
    return c


def setscrew(az_deg):
    """Boss + radial hole for an M3 set screw at azimuth az_deg."""
    a = math.radians(az_deg)
    d = (math.cos(a), math.sin(a), 0)
    boss = Solid.make_cylinder(
        4.0, 7.0, Plane(origin=(27 * d[0], 27 * d[1], -17.25),
                        x_dir=(0, 0, 1), z_dir=d))
    hole = Solid.make_cylinder(
        1.5, 16.0, Plane(origin=(19 * d[0], 19 * d[1], -17.25),
                         x_dir=(0, 0, 1), z_dir=d))
    return boss, hole


# ---------------- top ring ----------------
ring = cyl(OUT_R, 0.0, RIM_Z)
ring -= sphere_at(CAV_R, 0, 0, 0)
for az in RING_SCREW_AZ:
    a = math.radians(az)
    ring -= cyl_at(1.3, 0.0, RIM_Z,
                   SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- centre unit ----------------
centre = cyl(OUT_R, -24.0, 24.0)                    # z -24..0
centre += cyl(29.0, -13.0, 2.0)                     # anti-lift flange
centre -= sphere_at(CAV_R, 0, 0, 0)
for (bx, by, bz) in bearing_centres():
    centre -= sphere_at(BEARING_POCKET_R, bx, by, bz)
for az in RING_SCREW_AZ:                            # M2.5 pilots
    a = math.radians(az)
    centre -= cyl_at(1.1, -8.0, 8.0,
                     SCREW_R * math.cos(a), SCREW_R * math.sin(a))
# lens window cone + TANBOKU pocket + retainer recess (as v3)
centre -= Solid.make_cone(3.5, 7.5, 5.9, Plane(origin=(0, 0, BOARD_TOP_Z)))
centre -= box_at(BOARD_POCKET_W, BOARD_POCKET_L, BOARD_TOP_Z + 24.0,
                 -BOARD_POCKET_W / 2, -BOARD_POCKET_L / 2, -24.0)
centre -= box_at(15.4, 19.4, 0.9, -7.7, -9.7, -24.0)
for sx in (-RET_SCREW_X, RET_SCREW_X):
    for sy in (-RET_SCREW_Y, RET_SCREW_Y):
        centre -= cyl_at(0.8, -24.0, 6.0, sx, sy)
# sensor wire duct: pocket -> +Y channel -> up -> out the back
centre -= box_at(6.0, 18.0, 2.2, -3.0, 4.0, BOARD_TOP_Z - 0.2)
centre -= cyl_at(2.6, BOARD_TOP_Z - 0.2, 6.9, 0.0, 20.8)
centre -= box_at(6.0, 5.5, 2.2, -3.0, 19.0, -15.5)

# ---------------- TANBOKU retainer frame (as v3) ----------------
retainer = box_at(15.0, 19.0, 0.9, -7.5, -9.5, -24.0)
retainer -= box_at(6.5, 10.5, 0.9, -3.25, -5.25, -24.0)
for sx in (-RET_SCREW_X, RET_SCREW_X):
    for sy in (-RET_SCREW_Y, RET_SCREW_Y):
        retainer -= cyl_at(1.1, -24.0, 0.9, sx, sy)

# ---------------- loose wire ring ----------------
wirering = cyl(33.0, -24.0, 3.0)
wirering -= cyl(24.0, -24.0, 3.0)
_groove = cyl(32.0, -22.8, 1.8)
_groove -= cyl(27.0, -22.8, 1.8)
wirering -= _groove                                 # annular channel on top

# ---------------- left arm (keys) ----------------
leftarm = collar(180.0)
leftarm += box_at(48.0, 35.0, ARM_TOP - ARM_BOT, -73.0, -17.5, ARM_BOT)
_boss, _hole = setscrew(230.0)
leftarm += _boss
leftarm -= _hole
for kx in KEY_XS:
    leftarm -= box_at(16.0, 16.0, 2.0, kx - 8.0, -8.0, ARM_TOP - 2.0)
    leftarm -= box_at(14.2, 14.2, 4.0, kx - 7.1, -7.1, ARM_TOP - 4.0)
    leftarm -= box_at(17.0, 17.0, 7.0, kx - 8.5, -8.5, ARM_BOT)
leftarm -= box_at(40.0, 8.0, 3.0, -69.0, -4.0, ARM_BOT)   # wire groove
leftarm += box_at(10.0, 24.0, 3.0, -68.0, -12.0, -24.0)   # foot

# ---------------- right arm (display deck base) ----------------
rightarm = collar(0.0)
rightarm += box_at(48.0, 35.0, ARM_TOP - ARM_BOT, 25.0, -17.5, ARM_BOT)
rightarm += rrect(DISP_CX, 0, 36.0, 42.0, 6.0, ARM_BOT, ARM_TOP - ARM_BOT)
_boss, _hole = setscrew(-50.0)
rightarm += _boss
rightarm -= _hole
# XIAO cavity (opens at the top under the lid, closed by the cover)
rightarm -= box_at(34.0, 29.0, ARM_TOP - ARM_BOT,
                   DISP_CX - 17.0, -14.5, ARM_BOT)
# USB slot piercing the arm's right end
rightarm -= box_at(11.5, 11.0, 6.0, DISP_CX + 13.0, -5.5, -20.5)
# top case screws from the back: clearance holes through the arm
for dx in (-16.0, 16.0):
    for dy in (-18.0, 18.0):
        rightarm -= cyl_at(1.6, ARM_BOT, ARM_TOP - ARM_BOT,
                           DISP_CX + dx, dy)
# bottom cover recess + pilots
rightarm -= rrect(DISP_CX, 0, 38.0, 33.0, 5.0, ARM_BOT, 1.8)
for dx in (-15.0, 15.0):
    for dy in (-12.5, 12.5):
        rightarm -= cyl_at(1.3, ARM_BOT, 6.0, DISP_CX + dx, dy)
rightarm -= box_at(18.0, 8.0, 3.0, 29.0, -4.0, ARM_BOT)   # wire groove
rightarm += box_at(10.0, 24.0, 3.0, 58.0, -12.0, -24.0)   # foot

# ---------------- top case (display + XIAO deck) ----------------
# Local frame: origin at display centre, z=0 at ARM_TOP; screwed
# from the back (pilots under the flange). XIAO hangs underneath.
lid = box_at(38.0, 46.0, 5.0, -19.0, -23.0, 0.0)                    # flange
lid += box_at(36.0, 44.0, 8.5, -18.0, -22.0, 5.0)                   # wedge
lid -= Pos(0, 0, 13.5) * Rot(X=DISP_TILT) * box_at(40.0, 48.0, 14.0,
                                                   -20.0, -24.0, 0.0)
_F = Pos(0, 0, 13.5) * Rot(X=DISP_TILT)
lid -= _F * box_at(DISP_W + 0.8, DISP_L + 0.8, 3.8,
                   -(DISP_W + 0.8) / 2, -(DISP_L + 0.8) / 2, -1.8)
lid += _F * box_at(12.0, 1.8, 1.0, -6.0, DISP_L / 2 - 0.5, 5.3)     # lip
for dx in (-16.0, 16.0):
    for dy in (-18.0, 18.0):
        lid -= cyl_at(1.3, 0.0, 4.5, dx, dy)
CRADLE_LX = 2.0
for sgn in (-1, 1):
    lid += box_at(30.0, 2.0, 3.3,
                  CRADLE_LX - 15.0, sgn * 10.0 - 1.0, -3.3)
    lid += box_at(30.0, 1.7, 1.2,
                  CRADLE_LX - 15.0, sgn * 8.85 - 0.85, -4.5)
lid += box_at(2.0, 19.0, 3.3, CRADLE_LX - 12.5, -9.5, -3.3)         # stop
lid = Pos(DISP_CX, 0, ARM_TOP) * lid

# ---------------- bottom cover (right arm) ----------------
cover = rrect(DISP_CX, 0, 38.0, 33.0, 5.0, ARM_BOT, 1.8)
for dx in (-15.0, 15.0):
    for dy in (-12.5, 12.5):
        cover -= cyl_at(1.6, ARM_BOT, 1.8, DISP_CX + dx, dy)

for name, part in [("centre", centre), ("ring", ring),
                   ("retainer", retainer), ("wirering", wirering),
                   ("leftarm", leftarm), ("rightarm", rightarm),
                   ("lid", lid), ("cover", cover)]:
    assert part.is_valid, f"{name} is not a valid solid"
    bb = part.bounding_box()
    print(f"{name}: valid, volume={part.volume:.1f} mm^3, "
          f"bbox X[{bb.min.X:.2f},{bb.max.X:.2f}] "
          f"Y[{bb.min.Y:.2f},{bb.max.Y:.2f}] "
          f"Z[{bb.min.Z:.2f},{bb.max.Z:.2f}]")

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck5")
os.makedirs(OUT, exist_ok=True)
for name, part in [("centre", centre), ("ring", ring),
                   ("retainer", retainer), ("wirering", wirering),
                   ("leftarm", leftarm), ("rightarm", rightarm),
                   ("lid", lid), ("cover", cover)]:
    export_stl(part, os.path.join(OUT, f"NapeDeck5-{name}.stl"))
    print("wrote", f"NapeDeck5-{name}.stl")
