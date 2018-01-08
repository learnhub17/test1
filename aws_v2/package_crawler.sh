#!/bin/sh
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update
apt-get purge -y python python2.7 python3 python3.5 python3.5-minimal python3
apt-get autoremove -y
apt-get install -y python3.6
cd /usr/bin
rm python
ln -s python3.6 python
apt-get update
apt-get install -y python3-pip
pip3 install --upgrade pip
pip install feedparser
pip install scrapy
pip install elasticsearch
pip install bs4
rm python3
ln -s python3.6 python3
pip install web.py==0.40.dev0
sleep 150
cd /home/ubuntu/project
python dark.py 8080
