import os
import sys
import time
import datetime
import getpass
import random
import posixpath

ARCHIVOS_DIR = os.path.join(os.path.dirname(__file__), "archivos")

VIRTUAL_DIRS = {
    "/",
    "/home",
    "/home/ubuntu",
    "/home/ubuntu/server_config",
    "/home/ubuntu/backups",
    "/home/ubuntu/.ssh",
    "/etc",
    "/var",
    "/var/log",
    "/proc",
}

_extras = {}
_ocultos = set()

def _extra_for(dirpath):
    return [e for e in _extras.get(dirpath, [])
            if dirpath.rstrip("/") + "/" + e["name"] not in _ocultos]

def _add_entry(dirpath, name, is_dir=False, size=0):
    if dirpath not in _extras:
        _extras[dirpath] = []
    full_path = dirpath.rstrip("/") + "/" + name
    _ocultos.discard(full_path)  # si va ser rm'd, ressuscitar-lo
    now = datetime.datetime.now().strftime("%b %d %H:%M")
    for e in _extras[dirpath]:
        if e["name"] == name:
            e["is_dir"] = is_dir
            e["size"] = size
            e["date"] = now
            return
    _extras[dirpath].append({"name": name, "is_dir": is_dir, "size": size, "date": now})

def _norm(path):
    return posixpath.normpath(path)

VIRTUAL_FS = {
    "/home/ubuntu/.bashrc": (
        "# ~/.bashrc: executed by bash(1) for non-login shells.\n"
        "export PATH=\"$HOME/.local/bin:$PATH\"\n"
        "alias ll='ls -alF'\nalias la='ls -A'\nalias l='ls -CF'\n"
        "PS1='\\u@\\h:\\w\\$ '\n"
    ),
    "/home/ubuntu/.bash_history": (
        "ls -la\ncat credentials.bak\nmysql -u root -p\nsudo su\n"
        "cat /etc/passwd\nssh root@192.168.1.1\n"
        "wget http://updates.company-internal.net/agent.sh\n"
        "chmod +x agent.sh\n./agent.sh\nhistory -c\n"
    ),
    "/home/ubuntu/.mysql_history": (
        "show databases;\nuse production_db;\n"
        "select * from users limit 10;\n"
        "update users set password='newpass123' where id=1;\n"
    ),
    "/home/ubuntu/credentials.bak": (
        "# Server credentials backup - DO NOT SHARE\n"
        "# Generated: 2026-01-15\n\n"
        "[database]\nhost=127.0.0.1\nuser=root\npass=Pr0duct10n#2025!\n\n"
        "[ssh]\nuser=ubuntu\nkey=/home/ubuntu/.ssh/id_rsa\n\n"
        "[api]\ntoken=ghp_xK9mN2pL8qR4vT6wY0zA3bC5dE7fG1hI\n"
        "secret=sk-prod-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6\n"
    ),
    "/home/ubuntu/server_config/nginx.conf": (
        "server {\n    listen 80;\n    server_name company-internal.net;\n"
        "    root /var/www/html;\n    index index.php index.html;\n\n"
        "    location / { try_files $uri $uri/ =404; }\n"
        "    location ~ \\.php$ {\n"
        "        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;\n    }\n}\n"
    ),
    "/home/ubuntu/server_config/app.conf": (
        "[app]\ndebug=false\n"
        "secret_key=f3a9b2c1d4e5f6a7b8c9d0e1f2a3b4c5\n"
        "db_url=mysql://root:Pr0duct10n#2025!@127.0.0.1/production_db\n"
        "redis_url=redis://127.0.0.1:6379/0\n"
    ),
    "/home/ubuntu/.ssh/known_hosts": (
        "192.168.1.1 ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB\n"
        "10.0.0.5 ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQ\n"
        "github.com ssh-rsa AAAAB3NzaC1yc2AAAABIwAAAQEA\n"
    ),
    "/home/ubuntu/.ssh/id_rsa": (
        "-----BEGIN OPENSSH PRIVATE KEY-----\n"
        "b3BlbnNzaC1rZXkAAAABAAAAMAAAABNlY2RzYS1zaGEyLW5pc3RwMjU2AAAACG5pc3Rw\n"
        "MjU2AAAAQQTfakeKEYdataXXXimKh5OLhFP3GXqIPMzMFAaBX5LvnRGqVpn2tD8IV\n"
        "TD8SfakeXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n"
        "AAAAE3VidW50dUB1YnVudHUtc2VydmVyAQ==\n"
        "-----END OPENSSH PRIVATE KEY-----\n"
    ),
    "/home/ubuntu/.ssh/id_rsa.pub": (
        "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYA"
        "AABBBMfakeKEYpublicXXXimKh5OLhFP3GXqIPMzMFAaBX5LvnRGqVpn2tD8IVTD8S"
        " ubuntu@ubuntu-server\n"
    ),
    "/var/log/auth.log": (
        "Jan 15 08:15:33 ubuntu-server sshd[2756]: Accepted publickey for ubuntu from 192.168.1.10 port 54821 ssh2: RSA SHA256:xK9mN2pL8qR4vT6wY0zA3bC5\n"
        "Jan 15 09:22:11 ubuntu-server sudo:   ubuntu : TTY=pts/0 ; PWD=/home/ubuntu ; USER=root ; COMMAND=/bin/cat /etc/shadow\n"
        "Jan 15 09:22:11 ubuntu-server sudo: pam_unix(sudo:auth): authentication failure; logname=ubuntu uid=1000 euid=0\n"
        "Jan 15 10:33:41 ubuntu-server sshd[2891]: Accepted publickey for ubuntu from 192.168.1.10 port 54822 ssh2: RSA SHA256:xK9mN2pL8qR4vT6wY0zA3bC5\n"
        "Jan 15 11:04:22 ubuntu-server su[4521]: pam_unix(su-l:session): session opened for user root by ubuntu(uid=0)\n"
        "Jan 15 13:45:01 ubuntu-server CRON[5234]: pam_unix(cron:session): session opened for user ubuntu by (uid=0)\n"
        "Jan 15 14:22:03 ubuntu-server sshd[6102]: Accepted publickey for ubuntu from 192.168.1.10 port 54823 ssh2: RSA SHA256:xK9mN2pL8qR4vT6wY0zA3bC5\n"
    ),
    "/var/log/syslog": (
        "Jan 15 08:00:01 ubuntu-server kernel: [    0.000000] Linux version 5.15.0-88-generic\n"
        "Jan 15 08:00:03 ubuntu-server systemd[1]: Started MySQL Community Server.\n"
        "Jan 15 08:00:05 ubuntu-server systemd[1]: Started nginx - A high performance web server.\n"
        "Jan 15 08:15:30 ubuntu-server systemd[1]: Started OpenBSD Secure Shell server.\n"
        "Jan 15 13:45:01 ubuntu-server CRON[5234]: (ubuntu) CMD (/home/ubuntu/server_config/health_check.py)\n"
    ),
    "/etc/crontab": (
        "# /etc/crontab: system-wide crontab\n"
        "SHELL=/bin/sh\n"
        "PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n\n"
        "# m  h  dom mon dow user    command\n"
        "17 *  * * *  root  cd / && run-parts --report /etc/cron.hourly\n"
        "0  3  * * *  root  /home/ubuntu/backups/backup.sh\n"
        "*/5 * * * *  ubuntu /home/ubuntu/server_config/health_check.py > /dev/null 2>&1\n"
    ),
    "/etc/hosts": (
        "127.0.0.1   localhost\n"
        "127.0.1.1   ubuntu-server\n"
        "192.168.1.1 gateway.local\n"
        "10.0.0.5    db-replica.internal\n"
        "::1         localhost ip6-localhost ip6-loopback\n"
    ),
    "/proc/version": (
        "Linux version 5.15.0-88-generic (buildd@lcy02-amd64-059) "
        "(gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0, GNU ld (GNU Binutils for Ubuntu) 2.38) "
        "#98-Ubuntu SMP Mon Oct 2 15:18:56 UTC 2023\n"
    ),
    "/proc/cpuinfo": (
        "processor\t: 0\nvendor_id\t: GenuineIntel\n"
        "model name\t: Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz\n"
        "cpu MHz\t\t: 2400.068\ncache size\t: 30720 KB\n"
        "processor\t: 1\nvendor_id\t: GenuineIntel\n"
        "model name\t: Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz\n"
        "cpu MHz\t\t: 2400.068\ncache size\t: 30720 KB\n"
    ),
}

