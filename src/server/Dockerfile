from alpine:latest

RUN apk add --no-cache python3-dev \
    && pip3 install --upgrade pip
    
WORKDIR /app/server

COPY . /app/server

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["server.py"]