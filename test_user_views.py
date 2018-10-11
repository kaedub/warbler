"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test User routes."""

    def setUp(self):
        """Create est client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        self.client = app.test_client()