import csv
import os

_BASE = os.path.dirname(__file__)
_PATRONS_CSV = os.path.join(_BASE, "patrons.csv")

def _cargar_patrons():
    """Llegeix patrons.csv i retorna un diccionari {nom_patró: [llista de comandes]} carregat a memoria."""
    patrons = {}
    if not os.path.exists(_PATRONS_CSV):
        return patrons
    with open(_PATRONS_CSV, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            patrons[row["nombre"]] = [c.strip() for c in row["comandos"].split(",")]
    return patrons

PATRONS = _cargar_patrons()

def guardar_patron(nombre, comandos):
    """Afegeix un nou patró a patrons.csv i actualitza el diccionari PATRONS en memoria."""
    exists = os.path.exists(_PATRONS_CSV)
    with open(_PATRONS_CSV, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["nombre", "comandos"])
        w.writerow([nombre, ",".join(comandos)])
    PATRONS[nombre] = comandos

def caçar_patro(historial, seq_atac, i_hist=0, i_seq=0):
    """Cerca recursivament si seq_atac és una subsequencia del historial de comandes. Complexitat O(n·m)."""
    if i_seq == len(seq_atac): return True
    if i_hist == len(historial): return False

    if seq_atac[i_seq] in historial[i_hist]:
        return caçar_patro(historial, seq_atac, i_hist + 1, i_seq + 1)

    return caçar_patro(historial, seq_atac, i_hist + 1, i_seq)

def escanear_logs(logs):
    """Retorna els noms dels patrons de patrons.csv que han estat detectats en el historial de la sessió."""
    return [nom for nom, seq in PATRONS.items() if caçar_patro(logs, seq)]