LS_DATA = {
    "/": {
        "short": "bin  boot  dev  etc  home  lib  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var",
        "long": (
            "total 64\n"
            "drwxr-xr-x  20 root root 4096 Nov 19 08:00 .\n"
            "drwxr-xr-x  20 root root 4096 Nov 19 08:00 ..\n"
            "drwxr-xr-x   2 root root 4096 Nov 19 08:00 bin\n"
            "drwxr-xr-x   3 root root 4096 Nov 19 08:00 boot\n"
            "drwxr-xr-x  17 root root 3860 Nov 20 08:00 dev\n"
            "drwxr-xr-x  76 root root 4096 Nov 20 08:01 etc\n"
            "drwxr-xr-x   3 root root 4096 Nov 19 08:10 home\n"
            "drwxr-xr-x  10 root root 4096 Nov 19 08:00 lib\n"
            "drwxr-xr-x   2 root root 4096 Nov 19 08:00 media\n"
            "drwxr-xr-x   2 root root 4096 Nov 19 08:00 mnt\n"
            "drwxr-xr-x   2 root root 4096 Nov 19 08:00 opt\n"
            "dr-xr-xr-x 174 root root    0 Nov 20 08:00 proc\n"
            "drwx------   4 root root 4096 Nov 20 10:00 root\n"
            "drwxr-xr-x  26 root root  760 Nov 20 08:01 run\n"
            "drwxr-xr-x   2 root root 4096 Nov 19 08:00 sbin\n"
            "drwxr-xr-x   2 root root 4096 Nov 19 08:00 srv\n"
            "dr-xr-xr-x  13 root root    0 Nov 20 08:00 sys\n"
            "drwxrwxrwt  10 root root 4096 Nov 20 14:22 tmp\n"
            "drwxr-xr-x  11 root root 4096 Nov 19 08:00 usr\n"
            "drwxr-xr-x  12 root root 4096 Nov 19 08:00 var"
        ),
    },
    "/home": {
        "short": "ubuntu",
        "long": (
            "total 4\n"
            "drwxr-xr-x  3 root   root   4096 Nov 19 08:10 .\n"
            "dr-xr-xr-x 20 root   root   4096 Nov 19 08:00 ..\n"
            "drwxr-xr-x  5 ubuntu ubuntu 4096 Nov 20 14:22 ubuntu"
        ),
    },
    "/home/ubuntu": {
        "short": "server_config  backups  credentials.bak",
        "long": (
            "total 48\n"
            "drwxr-xr-x 5 ubuntu ubuntu 4096 Nov 20 14:22 .\n"
            "drwxr-xr-x 3 root   root   4096 Nov 19 08:10 ..\n"
            "-rw-r--r-- 1 ubuntu ubuntu  220 Nov 20 10:15 .bash_logout\n"
            "-rw-r--r-- 1 ubuntu ubuntu  256 Nov 20 10:15 .bashrc\n"
            "-rw------- 1 ubuntu ubuntu  512 Nov 20 14:22 .bash_history\n"
            "-rw------- 1 ubuntu ubuntu  189 Nov 20 13:55 .mysql_history\n"
            "drwx------ 2 ubuntu ubuntu 4096 Nov 20 11:00 .ssh\n"
            "drwxr-xr-x 2 ubuntu ubuntu 4096 Nov 20 11:30 backups\n"
            "-rw------- 1 ubuntu ubuntu  342 Nov 20 12:18 credentials.bak\n"
            "drwxr-xr-x 2 ubuntu ubuntu 4096 Nov 20 11:45 server_config"
        ),
    },
    "/home/ubuntu/server_config": {
        "short": "nginx.conf  app.conf",
        "long": (
            "total 16\n"
            "drwxr-xr-x 2 ubuntu ubuntu 4096 Nov 20 11:45 .\n"
            "drwxr-xr-x 5 ubuntu ubuntu 4096 Nov 20 14:22 ..\n"
            "-rw-r--r-- 1 ubuntu ubuntu  389 Nov 20 11:45 nginx.conf\n"
            "-rw-r--r-- 1 ubuntu ubuntu  201 Nov 20 11:50 app.conf"
        ),
    },
    "/home/ubuntu/backups": {
        "short": "db_backup_2025-11-20.sql.gz",
        "long": (
            "total 2052\n"
            "drwxr-xr-x 2 ubuntu ubuntu    4096 Nov 20 11:00 .\n"
            "drwxr-xr-x 5 ubuntu ubuntu    4096 Nov 20 14:22 ..\n"
            "-rw-r--r-- 1 ubuntu ubuntu 2097152 Nov 20 11:00 db_backup_2025-11-20.sql.gz"
        ),
    },
    "/home/ubuntu/.ssh": {
        "short": "known_hosts  id_rsa  id_rsa.pub",
        "long": (
            "total 20\n"
            "drwx------ 2 ubuntu ubuntu 4096 Jan 15 10:33 .\n"
            "drwxr-xr-x 5 ubuntu ubuntu 4096 Jan 15 14:22 ..\n"
            "-rw------- 1 ubuntu ubuntu  411 Jan 15 10:33 id_rsa\n"
            "-rw-r--r-- 1 ubuntu ubuntu  102 Jan 15 10:33 id_rsa.pub\n"
            "-rw-r--r-- 1 ubuntu ubuntu  189 Jan 15 11:00 known_hosts"
        ),
    },
    "/etc": {
        "short": "crontab  hosts  hostname  passwd  shadow  fstab  os-release  ssh",
        "long": (
            "total 76\n"
            "drwxr-xr-x 76 root root 4096 Jan 15 08:01 .\n"
            "drwxr-xr-x 20 root root 4096 Jan 15 08:00 ..\n"
            "-rw-r--r--  1 root root  722 Jan 15 08:00 crontab\n"
            "-rw-r--r--  1 root root  194 Jan 15 08:00 hosts\n"
            "-rw-r--r--  1 root root   13 Jan 15 08:00 hostname\n"
            "-rw-r--r--  1 root root 1895 Jan 15 08:00 passwd\n"
            "-rw-r-----  1 root shadow 1024 Jan 15 08:00 shadow\n"
            "-rw-r--r--  1 root root  741 Jan 15 08:00 fstab\n"
            "-rw-r--r--  1 root root  230 Jan 15 08:00 os-release\n"
            "drwxr-xr-x  4 root root 4096 Jan 15 08:00 ssh"
        ),
    },
    "/var/log": {
        "short": "auth.log  syslog  kern.log  dpkg.log  apt",
        "long": (
            "total 1124\n"
            "drwxrwxr-x  8 root syslog 4096 Jan 15 14:22 .\n"
            "drwxr-xr-x 12 root root   4096 Jan 15 08:00 ..\n"
            "-rw-r-----  1 syslog adm   8420 Jan 15 14:22 auth.log\n"
            "-rw-r-----  1 syslog adm  92340 Jan 15 14:22 syslog\n"
            "-rw-r-----  1 syslog adm  14210 Jan 15 14:22 kern.log\n"
            "-rw-r--r--  1 root   root  3210 Jan 15 10:00 dpkg.log"
        ),
    },
    "/proc": {
        "short": "version  cpuinfo  meminfo  uptime  net",
        "long": (
            "total 0\n"
            "dr-xr-xr-x 174 root root 0 Jan 15 08:00 .\n"
            "drwxr-xr-x  20 root root 0 Jan 15 08:00 ..\n"
            "-r--r--r--   1 root root 0 Jan 15 08:00 cpuinfo\n"
            "-r--r--r--   1 root root 0 Jan 15 08:00 meminfo\n"
            "-r--r--r--   1 root root 0 Jan 15 08:00 uptime\n"
            "-r--r--r--   1 root root 0 Jan 15 08:00 version"
        ),
    },
}

