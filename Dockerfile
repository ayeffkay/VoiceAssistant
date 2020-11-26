FROM python:3.8.3
MAINTAINER "Alina Kolesnikova <alina.f.kolesnikova@gmail.com>"

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

CMD python app.py

