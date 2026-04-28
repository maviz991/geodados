#!/usr/bin/env python3
"""
Bottom Trawl Net — Technical Plan (Development / Front View).
Matches FAO-style "ESQUEMA TÉCNICO DE REDE DE ARRASTO V-FORM" format.
Two net variants side by side: extension 5.50 m vs 3.50 m.

Usage: python3 plano_rede_frontal.py
"""

# =============================================================
#  NET SPECIFICATIONS
# =============================================================
MOUTH_WIDTH   = 18.33   # m  — total mouth / headline
BODY_LENGTH   = 10.60   # m  — body (mouth → throat)
THROAT_WIDTH  = 2.40    # m  — throat opening
MESH_MM       = 20      # mm — mesh size (opposite knots)
THREAD_MM     = 1       # mm — knot distance
MATERIAL      = "PA"
NET_CODE      = "IN 28"

COD_OPENING   = 3.30    # m  — cod-end opening (connecting to extension)
COD_HEIGHT    = 3.50    # m  — cod-end total width (bag)
COD_LENGTH    = 5.50    # m  — cod-end bag length
COD_MESH_MM   = 120     # mm — cod-end mesh size

EXT1          = 5.50    # m  — extension, Net 1
EXT2          = 3.50    # m  — extension, Net 2

# Wing geometry (asa)
WING_W        = 2.20    # m  — wing width beyond mouth edge
WING_DEPTH    = 2.50    # m  — depth where wing base meets body

# Panel seam positions (fractions of body length from mouth)
SEAMS = [0.20, 0.44, 0.66, 0.85]

# Approximate mesh counts at each panel boundary (based on 20 mm mesh)
# [mouth, seam1, seam2, seam3, seam4, throat]
PANEL_M = [910, 756, 566, 390, 240, 120]
# =============================================================

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
from matplotlib.patches import Polygon as MPoly, FancyBboxPatch, Ellipse

# ── Derived geometry ──────────────────────────────────────────
half_m   = MOUTH_WIDTH / 2      # 9.165
half_th  = THROAT_WIDTH / 2     # 1.20
half_co  = COD_OPENING  / 2     # 1.65
half_bag = COD_HEIGHT   / 2     # 1.75

# Body half-width at fractional depth
def bx(frac): return half_m + (half_th - half_m) * frac

# Seam boundary half-widths
seam_y  = [BODY_LENGTH * f for f in SEAMS]
seam_bx = [bx(f)           for f in SEAMS]

GAP = 6.0   # horizontal gap between the two nets (centre-to-centre of mouths)

# Net centre-x positions
cx1 = -(half_m + WING_W + GAP / 2)
cx2 = +(half_m + WING_W + GAP / 2)

# Colours
C_WING = "#cce8cc"
C_BODY = "#d8eed8"
C_EXT  = "#e8f5e8"
C_COD  = "#b8d4f0"
C_LN   = "#111111"
LW     = 1.8


# ── Figure layout ─────────────────────────────────────────────
fig = plt.figure(figsize=(32, 28))
fig.patch.set_facecolor("white")

# Main plan occupies ~70% height; profile view at bottom ~18%
ax  = fig.add_axes([0.03, 0.26, 0.94, 0.70])
ax2 = fig.add_axes([0.05, 0.03, 0.90, 0.20])

for a in [ax, ax2]:
    a.set_facecolor("white")
    a.axis("off")
ax.set_aspect("equal")
ax.invert_yaxis()


