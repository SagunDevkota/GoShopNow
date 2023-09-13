FROM python:3.10

LABEL maintainer="Sagun Devkota" 

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app 
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apt-get update && apt-get install -y postgresql-client && \ 
    if [ $DEV = true ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    useradd -m django-user

ENV PATH="/py/bin:$PATH" 

USER django-user

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]