import asyncio
import random


async def productor(cola: asyncio.Queue, mensajes) -> None:
    for mensaje in mensajes:
        await cola.put(mensaje)
    await cola.put(None)  # marca de fin


async def consumidor(cola: asyncio.Queue, procesar) -> None:
    while True:
        mensaje = await cola.get()
        try:
            if mensaje is None:
                return
            resultado = procesar(mensaje)
            if hasattr(resultado, "__await__"):
                await resultado
        finally:
            cola.task_done()


async def conectar_con_reintentos(abrir_flujo, procesar, max_intentos=5,
                                  espera_inicial=1.0, tope=30.0) -> None:
    if max_intentos < 1:
        raise ValueError("max_intentos debe ser >= 1")
    espera, fallos = espera_inicial, 0
    while True:
        recibio = False
        try:
            async for mensaje in abrir_flujo():
                recibio = True
                resultado = procesar(mensaje)
                if hasattr(resultado, "__await__"):
                    await resultado
            raise ConnectionError("el flujo terminó inesperadamente")
        except (ConnectionError, asyncio.TimeoutError):
            if recibio:                      # la conexión funcionó: se empieza de nuevo
                fallos, espera = 0, espera_inicial
            fallos += 1
            if fallos >= max_intentos:
                raise RuntimeError("no se pudo restablecer la conexión")
            await asyncio.sleep(random.uniform(0, espera))
            espera = min(espera * 2, tope)
