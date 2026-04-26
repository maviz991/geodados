#!/usr/bin/env python3
"""
Plano técnico da rede de arrasto de fundo — Vista frontal do ensacador (Y).
Perspectiva de quem olha a rede de trás para frente.
Gera PDF e PNG.

Uso: python plano_rede_frontal.py
"""

# =============================================================
#  ESPECIFICAÇÕES DA REDE — ajuste aqui
# =============================================================
ABERTURA_BOCA      = 18.33
MALHA_TIPO         = "Nós opostos"
MALHA_TAMANHO      = 2
MALHA_ENTRE_NOS    = 1

ABERTURA_Y         = 3.30    # m — abertura de cada ensacador
ALTURA_ENSACADOR   = 3.50    # m — altura de cada ensacador
COMP_SACO          = 5.50    # m — comprimento do saco
DIST_ENSACADORES   = 2.00    # m — separação entre ensacadores

SAIDA = "trawl_net_frontal"
# =============================================================

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import Polygon as MPoly

fig, ax = plt.subplots(figsize=(13, 11))
ax.set_aspect("equal")
ax.axis("off")
ax.set_facecolor("white")
fig.patch.set_facecolor("white")

COR_ENS   = "#c4e0f8"
COR_CORPO = "#ddeedd"
COR_BORDA = "#1a1a1a"

# ── Posições ──────────────────────────────────────────────────
gap      = DIST_ENSACADORES       # 2.00 m
ab_y     = ABERTURA_Y             # 3.30 m
ens_h    = ALTURA_ENSACADOR       # 3.50 m
stem_w   = 1.60                   # largura do emboçador (seção frontal)
branch_h = 1.80                   # altura da região de bifurcação do Y
stem_h   = 2.40                   # altura do tronco abaixo da bifurcação

# x: bordas dos ensacadores
xi_r =  gap / 2                   #  1.00  borda interna direita
xo_r =  gap / 2 + ab_y           #  4.30  borda externa direita
xi_l = -gap / 2                   # -1.00
xo_l = -(gap / 2 + ab_y)         # -4.30

# x: bordas do emboçador (tronco)
xs_r =  stem_w / 2               #  0.80
xs_l = -stem_w / 2               # -0.80

# y: níveis
y_ens_bot  =  0.0
y_ens_top  =  ens_h              #  3.50
y_fork     = -branch_h           # -1.80  (ponto de bifurcação)
y_stem_bot = -branch_h - stem_h  # -4.20  (base do tronco)


# ================================================================
#  ENSACADOR DIREITO
# ================================================================
right_pts = np.array([
    [xi_r, y_ens_bot], [xi_r, y_ens_top],
    [xo_r, y_ens_top], [xo_r, y_ens_bot],
])
ax.add_patch(MPoly(right_pts, closed=True,
                   facecolor=COR_ENS, edgecolor=COR_BORDA, lw=2.0, zorder=2))
ax.add_patch(MPoly(right_pts, closed=True, facecolor="none",
                   edgecolor="#3a6a9a", hatch="xx", lw=0.3, alpha=0.25, zorder=3))

# ================================================================
#  ENSACADOR ESQUERDO
# ================================================================
left_pts = np.array([
    [xi_l, y_ens_bot], [xi_l, y_ens_top],
    [xo_l, y_ens_top], [xo_l, y_ens_bot],
])
ax.add_patch(MPoly(left_pts, closed=True,
                   facecolor=COR_ENS, edgecolor=COR_BORDA, lw=2.0, zorder=2))
ax.add_patch(MPoly(left_pts, closed=True, facecolor="none",
                   edgecolor="#3a6a9a", hatch="xx", lw=0.3, alpha=0.25, zorder=3))

# ================================================================
#  ALA DIREITA DO Y  (bifurcação)
#  Trapézio: base estreita no fork → largura do ensacador na abertura
# ================================================================
wing_r = np.array([
    [0,    y_fork],     # centro, nível da bifurcação
    [xs_r, y_fork],     # borda do emboçador, nível da bifurcação
    [xo_r, y_ens_bot],  # canto externo do ensacador direito
    [xi_r, y_ens_bot],  # canto interno do ensacador direito
])
ax.add_patch(MPoly(wing_r, closed=True,
                   facecolor=COR_CORPO, edgecolor=COR_BORDA, lw=1.8, zorder=2))
ax.add_patch(MPoly(wing_r, closed=True, facecolor="none",
                   edgecolor="#5a8a5a", hatch="//", lw=0.3, alpha=0.3, zorder=3))

# ================================================================
#  ALA ESQUERDA DO Y  (bifurcação)
# ================================================================
wing_l = np.array([
    [xs_l, y_fork],     # borda do emboçador, nível da bifurcação
    [0,    y_fork],     # centro, nível da bifurcação
    [xi_l, y_ens_bot],  # canto interno do ensacador esquerdo
    [xo_l, y_ens_bot],  # canto externo do ensacador esquerdo
])
ax.add_patch(MPoly(wing_l, closed=True,
                   facecolor=COR_CORPO, edgecolor=COR_BORDA, lw=1.8, zorder=2))
ax.add_patch(MPoly(wing_l, closed=True, facecolor="none",
                   edgecolor="#5a8a5a", hatch="//", lw=0.3, alpha=0.3, zorder=3))

# ================================================================
#  TRONCO DO Y  (emboçador)
# ================================================================
stem_pts = np.array([
    [xs_l, y_fork],     [xs_r, y_fork],
    [xs_r, y_stem_bot], [xs_l, y_stem_bot],
])
ax.add_patch(MPoly(stem_pts, closed=True,
                   facecolor=COR_CORPO, edgecolor=COR_BORDA, lw=1.8, zorder=4))
