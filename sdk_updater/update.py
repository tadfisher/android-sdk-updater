#!/usr/bin/python

from __future__ import print_function
import os
import sys
import pexpect
from sdk_updater.scan import scan
from sdk_updater.list import list_packages


class PackageOperation(object):
    def __init__(self, package):
        self.package = package


class Install(PackageOperation):
    def __init__(self, package, revision):
        super(Install, self).__init__(package)
        self.revision = revision

    def __str__(self):
        return 'Installing: {:s} [{:s}]'\
            .format(self.package.name, self.revision)


class Update(PackageOperation):
    def __init__(self, package, revision_installed, revision_available):
        super(Update, self).__init__(package)
        self.revision_installed = revision_installed
        self.revision_available = revision_available

    def __str__(self):
        return 'Updating: {:s} [{:s} -> {:s}]'\
            .format(self.package.name, self.revision_installed, self.revision_available)


def to_dict(packages):
    d = {}
    for p in packages:
        d[p.name] = p
    return d


def compute_package_ops(package_names, installed, available):
    ops = []
    missing = set()

    ad = to_dict(available)
    installed_names = [p.name for p in installed]
    
    if package_names is not None:
        not_installed = set(package_names) - set(installed_names)

        for name in not_installed:
            p = ad.get(name)
            if p is None:
                missing.add(name)
            else:
                ops.append(Install(p, p.revision))

    for i in installed:
        p = ad.get(i.name)
        if p is None:
            missing.add(i.name)
        elif p.semver > i.semver:
            ops.append(Update(p, i.revision, p.revision))

    return ops, missing


def scan_missing(sdk, packages, verbose=False):
    # Re-scan SDK root to check for failed installs.
    print('Re-scanning {:s}...'.format(sdk))
    installed = scan(sdk, verbose=verbose)
    return [p for p in packages if p not in installed]


def install_packages(packages, android, options=None, verbose=False, timeout=None):
    if options is None:
        options = []
    package_filter = ','.join([p.num for p in packages])
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
            print('WARNING: Package installation timed out after {:d} seconds.'
                  .format(timeout), file=sys.stderr)
            break
        else:
            break

def updates_available(android, sdk, packages=None, options=None, verbose=False):
    print('Scanning', sdk, 'for installed packages...')
    installed = scan(sdk, verbose=verbose)
    print('   ', str(len(installed)), 'packages installed.')

    print('Querying update sites for available packages...')
    available = list_packages(android, options=options, verbose=verbose)
    print('   ', str(len(available)), 'packages available.')

    return compute_package_ops(packages, installed, available)


def main(sdk, packages=None, options=None, verbose=False, timeout=None, dry_run=False):
    if timeout == 0:
        timeout = None

    android = os.path.join(sdk, 'tools', 'android')
    if not os.path.isfile(android):
        print('{:s} not found. Is ANDROID_HOME correct?'.format(android))
        exit(1)

    ops, missing_remote = updates_available(android, sdk, packages, options, verbose)

    if missing_remote:
        print('WARNING: Remote repository is missing package(s):', file=sys.stderr)
        for name in missing_remote:
            print('    ', name, file=sys.stderr)
        if packages:
            missing_requested = set(missing_remote).intersection(set(packages))
            if missing_requested:
                print('FATAL: Remote repository is missing explicitly requested package(s):', file=sys.stderr)
                for p in missing_requested:
                    print('    ', p, file=sys.stderr)
                exit(1)

    if not ops:
        print("All packages are up-to-date.")
        exit(0)

    if dry_run:
        print("--dry-run was set; exiting.")
        exit(0)

    for op in ops:
        print(op)

    to_install = [op.package for op in ops]

    install_packages(to_install, android, options, verbose, timeout)

    # Re-scan SDK dir for packages we missed.
    missing = scan_missing(sdk, to_install, verbose=verbose)

    if missing:
        print('FATAL: Finished: {:d} packages installed. Failed to install {:d} package(s):'
              .format(len(to_install) - len(missing), len(missing)), file=sys.stderr)
        for p in missing:
            print('    ', p, file=sys.stderr)
        exit(1)
    else:
        print('Finished: {:d} packages installed.'.format(len(to_install)))
        exit(0)

if __name__ == '__main__':
    main(sys.argv[1:])
