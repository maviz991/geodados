#!/usr/bin/env python3
"""
Plano técnico da rede de arrasto de fundo (bottom trawl).
Vista superior (plano horizontal).

Gera 2 versões:
  plano_rede_1.pdf/png  — Rede 1°  (saco 5.50 m)
  plano_rede_2.pdf/png  — Rede 2°  (saco 3.50 m)

Uso: python plano_rede.py
"""

# =============================================================
#  ESPECIFICAÇÕES COMUNS (iguais nas 2 redes)
# =============================================================
ABERTURA_BOCA      = 18.33
COMPRIMENTO_TOTAL  = 18.60
DIST_BOCA_FUNDO    = 10.60
MALHA_TIPO         = "Nós opostos"
MALHA_TAMANHO      = 2
MALHA_ENTRE_NOS    = 1

ABERTURA_Y         = 3.30
ALTURA_ENSACADOR   = 3.50
COMP_SACO          = 5.50
DIST_ENSACADORES   = 2.00

# Distância do emboçador ao ensacador difere entre as 2 redes
REDES = [
    {"dist_emb": 5.50, "label": "Net 1  (extension 5.50 m)", "saida": "trawl_net_1"},
    {"dist_emb": 3.50, "label": "Net 2  (extension 3.50 m)", "saida": "trawl_net_2"},
]
# =============================================================

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import Polygon as MPoly


