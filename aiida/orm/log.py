# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from collections import namedtuple

import six

from aiida.utils import timezone
from aiida.orm.entities import Collection
from .backends import construct_backend
from . import entities

ASCENDING = 1
DESCENDING = -1

OrderSpecifier = namedtuple("OrderSpecifier", ['field', 'direction'])

__all_ = ['Log']


class Log(entities.Entity):
    class Collection(entities.Entity.Collection):
        """
        This class represents the collection of logs and can be used to create
        and retrieve logs.
        """

        def create_entry(self, **kwargs):
            return self._backend.log.create_entry(**kwargs)

        def create_entry_from_record(self, record):
            """
            Helper function to create a log entry from a record created as by the
            python logging lobrary

            :param record: The record created by the logging module
            :type record: :class:`logging.record`
            :return: An object implementing the log entry interface
            :rtype: :class:`aiida.orm.log.Log`
            """
            from datetime import datetime

            objpk = record.__dict__.get('objpk', None)
            objname = record.__dict__.get('objname', None)

            # Do not store if objpk and objname are not set
            if objpk is None or objname is None:
                return None

            return self.create_entry(
                time=timezone.make_aware(datetime.fromtimestamp(record.created)),
                loggername=record.name,
                levelname=record.levelname,
                objname=objname,
                objpk=objpk,
                message=record.getMessage(),
                metadata=record.__dict__
            )

        def find(self, **kwargs):
            return self._backend.log.find(**kwargs)

        def delete_many(self, filter):
            return self._backend.log.delete_many(filter)

    def __init__(self, backend=None):
        backend = backend or construct_backend()
        model = backend.logs.create()
        super(Log, self).__init__(model)

    @property
    def id(self):
        """
        Get the primary key of the entry

        :return: The entry primary key
        :rtype: int
        """
        return self._backend_entity.id

    @property
    def time(self):
        """
        Get the time corresponding to the entry

        :return: The entry timestamp
        :rtype: :class:`!datetime.datetime`
        """
        return self._backend_entity.time

    @property
    def loggername(self):
        """
        The name of the logger that created this entry

        :return: The entry loggername
        :rtype: basestring
        """
        return self._backend_entity.loggername

    @property
    def levelname(self):
        """
        The name of the log level

        :return: The entry log level name
        :rtype: basestring
        """
        return self._backend_entity.levelname

    @property
    def objpk(self):
        """
        Get the id of the object that created the log entry

        :return: The entry timestamp
        :rtype: int
        """
        return self._backend_entity.objpk

    @property
    def objname(self):
        """
        Get the name of the object that created the log entry

        :return: The entry object name
        :rtype: basestring
        """
        return self._backend_entity.objname

    @property
    def message(self):
        """
        Get the message corresponding to the entry

        :return: The entry message
        :rtype: basestring
        """
        return self._backend_entity.message

    @property
    def metadata(self):
        """
        Get the metadata corresponding to the entry

        :return: The entry metadata
        :rtype: :class:`!json.json`
        """
        return self._backend_entity.metadata

    def save(self):
        """
        Persist the log entry to the database

        :return: reference of self
        :rtype: :class: Log
        """
        return self._backend_entity.save()