ax.add_patch(MPoly(stem_pts, closed=True, facecolor="none",
                   edgecolor="#5a8a5a", hatch="//", lw=0.3, alpha=0.3, zorder=5))

# Seta abaixo do tronco
ax.annotate("", xy=(0, y_stem_bot - 0.5), xytext=(0, y_stem_bot),
            arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.5, mutation_scale=14))
ax.text(0, y_stem_bot - 0.75, "→ Net body",
        ha="center", va="top", fontsize=8.5, color="#555", style="italic")


# ================================================================
#  RÓTULOS
# ================================================================
ax.text((xi_r + xo_r) / 2, ens_h / 2,
        "COD-END\n(Bag)", ha="center", va="center",
        fontsize=9.5, fontweight="bold", color="#0a4070", zorder=6)
ax.text((xi_l + xo_l) / 2, ens_h / 2,
        "COD-END\n(Bag)", ha="center", va="center",
        fontsize=9.5, fontweight="bold", color="#0a4070", zorder=6)
ax.text(0, (y_fork + y_stem_bot) / 2,
        "EXTENSION", ha="center", va="center",
        fontsize=8.5, color="#1a5c1a", zorder=6)
ax.text((xi_r + xo_r) / 2, y_fork / 2,
        "Y-split", ha="center", va="center",
        fontsize=7.5, color="#444", zorder=6)
ax.text((xi_l + xo_l) / 2, y_fork / 2,
        "Y-split", ha="center", va="center",
        fontsize=7.5, color="#444", zorder=6)


# ================================================================
#  COTAS
# ================================================================
def dim_h(x1, x2, y, txt, cor="k", fs=8.5):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="<->", color=cor, lw=1.0, mutation_scale=10))
    ax.text((x1+x2)/2, y + 0.15, txt,
            ha="center", va="bottom", fontsize=fs, color=cor)

def dim_v(x, y1, y2, txt, cor="k", fs=8.5):
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="<->", color=cor, lw=1.0, mutation_scale=10))
    ax.text(x + 0.12, (y1+y2)/2, txt,
            ha="left", va="center", fontsize=fs, color=cor)

def guide(x1, y1, x2, y2):
    ax.plot([x1, x2], [y1, y2], color="#aaa", lw=0.7, ls=":", zorder=1)

# Abertura Y (largura de cada ensacador)
y_d = ens_h + 0.8
guide(xi_r, ens_h, xi_r, y_d);  guide(xo_r, ens_h, xo_r, y_d)
dim_h(xi_r, xo_r, y_d, f"Y opening  {ABERTURA_Y} m")
guide(xi_l, ens_h, xi_l, y_d);  guide(xo_l, ens_h, xo_l, y_d)
dim_h(xo_l, xi_l, y_d, f"Y opening  {ABERTURA_Y} m")

# Largura total do conjunto
y_tot = ens_h + 1.8
guide(xo_l, ens_h, xo_l, y_tot);  guide(xo_r, ens_h, xo_r, y_tot)
total_w = 2 * (gap/2 + ab_y)
dim_h(xo_l, xo_r, y_tot,
      f"Total assembly width  {total_w:.2f} m", cor="#333", fs=9)

# Altura do ensacador
x_hd = xo_r + 0.7
guide(xo_r, y_ens_bot, x_hd, y_ens_bot);  guide(xo_r, y_ens_top, x_hd, y_ens_top)
dim_v(x_hd, y_ens_bot, y_ens_top, f"{ALTURA_ENSACADOR} m")

# Separação entre ensacadores — no espaço em branco entre eles
y_sep = ens_h / 2
guide(xi_l, y_sep, xi_r, y_sep)
dim_h(xi_l, xi_r, y_sep - 0.3, f"Gap  {DIST_ENSACADORES} m", cor="#555", fs=8)

# Comprimento do saco (anotação lateral)
ax.text(xo_r + 0.7 + 0.15 + 1.2, ens_h / 2,
        f"Bag length:\n{COMP_SACO} m\n(in depth)",
        ha="left", va="center", fontsize=8.5, color="#333",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#f8f8f8",
                  edgecolor="#bbb", lw=0.8))


# ================================================================
#  TÍTULO
# ================================================================
ax.set_title(
    "Bottom Trawl Net — Technical Plan  (Front View — Y Cod-end Assembly)",
    fontsize=13, fontweight="bold", pad=18
)
specs = (
    f"Mesh: {MALHA_TIPO}  ·  {MALHA_TAMANHO} cm  |  "
    f"Between knots: {MALHA_ENTRE_NOS} cm  |  "
    f"Mouth opening: {ABERTURA_BOCA} m"
)
ax.text(0.5, -0.01, specs, transform=ax.transAxes,
        ha="center", va="top", fontsize=8.5, color="#555")

p_ens  = mpatches.Patch(facecolor=COR_ENS,   edgecolor=COR_BORDA, label="Cod-end (bag)")
p_emb  = mpatches.Patch(facecolor=COR_CORPO, edgecolor=COR_BORDA, label="Extension / Y-split")
ax.legend(handles=[p_ens, p_emb], loc="lower right",
          fontsize=9, framealpha=0.95, edgecolor="#ccc")

plt.tight_layout(pad=1.5)
plt.savefig(f"{SAIDA}.pdf", dpi=300, bbox_inches="tight")
plt.savefig(f"{SAIDA}.png", dpi=300, bbox_inches="tight")
print(f"✅ Salvo: {SAIDA}.pdf e {SAIDA}.png")
plt.close()