ENV_VARS = {
    "SHELL":    "/bin/bash",
    "HOME":     "/home/ubuntu",
    "LOGNAME":  "ubuntu",
    "USER":     "ubuntu",
    "PATH":     "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "LANG":     "en_US.UTF-8",
    "DB_HOST":  "127.0.0.1",
    "DB_PASSWORD": "Pr0duct10n#2025!",
    "API_KEY":  "sk-prod-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "MAIL_SMTP": "smtp.company-internal.net",
    "MAIL_USER": "noreply@company-internal.net",
    "MAIL_PASS": "M4ilS3rv3r!2026",
}

class ComandoHoneypot:
    """Classe base per a tots els comandos del honeypot. Defineix l'estructura comuna: arguments, directori actual i el mètode executar() que cada subclasse sobreescriu."""
    def __init__(self, args, cwd="/home/ubuntu"):
        self.args = args
        self.cwd = cwd

    def executar(self):
        pass

class ComandoPwd(ComandoHoneypot):
    """Retorna el directori de treball actual. Simula el comportament real de pwd mostrant la ruta on es troba l'atacant."""
    def executar(self):
        return self.cwd

class ComandoLs(ComandoHoneypot):
    """Llista el contingut d'un directori. Suporta -l per al format llarg. Combina arxius estàtics predefinits amb els creats dinàmicament per l'atacant."""
    def executar(self):
        args_str = " ".join(self.args)
        target = self.cwd
        for a in self.args:
            if not a.startswith("-"):
                target = _norm(a if a.startswith("/") else self.cwd.rstrip("/") + "/" + a)
                break

        data = LS_DATA.get(target)
        if data is None:
            if target in VIRTUAL_DIRS:
                data = {"short": "", "long": "total 0"}
            else:
                return f"ls: cannot access '{target}': No such file or directory"

        extras = _extra_for(target)

        if "-l" in args_str:
            result = data["long"]
            for e in extras:
                perm = "drwxr-xr-x" if e["is_dir"] else "-rw-r--r--"
                result += f"\n{perm} 1 ubuntu ubuntu {e['size']:8d} {e['date']} {e['name']}"
            return result

        parts = [data["short"]] if data["short"] else []
        parts += [e["name"] for e in extras]
        return "  ".join(parts)


class ComandoDir(ComandoLs):
    """Àlies de ls per compatibilitat amb sistemes Windows. Hereta tot el comportament de ComandoLs."""
    pass

class ComandoClear(ComandoHoneypot):
    """Esborra la pantalla del terminal mitjançant seqüències d'escapament ANSI. Simula el comportament real de clear."""
    def executar(self):
        return "\033[2J\033[H"

class ComandoHistory(ComandoHoneypot):
    """Mostra un historial de comandos fals però creïble, dissenyat per atreure l'atenció de l'atacant cap a arxius sensibles i accions sospitoses."""
    def executar(self):
        return (
            "    1  ls -la\n"
            "    2  cat credentials.bak\n"
            "    3  mysql -u root -p\n"
            "    4  sudo su\n"
            "    5  cat /etc/passwd\n"
            "    6  ssh root@192.168.1.1\n"
            "    7  wget http://updates.company-internal.net/agent.sh\n"
            "    8  chmod +x agent.sh\n"
            "    9  ./agent.sh\n"
            "   10  history"
        )

class ComandoCat(ComandoHoneypot):
    """Mostra el contingut d'arxius virtuals. Gestiona arxius del sistema ficticis (/etc/passwd, /etc/shadow), arxius del sistema de fitxers virtual i errors de permisos."""
    def executar(self):
        if not self.args:
            return ""
        target = self.args[0]
        abs_path = _norm(target if target.startswith("/") else self.cwd.rstrip("/") + "/" + target)

        if abs_path in _ocultos:
            return f"cat: {target}: No such file or directory"
        if abs_path in VIRTUAL_FS:
            return VIRTUAL_FS[abs_path]
        if "/etc/passwd" in abs_path:
            return (
                "root:x:0:0:root:/root:/bin/bash\n"
                "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                "ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\n"
                "mysql:x:114:119:MySQL Server,,,:/nonexistent:/bin/false"
            )
        if "/etc/shadow" in abs_path:
            return "cat: /etc/shadow: Permission denied"
        if "db_backup" in abs_path:
            return f"cat: {target}: binary file — use 'gunzip' first"

        dirname = abs_path.rsplit("/", 1)[0]
        basename = abs_path.rsplit("/", 1)[1]
        if any(e["name"] == basename for e in _extras.get(dirname, [])):
            return ""

        return f"cat: {target}: No such file or directory"

class ComandoVi(ComandoHoneypot):
    """Editor de text interactiu que simula vi. Permet a l'atacant escriure i guardar arxius. Tot el que s'edita queda desat a archivos/editados/ per anàlisi forense."""
    def executar(self):
        raw = next((a for a in self.args if not a.startswith("-")), "")
        if raw:
            abs_path = _norm(raw if raw.startswith("/") else self.cwd.rstrip("/") + "/" + raw)
            fname = abs_path.rsplit("/", 1)[-1]
        else:
            abs_path = ""
            fname = ""

        existing = VIRTUAL_FS.get(abs_path, "")
        lines = existing.splitlines() if existing else []

        print("\033[2J\033[H", end="")
        for line in lines:
            print(line)
        for _ in range(max(0, 20 - len(lines))):
            print("~")
        label = f'"{fname}"' if fname else "[No Name]"
        new_marker = " [New File]" if not existing else ""
        print(f"{label}{new_marker}")
        print("-- INSERT -- (escriu línies, ':wq' per guardar, ':q!' per sortir)", flush=True)

        buffer = list(lines)
        try:
            while True:
                line = input()
                if line in (":wq", ":x"):
                    content = "\n".join(buffer)
                    if abs_path:
                        VIRTUAL_FS[abs_path] = content
                        _add_entry(self.cwd, fname, size=len(content))
                        edit_dir = os.path.join(ARCHIVOS_DIR, "editados")
                        os.makedirs(edit_dir, exist_ok=True)
                        with open(os.path.join(edit_dir, os.path.basename(fname)), "w", encoding="utf-8") as f:
                            f.write(content)
                    return f'"{fname}" {len(buffer)}L, {len(content)}C written'
                elif line in (":q!", ":q"):
                    return ""
                else:
                    buffer.append(line)
        except (KeyboardInterrupt, EOFError):
            print("\033[2J\033[H", end="")
            return ""

