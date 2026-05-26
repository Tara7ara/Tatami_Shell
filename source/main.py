import os
import re
import random
import datetime
import posixpath
"""Import de todos los comandos falsos, maquinas de estados, varriables y funciones aux."""
from comandos import (
    ComandoWhoami, ComandoNoEncontrado, ComandoPwd, ComandoLs, ComandoDir,
    ComandoClear, ComandoHistory, ComandoCat, ComandoVi,
    ComandoGrep, ComandoFind, ComandoMkdir, ComandoRm, ComandoIp, ComandoSsh,
    ComandoWget, ComandoCurl, ComandoSudo, ComandoChmod, ComandoBash,
    ComandoPython3, ComandoApt, ComandoAptGet, ComandoEcho, ComandoTouch,
    ComandoCowsay, ComandoSl,
    ComandoId, ComandoUname, ComandoHostname,
    ComandoPs, ComandoNetstat, ComandoSs, ComandoEnv,
    ComandoDocker, ComandoSystemctl, ComandoService,
    ComandoMysql, ComandoNc, ComandoBase64, ComandoCp, ComandoMv,
    ComandoTail, ComandoHead, ComandoLast, ComandoWho, ComandoW,
    ComandoDf, ComandoFree, ComandoUptime, ComandoCrontab, ComandoAlias,
    ARCHIVOS_DIR, VIRTUAL_DIRS, VIRTUAL_FS, ENV_VARS, _add_entry,
)
from grafo import muntar_xarxa_paranoid, trobar_millor_fase
from patrons import escanear_logs

ALIASES = {
    "ll": "ls -alF",
    "la": "ls -A",
    "l":  "ls -CF",
}

def _make_banner():
    """Genera el banner d'inici d'Ubuntu 22.04 amb data, carrega i darrer login aleatoris per simular un servidor real."""
    """El tema de la data i la carga s'ha fet amb IA"""
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = datetime.timedelta(hours=random.randint(2, 8), minutes=random.randint(0, 59))
    last_login = now - delta
    mem  = random.randint(14, 41)
    load = round(random.uniform(0.01, 0.35), 2)
    return (
        "Ubuntu 22.04.3 LTS ubuntu-server tty1\n\n"
        "ubuntu-server login: ubuntu\n"
        "Password:\n"
        "Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-88-generic x86_64)\n\n"
        " * Documentation:  https://help.ubuntu.com\n"
        " * Management:     https://landscape.canonical.com\n"
        " * Support:        https://ubuntu.com/advantage\n\n"
        f"  System information as of {now.strftime('%a %b %d %H:%M:%S UTC %Y')}\n\n"
        f"  System load:  {load:<19}Processes:             127\n"
        f"  Usage of /:   34.2% of 19.52GB   Users logged in:       1\n"
        f"  Memory usage: {mem}%                IPv4 address for eth0: 192.168.1.45\n"
        f"  Swap usage:   0%\n\n"
        "0 updates can be applied immediately.\n\n"
        f"Last login: {last_login.strftime('%a %b %d %H:%M:%S %Y')} from 192.168.1.10\n"
    )


