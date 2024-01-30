FROM python:latest
WORKDIR /prog
RUN pip install fastapi uvicorn python-multipart websockets
COPY static ./static/
COPY webserver.py ./
CMD python3 /prog/webserver.py
EXPOSE 80