class ComandoGrep(ComandoHoneypot):
    """Cerca patrons de text dins dels arxius del sistema virtual. Suporta -i (case insensitive), -r (recursiu), -n (número de línia) i stdin des de pipes."""
    def _get_content(self, abs_path):
        if abs_path in _ocultos:
            return None, "hidden"
        if abs_path in VIRTUAL_FS:
            return VIRTUAL_FS[abs_path], None
        if "/etc/passwd" in abs_path:
            return (
                "root:x:0:0:root:/root:/bin/bash\n"
                "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                "ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\n"
                "mysql:x:114:119:MySQL Server,,,:/nonexistent:/bin/false\n"
            ), None
        dirname = abs_path.rsplit("/", 1)[0]
        basename = abs_path.rsplit("/", 1)[1]
        if any(e["name"] == basename for e in _extras.get(dirname, [])):
            return "", None
        return None, "missing"

    def executar(self):
        if not self.args:
            return "Usage: grep [OPTION]... PATTERN [FILE]..."

        flags  = [a for a in self.args if a.startswith("-")]
        others = [a for a in self.args if not a.startswith("-")]

        case_i   = "-i" in flags
        show_num = "-n" in flags
        recursive = "-r" in flags or "-R" in flags

        if not others:
            return "Usage: grep [OPTION]... PATTERN [FILE]..."

        pattern = others[0]
        files   = others[1:]

        stdin = getattr(self, "_stdin", None)

        # no file and no stdin → nothing to search
        if not files and stdin is None:
            return ""

        def match_lines(content, label=None):
            out = []
            for i, line in enumerate(content.splitlines(), 1):
                haystack = line.lower() if case_i else line
                needle   = pattern.lower() if case_i else pattern
                if needle in haystack:
                    prefix = f"{label}:" if label else ""
                    num    = f"{i}:" if show_num else ""
                    out.append(f"{prefix}{num}{line}")
            return out

        results = []

        if stdin is not None and not files:
            results = match_lines(stdin)
        else:
            for fname in files:
                abs_path = _norm(fname if fname.startswith("/") else self.cwd.rstrip("/") + "/" + fname)
                if recursive and abs_path in VIRTUAL_DIRS:
                    for key, val in VIRTUAL_FS.items():
                        if key.startswith(abs_path) and key not in _ocultos:
                            results += match_lines(val, key)
                    continue
                content, err = self._get_content(abs_path)
                if err == "hidden" or err == "missing":
                    results.append(f"grep: {fname}: No such file or directory")
                    continue
                label = fname if len(files) > 1 else None
                results += match_lines(content, label)

        return "\n".join(results)

def _resolve_content(abs_path):
    """Devuelve (contenido, error_msg). Centraliza la lógica de acceso al FS virtual."""
    if abs_path in _ocultos:
        return None, f"No such file or directory"
    if abs_path in VIRTUAL_FS:
        return VIRTUAL_FS[abs_path], None
    if "/etc/passwd" in abs_path:
        return (
            "root:x:0:0:root:/root:/bin/bash\n"
            "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
            "ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\n"
            "mysql:x:114:119:MySQL Server,,,:/nonexistent:/bin/false\n"
        ), None
    if "/etc/shadow" in abs_path:
        return None, "Permission denied"
    if "db_backup" in abs_path:
        return None, f"binary file — use 'gunzip' first"
    dirname = abs_path.rsplit("/", 1)[0]
    basename = abs_path.rsplit("/", 1)[1]
    if any(e["name"] == basename for e in _extras.get(dirname, [])):
        return "", None
    return None, "No such file or directory"

class ComandoTail(ComandoHoneypot):
    """Mostra les últimes N línies d'un arxiu (per defecte 10). Suporta -n N i -F per seguir en temps real (simulat)."""
    def _parse(self):
        n, fname = 10, None
        i = 0
        while i < len(self.args):
            a = self.args[i]
            if a in ("-n", "--lines") and i + 1 < len(self.args):
                try:
                    n = int(self.args[i + 1]); i += 2; continue
                except ValueError:
                    pass
            elif a.lstrip("-").isdigit():
                n = int(a.lstrip("-"))
            elif not a.startswith("-"):
                fname = a
            i += 1
        return n, fname

    def executar(self):
        n, fname = self._parse()
        stdin = getattr(self, "_stdin", None)
        if fname is None and stdin is not None:
            return "\n".join(stdin.splitlines()[-n:])
        if fname is None:
            return ""
        abs_path = _norm(fname if fname.startswith("/") else self.cwd.rstrip("/") + "/" + fname)
        content, err = _resolve_content(abs_path)
        if err:
            return f"tail: {fname}: {err}"
        return "\n".join(content.splitlines()[-n:])

class ComandoHead(ComandoHoneypot):
    """Mostra les primeres N línies d'un arxiu (per defecte 10). Suporta -n N i stdin des de pipes."""
    def _parse(self):
        n, fname = 10, None
        i = 0
        while i < len(self.args):
            a = self.args[i]
            if a in ("-n", "--lines") and i + 1 < len(self.args):
                try:
                    n = int(self.args[i + 1]); i += 2; continue
                except ValueError:
                    pass
            elif a.lstrip("-").isdigit():
                n = int(a.lstrip("-"))
            elif not a.startswith("-"):
                fname = a
            i += 1
        return n, fname

    def executar(self):
        n, fname = self._parse()
        stdin = getattr(self, "_stdin", None)
        if fname is None and stdin is not None:
            return "\n".join(stdin.splitlines()[:n])
        if fname is None:
            return ""
        abs_path = _norm(fname if fname.startswith("/") else self.cwd.rstrip("/") + "/" + fname)
        content, err = _resolve_content(abs_path)
        if err:
            return f"head: {fname}: {err}"
        return "\n".join(content.splitlines()[:n])

class ComandoFind(ComandoHoneypot):
    """Llista arxius del sistema virtual incloent credencials i configuracions sensibles. Afegeix dinàmicament els arxius creats per l'atacant durant la sessió."""
    def executar(self):
        static = [p for p in [
            "/home/ubuntu/credentials.bak",
            "/home/ubuntu/server_config/app.conf",
            "/home/ubuntu/server_config/nginx.conf",
            "/home/ubuntu/backups/db_backup_2025-11-20.sql.gz",
        ] if p not in _ocultos]
        dynamic = []
        for dirpath, entries in _extras.items():
            for e in entries:
                full = dirpath.rstrip("/") + "/" + e["name"]
                if full not in _ocultos:
                    dynamic.append(full)
        errors = (
            "find: '/root': Permission denied\n"
            "find: '/etc/ssl/private': Permission denied"
        )
        return "\n".join(static + dynamic) + "\n" + errors

class ComandoMkdir(ComandoHoneypot):
    """Crea directoris virtuals dins del sistema de fitxers del honeypot. El nou directori queda registrat i és navegable amb cd."""
    def executar(self):
        if not self.args:
            return "mkdir: missing operand"
        for name in self.args:
            if name.startswith("-"):
                continue
            new_path = self.cwd.rstrip("/") + "/" + name
            _add_entry(self.cwd, name, is_dir=True, size=4096)
            VIRTUAL_DIRS.add(new_path)
        return ""

