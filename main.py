import os
import random
import time

from plataforma import almacen
from plataforma.arquitectura import Senal
from plataforma.cartera import BrokerSimulado, Cartera
from plataforma.observabilidad import Metricas, crear_logger
from plataforma.ordenes import Estado, Orden
from plataforma.parada import Control, Modo
from plataforma.riesgo import Limites, MotorRiesgoBasico


def simular(
    pasos: int = 200,
    semilla: int = 7,
    *,
    inicio_ms: int = 0,
    corrida: str = "sim",
) -> dict:
    if not isinstance(pasos, int) or isinstance(pasos, bool) or pasos < 0:
        raise ValueError("los pasos deben ser un entero no negativo")
    if not isinstance(inicio_ms, int) or isinstance(inicio_ms, bool) or inicio_ms < 0:
        raise ValueError("el instante de inicio debe ser un entero no negativo")
    if not corrida:
        raise ValueError("se requiere un identificador de ejecución")

    rng = random.Random(semilla)
    log, met = crear_logger(), Metricas()
    con = almacen.abrir(os.environ.get("RUTA_BD", ":memory:"))

    try:
        capital_inicial = 10_000.0
        cartera = Cartera(capital_inicial)
        broker = BrokerSimulado(cartera)
        riesgo = MotorRiesgoBasico(Limites(max_nocional=2_000))
        control = Control(Modo.SIMULACION)

        precio = 100.0
        curva = [cartera.patrimonio(precio)]

        for paso in range(pasos):
            ts = inicio_ms + paso * 1_000
            precio *= 1 + rng.gauss(0, 0.002)
            bid, ask = precio * 0.9995, precio * 1.0005

            lado = "compra" if cartera.posicion == 0 else "venta"

            if rng.random() < 0.9 or not control.puede("enviar_simulado"):
                curva.append(cartera.patrimonio(precio))
                continue

            cantidad = 10 if lado == "compra" else cartera.posicion
            senal = Senal("BTC/USDT", lado, cantidad, ts)

            # Pérdida no realizada de la sesión respecto al capital inicial.
            # No representa un cálculo contable por día natural.
            patrimonio_actual = cartera.patrimonio(precio)
            perdida_sesion = max(0.0, capital_inicial - patrimonio_actual)

            ok, motivo = riesgo.evaluar(
                senal,
                precio,
                ahora_ms=ts,
                efectivo=cartera.efectivo,
                exposicion=cartera.posicion * precio,
                perdida_diaria=perdida_sesion,
            )

            if not ok:
                met.incrementar("rechazadas_por_riesgo")
                log.info(
                    "señal bloqueada",
                    extra={"contexto": {"motivo": motivo}},
                )
                curva.append(cartera.patrimonio(precio))
                continue

            orden = Orden(f"{corrida}-{paso}", lado, cantidad)

            almacen.registrar_orden(
                con,
                orden.id_cliente,
                senal.simbolo,
                lado,
                cantidad,
                orden.estado.value,
                ts,
            )

            orden.mover(Estado.ENVIADA)
            orden.mover(Estado.ACEPTADA)

            fill = broker.ejecutar(lado, cantidad, bid, ask)
            id_fill = f"{corrida}-fill-{paso}"

            orden.registrar_ejecucion(fill["cantidad"], id_fill)

            almacen.registrar_ejecucion(
                con,
                orden.id_cliente,
                id_fill,
                fill["cantidad"],
                fill["precio"],
                fill["comision"],
                ts,
            )

            almacen.cambiar_estado(
                con,
                orden.id_cliente,
                orden.estado.value,
            )

            met.incrementar("ordenes_ejecutadas")
            curva.append(cartera.patrimonio(precio))

        return {
            "curva": curva,
            "metricas": met.contadores,
            "posiciones": almacen.posiciones(con),
        }

    finally:
        con.close()


if __name__ == "__main__":
    pasos = 200
    ahora_ms = int(time.time() * 1000)

    resultado = simular(
        pasos,
        inicio_ms=ahora_ms - pasos * 1_000,
        corrida=f"corrida{ahora_ms}",
    )

    print(
        "patrimonio final:",
        round(resultado["curva"][-1], 2),
        dict(resultado["metricas"]),
    )