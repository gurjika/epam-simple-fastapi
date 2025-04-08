#!/bin/bash
# Update system and install required dependencies
sudo yum update -y
sudo yum install -y unzip aws-cli docker git

sudo systemctl start docker
sudo systemctl enable docker

DOCKER_COMPOSE_VERSION=1.29.2
sudo curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose