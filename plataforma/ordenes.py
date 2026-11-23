from enum import Enum
import math


class Estado(Enum):
    CREADA = "creada"
    ENVIADA = "enviada"
    ACEPTADA = "aceptada"
    PARCIAL = "parcialmente ejecutada"
    EJECUTADA = "ejecutada"
    CANCELACION_PENDIENTE = "cancelación pendiente"
    CANCELADA = "cancelada"
    RECHAZADA = "rechazada"
E = Estado
TRANSICIONES = {
    E.CREADA: {E.ENVIADA, E.RECHAZADA},
    E.ENVIADA: {E.ACEPTADA, E.RECHAZADA},
    E.ACEPTADA: {E.PARCIAL, E.EJECUTADA, E.CANCELACION_PENDIENTE, E.CANCELADA},
    E.PARCIAL: {E.PARCIAL, E.EJECUTADA, E.CANCELACION_PENDIENTE, E.CANCELADA},
    E.CANCELACION_PENDIENTE: {E.CANCELADA, E.PARCIAL, E.EJECUTADA},
    E.EJECUTADA: set(), E.CANCELADA: set(), E.RECHAZADA: set(),
}


class TransicionInvalida(Exception):
    pass


class Orden:
    def __init__(self, id_cliente: str, lado: str, cantidad: float):
        if lado not in {"compra", "venta"} or not math.isfinite(cantidad) or cantidad <= 0:
            raise ValueError("lado o cantidad de orden no válidos")
        self.id_cliente, self.lado, self.cantidad = id_cliente, lado, cantidad
        self.ejecutada = 0.0
        self.ids_ejecucion: set[str] = set()
        self.estado = Estado.CREADA
    def mover(self, nuevo: Estado) -> None:
        if nuevo not in TRANSICIONES[self.estado]:
            raise TransicionInvalida(f"{self.estado.value} -> {nuevo.value}")
        self.estado = nuevo
    def registrar_ejecucion(self, cantidad: float, id_ejecucion: str) -> bool:
        """Deduplica por ID de ejecución; True solo si se aplica por primera vez."""
        if not id_ejecucion:
            raise ValueError("se requiere el identificador de ejecución del proveedor")
        if id_ejecucion in self.ids_ejecucion:
            return False
        if self.estado not in (Estado.ACEPTADA, Estado.PARCIAL, Estado.CANCELACION_PENDIENTE):
            raise TransicionInvalida("ejecución en un estado no ejecutable")
        if not math.isfinite(cantidad) or cantidad <= 0:
            raise ValueError("cantidad ejecutada no válida")
        if self.ejecutada + cantidad > self.cantidad + 1e-12:
            raise ValueError("ejecución superior a la cantidad pedida")
        total = self.ejecutada + cantidad
        nuevo = Estado.EJECUTADA if total >= self.cantidad - 1e-12 else Estado.PARCIAL
        if nuevo not in TRANSICIONES[self.estado]:
            raise TransicionInvalida(f"{self.estado.value} -> {nuevo.value}")
        self.ejecutada = total
        self.ids_ejecucion.add(id_ejecucion)
        self.mover(nuevo)
        return True
