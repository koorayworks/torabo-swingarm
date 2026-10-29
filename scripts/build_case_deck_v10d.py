"""
Nape Deck wireless D-study - big battery in a plinth base
================================================================
The two collars ride DIFFERENT height bands on the centre drum
(left: z -22.5..-18, right: z -17..-12), so they never collide and
each arm swings ~65 deg toward the front: the key section and the
display section can end up side by side in front of the ball.
Neck sections (20mm wide) between collar and body keep the wide
parts clear of each other in that pose. Wires cross under the arms
with slack loops on the desk (the v5 wire ring is dropped: the
low collar band would plough through it).

Parts (8): centre / ring / retainer / wire ring / left arm / right arm /
top case / bottom cover.
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

ARM_TOP = -5.5
ARM_BOT = -15.5                  # arms ride on legs above the base
COLLAR_R_OUT = 29.0
COLLAR_R_IN = 23.4
# two collar bands on the drum (they pass over/under each other)
COLLAR_L_Z0, COLLAR_L_H, COLLAR_L_HALF = -15.5, 4.5, 85.0   # left
COLLAR_R_Z0, COLLAR_R_H, COLLAR_R_HALF = -10.0, 4.5, 60.0   # right

DISP_CX = 51.0                   # display centre on the right arm
DISP_W, DISP_L = 31.5, 39.0      # module (verify with calipers)
DISP_TILT = 10.0
XIAO_W, XIAO_L = 17.8, 21.0
KEY_GRID = [(-67.5, -9.5), (-67.5, 9.5),
            (-48.5, -9.5), (-48.5, 9.5)]   # 2x2 square, 19mm pitch


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


def collar(az_center_deg, z0, h, half_deg):
    c = cyl(COLLAR_R_OUT, z0, h)
    c -= cyl(COLLAR_R_IN, z0, h)
    c -= sector_cutter(az_center_deg + half_deg, +1, z0, h)
    c -= sector_cutter(az_center_deg - half_deg, -1, z0, h)
    return c


def setscrew(az_deg, z0, h):
    """Box boss + radial hole for an M3 set screw at azimuth az_deg,
    kept inside the collar band (z0..z0+h)."""
    a = math.radians(az_deg)
    d = (math.cos(a), math.sin(a), 0)
    boss = Pos(31 * d[0], 31 * d[1], 0) * Rot(Z=az_deg) * \
        box_at(7.0, 11.0, h, -3.5, -5.5, z0)
    hole = Solid.make_cylinder(
        1.5, 16.0, Plane(origin=(19 * d[0], 19 * d[1], z0 + h / 2),
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
centre = cyl(55.0, -24.0, 8.0)                      # plinth base
centre += cyl(OUT_R, -16.0, 16.0)                   # drum z -16..0
centre += cyl(29.0, -4.5, 2.0)                      # anti-lift flange
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
# sensor wires: LOW slot from the pocket straight out at z -23.8..-22.6,
# below both collar bands, so the arms can rotate a full 360 deg.
centre -= box_at(6.0, 36.0, 1.2, -3.0, 4.0, -23.8)
centre -= cyl_at(2.6, -22.6, 5.1, 0.0, 40.7)        # riser to groove
_bg = cyl(43.5, -17.5, 1.5)
_bg -= cyl(38.0, -17.5, 1.5)
centre -= _bg                                       # base-top wire groove

# ---------------- TANBOKU retainer frame (as v3) ----------------
retainer = box_at(15.0, 19.0, 0.9, -7.5, -9.5, -24.0)
retainer -= box_at(6.5, 15.0, 0.9, -3.25, -5.25, -24.0)  # +Y side open for wires
for sx in (-RET_SCREW_X, RET_SCREW_X):
    for sy in (-RET_SCREW_Y, RET_SCREW_Y):
        retainer -= cyl_at(1.1, -24.0, 0.9, sx, sy)


# ---------------- left arm (keys, LOWER collar band) ----------------
leftarm = collar(180.0, COLLAR_L_Z0, COLLAR_L_H, COLLAR_L_HALF)
leftarm += box_at(15.6, 20.0, ARM_TOP - ARM_BOT, -45.0, -10.0, ARM_BOT)  # neck
leftarm += box_at(50.6, 35.0, ARM_TOP - ARM_BOT, -80.0, -17.5, ARM_BOT)  # body
leftarm += rrect(-58.0, 0, 44.0, 44.0, 6.0, ARM_BOT, ARM_TOP - ARM_BOT)  # key pad
_boss, _hole = setscrew(130.0, COLLAR_L_Z0, COLLAR_L_H)
leftarm += _boss
leftarm -= _hole
for kx, ky in KEY_GRID:
    leftarm -= box_at(16.0, 16.0, 2.0, kx - 8.0, ky - 8.0, ARM_TOP - 2.0)
    leftarm -= box_at(14.2, 14.2, 4.0, kx - 7.1, ky - 7.1, ARM_TOP - 4.0)
    leftarm -= box_at(17.0, 17.0, 7.0, kx - 8.5, ky - 8.5, ARM_BOT)
leftarm -= box_at(39.0, 8.0, 3.0, -69.0, -4.0, ARM_BOT)   # wire groove
leftarm += box_at(10.0, 24.0, 8.5, -74.0, -12.0, -24.0)   # leg

# ---------------- right arm (keys + XIAO, UPPER collar band) ---------
rightarm = collar(0.0, COLLAR_R_Z0, COLLAR_R_H, COLLAR_R_HALF)
rightarm += box_at(15.6, 20.0, ARM_TOP - ARM_BOT, 29.4, -10.0, ARM_BOT)  # neck
rightarm += box_at(50.6, 35.0, ARM_TOP - ARM_BOT, 29.4, -17.5, ARM_BOT)  # body
rightarm += rrect(58.0, 0, 44.0, 44.0, 6.0, ARM_BOT, ARM_TOP - ARM_BOT)  # key pad
_boss, _hole = setscrew(50.0, COLLAR_R_Z0, COLLAR_R_H)
rightarm += _boss
rightarm -= _hole
for kx, ky in [(48.5, -9.5), (48.5, 9.5), (67.5, -9.5), (67.5, 9.5)]:
    rightarm -= box_at(16.0, 16.0, 2.0, kx - 8.0, ky - 8.0, ARM_TOP - 2.0)
    rightarm -= box_at(14.2, 14.2, 4.0, kx - 7.1, ky - 7.1, ARM_TOP - 4.0)
    rightarm -= box_at(17.0, 17.0, 7.0, kx - 8.5, ky - 8.5, ARM_BOT)
# XIAO pocket under the key pad (opens at the bottom, closed by cover)
rightarm -= box_at(34.0, 29.0, 6.0, 41.0, -14.5, ARM_BOT)
rightarm -= box_at(39.0, 8.0, 3.0, 30.0, -4.0, ARM_BOT)   # wire groove
rightarm += box_at(10.0, 24.0, 8.5, 64.0, -12.0, -24.0)   # leg

# ---------------- XIAO pocket cover (right arm) -----------------------
cover = rrect(58.0, 0, 38.0, 33.0, 5.0, ARM_BOT, 1.8)

for name, part in [("centre", centre), ("ring", ring),
                   ("retainer", retainer),
                   ("leftarm", leftarm), ("rightarm", rightarm),
                   ("cover", cover)]:
    assert part.is_valid, f"{name} is not a valid solid"
    bb = part.bounding_box()
    print(f"{name}: valid, volume={part.volume:.1f} mm^3, "
          f"bbox X[{bb.min.X:.2f},{bb.max.X:.2f}] "
          f"Y[{bb.min.Y:.2f},{bb.max.Y:.2f}] "
          f"Z[{bb.min.Z:.2f},{bb.max.Z:.2f}]")

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck10d")
os.makedirs(OUT, exist_ok=True)
for name, part in [("centre", centre), ("ring", ring),
                   ("retainer", retainer),
                   ("leftarm", leftarm), ("rightarm", rightarm),
                   ("cover", cover)]:
    export_stl(part, os.path.join(OUT, f"NapeDeck10D-{name}.stl"))
    print("wrote", f"NapeDeck10D-{name}.stl")
