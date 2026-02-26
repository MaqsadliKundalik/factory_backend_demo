FROM python:3.13-slim

# Kerakli paketlar
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates gnupg && \
    rm -rf /var/lib/apt/lists/*

# Azul Zulu Java 11 o‘rnatish
RUN curl -fsSL https://repos.azul.com/azul-repo.key -o /usr/share/keyrings/azul.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/azul.gpg] https://repos.azul.com/zulu/deb stable main" \
    > /etc/apt/sources.list.d/zulu.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends zulu11-jre && \
    rm -rf /var/lib/apt/lists/*

# Java environment (dinamik yo‘l)
RUN export JAVA_PATH=$(dirname $(dirname $(readlink -f $(which java)))) && \
    echo "JAVA_HOME=$JAVA_PATH" >> /etc/environment

ENV JAVA_HOME=/usr/lib/jvm/zulu11-ca-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# JDBC driver
RUN mkdir -p /app/jdbc && \
    curl -o /app/jdbc/mssql-jdbc-9.4.1.jre11.jar \
    https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/9.4.1.jre11/mssql-jdbc-9.4.1.jre11.jar

# TLS 1.0 ni yoqish
RUN sed -i 's/TLSv1, TLSv1.1,//g' $JAVA_HOME/conf/security/java.security || true

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# TLS protokollari
ENV JAVA_OPTS="-Djdk.tls.client.protocols=TLSv1,TLSv1.1,TLSv1.2 -Dhttps.protocols=TLSv1,TLSv1.1,TLSv1.2"



