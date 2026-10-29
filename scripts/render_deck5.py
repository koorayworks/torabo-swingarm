import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math

BASE = "/home/hatch/workspace/nape-trackball-case/deck5/"
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
POSE_L = 14.0    # left arm swung toward the user
POSE_R = -14.0   # right arm swung toward the user

parts = [
    (load("NapeDeck5-centre.stl"), CASE),
    (load("NapeDeck5-ring.stl"), "#5b8dd9"),
    (load("NapeDeck5-wirering.stl"), "#9aa2ac"),
    (rotz(load("NapeDeck5-leftarm.stl"), POSE_L), CASE),
    (rotz(load("NapeDeck5-rightarm.stl"), POSE_R), CASE),
    (rotz(load("NapeDeck5-lid.stl"), POSE_R), "#bcc2ca"),
]

ball = trimesh.creation.uv_sphere(radius=17.0, count=[48, 32])
parts.append((ball, "#c0272d"))

# display module in the lid's tilted frame, then posed with the arm
F = trimesh.transformations.translation_matrix([44, 0, 1.5]) @ \
    trimesh.transformations.rotation_matrix(math.radians(10.0), [1, 0, 0])
disp = box([31.5, 39.0, 7.2], [0, 0, 1.8])
disp.apply_transform(F)
parts.append((rotz(disp, POSE_R), "#232a33"))
screen = box([27.97, 32.63, 0.6], [0, 0, 5.7])
screen.apply_transform(F)
parts.append((rotz(screen, POSE_R), "#a8d8ea"))

for kx in (-40.0, -59.0):
    cap = box([14.0, 14.0, 7.0], [kx, 0, -8.5])
    parts.append((rotz(cap, POSE_L), "#eef0f2"))

xiao = box([21.0, 17.8, 4.6], [46, 0, -16.2])
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

for elev, azim, fname in [(24, -55, "NapeDeck-case-v5.png"),
                          (80, -90, "NapeDeck-case-v5-top.png")]:
    fig = plt.figure(figsize=(9.5, 6.8), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tris, facecolors=cols, edgecolors="none"))
    ax.set_xlim(-90, 90); ax.set_ylim(-60, 60); ax.set_zlim(-40, 40)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off(); ax.set_box_aspect((2.2, 1.2, 1))
    fig.savefig(OUT + fname, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", fname)
