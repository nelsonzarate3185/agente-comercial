FROM python:3.11-slim

WORKDIR /app

# libaio1 es requerido por Oracle Instant Client en Linux
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libaio-dev \
        libnsl2 && \
    ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 \
           /usr/lib/x86_64-linux-gnu/libaio.so.1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Oracle Instant Client Basic (Linux x64)
# Antes de buildear, descargar el ZIP desde:
#   https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html
# Descomprimir y renombrar la carpeta como instantclient/ junto a este Dockerfile.
COPY /media/sdb1/agente-ia-comercial/instantclient_12_2/ /opt/oracle/instantclient/

RUN ln -s /opt/oracle/instantclient/libclntsh.so.12.1 \
          /opt/oracle/instantclient/libclntsh.so

RUN ln -s /opt/oracle/instantclient/libocci.so.12.1 \
          /opt/oracle/instantclient/libocci.so

RUN echo /opt/oracle/instantclient > /etc/ld.so.conf.d/oracle-ic.conf && ldconfig

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ORACLE_CLIENT_DIR=/opt/oracle/instantclient

EXPOSE 8010
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]