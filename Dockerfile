FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


RUN apt-get update && apt-get install -y wget unzip \
    && wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip \
    && unzip ngrok-stable-linux-amd64.zip \
    && mv ngrok /usr/local/bin \
    && rm ngrok-stable-linux-amd64.zip

COPY . .

# NGROK
ENV NGROK_DOMAIN=pleasing-kingfish-on.ngrok-free.app
ENV NGROK_AUTHTOKEN=2xcxnNI9wuwaIgCM8mJwiwCSwUE_2q69n3y1QReiu2sNNiiuN
ENV PORT=8080

RUN echo '#!/bin/bash\n'\
    'ngrok config add-authtoken $NGROK_AUTHTOKEN\n'\
    'ngrok http --domain=$NGROK_DOMAIN $PORT &\n'\
    'python main.py' > /app/start.sh \
    && chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]
