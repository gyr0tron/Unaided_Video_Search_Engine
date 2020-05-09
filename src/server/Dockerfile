from python:3.7-slim

# RUN apk add --no-cache python3-dev \
#     && pip3 install --upgrade pip
    
WORKDIR /app/server

COPY . /app/server

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["server.py"]