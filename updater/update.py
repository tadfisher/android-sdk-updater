#!/usr/bin/env python3

import os
import sys

import pexpect

from updater.scan import scan
from updater.list import list_packages


class Update:
    def __init__(self, installed, available):
        self.installed = installed
        self.available = available

    def __str__(self):
        return self.installed.name + " [" + self.installed.revision + " -> " + self.available.revision + "]"


def to_dict(packages):
    d = {}
    for p in packages:
        d[p.name] = p
    return d


def compute_updates(installed, available):
    updates = []
    ad = to_dict(available)
    for i in installed:
        a = ad.get(i.name)
        if a is None:
            print('   Update site is missing package \'{:s}!\''.format(i.name), file=sys.stderr)
            continue
        if a.semver > i.semver:
            updates.append(Update(i, a))
    return updates


def compute_requests(requested, available):
    requests = []
    ad = to_dict(available)
    for r in requested:
        a = ad.get(r)
        if a is None:
            print('   Update site is missing package \'{:s}!\''.format(r), file=sys.stderr)
            continue
        requests.append(a)
    return requests


def remove_packages(packages, requested):
    pd = to_dict(packages)
    for r in requested:
        if r in pd:
            requested.remove(r)


def combine_updates(requests, updates):
    nums = set()
    for r in requests:
        nums.add(r.num)
    for u in updates:
        nums.add(u.available.num)
    return nums


def main(sdk, req=None):
    if req is None:
        req = []

    android = os.path.join(sdk, 'tools', 'android')

    print('Scanning', sdk, 'for installed packages...')
    installed = scan(sdk)
    print('   ', str(len(installed)), 'packages installed.')

    # Remove requested package names we already have
    if len(req) > 0:
        remove_packages(installed, req)

    print('Querying update sites for available packages...')
    available = list_packages(android)
    print('   ', str(len(available)), 'packages available.')

    requests = compute_requests(req, available)
    updates = compute_updates(installed, available)

    for r in requests:
        print('Installing: {:s}'.format(str(r)))
    for u in updates:
        print('Updating:   {:s}'.format(str(u)))

    nums = combine_updates(requests, updates)
    if len(nums) == 0:
        print("All packages are up-to-date.")
        exit(0)

    package_filter = ','.join(nums)

    installer = pexpect.spawn('{:s} update sdk --no-ui --all --filter {:s}'.format(android, package_filter))
    installer.logfile = sys.stdout.buffer
    eof = False
    while not eof:
        i = installer.expect([r"Do you accept the license '.+' \[y/n\]:", pexpect.EOF])
        if i == 0:
            installer.sendline('y')
        else:
            eof = True

    print('Done; installed {:d} packages.'.format(len(nums)))

if __name__ == '__main__':
    main(sys.argv[1:])
