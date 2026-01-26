#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

# ============================================================
#        MATRIZ 5x5 DE BLOQUES NMOS (SÍMBOLOS JERÁRQUICOS)
# ============================================================

ROWS = 5
COLS = 5

# Filas = W, columnas = L
W_LIST = ["2p4u", "1p2u", "0p6u", "0p3u", "0p15u"]
L_LIST = ["2p08u", "1p04u", "0p52u", "0p26u", "0p13u"]

# Coordenadas de los CENTROS de los pines en el .sym
# (revisadas a partir de las B-lines del símbolo)
OFF_D = ( 50, -210)   # centro pin D
OFF_B = (-50, -210)   # centro pin B
OFF_G = (-210, -30)   # centro pin G
OFF_S = (-210,  30)   # centro pin S

GRID      = 20
PITCH_X   = 600
PITCH_Y   = 480
ORIGIN_X  = 1000
ORIGIN_Y  = 1000

B_STUB_DX = 80   # largo del stub de B hacia la IZQUIERDA

def snap(v):
    return int(round(v / GRID)) * GRID

def inst(sym, x, y, rot=0, mir=0, props=""):
    return f"C {{{sym}}} {snap(x)} {snap(y)} {rot} {mir} {{{props}}}"

def wire(x1, y1, x2, y2, lab=None):
    x1, y1, x2, y2 = map(snap, (x1, y1, x2, y2))
    if lab:
        return f"N {x1} {y1} {x2} {y2} {{lab={lab}}}"
    return f"N {x1} {y1} {x2} {y2} {{}}"

def label_pin(x, y, lab):
    x, y = snap(x), snap(y)
    props = f"name=lab_{lab}_{x}_{y} lab={lab} dir=inout"
    return inst("devices/lab_pin.sym", x, y, 0, 0, props)

# ============================================================
#            GENERACIÓN DEL ESQUEMÁTICO 5x5
# ============================================================

def gen_matrix_sch(filename="nmos_matrix_5x5.sch"):
    L = []
    # Header xschem
    L.append("v {xschem version=3.0.0 file_version=1.2}")
    L.append("G {}")
    L.append("K {type=schematic}")
    L.append("V {}")
    L.append("S {}")
    L.append("")

    # ---------------- PINES EXTERNOS ----------------
    x_lab = ORIGIN_X - 800
    x_pin = x_lab + 200
    yD = ORIGIN_Y - 600
    yG = ORIGIN_Y - 550
    yS = ORIGIN_Y - 500
    yB = ORIGIN_Y - 450

    def export_bus(y, net, pinname):
        L.append(wire(x_lab, y, x_pin, y, net))
        L.append(label_pin(x_lab, y, net))
        L.append(
            inst("devices/iopin.sym", x_pin, y, 0, 0,
                 f"name={pinname}_pin lab={pinname} dir=inout")
        )

    export_bus(yD, "D[0:4]", "D")
    export_bus(yG, "G[0:4]", "G")
    export_bus(yS, "S[0:4]", "S")
    export_bus(yB, "B",      "B")
    L.append("")

    # ---------------- INSTANCIAS ----------------
    D_points = [[None]*COLS for _ in range(ROWS)]
    G_points = [[None]*COLS for _ in range(ROWS)]
    S_points = [[None]*COLS for _ in range(ROWS)]
    B_points = [[None]*COLS for _ in range(ROWS)]

    for r in range(ROWS):
        for c in range(COLS):
            w = W_LIST[r]
            l = L_LIST[c]
            sym_name  = f"W{w}_L{l}.sym"
            inst_name = f"X{r}{c}"

            x0 = ORIGIN_X + c * PITCH_X
            y0 = ORIGIN_Y + r * PITCH_Y

            # instancia del símbolo
            L.append(inst(sym_name, x0, y0, 0, 0, f"name={inst_name}"))

            # centros de pines
            D_points[r][c] = (x0 + OFF_D[0], x0*0 + y0 + OFF_D[1])
            B_points[r][c] = (x0 + OFF_B[0], x0*0 + y0 + OFF_B[1])
            G_points[r][c] = (x0 + OFF_G[0], x0*0 + y0 + OFF_G[1])
            S_points[r][c] = (x0 + OFF_S[0], x0*0 + y0 + OFF_S[1])

    L.append("")

    # ---------------- G[row] y S[row] ----------------
    for r in range(ROWS):

        # ===== G[row]: bus un poco más ARRIBA =====
        xG_left,  yG_any = G_points[r][0]
        xG_right, _      = G_points[r][COLS-1]

        bus_y = yG_any - 40  # subir 40 units respecto al centro del pin G

        # bus horizontal
        L.append(wire(xG_left, bus_y, xG_right, bus_y, f"G[{r}]"))

        # palitos verticales desde cada pin G al bus
        for c in range(COLS):
            xg, yg = G_points[r][c]
            L.append(wire(xg, yg, xg, bus_y, f"G[{r}]"))

        # label G[r] a la izquierda
        xG_lab = xG_left - 80
        L.append(wire(xG_lab, bus_y, xG_left, bus_y, f"G[{r}]"))
        L.append(label_pin(xG_lab, bus_y, f"G[{r}]"))

        # ===== S[row]: recto por el centro del pin =====
        for c in range(COLS - 1):
            x1, y1 = S_points[r][c]
            x2, y2 = S_points[r][c+1]
            L.append(wire(x1, y1, x2, y2, f"S[{r}]"))

        xS0, yS0 = S_points[r][0]
        xS_lab   = xS0 - 80
        L.append(wire(xS_lab, yS0, xS0, yS0, f"S[{r}]"))
        L.append(label_pin(xS_lab, yS0, f"S[{r}]"))
        L.append("")

    # ---------------- D[col] ----------------
    for c in range(COLS):
        for r in range(ROWS - 1):
            x1, y1 = D_points[r][c]
            x2, y2 = D_points[r+1][c]
            L.append(wire(x1, y1, x2, y2, f"D[{c}]"))

        xT, yT = D_points[0][c]
        yD_lab = yT - 120
        L.append(wire(xT, yD_lab, xT, yT, f"D[{c}]"))
        L.append(label_pin(xT, yD_lab, f"D[{c}]"))
        L.append("")

    # ---------------- Bulk B (stub hacia la IZQUIERDA) ----------------
    for r in range(ROWS):
        for c in range(COLS):
            x, y = B_points[r][c]
            xs   = x - B_STUB_DX
            L.append(wire(x, y, xs, y, "B"))
            L.append(label_pin(xs, y, "B"))

    Path(filename).write_text("\n".join(L))
    print(f"✔ Archivo generado: {filename}")

# ============================================================
#                            MAIN
# ============================================================

if __name__ == "__main__":
    gen_matrix_sch("nmos_matrix_5x5.sch")
