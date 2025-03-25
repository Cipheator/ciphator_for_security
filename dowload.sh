#!/bin/bash
apt install -y git
git clone https://github.com/Cipheator/ciphator_for_security/.
systemctl enable --now systemd-networkd
mv 10-static.network /etc/systemd/network/
systemctl restart systemd-networkd
useradd client
su client
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
ssh-copy-id worker@192.168.1.2