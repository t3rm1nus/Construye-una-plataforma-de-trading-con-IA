from dataclasses import dataclass
import math
from plataforma.arquitectura import Senal


@dataclass
class Limites:
    max_nocional: float = 1_000.0
    max_exposicion: float = 5_000.0
    max_perdida_diaria: float = 200.0
    max_antiguedad_ms: int = 2_000
    def __post_init__(self) -> None:
        positivos = (self.max_nocional, self.max_exposicion)
        if not all(math.isfinite(v) and v > 0 for v in positivos):
            raise ValueError("los límites de nocional y exposición deben ser finitos y positivos")
        if not math.isfinite(self.max_perdida_diaria) or self.max_perdida_diaria < 0:
            raise ValueError("el límite de pérdida diaria debe ser finito y no negativo")
        if (not isinstance(self.max_antiguedad_ms, int)
                or isinstance(self.max_antiguedad_ms, bool)
                or self.max_antiguedad_ms < 0):
            raise ValueError("el límite de antigüedad de la señal debe ser un entero no negativo")


class MotorRiesgoBasico:
    def __init__(self, limites: Limites):
        self.l = limites
    def evaluar(self, senal: Senal, precio: float, *, ahora_ms: int,
                efectivo: float, exposicion: float,
                perdida_diaria: float) -> tuple[bool, str]:
        if senal.lado not in {"compra", "venta"}:
            return False, "lado no válido"
        valores = (senal.cantidad, precio, efectivo, exposicion, perdida_diaria)
        if not all(math.isfinite(v) for v in valores):
            return False, "parámetros no finitos"
        if senal.cantidad <= 0 or precio <= 0 or efectivo < 0 or exposicion < 0 or perdida_diaria < 0:
            return False, "parámetros fuera de rango"
        edad = ahora_ms - senal.ts_ms
        if edad < 0:
            return False, "marca temporal futura"
        if edad > self.l.max_antiguedad_ms:
            return False, "señal obsoleta"
        if perdida_diaria >= self.l.max_perdida_diaria:
            return False, "pérdida diaria superada"
        nocional = senal.cantidad * precio
        if nocional > self.l.max_nocional:
            return False, "tamaño superior al máximo"
        if senal.lado == "compra":
            if nocional > efectivo:
                return False, "saldo insuficiente"
            if exposicion + nocional > self.l.max_exposicion:
                return False, "exposición agregada excedida"
        elif nocional > exposicion + 1e-9:
            return False, "venta superior a la exposición disponible"
        return True, "aprobada"
