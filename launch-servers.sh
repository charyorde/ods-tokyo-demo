#!/bin/bash
#
# Used to boot a new nova instance with the plex server
#

source ./novarc


# First, import our public ssh key.
echo "Import ssh keys..."
nova keypair-add --pub-key ~/.ssh/id_rsa.pub default

echo "Updating default security group rules..."
nova secgroup-add-rule default tcp 22 22 0.0.0.0/0
nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0
nova secgroup-add-rule default udp 53 53 0.0.0.0/0
nova secgroup-add-rule default tcp 80 80 0.0.0.0/0
nova secgroup-add-rule default tcp 443 443 0.0.0.0/0
nova secgroup-add-rule default tcp 3128 3128 0.0.0.0/0

echo "Creating plex security group..."
if nova secgroup-list | grep -q plex; then
  echo "plex security group already exists."
else
  nova secgroup-create plex "security group for plex related rules"
  nova secgroup-add-rule plex tcp 32400 32400 0.0.0.0/0
fi


echo "Booting instances..."
priv_net_id=$(neutron net-list | awk '/private/ { print $2 }')

if nova list | grep -q bastion; then
  echo "bastion already exists."
else
  echo "Booting juju node..."
  nova boot --flavor m1.small --image trusty --key-name default \
            --nic net-id=$priv_net_id --security-groups default \
            --poll bastion

  floating_ip=$(neutron floatingip-create ext_net | awk '/floating_ip_address/ { print $4 }')
  nova floating-ip-associate bastion $floating_ip
  echo "Juju bastion node is available at: $floating_ip"
fi


echo "Booting plex server..."
if nova list | grep -q plexserver; then
  echo "plexserver already exists."
else
  nova boot --flavor m1.medium --image trusty --key-name default \
            --user-data userdata/plex.sh --nic net-id=$priv_net_id \
            --security-groups default,plex --poll plexserver

  floating_ip=$(neutron floatingip-create ext_net | awk '/floating_ip_address/ { print $4 }')

  nova floating-ip-associate plexserver $floating_ip
  echo "Plex server is available at: $floating_ip"
fi

