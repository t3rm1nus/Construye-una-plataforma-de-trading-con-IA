# Construye una plataforma de trading con IA

Repositorio de código de referencia del libro *Construye una plataforma de trading con IA: APIs de exchanges, ejecución automatizada y despliegue en producción*, de Juan Antonio Charneco (2026), tercer libro de la serie sobre trading algorítmico con Python.

El proyecto reúne los módulos de implementación, la simulación, el panel de control, los ejemplos de integración y las pruebas automatizadas que acompañan al libro.

> **Importante:** el programa principal ejecuta una simulación con un broker simulado. No envía órdenes reales a exchanges, no promete rentabilidad y no constituye asesoramiento financiero. Los mercados financieros implican riesgo de pérdida de capital. Los ejemplos de conexión con exchanges deben utilizarse únicamente en entornos de prueba (*testnet*) y con credenciales de prueba.

## 1. Requisitos

- Python 3.12.
- pip.
- Git, para clonar el repositorio.
- Docker y Docker Compose, únicamente si se desea ejecutar el proyecto en contenedores.

El proyecto se ha configurado para Python 3.12 y las dependencias directas están fijadas en `requirements.txt`.

## 2. Estructura del repositorio

```text
Construye-una-plataforma-de-trading-con-IA/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── plataforma/
│   ├── __init__.py
│   ├── arquitectura.py
│   ├── firma.py
│   ├── streaming.py
│   ├── mercado.py
│   ├── cartera.py
│   ├── ordenes.py
│   ├── reintentos.py
│   ├── secretos.py
│   ├── riesgo.py
│   ├── almacen.py
│   ├── observabilidad.py
│   ├── conciliacion.py
│   ├── parada.py
│   └── aceptacion.py
│
├── tests/
│   ├── test_plataforma.py
│   └── test_revision_seguridad_riesgo.py
│
├── main.py
├── panel.py
│
├── Dockerfile
├── docker-compose.yml
│
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
│
├── .env.example
├── .gitignore
├── .dockerignore
│
└── README.md
```

### Relación entre los módulos y los capítulos

| Módulo | Capítulo |
|---|---:|
| `arquitectura.py` | 1 |
| `firma.py` | 2 |
| `streaming.py` | 3 |
| `mercado.py` | 4 |
| `cartera.py` | 5 |
| `ordenes.py` | 6 |
| `reintentos.py` | 7 |
| `secretos.py` | 8 |
| `riesgo.py` | 9 |
| `almacen.py` | 10 |
| `observabilidad.py` | 11 |
| `panel.py` | 12 |
| `tests/` | 13 |
| `Dockerfile` y `docker-compose.yml` | 14 |
| `conciliacion.py` | 15 |
| `parada.py` | 16 |
| `aceptacion.py` | 17 |
| `main.py` | 18 |

## 3. Instalación local

Clona el repositorio:

```bash
git clone https://github.com/t3rm1nus/Construye-una-plataforma-de-trading-con-IA.git
cd Construye-una-plataforma-de-trading-con-IA
```

Crea un entorno virtual.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Actualiza pip e instala las dependencias de desarrollo:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Este archivo instala las dependencias de ejecución y pytest.

## 4. Ejecutar la simulación

Con el entorno virtual activado:

```bash
python main.py
```

El programa ejecuta una simulación de 200 pasos con una semilla reproducible y muestra el patrimonio final y las métricas de ejecución.

La simulación utiliza:

- Una cartera inicial simulada.
- Un broker simulado.
- Un motor básico de gestión del riesgo.
- Una máquina de estados para las órdenes.
- Persistencia SQLite.
- Registro de eventos y métricas.

Por defecto, la base de datos se mantiene en memoria durante la ejecución. Para utilizar un archivo SQLite persistente, define la variable `RUTA_BD`.

**Windows (PowerShell):**

```powershell
$env:RUTA_BD = "plataforma.db"
python main.py
```

**Linux / macOS:**

```bash
RUTA_BD=plataforma.db python main.py
```

Cada ejecución añade una nueva corrida a la base de datos. Los identificadores de las órdenes permiten distinguir las diferentes ejecuciones.

## 5. Panel de control

El panel está implementado con Streamlit y proporciona una vista de solo lectura de las órdenes almacenadas en SQLite.

Para iniciarlo, instala primero las dependencias y configura la misma ruta de base de datos que utiliza la simulación.

**Windows (PowerShell):**

```powershell
$env:RUTA_BD = "plataforma.db"
streamlit run panel.py
```

**Linux / macOS:**

```bash
RUTA_BD=plataforma.db streamlit run panel.py
```

Abre en el navegador:

```text
http://localhost:8501
```

El panel permite consultar las órdenes recientes y las órdenes activas. No envía órdenes ni modifica el estado de la plataforma.

## 6. Pruebas automatizadas

La suite de pruebas está ubicada en `tests/` y se ejecuta mediante pytest.

Actualmente contiene **25 pruebas**, distribuidas en dos archivos:

