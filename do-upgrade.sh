#!/bin/bash


for i in cinder glance keystone neutron-api neutron-gateway nova-cloud-controller nova-compute openstack-dashboard swift-storage-z1 swift-storage-z2 swift-storage-z3 swift-proxy
do
  echo "Starting the upgrade for: $i"
  juju set $i openstack-origin="cloud:trusty-liberty"
done


