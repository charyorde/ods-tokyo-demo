#!/bin/bash
SVC=$(cat /tmp/upgrade.service)
juju status $SVC
