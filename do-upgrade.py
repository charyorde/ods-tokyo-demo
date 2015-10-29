#!/usr/bin/env python
#
# This script is used to upgrade the OpenStack cluster using Juju.
#

import argparse
import logging
import subprocess
import time
import yaml


logging.basicConfig(
    filename='os-upgrade.log',
    level=logging.DEBUG,
    format=('%(asctime)s %(levelname)s '
            '(%(funcName)s) %(message)s'))

log = logging.getLogger('os_upgrader')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


class Juju(dict):

    def get_service(self, name):
        svc = Service(self['services'][name])
        svc['name'] = name
        return svc

    @classmethod
    def set_config_value(self, service, key, value):
        try:
            setting = '%s=%s' % (key, value)
            cmd = ['juju', 'set', service, setting]
            subprocess.check_output(cmd)
            return True
        except subprocess.CalledProcessError as e:
            # If the value is already set to the current value
            # return True to let the calling code know that it
            # can expect the value is set.
            print(e)
            if e.message.lower().index('already') >= 0:
                return True

            log.error(e)
            return False

    @classmethod
    def run_action(self, service, action):
        try:
            cmd = ['juju', 'action', 'do', service, action]
            output = subprocess.check_output(cmd)
            return output.split(':')[1].strip()
        except subprocess.CalledProcessError as e:
            log.error(e)
            raise e

    @classmethod
    def enumerate_actions(self, service):
        try:
            cmd = ['juju', 'action', 'defined', service]
            output = subprocess.check_output(cmd)
            actions = yaml.safe_load(output)
            return actions.keys()
        except subprocess.CalledProcessError as e:
            log.error(e)
            raise e

    @classmethod
    def is_action_done(cls, act_id):
        """Determines if the action by the action id is currently done or not.
    
        :param act_id: the action id to query the juju service on the status.
        :return boolean: True if the actino is done, False otherwise.
        """
        try:
            output = subprocess.check_output(['juju', 'action', 'fetch', act_id])
            results = yaml.safe_load(output)
            return results['status'] in ['completed', 'failed']
        except subprocess.CalledProcessError as e:
            log.error(e)
            raise e

    @classmethod
    def current(cls, service=None):
        cmd = ['juju', 'status']
        if service:
            cmd.extend(service)
        output = subprocess.check_output(cmd)
        parsed = yaml.safe_load(output)
        return Juju(parsed)


class Service(dict):
    @property
    def name(self):
        return self['name']

    def has_relation(self, rel_name):
        return rel_name in self['relations']

    def set_config(self, key, value):
        return Juju.set_config_value(self.name, key, value)

    def units(self):
        units = []
        for name, info in self['units'].iteritems():
            unit = Unit(info)
            unit['name'] = name
            units.append(unit)
        return units


class Unit(dict):
    @property
    def name(self):
        return self['name']

    @property
    def workload_status(self):
        if 'workload-status' in self:
            return Status(self['workload-status'])
        else:
            return None

    @property
    def agent_status(self):
        if 'agent-status' in self: 
            return Status(self['agent-status'])
        else:
            return None

    def is_upgrading(self):
        wl_status = self.workload_status
        if wl_status is None:
            return False
        return wl_status.is_upgrading()

    def run_action(self, action):
        try:
            action_id = Juju.run_action(self.name, action)
            while not Juju.is_action_done(action_id):
                time.sleep(2)
        except subprocess.CalledProcessError as e:
            log.error(e)
            raise e

    def pause(self):
        log.info(' Pausing service on unit: %s' % self.name)
        self.run_action('pause')
        log.info(' Service on unit %s is paused.' % self.name)

    def resume(self):
        log.info(' Resuming service on unit: %s' % self.name)
        self.run_action('resume')
        log.info(' Service on unit %s has resumed.' % self.name)

    def upgrade_openstack(self):
        log.info(' Upgrading OpenStack for unit: %s' % self.name)
        self.run_action('openstack-upgrade')
        log.info(' Completed upgrade for unit: %s' % self.name)


class Status(dict):

    @property
    def current(self):
        return self['current']

    @property
    def message(self):
        return self['message']

    def is_upgrading(self):
        return self.message.lower().find('upgrad') >= 0


# The 15.10 charm versions support the big bang upgrade scenario
# or the rollinng upgrade within a specific service (e.g. all
# units of a given service are upgraded at the same time).

SERVICES = [
    # Identity and Image
    'keystone',
    'glance',

    # Upgrade nova
    'nova-cloud-controller', 
    'nova-compute', 

    # Neutron upgrades
    'neutron-api',
    'neutron-gateway',

    # Backend block-storage upgrade.
    # Note: just upgrade cinder service.
    'cinder',

    # Swift Storage Upgrade
    'swift-proxy',
    'swift-storage-z1',
    'swift-storage-z2',
    'swift-storage-z3',
]


def is_rollable(service):
    """Determines if the service provided is eligible for a rolling
    upgrade or not.

    :param service <Service>: the service object describing the service
                              that should be tested for rollable upgrades
    :return <bool>: True if the service is rollable, false if not.
    """
    if not service.has_relation('ha'):
        # If there's no hacluster relation, no need to do the rolling
        # upgrade. Go for the big bang.
        return False

    if not service.set_config('action-managed-upgrade', True):
        log.warning('Failed to enable action-managed-upgrade mode.')
        return False

    return True


def perform_rolling_upgrade(service):
    """Performs a rolling upgrade for the specified service.

    Performs a rolling upgrade of the service by iterating through each
    of the units and runs a juju action do <unit_name> openstack-upgrade
    and waits for each unit to finish before continuing on to the next.

    :param service <Service>: the service object describing the juju service
                              that should be upgraded.
    """
    log.info('Performing a rolling upgrade for service: %s' % service.name)
    avail_actions = Juju.enumerate_actions(service.name)
    service.set_config('openstack-origin', args.origin)

    for unit in service.units():
        log.info('Upgrading unit: %s' % unit.name)
        if args.pause and 'pause' in avail_actions:
            unit.pause()

        if 'openstack-upgrade' in avail_actions:
            unit.upgrade_openstack()

        if args.pause and 'resume' in avail_actions:
            unit.resume()

        log.info(' Unit %s has finished the upgrade.' % unit.name)


def perform_bigbang_upgrade(service):
    """Performs a big-bang style upgrade for the specified service.

    In order to do the big-bang style upgrade, set the config value
    for the openstack-origin. Wait a few seconds until the upgrading
    message is reported.
    """
    log.info('Performing a big-bang upgrade for service: %s' % service.name)
    service.set_config('openstack-origin', args.origin)

    # Give the service a chance to invoke the config-changed hook
    # for the bigbang upgrade.
    time.sleep(5)

    upgrade_in_progress = True
    while upgrade_in_progress:
        service = Juju.current().get_service(service.name)
        unit_uip = [u.is_upgrading() for u in service.units()]
        upgrade_in_progress = any(unit_uip)
        if upgrade_in_progress:
            time.sleep(5)


def main():
    global args
    parser = argparse.ArgumentParser(description='Upgrades the currently running cloud.')
    parser.add_argument('-o', '--origin', type=str, default='cloud:trusty-liberty',
                        required=False, metavar='origin')
    parser.add_argument('-p', '--pause', type=bool, default=False,
                        required=False, metavar='pause')
    args = parser.parse_args() 

    env = Juju.current()

    for service in SERVICES:
        log.info('Upgrading service %s', service)
        svc = env.get_service(service)

        if is_rollable(svc):
            perform_rolling_upgrade(svc)
        else:
            perform_bigbang_upgrade(svc)


if __name__ == '__main__':
    main()