# =================================================================
def draw_net(cx, ext, net_label, side):
    ye = BODY_LENGTH + ext
    yc = ye + COD_LENGTH

    wing_frac   = WING_DEPTH / BODY_LENGTH
    bx_wing     = bx(wing_frac)
    y_wing_base = WING_DEPTH

    # ── Wings ───────────────────────────────────────────────────
    for sgn, ha_lbl in [(-1, "right"), (+1, "left")]:
        wpts = np.array([
            [cx + sgn * half_m,             0.0],
            [cx + sgn * (half_m + WING_W),  0.0],
            [cx + sgn * bx_wing,            y_wing_base],
        ])
        ax.add_patch(MPoly(wpts, closed=True,
                           facecolor=C_WING, edgecolor=C_LN, lw=LW, zorder=2))
        ax.add_patch(MPoly(wpts, closed=True, facecolor="none",
                           edgecolor="#448844", hatch="\\\\",
                           lw=0.3, alpha=0.22, zorder=3))
        # Wing rope label
        mid_x = cx + sgn * (half_m + WING_W * 0.60)
        mid_y = y_wing_base * 0.45
        ax.text(mid_x, mid_y,
                f"{NET_CODE}\n{MESH_MM} mm\nASA",
                ha=ha_lbl, va="center", fontsize=7.5, color="#1a4a1a",
                fontweight="bold", zorder=6)

    # Outer wing measurement arrow
    for sgn, ha_ in [(-1, "right"), (+1, "left")]:
        xw_out = cx + sgn * (half_m + WING_W)
        ax.annotate("", xy=(cx + sgn * half_m, -1.4),
                    xytext=(xw_out, -1.4),
                    arrowprops=dict(arrowstyle="<->", color="#555",
                                   lw=0.9, mutation_scale=8))
        ax.text(cx + sgn * (half_m + WING_W * 0.5), -1.7,
                f"{WING_W:.2f} m",
                ha="center", va="top", fontsize=7.5, color="#555")

    # ── Body (trapezoid) ────────────────────────────────────────
    body = np.array([
        [cx - half_m,  0.0],      [cx + half_m,  0.0],
        [cx + half_th, BODY_LENGTH], [cx - half_th, BODY_LENGTH],
    ])
    ax.add_patch(MPoly(body, closed=True,
                       facecolor=C_BODY, edgecolor=C_LN, lw=LW, zorder=2))
    ax.add_patch(MPoly(body, closed=True, facecolor="none",
                       edgecolor="#448844", hatch="xx",
                       lw=0.3, alpha=0.15, zorder=3))

    # ── Extension ───────────────────────────────────────────────
    ext_pts = np.array([
        [cx - half_th, BODY_LENGTH], [cx + half_th, BODY_LENGTH],
        [cx + half_co, ye],          [cx - half_co, ye],
    ])
    ax.add_patch(MPoly(ext_pts, closed=True,
                       facecolor=C_EXT, edgecolor=C_LN, lw=LW, zorder=2))
    ax.add_patch(MPoly(ext_pts, closed=True, facecolor="none",
                       edgecolor="#448844", hatch="//",
                       lw=0.3, alpha=0.15, zorder=3))

    # ── Cod-end ──────────────────────────────────────────────────
    cod = np.array([
        [cx - half_bag, ye],  [cx + half_bag, ye],
        [cx + half_bag, yc],  [cx - half_bag, yc],
    ])
    ax.add_patch(MPoly(cod, closed=True,
                       facecolor=C_COD, edgecolor=C_LN, lw=LW, zorder=2))
    # Closing reinforcement line
    ax.plot([cx - half_bag, cx + half_bag], [yc, yc],
            color=C_LN, lw=3.5, zorder=5)
    # Cod-end centre labels
    yc_mid = (ye + yc) / 2
    ax.text(cx, yc_mid - 0.6,
            f"{COD_MESH_MM} mm {MATERIAL}",
            ha="center", va="center", fontsize=8,
            fontweight="bold", color="#0a3060", zorder=6)
    ax.text(cx, yc_mid + 0.2,
            f"Opening: {COD_OPENING} m",
            ha="center", va="center", fontsize=7.5, color="#0a3060", zorder=6)
    ax.text(cx, yc_mid + 0.9,
            f"Width: {COD_HEIGHT} m  |  L: {COD_LENGTH} m",
            ha="center", va="center", fontsize=7, color="#2060a0", zorder=6)

    # ── Boundary lines ───────────────────────────────────────────
    ax.plot([cx - half_m,   cx + half_m],   [0.0, 0.0],
            color=C_LN, lw=3.0, zorder=5)  # mouth
    ax.plot([cx - half_th,  cx + half_th],  [BODY_LENGTH, BODY_LENGTH],
            color=C_LN, lw=LW, zorder=5)   # throat
    ax.plot([cx - half_co,  cx + half_co],  [ye, ye],
            color=C_LN, lw=LW, zorder=5)   # ext/cod junction

    # ── Panel seam lines ─────────────────────────────────────────
    all_bounds = (
        [(0.0, half_m)]
        + list(zip(seam_y, seam_bx))
        + [(BODY_LENGTH, half_th)]
    )

    for ys, xw in zip(seam_y, seam_bx):
        ax.plot([cx - xw, cx + xw], [ys, ys],
                color="#444", lw=1.0, ls="--", zorder=4)

    # Extension mid-seam
    y_emid = (BODY_LENGTH + ye) / 2
    fe = (y_emid - BODY_LENGTH) / ext if ext > 0 else 0
    xw_e = half_th + (half_co - half_th) * fe
    ax.plot([cx - xw_e, cx + xw_e], [y_emid, y_emid],
            color="#666", lw=0.8, ls="--", zorder=4)

    # Cod mid-seam
    y_cmid = (ye + yc) / 2
    ax.plot([cx - half_bag, cx + half_bag], [y_cmid, y_cmid],
            color="#4477aa", lw=0.8, ls="--", zorder=4)

    # ── Panel labels — mesh count (centre) & depth (side) ────────
    sgn_s = -1 if side == "left" else +1
    x_side = cx + sgn_s * (half_m + WING_W + 1.2)

    # Body panels
    for i in range(len(all_bounds) - 1):
        y_a, xw_a = all_bounds[i]
        y_b, xw_b = all_bounds[i + 1]
        y_mid = (y_a + y_b) / 2
        depth = y_b - y_a
        m_count = PANEL_M[i]
        ax.text(cx, y_mid - 0.35,
                f"{MATERIAL}  {m_count}",
                ha="center", va="center", fontsize=9,
                color="#1a4a1a", fontweight="bold", zorder=6)
        ax.text(cx, y_mid + 0.35,
                f"{MESH_MM} mm",
                ha="center", va="center", fontsize=7.5,
                color="#2a6a2a", zorder=6)
        ax.text(x_side, y_mid,
                f"{depth:.2f} m",
                ha="center", va="center", fontsize=7.5,
                color="#555", zorder=6)

    # Extension label
    y_e_mid = (BODY_LENGTH + ye) / 2
    ax.text(cx, y_e_mid - 0.3,
            f"{MATERIAL}  {MESH_MM} mm",
            ha="center", va="center", fontsize=8.5,
            fontweight="bold", color="#2a5a2a", zorder=6)
    ax.text(cx, y_e_mid + 0.35,
            f"EXTENSION  ({ext} m)",
            ha="center", va="center", fontsize=7.5,
            color="#2a5a2a", zorder=6)
    ax.text(x_side, y_e_mid,
            f"{ext:.2f} m",
            ha="center", va="center", fontsize=7.5, color="#555", zorder=6)

    # ── Net label above mouth ─────────────────────────────────────
    ax.text(cx, -3.5, net_label,
            ha="center", va="bottom", fontsize=12,
            fontweight="bold", color="#111")
    ax.text(cx, -2.8,
            f"Mouth: {MOUTH_WIDTH} m  |  Mesh: {MESH_MM} mm",
            ha="center", va="bottom", fontsize=8.5, color="#444")

    # Mouth width arrow
    ax.annotate("", xy=(cx + half_m, -2.2),
                xytext=(cx - half_m, -2.2),
                arrowprops=dict(arrowstyle="<->", color="#222",
                               lw=1.0, mutation_scale=10))
    ax.text(cx, -2.0,
            f"← {MOUTH_WIDTH} m →",
            ha="center", va="bottom", fontsize=9, color="#222")

    # ── Outer dimension lines (body/ext/total) ────────────────────
    if side == "left":
        xd = cx - half_m - WING_W - 2.2
        xd2 = xd - 1.8

        def gl(y_, x_): ax.plot([cx - x_, xd], [y_, y_],
                                color="#ccc", lw=0.6, ls=":", zorder=1)
        def dvl(ya_, yb_, t_):
            ax.annotate("", xy=(xd, yb_), xytext=(xd, ya_),
                        arrowprops=dict(arrowstyle="<->", color="#444",
                                       lw=1.0, mutation_scale=9))
            ax.text(xd - 0.2, (ya_ + yb_) / 2, t_,
                    ha="right", va="center", fontsize=8.5, color="#333")

        gl(0.0, half_m);         gl(BODY_LENGTH, half_th)
        dvl(0.0, BODY_LENGTH, f"Body  {BODY_LENGTH} m")
        gl(BODY_LENGTH, half_th); gl(ye, half_co)
        dvl(BODY_LENGTH, ye,     f"Ext.  {ext} m")
        gl(ye, half_co);          gl(yc, half_bag)
        dvl(ye, yc,              f"Cod  {COD_LENGTH} m")

        ax.plot([cx - half_m,  xd2], [0.0, 0.0], color="#bbb", lw=0.6, ls=":")
        ax.plot([cx - half_co, xd2], [ye,  ye],  color="#bbb", lw=0.6, ls=":")
        ax.annotate("", xy=(xd2, ye), xytext=(xd2, 0.0),
                    arrowprops=dict(arrowstyle="<->", color="#333",
                                   lw=1.2, mutation_scale=9))
        ax.text(xd2 - 0.2, (0.0 + ye) / 2,
                f"Total\n{BODY_LENGTH + ext:.2f} m",
                ha="right", va="center", fontsize=8.5, color="#222")
    else:
        xd = cx + half_m + WING_W + 2.2
        xd2 = xd + 1.8

        def gr(y_, x_): ax.plot([cx + x_, xd], [y_, y_],
                                color="#ccc", lw=0.6, ls=":", zorder=1)
        def dvr(ya_, yb_, t_):
            ax.annotate("", xy=(xd, yb_), xytext=(xd, ya_),
                        arrowprops=dict(arrowstyle="<->", color="#444",
                                       lw=1.0, mutation_scale=9))
            ax.text(xd + 0.2, (ya_ + yb_) / 2, t_,
                    ha="left", va="center", fontsize=8.5, color="#333")

        gr(0.0, half_m);          gr(BODY_LENGTH, half_th)
        dvr(0.0, BODY_LENGTH, f"Body  {BODY_LENGTH} m")
        gr(BODY_LENGTH, half_th); gr(ye, half_co)
        dvr(BODY_LENGTH, ye,     f"Ext.  {ext} m")
        gr(ye, half_co);          gr(yc, half_bag)
        dvr(ye, yc,              f"Cod  {COD_LENGTH} m")

        ax.plot([cx + half_m,  xd2], [0.0, 0.0], color="#bbb", lw=0.6, ls=":")
        ax.plot([cx + half_co, xd2], [ye,  ye],  color="#bbb", lw=0.6, ls=":")
        ax.annotate("", xy=(xd2, ye), xytext=(xd2, 0.0),
                    arrowprops=dict(arrowstyle="<->", color="#333",
                                   lw=1.2, mutation_scale=9))
        ax.text(xd2 + 0.2, (0.0 + ye) / 2,
                f"Total\n{BODY_LENGTH + ext:.2f} m",
                ha="left", va="center", fontsize=8.5, color="#222")

    # Cod-end width arrow (bottom)
    ax.annotate("", xy=(cx + half_bag, yc + 0.6),
                xytext=(cx - half_bag, yc + 0.6),
                arrowprops=dict(arrowstyle="<->", color="#0a3060",
                               lw=0.9, mutation_scale=8))
    ax.text(cx, yc + 0.9,
            f"{COD_HEIGHT} m",
            ha="center", va="top", fontsize=8, color="#0a3060")

    # ── Section name labels (vertical, outside net) ───────────────
    sgn2 = -1 if side == "left" else +1
    xn = cx + sgn2 * (half_m + WING_W + 0.45)
    rot = 90 if side == "left" else 270
    for y_s, y_e, lbl, col, bld in [
        (0.0,        BODY_LENGTH, "BODY",      "#1a5c1a", True),
        (BODY_LENGTH, ye,         "EXTENSION", "#2a5c2a", False),
        (ye,          yc,         "COD-END",   "#0a3060", True),
    ]:
        ax.text(xn, (y_s + y_e) / 2, lbl,
                ha="center", va="center", fontsize=8.5,
                fontweight="bold" if bld else "normal",
                color=col, rotation=rot, zorder=6)


