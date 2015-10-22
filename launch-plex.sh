#!/bin/bash
#
# Used to boot a new nova instance with the plex server
#

set -ex

source ./novarc

priv_net_id=$(neutron net-list | awk '/private/ { print $2 }')

nova boot --flavor m1.medium --image trusty --key-name wolsen \
          --user-data userdata/plex.sh --nic net-id=$priv_net_id \
          --security-groups default,plex --poll plexserver

floating_ip=$(neutron floatingip-create ext_net | awk '/floating_ip_address/ { print $4 }')

nova floating-ip-associate plexserver $floating_ip


