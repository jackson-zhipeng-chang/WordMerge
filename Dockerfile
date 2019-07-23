FROM python:3.7-stretch
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY .env.example .env
RUN pip install -r requirements.txt
COPY . /code/
CMD python3 manage.py runserver 0.0.0.0:8000