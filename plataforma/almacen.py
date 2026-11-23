import math
import sqlite3


ESQUEMA = """
CREATE TABLE IF NOT EXISTS ordenes (
    id TEXT PRIMARY KEY, simbolo TEXT NOT NULL, lado TEXT NOT NULL,
    cantidad REAL NOT NULL, estado TEXT NOT NULL, ts_ms INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS ejecuciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT, id_evento TEXT NOT NULL UNIQUE,
    orden_id TEXT NOT NULL REFERENCES ordenes(id), cantidad REAL NOT NULL,
    precio REAL NOT NULL, comision REAL NOT NULL, ts_ms INTEGER NOT NULL);
"""


def abrir(ruta: str = "plataforma.db") -> sqlite3.Connection:
    con = sqlite3.connect(ruta)
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(ESQUEMA)
    return con


def registrar_orden(con, id_, simbolo, lado, cantidad, estado, ts_ms) -> None:
    if not id_ or not simbolo or lado not in {"compra", "venta"} or not estado:
        raise ValueError("se requieren el ID de la orden, el símbolo, el lado y el estado")
    if not math.isfinite(cantidad) or cantidad <= 0:
        raise ValueError("la cantidad de la orden debe ser finita y positiva")
    if not isinstance(ts_ms, int) or isinstance(ts_ms, bool) or ts_ms < 0:
        raise ValueError("la marca temporal de la orden debe ser un entero no negativo")
    with con:
        con.execute("INSERT INTO ordenes VALUES (?,?,?,?,?,?)",
                    (id_, simbolo, lado, cantidad, estado, ts_ms))


def cambiar_estado(con, id_, estado) -> None:
    with con:
        cur = con.execute("UPDATE ordenes SET estado=? WHERE id=?", (estado, id_))
        if cur.rowcount != 1:
            raise KeyError(f"la orden no existe: {id_}")


def registrar_ejecucion(con, orden_id, id_evento, cantidad, precio, comision, ts_ms) -> bool:
    """Inserta una ejecución una sola vez usando el ID único del proveedor."""
    if not id_evento:
        raise ValueError("se requiere el ID único de ejecución del proveedor")
    if not all(math.isfinite(v) for v in (cantidad, precio, comision)):
        raise ValueError("los valores de la ejecución deben ser finitos")
    if cantidad <= 0 or precio <= 0 or comision < 0:
        raise ValueError("cantidad y precio de la ejecución deben ser positivos y la comisión no negativa")
    if not isinstance(ts_ms, int) or isinstance(ts_ms, bool) or ts_ms < 0:
        raise ValueError("la marca temporal de la ejecución debe ser un entero no negativo")
    with con:
        cur = con.execute(
            "INSERT OR IGNORE INTO ejecuciones "
            "(id_evento, orden_id, cantidad, precio, comision, ts_ms) "
            "VALUES (?,?,?,?,?,?)",
            (id_evento, orden_id, cantidad, precio, comision, ts_ms))
    return cur.rowcount == 1


def posiciones(con) -> dict[str, float]:
    """Reconstruye la posición neta desde el historial deduplicado de ejecuciones."""
    filas = con.execute(
        "SELECT o.simbolo, "
        "SUM(CASE o.lado WHEN 'compra' THEN e.cantidad ELSE -e.cantidad END) "
        "FROM ejecuciones e JOIN ordenes o ON o.id = e.orden_id "
        "GROUP BY o.simbolo").fetchall()
    return {simbolo: neto for simbolo, neto in filas}
