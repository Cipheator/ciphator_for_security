#!/bin/bash

apt install -y git
git clone https://github.com/Cipheator/ciphator_for_security/.


systemctl enable --now systemd-networkd
systemctl restart systemd-networkd

useradd -m -s /bin/bash client
echo 'client:1' | chpasswd
usermod -aG sudo client

systemctl start ssh
xhost +SI:localuser:client

su client
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
ssh-copy-id worker@192.168.1.2
