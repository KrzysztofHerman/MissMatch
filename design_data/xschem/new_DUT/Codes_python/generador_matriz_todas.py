#!/usr/bin/env python3
#Generación de todas las matrices, sin dummies
# Genera, para cada (W,L) en SIZES:
#   nmos_matrix_W<val>_L<val>.sch  (matriz)
#   nmos_matrix_W<val>_L<val>.sym  (símbolo jerárquico B,G,S,D)

from pathlib import Path

# ============================================================
#              LISTA DE TAMAÑOS A GENERAR
# ============================================================

SIZES = [
    ("2.4u", "2.08u"), ("2.4u", "1.04u"), ("2.4u", "0.52u"), ("2.4u", "0.26u"), ("2.4u", "0.13u"),
    ("1.2u", "2.08u"), ("1.2u", "1.04u"), ("1.2u", "0.52u"), ("1.2u", "0.26u"), ("1.2u", "0.13u"),
    ("0.6u", "2.08u"), ("0.6u", "1.04u"), ("0.6u", "0.52u"), ("0.6u", "0.26u"), ("0.6u", "0.13u"),
    ("0.3u", "2.08u"), ("0.3u", "1.04u"), ("0.3u", "0.52u"), ("0.3u", "0.26u"), ("0.3u", "0.13u"),
    ("0.15u", "2.08u"), ("0.15u", "1.04u"), ("0.15u", "0.52u"), ("0.15u", "0.26u"), ("0.15u", "0.13u"),
]


# ============================================================
#                  AJUSTES PRINCIPALES
# ============================================================

ROWS = 18
COLS = 18

# Símbolo NMOS de IHP 
SYM_PATH = "/opt/pdks/ihp-sg13g2/libs.tech/xschem/sg13g2_pr/sg13_lv_nmos.sym"
MODEL = "sg13_lv_nmos"

# Offsets de pines medidos en xschem
OFF_D = (20, -30)
OFF_G = (-20, 0)
OFF_S = (20, 30)
OFF_B = (20, 0)

# Pitch matriz
PITCH_X = 460
PITCH_Y = 360

# Grilla
GRID = 10

# Origen de la matriz
ORIGIN_X = 1000
ORIGIN_Y = 1000

# Distancias a buses
D_BUS_DX   = 80
G_BUS_DY   = 0
S_BUS_DY   = 0

# --- Bus de G levantado para eliminar corto con B ---
G_BUS_OFFSET_Y = -120

# Stub de bulk
B_STUB_DX = 60

# ============================================================
#                  UTILIDADES BÁSICAS
# ============================================================

def snap(v):
    return int(round(v / GRID)) * GRID

def write_text(path, lines):
    Path(path).write_text("\n".join(lines))

def inst(sym, x, y, rot=0, mir=0, props=""):
    return f"C {{{sym}}} {snap(x)} {snap(y)} {rot} {mir} {{{props}}}"

def wire(x1, y1, x2, y2, lab=None):
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    if lab:
        return f"N {x1} {y1} {x2} {y2} {{lab={lab}}}"
    else:
        return f"N {x1} {y1} {x2} {y2} {{}}"

def label(x, y, text):
    props = f"name=lab_{text}_{x}_{y} lab={text} dir=inout"
    return inst("devices/lab_pin.sym", x, y, 0, 0, props)

def clean_val(val):
    """Convierte '1.15u' → '1p15u' para usar en nombres de archivo."""
    val = val.replace(".", "p")
    val = val.replace("[", "").replace("]", "")
    return val

# ============================================================
#           NOMBRES DE BUSES INTERNOS
# ============================================================

def DRAIN_NET(col):   return f"D[{col}]"
def GATE_NET(row):    return f"G[{row}]"
def SOURCE_NET(row):  return f"S[{row}]"
def BULK_NET():       return "B"

# ============================================================
#                MATRIZ CON BUSES (.sch)
# ============================================================

