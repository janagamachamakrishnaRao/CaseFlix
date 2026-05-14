#!/usr/bin/env bash

apt-get update
apt-get install -y libreoffice

pip install -r backend/requirements.txt
