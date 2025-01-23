FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./src /code/src/
WORKDIR /code/src


CMD ["fastapi", "run", "main.py", "--workers", "4", "--port", "8000"]