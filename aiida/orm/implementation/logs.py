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
from abc import abstractmethod, abstractproperty, ABCMeta

import six

from . import backends

__all__ = ('BackendLog', 'BackendLogCollection')


@six.add_metaclass(ABCMeta)
class BackendLog(backends.BackendEntity):
    @abstractproperty
    def id(self):
        """
        Get the primary key of the entry

        :return: The entry primary key
        :rtype: int
        """
        pass

    @abstractproperty
    def time(self):
        """
        Get the time corresponding to the entry

        :return: The entry timestamp
        :rtype: :class:`!datetime.datetime`
        """
        pass

    @abstractproperty
    def loggername(self):
        """
        The name of the logger that created this entry

        :return: The entry loggername
        :rtype: basestring
        """
        pass

    @abstractproperty
    def levelname(self):
        """
        The name of the log level

        :return: The entry log level name
        :rtype: basestring
        """
        pass

    @abstractproperty
    def objpk(self):
        """
        Get the id of the object that created the log entry

        :return: The entry timestamp
        :rtype: int
        """
        pass

    @abstractproperty
    def objname(self):
        """
        Get the name of the object that created the log entry

        :return: The entry object name
        :rtype: basestring
        """
        pass

    @abstractproperty
    def message(self):
        """
        Get the message corresponding to the entry

        :return: The entry message
        :rtype: basestring
        """
        pass

    @abstractproperty
    def metadata(self):
        """
        Get the metadata corresponding to the entry

        :return: The entry metadata
        :rtype: :class:`!json.json`
        """
        pass

    @abstractmethod
    def save(self):
        """
        Persist the log entry to the database

        :return: reference of self
        :rtype: :class: Log
        """
        pass


@six.add_metaclass(ABCMeta)
class BackendLogCollection(backends.BackendCollection):
    """
    This class represents the collection of logs and can be used to create
    and retrieve logs.
    """

    ENTRY_TYPE = BackendLog

    @abstractmethod
    def create_entry(self, time, loggername, levelname, objname,
                     objpk=None, message="", metadata=None):
        """
        Create a log entry.

        :param time: The time of creation for the entry
        :type time: :class:`!datetime.datetime`
        :param loggername: The name of the logger that generated the entry
        :type loggername: basestring
        :param levelname: The log level
        :type levelname: basestring
        :param objname: The object name (if any) that emitted the entry
        :type objname: basestring
        :param objpk: The object id that emitted the entry
        :type objpk: int
        :param message: The message to log
        :type message: basestring
        :param metadata: Any (optional) metadata, should be JSON serializable dictionary
        :type metadata: :class:`dict`
        :return: An object implementing the log entry interface
        :rtype: :class:`aiida.orm.log.Log`
        """
        pass

    @abstractmethod
    def create_entry_from_record(self, record):
        """
        Helper function to create a log entry from a record created as by the
        python logging lobrary

        :param record: The record created by the logging module
        :type record: :class:`logging.record`
        :return: An object implementing the log entry interface
        :rtype: :class:`aiida.orm.log.Log`
        """
        pass

    @abstractmethod
    def find(self, filter_by=None, order_by=None, limit=None):
        """
        Find all entries in the Log collection that conforms to the filter and
        optionally sort and/or apply a limit.

        :param filter_by: A dictionary of key value pairs where the entries have
            to match all the criteria (i.e. an AND operation)
        :type filter_by: :class:`dict`
        :param order_by: A list of tuples of type :class:`OrderSpecifier`
        :type order_by: list
        :param limit: The number of entries to retrieve
        :return: An iterable of the matching entries
        """
        pass

    @abstractmethod
    def delete_many(self, filter):
        """
        Delete all the log entries matching the given filter
        """
        pass
