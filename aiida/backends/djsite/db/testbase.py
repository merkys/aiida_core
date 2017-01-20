# -*- coding: utf-8 -*-
"""
Base class for AiiDA tests
"""
import os
import shutil
import uuid as UUID

from django.utils import unittest
from aiida import settings
from aiida.repository.implementation.filesystem.repository import RepositoryFileSystem
from aiida.backends.testimplbase import AiidaTestImplementation

# Add a new entry here if you add a file with tests under aiida.backends.djsite.db.subtests
# The key is the name to use in the 'verdi test' command (e.g., a key 'generic'
# can be run using 'verdi test db.generic')
# The value must be the module name containing the subclasses of unittest.TestCase

__copyright__ = u"Copyright (c), This file is part of the AiiDA platform. For further information please visit http://www.aiida.net/. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file."
__version__ = "0.7.1"
__authors__ = "The AiiDA team."

# This contains the codebase for the setUpClass and tearDown methods used internally by the AiidaTestCase
# This inherits only from 'object' to avoid that it is picked up by the automatic discovery of tests
# (It shouldn't, as it risks to destroy the DB if there are not the checks in place, and these are
# implemented in the AiidaTestCase
class DjangoTests(AiidaTestImplementation):
    """
    Automatically takes care of the setUpClass and TearDownClass, when needed.
    """

    # Note this is has to be a normal method, not a class method
    def setUpClass_method(self):
        self.clean_db()
        self.insert_data()
        self.create_repo()

    def setUp_method(self):
        pass

    def tearDown_method(self):
        pass

    def create_repo(self):
        """
        Create the repository in the database
        """
        from aiida.backends.djsite.db.models import DbRepository
        repo_config = {
            'base_path' : settings.REPOSITORY_BASE_PATH,
            'uuid_path' : settings.REPOSITORY_UUID_PATH,
            'repo_name' : settings.REPOSITORY_NAME,
        }
        repository = RepositoryFileSystem(repo_config)
        dbrepo = DbRepository(name=settings.REPOSITORY_NAME, uuid=repository.get_uuid())
        dbrepo.save()

    def insert_data(self):
        """
        Insert default data into the DB.
        """
        from django.core.exceptions import ObjectDoesNotExist

        from aiida.backends.djsite.db.models import DbUser
        from aiida.orm.computer import Computer
        from aiida.common.utils import get_configured_user_email
        # We create the user only once:
        # Otherwise, get_automatic_user() will fail when the
        # user is recreated because it caches the user!
        # In any case, store it in self.user though
        try:
            self.user = DbUser.objects.get(email=get_configured_user_email())
        except ObjectDoesNotExist:
            self.user = DbUser.objects.create_user(get_configured_user_email(),
                                                   'fakepwd')
        # Reqired by the calling class
        self.user_email = self.user.email

        # Also self.computer is required by the calling class
        self.computer = Computer(name='localhost',
                                hostname='localhost',
                                transport_type='local',
                                scheduler_type='pbspro',
                                workdir='/tmp/aiida')
        self.computer.store()

    def clean_db(self):
        from aiida.backends.djsite.db.models import DbComputer

        # I first delete the workflows
        from aiida.backends.djsite.db.models import DbWorkflow

        DbWorkflow.objects.all().delete()

        # Delete groups
        from aiida.backends.djsite.db.models import DbGroup

        DbGroup.objects.all().delete()

        # I first need to delete the links, because in principle I could
        # not delete input nodes, only outputs. For simplicity, since
        # I am deleting everything, I delete the links first
        from aiida.backends.djsite.db.models import DbLink

        DbLink.objects.all().delete()

        # Then I delete the nodes, otherwise I cannot
        # delete computers and users
        from aiida.backends.djsite.db.models import DbNode

        DbNode.objects.all().delete()

        ## I do not delete it, see discussion in setUpClass
        # try:
        #    DbUser.objects.get(email=get_configured_user_email()).delete()
        # except ObjectDoesNotExist:
        #    pass

        DbComputer.objects.all().delete()

        from aiida.backends.djsite.db.models import DbLog

        DbLog.objects.all().delete()

        from aiida.backends.djsite.db.models import DbRepository, DbNodeFile, DbFile

        DbNodeFile.objects.all().delete()
        DbFile.objects.all().delete()
        DbRepository.objects.all().delete()


    # Note this is has to be a normal method, not a class method
    def tearDownClass_method(self):
        from aiida.settings import REPOSITORY_BASE_PATH, REPOSITORY_UUID_PATH
        from aiida.common.setup import TEST_KEYWORD
        from aiida.common.exceptions import InvalidOperation

        base_repo_path = os.path.basename(
            os.path.normpath(REPOSITORY_BASE_PATH))
        if TEST_KEYWORD not in base_repo_path:
            raise InvalidOperation("Be careful. The repository for the tests "
                                   "is not a test repository. I will not "
                                   "empty the database and I will not delete "
                                   "the repository. Repository path: "
                                   "{}".format(REPOSITORY_BASE_PATH))

        self.clean_db()

        # I clean the test repository and recreate it
        shutil.rmtree(REPOSITORY_BASE_PATH, ignore_errors=True)
        os.makedirs(REPOSITORY_BASE_PATH)

        # TODO: this should be moved eventually.
        # At startup, the configuration is parsed and assumes the configured
        # repository is properly initialized. For the filesystem type this means
        # that the base directory exists and the UUID is readable from the UUID file.
        # So we have to recreate a new random UUID here
        uuid = unicode(UUID.uuid4())
        with open(REPOSITORY_UUID_PATH, 'w') as f:
            f.write(uuid)
