#!/usr/bin/env python3
"""
Bottom Trawl Net — Technical Plan (Top View, single cod-end).
Generates two variants differing in extension length.

Usage: python plano_rede.py
"""

# =============================================================
#  NET SPECIFICATIONS
# =============================================================
MOUTH_WIDTH        = 18.33   # m — total mouth opening
TOTAL_LENGTH       = 18.60   # m — body + extension
BODY_LENGTH        = 10.60   # m — body (mouth to throat)
MESH_TYPE          = "Opposite knots"
MESH_SIZE          = 2       # cm
MESH_BETWEEN_KNOTS = 1       # cm

COD_OPENING        = 3.30    # m — cod-end opening width
COD_HEIGHT         = 3.50    # m — cod-end total width (bag)
COD_LENGTH         = 5.50    # m — cod-end bag length

# Extension length differs between the two nets
NETS = [
    {"ext": 5.50, "label": "Net 1  (extension 5.50 m)", "out": "trawl_net_1"},
    {"ext": 3.50, "label": "Net 2  (extension 3.50 m)", "out": "trawl_net_2"},
]
# =============================================================

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import Polygon as MPoly


def draw_net(ext_len, label, outfile):
    fig, ax = plt.subplots(figsize=(20, 11))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    COR_BODY  = "#d6ecd6"
    COR_COD   = "#b8d8f0"
    COR_LINE  = "#1a1a1a"
    LW        = 2.0

    half_mouth  = MOUTH_WIDTH / 2        # 9.165
    half_throat = 1.20                   # throat half-width
    half_cod    = COD_OPENING / 2        # 1.65 — cod-end half-width

    x0         = 0.0
    x_throat   = BODY_LENGTH             # 10.60
    x_ext_end  = x_throat + ext_len
    x_cod_end  = x_ext_end + COD_LENGTH

    # ── Body (trapezoid: wide mouth → narrow throat) ──────────
    body = np.array([
        [x0,       half_mouth],
        [x_throat, half_throat],
        [x_throat, -half_throat],
        [x0,      -half_mouth],
    ])
    ax.add_patch(MPoly(body, closed=True,
                       facecolor=COR_BODY, edgecolor=COR_LINE, lw=LW, zorder=2))
    ax.add_patch(MPoly(body, closed=True, facecolor="none",
                       edgecolor="#5a8a5a", hatch="xx", lw=0.3, alpha=0.28, zorder=3))

    # ── Extension / emboçador (tapers from throat to cod-end) ─
    ext = np.array([
        [x_throat,  half_throat],
        [x_ext_end, half_cod],
        [x_ext_end, -half_cod],
        [x_throat, -half_throat],
    ])
    ax.add_patch(MPoly(ext, closed=True,
                       facecolor=COR_BODY, edgecolor=COR_LINE, lw=LW, zorder=2))
    ax.add_patch(MPoly(ext, closed=True, facecolor="none",
                       edgecolor="#5a8a5a", hatch="xx", lw=0.3, alpha=0.28, zorder=3))

    # ── Cod-end (single rectangle, centered) ─────────────────
    cod = np.array([
        [x_ext_end, half_cod],
        [x_ext_end, -half_cod],
        [x_cod_end, -half_cod],
        [x_cod_end,  half_cod],
    ])
    ax.add_patch(MPoly(cod, closed=True,
                       facecolor=COR_COD, edgecolor=COR_LINE, lw=LW, zorder=2))

    # Closed end reinforcement
    ax.plot([x_cod_end, x_cod_end], [-half_cod, half_cod],
            color=COR_LINE, lw=3.5, zorder=4)

    # ── Mouth line ────────────────────────────────────────────
    ax.plot([x0, x0], [-half_mouth, half_mouth],
            color=COR_LINE, lw=3.5, zorder=4)

    # ── Throat line ───────────────────────────────────────────
    ax.plot([x_throat, x_throat], [-half_throat, half_throat],
            color=COR_LINE, lw=LW, zorder=4)

    # ── Trawling direction arrow ──────────────────────────────
    ax.annotate("", xy=(-2.5, 0), xytext=(-0.3, 0),
                arrowprops=dict(arrowstyle="-|>", color="#444",
                                lw=1.5, mutation_scale=18))
    ax.text(-3.1, 0, "Trawling\ndirection", ha="right", va="center",
            fontsize=8, color="#444", style="italic")

    # ── Internal labels ───────────────────────────────────────
    def lbl(x, y, t, sz=9, bold=False, cor="#1a1a1a"):
        ax.text(x, y, t, ha="center", va="center", fontsize=sz,
                fontweight="bold" if bold else "normal", color=cor, zorder=5)

    lbl((x0 + x_throat) / 2,    0, "BODY",      sz=10, bold=True, cor="#1a5c1a")
    lbl((x_throat + x_ext_end) / 2, 0, "EXTENSION", sz=8.5, cor="#333")
    lbl((x_ext_end + x_cod_end) / 2, 0, "COD-END",  sz=9, bold=True, cor="#0a4070")
    ax.text(x0 + 0.35, 0, "MOUTH", ha="left", va="center",
            fontsize=8, rotation=90, color="#333", zorder=5)
    ax.text(x_throat + 0.2, half_throat + 0.25, "Throat",
            ha="left", va="bottom", fontsize=8, color="#555", zorder=5)

    # ── Dimension lines ───────────────────────────────────────
    def dh(x1, x2, y, t, cor="k", fs=8.5):
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="<->", color=cor,
                                    lw=1.1, mutation_scale=10))
        ax.text((x1+x2)/2, y + 0.22, t,
                ha="center", va="bottom", fontsize=fs, color=cor)

    def dv(x, y1, y2, t, cor="k", fs=8.5):
        ax.annotate("", xy=(x, y2), xytext=(x, y1),
                    arrowprops=dict(arrowstyle="<->", color=cor,
                                    lw=1.1, mutation_scale=10))
        ax.text(x + 0.15, (y1+y2)/2, t,
                ha="left", va="center", fontsize=fs, color=cor)

    def g(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color="#aaa", lw=0.7, ls=":", zorder=1)

    # Mouth width
    g(x0, -half_mouth, x0-2.1, -half_mouth)
    g(x0,  half_mouth, x0-2.1,  half_mouth)
    dv(x0-2.0, -half_mouth, half_mouth, f"{MOUTH_WIDTH} m", fs=9.5)

    # Body length
    y1 = -half_mouth - 1.3
    g(x0, -half_mouth, x0, y1); g(x_throat, -half_throat, x_throat, y1)
    dh(x0, x_throat, y1, f"Body  {BODY_LENGTH} m")

    # Extension length
    y2 = -(half_cod + 1.1)
    g(x_throat, -half_cod, x_throat, y2); g(x_ext_end, -half_cod, x_ext_end, y2)
    dh(x_throat, x_ext_end, y2, f"Extension  {ext_len} m")

    # Cod-end length
    y3 = half_cod + 1.0
    g(x_ext_end, half_cod, x_ext_end, y3); g(x_cod_end, half_cod, x_cod_end, y3)
    dh(x_ext_end, x_cod_end, y3, f"Cod-end  {COD_LENGTH} m")

    # Total length (body + extension)
    y_tot = -half_mouth - 2.4
    g(x0, -half_mouth, x0, y_tot); g(x_ext_end, -half_cod, x_ext_end, y_tot)
    dh(x0, x_ext_end, y_tot,
       f"Total length (body + extension)  {TOTAL_LENGTH} m", cor="#333", fs=9.5)

    # Cod-end width
    xd = x_cod_end + 0.7
    g(x_cod_end, -half_cod, xd, -half_cod); g(x_cod_end, half_cod, xd, half_cod)
    dv(xd, -half_cod, half_cod, f"{COD_HEIGHT} m")
    ax.text(xd + 0.15, half_cod + 0.4,
            f"(opening: {COD_OPENING} m)",
            ha="left", va="center", fontsize=7.5, color="#777")

    # ── Title ─────────────────────────────────────────────────
    ax.set_title(
        f"Bottom Trawl Net — Technical Plan  (Top View)  [{label}]",
        fontsize=14, fontweight="bold", pad=20)
    specs = (f"Mesh: {MESH_TYPE}  ·  {MESH_SIZE} cm  |  "
             f"Between knots: {MESH_BETWEEN_KNOTS} cm  |  "
             f"Cod-end opening: {COD_OPENING} m")
    ax.text(0.5, -0.01, specs, transform=ax.transAxes,
            ha="center", va="top", fontsize=8.5, color="#555")

    p1 = mpatches.Patch(facecolor=COR_BODY, edgecolor=COR_LINE, label="Body / Extension")
    p2 = mpatches.Patch(facecolor=COR_COD,  edgecolor=COR_LINE, label="Cod-end (bag)")
    ax.legend(handles=[p1, p2], loc="lower right",
              fontsize=9, framealpha=0.95, edgecolor="#ccc")

    plt.tight_layout(pad=1.5)
    plt.savefig(f"{outfile}.pdf", dpi=300, bbox_inches="tight")
    plt.savefig(f"{outfile}.png", dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {outfile}.pdf  and  {outfile}.png")
    plt.close()


for net in NETS:
    draw_net(net["ext"], net["label"], net["out"])

print("✅ Done.")
