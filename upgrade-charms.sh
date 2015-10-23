#!/bin/bash

juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/ceph ceph
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/ceph-osd ceph-osd
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/cinder cinder
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/cinder-ceph cinder-ceph
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/glance glance
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/keystone keystone
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/hacluster keystone-hacluster
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/neutron-api neutron-api
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/neutron-gateway neutron-gateway
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/neutron-openvswitch neutron-openvswitch
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/nova-cloud-controller nova-cloud-controller
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/hacluster nova-cloud-controller-hacluster
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/nova-compute nova-compute
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/openstack-dashboard openstack-dashboard
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/hacluster openstack-dashboard-hacluster
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/percona-cluster percona
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/hacluster percona-hacluster
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/rabbitmq-server rabbitmq-server
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/swift-proxy swift-proxy
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/swift-storage swift-storage-z1
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/swift-storage swift-storage-z2
juju upgrade-charm --switch cs:~openstack-charmers-next/trusty/swift-storage swift-storage-z3

