import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math

BASE = "/home/hatch/workspace/nape-trackball-case/deck/"
OUT = "/home/hatch/workspace/goals/nape-trackball-redesign/files/"

def load(name):
    return trimesh.load(BASE + name)

def box(extents, center):
    m = trimesh.creation.box(extents=extents)
    m.apply_translation(center)
    return m

CASE = "#ccd1d8"
parts = [
    (load("NapeDeck-base.stl"), CASE),
    (load("NapeDeck-plate.stl"), "#9aa2ac"),
    (load("NapeDeck-cup.stl"), CASE),
    (load("NapeDeck-ring.stl"), "#5b8dd9"),
]

ball = trimesh.creation.uv_sphere(radius=17.0, count=[48, 32])
parts.append((ball, "#c0272d"))

# display module on the tilted tray (tray centre (50,0,-13.5), tilt -15deg)
disp = box([31.5, 39.0, 7.0], [0, 0, 1.5 + 3.5])
ang = math.radians(-15.0)
R = trimesh.transformations.rotation_matrix(ang, [1, 0, 0])
disp.apply_transform(R)
disp.apply_translation([50, 0, -13.5])
parts.append((disp, "#232a33"))
screen = box([27.97, 32.63, 0.6], [0, 0, 1.5 + 7.0 + 0.3])
screen.apply_transform(R)
screen.apply_translation([50, 0, -13.5])
parts.append((screen, "#a8d8ea"))

# XIAO in the cradle
parts.append((box([21.0, 17.8, 3.2], [48, -28, -27.6]), "#3f7f4f"))
# keycaps
for ky in (-20.0, 0.0, 20.0):
    parts.append((box([14.0, 14.0, 7.0], [-44, ky, -22.5]), "#eef0f2"))
# TANBOKU board peeking in its pocket (under the ball, shown for scale)
parts.append((box([7.75, 12.53, 1.6], [0, 0, -23.2]), "#b58900"))

LIGHT = np.array([0.5, -0.4, 0.75]); LIGHT /= np.linalg.norm(LIGHT)
tris_all, cols_all = [], []
for mesh, color in parts:
    tris_all.append(mesh.vertices[mesh.faces])
    shade = 0.45 + 0.55 * np.clip(mesh.face_normals @ LIGHT, 0, 1)
    base = np.array(matplotlib.colors.to_rgb(color))
    cols_all.append(np.clip(base[None, :] * shade[:, None], 0, 1))
tris = np.concatenate(tris_all); cols = np.concatenate(cols_all)

for elev, azim, fname in [(24, -55, "NapeDeck-case-v1.png"),
                          (80, -90, "NapeDeck-case-v1-top.png")]:
    fig = plt.figure(figsize=(9.5, 6.8), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tris, facecolors=cols, edgecolors="none"))
    ax.set_xlim(-85, 85); ax.set_ylim(-60, 60); ax.set_zlim(-45, 45)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off(); ax.set_box_aspect((2, 1.4, 1))
    fig.savefig(OUT + fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", fname)
