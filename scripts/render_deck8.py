import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math

BASE = "/home/hatch/workspace/nape-trackball-case/deck8/"
OUT = "/home/hatch/workspace/goals/nape-trackball-redesign/files/"

def load(name):
    return trimesh.load(BASE + name)

def box(extents, center):
    m = trimesh.creation.box(extents=extents)
    m.apply_translation(center)
    return m

def rotz(mesh, deg):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.radians(deg), [0, 0, 1]))
    return m

CASE = "#ccd1d8"
POSE_L = 66.0
POSE_R = -66.0

parts = [
    (load("NapeDeck8-centre.stl"), CASE),
    (load("NapeDeck8-ring.stl"), "#5b8dd9"),
    (load("NapeDeck8-wirering.stl"), "#e0a458"),
    (rotz(load("NapeDeck8-leftarm.stl"), POSE_L), CASE),
    (rotz(load("NapeDeck8-rightarm.stl"), POSE_R), CASE),
    (rotz(load("NapeDeck8-lid.stl"), POSE_R), "#bcc2ca"),
]

ball = trimesh.creation.uv_sphere(radius=17.0, count=[48, 32])
parts.append((ball, "#c0272d"))

# display module lying FLAT in the lid pocket, posed with the arm
disp = box([39.0, 31.5, 7.2], [51, 0, -1.3])
parts.append((rotz(disp, POSE_R), "#232a33"))
screen = box([32.63, 27.97, 0.6], [51, 0, 2.6])
parts.append((rotz(screen, POSE_R), "#a8d8ea"))

for kx, ky in ((-67.5, -9.5), (-67.5, 9.5), (-48.5, -9.5), (-48.5, 9.5)):
    cap = box([14.0, 14.0, 7.0], [kx, ky, -8.5])
    parts.append((rotz(cap, POSE_L), "#eef0f2"))

xiao = box([21.0, 17.8, 4.6], [53, 0, -16.2])
parts.append((rotz(xiao, POSE_R), "#3f7f4f"))
parts.append((box([7.75, 12.53, 1.6], [0, 0, -23.2]), "#b58900"))

LIGHT = np.array([0.5, -0.4, 0.75]); LIGHT /= np.linalg.norm(LIGHT)
tris_all, cols_all = [], []
for mesh, color in parts:
    tris_all.append(mesh.vertices[mesh.faces])
    shade = 0.45 + 0.55 * np.clip(mesh.face_normals @ LIGHT, 0, 1)
    base = np.array(matplotlib.colors.to_rgb(color))
    cols_all.append(np.clip(base[None, :] * shade[:, None], 0, 1))
tris = np.concatenate(tris_all); cols = np.concatenate(cols_all)

for elev, azim, fname in [(24, -55, "NapeDeck-case-v8.png"),
                          (80, -90, "NapeDeck-case-v8-top.png")]:
    fig = plt.figure(figsize=(9.5, 6.8), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tris, facecolors=cols, edgecolors="none"))
    ax.set_xlim(-90, 90); ax.set_ylim(-60, 60); ax.set_zlim(-40, 40)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off(); ax.set_box_aspect((2.2, 1.2, 1))
    fig.savefig(OUT + fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", fname)
