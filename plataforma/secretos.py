import logging
import os
import re


def leer_credenciales(prefijo: str = "EXCHANGE") -> tuple[str, str]:
    clave = os.environ.get(f"{prefijo}_API_KEY")
    secreto = os.environ.get(f"{prefijo}_API_SECRET")
    if not clave or not secreto:
        raise RuntimeError(f"faltan {prefijo}_API_KEY / {prefijo}_API_SECRET")
    return clave, secreto


class FiltroSecretos(logging.Filter):
    """Redacción básica de claves en mensajes; no sustituye una política de logging segura."""
    PATRON = re.compile(r"(?i)(api[_-]?key|api[_-]?secret|secret|signature)(\s*[\"']?\s*[:=]\s*[\"']?\s*)([^&\s,\"']+)")
    def filter(self, record: logging.LogRecord) -> bool:
        mensaje = self.PATRON.sub(r"\1\2***", record.getMessage())
        record.msg, record.args = mensaje, ()
        return True