# =================================================================
#  DRAW BOTH NETS
# =================================================================
draw_net(cx1, EXT1, f"Net 1°  —  Extension {EXT1} m", side="left")
draw_net(cx2, EXT2, f"Net 2°  —  Extension {EXT2} m", side="right")


# =================================================================
#  CENTRAL MATERIAL SPECIFICATION TABLE
# =================================================================
# Positioned between the two nets in the centre column
tbl_x  = 0.0
tbl_ys = [BODY_LENGTH * 0.12,   # top section
          BODY_LENGTH * 0.38,
          BODY_LENGTH * 0.62,
          BODY_LENGTH * 0.80,
          BODY_LENGTH * 0.92]

# Table header box
ax.text(tbl_x, -0.6,
        "MATERIAL SPECIFICATIONS",
        ha="center", va="bottom", fontsize=9,
        fontweight="bold", color="#111",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0",
                  edgecolor="#888", lw=1.0))

rows = [
    ("mm", "Type",     "R-tex"),
    (f"{MESH_MM}",  MATERIAL,  f"{MESH_MM}"),
    ("20",  "PA IN-28", "20"),
    ("20",  "PA IN-28", "20"),
    (f"{COD_MESH_MM}", f"{MATERIAL} d:3", "—"),
]
headers = ["Mesh mm", "Mat.", "Thread"]
col_x = [-1.6, 0.0, 1.6]

