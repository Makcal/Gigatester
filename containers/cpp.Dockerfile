FROM alpine:latest
LABEL authors="max"

RUN apk add gcc
RUN apk add g++
RUN apk add bash
