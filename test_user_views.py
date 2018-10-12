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
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD"
        )

        juan = User(
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([edward, juan])
        db.session.commit()

        self.assertIsInstance(edward, User)
        self.assertIsInstance(juan, User)

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
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        db.session.add_all([edward, juan])
        db.session.commit()

        user_ids = {
            'edward': edward.id,
            'juan': juan.id,
        }

        # LETS SEE IF EDWARD FOLLOWS JUAN THAT FOLLOW/UNFOLLOW
        # BUTTON IS RIGHT
        edward.following.append(juan)
        db.session.commit()   

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user_ids['edward']

            # Get edward's user detail page as edward
            resp = c.get(f'/users/{user_ids["edward"]}')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@edward', resp.data)
            self.assertIn(b'Oakland', resp.data)
            self.assertIn(b'Edit Profile</a>', resp.data)
            self.assertNotIn(b'@juan', resp.data)
            self.assertNotIn(b'New York', resp.data)

            # Get juan's user detail page as edward
            resp = c.get(f'/users/{user_ids["juan"]}')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@juan', resp.data)
            self.assertIn(b'New York', resp.data)
            self.assertIn(b'Unfollow</button>', resp.data)
            self.assertNotIn(b'@edward', resp.data)
            self.assertNotIn(b'Oakland', resp.data)


    def test_show_following(self):
        """Test /users/user_id/following route shows who user is following"""

        edward = User(
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        timmy = User(
            email="tim@test.com",
            username="timmy",
            password="HASHED_PASSWORD",
            location="Antarctica"
        )        

        db.session.add_all([edward, juan, timmy])
        db.session.commit()

        user_ids = {
            'edward': edward.id,
            'juan': juan.id,
            'timmy': timmy.id
        }

        # LETS SEE IF EDWARD FOLLOWS JUAN THAT FOLLOW/UNFOLLOW
        # BUTTON IS RIGHT
        edward.following.append(juan)
        db.session.commit()

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user_ids['edward']

            # View who edward is following
            resp = c.get(f'/users/{user_ids["edward"]}/following')
            
            self.assertEqual(resp.status_code, 200)

            # test username under profile pic on left but not a
            # following card
            self.assertIn(b'@edward</h4>', resp.data)
            self.assertNotIn(b'@edward</a>', resp.data)

            #test follower cards
            self.assertIn(b'@juan', resp.data)
            self.assertNotIn(b'@timmy</a>', resp.data)  
            self.assertIn(b'Unfollow</button>', resp.data)

    def test_users_followers(self):
        """Test /users/user_id/followers route show who is following user"""

        edward = User(
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        timmy = User(
            email="tim@test.com",
            username="timmy",
            password="HASHED_PASSWORD",
            location="Antarctica"
        )     

        db.session.add_all([edward, juan, timmy])

        timmy.following.append(edward)
        db.session.commit()

        user_ids = {
            'edward': edward.id,
            'juan': juan.id,
            'timmy': timmy.id
        }

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user_ids['edward']
            # View edwards followers
            resp = c.get(f'/users/{user_ids["edward"]}/followers')
            
            self.assertEqual(resp.status_code, 200)

            # test username under profile pic on left but not a
            # following card
            self.assertIn(b'@edward</h4>', resp.data)
            self.assertNotIn(b'@edward</a>', resp.data)

            #test cards of followers
            self.assertNotIn(b'@juan', resp.data)
            self.assertIn(b'@timmy', resp.data)

    def test_users_likes(self):
        """Test the /users/user_id/likes page"""

        edward = User(
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        timmy = User(
            email="tim@test.com",
            username="timmy",
            password="HASHED_PASSWORD",
            location="Antarctica"
        )

        db.session.add_all([edward, juan, timmy])
        db.session.commit()

        user_ids = {
            'edward': edward.id,
            'juan': juan.id,
            'timmy': timmy.id
        }

        # POSTED BY EDWARD
        edwards_message = Message(
            text="test message 1",
            user_id=user_ids['edward']
        )

        # POSTED BY TIMMY
        timmys_message = Message(
            text="test message 2",
            user_id=user_ids['timmy']
        )

        db.session.add_all([edwards_message, timmys_message])
        db.session.commit()

        # LETS LIKE SOME THINGS
        # EDWARD LIKES TIMMYS POST
        edward.messages_liked.append(Message.query.get(timmys_message.id))

        # JUAN LIKES EDWARDS POST
        juan.messages_liked.append(Message.query.get(edwards_message.id))

        db.session.commit()

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user_ids['edward']

            # View edwards followers
            resp = c.get(f'/users/{user_ids["edward"]}/likes')
            
            self.assertEqual(resp.status_code, 200)

            #test list group items of liked posts on page
            self.assertNotIn(b'@juan', resp.data)
            self.assertIn(b'@timmy', resp.data)

            # check that only solid stars
            self.assertIn(b'class="fas fa-star', resp.data)
            self.assertNotIn(b'class="far fa-star', resp.data)

    def test_add_follow(self):
        """Test the /users/follow/user_id page"""

        edward = User(
            email="ed@test.com",
            username="edward",
            password="HASHED_PASSWORD",
            location="Oakland"
        )

        juan = User(
            email="juanton@test.com",
            username="juan",
            password="HASHED_PASSWORD",
            location="New York"
        )

        timmy = User(
            email="tim@test.com",
            username="timmy",
            password="HASHED_PASSWORD",
            location="Antarctica"
        )

        db.session.add_all([edward, juan, timmy])
        db.session.commit()

        user_ids = {
            'edward': edward.id,
            'juan': juan.id,
            'timmy': timmy.id
        }

        db.session.commit()

        with self.client as c:

            # Let's make sure our session knows we are test user "edward"
            # Edward is the current logged in user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = user_ids['edward']

            # Tell server to have Edward follow Juan
            resp = c.post(f'/users/follow/{user_ids["juan"]}', data={"text": "Hello"})


            # We have to re-grab juan and edward user instances
            # because sqlalchemy gets rid of them when we initiate
            # a new application context
            juan = User.query.get(user_ids['juan'])
            edward = User.query.get(user_ids['edward'])

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            # import pdb; pdb.set_trace()
            # Make sure Edward is a follower of Juan
            # Assert that Edwars is IN Juan's followers
            self.assertIn(edward, juan.followers)



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

    