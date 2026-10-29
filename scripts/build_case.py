"""
Nape 40mm trackball case - parametric model (build123d)
=========================================================
Coordinate system: ball centre at origin, Z up, units mm.

Parts (3):
  1. bottom cup   : z -24 .. 0   (bearing pockets, sensor window, screw pilots)
  2. top ring     : z   0 .. +6  (rim; ball is retained, see assembly note)
  3. sensor plate : z -30 .. -24 (pocket for the PAW3222 breakout board)

Assembly order (important):
  plate -> breakout board in pocket -> bottom cup on plate -> bearings
  into pockets -> ball seated from above -> top ring lowered over the
  ball from above (its bottom opening is the equator, dia 40.8mm) and
  screwed into the bottom cup.

Key parameters (edit here and re-run):
  BALL_R      = 20.0   ball radius (40mm ball)
  CLEARANCE   = 0.4    ball-to-cavity clearance
  EXPOSURE    = 14.0   ball height above the rim (rim at z = +6)
  BEARING_R   = 3.0    bearing ball radius (6mm bearing balls)
  LENS_GAP    = 2.0    ball-bottom to lens-top gap (ASSUMED, verify by test)
  LENS_HEIGHT = 4.0    lens top above breakout PCB top (ASSUMED, verify)
  BOARD_W/L   = 8.2 / 13.0  breakout pocket (board is 7.75 x 12.53mm)
"""

import math
from build123d import *

# ---------------- parameters ----------------
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
# bearing centres: 23mm from ball centre, 55 deg from downward vertical
BEARING_DIST = BALL_R + BEARING_R
BEARING_AZ = [30.0, 150.0, 270.0]
BEARING_TILT = 55.0  # deg from downward vertical
SENSOR_HOLE_R = 8.0
# breakout pocket: board top must sit at -26 so lens top (-26+4) is 2mm
# below the ball bottom (-20).
BOARD_TOP_Z = -26.0
POCKET_DEPTH = PLATE_TOP - (BOARD_TOP_Z - 1.6)  # 3.6 (floor at -27.6, board top at -26)
PLATE_SCREW_AZ = [45.0, 135.0, 225.0, 315.0]
RING_SCREW_AZ = [0.0, 90.0, 180.0, 270.0]
SCREW_R = 22.0


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


# ---------------- bottom cup ----------------
cup = cyl(OUT_R, CUP_BOT, -CUP_BOT)              # -24 .. 0
cup -= sphere_at(CAV_R, 0, 0, 0)                 # ball cavity
cup -= cyl(SENSOR_HOLE_R, CUP_BOT, 6.0)          # sensor window -24 .. -18
for (bx, by, bz) in bearing_centres():
    cup -= sphere_at(BEARING_POCKET_R, bx, by, bz)
for az in PLATE_SCREW_AZ:                        # M3 self-tap pilots, from below
    a = math.radians(az)
    cup -= cyl_at(1.3, CUP_BOT, 8.0,
                  SCREW_R * math.cos(a), SCREW_R * math.sin(a))
for az in RING_SCREW_AZ:                         # M2.5 pilots, from equator face
    a = math.radians(az)
    cup -= cyl_at(1.1, -8.0, 8.0,
                  SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- top ring ----------------
ring = cyl(OUT_R, 0.0, RIM_Z)                    # 0 .. +6
ring -= sphere_at(CAV_R, 0, 0, 0)
for az in RING_SCREW_AZ:                         # M2.5 clearance, through
    a = math.radians(az)
    ring -= cyl_at(1.3, 0.0, RIM_Z,
                   SCREW_R * math.cos(a), SCREW_R * math.sin(a))

# ---------------- sensor plate ----------------
plate = cyl(OUT_R, PLATE_BOT, PLATE_TOP - PLATE_BOT)  # -30 .. -24
# breakout pocket: 8.2 (X) x 13.0 (Y), floor at BOARD_TOP_Z - 1.6
pocket = Solid.make_box(8.2, 13.0, POCKET_DEPTH,
                        Plane(origin=(-4.1, -6.5, PLATE_TOP - POCKET_DEPTH)))
plate -= pocket
# wire channel on the top face, +X side, 10 wide, 2 deep
plate -= Solid.make_box(OUT_R - 4.1, 10.0, 2.0, Plane(origin=(4.1, -5.0, -26.0)))
for az in PLATE_SCREW_AZ:                        # M3 clearance, through
    a = math.radians(az)
    plate -= cyl_at(1.6, PLATE_BOT, PLATE_TOP - PLATE_BOT,
                    SCREW_R * math.cos(a), SCREW_R * math.sin(a))

for name, part in [("cup", cup), ("ring", ring), ("plate", plate)]:
    assert part.is_valid, f"{name} is not a valid solid"
    bb = part.bounding_box()
    print(f"{name}: valid, volume={part.volume:.1f} mm^3, "
          f"bbox X[{bb.min.X:.2f},{bb.max.X:.2f}] "
          f"Y[{bb.min.Y:.2f},{bb.max.Y:.2f}] "
          f"Z[{bb.min.Z:.2f},{bb.max.Z:.2f}]")

export_stl(cup, "Nape-40mm-ball-cup.stl")
export_stl(ring, "Nape-40mm-ball-ring.stl")
export_stl(plate, "Nape-40mm-ball-plate.stl")
print("STL files written.")
