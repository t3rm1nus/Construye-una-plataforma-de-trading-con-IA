FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# Usuario sin privilegios: el contenedor no corre como root
RUN useradd --create-home --uid 1000 app
# Primero las dependencias: esta capa se reutiliza mientras no cambien
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY plataforma ./plataforma
COPY main.py panel.py ./
RUN mkdir /app/datos && chown app:app /app/datos
USER app
CMD ["python", "main.py"]
