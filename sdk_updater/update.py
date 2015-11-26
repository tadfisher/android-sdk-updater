#!/usr/bin/python

from __future__ import print_function

import os
import sys

import pexpect

from sdk_updater.scan import scan
from sdk_updater.list import list_packages


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


def main(sdk, bootstrap=None, verbose=False, timeout=None):
    if bootstrap is None:
        bootstrap = []

    if timeout == 0:
        timeout = None

    android = os.path.join(sdk, 'tools', 'android')

    print('Scanning', sdk, 'for installed packages...')
    installed = scan(sdk, verbose=verbose)
    print('   ', str(len(installed)), 'packages installed.')

    # Remove package names we already have
    if len(bootstrap) > 0:
        remove_packages(installed, bootstrap)

    print('Querying update sites for available packages...')
    available = list_packages(android, verbose=verbose)
    print('   ', str(len(available)), 'packages available.')

    requests = compute_requests(bootstrap, available)
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

    installer = pexpect.spawn(
        '{:s} update sdk --no-ui --all --filter {:s}'.format(android, package_filter),
        timeout=timeout)
    if verbose:
        if sys.version_info[0] == '3':
          installer.logfile = sys.stdout.buffer
        else:
          installer.logfile = sys.stdout
    while True:
        i = installer.expect([r"Do you accept the license '.+' \[y/n\]:",
                pexpect.TIMEOUT, pexpect.EOF])
        if i == 0:
            # Prompt
            installer.sendline('y')
        elif i == 1:
            # Timeout
            print(('Package installation timed out after {:d} seconds. '
                   'Some packages may have been installed successfully.')
                  .format(timeout), file=sys.stderr)
            exit(1)
        else:
            break

    print('Done; (should have) installed {:d} package(s).'.format(len(nums)))
    exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