# Draw header
for cx_t, hdr in zip(col_x, headers):
    ax.text(tbl_x + cx_t, BODY_LENGTH * 0.05,
            hdr, ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="#333")
ax.plot([tbl_x - 2.1, tbl_x + 2.1],
        [BODY_LENGTH * 0.08, BODY_LENGTH * 0.08],
        color="#888", lw=0.8)

for (v1, v2, v3), ty in zip(rows[1:], tbl_ys):
    ax.text(tbl_x - 1.6, ty, v1,
            ha="center", va="center", fontsize=7.5, color="#222")
    ax.text(tbl_x,       ty, v2,
            ha="center", va="center", fontsize=8,
            fontweight="bold", color="#1a4a1a")
    ax.text(tbl_x + 1.6, ty, v3,
            ha="center", va="center", fontsize=7.5, color="#222")

# Separator lines
for ty in tbl_ys:
    ax.plot([tbl_x - 2.1, tbl_x + 2.1], [ty + 0.5, ty + 0.5],
            color="#ddd", lw=0.5, ls="-")

# Box around table
from matplotlib.patches import FancyBboxPatch
rect = FancyBboxPatch(
    (tbl_x - 2.2, -0.2), 4.4, BODY_LENGTH * 0.97,
    boxstyle="round,pad=0.1",
    facecolor="none", edgecolor="#999", lw=1.0, zorder=1
)
ax.add_patch(rect)


