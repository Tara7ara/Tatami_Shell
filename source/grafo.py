class NodoFase:
    def __init__(self, nom, risc):
        self.nom = nom
        self.risc = risc
        self.rutes = {}

    def on_vaig(self, input_usuari):
        input_net = input_usuari.lower()
        for clau, seguent_fase in self.rutes.items():
            if clau in input_net:
                return seguent_fase
        return None

def muntar_xarxa_paranoid():
    fase0 = NodoFase("Inici", 0)
    fase1 = NodoFase("Reconeixament", 1)
    fase2 = NodoFase("Enumeració", 2)
    fase3 = NodoFase("Escalada", 3)
    fase4 = NodoFase("Lectura de dades", 4)
    fase5 = NodoFase("Exfiltració", 5)

    fase0.rutes["whoami"] = fase1
    fase0.rutes["id"] = fase1
    fase0.rutes["uname"] = fase1
    fase0.rutes["hostname"] = fase1

    fase1.rutes["ls"] = fase2
    fase1.rutes["ps"] = fase2
    fase1.rutes["find"] = fase2
    fase1.rutes["netstat"] = fase2
    fase1.rutes["ss"] = fase2
    fase1.rutes["env"] = fase2
    fase1.rutes["history"] = fase2
    fase1.rutes["docker"] = fase2
    fase1.rutes["systemctl"] = fase2

    fase2.rutes["sudo"] = fase3
    fase2.rutes["chmod"] = fase3
    fase2.rutes["bash"] = fase3
    fase2.rutes["python3"] = fase3

    fase3.rutes["cat"] = fase4
    fase3.rutes["grep"] = fase4
    fase3.rutes["vi"] = fase4
    fase3.rutes["base64"] = fase4
    fase3.rutes["mysql"] = fase4

    fase4.rutes["wget"] = fase5
    fase4.rutes["curl"] = fase5
    fase4.rutes["nc"] = fase5
    fase4.rutes["ssh"] = fase5

    return fase0