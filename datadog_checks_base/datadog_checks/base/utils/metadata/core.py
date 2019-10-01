# (C) Datadog, Inc. 2019
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import logging

from six import iteritems

from .version import parse_version

try:
    import datadog_agent
except ImportError:
    from ...stubs import datadog_agent

LOGGER = logging.getLogger(__file__)


class MetadataManager(object):
    __slots__ = ('check_id', 'logger', 'metadata_transformers')

    def __init__(self, check_id, logger, metadata_transformers=None):
        self.check_id = check_id
        self.logger = logger or LOGGER
        self.metadata_transformers = {'version': self.transform_version}

        if metadata_transformers:
            self.metadata_transformers.update(metadata_transformers)

    def submit_raw(self, name, value):
        datadog_agent.set_check_metadata(self.check_id, name, value)

    def transform_version(self, value, options):
        scheme, version_parts = parse_version(value, options)

        data = {'version.{}'.format(part_name): part_value for part_name, part_value in iteritems(version_parts)}
        data['version.raw'] = value
        data['version.scheme'] = scheme

        return data

    def submit(self, name, value, options):
        transformer = self.metadata_transformers.get(name)
        if transformer:
            try:
                transformed = transformer(value, options)
            except Exception as e:
                self.logger.error('Unable to transform `%s` metadata value `%s`: %s', name, value, e)
                return

            if isinstance(transformed, str):
                self.submit_raw(name, transformed)
            else:
                for transformed_name, transformed_value in iteritems(transformed):
                    self.submit_raw(transformed_name, transformed_value)
        else:
            self.submit_raw(name, value)
