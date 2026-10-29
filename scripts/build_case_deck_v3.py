"""
Nape Deck prototype case v3 - TANBOKU screwed to the bottom case
================================================================
Changes from v2 (user requests):
  - keys on the arm opposite the display: 3 -> 2 (bar back to the
    original 135mm length)
  - no separate sensor plate/cup stack: the ball cavity is moulded
    into the body, and the TANBOKU sits in a pocket in the body's
    bottom face, pinched by a screwed retainer frame. This removes
    the plate floor (2mm) from the height chain.

Parts (5): body (with ball cup) / ring / retainer / display lid /
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
KEY_XS = [-33.0, -52.05]         # 2 keys, 19.05 pitch, left arm


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

# keys on the left arm: switch pocket on top + open wiring well below
for kx in KEY_XS:
    body -= box_at(16.0, 16.0, 2.0, kx - 8.0, -8.0, BODY_TOP - 2.0)
    body -= box_at(14.2, 14.2, 4.0, kx - 7.1, -7.1, BODY_TOP - 4.0)
    body -= box_at(18.0, 18.0, 7.0,
                   kx - 9.0, -9.0, BODY_BOT)   # well z -26..-19

# XIAO cavity under the display pad (accessed from the bottom)
body -= box_at(34.0, 29.0, BODY_TOP - 1.5 - BODY_BOT,
               DISP_PAD_CX - 17.0, -14.5, BODY_BOT)   # ceiling at -15.5
# USB slot through the pad's right edge (XIAO usb faces +X)
body -= box_at(6.0, 10.0, 5.0, DISP_PAD_CX + 15.0, -5.0, -22.5)
# XIAO hanging cradle: side rails from the cavity ceiling + edge lips.
# XIAO long axis along X, component face DOWN (solder from below).
for sgn in (-1, 1):
    body += box_at(30.0, 2.0, 4.5,
                   DISP_PAD_CX - 15.0, sgn * (XIAO_W / 2 + 0.6) - (2.0 if sgn > 0 else 0.0),
                   BODY_TOP - 6.0)
    body += box_at(30.0, 1.6, 1.2,
                   DISP_PAD_CX - 15.0, sgn * (XIAO_W / 2) - (0.8 if sgn > 0 else 0.8),
                   BODY_TOP - 7.3)
# bottom cover recess
body -= rrect(DISP_PAD_CX, 0, 38.0, 33.0, 5.0, BODY_BOT, 2.0)
for dx in (-15.0, 15.0):
    for dy in (-12.5, 12.5):
        body -= cyl_at(1.3, BODY_BOT, 6.0, DISP_PAD_CX + dx, dy)

# wire groove on the bottom face: keys -> centre -> XIAO cavity
body -= box_at(88.0, 8.0, 3.0, -61.0, -4.0, BODY_BOT)   # x -61..27

# ---------------- display lid (wedge + tray, screwed flat) -----------
# Local frame: origin at pad centre, z=0 at BODY_TOP. Flat flange with
# vertical screws; the top face is sliced at DISP_TILT.
lid = box_at(38.0, 46.0, 2.5, -19.0, -23.0, 0.0)                    # flange
lid += box_at(36.0, 44.0, 11.0, -18.0, -22.0, 2.5)                  # wedge
lid -= Pos(0, 0, 13.5) * Rot(X=DISP_TILT) * box_at(40.0, 48.0, 14.0,
                                                   -20.0, -24.0, 0.0)
_F = Pos(0, 0, 13.5) * Rot(X=DISP_TILT)   # tilted face frame
lid -= _F * box_at(DISP_W + 0.8, DISP_L + 0.8, 3.8,
                   -(DISP_W + 0.8) / 2, -(DISP_L + 0.8) / 2, -1.8)
lid += _F * box_at(12.0, 1.8, 1.0, -6.0, DISP_L / 2 - 0.5, 5.3)     # lip
for dx in (-15.0, 15.0):
    for dy in (-18.0, 18.0):
        lid -= cyl_at(1.6, 0.0, 2.5, dx, dy)                        # M3 clr
lid = Pos(DISP_PAD_CX, 0, BODY_TOP) * lid
for dx in (-15.0, 15.0):     # matching pilots in the body top
    for dy in (-18.0, 18.0):
        body -= cyl_at(1.3, BODY_TOP - 6.0, 6.0, DISP_PAD_CX + dx, dy)

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
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck3")
os.makedirs(OUT, exist_ok=True)
for name, part in [("body", body), ("ring", ring),
                   ("retainer", retainer), ("lid", lid),
                   ("cover", cover)]:
    export_stl(part, os.path.join(OUT, f"NapeDeck3-{name}.stl"))
    print("wrote", f"NapeDeck3-{name}.stl")
