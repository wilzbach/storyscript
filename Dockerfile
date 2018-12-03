FROM        python:3.7-alpine

RUN         mkdir /app
ADD         omg/requirements.txt /app
RUN         pip install -r /app/requirements.txt
ADD         omg/app.py /app/app.py
ADD         README.md /storyscript/README.md
ADD         setup.py /storyscript/setup.py
RUN         python /storyscript/setup.py install
ADD         storyscript /app/storyscript

ENTRYPOINT  ["python", "/app/app.py"]