def gen_array(W, L, array_file):
    lines = [
        "v {xschem version=3.0.0 file_version=1.2}",
        "G {}", "K {type=schematic}", "V {}", "S {}",
    ]

    # ========================================================
    #   EXPORTS + IOPIN: D[0:17], G[0:17], S[0:17], B
    # ========================================================

    x_lab = ORIGIN_X - 500
    x_pin = x_lab + 180
    y_D = ORIGIN_Y - 460
    y_G = ORIGIN_Y - 420
    y_S = ORIGIN_Y - 380
    y_B = ORIGIN_Y - 340

    def add_bus_export(xl, xp, y, netname, pinname):
        
        lines.append(wire(xl, y, xp, y, netname))
        # etiqueta de bus 
        lines.append(
            inst("devices/lab_pin.sym", xl, y, 0, 0,
                 f"name=lab_{pinname}_bus lab={netname} dir=inout")
        )
        # iopin 
        lines.append(
            inst("devices/iopin.sym", xp, y, 0, 0,
                 f"name={pinname}_pin lab={pinname} dir=inout")
        )

    # Construimos dinámicamente los nombres según ROWS y COLS
    D_BUS_NAME = f"D[0:{COLS-1}]"
    G_BUS_NAME = f"G[0:{ROWS-1}]"
    S_BUS_NAME = f"S[0:{ROWS-1}]"
    B_BUS_NAME = "B"

    add_bus_export(x_lab, x_pin, y_D, D_BUS_NAME, "D")
    add_bus_export(x_lab, x_pin, y_G, G_BUS_NAME, "G")
    add_bus_export(x_lab, x_pin, y_S, S_BUS_NAME, "S")
    add_bus_export(x_lab, x_pin, y_B, B_BUS_NAME, "B")


    # ========================================================
    #   BUSES INTERNOS
    # ========================================================

    # Coordenadas de buses de D
    drain_bus_x = []
    for c in range(COLS):
        x0 = ORIGIN_X + c * PITCH_X
        drain_bus_x.append(x0 + OFF_D[0] + D_BUS_DX)

    # Coordenadas de buses de G y S
    gate_bus_y = []
    source_bus_y = []
    for r in range(ROWS):
        y0 = ORIGIN_Y + r * PITCH_Y
        gate_bus_y.append(y0 + OFF_G[1] + G_BUS_DY + G_BUS_OFFSET_Y)  # BUS G LEVANTADO
        source_bus_y.append(y0 + OFF_S[1] + S_BUS_DY)

    # Límites
    y_min = ORIGIN_Y - 2 * PITCH_Y
    y_max = ORIGIN_Y + (ROWS - 1) * PITCH_Y + 2 * PITCH_Y
    x_min = ORIGIN_X - 2 * PITCH_X
    x_max_gs = ORIGIN_X + (COLS - 1) * PITCH_X + 2 * PITCH_X

    # ---- buses de D ----
    for c in range(COLS):
        xbus = drain_bus_x[c]
        netD = DRAIN_NET(c)
        lines.append(wire(xbus, y_min, xbus, y_max, netD))
        lines.append(label(xbus, y_min + 20, netD))

    # ---- Buses G y S ----
    for r in range(ROWS):
        yg = gate_bus_y[r]
        ys = source_bus_y[r]
        netG = GATE_NET(r)
        netS = SOURCE_NET(r)

        lines.append(wire(x_min, yg, x_max_gs, yg, netG))
        lines.append(label(x_min + 20, yg, netG))

        lines.append(wire(x_min, ys, x_max_gs, ys, netS))
        lines.append(label(x_min + 20, ys, netS))

    # ---- Transistores ----
    for r in range(ROWS):
        for c in range(COLS):
            x0 = ORIGIN_X + c * PITCH_X
            y0 = ORIGIN_Y + r * PITCH_Y

            name = f"M_{r}_{c}"
            props = f"name={name} w={W} l={L} ng=1 m=1 model={MODEL}"
            lines.append(inst(SYM_PATH, x0, y0, 0, 0, props))

            # Pines
            xd, yd = x0 + OFF_D[0], y0 + OFF_D[1]
            xg, yg = x0 + OFF_G[0], y0 + OFF_G[1]
            xs, ys = x0 + OFF_S[0], y0 + OFF_S[1]
            xb, yb = x0 + OFF_B[0], y0 + OFF_B[1]

            netD = DRAIN_NET(c)
            netG = GATE_NET(r)
            netS = SOURCE_NET(r)
            netB = BULK_NET()

            xD_bus = drain_bus_x[c]
            yG_bus = gate_bus_y[r]
            yS_bus = source_bus_y[r]

            # D: pin → bus D
            lines.append(wire(xd, yd, xD_bus, yd, netD))

            # G: vertical + horizontal hasta bus
            lines.append(wire(xg, yg, xg, yG_bus, netG))
            lines.append(wire(xg, yG_bus, x_min, yG_bus, netG))

            # S: pin → bus S
            lines.append(wire(xs, ys, x_min, yS_bus, netS))

            # B: stub local + label 
            x_stub = xb + B_STUB_DX
            lines.append(wire(xb, yb, x_stub, yb, netB))
            lines.append(
                inst(
                    "devices/lab_pin.sym",
                    x_stub,
                    yb,
                    0,
                    0,
                    f"name=labB_{r}_{c} lab=B dir=inout"
                )
            )

    write_text(array_file, lines)

