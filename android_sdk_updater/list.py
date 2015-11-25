#!/usr/bin/env python3

import re
import sys
import subprocess
import semantic_version
from android_sdk_updater.package import Package

categories = {
    'Addon': 'add-ons',
    'BuildTool': 'build-tools',
    'Doc': 'docs',
    'Extra': 'extras',
    'Platform': 'platforms',
    'PlatformTool': 'platform-tools',
    'Sample': 'samples',
    'Source': 'sources',
    'SystemImage': 'system-images',
    'Tool': 'tools'
}

def list(android):
    packages = []
    separator = '----------'
    out = subprocess.getoutput(android + ' list sdk --all --extended')
    fields = out.split(separator)[1:]
    p_id = re.compile('^id: (\d+) or "(.+)"$', flags=re.MULTILINE)
    p_revision = re.compile('[Rr]evision (.+)')
    p_type = re.compile('Type: (\w+)')
    for field in fields:
        m = p_id.search(field)
        if m is None:
            print("Failed to parse package ID:", field, file=sys.stderr)
            continue
        num, name = m.groups()
        m = p_revision.search(field)
        if m is None:
            print("Failed to parse revision:", field, file=sys.stderr)
            continue
        revision, *rest = m.groups()
        revision = semantic_version.Version.coerce(revision.replace(' (Obsolete)', ''))

        m = p_type.search(field)
        if m is None:
            print("Failed to parse type:", field, file=sys.stderr)
            continue
        ptype, = m.groups()
        category = categories[ptype]
        if category is None:
            print("Unrecognized type:", ptype, file=sys.stderr)
            category = ptype.lower()
        packages += [Package(category, name, revision, num)]
    return packages


def main(android):
    packages = list(android)
    for p in packages:
        print(p)

if __name__ == '__main__':
    main(sys.argv[1])