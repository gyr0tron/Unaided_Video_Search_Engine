docker build -t flaskapp:latest .
docker run -t -d -p 5000:5000 flaskapp

to kill
docker system prune -a
