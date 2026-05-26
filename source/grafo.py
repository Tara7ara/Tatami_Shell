import csv
import os

_BASE = os.path.dirname(__file__)

class NodoFase:
    """Representa un node del graf d'atac amb nom, nivell de risc i transicions cap a altres nodes."""

    def __init__(self, nom, risc):
        """Inicialitza el node amb nom, nivell de risc i diccionari de rutes buit."""
        self.nom = nom
        self.risc = risc
        self.rutes = {}

    def on_vaig(self, input_usuari):
        """Retorna el seguent NodoFase si la comanda de l'usuari conté alguna clau de transicio, o None si no n'hi ha cap."""
        input_net = input_usuari.lower()
        for clau, seguent_fase in self.rutes.items():
            if clau in input_net:
                return seguent_fase
        return None

def muntar_xarxa_paranoid():
    """Construeix el graf de fases llegint fases.csv (nodes) i transicions.csv (arestes). Retorna (node_arrel, dict_tots_nodes)."""
    fases = {}
    with open(os.path.join(_BASE, "fases.csv"), encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            fases[int(row["id"])] = NodoFase(row["nombre"], int(row["riesgo"]))

    with open(os.path.join(_BASE, "transicions.csv"), encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            origen  = int(row["desde"])
            destino = int(row["hasta"])
            fases[origen].rutes[row["clave"]] = fases[destino]

    return fases[0], fases

def trobar_millor_fase(input_usuari, fase_actual, totes_fases):
    """Busca en tots els nodes la transicio de major risc que coincideixi amb la comanda. Avanca si el risc es superior a l'actual, mai regredeix."""
    input_net = input_usuari.lower()
    millor = None
    for node in totes_fases.values():
        for clau, seguent in node.rutes.items():
            if clau in input_net and seguent.risc > fase_actual.risc:
                if millor is None or seguent.risc > millor.risc:
                    millor = seguent
    return millor