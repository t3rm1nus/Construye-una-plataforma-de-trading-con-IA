import pytest
from plataforma.cartera import BrokerSimulado, Cartera
from plataforma.ordenes import Estado, Orden, TransicionInvalida
from plataforma.reintentos import (ErrorPermanente, ErrorTransitorio,
                                   enviar_idempotente, reintentar)
from plataforma.parada import Control, Modo
from plataforma import almacen


def test_compra_y_venta_sin_costes_conserva_el_patrimonio():
    c = Cartera(1_000)
    c.aplicar("compra", 2, 100, 0)
    c.aplicar("venta", 2, 100, 0)
    assert c.patrimonio(100) == pytest.approx(1_000) and c.posicion == 0


def test_el_spread_y_la_comision_cuestan_dinero():
    c = Cartera(1_000)
    b = BrokerSimulado(c)
    b.ejecutar("compra", 1, bid=99.9, ask=100.1)
    b.ejecutar("venta", 1, bid=99.9, ask=100.1)
    assert c.patrimonio(100) < 1_000


def test_lado_invalido_no_se_interpreta_como_venta():
    c = Cartera(1_000)
    with pytest.raises(ValueError):
        c.aplicar("short", 1, 100, 0)
    assert c.efectivo == 1_000 and c.posicion == 0


def test_orden_rechazada_es_terminal():
    o = Orden("a", "compra", 1)
    o.mover(Estado.ENVIADA); o.mover(Estado.RECHAZADA)
    with pytest.raises(TransicionInvalida):
        o.mover(Estado.ACEPTADA)


def test_ejecucion_tardia_tras_cancelar_se_detecta():
    o = Orden("a", "compra", 1)
    o.mover(Estado.ENVIADA); o.mover(Estado.ACEPTADA); o.mover(Estado.CANCELADA)
    with pytest.raises(TransicionInvalida):
        o.registrar_ejecucion(0.1, "fill-late")
    assert o.ejecutada == 0


def test_ejecucion_duplicada_no_suma_dos_veces():
    o = Orden("a", "compra", 1)
    o.mover(Estado.ENVIADA); o.mover(Estado.ACEPTADA)
    assert o.registrar_ejecucion(0.4, "fill-1")
    assert not o.registrar_ejecucion(0.4, "fill-1")
    assert o.ejecutada == pytest.approx(0.4)


def test_ejecucion_en_base_de_datos_es_idempotente():
    con = almacen.abrir(":memory:")
    almacen.registrar_orden(con, "o1", "BTC/USDT", "compra", 1, "aceptada", 1)
    assert almacen.registrar_ejecucion(con, "o1", "fill-1", 0.4, 100, 0, 2)
    assert not almacen.registrar_ejecucion(con, "o1", "fill-1", 0.4, 100, 0, 2)
    assert almacen.posiciones(con)["BTC/USDT"] == pytest.approx(0.4)
    con.close()


def test_reintentos_y_idempotencia_en_memoria():
    llamadas = []
    def inestable(cid):
        llamadas.append(cid)
        if len(llamadas) < 3:
            raise ErrorTransitorio()
        return "ok"
    registro = {}
    r = enviar_idempotente(registro, "x1", inestable)
    assert r == "ok" and len(llamadas) == 3
    assert enviar_idempotente(registro, "x1", inestable) == "ok"
    assert len(llamadas) == 3
    with pytest.raises(ErrorPermanente):
        reintentar(lambda: (_ for _ in ()).throw(ErrorPermanente()),
                   dormir=lambda s: None)


def test_parada_de_emergencia_bloquea_antes_de_cancelar():
    c = Control(Modo.OPERATIVO)
    visto = []
    def cancelar(id_):
        visto.append(c.modo)
        if id_ == "malo":
            raise RuntimeError
    fallidas = c.parada_emergencia(["a", "malo"], cancelar)
    assert visto == [Modo.BLOQUEADO, Modo.BLOQUEADO] and fallidas == ["malo"]
    assert not c.puede("enviar") and c.puede("cancelar")


def test_limites_rechazan_configuracion_invalida():
    from plataforma.riesgo import Limites
    with pytest.raises(ValueError):
        Limites(max_nocional=float("nan"))
    with pytest.raises(ValueError):
        Limites(max_antiguedad_ms=-1)


def test_motor_riesgo_rechaza_senal_obsoleta():
    from plataforma.riesgo import Limites, MotorRiesgoBasico
    from plataforma.arquitectura import Senal
    motor = MotorRiesgoBasico(Limites(max_antiguedad_ms=100))
    senal = Senal("BTC/USDT", "compra", 1, ts_ms=0)
    ok, motivo = motor.evaluar(
        senal, 100, ahora_ms=101, efectivo=1_000,
        exposicion=0, perdida_diaria=0)
    assert not ok and motivo == "señal obsoleta"


