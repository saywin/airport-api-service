FROM python:3.12-alpine

LABEL maintainer="stilon570@gmail.com"
ENV PYTHOUNMBUFFERED 1
WORKDIR app/
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
