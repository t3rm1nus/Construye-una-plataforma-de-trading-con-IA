from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Senal:
    simbolo: str
    lado: str            # "compra" o "venta"
    cantidad: float
    ts_ms: int = 0


class FuenteDatos(Protocol):
    def ultimo_precio(self, simbolo: str) -> float: ...


class Estrategia(Protocol):
    def decidir(self, precio: float) -> Senal | None: ...


class MotorRiesgo(Protocol):
    def evaluar(self, senal: Senal, precio: float, *, ahora_ms: int,
                efectivo: float, exposicion: float,
                perdida_diaria: float) -> tuple[bool, str]: ...


class Ejecutor(Protocol):
    def enviar(self, senal: Senal, precio: float) -> str: ...


def ciclo(datos: FuenteDatos, estrategia: Estrategia,
          riesgo: MotorRiesgo, ejecutor: Ejecutor, simbolo: str, *,
          ahora_ms: int, efectivo: float, exposicion: float,
          perdida_diaria: float) -> str:
    """Un ciclo: dato -> decisión -> evaluación de riesgo -> ejecución."""
    precio = datos.ultimo_precio(simbolo)
    senal = estrategia.decidir(precio)
    if senal is None:
        return "sin señal"
    ok, motivo = riesgo.evaluar(senal, precio, ahora_ms=ahora_ms,
                              efectivo=efectivo, exposicion=exposicion,
                              perdida_diaria=perdida_diaria)
    if not ok:
        return f"bloqueada por riesgo: {motivo}"
    return ejecutor.enviar(senal, precio)
