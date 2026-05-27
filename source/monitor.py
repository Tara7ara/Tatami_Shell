import os
import csv
import time
import datetime
import glob

ARCHIVOS_DIR = os.path.join(os.path.dirname(__file__), "archivos")
_BASE = os.path.dirname(__file__)
"""La parte visual, se ha hecho con IA, pero el código de lectura de logs, detección de fases y generación de evidencias es completamente original."""

def find_latest_log():
    """Retorna el fitxer LOG*.log mes recent de la carpeta archivos/, o None si no n'hi ha cap."""
    logs = glob.glob(os.path.join(ARCHIVOS_DIR, "LOG*.log"))
    return max(logs, key=os.path.getmtime) if logs else None

def parse_log(path):
    """Parseja un fitxer de log generat per main.py i retorna una llista de tuples (timestamp, comanda)."""
    if not path or not os.path.exists(path):
        return []
    entries = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if "] - " in line:
                try:
                    ts, cmd = line.split("] - ", 1)
                    entries.append((ts.lstrip("["), cmd))
                except ValueError:
                    pass
    return entries

def read_file(fname):
    """Llegeix un fitxer de la carpeta archivos/ (p.ex. sudo_passwords.txt) i retorna les seves linies no buides."""
    path = os.path.join(ARCHIVOS_DIR, fname)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as f:
        return [l.strip() for l in f if l.strip()]

def count_dir(subdir):
    """Compta i llista els fitxers d'un subdirectori de archivos/ (downloads, editados, creados, eliminados, redireccionados)."""
    path = os.path.join(ARCHIVOS_DIR, subdir)
    if not os.path.exists(path):
        return 0, []
    items = os.listdir(path)
    return len(items), items

def _leer_transicions():
    """Llegeix transicions.csv en cada cicle i retorna un diccionari {clau: fase_destino} per a la deteccio dinamica de fases."""
    path = os.path.join(_BASE, "transicions.csv")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {row["clave"]: int(row["hasta"]) for row in csv.DictReader(f)}

def _leer_fases():
    """Llegeix fases.csv i retorna un diccionari {id: nombre} per mostrar el nom de la fase detectada."""
    path = os.path.join(_BASE, "fases.csv")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {int(row["id"]): row["nombre"] for row in csv.DictReader(f)}

_RIESGO_LABEL = {5: "CRITICO", 4: "ALTO", 3: "ALTO", 2: "MEDIO", 1: "BAJO"}

def detect_phase(cmds):
    """Determina la fase de major risc detectada llegint dinamicament transicions.csv i fases.csv en cada refresc."""
    transicions = _leer_transicions()
    fases       = _leer_fases()
    flat        = " ".join(c for _, c in cmds).lower()

    max_fase = max(
        (fase_id for clave, fase_id in transicions.items() if clave in flat),
        default=0,
    )

    if max_fase == 0:
        return "INICIAL (sin actividad)"

    nombre = fases.get(max_fase, "Desconocida").upper()
    label  = _RIESGO_LABEL.get(max_fase, "DESCONOCIDO")
    return f"{nombre} (riesgo {label})"

