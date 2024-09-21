from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check')
@patch('time.sleep')
class CommandTests(SimpleTestCase):
    def test_wait_for_db_ready(self, patched_sleep, patched_check):
        """Test waiting for db when db is available"""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])
        patched_sleep.assert_not_called()  # sleep should not be called if the db is ready

