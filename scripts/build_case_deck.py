"""
Nape Deck prototype case - parametric model (build123d)
=========================================================
Hand-wired prototype: no PCB. The case fixes the XIAO and the
TANBOKU sensor board; everything else is wired in the air.

Parts (4):
  1. ball unit bottom cup   (34mm ball, bearing pockets, sensor window)
  2. ball unit top ring
  3. ball unit sensor plate (TANBOKU pocket = sensor fixation)
  4. base chassis           (ball unit mount, XIAO cradle, display
                             tray, 3x MX switch pockets, wire groove)

Coordinates: ball centre at origin, Z up, units mm.
Ball unit Z stack: plate -27..-21, cup -21..0, ring 0..+5.
Base chassis top at z=-27 (ball unit sits on it), base -31..-27.

Verify with calipers before printing:
  DISP_W/DISP_L : display module 31.5 x 39.0 (Waveshare 1.69" touch)
  XIAO_W/XIAO_L : 17.8 x 21.0
  LENS_HEIGHT   : TANBOKU lens top above board top = 3.4
"""

import math
from build123d import *

# ---------------- parameters ----------------
BALL_R = 17.0            # 34mm ball
CLEAR = 0.4
CAV_R = BALL_R + CLEAR
RIM_Z = BALL_R - 12.0    # +5.0 (12mm of ball above the rim)
OUT_R = 23.0
CUP_BOT = -21.0
PLATE_TOP = CUP_BOT      # -21.0
PLATE_BOT = -27.0
BEARING_R = 3.0
BEARING_POCKET_R = BEARING_R + 0.3
BEARING_DIST = BALL_R + BEARING_R
BEARING_AZ = [30.0, 150.0, 270.0]
BEARING_TILT = 55.0      # deg from downward vertical
SENSOR_HOLE_R = 8.0
LENS_GAP = 2.0           # ball bottom to lens top
LENS_HEIGHT = 3.4        # TANBOKU lens top above board top
BOARD_TOP_Z = -(BALL_R + LENS_GAP) - LENS_HEIGHT   # -22.4
POCKET_FLOOR_Z = BOARD_TOP_Z - 1.6                 # -24.0 (1.6mm board)
POCKET_DEPTH = PLATE_TOP - POCKET_FLOOR_Z         # 3.0
BOARD_POCKET_W = 8.2     # board 7.75 x 12.53 + clearance
BOARD_POCKET_L = 13.0
SCREW_R = 19.0
PLATE_SCREW_AZ = [45.0, 135.0, 225.0, 315.0]
RING_SCREW_AZ = [0.0, 90.0, 180.0, 270.0]

# base chassis
BASE_X0, BASE_X1 = -64.0, 72.0
BASE_Y0, BASE_Y1 = -40.0, 40.0
BASE_BOT = PLATE_BOT - 4.0     # -31.0
BASE_TOP = PLATE_BOT           # -27.0
BASE_CORNER_R = 6.0

# XIAO cradle (front-right, USB toward +X edge)
XIAO_W, XIAO_L = 17.8, 21.0    # across / along
CRADLE_CX, CRADLE_CY = 48.0, -28.0
CRADLE_DEPTH = 2.4

# display tray (right, tilted back)
DISP_W, DISP_L = 31.5, 39.0
DISP_TILT = 15.0               # deg from vertical
DISP_CX = 50.0

# keys (left column)
KEY_X = -44.0
KEY_YS = [-20.0, 0.0, 20.0]


def cyl(r, z0, h):
    return Solid.make_cylinder(r, h, Plane(origin=(0, 0, z0)))


def cyl_at(r, z0, h, x, y):
    return Solid.make_cylinder(r, h, Plane(origin=(x, y, z0)))


def sphere_at(r, x, y, z):
    return Solid.make_sphere(r, Plane(origin=(x, y, z)))


def box_at(sx, sy, sz, x, y, z):
    return Solid.make_box(sx, sy, sz, Plane(origin=(x, y, z)))


def bearing_centres():
    out = []
    for az in BEARING_AZ:
        a = math.radians(az)
        t = math.radians(BEARING_TILT)
        hr = BEARING_DIST * math.sin(t)
        out.append((hr * math.cos(a), hr * math.sin(a),
                    -BEARING_DIST * math.cos(t)))
    return out


# ---------------- ball unit: bottom cup ----------------
cup = cyl(OUT_R, CUP_BOT, -CUP_BOT)              # -21 .. 0
cup -= sphere_at(CAV_R, 0, 0, 0)
cup -= cyl(SENSOR_HOLE_R, CUP_BOT, 6.0)          # sensor window
for (bx, by, bz) in bearing_centres():
    cup -= sphere_at(BEARING_POCKET_R, bx, by, bz)
for az in PLATE_SCREW_AZ:                        # M3 self-tap pilots
    a = math.radians(az)
    cup -= cyl_at(1.3, CUP_BOT, 8.0,
                  SCREW_R * math.cos(a), SCREW_R * math.sin(a))
