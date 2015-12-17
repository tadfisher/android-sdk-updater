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
        return '{:s} [{:s} -> {:s}]'.format(self.installed.name, self.installed.revision, self.available.revision)


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
            print('   Update site is missing package \'{:s}\''.format(i.name), file=sys.stderr)
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
            print('    Update site is missing package \'{:s}\''.format(r), file=sys.stderr)
            continue
        requests.append(a)
    return requests


def remove_packages(packages, requested):
    pd = to_dict(packages)
    diff = set()
    for r in requested:
        if r not in pd:
            diff.add(r)
    return diff


def scan_missing(sdk, packages, verbose=False):
    # Re-scan SDK root to check for failed installs.
    print('Re-scanning {:s}...'.format(sdk))
    installed = scan(sdk, verbose=verbose)
    missing = [p for p in packages if p not in installed]
    if missing:
        print('Failed to install packages:', file=sys.stderr)
        for m in missing:
            print('   ', m, file=sys.stderr)
    return missing


def update_packages(android, package_filter, options=None, verbose=False, timeout=None):
    if options is None:
        options = []
    args = ['update', 'sdk', '--no-ui', '--all', '--filter', package_filter] + options
    installer = pexpect.spawn(android, args=args, timeout=timeout)
    if verbose:
        if sys.version_info >= (3,):
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
            print('Package installation timed out after {:d} seconds.'
                  .format(timeout), file=sys.stderr)
            break
        else:
            break


def main(sdk, bootstrap=None, options=None, verbose=False, timeout=None, dry_run=False):
    if timeout == 0:
        timeout = None

    android = os.path.join(sdk, 'tools', 'android')
    if not os.path.isfile(android):
        print('{:s} not found. Is ANDROID_HOME correct?'.format(android))
        exit(1)

    print('Scanning', sdk, 'for installed packages...')
    installed = scan(sdk, verbose=verbose)
    print('   ', str(len(installed)), 'packages installed.')

    # Remove package names we already have
    requested = []
    if bootstrap:
        requested = remove_packages(installed, bootstrap)

    print('Querying update sites for available packages...')
    available = list_packages(android, options=options, verbose=verbose)
    print('   ', str(len(available)), 'packages available.')

    requests = compute_requests(requested, available)
    updates = compute_updates(installed, available)

    for r in requests:
        print('Installing: {:s}'.format(str(r)))
    for u in updates:
        print('Updating:   {:s}'.format(str(u)))

    to_install = set(requests + [u.available for u in updates])

    if not to_install:
        print("All packages are up-to-date.")
        exit(0)

    if dry_run:
        print("--dry-run was set; exiting.")
        exit(0)

    package_filter = ','.join([p.name for p in to_install])
    update_packages(android, package_filter, options, verbose, timeout)

    # Re-scan SDK dir for packages we missed.
    missing = scan_missing(sdk, to_install, verbose=verbose)

    if missing:
        print('Finished: {:d} packages installed. Failed to install {:d} packages.'
              .format(len(to_install) - len(missing), len(missing)))
        exit(1)
    else:
        print('Finished: {:d} packages installed.'.format(len(to_install)))
        exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