class ComandoRm(ComandoHoneypot):
    """Simula l'eliminació d'arxius marcant-los com a ocults. L'arxiu no s'esborra realment, sinó que queda registrat a archivos/eliminados/ per anàlisi forense."""
    def executar(self):
        targets = [a for a in self.args if not a.startswith("-")]
        if not targets:
            return "rm: missing operand"
        el_dir = os.path.join(ARCHIVOS_DIR, "eliminados")
        os.makedirs(el_dir, exist_ok=True)
        for t in targets:
            full = _norm(t if t.startswith("/") else self.cwd.rstrip("/") + "/" + t)
            _ocultos.add(full)
            with open(os.path.join(el_dir, os.path.basename(t)), "w", encoding="utf-8") as f:
                f.write(f"# Honeypot: rm capturat {datetime.datetime.now().isoformat()}\n# Ruta: {full}\n")
        return ""

class ComandoIp(ComandoHoneypot):
    """Mostra la configuració de xarxa fictícia del servidor. Respon tant a ip com a ifconfig amb adreces IP inventades però versemblants."""
    def executar(self):
        return (
            "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN\n"
            "    inet 127.0.0.1/8 scope host lo\n"
            "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP\n"
            "    inet 192.168.1.45/24 brd 192.168.1.255 scope global eth0"
        )

class ComandoSsh(ComandoHoneypot):
    """Simula un intent de connexió SSH fallida. Qualsevol intent de connexió externa des del servidor retorna Connection refused."""
    def executar(self):
        return "ssh: connect to host: Connection refused"

class ComandoWget(ComandoHoneypot):
    """Simula una descàrrega amb barra de progrés animada i velocitat variable. La URL i el fitxer descarregat queden registrats a archivos/downloads/."""
    def executar(self):
        if not self.args:
            return "wget: missing URL\nUsage: wget [OPTION]... [URL]..."
        url = self.args[0]
        filename = url.rstrip("/").split("/")[-1] or "index.html"
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        host = url.split("/")[2] if "//" in url else url
        size = random.randint(8192, 524288)
        size_kb = size / 1024
        base_speed = random.uniform(80, 480)

        print(f"--{now}--  {url}")
        print(f"Resolving {host}... 104.21.45.12")
        print(f"Connecting to {host}|104.21.45.12|:80... connected.")
        print("HTTP request sent, awaiting response... 200 OK")
        print(f"Length: {size} ({size_kb:.1f}K) [application/octet-stream]")
        print(f"Saving to: '{filename}'\n")

        try:
            for i in range(0, 101, 2):
                filled = i // 2
                bar = "=" * filled + (">" if i < 100 else "=") + " " * (50 - filled)
                transferred = int(size * i / 100)
                speed = base_speed * random.uniform(0.88, 1.12)
                speed_str = f"{speed:.1f}K/s" if speed < 1000 else f"{speed / 1024:.2f}M/s"
                sys.stdout.write(f"\r{i:3d}%[{bar}] {transferred:,}  {speed_str}   ")
                sys.stdout.flush()
                time.sleep(0.04)
        except KeyboardInterrupt:
            pass

        final_speed = f"{base_speed:.1f}K/s" if base_speed < 1000 else f"{base_speed / 1024:.2f}M/s"
        print(f"\n\n{now} ({final_speed}) - '{filename}' saved [{size}/{size}]")

        dl_dir = os.path.join(ARCHIVOS_DIR, "downloads")
        os.makedirs(dl_dir, exist_ok=True)
        with open(os.path.join(dl_dir, filename), "w", encoding="utf-8") as f:
            f.write(f"# Honeypot: wget capturat {datetime.datetime.now().isoformat()}\n# URL: {url}\n")

        _add_entry(self.cwd, filename, size=size)
        return ""

class ComandoCurl(ComandoHoneypot):
    """Simula una petició HTTP amb curl. Retorna una pàgina 403 Forbidden per fer creure que hi ha un servidor web però sense accés."""
    def executar(self):
        if not self.args:
            return "curl: try 'curl --help' or 'curl --manual' for more information"
        return (
            "<!DOCTYPE html>\n<html>\n<head><title>403 Forbidden</title></head>\n"
            "<body>\n<center><h1>403 Forbidden</h1></center>\n"
            "<hr><center>nginx</center>\n</body>\n</html>"
        )

class ComandoSudo(ComandoHoneypot):
    """Captura intents d'escalada de privilegis. Amb -l mostra permisos sudo. Per a subcomandos, captura contrasenya i executa la comanda amb 'privilegis de root'."""
    _SHADOW = (
        "root:$6$rounds=5000$fakehashedXXXXXX$AbCdEfGhIjKlMnOpQrStUvWxYz0123456789012345678901234567890123456789012345678901234:19372:0:99999:7:::\n"
        "daemon:*:19000:0:99999:7:::\n"
        "ubuntu:$6$rounds=5000$fakehashedYYYYYY$ZyXwVuTsRqPoNmLkJiHgFeDcBa9876543210987654321098765432109876543210987654321098765:19372:0:99999:7:::\n"
        "mysql:!:19000:0:99999:7:::\n"
    )

    def executar(self):
        # sudo -l
        if "-l" in self.args:
            return (
                "Matching Defaults entries for ubuntu on ubuntu-server:\n"
                "    env_reset, mail_badpass,\n"
                "    secure_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n\n"
                "User ubuntu may run the following commands on ubuntu-server:\n"
                "    (ALL : ALL) ALL"
            )

        pwd_file = os.path.join(ARCHIVOS_DIR, "sudo_passwords.txt")
        os.makedirs(ARCHIVOS_DIR, exist_ok=True)

        for intento in range(1, 4):
            try:
                pwd = getpass.getpass("[sudo] password for ubuntu: ")
            except (KeyboardInterrupt, EOFError):
                print()
                return ""

            with open(pwd_file, "a", encoding="utf-8") as f:
                ts = datetime.datetime.now().isoformat()
                f.write(f"[{ts}] cmd: sudo {' '.join(self.args)} | password: {pwd}\n")

            if intento < 3:
                print("Sorry, try again.")
            else:
                return "sudo: 3 incorrect password attempts"
        return ""

class ComandoChmod(ComandoHoneypot):
    """Simula el canvi de permisos d'arxius. Retorna silenci com faria un chmod real sense permisos suficients."""
    def executar(self):
        return ""

class ComandoBash(ComandoHoneypot):
    """Simula l'obertura d'un subshell bash o sh. Retorna silenci per no revelar que és un entorn controlat."""
    def executar(self):
        return ""

class ComandoPython3(ComandoHoneypot):
    """Simula l'execució de Python 3 mostrant un intèrpret interactiu que peta amb un error aleatori de permisos, suggerint que l'atacant intenta explotar el sistema."""
    _crashes = [
        (
            "import socket; s=socket.socket(); s.connect(('10.0.0.1', 9001))",
            "ConnectionRefusedError: [Errno 111] Connection refused",
        ),
        (
            "open('/etc/shadow').read()",
            "PermissionError: [Errno 13] Permission denied: '/etc/shadow'",
        ),
        (
            "import subprocess; subprocess.check_output(['id'])",
            "PermissionError: [Errno 1] Operation not permitted",
        ),
        (
            "import os; os.setuid(0)",
            "PermissionError: [Errno 1] Operation not permitted",
        ),
    ]

    def executar(self):
        cmd_shown, err = random.choice(self._crashes)
        return (
            "Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux\n"
            "Type \"help\", \"copyright\", \"credits\" or \"license\" for more information.\n"
            f">>> {cmd_shown}\n"
            "Traceback (most recent call last):\n"
            f"  File \"<stdin>\", line 1, in <module>\n"
            f"{err}"
        )

