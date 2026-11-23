# Construye una plataforma de trading con IA — repositorio del libro

Código de referencia del libro *Construye una plataforma de trading con IA: APIs de
exchanges, ejecución automatizada y despliegue en producción* (Juan Antonio Charneco,
2026, tercer libro de la serie sobre trading algorítmico con Python).

El repositorio contiene exactamente los módulos impresos en la sección «Implementación de
referencia» de cada capítulo, además de las pruebas (capítulo 13), el panel de control
(capítulo 12) y los archivos de contenedores (capítulo 14). Está pensado para aprender y
simular: **nunca envía órdenes reales**, no promete rentabilidad y no es asesoramiento
financiero. Operar en los mercados implica riesgo de pérdida de capital.

## Estructura

```
Construye_una_plataforma_de_trading_con_IA/
├── plataforma/
│   ├── arquitectura.py      (cap. 1)    ├── riesgo.py            (cap. 9)
│   ├── firma.py             (cap. 2)    ├── almacen.py           (cap. 10)
│   ├── streaming.py         (cap. 3)    ├── observabilidad.py    (cap. 11)
│   ├── mercado.py           (cap. 4)    ├── conciliacion.py      (cap. 15)
│   ├── cartera.py           (cap. 5)    ├── parada.py            (cap. 16)
│   ├── ordenes.py           (cap. 6)    └── aceptacion.py        (cap. 17)
│   ├── reintentos.py        (cap. 7)
│   └── secretos.py          (cap. 8)
├── tests/test_plataforma.py (cap. 13)
├── panel.py                 (cap. 12)
├── main.py                  (cap. 18)
├── Dockerfile, docker-compose.yml, requirements.txt, requirements-dev.txt (cap. 14)
├── .env.example, .gitignore, .dockerignore, pytest.ini
└── README.md
```

`main.py` ejecuta el bucle de simulación. Usa la cartera, el broker simulado, el motor de
riesgo, la máquina de estados de las órdenes, el almacén SQLite, los logs y métricas y el
control operativo. El resto de módulos (firma REST, streaming, normalización de mercado,
reintentos, conciliación, aceptación) son ejemplos autocontenidos con sus propias pruebas
o ejercicios; `main.py` no los invoca.

## Inicio rápido (Python 3.12)

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt  # dependencias de ejecución + pytest

pytest                               # 20 pruebas, sin red, unos segundos
python main.py                       # ejecuta la simulación e imprime el patrimonio final
```

Para ver los resultados en el panel de control, da el mismo archivo de base de datos a
los dos procesos:

```bash
RUTA_BD=plataforma.db python main.py
RUTA_BD=plataforma.db streamlit run panel.py
```

Cada ejecución de `main.py` añade una nueva corrida (sus órdenes se identifican como
`corrida<marca>-<paso>`) a la base de datos, de modo que puedes lanzarlo tantas veces
como quieras sobre el mismo archivo. Las posiciones netas que devuelve `simular()` se
reconstruyen a partir de todo el historial guardado en ese archivo.

## Docker

```bash
cp .env.example .env                 # opcional: solo para inyectar claves del exchange
docker compose up --build
```

La simulación se ejecuta una vez en el servicio `plataforma` y escribe en el volumen
compartido. El panel se publica solo en `http://127.0.0.1:8501` (vista de solo lectura
de la misma base de datos). No abras ese puerto a Internet; usa un túnel o un proxy
con autenticación.

## Dependencias

`requirements.txt` fija las versiones exactas de las dependencias directas con las que se
ejecutaron las pruebas (Python 3.12). Para una reproducibilidad estricta, fija también las
dependencias transitivas (`pip freeze > requirements.lock`) y el digest de la imagen base
en el Dockerfile. `ccxt` solo hace falta para los ejercicios con exchanges (capítulos 2 y 18).

## Cómo leer el código

Los nombres de archivos, clases, funciones y variables están en español, igual que los
comentarios, las cadenas de documentación y los mensajes. Se mantienen unos pocos
términos de mercado que se usan tal cual en inglés y que el libro explica: `bid` y `ask`
(precios de oferta y demanda), `broker`, `drawdown`, `equity`, `ts_ms` (marca temporal en
milisegundos) y `p95` (percentil 95).

## Derechos

© 2026 Juan Antonio Charneco. Todos los derechos reservados. Consulta el libro para ver las
condiciones de uso.
