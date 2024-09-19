FROM python:3.6-slim-buster

WORKDIR /app

COPY requirements.txt /app

RUN python -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 4000

CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]
