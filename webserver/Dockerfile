FROM python:latest
WORKDIR /prog
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD python3 /prog/webserver.py
EXPOSE 80