# ============================================================
#                 SÍMBOLO JERÁRQUICO (.sym)
# ============================================================

def gen_symbol(array_file, symbol_file):
    lines = []
    lines.append("v {xschem version=3.4.6 file_version=1.2}")
    lines.append("K {type=subcircuit")
    lines.append('format="@name @pinlist @symname"')
    lines.append('template="name=x1"')
    lines.append("}")

    # Nombre del símbolo en el interior
    lines.append("T {@symname} -120 0 0 0 0.3 0.3 {}")
    lines.append("T {@name} 160 -175 0 0 0.2 0.2 {}")

    # CUADRADO del DUT (150 x 150)
    lines.append("P 4 5 150 -150 -150 -150 -150 150 150 150 150 -150 {}")

    # PIN D
    lines.append('B 5 -2.5 -170 2.5 -165 {name=D dir=inout}')
    lines.append("L 7 0 -150 0 -165 {}")
    lines.append("T {D} -10 -180 0 0 0.25 0.25 {}")

    # PIN B 
    lines.append('B 5 -40 -170 -35 -165 {name=B dir=inout}')
    lines.append("L 7 -40 -150 -40 -165 {}")
    lines.append("T {B} -50 -180 0 0 0.25 0.25 {}")

    # PIN G
    lines.append('B 5 -170 -80 -165 -75 {name=G dir=inout}')
    lines.append("L 7 -150 -77.5 -165 -77.5 {}")
    lines.append("T {G} -185 -82 0 0 0.25 0.25 {}")

    # PIN S 
    lines.append('B 5 -170 -20 -165 -15 {name=S dir=inout}')
    lines.append("L 7 -150 -17.5 -165 -17.5 {}")
    lines.append("T {S} -185 -22 0 0 0.25 0.25 {}")

    # Vínculo jerárquico
    lines.append(f".prop prop=schematic_name:{array_file}")

    write_text(symbol_file, lines)

# ============================================================
#                        MAIN
# ============================================================

def generate_for_size(W, L):
    clean_w = clean_val(W)
    clean_l = clean_val(L)
    base_name  = f"W{clean_w}_L{clean_l}"
    array_file = f"{base_name}.sch"
    symbol_file = f"{base_name}.sym"

    print(f"--> Generando {base_name}  (W={W}, L={L})")
    gen_array(W, L, array_file)
    gen_symbol(array_file, symbol_file)

if __name__ == "__main__":
    for W, L in SIZES:
        generate_for_size(W, L)
    print("Matrices creadas")
