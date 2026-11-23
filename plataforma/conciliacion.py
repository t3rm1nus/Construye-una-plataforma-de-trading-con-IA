import math


def conciliar(local: dict[str, float], remoto: dict[str, float],
              tolerancia: float = 1e-9) -> dict[str, float]:
    """Devuelve las diferencias remoto - local por instrumento."""
    if not math.isfinite(tolerancia) or tolerancia < 0:
        raise ValueError("la tolerancia debe ser finita y no negativa")
    if not all(math.isfinite(v) for v in (*local.values(), *remoto.values())):
        raise ValueError("las posiciones deben ser finitas")
    difs = {}
    for simbolo in set(local) | set(remoto):
        d = remoto.get(simbolo, 0.0) - local.get(simbolo, 0.0)
        if abs(d) > tolerancia:
            difs[simbolo] = d
    return difs


def estado_de_arranque(difs: dict[str, float]) -> str:
    """Sin diferencias se opera; con diferencias se bloquea y se revisa."""
    return "operativo" if not difs else "bloqueado"
