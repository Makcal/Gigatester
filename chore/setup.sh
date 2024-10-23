#!/bin/bash
apt update && apt upgrade -y &&
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa
apt install python3.11 python3.11-venv

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo docker plugin install grafana/loki-docker-driver:2.9.4 --alias loki --grant-all-permissions

sudo ln -s "$PWD" /usr/gigatester
mkdir data prog queue reference
cd tester || (echo "Run from the root"; exit)
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