def render():
    """Refresca la pantalla del monitor cada 2 segons mostrant fase, credencials capturades, activitat de fitxers i comandes sospechoses."""
    log_path = find_latest_log()
    cmds     = parse_log(log_path)

    sudo_lines  = read_file("sudo_passwords.txt")
    mysql_lines = read_file("mysql_passwords.txt")

    n_dl, dl   = count_dir("downloads")
    n_ed, ed   = count_dir("editados")
    n_cr, cr   = count_dir("creados")
    n_rm, rm   = count_dir("eliminados")
    n_red, red = count_dir("redireccionados")

    danger_kw   = ["wget", "curl", "nc ", "base64", "sudo", "cat /etc", "cat credential", "id_rsa", ".bash_history"]
    danger_cmds = [(ts, c) for ts, c in cmds if any(k in c.lower() for k in danger_kw)]

    os.system("cls" if os.name == "nt" else "clear")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_name = os.path.basename(log_path) if log_path else "ninguno"

    print("  Tatami Honeypot")
    print(f"  {now}  |  log activo: {log_name}")

    if not cmds:
        print("\n  Esperando sesion activa...\n")
    else:
        print(f"\n  Fase detectada:  {detect_phase(cmds)}")
        print(f"  Comandos totales: {len(cmds)}\n")

    print("  -- Credenciales capturadas --")
    if sudo_lines:
        for line in sudo_lines[-4:]:
            print(f"  sudo  ->  {line}")
    if mysql_lines:
        for line in mysql_lines[-4:]:
            print(f"  mysql ->  {line}")
    if not sudo_lines and not mysql_lines:
        print("  ninguna todavia")

    print()
    print("  -- Actividad de archivos --")
    print(f"  descargados : {n_dl}   {' '.join(dl[:3])}")
    print(f"  editados    : {n_ed}   {' '.join(ed[:3])}")
    print(f"  creados     : {n_cr}   {' '.join(cr[:3])}")
    print(f"  eliminados  : {n_rm}   {' '.join(rm[:3])}")
    print(f"  redirigidos : {n_red}   {' '.join(red[:3])}")

    print()
    print("  -- Comandos sospechosos --")
    if danger_cmds:
        for ts, cmd in danger_cmds[-6:]:
            print(f"  {ts[11:19]}  {cmd[:44]}")
    else:
        print("  ninguno todavia")

    print()
    print("  -- Ultimos comandos --")
    for ts, cmd in cmds[-10:]:
        print(f"  {ts[11:19]}  {cmd[:44]}")

    print()

def generate_evidencia(log_path):
    """Genera el fitxer Evidencia_LOGn.txt a archivos/ amb el resum complet de la sessio en tancar el monitor amb Ctrl+C."""
    if not log_path:
        return

    log_name   = os.path.basename(log_path)
    log_number = ''.join(filter(str.isdigit, log_name))
    out_path   = os.path.join(ARCHIVOS_DIR, f"Evidencia_LOG{log_number}.txt")

    cmds        = parse_log(log_path)
    sudo_lines  = read_file("sudo_passwords.txt")
    mysql_lines = read_file("mysql_passwords.txt")
    phase       = detect_phase(cmds)

    n_dl, dl   = count_dir("downloads")
    n_ed, ed   = count_dir("editados")
    n_cr, cr   = count_dir("creados")
    n_rm, rm   = count_dir("eliminados")
    n_red, red = count_dir("redireccionados")

    danger_kw   = ["wget", "curl", "nc ", "base64", "sudo", "cat /etc", "cat credential", "id_rsa", ".bash_history"]
    danger_cmds = [(ts, c) for ts, c in cmds if any(k in c.lower() for k in danger_kw)]

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("Tatami Honeypot - Informe de evidencias")
    lines.append(f"Generado: {now}")
    lines.append(f"Log analizado: {log_name}")
    lines.append("")
    lines.append(f"Fase final detectada: {phase}")
    lines.append(f"Total de comandos ejecutados: {len(cmds)}")
    lines.append("")

    lines.append("-- Credenciales capturadas --")
    if sudo_lines:
        for l in sudo_lines:
            lines.append(f"  sudo  ->  {l}")
    if mysql_lines:
        for l in mysql_lines:
            lines.append(f"  mysql ->  {l}")
    if not sudo_lines and not mysql_lines:
        lines.append("  ninguna")
    lines.append("")

    lines.append("-- Actividad de archivos --")
    lines.append(f"  descargados : {n_dl}   {', '.join(dl)}")
    lines.append(f"  editados    : {n_ed}   {', '.join(ed)}")
    lines.append(f"  creados     : {n_cr}   {', '.join(cr)}")
    lines.append(f"  eliminados  : {n_rm}   {', '.join(rm)}")
    lines.append(f"  redirigidos : {n_red}   {', '.join(red)}")
    lines.append("")

    lines.append("-- Comandos sospechosos --")
    if danger_cmds:
        for ts, cmd in danger_cmds:
            lines.append(f"  {ts[11:19]}  {cmd}")
    else:
        lines.append("  ninguno")
    lines.append("")

    lines.append("-- Historial completo de comandos --")
    for ts, cmd in cmds:
        lines.append(f"  {ts}  {cmd}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nEvidencia guardada en: {out_path}")

def main():
    """Bucle principal del monitor. Crida render() cada 2 segons i en sortir genera l'evidencia via generate_evidencia."""
    log_path = None
    try:
        while True:
            log_path = find_latest_log()
            render()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nMonitor detenido.")
        generate_evidencia(log_path)

if __name__ == "__main__":
    main()