# =================================================================
#  SIDE PROFILE  (ax2 — operational rig diagram)
# =================================================================
ax2.set_xlim(-2, 65)
ax2.set_ylim(-4, 7)
ax2.invert_yaxis()

# Background label
ax2.text(32.5, -3.5,
         "SIDE PROFILE — OPERATIONAL RIGGING",
         ha="center", va="bottom", fontsize=9,
         fontweight="bold", color="#333")
ax2.axhline(y=-3.2, xmin=0.02, xmax=0.98, color="#bbb", lw=0.7, ls="--")

# ── Trawl warp (steel cable) ──────────────────────────────────
ax2.plot([0, 10], [2.0, 1.5], color="#444", lw=2.0)
ax2.text(5, 0.8, "Steel wire  Ø8 mm\n1.30×0.65  /  40–60 kg",
         ha="center", va="bottom", fontsize=7, color="#333")

# ── Ground rope ───────────────────────────────────────────────
ax2.plot([10, 38], [1.5, 0.8], color="#444", lw=2.0)
ax2.text(24, -0.2, "20.00–30.00 m   MISTO  Ø12–14",
         ha="center", va="bottom", fontsize=7.5, color="#333")

ax2.plot([38, 48], [0.8, 0.4], color="#555", lw=1.8)
ax2.text(43, -0.5, "10.00 m  MISTO  Ø10",
         ha="center", va="bottom", fontsize=7, color="#333")

ax2.plot([48, 52], [0.4, 0.2], color="#555", lw=1.5)
ax2.text(50, -0.8, "3.00 m  MISTO  Ø12\n1.00 m",
         ha="center", va="bottom", fontsize=6.5, color="#555")

# ── Net body (profile view) ───────────────────────────────────
net_profile = np.array([
    [52,  0.2], [55, -0.5], [60, -2.2],
    [60,  2.8], [55,  2.0], [52,  1.8]
])
ax2.add_patch(MPoly(net_profile, closed=True,
                    facecolor="#c8e8c8", edgecolor="#333",
                    lw=1.0, zorder=2))