class ComandoApt(ComandoHoneypot):
    """Simula apt fallant per manca de permisos de root. Fa creure a l'atacant que el sistema és real però que necessita privilegis per instal·lar paquets."""
    def executar(self):
        return (
            "Reading package lists... Done\nBuilding dependency tree... Done\n"
            "Reading state information... Done\n"
            "E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)\n"
            "E: Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), are you root?"
        )

class ComandoAptGet(ComandoApt):
    """Àlies de ComandoApt per al format antic apt-get. Hereta el comportament idèntic."""
    pass

class ComandoEcho(ComandoHoneypot):
    """Retorna el text passat com a argument. Funciona com l'echo real i és compatible amb la redirecció > per crear arxius virtuals."""
    def executar(self):
        return " ".join(self.args)

class ComandoTouch(ComandoHoneypot):
    """Crea arxius buits al sistema de fitxers virtual. L'arxiu queda visible per ls i find, i es desa una còpia a archivos/creados/."""
    def executar(self):
        if self.args:
            created_dir = os.path.join(ARCHIVOS_DIR, "creados")
            os.makedirs(created_dir, exist_ok=True)
            for fname in self.args:
                abs_path = _norm(self.cwd.rstrip("/") + "/" + fname)
                fname_norm = abs_path.rsplit("/", 1)[-1]
                if abs_path in VIRTUAL_FS or abs_path in VIRTUAL_DIRS:
                    continue
                _add_entry(self.cwd, fname_norm, size=0)
                open(os.path.join(created_dir, fname_norm), "a").close()
        return ""

class ComandoCowsay(ComandoHoneypot):
    """Dibuixa una vaca ASCII que diu el missatge indicat. Si no es passa cap argument, diu 'Moo!' per defecte."""
    def executar(self):
        texto = " ".join(self.args) if self.args else "Moo!"
        w = len(texto) + 2
        return (
            f" {'_' * w}\n"
            f"< {texto} >\n"
            f" {'-' * w}\n"
            "        \\   ^__^\n"
            "         \\  (oo)\\_______\n"
            "            (__)\\       )\\/\\\n"
            "                ||----w |\n"
            "                ||     ||"
        )

class ComandoSl(ComandoHoneypot):
    """Animació ASCII d'un tren de vapor que travessa el terminal. S'executa quan l'atacant escriu sl per error de tecleig en lloc de ls."""
    _TREN = [
        r"      ====        ________                ___________",
        r"  _D _|  |_______/        \__I_I_____===__|_________|",
        r"   |(_)---  |   H\________/ |   |        =|___ ___|      _________________",
        r"   /     |  |   H  |  |     |   |         ||_| |_||     _|                \_____A",
        r"  |      |  |   H  |__--------------------| [___] |   =|                        |",
        r"  | ________|___H__/__|_____/[][]~\_______|       |   -|                        |",
        r"  |/ |   |-----------I_____I [][] []  D   |=======|____|________________________|_",
        r"__/ =| o |=-~~\  /~~\  /~~\  /~~\ ____Y___________|__|__________________________|",
        r" |/-=|___|=    ||    ||    ||    |_____/~\___/          |_D__D__D_|  |_D__D__D_|",
        r"  \_/      \O=====O=====O=====O_/      \_/               \_/   \_/    \_/   \_/ ",
    ]

    def executar(self):
        n = len(self._TREN)
        first = True
        try:
            for pad in range(55, -90, -3):
                if not first:
                    sys.stdout.write(f"\033[{n}A")
                for line in self._TREN:
                    if pad >= 0:
                        sys.stdout.write("\r" + " " * pad + line + "\033[K\n")
                    else:
                        clipped = line[min(-pad, len(line)):]
                        sys.stdout.write("\r" + clipped + "\033[K\n")
                sys.stdout.flush()
                time.sleep(0.07)
                first = False
        except KeyboardInterrupt:
            pass
        return ""

class ComandoId(ComandoHoneypot):
    """Mostra la identitat de l'usuari actual amb uid, gid i grups. Sempre retorna ubuntu amb els grups reals d'un servidor Ubuntu típic."""
    def executar(self):
        return "uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev)"

class ComandoUname(ComandoHoneypot):
    """Mostra informació del sistema operatiu. Suporta les flags -a, -r, -m, -n per revelar dades del kernel que poden interessar a l'atacant."""
    def executar(self):
        args_str = " ".join(self.args)
        if "-a" in args_str:
            return "Linux ubuntu-server 5.15.0-88-generic #98-Ubuntu SMP Mon Oct 2 15:18:56 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux"
        if "-r" in args_str:
            return "5.15.0-88-generic"
        if "-m" in args_str:
            return "x86_64"
        if "-n" in args_str:
            return "ubuntu-server"
        return "Linux"

class ComandoHostname(ComandoHoneypot):
    """Retorna el nom del servidor. Sempre respon ubuntu-server per mantenir la coherència amb el banner inicial de connexió."""
    def executar(self):
        return "ubuntu-server"

class ComandoPs(ComandoHoneypot):
    """Mostra la llista de processos en execució. Inclou processos com mysqld, nginx, apache2 i sshd per simular un servidor de producció real."""
    def executar(self):
        return (
            "USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n"
            "root           1  0.0  0.1  22548  3840 ?        Ss   Nov19   0:02 /sbin/init\n"
            "root           2  0.0  0.0      0     0 ?        S    Nov19   0:00 [kthreadd]\n"
            "root         892  0.0  0.2  72308  4608 ?        Ss   Nov19   0:00 /usr/sbin/sshd -D\n"
            "mysql        924  0.0  3.2 1836152 65820 ?       Ssl  Nov19   0:33 /usr/sbin/mysqld\n"
            "www-data    1204  0.0  0.5 428916 10240 ?        Ss   Nov19   0:00 nginx: master process\n"
            "root        1358  0.0  0.3 215612  6144 ?        Ss   Nov19   0:01 /usr/sbin/apache2 -k start\n"
            "root        2756  0.0  0.1  14976  2560 ?        Ss   14:22   0:00 sshd: ubuntu [priv]\n"
            "ubuntu      2891  0.0  0.1  14228  3248 pts/0    Ss   14:22   0:00 -bash\n"
            "ubuntu      2934  0.0  0.0  13344  1568 pts/0    R+   14:33   0:00 ps aux"
        )

class ComandoNetstat(ComandoHoneypot):
    """Mostra les connexions de xarxa actives. Inclou ports oberts (22, 80, 3306) i una connexió SSH establerta des d'una IP externa."""
    def executar(self):
        return (
            "Active Internet connections (servers and established)\n"
            "Proto Recv-Q Send-Q Local Address           Foreign Address         State\n"
            "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN\n"
            "tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN\n"
            "tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN\n"
            "tcp        0    256 192.168.1.45:22         192.168.1.10:54821      ESTABLISHED\n"
            "tcp6       0      0 :::80                   :::*                    LISTEN"
        )

class ComandoSs(ComandoNetstat):
    """Versió moderna de netstat. Hereta la mateixa sortida per simular el comportament equivalent."""
    pass

class ComandoEnv(ComandoHoneypot):
    """Mostra les variables d'entorn del sistema. Inclou credencials de base de dades i API keys fictícies per atreure l'atenció de l'atacant."""
    def executar(self):
        return (
            "SHELL=/bin/bash\n"
            "HOME=/home/ubuntu\n"
            "LOGNAME=ubuntu\n"
            "USER=ubuntu\n"
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
            "LANG=en_US.UTF-8\n"
            "DB_HOST=127.0.0.1\n"
            "DB_PASSWORD=Pr0duct10n#2025!\n"
            "API_KEY=sk-prod-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6\n"
            "MAIL_SMTP=smtp.company-internal.net\n"
            "MAIL_USER=noreply@company-internal.net\n"
            "MAIL_PASS=M4ilS3rv3r!2025"
        )

