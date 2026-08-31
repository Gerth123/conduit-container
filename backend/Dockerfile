FROM python:3.8-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY patch_django.py .
RUN python3 patch_django.py /install/lib/python3.8/site-packages

FROM python:3.8-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD python manage.py migrate --noinput && gunicorn conduit.wsgi:application --bind 0.0.0.0:8000