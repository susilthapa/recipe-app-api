from unittest.mock import patch

from django.core.management import call_command # allows us to call the command in our source code
from django.db.utils import OperationalError # allows to  throws if databse is unavailable
from django.test import TestCase

class CommandTests(TestCase):

  def test_wait_for_db_ready(self):
    """Test for db when db is available"""
    with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
      gi.return_value = True
      call_command('wait_for_db')
      self.assertEqual(gi.call_count, 1)

  @patch('time.sleep', return_value=True)
  def test_wait_for_db(self, ts):
    """Test waiting for db""" 
    with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
      gi.side_effect = [OperationalError] * 5 + [True]
      """call to getitem raisers five times the operational error and on the sixth time it returns"""
      call_command('wait_for_db')
      self.assertEqual(gi.call_count, 6)