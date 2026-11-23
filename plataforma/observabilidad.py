import json
import logging
import math
import time
from collections import Counter


class FormatoJson(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        datos = {"ts": round(time.time(), 3), "nivel": record.levelname,
                 "mensaje": record.getMessage()}
        datos.update(getattr(record, "contexto", {}))
        return json.dumps(datos, ensure_ascii=False)


def crear_logger(nombre: str = "plataforma") -> logging.Logger:
    log = logging.getLogger(nombre)
    if not log.handlers:
        h = logging.StreamHandler()
        h.setFormatter(FormatoJson())
        log.addHandler(h)
        log.setLevel(logging.INFO)
    return log


class Metricas:
    def __init__(self):
        self.contadores: Counter = Counter()
        self.latencias_ms: list[float] = []
    def incrementar(self, nombre: str, n: int = 1) -> None:
        if not nombre or not isinstance(n, int) or isinstance(n, bool) or n < 0:
            raise ValueError("se requieren un nombre de contador y un incremento entero no negativo")
        self.contadores[nombre] += n
    def observar_latencia(self, ms: float) -> None:
        if not math.isfinite(ms) or ms < 0:
            raise ValueError("la latencia debe ser finita y no negativa")
        self.latencias_ms.append(ms)
    def p95(self) -> float:
        if not self.latencias_ms:
            return 0.0
        orden = sorted(self.latencias_ms)
        indice = max(0, math.ceil(0.95 * len(orden)) - 1)
        return orden[indice]
