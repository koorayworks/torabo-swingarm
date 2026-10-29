"""
Nape Deck prototype case v4 - arc keys + top case from the back
================================================================
Changes from v3 (user requests):
  - the 2 keys sit on an arc around the ball (R=50, az 169/191),
    each rotated tangentially
  - display AND XIAO are carried by a top case screwed from the
    BACK of the body; the XIAO hangs under the top case, so the
    whole electronics deck lifts out for soldering (side access)

Parts (5): body (with ball cup) / ring / retainer / top case /
bottom cover. Coordinates: ball centre at origin, Z up, mm.
Desk level z=-24.
"""

import math
from build123d import *

# ---------------- parameters (same ball unit as v1) ----------------
BALL_R = 17.0
CLEAR = 0.4
CAV_R = BALL_R + CLEAR
RIM_Z = BALL_R - 12.0            # +5.0
OUT_R = 23.0
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
# TANBOKU retainer frame (screwed to the bottom face)
RET_SCREW_X = 6.0
RET_SCREW_Y = 7.5

# body: stadium bar + centre dome + display pad, z -24..-12
BAR_L = 135.0
BAR_W = 35.0
BODY_BOT = -24.0
BODY_TOP = -12.0
DOME_R = 24.5
DISP_PAD_CX = 44.0
DISP_PAD_W = 36.0     # along X
DISP_PAD_L = 42.0     # along Y

DISP_W, DISP_L = 31.5, 39.0     # module (verify with calipers)
DISP_TILT = 10.0
XIAO_W, XIAO_L = 17.8, 21.0
KEY_ARC_R = 49.0                 # keys on an arc around the ball
KEY_ARC_AZ = [171.0, 189.0]      # degrees (180 = straight left)


def cyl(r, z0, h):
    return Solid.make_cylinder(r, h, Plane(origin=(0, 0, z0)))


def cyl_at(r, z0, h, x, y):
    return Solid.make_cylinder(r, h, Plane(origin=(x, y, z0)))


def sphere_at(r, x, y, z):
    return Solid.make_sphere(r, Plane(origin=(x, y, z)))


def box_at(sx, sy, sz, x, y, z):
    return Solid.make_box(sx, sy, sz, Plane(origin=(x, y, z)))


def rrect(cx, cy, sx, sy, r, z0, h):
    """rounded-rect prism centred at (cx, cy)."""
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