class TatamiShell:
    """Shell principal del honeypot. Gestiona el bucle d'entrada, els logs i la maquina d'estats carregada des de grafo.py. Els comandos son instanciats des de comandos.py."""

    def __init__(self):
        """Inicialitza la shell: carrega el graf de grafo.py, crea el fitxer de log a archivos i registra tots els binaris disponibles."""
        self.fase_actual, self.totes_fases = muntar_xarxa_paranoid()
        self.logs  = []
        self.cwd   = "/home/ubuntu"
        os.makedirs(ARCHIVOS_DIR, exist_ok=True)
        existing = [f for f in os.listdir(ARCHIVOS_DIR) if f.startswith("LOG") and f.endswith(".log")]
        n = len(existing) + 1
        self.log_path = os.path.join(ARCHIVOS_DIR, f"LOG{n}.log")

        """Todos los comandos falsos disponibles"""
        self.binarios = {
            "whoami":    ComandoWhoami,
            "pwd":       ComandoPwd,
            "ls":        ComandoLs,
            "dir":       ComandoDir,
            "clear":     ComandoClear,
            "history":   ComandoHistory,
            "cat":       ComandoCat,
            "vi":        ComandoVi,
            "grep":      ComandoGrep,
            "egrep":     ComandoGrep,
            "fgrep":     ComandoGrep,
            "find":      ComandoFind,
            "mkdir":     ComandoMkdir,
            "rm":        ComandoRm,
            "ip":        ComandoIp,
            "ifconfig":  ComandoIp,
            "ssh":       ComandoSsh,
            "wget":      ComandoWget,
            "curl":      ComandoCurl,
            "sudo":      ComandoSudo,
            "chmod":     ComandoChmod,
            "bash":      ComandoBash,
            "sh":        ComandoBash,
            "python3":   ComandoPython3,
            "python":    ComandoPython3,
            "apt":       ComandoApt,
            "apt-get":   ComandoAptGet,
            "echo":      ComandoEcho,
            "touch":     ComandoTouch,
            "cowsay":    ComandoCowsay,
            "sl":        ComandoSl,
            "id":        ComandoId,
            "uname":     ComandoUname,
            "hostname":  ComandoHostname,
            "ps":        ComandoPs,
            "netstat":   ComandoNetstat,
            "ss":        ComandoSs,
            "env":       ComandoEnv,
            "docker":    ComandoDocker,
            "systemctl": ComandoSystemctl,
            "service":   ComandoService,
            "mysql":     ComandoMysql,
            "nc":        ComandoNc,
            "netcat":    ComandoNc,
            "base64":    ComandoBase64,
            "cp":        ComandoCp,
            "mv":        ComandoMv,
            "tail":      ComandoTail,
            "head":      ComandoHead,
            "last":      ComandoLast,
            "who":       ComandoWho,
            "w":         ComandoW,
            "df":        ComandoDf,
            "free":      ComandoFree,
            "uptime":    ComandoUptime,
            "crontab":   ComandoCrontab,
            "alias":     ComandoAlias,
        }

    def _setup_readline(self):
        """Configura l'autocompletat per tabulador usant els noms de binaris i els arxius virtuals de LS_DATA a comandos.py."""
        try:
            import readline
            from comandos import LS_DATA, _extra_for
            cmds = list(self.binarios.keys()) + list(ALIASES.keys()) + ["cd", "exit", "logout"]

            def completer(text, state):
                buf = readline.get_line_buffer()
                before_text = buf[:buf.rfind(text)] if text in buf else buf
                if not before_text.strip():
                    options = [c + " " for c in cmds if c.startswith(text)]
                else:
                    data  = LS_DATA.get(self.cwd)
                    names = data["short"].split() if data else []
                    names += [e["name"] for e in _extra_for(self.cwd)]
                    options = [n for n in names if n.startswith(text)]
                try:
                    return options[state]
                except IndexError:
                    return None

            readline.set_completer(completer)
            readline.parse_and_bind("tab: complete")
        except ImportError:
            pass

    def _expand_vars(self, text):
        """Substitueix variables d'entorn ($VAR o ${VAR}) usant el diccionari ENV_VARS de comandos.py."""
        env = {**ENV_VARS, "PWD": self.cwd, "OLDPWD": self.cwd}
        def _sub(m):
            key = m.group(1) or m.group(2)
            return env.get(key, m.group(0))
        return re.sub(r'\$\{(\w+)\}|\$(\w+)', _sub, text)

    def _run_one(self, cmd_str, stdin=None):
        """Executa una sola comanda: resol aliases, redireccions (>) i instancia la classe corresponent de comandos.py."""
        cmd_str = self._expand_vars(cmd_str.strip())
        if not cmd_str:
            return ""

        first_token = cmd_str.split()[0]
        if first_token in ALIASES:
            cmd_str = ALIASES[first_token] + cmd_str[len(first_token):]

        normalized = re.sub(r'(?<![>])>(?![>])', ' > ', cmd_str)
        parts = normalized.split()
        redir_file = None
        if ">" in parts:
            idx = parts.index(">")
            redir_file = parts[idx + 1] if idx + 1 < len(parts) else None
            parts = parts[:idx]
            if not parts:
                return ""

        base, args = parts[0], parts[1:]

        if base == "cd":
            out = self._cd(args)
        else:
            ClaseCmd = self.binarios.get(base)
            cmd_obj = ClaseCmd(args, self.cwd) if ClaseCmd else ComandoNoEncontrado(base, args, self.cwd)
            if stdin is not None:
                cmd_obj._stdin = stdin
            out = cmd_obj.executar()

        if redir_file:
            content  = out or ""
            abs_path = posixpath.normpath(
                redir_file if redir_file.startswith("/") else self.cwd.rstrip("/") + "/" + redir_file
            )
            VIRTUAL_FS[abs_path] = content
            _add_entry(self.cwd, os.path.basename(redir_file), size=len(content))
            redir_dir = os.path.join(ARCHIVOS_DIR, "redireccionados")
            os.makedirs(redir_dir, exist_ok=True)
            with open(os.path.join(redir_dir, os.path.basename(redir_file)), "w", encoding="utf-8") as f:
                f.write(content)
            return ""

        return out or ""

    def _run_pipeline(self, cmd_str):
        """Executa una cadena de comandes separades per pipes (|), passant la sortida de cada una com a stdin de la seguent."""
        pipe_parts = re.split(r'(?<!\|)\|(?!\|)', cmd_str)
        if len(pipe_parts) == 1:
            return self._run_one(cmd_str.strip())
        output = None
        for part in pipe_parts:
            output = self._run_one(part.strip(), stdin=output)
        return output

    def _run_compound(self, cmd_raw):
        """Executa comandes compostes separades per ; i &&, i actualitza la fase del graf de grafo.py despres de cada grup."""
        for seq_group in re.split(r'\s*;\s*', cmd_raw):
            and_parts = re.split(r'\s*&&\s*', seq_group)
            for i, part in enumerate(and_parts):
                out = self._run_pipeline(part.strip())
                if out:
                    print(out)
                if i < len(and_parts) - 1 and not out:
                    break
            nova_fase = trobar_millor_fase(seq_group.strip(), self.fase_actual, self.totes_fases)
            if nova_fase:
                self.fase_actual = nova_fase

    def _prompt(self):
        """Retorna el prompt de bash substituint /home/ubuntu per ~ per simular un terminal Ubuntu real."""
        display = self.cwd.replace("/home/ubuntu", "~")
        return f"ubuntu@ubuntu-server:{display}$ "

    def arrancar(self):
        """Bucle principal d'entrada. En sortir crida escanear_logs de patrons.py i guarda el resum de la sessio a archivos/LOGn.log."""
        print(_make_banner())
        self._setup_readline()

        while True:
            try:
                cmd_raw = input(self._prompt()).strip()
                if not cmd_raw:
                    continue
                if cmd_raw in ("exit", "logout", "quit"):
                    break

                if cmd_raw == "tatami":
                    cmds = sorted(list(self.binarios.keys()) + list(ALIASES.keys()) + ["cd", "exit"])
                    print("Comandos disponibles:")
                    cols = [cmds[i:i+6] for i in range(0, len(cmds), 6)]
                    for row in cols:
                        print("  " + "  ".join(f"{c:<12}" for c in row))
                    continue

                self._log(cmd_raw)
                self.logs.append(cmd_raw)
                self._run_compound(cmd_raw)

            except KeyboardInterrupt:
                print()

        amenazas = escanear_logs(self.logs)
        with open(self.log_path, "a", encoding="utf-8") as f:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] --- FIN DE SESION ---\n")
            f.write(f"[{ts}] Fase final: {self.fase_actual.nom} (riesgo: {self.fase_actual.risc})\n")
            f.write(f"[{ts}] Patrones: {', '.join(amenazas) if amenazas else 'Ninguno'}\n")

    def _log(self, cmd):
        """Escriu la comanda amb timestamp al fitxer de log actiu a archivos/LOGn.log."""
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] - {cmd}\n")

    def _cd(self, args):
        """Gestiona el canvi de directori validant la ruta contra VIRTUAL_DIRS de comandos.py."""
        if not args or args[0] in ("~", ""):
            self.cwd = "/home/ubuntu"
            return ""
        target = args[0]
        new_dir = posixpath.normpath(
            target if target.startswith("/") else self.cwd.rstrip("/") + "/" + target
        )
        if new_dir in VIRTUAL_DIRS:
            self.cwd = new_dir
            return ""
        return f"bash: cd: {target}: No such file or directory"

if __name__ == "__main__":
    app = TatamiShell()
    app.arrancar()