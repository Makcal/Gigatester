FROM alpine:latest
LABEL authors="max"

RUN apk add gcc
RUN apk add g++
RUN apk add python3
RUN apk add bash
