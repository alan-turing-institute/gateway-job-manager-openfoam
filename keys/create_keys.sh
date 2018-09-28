#!/bin/bash

# generate a key pair for ssh usage
ssh-keygen -t rsa -f simulator_key -C "simulator key" -N ''
ssh-keygen -t rsa -f github_key -C "github key" -N ''

# create .env file for use by docker-compose
echo AUTHORIZED_KEY=$PUBLIC_KEY > simulator.env
