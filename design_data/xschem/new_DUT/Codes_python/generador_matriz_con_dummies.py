#!/usr/bin/env python3
# Genera, para cada (W,L) en SIZES:
#   W<val>_L<val>.sch  (matriz con dummies)
#   W<val>_L<val>.sym  (símbolo jerárquico B,G,S,D)
#
# Matriz "total" = CORE_ROWS x CORE_COLS + borde de dummies.
# Ejemplo: CORE=16x16, DUMMY_BORDER=1  -> matriz física 18x18
# Sólo la parte CORE se conecta a los buses D[i], G[i], S[i].
# Los dummies quedan "al aire" (salvo el bulk B).

from pathlib import Path

# ============================================================
#              LISTA DE TAMAÑOS A GENERAR
# ============================================================

SIZES = [
    ("2.4u",  "2.08u"), ("2.4u",  "1.04u"), ("2.4u",  "0.52u"),
    ("2.4u",  "0.26u"), ("2.4u",  "0.13u"),
    ("1.2u",  "2.08u"), ("1.2u",  "1.04u"), ("1.2u",  "0.52u"),
    ("1.2u",  "0.26u"), ("1.2u",  "0.13u"),
    ("0.6u",  "2.08u"), ("0.6u",  "1.04u"), ("0.6u",  "0.52u"),
    ("0.6u",  "0.26u"), ("0.6u",  "0.13u"),
    ("0.3u",  "2.08u"), ("0.3u",  "1.04u"), ("0.3u",  "0.52u"),
    ("0.3u",  "0.26u"), ("0.3u",  "0.13u"),
    ("0.15u", "2.08u"), ("0.15u", "1.04u"), ("0.15u", "0.52u"),
    ("0.15u", "0.26u"), ("0.15u", "0.13u"),
]

# ============================================================
#                  AJUSTES PRINCIPALES
# ============================================================

# Tamaño de la matriz "útil"
CORE_ROWS = 16
CORE_COLS = 16

# Nº de filas/columnas de dummies alrededor
DUMMY_ROWS = 1
DUMMY_COLS = 1

# Tamaño total físico
ROWS_TOT = CORE_ROWS + 2 * DUMMY_ROWS
COLS_TOT = CORE_COLS + 2 * DUMMY_COLS

# Índices donde empieza la zona útil dentro de la matriz total
CORE_ROW0 = DUMMY_ROWS
CORE_COL0 = DUMMY_COLS

# Símbolo NMOS de IHP
SYM_PATH = "/opt/pdks/ihp-sg13g2/libs.tech/xschem/sg13g2_pr/sg13_lv_nmos.sym"
MODEL = "sg13_lv_nmos"

# Offsets de pines medidos en xschem 
OFF_D = (20, -30)
OFF_G = (-20, 0)
OFF_S = (20, 30)
OFF_B = (20, 0)

# Pitch matriz (
PITCH_X = 460
PITCH_Y = 360

# Grilla
GRID = 10

# Origen de la matriz
ORIGIN_X = 1000
ORIGIN_Y = 1000

# Distancias extra
D_BUS_DX      = 80   
G_BUS_OFFSETY = -120 
S_BUS_OFFSETY = 120  
B_STUB_DX     = 60   

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

def DRAIN_NET(c_core):  return f"D[{c_core}]"
def GATE_NET(r_core):   return f"G[{r_core}]"
def SOURCE_NET(r_core): return f"S[{r_core}]"
def BULK_NET():         return "B"

def is_core(r_tot, c_tot):
    """¿Este índice (total) pertenece a la matriz útil (no dummy)?"""
    return (CORE_ROW0 <= r_tot < CORE_ROW0 + CORE_ROWS and
            CORE_COL0 <= c_tot < CORE_COL0 + CORE_COLS)

# ============================================================
#                MATRIZ CON DUMMIES (.sch)
# ============================================================

