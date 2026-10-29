import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math

BASE = "/home/hatch/workspace/nape-trackball-case/deck4/"
OUT = "/home/hatch/workspace/goals/nape-trackball-redesign/files/"

def load(name):
    return trimesh.load(BASE + name)

def box(extents, center):
    m = trimesh.creation.box(extents=extents)
    m.apply_translation(center)
    return m

CASE = "#ccd1d8"
parts = [
    (load("NapeDeck4-body.stl"), CASE),
    (load("NapeDeck4-ring.stl"), "#5b8dd9"),
    (load("NapeDeck4-lid.stl"), "#bcc2ca"),
    (load("NapeDeck4-retainer.stl"), "#e0a458"),
]

ball = trimesh.creation.uv_sphere(radius=17.0, count=[48, 32])
parts.append((ball, "#c0272d"))

# display module in the lid's tilted frame (origin (44,0,1.5), Rot X +10)
F = trimesh.transformations.translation_matrix([44, 0, 1.5]) @ \
    trimesh.transformations.rotation_matrix(math.radians(10.0), [1, 0, 0])
disp = box([31.5, 39.0, 7.2], [0, 0, 1.8])
disp.apply_transform(F)
parts.append((disp, "#232a33"))
screen = box([27.97, 32.63, 0.6], [0, 0, 5.7])
screen.apply_transform(F)
parts.append((screen, "#a8d8ea"))

for az_deg in (171.0, 189.0):
    az = math.radians(az_deg)
    kx, ky = 49.0 * math.cos(az), 49.0 * math.sin(az)
    cap = box([14.0, 14.0, 7.0], [0, 0, 0])
    Rz = trimesh.transformations.rotation_matrix(math.radians(az_deg - 180.0), [0, 0, 1])
    cap.apply_transform(Rz)
    cap.apply_translation([kx, ky, -8.5])
    parts.append((cap, "#eef0f2"))

# XIAO hanging under the top case (visible in the bottom view)
parts.append((box([21.0, 17.8, 3.2], [46, 0, -17.3]), "#3f7f4f"))

# TANBOKU board in its bottom pocket
parts.append((box([7.75, 12.53, 1.6], [0, 0, -23.2]), "#b58900"))

LIGHT = np.array([0.5, -0.4, 0.75]); LIGHT /= np.linalg.norm(LIGHT)
tris_all, cols_all = [], []
for mesh, color in parts:
    tris_all.append(mesh.vertices[mesh.faces])
    shade = 0.45 + 0.55 * np.clip(mesh.face_normals @ LIGHT, 0, 1)
    base = np.array(matplotlib.colors.to_rgb(color))
    cols_all.append(np.clip(base[None, :] * shade[:, None], 0, 1))
tris = np.concatenate(tris_all); cols = np.concatenate(cols_all)

for elev, azim, fname in [(24, -55, "NapeDeck-case-v4.png"),
                          (80, -90, "NapeDeck-case-v4-top.png"),
                          (-28, -55, "NapeDeck-case-v4-bottom.png")]:
    fig = plt.figure(figsize=(9.5, 6.8), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tris, facecolors=cols, edgecolors="none"))
    ax.set_xlim(-85, 85); ax.set_ylim(-50, 50); ax.set_zlim(-38, 38)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off(); ax.set_box_aspect((2.2, 1.2, 1))
    fig.savefig(OUT + fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", fname)