def test_conciliacion_detecta_diferencias_y_rechaza_nan():
    import math
    from plataforma.conciliacion import conciliar
    assert conciliar({"BTC/USDT": 1.0}, {"BTC/USDT": 1.5}) == {"BTC/USDT": 0.5}
    with pytest.raises(ValueError):
        conciliar({"BTC/USDT": math.nan}, {})


def test_metricas_rechazan_incrementos_invalidos():
    from plataforma.observabilidad import Metricas
    met = Metricas()
    met.incrementar("ordenes", 2)
    assert met.contadores["ordenes"] == 2
    with pytest.raises(ValueError):
        met.incrementar("ordenes", -1)


def test_velas_conservan_orden_y_agregan_ohlcv():
    from plataforma.mercado import Operacion, a_velas
    ops = [Operacion(2_000, "BTC/USDT", 105.0, 2.0),
           Operacion(1_000, "BTC/USDT", 100.0, 1.0)]
    vela = a_velas(ops, intervalo_ms=60_000)[0]
    assert (vela["apertura"], vela["maximo"], vela["minimo"], vela["cierre"]) == (
        100.0, 105.0, 100.0, 105.0)
    assert vela["volumen"] == 3.0


def test_firma_y_identificador_son_deterministas():
    from plataforma.firma import firmar, id_cliente
    primero = firmar({"symbol": "BTCUSDT"}, "secret", ahora_ms=123)
    segundo = firmar({"symbol": "BTCUSDT"}, "secret", ahora_ms=123)
    assert primero == segundo
    assert len(primero["signature"]) == 64
    assert id_cliente("estrategia", "BTC/USDT", 123) == "estrategia-BTCUSDT-123"


def test_metricas_de_aceptacion_calculan_drawdown():
    from plataforma.aceptacion import metricas
    resultado = metricas([100.0, 120.0, 90.0, 110.0], enviadas=10, rechazadas=2)
    assert resultado["max_drawdown"] == pytest.approx(0.25)
    assert resultado["tasa_rechazo"] == pytest.approx(0.2)
    assert resultado["retorno"] == pytest.approx(0.1)


def test_simulacion_es_reproducible_y_no_altera_rng_global():
    import random
    from main import simular
    random.seed(1234)
    esperado = random.random()
    random.seed(1234)
    resultado = simular(pasos=50, semilla=7)
    observado = random.random()
    repetido = simular(pasos=50, semilla=7)
    assert observado == esperado
    assert resultado["curva"] == repetido["curva"]
    assert resultado["metricas"] == repetido["metricas"]


def test_ciclo_conecta_los_contratos_y_el_riesgo_bloquea_antes_de_enviar():
    from plataforma.arquitectura import Senal, ciclo
    from plataforma.riesgo import Limites, MotorRiesgoBasico
    class Datos:
        def ultimo_precio(self, simbolo):
            return 100.0
    class Estrategia:
        def decidir(self, precio):
            return Senal("BTC/USDT", "compra", 1, ts_ms=0)
    class Ejecutor:
        def __init__(self):
            self.enviadas = []
        def enviar(self, senal, precio):
            self.enviadas.append(senal)
            return "enviada"
    ejecutor, riesgo = Ejecutor(), MotorRiesgoBasico(Limites())
    estado = dict(ahora_ms=0, efectivo=1_000, exposicion=0, perdida_diaria=0)
    assert ciclo(Datos(), Estrategia(), riesgo, ejecutor, "BTC/USDT", **estado) == "enviada"
    estado["efectivo"] = 10
    resultado = ciclo(Datos(), Estrategia(), riesgo, ejecutor, "BTC/USDT", **estado)
    assert resultado.startswith("bloqueada por riesgo") and len(ejecutor.enviadas) == 1

def test_reconexion_reinicia_el_contador_tras_recibir_datos():
    import asyncio
    from plataforma.streaming import conectar_con_reintentos
    conexiones, recibidos = [], []
    async def flujo():
        conexiones.append(1)
        if len(conexiones) <= 3:         # tres conexiones que entregan datos y se cortan
            yield len(conexiones)
        raise ConnectionError("corte")
    with pytest.raises(RuntimeError):
        asyncio.run(conectar_con_reintentos(
            flujo, recibidos.append, max_intentos=2,
            espera_inicial=0.001, tope=0.002))
    assert recibidos == [1, 2, 3] and len(conexiones) == 4

def test_simulacion_repetida_sobre_la_misma_base_de_datos(tmp_path, monkeypatch):
    from main import simular
    ruta = str(tmp_path / "plataforma.db")
    monkeypatch.setenv("RUTA_BD", ruta)
    primera = simular(inicio_ms=1_000, corrida="a")
    segunda = simular(inicio_ms=500_000, corrida="b")
    assert primera["curva"] == segunda["curva"]
    con = almacen.abrir(ruta)
    ordenes = con.execute("SELECT COUNT(*) FROM ordenes").fetchone()[0]
    con.close()
    assert ordenes == 2 * primera["metricas"]["ordenes_ejecutadas"]
