FROM python:3.11

RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV TOKEN=6991735114:AAFy4nN5L35jxz6pl_R7kPyAmc9lsvH-wfM

RUN mkdir /bot_app

WORKDIR /bot_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY / .

CMD ["python3", "./app.py"]