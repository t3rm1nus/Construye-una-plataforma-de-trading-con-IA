import math


def metricas(curva_equity: list[float], enviadas: int, rechazadas: int) -> dict:
    if not curva_equity or not all(math.isfinite(v) and v > 0 for v in curva_equity):
        raise ValueError("la curva de equity debe ser no vacía, finita y positiva")
    if enviadas < 0 or rechazadas < 0 or rechazadas > enviadas:
        raise ValueError("contadores de órdenes no válidos")
    pico, max_dd = curva_equity[0], 0.0
    for v in curva_equity:
        pico = max(pico, v)
        max_dd = max(max_dd, (pico - v) / pico)
    return {"max_drawdown": max_dd,
            "tasa_rechazo": rechazadas / enviadas if enviadas else 0.0,
            "retorno": curva_equity[-1] / curva_equity[0] - 1,
            "ordenes_enviadas": enviadas}


def evaluar(m: dict, criterios: dict) -> list[str]:
    """Devuelve la lista de criterios incumplidos (vacía = aceptado)."""
    fallos = []
    if m["max_drawdown"] > criterios["max_drawdown"]:
        fallos.append("drawdown máximo superado")
    if m["tasa_rechazo"] > criterios["max_tasa_rechazo"]:
        fallos.append("demasiados rechazos")
    if m.get("ordenes_enviadas", 0) < criterios.get("min_ordenes", 0):
        fallos.append("muy pocas órdenes")
    return fallos
