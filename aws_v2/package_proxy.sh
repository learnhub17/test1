#!/bin/bash
#append repository
sleep 10
apt-get update
echo "deb http://deb.torproject.org/torproject.org xenial main" > /etc/apt/sources.list.d/tor.list
echo "deb-src http://deb.torproject.org/torproject.org xenial main" >> /etc/apt/sources.list.d/tor.list

##import keys
gpg --keyserver keys.gnupg.net --recv A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89
gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | sudo apt-key add -

##install packages
apt update && apt install -y tor deb.torproject.org-keyring privoxy

##stop the service
service tor stop
service privoxy stop

##configuring tor & privoxy server
sed -i 's/#SOCKSPort 9050/SOCKSPort 0.0.0.0:9050/' /etc/tor/torrc
sed -i 's/listen-address  localhost:8118/listen-address  0.0.0.0:8118/' /etc/privoxy/config
echo "forward-socks5   /               0.0.0.0:9050 ." >> /etc/privoxy/config

##install http proxy:polipo
apt-get install -y polipo

##Configure polipo
echo "socksParentProxy = 0.0.0.0:9050" >> /etc/polipo/config 
echo "socksProxyType = socks5" >> /etc/polipo/config 
echo "proxyAddress = "0.0.0.0"" >> /etc/polipo/config 
echo "proxyPort = 8123" >> /etc/polipo/config
##start the service
service tor restart
sleep 15
service privoxy restart
sleep 20
service polipo restart
