FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && pip install pipenv && pipenv install --system
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./src /code/src/
WORKDIR /code/src


CMD ["fastapi", "run", "main.py", "--workers", "4", "--port", "8000"]