#!/usr/bin/python

from __future__ import print_function

import os
import sys
import jprops

from semantic_version import Version

from sdk_updater.package import Package


# TODO: Support NDK installs
blacklist = [
    'ndk-bundle'
]


def add_ons(props, parts):
    return parts[1]


def build_tools(props, parts):
    return '-'.join(parts)


def docs(props, parts):
    return 'doc-' + props['api']


def extras(props, parts):
    return '-'.join(['extra'] + parts[1:])


def platforms(props, parts):
    return 'android-' + props['api']


def platform_tools(props, parts):
    if props['license'] == 'android-sdk-preview-license':
        return parts[0] + '-preview'
    return parts[0]


def samples(props, parts):
    return 'sample-' + props['api']


def sources(props, parts):
    return 'source-' + props['api']


def system_images(props, parts):
    tag = props['tag']
    if tag == 'default':
        tag = 'android'
    if tag == 'google_apis':
        tag = 'addon-google_apis-google'
    return '-'.join(['sys-img', props['abi'], tag, props['api']])


def tools(props, parts):
    return 'tools'


def default(props, parts):
    return None


def parse(top, root):
    path = os.path.relpath(root, top)

    if path in blacklist:
        print('Ignoring \'{:s}\' as it is blacklisted.'.format(path))
        return None

    parts = path.split(os.path.sep)
    props = parse_properties(os.path.join(root, 'source.properties'))
    name = {
        'add-ons': add_ons,
        'build-tools': build_tools,
        'docs': docs,
        'extras': extras,
        'platforms': platforms,
        'platform-tools': platform_tools,
        'samples': samples,
        'sources': sources,
        'system-images': system_images,
        'tools': tools
    }.get(parts[0], default)(props, parts)
    if not name:
        print("Package parse failed:", path, file=sys.stderr)
        return None
    return Package(parts[0], name, props['revision'], Version.coerce(props['revision']))


def parse_properties(file):
    props = {}
    with open(file, 'rb') as fp:
        for key, value in jprops.iter_properties(fp):
            if key == 'AndroidVersion.ApiLevel':
                props['api'] = value
            elif key == 'Pkg.LicenseRef':
                props['license'] = value
            elif key == 'Pkg.Revision':
                props['revision'] = value
            elif key == 'SystemImage.Abi':
                props['abi'] = value
            elif key == 'SystemImage.TagId':
                props['tag'] = value
    return props


def scan(top, verbose=False):
    packages = []
    for root, subdirs, files in os.walk(top):
        if 'source.properties' in files:
            del subdirs[:]
            package = parse(top, root)
            if package:
                packages.append(package)
                if verbose:
                    print('Found package "{:s}" in {:s}'.format(str(package), root))
    return packages


def main(top):
    packages = scan(top)
    for package in packages:
        print(str(package))


if __name__ == '__main__':
    main(sys.argv[1])
