# (C) Datadog, Inc. 2019
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import re

import semver
from six import iteritems


def parse_semver(version, options):
    version_info = semver.parse_version_info(version)

    parts = {'major': str(version_info.major), 'minor': str(version_info.minor), 'patch': str(version_info.patch)}

    if version_info.prerelease:
        parts['release'] = str(version_info.prerelease)

    if version_info.build:
        parts['build'] = str(version_info.build)

    return parts


def parse_regex(version, options):
    pattern = options.get('pattern')
    if not pattern:
        raise ValueError('Version scheme `regex` requires a `pattern` option')

    match = re.search(pattern, version)
    if not match:
        raise ValueError('Version does not match the regular expression pattern')

    parts = match.groupdict()
    if not parts:
        raise ValueError('Regular expression pattern has no named subgroups')

    return {part: value for part, value in iteritems(parts) if value is not None}


def parse_version(version, options):
    scheme = options.get('scheme')

    if not scheme:
        scheme = 'semver'
    elif scheme not in SCHEMES:
        raise ValueError('Unsupported version scheme `{}`'.format(scheme))

    return scheme, SCHEMES[scheme](version, options)


SCHEMES = {'semver': parse_semver, 'regex': parse_regex}
