"""
Nape 40mm trackball case - SEKIGON module variant (build123d)
==============================================================
Same cup / ring as the TANBOKU variant (build_case.py); only the
sensor plate differs. The sensor is sekigon-gonnoc's
small-mouse-sensor-module (PAW3222), connected through cornotry-rnd's
pitch-conversion FPC (0.5mm -> 2.54mm, 40mm long, flexible).

Coordinate system: ball centre at origin, Z up, units mm.

Module dimensions (from the repo's img/size.png, measured 2026-10-25):
  outline            7.4 (W) x 13.4 (L) mm
  optical centre     on the width centreline,
                     6.77mm from the lens-side edge,
                     6.63mm from the FPC-connector edge
  FPC connector      on the lens face, at the connector-side end
                     (about 4.2..6.4mm from the optical centre)

Assumed (NOT in the repo docs - verify against the real module):
  MODULE_T    = 1.0    module PCB thickness
  The module PCB top is placed at z=-26 (same datum as the TANBOKU
  variant). If the real lens height differs from ~3.4mm, adjust
  POCKET_FLOOR_Z so the lens-to-ball gap stays ~2-2.6mm.

Plate layout:
  pocket 14.0 (X) x 8.0 (Y), optical centre at the ball axis,
  connector end toward +X, FPC channel (8 wide, 2 deep) from the
  pocket to the plate edge on +X. The FPC connector body sits inside
  the cup's sensor window (r=8): its far corner is ~6.6mm from the
  axis, so it clears the window.
"""

import math
from build123d import *

# ---------------- parameters (shared with TANBOKU variant) ----------------
BALL_R = 20.0
CLEAR = 0.4
CAV_R = BALL_R + CLEAR
RIM_Z = BALL_R - 14.0          # +6.0
OUT_R = 26.0
CUP_BOT = -24.0
PLATE_BOT = -30.0
PLATE_TOP = CUP_BOT            # -24.0
BEARING_R = 3.0
BEARING_POCKET_R = BEARING_R + 0.3
BEARING_DIST = BALL_R + BEARING_R
BEARING_AZ = [30.0, 150.0, 270.0]
BEARING_TILT = 55.0
SENSOR_HOLE_R = 8.0
BOARD_TOP_Z = -26.0            # module PCB top datum
PLATE_SCREW_AZ = [45.0, 135.0, 225.0, 315.0]
RING_SCREW_AZ = [0.0, 90.0, 180.0, 270.0]
SCREW_R = 22.0

# ---------------- sekigon module ----------------
MODULE_T = 1.0                 # ASSUMED pcb thickness
OC_FROM_LENS_EDGE = 6.77       # measured from size.png
OC_FROM_CONN_EDGE = 6.63       # measured from size.png
POCKET_CLR = 0.3               # per side
POCKET_X0 = -(OC_FROM_LENS_EDGE + POCKET_CLR)   # -7.07
POCKET_X1 = +(OC_FROM_CONN_EDGE + POCKET_CLR)   # +6.93
POCKET_W = 7.4 + 2 * POCKET_CLR                 # 8.0 (Y)
POCKET_FLOOR_Z = BOARD_TOP_Z - MODULE_T         # -27.0


def cyl(r, z0, h):
    return Solid.make_cylinder(r, h, Plane(origin=(0, 0, z0)))


def cyl_at(r, z0, h, x, y):
    return Solid.make_cylinder(r, h, Plane(origin=(x, y, z0)))


def sphere_at(r, x, y, z):
    return Solid.make_sphere(r, Plane(origin=(x, y, z)))


def bearing_centres():
    out = []
    for az in BEARING_AZ:
        a = math.radians(az)
        t = math.radians(BEARING_TILT)
        hr = BEARING_DIST * math.sin(t)
        out.append((hr * math.cos(a), hr * math.sin(a),
                    -BEARING_DIST * math.cos(t)))
    return out


# ---------------- bottom cup (unchanged) ----------------
cup = cyl(OUT_R, CUP_BOT, -CUP_BOT)
cup -= sphere_at(CAV_R, 0, 0, 0)
cup -= cyl(SENSOR_HOLE_R, CUP_BOT, 6.0)
for (bx, by, bz) in bearing_centres():
    cup -= sphere_at(BEARING_POCKET_R, bx, by, bz)
for az in PLATE_SCREW_AZ:
    a = math.radians(az)
    cup -= cyl_at(1.3, CUP_BOT, 8.0,
                  SCREW_R * math.cos(a), SCREW_R * math.sin(a))
for az in RING_SCREW_AZ:
    a = math.radians(az)
    cup -= cyl_at(1.1, -8.0, 8.0,
                  SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- top ring (unchanged) ----------------
ring = cyl(OUT_R, 0.0, RIM_Z)
ring -= sphere_at(CAV_R, 0, 0, 0)
for az in RING_SCREW_AZ:
    a = math.radians(az)
    ring -= cyl_at(1.3, 0.0, RIM_Z,
                   SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- sensor plate (sekigon module) ----------------
plate = cyl(OUT_R, PLATE_BOT, PLATE_TOP - PLATE_BOT)  # -30 .. -24
pocket_len = POCKET_X1 - POCKET_X0
pocket = Solid.make_box(pocket_len, POCKET_W, PLATE_TOP - POCKET_FLOOR_Z,
                        Plane(origin=(POCKET_X0, -POCKET_W / 2, POCKET_FLOOR_Z)))
plate -= pocket
# FPC channel on the top face, +X side: 8 wide, 2 deep (z -26..-24),
# from the pocket end to the plate edge
plate -= Solid.make_box(OUT_R - POCKET_X1, 8.0, 2.0,
                        Plane(origin=(POCKET_X1, -4.0, -26.0)))
for az in PLATE_SCREW_AZ:
    a = math.radians(az)
    plate -= cyl_at(1.6, PLATE_BOT, PLATE_TOP - PLATE_BOT,
                    SCREW_R * math.cos(a), SCREW_R * math.sin(a))

for name, part in [("cup", cup), ("ring", ring), ("plate_sekigon", plate)]:
    assert part.is_valid, f"{name} is not a valid solid"
    bb = part.bounding_box()
    print(f"{name}: valid, volume={part.volume:.1f} mm^3, "
          f"bbox X[{bb.min.X:.2f},{bb.max.X:.2f}] "
          f"Y[{bb.min.Y:.2f},{bb.max.Y:.2f}] "
          f"Z[{bb.min.Z:.2f},{bb.max.Z:.2f}]")

export_stl(cup, "Nape-40mm-ball-cup.stl")
export_stl(ring, "Nape-40mm-ball-ring.stl")
export_stl(plate, "Nape-40mm-ball-sekigon-plate.stl")
print("STL files written.")
