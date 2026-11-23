from dataclasses import dataclass


MAPA_SIMBOLOS = {"BTCUSDT": "BTC/USDT", "ETHUSDT": "ETH/USDT"}


@dataclass(frozen=True)
class Operacion:
    ts_ms: int
    simbolo: str
    precio: float
    cantidad: float


def normalizar_trade(msg: dict) -> Operacion:
    """Convierte un mensaje 'trade' del exchange al formato interno."""
    return Operacion(ts_ms=int(msg["T"]),
                     simbolo=MAPA_SIMBOLOS[msg["s"]],
                     precio=float(msg["p"]),
                     cantidad=float(msg["q"]))


def a_velas(operaciones, intervalo_ms: int = 60_000) -> list[dict]:
    """Agrupa operaciones en velas con intervalos [inicio, fin)."""
    velas: dict[int, dict] = {}
    for op in sorted(operaciones, key=lambda o: o.ts_ms):
        inicio = op.ts_ms - op.ts_ms % intervalo_ms
        v = velas.get(inicio)
        if v is None:
            velas[inicio] = {"inicio": inicio, "apertura": op.precio,
                             "maximo": op.precio, "minimo": op.precio,
                             "cierre": op.precio, "volumen": op.cantidad}
        else:
            v["maximo"] = max(v["maximo"], op.precio)
            v["minimo"] = min(v["minimo"], op.precio)
            v["cierre"] = op.precio
            v["volumen"] += op.cantidad
    return [velas[k] for k in sorted(velas)]
