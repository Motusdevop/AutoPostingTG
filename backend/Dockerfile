FROM python:3.11


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt
COPY ./.dev.env /code/.dev.env

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./src /code/src/
WORKDIR /code/src


CMD ["fastapi", "run", "main.py", "--workers", "4", "--port", "8000"]