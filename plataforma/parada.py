from enum import Enum


class Modo(Enum):
    DETENIDO = "detenido"
    INICIALIZANDO = "inicializando"
    SIMULACION = "simulación"
    OPERATIVO = "operativo"
    DEGRADADO = "degradado"
    BLOQUEADO = "bloqueado"
PERMITIDO = {
    Modo.DETENIDO: {"consultar"},
    Modo.INICIALIZANDO: {"consultar"},
    Modo.SIMULACION: {"consultar", "enviar_simulado", "cancelar"},
    Modo.OPERATIVO: {"consultar", "enviar", "cancelar", "cambiar_config"},
    Modo.DEGRADADO: {"consultar", "cancelar", "reducir_posicion"},
    Modo.BLOQUEADO: {"consultar", "cancelar"},   # nunca abrir órdenes nuevas
}


class Control:
    def __init__(self, modo: Modo = Modo.DETENIDO):
        self.modo = modo
    def puede(self, accion: str) -> bool:
        return accion in PERMITIDO[self.modo]
    def parada_emergencia(self, ordenes_abiertas, cancelar) -> list[str]:
        """Primero bloquea; después cancela. Devuelve las que fallaron."""
        self.modo = Modo.BLOQUEADO                # 1) impedir órdenes nuevas
        fallidas = []
        for id_ in ordenes_abiertas:              # 2) reducir exposición
            try:
                cancelar(id_)
            except Exception:
                fallidas.append(id_)              # 3) escalar a un humano
        return fallidas
