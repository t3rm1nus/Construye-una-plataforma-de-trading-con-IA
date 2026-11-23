import hashlib
import hmac
import time
from urllib.parse import urlencode


def firmar(params: dict, secreto: str, ahora_ms: int | None = None) -> dict:
    """Añade marca temporal y firma HMAC-SHA256 a los parámetros."""
    ts = ahora_ms if ahora_ms is not None else int(time.time() * 1000)
    params = {**params, "timestamp": ts}
    cuerpo = urlencode(params)
    firma = hmac.new(secreto.encode(), cuerpo.encode(),
                     hashlib.sha256).hexdigest()
    return {**params, "signature": firma}


def id_cliente(estrategia: str, simbolo: str, ts_decision_ms: int) -> str:
    """Identificador determinista: se genera una vez y se reutiliza."""
    return f"{estrategia}-{simbolo.replace('/', '')}-{ts_decision_ms}"
