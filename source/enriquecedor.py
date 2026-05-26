import csv
import os

_BASE = os.path.dirname(__file__)
_BBDD_CSV       = os.path.join(_BASE, "bbdd_comandos.csv")
_TRANSICIONS_CSV = os.path.join(_BASE, "transicions.csv")

def _leer_bbdd():
    """Llegeix bbdd_comandos.csv i retorna un diccionari indexat per nom de comanda amb totes les seves dades."""
    if not os.path.exists(_BBDD_CSV):
        return {}
    with open(_BBDD_CSV, encoding="utf-8", newline="") as f:
        return {row["comando"]: row for row in csv.DictReader(f)}

def _transicion_existe(desde, clave, hasta):
    """Comprova si una transicio ja existeix a transicions.csv per evitar afegir duplicats."""
    if not os.path.exists(_TRANSICIONS_CSV):
        return False
    with open(_TRANSICIONS_CSV, encoding="utf-8", newline="") as f:
        return any(
            r["desde"] == str(desde) and r["clave"] == clave and r["hasta"] == str(hasta)
            for r in csv.DictReader(f)
        )

def enriquecer(comando):
    """Si la comanda existeix a bbdd_comandos.csv, afegeix la transicio a transicions.csv i el patró a patrons.csv via guardar_patron."""
    bbdd = _leer_bbdd()
    if comando not in bbdd:
        return False

    entrada = bbdd[comando]
    desde  = entrada["fase_origen"]
    hasta  = entrada["fase_destino"]
    patron = entrada["patron"]

    if not _transicion_existe(desde, comando, hasta):
        with open(_TRANSICIONS_CSV, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow([desde, comando, hasta])

    if patron:
        from patrons import PATRONS, guardar_patron
        if patron not in PATRONS:
            guardar_patron(patron, [comando])

    return True