def gerar_plano(dist_emb, label_rede, saida):

    fig, ax = plt.subplots(figsize=(20, 12))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    COR_CORPO = "#d6ecd6"
    COR_ENS   = "#b8d8f0"
    COR_BORDA = "#1a1a1a"
    LW        = 2.0

    meia_boca  = ABERTURA_BOCA / 2
    meia_garg  = 1.20
    sep        = DIST_ENSACADORES / 2
    ens_h      = ALTURA_ENSACADOR

    x0         = 0.0
    x_garg     = DIST_BOCA_FUNDO
    x_emb_fim  = x_garg + dist_emb
    x_saco_fim = x_emb_fim + COMP_SACO

    # ── Corpo ────────────────────────────────────────────────
    corpo_pts = np.array([
        [x0,    meia_boca],  [x_garg,  meia_garg],
        [x_garg, -meia_garg], [x0,    -meia_boca],
    ])
    ax.add_patch(MPoly(corpo_pts, closed=True,
                       facecolor=COR_CORPO, edgecolor=COR_BORDA, lw=LW, zorder=2))
    ax.add_patch(MPoly(corpo_pts, closed=True, facecolor="none",
                       edgecolor="#5a8a5a", hatch="xx", lw=0.3, alpha=0.30, zorder=3))

    # ── Emboçador + bifurcação Y ─────────────────────────────
    def emb(y_out0, y_in0, y_out1, y_in1):
        pts = np.array([
            [x_garg, y_out0], [x_emb_fim, y_out1],
            [x_emb_fim, y_in1], [x_garg, y_in0],
        ])
        ax.add_patch(MPoly(pts, closed=True,
                           facecolor=COR_CORPO, edgecolor="none", zorder=2))
        ax.add_patch(MPoly(pts, closed=True, facecolor="none",
                           edgecolor="#5a8a5a", hatch="xx", lw=0.3, alpha=0.30, zorder=3))

    emb( meia_garg,  0.0,  sep+ens_h,  sep)
    emb(-meia_garg,  0.0, -(sep+ens_h), -sep)

    ax.plot([x_garg, x_emb_fim], [ meia_garg,  sep+ens_h],  color=COR_BORDA, lw=LW, zorder=4)
    ax.plot([x_garg, x_emb_fim], [-meia_garg, -(sep+ens_h)], color=COR_BORDA, lw=LW, zorder=4)
    ax.plot([x_garg, x_emb_fim], [0,  sep], color="#444", lw=1.0, ls="--", zorder=4)
    ax.plot([x_garg, x_emb_fim], [0, -sep], color="#444", lw=1.0, ls="--", zorder=4)
    ax.plot([x_garg, x_garg], [-meia_garg, meia_garg], color=COR_BORDA, lw=LW, zorder=4)

    # ── Ensacadores ──────────────────────────────────────────
    for y_bot, y_top in [(sep, sep+ens_h), (-(sep+ens_h), -sep)]:
        pts = np.array([
            [x_emb_fim,  y_bot], [x_emb_fim,  y_top],
            [x_saco_fim, y_top], [x_saco_fim, y_bot],
        ])
        ax.add_patch(MPoly(pts, closed=True,
                           facecolor=COR_ENS, edgecolor=COR_BORDA, lw=LW, zorder=2))

    ax.plot([x_saco_fim, x_saco_fim], [ sep,        sep+ens_h ], color=COR_BORDA, lw=3.5, zorder=4)
    ax.plot([x_saco_fim, x_saco_fim], [-(sep+ens_h), -sep     ], color=COR_BORDA, lw=3.5, zorder=4)

    # ── Boca ─────────────────────────────────────────────────
    ax.plot([x0, x0], [-meia_boca, meia_boca], color=COR_BORDA, lw=3.5, zorder=4)

    # ── Seta de arrasto ──────────────────────────────────────
    ax.annotate("", xy=(-2.5, 0), xytext=(-0.3, 0),
                arrowprops=dict(arrowstyle="-|>", color="#444", lw=1.5, mutation_scale=18))
    ax.text(-3.0, 0, "Trawling\ndirection", ha="right", va="center",
            fontsize=8, color="#444", style="italic")

    # ── Rótulos ──────────────────────────────────────────────
    def lbl(x, y, t, sz=9, bold=False, cor="#1a1a1a"):
        ax.text(x, y, t, ha="center", va="center", fontsize=sz,
                fontweight="bold" if bold else "normal", color=cor, zorder=5)

    lbl((x0+x_garg)/2, 0, "BODY", sz=10, bold=True, cor="#1a5c1a")
    lbl((x_garg+x_emb_fim)/2,  (sep+ens_h)*0.52, "EXTENSION", sz=8.5, cor="#333")
    lbl((x_garg+x_emb_fim)/2, -(sep+ens_h)*0.52, "EXTENSION", sz=8.5, cor="#333")
    lbl((x_emb_fim+x_saco_fim)/2,  sep+ens_h/2, "COD-END", sz=9, bold=True, cor="#0a4070")
    lbl((x_emb_fim+x_saco_fim)/2, -(sep+ens_h/2), "COD-END", sz=9, bold=True, cor="#0a4070")
    ax.text(x0+0.35, 0, "MOUTH", ha="left", va="center",
            fontsize=8, rotation=90, color="#333", zorder=5)
    ax.text(x_garg+0.2, meia_garg+0.25, "Throat",
            ha="left", va="bottom", fontsize=8, color="#555", zorder=5)

    # ── Cotas ────────────────────────────────────────────────
    def dh(x1, x2, y, t, cor="k", fs=8.5):
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="<->", color=cor, lw=1.1, mutation_scale=10))
        ax.text((x1+x2)/2, y+0.22, t, ha="center", va="bottom", fontsize=fs, color=cor)

    def dv(x, y1, y2, t, cor="k", fs=8.5):
        ax.annotate("", xy=(x, y2), xytext=(x, y1),
                    arrowprops=dict(arrowstyle="<->", color=cor, lw=1.1, mutation_scale=10))
        ax.text(x+0.15, (y1+y2)/2, t, ha="left", va="center", fontsize=fs, color=cor)

    def g(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color="#aaa", lw=0.7, ls=":", zorder=1)

    g(x0, -meia_boca, x0-2.1, -meia_boca); g(x0, meia_boca, x0-2.1, meia_boca)
    dv(x0-2.0, -meia_boca, meia_boca, f"{ABERTURA_BOCA} m", fs=9.5)

    y1 = -meia_boca - 1.3
    g(x0, -meia_boca, x0, y1); g(x_garg, -meia_garg, x_garg, y1)
    dh(x0, x_garg, y1, f"Body  {DIST_BOCA_FUNDO} m")

    y2 = -(sep+ens_h+1.1)
    g(x_garg, -(sep+ens_h), x_garg, y2); g(x_emb_fim, -(sep+ens_h), x_emb_fim, y2)
    dh(x_garg, x_emb_fim, y2, f"Extension  {dist_emb} m")

    y3 = sep+ens_h+1.0
    g(x_emb_fim, sep+ens_h, x_emb_fim, y3); g(x_saco_fim, sep+ens_h, x_saco_fim, y3)
    dh(x_emb_fim, x_saco_fim, y3, f"Cod-end  {COMP_SACO} m")

    y_tot = -meia_boca - 2.4
    g(x0, -meia_boca, x0, y_tot); g(x_emb_fim, -(sep+ens_h), x_emb_fim, y_tot)
    dh(x0, x_emb_fim, y_tot,
       f"Total length (body + extension)  {COMPRIMENTO_TOTAL} m", cor="#333", fs=9.5)

    x_ev = x_saco_fim + 0.7
    g(x_saco_fim, sep, x_ev, sep); g(x_saco_fim, sep+ens_h, x_ev, sep+ens_h)
    dv(x_ev, sep, sep+ens_h, f"{ALTURA_ENSACADOR} m")
    ax.text(x_ev+0.15, sep+ens_h+0.5, f"(Y opening: {ABERTURA_Y} m)",
            ha="left", va="center", fontsize=7.5, color="#777", zorder=5)

    x_sv = (x_emb_fim+x_saco_fim)/2
    g(x_emb_fim, sep, x_sv, sep); g(x_emb_fim, -sep, x_sv, -sep)
    dv(x_sv, -sep, sep, f"{DIST_ENSACADORES} m\n(gap)", cor="#555", fs=7.5)

    # ── Título ───────────────────────────────────────────────
    ax.set_title(
        f"Bottom Trawl Net — Technical Plan  (Top View)  [{label_rede}  |  Extension: {dist_emb} m]",
        fontsize=14, fontweight="bold", pad=20
    )
    specs = (f"Mesh: {MALHA_TIPO}  ·  {MALHA_TAMANHO} cm  |  Between knots: {MALHA_ENTRE_NOS} cm  |  "
             f"Y opening: {ABERTURA_Y} m  |  Cod-end gap: {DIST_ENSACADORES} m")
    ax.text(0.5, -0.01, specs, transform=ax.transAxes,
            ha="center", va="top", fontsize=8.5, color="#555")

    p1 = mpatches.Patch(facecolor=COR_CORPO, edgecolor=COR_BORDA, label="Body / Extension")
    p2 = mpatches.Patch(facecolor=COR_ENS,   edgecolor=COR_BORDA, label="Cod-end (bag)")
    p3 = mpatches.Patch(facecolor="none", edgecolor="#444", linestyle="--", label="Y divider")
    ax.legend(handles=[p1, p2, p3], loc="lower right",
              fontsize=9, framealpha=0.95, edgecolor="#ccc")

    plt.tight_layout(pad=1.5)
    plt.savefig(f"{saida}.pdf", dpi=300, bbox_inches="tight")
    plt.savefig(f"{saida}.png", dpi=300, bbox_inches="tight")
    print(f"✅ Salvo: {saida}.pdf e {saida}.png")
    plt.close()


# ── Gera as 2 redes ──────────────────────────────────────────
for rede in REDES:
    gerar_plano(rede["dist_emb"], rede["label"], rede["saida"])

print("✅ Concluído: plano_rede_1 e plano_rede_2 gerados.")