ax2.add_patch(MPoly(net_profile, closed=True, facecolor="none",
                    edgecolor="#5a8a5a", hatch="xx",
                    lw=0.3, alpha=0.30, zorder=3))

# ── Floats ────────────────────────────────────────────────────
for xf in np.linspace(53.5, 59.5, 9):
    ax2.add_patch(plt.Circle((xf, -2.5), 0.22,
                              facecolor="#ffe", edgecolor="#aa8800",
                              lw=0.9, zorder=4))
ax2.text(56.5, -3.0,
         "Floats: PL 9–15  Ø13 cm\nor 3–4  Ø20 cm",
         ha="center", va="top", fontsize=7, color="#665500")

# ── Ground rope + chain ───────────────────────────────────────
ax2.plot([52, 60], [2.8, 2.8], color="#777", lw=2.5)
ax2.plot([42, 52], [1.5, 2.8], color="#999", lw=1.0, ls="--")
ax2.text(55, 3.3,
         "Regulation chain / footrope",
         ha="center", va="top", fontsize=7, color="#555")

# ── Cod-end (ellipse) ─────────────────────────────────────────
ell = Ellipse((57.5, -0.8), width=4.5, height=3.0,
              facecolor=C_COD, edgecolor="#333", lw=1.0, zorder=3)
ax2.add_patch(ell)
ax2.text(57.5, -0.8,
         "COD\nEND",
         ha="center", va="center", fontsize=7,
         fontweight="bold", color="#0a3060", zorder=5)

# ── Ballast info ─────────────────────────────────────────────
ax2.text(30, 4.5,
         "Ballast: 8–14 kg on footrope  |  2–3 kg each wing tip",
         ha="center", va="top", fontsize=7.5, color="#444")

# ── Door / otter board (simplified) ──────────────────────────
for xb, side_lbl in [(5.5, "Port"), (7.5, "Stbd")]:
    ax2.add_patch(FancyBboxPatch((xb - 0.4, 0.5), 0.8, 2.5,
                                  boxstyle="round,pad=0.05",
                                  facecolor="#d8d8d8", edgecolor="#444",
                                  lw=1.0, zorder=4))
ax2.text(6.5, 3.2, "Otter\nboards",
         ha="center", va="top", fontsize=7, color="#444")


# =================================================================
#  MAIN TITLE
# =================================================================
fig.text(0.5, 0.998,
         "ESQUEMA TÉCNICO DE REDE DE ARRASTO V-FORM\n"
         "Bottom Trawl Net — Technical Plan  (Development View)",
         ha="center", va="top", fontsize=15,
         fontweight="bold", color="#0a1a3a")
fig.text(0.5, 0.970,
         f"Mesh: {MATERIAL}  {MESH_MM} mm  opposite knots  |  "
         f"Thread: {THREAD_MM} mm  |  "
         f"Mouth: {MOUTH_WIDTH} m  |  "
         f"Throat: {THROAT_WIDTH} m  |  "
         f"Cod-end: {COD_OPENING} m opening  /  {COD_HEIGHT} m wide  /  {COD_LENGTH} m long",
         ha="center", va="top", fontsize=9, color="#444")

# Legend
handles = [
    mpatches.Patch(facecolor=C_WING, edgecolor=C_LN,  label="Wings (asas)"),
    mpatches.Patch(facecolor=C_BODY, edgecolor=C_LN,  label="Body (corpo)"),
    mpatches.Patch(facecolor=C_EXT,  edgecolor=C_LN,  label="Extension (emboçador)"),
    mpatches.Patch(facecolor=C_COD,  edgecolor=C_LN,  label="Cod-end (ensacador)"),
    mlines.Line2D([], [], color="#444", ls="--", label="Panel seam lines"),
]
ax.legend(handles=handles, loc="lower right",
          fontsize=8.5, framealpha=0.95, edgecolor="#ccc")

plt.savefig("trawl_net_plan.pdf", dpi=300, bbox_inches="tight")
plt.savefig("trawl_net_plan.png", dpi=300, bbox_inches="tight")
print("✅ Saved: trawl_net_plan.pdf  and  trawl_net_plan.png")
plt.close()
