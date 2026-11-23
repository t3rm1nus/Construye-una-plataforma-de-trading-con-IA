import math
import random
import time


class ErrorTransitorio(Exception):
    """Fallo de red, 5xx o límite de tasa: se puede reintentar."""


class ErrorPermanente(Exception):
    """Credenciales o parámetros inválidos: reintentar no ayuda."""


def espera_jitter(intento: int, base: float = 0.5, tope: float = 30.0) -> float:
    if not isinstance(intento, int) or isinstance(intento, bool) or intento < 0:
        raise ValueError("el intento debe ser un entero no negativo")
    if not all(math.isfinite(v) and v > 0 for v in (base, tope)):
        raise ValueError("la base y el tope de la espera deben ser finitos y positivos")
    return random.uniform(0, min(tope, base * 2 ** intento))


def reintentar(fn, max_intentos: int = 5, dormir=time.sleep):
    if max_intentos < 1:
        raise ValueError("max_intentos debe ser >= 1")
    for intento in range(max_intentos):
        try:
            return fn()
        except ErrorPermanente:
            raise  # no se reintenta
        except ErrorTransitorio:
            if intento == max_intentos - 1:
                raise
            dormir(espera_jitter(intento))


def enviar_idempotente(registro: dict, id_cliente: str, enviar):
    """Ejemplo en memoria; en producción, usar almacenamiento durable y conciliación."""
    if id_cliente in registro:
        return registro[id_cliente]
    resultado = reintentar(lambda: enviar(id_cliente))
    registro[id_cliente] = resultado
    return resultado