class ComandoDocker(ComandoHoneypot):
    """Simula un entorn Docker amb contenidors mysql i nginx en execució. Respon a ps, images, exec, run i logs amb sortides versemblants."""
    _CONTAINERS = (
        "CONTAINER ID   IMAGE          COMMAND                  CREATED        STATUS        PORTS                     NAMES\n"
        "a3f8c2b1d4e9   mysql:8.0      \"docker-entrypoint.s…\"   2 weeks ago    Up 2 weeks    127.0.0.1:3306->3306/tcp   db_prod\n"
        "7e9f1a2c3b5d   nginx:latest   \"/docker-entrypoint.…\"   2 weeks ago    Up 2 weeks    0.0.0.0:80->80/tcp         web_prod"
    )
    _IMAGES = (
        "REPOSITORY   TAG       IMAGE ID       CREATED        SIZE\n"
        "mysql        8.0       a3f8c2b1d4e9   2 weeks ago    544MB\n"
        "nginx        latest    7e9f1a2c3b5d   3 weeks ago    141MB"
    )

    def executar(self):
        if not self.args:
            return "Usage:  docker [OPTIONS] COMMAND\nA self-sufficient runtime for containers"
        sub = self.args[0]
        if sub == "ps":
            return self._CONTAINERS
        if sub == "images":
            return self._IMAGES
        if sub in ("exec", "run"):
            return "Error response from daemon: permission denied"
        if sub == "logs":
            name = self.args[1] if len(self.args) > 1 else ""
            return f"Error response from daemon: No such container: {name}"
        if sub == "inspect":
            return "Error response from daemon: permission denied"
        return f"docker: '{sub}' is not a docker command.\nSee 'docker --help'"

class ComandoSystemctl(ComandoHoneypot):
    """Simula la gestió de serveis systemd. Mostra serveis com apache2, mysql, nginx i ssh actius. Qualsevol intent de start/stop/restart retorna accés denegat."""
    _SERVICIOS = [
        ("apache2.service", "loaded active running", "The Apache HTTP Server"),
        ("cron.service",    "loaded active running", "Regular background program processing daemon"),
        ("docker.service",  "loaded active running", "Docker Application Container Engine"),
        ("mysql.service",   "loaded active running", "MySQL Community Server"),
        ("nginx.service",   "loaded active running", "A high performance web server"),
        ("ssh.service",     "loaded active running", "OpenBSD Secure Shell server"),
        ("ufw.service",     "loaded active exited",  "Uncomplicated firewall"),
    ]

    def executar(self):
        if not self.args:
            return "Failed to connect to bus: No such file or directory"
        sub = self.args[0]
        if sub in ("list-units", "list-unit-files"):
            lines = ["UNIT                      LOAD   ACTIVE  SUB      DESCRIPTION"]
            for name, status, desc in self._SERVICIOS:
                lines.append(f"  {name:<26} {status:<22} {desc}")
            lines.append(f"\n{len(self._SERVICIOS)} loaded units listed.")
            return "\n".join(lines)
        if sub == "status":
            svc = self.args[1] if len(self.args) > 1 else ""
            for name, status, desc in self._SERVICIOS:
                if svc.replace(".service", "") in name:
                    state = "active (running)" if "running" in status else "active (exited)"
                    pid = random.randint(800, 2000)
                    return (
                        f"● {name} - {desc}\n"
                        f"     Loaded: loaded (/lib/systemd/system/{name}; enabled)\n"
                        f"     Active: {state} since Thu 2026-01-15 08:15:23 UTC\n"
                        f"   Main PID: {pid} ({name.split('.')[0]})"
                    )
            return f"Unit {svc} could not be found."
        if sub in ("start", "stop", "restart", "enable", "disable"):
            tgt = self.args[1] if len(self.args) > 1 else ""
            return f"Failed to {sub} {tgt}: Access denied"
        return ""

class ComandoService(ComandoHoneypot):
    """Versió antiga de gestió de serveis. Respon a --status-all i a status de serveis individuals per simular un servidor Ubuntu real."""
    def executar(self):
        if not self.args:
            return "Usage: service <name> <command>"
        if "--status-all" in self.args:
            return (
                " [ + ]  apache2\n"
                " [ + ]  cron\n"
                " [ + ]  docker\n"
                " [ + ]  mysql\n"
                " [ + ]  nginx\n"
                " [ - ]  ufw\n"
                " [ + ]  ssh"
            )
        svc = self.args[0]
        cmd = self.args[1] if len(self.args) > 1 else "status"
        if cmd == "status":
            return f"{svc} is running."
        return "Access denied"

class ComandoMysql(ComandoHoneypot):
    """Captura intents d'accés a la base de dades. Si s'usa -p, demana contrasenya i la guarda a mysql_passwords.txt abans de retornar accés denegat."""
    def executar(self):
        user = "ubuntu"
        for i, a in enumerate(self.args):
            if a.startswith("-u") and len(a) > 2:
                user = a[2:]
            elif a == "-u" and i + 1 < len(self.args):
                user = self.args[i + 1]
        has_p = "-p" in self.args or any(a.startswith("-p") and len(a) > 2 for a in self.args)
        if has_p:
            try:
                pwd = getpass.getpass("Enter password: ")
                with open(os.path.join(ARCHIVOS_DIR, "mysql_passwords.txt"), "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.datetime.now().isoformat()}] user: {user} | password: {pwd}\n")
            except (KeyboardInterrupt, EOFError):
                print()
                return ""
            return f"ERROR 1045 (28000): Access denied for user '{user}'@'localhost' (using password: YES)"
        return f"ERROR 1045 (28000): Access denied for user '{user}'@'localhost' (using password: NO)"

class ComandoNc(ComandoHoneypot):
    """Simula netcat. Qualsevol intent de connexió espera 1.5 segons i retorna Connection refused per simular un port tancat real."""
    def executar(self):
        if not self.args:
            return "usage: nc [-46CDdFhklNnrStUuvZz] [-i interval] [-p source_port] [hostname] [port]"
        target = [a for a in self.args if not a.startswith("-")]
        if target:
            try:
                time.sleep(1.5)
            except KeyboardInterrupt:
                pass
            return "Ncat: Connection refused."
        return ""

class ComandoBase64(ComandoHoneypot):
    """Codifica o descodifica arxius en base64. Permet a l'atacant intentar exfiltrar contingut d'arxius virtuals en format codificat."""
    def executar(self):
        import base64 as _b64
        decode = "-d" in self.args or "--decode" in self.args
        fname = next((a for a in self.args if not a.startswith("-")), None)
        if not fname:
            return "Usage: base64 [OPTION]... [FILE]\nBase64 encode or decode FILE."
        abs_path = _norm(fname if fname.startswith("/") else self.cwd.rstrip("/") + "/" + fname)
        content = VIRTUAL_FS.get(abs_path, "")
        if not content:
            dirname = abs_path.rsplit("/", 1)[0]
            basename = abs_path.rsplit("/", 1)[1]
            if not any(e["name"] == basename for e in _extras.get(dirname, [])):
                return f"base64: {fname}: No such file or directory"
        if decode:
            try:
                decoded = _b64.b64decode(content.encode()).decode(errors="replace")
                return decoded if decoded else "(vacío)"
            except Exception:
                return "base64: invalid input"
        encoded = _b64.b64encode(content.encode()).decode()
        return encoded if encoded else "(archivo vacío)"

