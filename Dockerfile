FROM python:3.8

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

EXPOSE 5000

COPY . /app

ENTRYPOINT ["python"]

CMD ["python","taxi.py"]