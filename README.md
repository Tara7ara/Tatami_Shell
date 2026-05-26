# Tatami Honeypot

Proyecto de la asignatura Análisis y Diseño de Algoritmos Avanzados  

Honeypot de terminal Linux simulado. Captura y analiza el comportamiento de un atacante que cree haber accedido a un servidor Ubuntu real.

---

## Cómo ejecutarlo

Requiere Python 3.10 o superior. No necesita librerías externas.

**Terminal A — el honeypot:**
```
python main.py
```

**Terminal B — el monitor en tiempo real (opcional):**
```
python monitor.py
```

## Qué hace

El atacante ve un terminal Ubuntu 22.04 completamente funcional. Puede navegar directorios, leer archivos, ejecutar comandos, intentar escalar privilegios y exfiltrar datos. Todo es simulado: ningún comando toca el sistema real.

Mientras tanto, el sistema registra cada acción, captura credenciales introducidas y clasifica automáticamente la fase del ataque.


## Arquitectura

El proyecto se divide en cuatro módulos:

**main.py** — Shell principal. Gestiona el bucle de entrada, resuelve aliases, expande variables de entorno (`$VAR`), procesa pipes (`|`), cadenas (`&&`, `;`) y redirecciones (`>`). Instancia los comandos y actualiza la máquina de estados.

**comandos.py** — Contiene todas las clases de comandos, el sistema de archivos virtual (`VIRTUAL_FS`, `VIRTUAL_DIRS`) y los datos estáticos de directorios (`LS_DATA`). Cada comando hereda de `ComandoHoneypot` e implementa su propio método `executar()`.

**grafo.py** — Máquina de estados implementada como grafo dirigido. Define seis fases de ataque y las transiciones entre ellas según los comandos ejecutados.

**patrons.py** — Detección de patrones de ataque mediante búsqueda recursiva de subsecuencias en el historial de comandos.

**monitor.py** — Monitor independiente que lee los logs en tiempo real, detecta la fase actual y muestra credenciales capturadas y actividad de archivos. Al cerrarlo genera un informe de evidencias.

## Sistema de archivos virtual

El honeypot simula la siguiente estructura de directorios:

```
/home/ubuntu/
    credentials.bak --> contraseñas de BD, SSH y API tokens
    .bash_history --> historial con comandos sospechosos
    .ssh/id_rsa --> clave privada SSH
    .ssh/known_hosts
    server_config/
        nginx.conf
        app.conf --> cadena de conexión a BD con credenciales
    backups/
        db_backup.sql.gz

/etc/
    crontab --> cronjob sospechoso cada 5 minutos
    passwd / shadow
    hosts

/var/log/
    auth.log --> intentos de sudo y logins SSH
    syslog

/proc/
    version / cpuinfo
```

Los archivos son accesibles con `cat`, `grep`, `tail`, `head` y `base64`. Los directorios son navegables con `cd` y `ls`.

## Comandos disponibles

| Categoría | Comandos |
|---|---|
| Navegación | `ls`, `ll`, `la`, `cd`, `pwd`, `find` |
| Lectura | `cat`, `head`, `tail`, `grep`, `base64` |
| Edición | `vi`, `vim`, `nano`, `touch`, `mkdir`, `rm`, `cp`, `mv` |
| Sistema | `whoami`, `id`, `uname`, `hostname`, `uptime`, `env`, `ps`, `df`, `free` |
| Red | `ip`, `ifconfig`, `netstat`, `ss`, `ssh`, `nc`, `wget`, `curl` |
| Sesión | `who`, `w`, `last`, `history`, `alias` |
| Servicios | `systemctl`, `service`, `docker`, `mysql`, `crontab` |
| Privilegios | `sudo`, `chmod` |
| Otros | `echo`, `python3`, `apt`, `cowsay`, `sl` |

Soporta pipes (`|`), encadenado (`&&`, `;`), redirección (`>`), expansión de variables (`$VAR`) y tab completion.

## Fases del ataque (grafo de estados)

| Fase | Comandos que la activan |
|---|---|
| Reconeixament | `whoami`, `id`, `uname`, `hostname` |
| Enumeració | `ls`, `ps`, `find`, `netstat`, `ss`, `env`, `history`, `docker`, `systemctl` |
| Escalada | `sudo`, `chmod`, `bash`, `python3` |
| Lectura de dades | `cat`, `grep`, `vi`, `base64`, `mysql` |
| Exfiltració | `wget`, `curl`, `nc`, `ssh` |

## Capturas forenses

Todo lo que hace el atacante queda guardado en la carpeta `archivos/`:

```
archivos/
    LOG1.log --> historial completo con timestamps
    sudo_passwords.txt --> contraseñas introducidas en sudo
    mysql_passwords.txt --> contraseñas introducidas en mysql
    downloads/ --> archivos descargados con wget
    editados/ --> archivos modificados con vi
    creados/ --> archivos creados con touch
    eliminados/ --> archivos borrados con rm
    redireccionados/ --> archivos creados con >
    Evidencia_LOG1.txt --> informe generado al cerrar el monitor
```

## Monitor en tiempo real

`monitor.py` se ejecuta en una terminal separada y se refresca cada 2 segundos. Muestra:

- Fase de ataque detectada automáticamente
- Credenciales capturadas en tiempo real
- Actividad sobre archivos
- Comandos sospechosos con timestamp
- Últimos 10 comandos ejecutados

Al cerrarlo con Ctrl+C genera `Evidencia_LOGX.txt` con el informe completo de la sesión.

## Complejidad algorítmica

| Operación | Complejidad |
|---|---|
| Búsqueda de comando en `binarios` | O(1) — dict hash |
| Cambio de estado en el grafo | O(k) — k = número de transiciones del nodo |
| Detección de patrón en `patrons.py` | O(n·m) — n comandos, m longitud del patrón |
| Recorrido del grafo (informe) | O(V+E) |
| Construcción de `ls -l` | O(e) — e = entradas extras del directorio |