# ---------------- top ring ----------------
ring = cyl(OUT_R, 0.0, RIM_Z)
ring -= sphere_at(CAV_R, 0, 0, 0)
for az in RING_SCREW_AZ:
    a = math.radians(az)
    ring -= cyl_at(1.3, 0.0, RIM_Z,
                   SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- body (original Nape silhouette) ----------------
body = rrect(0, 0, BAR_L, BAR_W, BAR_W / 2, BODY_BOT, BODY_TOP - BODY_BOT)
body += cyl(DOME_R, BODY_BOT, BODY_TOP - BODY_BOT)
body += rrect(DISP_PAD_CX, 0, DISP_PAD_W, DISP_PAD_L, 6.0,
              BODY_BOT, BODY_TOP - BODY_BOT)
# dome tower: the ball cup is moulded into the body
body += cyl(OUT_R, BODY_TOP, -BODY_TOP)            # z -12..0
body -= sphere_at(CAV_R, 0, 0, 0)
for (bx, by, bz) in bearing_centres():
    body -= sphere_at(BEARING_POCKET_R, bx, by, bz)
for az in RING_SCREW_AZ:    # M2.5 pilots in the tower top
    a = math.radians(az)
    body -= cyl_at(1.1, -8.0, 8.0,
                   SCREW_R * math.cos(a), SCREW_R * math.sin(a))
# lens window: cone from the pocket ceiling (r=3.5) widening up (r=7.5)
body -= Solid.make_cone(3.5, 7.5, 5.9, Plane(origin=(0, 0, BOARD_TOP_Z)))
# TANBOKU pocket in the bottom face (board top against the ceiling)
body -= box_at(BOARD_POCKET_W, BOARD_POCKET_L, BOARD_TOP_Z - BODY_BOT,
               -BOARD_POCKET_W / 2, -BOARD_POCKET_L / 2, BODY_BOT)
# sensor wire notch: pocket -> +X -> XIAO cavity (inside the body)
body -= box_at(23.5, 6.0, 2.2, 4.0, -3.0, BOARD_TOP_Z - 0.2)
# retainer frame recess + M2 pilots in the bottom face
body -= box_at(15.4, 19.4, 0.9, -7.7, -9.7, BODY_BOT)
for sx in (-RET_SCREW_X, RET_SCREW_X):
    for sy in (-RET_SCREW_Y, RET_SCREW_Y):
        body -= cyl_at(0.8, BODY_BOT, 6.0, sx, sy)

# keys on the left arm, arranged on an arc around the ball centre;
# each key is rotated so its front faces along the arc tangent
for az_deg in KEY_ARC_AZ:
    az = math.radians(az_deg)
    kx, ky = KEY_ARC_R * math.cos(az), KEY_ARC_R * math.sin(az)
    phi = az_deg - 180.0
    for (s, z0, h) in [(16.0, BODY_TOP - 2.0, 2.0),
                       (14.2, BODY_TOP - 4.0, 4.0),
                       (17.0, BODY_BOT, 7.0)]:
        body -= Pos(kx, ky, 0) * Rot(Z=phi) * box_at(s, s, h, -s / 2, -s / 2, z0)

# XIAO cavity under the display pad: opens at the body top (the lid
# covers it) and at the bottom (the cover closes it)
body -= box_at(34.0, 29.0, BODY_TOP - BODY_BOT,
               DISP_PAD_CX - 17.0, -14.5, BODY_BOT)
# USB slot piercing the body's right end (XIAO usb faces +X)
body -= box_at(11.5, 11.0, 6.0, DISP_PAD_CX + 13.0, -5.5, -21.5)
# lid screws come from the BACK: clearance holes through the body
for dx in (-16.0, 16.0):
    for dy in (-18.0, 18.0):
        body -= cyl_at(1.6, BODY_BOT, BODY_TOP - BODY_BOT,
                       DISP_PAD_CX + dx, dy)
# bottom cover recess
body -= rrect(DISP_PAD_CX, 0, 38.0, 33.0, 5.0, BODY_BOT, 2.0)
for dx in (-15.0, 15.0):
    for dy in (-12.5, 12.5):
        body -= cyl_at(1.3, BODY_BOT, 6.0, DISP_PAD_CX + dx, dy)

# wire groove on the bottom face: keys -> centre -> XIAO cavity
body -= box_at(88.0, 8.0, 3.0, -61.0, -4.0, BODY_BOT)   # x -61..27

# ---------------- top case (display + XIAO deck) ---------------------
# Local frame: origin at pad centre, z=0 at BODY_TOP. The top case is
# screwed from the BACK of the body (pilots under its flange).
# The XIAO hangs from its underside (component face down); removing
# the top case brings display + XIAO out together for soldering,
# with the wiring accessible from the sides.
lid = box_at(38.0, 46.0, 5.0, -19.0, -23.0, 0.0)                    # flange
lid += box_at(36.0, 44.0, 8.5, -18.0, -22.0, 5.0)                   # wedge
lid -= Pos(0, 0, 13.5) * Rot(X=DISP_TILT) * box_at(40.0, 48.0, 14.0,
                                                   -20.0, -24.0, 0.0)
_F = Pos(0, 0, 13.5) * Rot(X=DISP_TILT)   # tilted face frame
lid -= _F * box_at(DISP_W + 0.8, DISP_L + 0.8, 3.8,
                   -(DISP_W + 0.8) / 2, -(DISP_L + 0.8) / 2, -1.8)
lid += _F * box_at(12.0, 1.8, 1.0, -6.0, DISP_L / 2 - 0.5, 5.3)     # lip
for dx in (-16.0, 16.0):     # M3 self-tap pilots from below
    for dy in (-18.0, 18.0):
        lid -= cyl_at(1.3, 0.0, 4.5, dx, dy)
# XIAO hanging cradle under the flange (centre x=+2, usb toward +X):
# side rails + edge lips + an end stop. PCB rests on the lips with
# its component face down (world z: pcb -16.6..-15.3, usb to -19.7).
CRADLE_LX = 2.0
for sgn in (-1, 1):
    lid += box_at(30.0, 2.0, 4.5,
                  CRADLE_LX - 15.0, sgn * 10.0 - 1.0,
                  -4.5)
    lid += box_at(30.0, 1.7, 1.2,
                  CRADLE_LX - 15.0, sgn * 8.85 - 0.85,
                  -5.7)
lid += box_at(2.0, 19.0, 3.3, CRADLE_LX - 12.5, -9.5, -4.5)         # stop
lid = Pos(DISP_PAD_CX, 0, BODY_TOP) * lid

# ---------------- TANBOKU retainer frame ----------------
# Picture frame that presses the board's bottom perimeter; the centre
# window leaves the pads/wires free.
retainer = box_at(15.0, 19.0, 0.9, -7.5, -9.5, BODY_BOT)
retainer -= box_at(6.5, 10.5, 0.9, -3.25, -5.25, BODY_BOT)
for sx in (-RET_SCREW_X, RET_SCREW_X):
    for sy in (-RET_SCREW_Y, RET_SCREW_Y):
        retainer -= cyl_at(1.1, BODY_BOT, 0.9, sx, sy)

# ---------------- bottom cover ----------------
cover = rrect(DISP_PAD_CX, 0, 38.0, 33.0, 5.0, BODY_BOT, 2.0)
for dx in (-15.0, 15.0):
    for dy in (-12.5, 12.5):
        cover -= cyl_at(1.6, BODY_BOT, 2.0, DISP_PAD_CX + dx, dy)

for name, part in [("body", body), ("ring", ring),
                   ("retainer", retainer), ("lid", lid),
                   ("cover", cover)]:
    assert part.is_valid, f"{name} is not a valid solid"
    bb = part.bounding_box()
    print(f"{name}: valid, volume={part.volume:.1f} mm^3, "
          f"bbox X[{bb.min.X:.2f},{bb.max.X:.2f}] "
          f"Y[{bb.min.Y:.2f},{bb.max.Y:.2f}] "
          f"Z[{bb.min.Z:.2f},{bb.max.Z:.2f}]")

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck4")
os.makedirs(OUT, exist_ok=True)
for name, part in [("body", body), ("ring", ring),
                   ("retainer", retainer), ("lid", lid),
                   ("cover", cover)]:
    export_stl(part, os.path.join(OUT, f"NapeDeck4-{name}.stl"))
    print("wrote", f"NapeDeck4-{name}.stl")
