PATRONS = {
    "Reconocimiento básico": ["whoami", "ls"],
    "Reconocimiento completo": ["whoami", "id", "uname", "ps"],
    "Enumeración de red": ["netstat", "ss"],
    "Análisis de servicios": ["ps", "systemctl"],
    "Búsqueda de credenciales": ["find", "cat"],
    "Lectura de credenciales": ["cat", "credentials"],
    "Acceso a base de datos": ["ps", "mysql"],
    "Intento escalada privilegios": ["sudo", "chmod"],
    "Escalada + lectura": ["sudo", "cat"],
    "Exfiltración por netcat": ["cat", "nc"],
    "Exfiltración web": ["cat", "wget"],
    "Reverse shell básico": ["bash", "nc"],
    "Reverse shell python": ["python3", "nc"],
    "Reconocimiento + exfiltración": ["whoami", "find", "wget"],
}

def caçar_patro(historial, seq_atac, i_hist=0, i_seq=0):
    if i_seq == len(seq_atac): return True
    if i_hist == len(historial): return False

    if seq_atac[i_seq] in historial[i_hist]:
        return caçar_patro(historial, seq_atac, i_hist + 1, i_seq + 1)

    return caçar_patro(historial, seq_atac, i_hist + 1, i_seq)

def escanear_logs(logs):
    return [nom for nom, seq in PATRONS.items() if caçar_patro(logs, seq)]