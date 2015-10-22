#!/bin/bash

for s in cinder glance keystone nova-cloud-controller openstack-dashboard percona swift-proxy; do
    vip=$(juju get $s | python -c "import subprocess, sys, yaml; t = yaml.safe_load('\n'.join(sys.stdin.readlines())); vip = t['settings']['vip']['value']; print vip")
    echo "$s = $vip"
done
