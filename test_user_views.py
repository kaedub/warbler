"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, User, Message, FollowersFollowee

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

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
        """Test that /user route correctly shows searched users"""

        edward = User(
            id=1,
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD"
        )

        juan = User(
            id=2,
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD"
        )

        db.session.add(edward)
        db.session.add(juan)
        db.session.commit()

        # SHOULD WE REMOVE THIS SINCE THIS IS TESTING THE USER MODEL
        # AND DATABASE MORE THAN THE VIEW FUNCTION?
        user_edward = User.query.get(1)
        user_juan = User.query.get(2)

        self.assertIsInstance(user_edward, User)
        self.assertIsInstance(user_juan, User)

        with self.client as c:
            resp = c.get('/users')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@edward', resp.data)
            self.assertIn(b'@juan', resp.data)

            resp = c.get('/users?q=ed')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@edward', resp.data)
            self.assertNotIn(b'@juan', resp.data)


    def test_users_show(self):
        """Test that /user/user_id shows that users profile"""

        edward = User(
            id=1,
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            id=2,
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        db.session.add(edward)
        db.session.add(juan)
        db.session.commit()

        # LETS SEE IF EDWARD FOLLOWS JUAN THAT FOLLOW/UNFOLLOW
        # BUTTON IS RIGHT
        edward.following.append(juan)
        db.session.commit()   

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1

            # Get edward's user detail page as edward
            resp = c.get('/users/1')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@edward', resp.data)
            self.assertIn(b'Oakland', resp.data)
            self.assertIn(b'Edit Profile</a>', resp.data)
            self.assertNotIn(b'@juan', resp.data)
            self.assertNotIn(b'New York', resp.data)

            # Get juan's user detail page as edward
            resp = c.get('/users/2')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@juan', resp.data)
            self.assertIn(b'New York', resp.data)
            self.assertIn(b'Unfollow</button>', resp.data)
            self.assertNotIn(b'@edward', resp.data)
            self.assertNotIn(b'Oakland', resp.data)


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

    