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

        db.session.commit()

        self.client = app.test_client()

    def test_list_users(self):
        with self.client as c:
            resp = c.get('/users')

            

    def test_users_show(self):
        pass

    def test_show_following(self):
        pass

    def test_users_followers(self):
        pass

    def users_likes(self):
        pass

    def test_add_follow(self):
        pass

    def test_stop_following(self):
        pass

    def test_profile(self):
        pass

    def test_delete_user(self):
        pass

    # def test_signup(self):
    #     pass

    # def test_login(self):
    #     pass

    # def test_logout(self):
    #     pass

    