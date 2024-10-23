#!/bin/bash
docker rmi --no-prune=true gigatester/{cpp,cs,java,py}
for i in cpp cs java py
do
  docker build -f containers/$i.Dockerfile -t gigatester/$i .
done