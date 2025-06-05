FROM python:3.10.14-bookworm

WORKDIR /lexiloop

COPY ./requirements.txt /lexiloop/requirements.txt
COPY ./data /lexiloop/data


RUN pip install --no-cache-dir --upgrade -r /lexiloop/requirements.txt

COPY ./app /lexiloop/app
COPY ./.env /lexiloop/

EXPOSE 80

CMD ["fastapi", "run", "app/main.py", "--port", "80"]