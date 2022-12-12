FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1

WORKDIR src

COPY requirements.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY . .

CMD [ "python", "run_app.py" ]