| Archivo | Pruebas | Cobertura principal |
|---|---:|---|
| `tests/test_plataforma.py` | 20 | Cartera, broker simulado, órdenes, idempotencia, reintentos, riesgo, persistencia, streaming, conciliación, métricas y simulación. |
| `tests/test_revision_seguridad_riesgo.py` | 5 | Límites de riesgo, ventas para reducir exposición, validación de exposición, filtrado de secretos y configuración del logger. |
| **Total** | **25** | |

Ejecuta toda la suite:

```bash
python -m pytest -q
```

Para obtener un informe más detallado:

```bash
python -m pytest -v
```

La configuración de pytest está en `pytest.ini`. El archivo establece `tests/` como directorio de pruebas y añade la raíz del proyecto a la ruta de importación.

## 7. Integración continua

El repositorio incorpora un workflow de GitHub Actions:

```text
.github/workflows/tests.yml
```

El workflow se ejecuta automáticamente cuando se realiza:

- Un `push` a `master` o `main`.
- Un `pull_request` dirigido a `master` o `main`.
- Una ejecución manual mediante `workflow_dispatch`.

El entorno de integración utiliza:

- Ubuntu Latest.
- Python 3.12.
- Dependencias de `requirements-dev.txt`.
- Ejecución completa de pytest mediante `python -m pytest -q`.

Puedes consultar las ejecuciones y sus resultados en:

[GitHub Actions — Tests](https://github.com/t3rm1nus/Construye-una-plataforma-de-trading-con-IA/actions/workflows/tests.yml)

## 8. Docker

El proyecto incluye un `Dockerfile` y un archivo `docker-compose.yml`.

Para iniciar los servicios:

```bash
docker compose up --build
```

Se levantan dos servicios:

**plataforma**

- Construye la imagen.
- Ejecuta `main.py`.
- Utiliza un volumen compartido para almacenar la base de datos SQLite.

**panel**

- Ejecuta Streamlit.
- Lee la misma base de datos.
- Publica el puerto `8501` únicamente en la interfaz local `127.0.0.1`.
- Proporciona una vista de solo lectura.

Para detener los servicios:

```bash
docker compose down
```

Para detenerlos y eliminar también el volumen persistente:

```bash
docker compose down -v
```

**Atención:** el segundo comando elimina los datos almacenados en el volumen de Docker.

No expongas el panel directamente a Internet. Si necesitas acceso remoto, utiliza una solución de acceso protegida y autenticada.

## 9. Variables de entorno y credenciales

El repositorio incluye:

```text
.env.example
```

Puedes copiarlo para crear tu archivo local.

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

El archivo de ejemplo contempla:

```dotenv
EXCHANGE_API_KEY=
EXCHANGE_API_SECRET=
```

También incluye variables comentadas para los ejemplos de testnet de Binance.

La simulación principal no necesita claves de API.

**Seguridad:**

- No introduzcas credenciales reales en el código.
- No publiques el archivo `.env`.
- No incluyas claves privadas en logs, capturas o documentación.
- Utiliza credenciales de prueba y entornos testnet para los ejercicios de integración.
- Revoca cualquier credencial que se haya publicado accidentalmente.

El archivo `.gitignore` excluye `.env` y otros archivos locales sensibles.

## 10. Dependencias

Las dependencias directas de ejecución están definidas en:

```text
requirements.txt
```

Incluyen:

- `ccxt`
- `pandas`
- `streamlit`

Las dependencias para desarrollo y pruebas se encuentran en:

```text
requirements-dev.txt
```

Este archivo incorpora las dependencias de ejecución y `pytest`.

Para instalar únicamente las dependencias de ejecución:

```bash
pip install -r requirements.txt
```

Para instalar también las dependencias de pruebas:

```bash
pip install -r requirements-dev.txt
```

Para consultar las versiones instaladas:

```bash
pip freeze
```

## 11. Organización y convenciones

Los nombres de archivos, clases, funciones y variables están escritos en español, al igual que los comentarios, las cadenas de documentación y los mensajes.

Se conservan algunos términos habituales del ámbito de mercado y programación cuando se utilizan en el código y se explican en el libro:

- `bid`: precio de compra disponible en el mercado.
- `ask`: precio de venta disponible en el mercado.
- `broker`: intermediario o componente de ejecución.
- `drawdown`: caída desde un máximo anterior.
- `equity`: patrimonio de la cuenta.
- `ts_ms`: marca temporal en milisegundos.
- `p95`: percentil 95.

## 12. Alcance y limitaciones

Este repositorio es una implementación didáctica de los conceptos desarrollados en el libro.

La simulación principal utiliza datos y ejecución simulados. Los módulos de firma, streaming y conexión con exchanges son ejemplos de integración y no convierten automáticamente el programa principal en un sistema de ejecución real.

El proyecto no debe interpretarse como un sistema de inversión listo para operar con capital real ni como una garantía de seguridad, disponibilidad o rentabilidad.

Antes de adaptar cualquier ejemplo a un entorno externo, es necesario realizar una revisión técnica y de seguridad independiente, probar los mecanismos de control y utilizar entornos de prueba.

## 13. Derechos

© 2026 Juan Antonio Charneco. Todos los derechos reservados.

Este repositorio acompaña al libro *Construye una plataforma de trading con IA*. Consulta las condiciones de uso y distribución aplicables antes de reutilizar el código o sus materiales.