#!/bin/bash

# generate a key pair for ssh usage
ssh-keygen -t rsa -f simulator_key -C "simulator key" -N ''
PUBLIC_KEY=$(cat simulator_key.pub)

# create .env file for use by docker-compose
echo AUTHORIZED_KEY=$PUBLIC_KEY > simulator.env