def gen_array(W, L, array_file):
    lines = [
        "v {xschem version=3.0.0 file_version=1.2}",
        "G {}", "K {type=schematic}", "V {}", "S {}",
    ]

    # ========================================================
    #   EXPORTS + IOPIN: D[0:n], G[0:n], S[0:n], B
    # ========================================================

    x_lab = ORIGIN_X - 700
    x_pin = x_lab + 180
    y_D  = ORIGIN_Y - 460
    y_G  = ORIGIN_Y - 420
    y_S  = ORIGIN_Y - 380
    y_B  = ORIGIN_Y - 340

    def add_bus_export(xl, xp, y, netname, pinname):
        lines.append(wire(xl, y, xp, y, netname))
        lines.append(
            inst("devices/lab_pin.sym", xl, y, 0, 0,
                 f"name=lab_{pinname}_bus lab={netname} dir=inout")
        )
        lines.append(
            inst("devices/iopin.sym", xp, y, 0, 0,
                 f"name={pinname}_pin lab={pinname} dir=inout")
        )

    D_BUS_NAME = f"D[0:{CORE_COLS-1}]"
    G_BUS_NAME = f"G[0:{CORE_ROWS-1}]"
    S_BUS_NAME = f"S[0:{CORE_ROWS-1}]"
    B_BUS_NAME = "B"

    add_bus_export(x_lab, x_pin, y_D, D_BUS_NAME, "D")
    add_bus_export(x_lab, x_pin, y_G, G_BUS_NAME, "G")
    add_bus_export(x_lab, x_pin, y_S, S_BUS_NAME, "S")
    add_bus_export(x_lab, x_pin, y_B, B_BUS_NAME, "B")

    # ========================================================
    #   BUSES INTERNOS (SOLO PARA LA ZONA ÚTIL)
    # ========================================================

    drain_bus_x = [0.0] * CORE_COLS
    gate_bus_y  = [0.0] * CORE_ROWS
    source_bus_y = [0.0] * CORE_ROWS

    # Coordenadas de buses de D 
    for j in range(CORE_COLS):
        c_tot = CORE_COL0 + j
        x0 = ORIGIN_X + c_tot * PITCH_X
        drain_bus_x[j] = x0 + OFF_D[0] + D_BUS_DX

    # Coordenadas de buses de G y S 
    for i in range(CORE_ROWS):
        r_tot = CORE_ROW0 + i
        y0 = ORIGIN_Y + r_tot * PITCH_Y
        gate_bus_y[i]   = y0 + OFF_G[1] + G_BUS_OFFSETY
        source_bus_y[i] = y0 + OFF_S[1] + S_BUS_OFFSETY 

    # Límites horizontales para buses G y S
    x_min = ORIGIN_X - 2 * PITCH_X
    x_max_g = ORIGIN_X + (COLS_TOT - 1) * PITCH_X + 2 * PITCH_X

    # ---- Buses G ----
    for i in range(CORE_ROWS):
        yg = gate_bus_y[i]
        netG = GATE_NET(i)
        lines.append(wire(x_min, yg, x_max_g, yg, netG))
        lines.append(label(x_min + 20, yg, netG))

    # ---- Buses S  ----
    for i in range(CORE_ROWS):
        ys = source_bus_y[i]
        netS = SOURCE_NET(i)
        lines.append(wire(x_min, ys, x_max_g, ys, netS))
        lines.append(label(x_min + 20, ys, netS))

    # ---- Buses de D ----
    top_r_tot    = CORE_ROW0
    bottom_r_tot = CORE_ROW0 + CORE_ROWS - 1

    top_y0    = ORIGIN_Y + top_r_tot * PITCH_Y
    bottom_y0 = ORIGIN_Y + bottom_r_tot * PITCH_Y

    yD_top_pin    = top_y0    + OFF_D[1]
    yD_bottom_pin = bottom_y0 + OFF_D[1]

    d_y_min = yD_top_pin - PITCH_Y     
    d_y_max = yD_bottom_pin               
    for j in range(CORE_COLS):
        xbus = drain_bus_x[j]
        netD = DRAIN_NET(j)
        lines.append(wire(xbus, d_y_min, xbus, d_y_max, netD))
        lines.append(label(xbus, d_y_min + 20, netD))

    # ========================================================
    #   TRANSISTORES (ÚTILES + DUMMIES)
    # ========================================================

    for r_tot in range(ROWS_TOT):
        for c_tot in range(COLS_TOT):
            x0 = ORIGIN_X + c_tot * PITCH_X
            y0 = ORIGIN_Y + r_tot * PITCH_Y

            name  = f"M_{r_tot}_{c_tot}"
            props = f"name={name} w={W} l={L} ng=1 m=1 model={MODEL}"
            lines.append(inst(SYM_PATH, x0, y0, 0, 0, props))

            # Pines físicos
            xd, yd = x0 + OFF_D[0], y0 + OFF_D[1]
            xg, yg = x0 + OFF_G[0], y0 + OFF_G[1]
            xs, ys = x0 + OFF_S[0], y0 + OFF_S[1]
            xb, yb = x0 + OFF_B[0], y0 + OFF_B[1]

            # Bulk
            x_stub = xb + B_STUB_DX
            lines.append(wire(xb, yb, x_stub, yb, BULK_NET()))
            lines.append(
                inst("devices/lab_pin.sym", x_stub, yb, 0, 0,
                     f"name=labB_{r_tot}_{c_tot} lab=B dir=inout")
            )

            # Si es dummy, no conectamos D/G/S a los buses
            if not is_core(r_tot, c_tot):
                continue

            # Índices dentro de la parte útil
            i = r_tot - CORE_ROW0  # fila útil
            j = c_tot - CORE_COL0  # columna útil

            netD = DRAIN_NET(j)
            netG = GATE_NET(i)
            netS = SOURCE_NET(i)

            xD_bus = drain_bus_x[j]
            yG_bus = gate_bus_y[i]
            yS_bus = source_bus_y[i]

            # D: pin → bus D 
            lines.append(wire(xd, yd, xD_bus, yd, netD))

            # G
            lines.append(wire(xg, yg, xg, yG_bus, netG))
            lines.append(wire(xg, yG_bus, x_min, yG_bus, netG))

            # S
            lines.append(wire(xs, ys, xs, yS_bus, netS))
            lines.append(wire(xs, yS_bus, x_min, yS_bus, netS))

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

    # Nombre del bloque (W0p15u_L0p26u) centrado
    lines.append("T {@symname} 0 0 0 0 0.35 0.35 {}")
    # Nombre de instancia pequeño arriba-derecha (x1, x2, …)
    lines.append("T {@name} 180 -180 0 0 0.2 0.2 {}")

    # Cuadrado del DUT (todo múltiplos de 20)
    lines.append("P 4 5 160 -160 -160 -160 -160 160 160 160 160 -160 {}")

    # ============================
    # PIN B (ARRIBA IZQUIERDA)
    # ============================
    lines.append('B 5 -60 -220 -40 -200 {name=B dir=inout}')
    lines.append("L 7 -50 -160 -50 -200 {}")
    lines.append("T {B} -60 -230 0 0 0.25 0.25 {}")

    # ============================
    # PIN D (ARRIBA DERECHA)
    # ============================
    lines.append('B 5 40 -220 60 -200 {name=D dir=inout}')
    lines.append("L 7 50 -160 50 -200 {}")
    lines.append("T {D} 40 -230 0 0 0.25 0.25 {}")

    # ============================
    # PIN G (LADO IZQUIERDO, ARRIBA)
    # ============================
    lines.append('B 5 -220 -40 -200 -20 {name=G dir=inout}')
    lines.append("L 7 -160 -30 -200 -30 {}")
    lines.append("T {G} -240 -40 0 0 0.25 0.25 {}")

    # ============================
    # PIN S (LADO IZQUIERDO, ABAJO)
    # ============================
    lines.append('B 5 -220 20 -200 40 {name=S dir=inout}')
    lines.append("L 7 -160 30 -200 30 {}")
    lines.append("T {S} -240 20 0 0 0.25 0.25 {}")

    # Enlace al esquemático interno
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
    print("Matrices generadas")
