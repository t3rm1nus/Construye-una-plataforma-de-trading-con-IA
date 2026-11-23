import math


class Cartera:
    def __init__(self, efectivo: float):
        if not math.isfinite(efectivo) or efectivo < 0:
            raise ValueError("efectivo inicial no válido")
        self.efectivo = efectivo
        self.posicion = 0.0
        self.precio_medio = 0.0
    def aplicar(self, lado: str, cantidad: float, precio: float,
                comision: float) -> None:
        if lado not in {"compra", "venta"}:
            raise ValueError("lado debe ser compra o venta")
        if not all(math.isfinite(x) for x in (cantidad, precio, comision)):
            raise ValueError("cantidad, precio y comisión deben ser finitos")
        if cantidad <= 0 or precio <= 0 or comision < 0:
            raise ValueError("cantidad/precio deben ser positivos y comisión no negativa")
        if lado == "compra":
            coste = cantidad * precio + comision
            if coste > self.efectivo + 1e-12:
                raise ValueError("saldo insuficiente")
            total = self.posicion + cantidad
            self.precio_medio = (self.posicion * self.precio_medio
                                 + cantidad * precio) / total
            self.posicion = total
            self.efectivo -= coste
        else:
            if cantidad > self.posicion + 1e-12:
                raise ValueError("posición insuficiente")
            self.posicion -= cantidad
            self.efectivo += cantidad * precio - comision
            if self.posicion < 1e-12:
                self.posicion, self.precio_medio = 0.0, 0.0
    def patrimonio(self, precio: float) -> float:
        if not math.isfinite(precio) or precio < 0:
            raise ValueError("precio de valoración no válido")
        return self.efectivo + self.posicion * precio


class BrokerSimulado:
    def __init__(self, cartera: Cartera, comision: float = 0.001,
                 deslizamiento_pb: float = 2.0):
        if not math.isfinite(comision) or comision < 0:
            raise ValueError("comisión no válida")
        if not math.isfinite(deslizamiento_pb) or deslizamiento_pb < 0:
            raise ValueError("deslizamiento no válido")
        self.cartera = cartera
        self.comision = comision
        self.deslizamiento = deslizamiento_pb / 10_000
    def ejecutar(self, lado: str, cantidad: float,
                 bid: float, ask: float) -> dict:
        """Compra al ask, vende al bid, más deslizamiento y comisión."""
        if lado not in {"compra", "venta"}:
            raise ValueError("lado debe ser compra o venta")
        if not all(math.isfinite(x) and x > 0 for x in (bid, ask)) or bid > ask:
            raise ValueError("cotización bid/ask no válida")
        if lado == "compra":
            precio = ask * (1 + self.deslizamiento)
        else:
            precio = bid * (1 - self.deslizamiento)
        comision = cantidad * precio * self.comision
        self.cartera.aplicar(lado, cantidad, precio, comision)
        return {"lado": lado, "cantidad": cantidad,
                "precio": precio, "comision": comision}
