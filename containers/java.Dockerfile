FROM openjdk:23-slim-bullseye

RUN apt update && apt install -y --no-install-recommends --no-install-suggests python3
