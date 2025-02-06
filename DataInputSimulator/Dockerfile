# Verwenden von Python 3.9 als Basis-Image
FROM python:3.9-slim

# Setzen des Arbeitsverzeichnisses
WORKDIR /app

# Kopieren der Anforderungen
COPY requirements.txt .

# Installieren der Anforderungen
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren des Python-Programms
COPY . .

# Setzen der Umgebungsvariable
ENV PYTHONUNBUFFERED 1

# Setzen des Einstiegspunkts
CMD ["python", "main.py"]
