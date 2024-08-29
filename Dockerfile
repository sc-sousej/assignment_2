FROM python:3.11-slim

WORKDIR /app

COPY . /app/

ENV MONGO_URI="mongodb://admin:admin@mongodb:27017/"

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8081

CMD ["python", "-m", "api.cherrypy_api"]