for az in RING_SCREW_AZ:                         # M2.5 pilots
    a = math.radians(az)
    cup -= cyl_at(1.1, -8.0, 8.0,
                  SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- ball unit: top ring ----------------
ring = cyl(OUT_R, 0.0, RIM_Z)                    # 0 .. +5
ring -= sphere_at(CAV_R, 0, 0, 0)
for az in RING_SCREW_AZ:                         # M2.5 clearance
    a = math.radians(az)
    ring -= cyl_at(1.3, 0.0, RIM_Z,
                   SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- ball unit: sensor plate (TANBOKU) ----------------
plate = cyl(OUT_R, PLATE_BOT, PLATE_TOP - PLATE_BOT)   # -27 .. -21
pocket = box_at(BOARD_POCKET_W, BOARD_POCKET_L, POCKET_DEPTH,
                -BOARD_POCKET_W / 2, -BOARD_POCKET_L / 2,
                PLATE_TOP - POCKET_DEPTH)
plate -= pocket
# wire channel on the top face toward +X (sensor wires exit here)
plate -= box_at(OUT_R - 4.1, 10.0, 2.0, 4.1, -5.0, PLATE_TOP - 2.0)
for az in PLATE_SCREW_AZ:                        # M3 clearance
    a = math.radians(az)
    plate -= cyl_at(1.6, PLATE_BOT, PLATE_TOP - PLATE_BOT,
                    SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- base chassis ----------------
# rounded-rectangle slab: two crossed slabs + 4 corner cylinders
_H = BASE_TOP - BASE_BOT
base = box_at(BASE_X1 - BASE_X0 - 2 * BASE_CORNER_R, BASE_Y1 - BASE_Y0,
              _H, BASE_X0 + BASE_CORNER_R, BASE_Y0, BASE_BOT)
base += box_at(BASE_X1 - BASE_X0, BASE_Y1 - BASE_Y0 - 2 * BASE_CORNER_R,
               _H, BASE_X0, BASE_Y0 + BASE_CORNER_R, BASE_BOT)
for cx in (BASE_X0 + BASE_CORNER_R, BASE_X1 - BASE_CORNER_R):
    for cy in (BASE_Y0 + BASE_CORNER_R, BASE_Y1 - BASE_CORNER_R):
        base += cyl_at(BASE_CORNER_R, BASE_BOT, _H, cx, cy)

# ball unit through-holes (M3 from below into the cup pilots)
for az in PLATE_SCREW_AZ:
    a = math.radians(az)
    base -= cyl_at(1.7, BASE_BOT, BASE_TOP - BASE_BOT,
                   SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# rubber feet recesses (8mm dia, 1mm deep, from below)
for fx in (BASE_X0 + 10, BASE_X1 - 10):
    for fy in (BASE_Y0 + 10, BASE_Y1 - 10):
        base -= cyl_at(4.0, BASE_BOT, 1.0, fx, fy)

# ---- XIAO cradle: recess + edge clips + USB/cable notch ----
base -= box_at(XIAO_L + 1.2, XIAO_W + 1.2, CRADLE_DEPTH,
               CRADLE_CX - (XIAO_L + 1.2) / 2, CRADLE_CY - (XIAO_W + 1.2) / 2,
               BASE_TOP - CRADLE_DEPTH)
# cable notch from the cradle's +X end to the base edge
base -= box_at(BASE_X1 - (CRADLE_CX + XIAO_L / 2) + 2.0, 10.0, BASE_TOP - BASE_BOT,
               CRADLE_CX + XIAO_L / 2 - 1.0, CRADLE_CY - 5.0, BASE_BOT)
# clip lips over the two long edges of the PCB (top face stays open so
# the hidden pads and castellated pins remain solderable). Each lip is
# centred on the PCB edge line so 0.7mm overhangs the board.
for sgn in (-1, 1):
    base += box_at(6.0, 1.4, 1.1,
                   CRADLE_CX - 3.0, CRADLE_CY + sgn * (XIAO_W / 2) - 0.7,
                   BASE_TOP - CRADLE_DEPTH + 1.4)

# ---- display wedge + tray ----
wedge = box_at(38.0, 42.0, 15.0, DISP_CX - 19.0, -21.0, BASE_TOP)
base += wedge
tray = box_at(DISP_W + 6.0, DISP_L + 7.0, 3.0,
              -(DISP_W + 6.0) / 2, -(DISP_L + 7.0) / 2, -1.5)
tray -= box_at(DISP_W + 0.8, DISP_L + 0.8, 1.8,
               -(DISP_W + 0.8) / 2, -(DISP_L + 0.8) / 2, 0.4)
# retaining lip over the module's top edge (module is 7.2mm thick and
# lies back-down in the recess; the lip stops it sliding out up-slope)
tray += box_at(12.0, 1.8, 1.0, -6.0, DISP_L / 2 - 0.5, 6.9)
tray = Pos(DISP_CX, 0, -13.5) * Rot(X=-DISP_TILT) * tray
base += tray

# ---- MX switch pockets (left column) ----
for ky in KEY_YS:
    base -= box_at(16.0, 16.0, 2.0, KEY_X - 8.0, ky - 8.0, BASE_TOP - 2.0)
    base -= box_at(14.2, 14.2, BASE_TOP - BASE_BOT,
                   KEY_X - 7.1, ky - 7.1, BASE_BOT)

# ---- wire groove along the front (ball unit -> XIAO cradle) ----
base -= box_at(38.0, 6.0, 2.0, 8.0, CRADLE_CY - 3.0, BASE_TOP - 2.0)

for name, part in [("cup", cup), ("ring", ring), ("plate", plate),
                   ("base", base)]:
    assert part.is_valid, f"{name} is not a valid solid"
    bb = part.bounding_box()
    print(f"{name}: valid, volume={part.volume:.1f} mm^3, "
          f"bbox X[{bb.min.X:.2f},{bb.max.X:.2f}] "
          f"Y[{bb.min.Y:.2f},{bb.max.Y:.2f}] "
          f"Z[{bb.min.Z:.2f},{bb.max.Z:.2f}]")

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck")
os.makedirs(OUT, exist_ok=True)
for name, part in [("cup", cup), ("ring", ring), ("plate", plate),
                   ("base", base)]:
    export_stl(part, os.path.join(OUT, f"NapeDeck-{name}.stl"))
    print("wrote", f"NapeDeck-{name}.stl")
