import logging

from plataforma.arquitectura import Senal
from plataforma.observabilidad import crear_logger
from plataforma.riesgo import Limites, MotorRiesgoBasico
from plataforma.secretos import FiltroSecretos


def crear_motor():
    return MotorRiesgoBasico(
        Limites(
            max_nocional=1_000,
            max_exposicion=5_000,
            max_perdida_diaria=200,
            max_antiguedad_ms=2_000,
        )
    )


def test_bloquea_compra_cuando_se_supera_limite_perdida():
    motor = crear_motor()
    senal = Senal("BTC/USDT", "compra", 1, 1_000)

    ok, motivo = motor.evaluar(
        senal,
        100,
        ahora_ms=1_000,
        efectivo=10_000,
        exposicion=0,
        perdida_diaria=200,
    )

    assert ok is False
    assert motivo == "pérdida diaria superada"


def test_permite_venta_para_reducir_exposicion_tras_limite_perdida():
    motor = crear_motor()
    senal = Senal("BTC/USDT", "venta", 1, 1_000)

    ok, motivo = motor.evaluar(
        senal,
        100,
        ahora_ms=1_000,
        efectivo=0,
        exposicion=100,
        perdida_diaria=250,
    )

    assert ok is True
    assert motivo == "aprobada"


def test_sigue_bloqueando_venta_superior_a_exposicion():
    motor = crear_motor()
    senal = Senal("BTC/USDT", "venta", 2, 1_000)

    ok, motivo = motor.evaluar(
        senal,
        100,
        ahora_ms=1_000,
        efectivo=0,
        exposicion=100,
        perdida_diaria=250,
    )

    assert ok is False
    assert motivo == "venta superior a la exposición disponible"


def test_filtro_secretos_redacta_api_key():
    filtro = FiltroSecretos()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="api_key=MI_CLAVE_PRIVADA",
        args=(),
        exc_info=None,
    )

    assert filtro.filter(record) is True
    assert "MI_CLAVE_PRIVADA" not in record.getMessage()
    assert "***" in record.getMessage()


def test_logger_incluye_filtro_secretos():
    nombre = "test_logger_revision_seguridad"
    logger = crear_logger(nombre)

    assert logger.handlers
    assert any(
        isinstance(filtro, FiltroSecretos)
        for handler in logger.handlers
        for filtro in handler.filters
    )