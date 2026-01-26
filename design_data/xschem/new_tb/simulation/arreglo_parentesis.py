import re
from pathlib import Path

# =========================
# 1) INPUT / OUTPUT (EDITA SOLO ESTO SI CAMBIA EL PATH)
# =========================
INPUT_SPICE = Path(r"C:\Users\Fernanda\uniccass-icdesign-tools\shared_xserver\verification\simulations\ihp-sg13g2\MissMatch\design_data\xschem\new_tb\simulation\MissMatch_chip_tb_NEW.spice")
OUTPUT_SPICE = INPUT_SPICE.with_name(INPUT_SPICE.stem + "_FLAT.spice")

# =========================
# 2) VALORES QUE QUIERES "PEGAR" (flatten)
# =========================
OVERRIDES = {
    "temp": "27",
    "VDD": "1.2",
    "m1_w": "10u",
    "m2_w": "10u",
    "m1_l": "0.13u",
    "m2_l": "0.13u",
    "dut_w": "1.0u",
    "dut_l": "0.13u",
    # Si aparece {w} o {l} en algún lado y NO sabes de dónde viene,
    # NO lo pongas aquí a ciegas (puede romper el netlist).
    # "w": "0.15u",
    # "l": "0.13u",
}

# =========================
# Helpers
# =========================
PARAM_LINE = re.compile(r"^\s*\.param\s+(.*)$", re.IGNORECASE)

def parse_params(lines):
    """Lee .param existentes del netlist y los guarda en dict."""
    params = {}
    for ln in lines:
        m = PARAM_LINE.match(ln)
        if not m:
            continue
        rhs = m.group(1).strip()
        # Soporta: .param a=1 b=2 c=3
        for token in rhs.split():
            if "=" in token:
                k, v = token.split("=", 1)
                params[k.strip()] = v.strip()
    return params

def fix_missing_closing_brace(text):
    """
    Arregla casos como:
      l={m1_l ng=1 m=1
    -> l={m1_l} ng=1 m=1
    para cualquier parámetro del estilo xxx={NAME ...
    """
    # inserta "}" si después de "{algo" viene un espacio y luego una palabra (ng=, m=, etc)
    # y NO hay '}' antes del espacio.
    return re.sub(r"(\=\{[A-Za-z_][A-Za-z0-9_]*)(\s+[A-Za-z_][A-Za-z0-9_]*\=)", r"\1}\2", text)

def substitute_braced_params(text, params):
    """
    Reemplaza {m1_w} -> 10u, etc.
    Solo reemplaza cuando el contenido dentro de {} es un IDENTIFICADOR simple.
    """
    unresolved = set()

    def repl(m):
        name = m.group(1)
        if name in params:
            return params[name]
        unresolved.add(name)
        return m.group(0)  # deja {name} tal cual si no se conoce

    out = re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, text)
    return out, unresolved

def main():
    if not INPUT_SPICE.exists():
        raise FileNotFoundError(f"No existe el archivo: {INPUT_SPICE}")

    text = INPUT_SPICE.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # 1) lee params actuales
    params = parse_params(lines)

    # 2) aplica overrides (estos mandan)
    params.update(OVERRIDES)

    # 3) arregla llaves faltantes
    text2 = fix_missing_closing_brace(text)

    # 4) reemplaza {param} por valor
    text3, unresolved = substitute_braced_params(text2, params)

    # 5) (opcional) agrega un bloque .param arriba para dejar explícitos los valores
    header = []
    header.append("* ===== FLATTENED PARAMS (auto-generated) =====")
    header.append(f".param temp={params.get('temp','27')}")
    header.append(f".param VDD={params.get('VDD','1.2')}")
    header.append(f".param m1_w={params.get('m1_w','10u')} m2_w={params.get('m2_w','10u')}")
    header.append(f".param m1_l={params.get('m1_l','0.13u')} m2_l={params.get('m2_l','0.13u')}")
    header.append(f".param dut_w={params.get('dut_w','1.0u')} dut_l={params.get('dut_l','0.13u')}")
    header.append("* =============================================")
    header_text = "\n".join(header) + "\n\n"

    final_text = header_text + text3
    OUTPUT_SPICE.write_text(final_text, encoding="utf-8")

    print("OK ✅ Generado:", OUTPUT_SPICE)

    # Reporte de cosas que NO pudo reemplazar
    if unresolved:
        # Filtra tokens muy comunes que a veces aparecen pero no necesitas tocar.
        print("\n⚠️ OJO: quedaron llaves sin reemplazar (no estaban definidas como .param):")
        for u in sorted(unresolved):
            print("  -", u)
        print("\nSi alguno de esos te aparece como 'Undefined parameter' en ngspice, dímelo y lo resolvemos.")

if __name__ == "__main__":
    main()