class ComandoCp(ComandoHoneypot):
    """Copia arxius dins del sistema de fitxers virtual. Actualitza tant VIRTUAL_FS com _extras perquè ls i cat reflecteixin el canvi."""
    def executar(self):
        paths = [a for a in self.args if not a.startswith("-")]
        if len(paths) < 2:
            return "cp: missing destination file operand"
        src, dst = paths[0], paths[-1]
        src_abs = _norm(src if src.startswith("/") else self.cwd.rstrip("/") + "/" + src)
        dst_abs = _norm(dst if dst.startswith("/") else self.cwd.rstrip("/") + "/" + dst)
        content = VIRTUAL_FS.get(src_abs)
        if content is not None:
            VIRTUAL_FS[dst_abs] = content
        dst_name = dst_abs.rsplit("/", 1)[1]
        dst_dir = dst_abs.rsplit("/", 1)[0]
        _add_entry(dst_dir, dst_name, size=len(content) if content else 0)
        return ""

class ComandoMv(ComandoHoneypot):
    """Mou o reanomena arxius dins del sistema de fitxers virtual. Elimina l'origen i crea la destinació mantenint el contingut."""
    def executar(self):
        paths = [a for a in self.args if not a.startswith("-")]
        if len(paths) < 2:
            return "mv: missing destination file operand"
        src, dst = paths[0], paths[-1]
        src_abs = _norm(src if src.startswith("/") else self.cwd.rstrip("/") + "/" + src)
        dst_abs = _norm(dst if dst.startswith("/") else self.cwd.rstrip("/") + "/" + dst)
        content = VIRTUAL_FS.pop(src_abs, None)
        if content is not None:
            VIRTUAL_FS[dst_abs] = content
        _ocultos.add(src_abs)
        dst_name = dst_abs.rsplit("/", 1)[1]
        dst_dir = dst_abs.rsplit("/", 1)[0]
        _add_entry(dst_dir, dst_name, size=len(content) if content else 0)
        return ""

class ComandoLast(ComandoHoneypot):
    """Mostra l'historial d'inicis de sessió SSH des de wtmp. Inclou connexions recents des d'IPs externes."""
    def executar(self):
        now  = datetime.datetime.now()
        prev = now - datetime.timedelta(hours=random.randint(14, 20))
        old  = now - datetime.timedelta(days=3)
        return (
            f"ubuntu   pts/0        192.168.1.10     {now.strftime('%a %b %d %H:%M')}   still logged in\n"
            f"ubuntu   pts/0        192.168.1.10     {prev.strftime('%a %b %d %H:%M')} - {(prev + datetime.timedelta(hours=8)).strftime('%H:%M')}  (08:12)\n"
            f"ubuntu   pts/0        10.0.0.5         {old.strftime('%a %b %d %H:%M')} - {(old + datetime.timedelta(minutes=47)).strftime('%H:%M')}  (00:47)\n"
            f"reboot   system boot  5.15.0-88-generic {now.strftime('%a %b %d')} 08:00 - {now.strftime('%H:%M')}  ({int((now - now.replace(hour=8, minute=0, second=0)).seconds/3600):02d}:{int(((now - now.replace(hour=8, minute=0, second=0)).seconds%3600)/60):02d})\n"
            f"\nwtmp begins Mon Jan 05 08:00:00 2026"
        )

class ComandoWho(ComandoHoneypot):
    """Mostra els usuaris connectats en aquest moment al sistema."""
    def executar(self):
        return f"ubuntu   pts/0        {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} (192.168.1.10)"

class ComandoW(ComandoHoneypot):
    """Versió estesa de who: mostra usuaris, uptime i ús de CPU."""
    def executar(self):
        now   = datetime.datetime.now()
        load  = round(random.uniform(0.01, 0.35), 2)
        h     = random.randint(4, 10)
        m     = random.randint(0, 59)
        return (
            f" {now.strftime('%H:%M:%S')} up {h}:{m:02d},  1 user,  load average: {load}, {round(load*0.9,2)}, {round(load*0.8,2)}\n"
            "USER     TTY      FROM             LOGIN@   IDLE JCPU   PCPU WHAT\n"
            f"ubuntu   pts/0    192.168.1.10     {now.strftime('%H:%M')}    0.00s  0.12s  0.01s -bash"
        )

class ComandoDf(ComandoHoneypot):
    """Mostra l'espai en disc de cada sistema de fitxers muntat al servidor."""
    def executar(self):
        return (
            "Filesystem      Size  Used Avail Use% Mounted on\n"
            "tmpfs           197M  1.4M  196M   1% /run\n"
            "/dev/sda1        20G  6.7G   12G  36% /\n"
            "tmpfs           985M     0  985M   0% /dev/shm\n"
            "tmpfs           5.0M     0  5.0M   0% /run/lock\n"
            "/dev/sda15      105M  6.1M   99M   6% /boot/efi\n"
            "tmpfs           197M  4.0K  197M   1% /run/user/1000"
        )

class ComandoFree(ComandoHoneypot):
    """Mostra l'ús de memòria RAM i swap en bytes i percentatge."""
    def executar(self):
        total = 2014464
        used  = random.randint(350000, 750000)
        free  = total - used
        avail = free - 50000
        return (
            "               total        used        free      shared  buff/cache   available\n"
            f"Mem:        {total:>10}  {used:>10}  {free:>10}        1476      256248     {avail:>10}\n"
            "Swap:        2097148           0     2097148"
        )

class ComandoUptime(ComandoHoneypot):
    """Mostra el temps que porta en marxa el sistema, usuaris i carga mitja."""
    def executar(self):
        now  = datetime.datetime.now()
        h    = random.randint(4, 12)
        m    = random.randint(0, 59)
        load = round(random.uniform(0.01, 0.35), 2)
        return (
            f" {now.strftime('%H:%M:%S')} up {h}:{m:02d},  1 user,  "
            f"load average: {load}, {round(load*0.9,2)}, {round(load*0.8,2)}"
        )

class ComandoCrontab(ComandoHoneypot):
    """Gestiona el crontab de l'usuari. -l mostra les tasques; -e obre l'editor vi."""
    def executar(self):
        if not self.args or "-l" in self.args:
            return VIRTUAL_FS.get("/etc/crontab", "no crontab for ubuntu")
        if "-e" in self.args:
            return ComandoVi(["/etc/crontab"], self.cwd).executar()
        return "usage: crontab [-u user] file\n       crontab [-u user] [-l | -r | -e] [-i]"

class ComandoAlias(ComandoHoneypot):
    """Mostra o defineix àlies de la sessió. Sense arguments, llista els àlies actius."""
    def executar(self):
        if not self.args:
            return (
                "alias l='ls -CF'\n"
                "alias la='ls -A'\n"
                "alias ll='ls -alF'\n"
                "alias grep='grep --color=auto'"
            )
        return ""

class ComandoWhoami(ComandoHoneypot):
    """Retorna l'usuari actual del sistema. Sempre imprimeix ubuntu ja que el honeypot simula estar autenticat com aquest usuari."""
    def executar(self):
        return "ubuntu"

class ComandoNoEncontrado(ComandoHoneypot):
    """Gestiona qualsevol comanda no reconeguda. Retorna el missatge d'error estàndard de bash per no revelar que es tracta d'un entorn simulat."""
    def __init__(self, nom, args, cwd="/home/ubuntu"):
        super().__init__(args, cwd)
        self.nom = nom

    def executar(self):
        return f"bash: {self.nom}: command not found"
